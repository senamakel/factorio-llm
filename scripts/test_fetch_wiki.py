"""Offline checks for wiki-cache conversion, slugs, API parsing and the index."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts import fetch_wiki
from scripts.wiki_text import first_sentence, title_to_slug, wiki_url, wikitext_to_text

INFOBOX = """{{Infobox
|image = Lab_entity
|crafting-speed = {{Quality|0.5|0.65|0.8|0.95|1.25}}
|recipe = Time, 0.5 + Iron gear wheel, 1 + Iron plate, 1 = Transport belt, 2
|technology-trigger = craft-item: Iron plate, 50
|effects = Boiler + Steam engine
|resistance = {{Translation|Fire}}: 0/70%<br>{{Translation|Impact}}: 0/30%
}}<noinclude>[[Category:Infobox page]]</noinclude>"""


class SlugTest(unittest.TestCase):
    def test_titles_map_to_shell_friendly_stems(self):
        self.assertEqual(title_to_slug('Automation (research)'), 'Automation_research')
        self.assertEqual(title_to_slug('Tutorial:Main bus'), 'Tutorial_Main_bus')
        self.assertEqual(title_to_slug('Transport belts/Physics'), 'Transport_belts_Physics')
        self.assertEqual(title_to_slug('Long-handed inserter'), 'Long-handed_inserter')

    def test_empty_slug_is_rejected(self):
        with self.assertRaises(ValueError):
            title_to_slug(' () ')

    def test_url_uses_underscores(self):
        self.assertEqual(wiki_url('Steam power (research)'),
                         'https://wiki.factorio.com/Steam_power_(research)')


class ConversionTest(unittest.TestCase):
    def convert(self, text, pages=None):
        return wikitext_to_text(text, (pages or {}).get)

    def test_transcluded_infobox_keeps_recipe_trigger_and_quality_facts(self):
        out = self.convert('{{Languages}}\n{{:Infobox:Belt}}\nBody.', {'Infobox:Belt': INFOBOX})
        self.assertIn('## Infobox', out)
        self.assertIn('- Recipe: 0.5 s; 1 × Iron gear wheel + 1 × Iron plate -> 2 × Transport belt', out)
        self.assertIn('craft-item: Iron plate × 50', out)
        self.assertIn('- Crafting speed: 0.5 (by quality normal/uncommon/rare/epic/legendary: '
                      '0.5 / 0.65 / 0.8 / 0.95 / 1.25)', out)
        self.assertIn('- Effects (unlocks): Boiler, Steam engine', out)
        self.assertIn('- Resistance: Fire: 0/70% / Impact: 0/30%', out)
        self.assertNotIn('Lab_entity', out)
        self.assertNotIn('Category', out)
        self.assertNotIn('{{', out)

    def test_missing_transclusion_is_dropped_quietly(self):
        self.assertEqual(self.convert('{{:Infobox:Nope}}Text'), 'Text\n')

    def test_quality_outside_infobox_keeps_only_normal_value(self):
        self.assertEqual(self.convert('Speed {{ Quality | 0.78 | 1.03 }} items/s'),
                         'Speed 0.78 items/s\n')

    def test_links_templates_and_files(self):
        out = self.convert("See [[iron plate]]s, [[Electric_system#Distribution|power poles]] "
                           "and [https://example.com the forum]. [[File:x.png|thumb|cap]]"
                           "[[File:Belt.png|link=Transport belt|32px]] {{Icon|Coal|5}} "
                           "{{Imagelink|Lab}} {{IntermediateNav}}[[Category:Items]][[de:Eisen]]")
        self.assertEqual(out, 'See iron plates, power poles and the forum. '
                              'Transport belt 5 × Coal Lab\n')

    def test_bold_lead_and_headings_are_not_mistaken_for_lists(self):
        out = self.convert("'''Lab''' does research.\n== Ratio ==\n=== Sub ===\n"
                           "* one\n** nested\n# first\n''italic''")
        self.assertEqual(out, '**Lab** does research.\n## Ratio\n### Sub\n'
                              '- one\n  - nested\n1. first\n*italic*\n')

    def test_table_spans_expand_into_aligned_grid(self):
        table = ('{| class="wikitable"\n! rowspan=2 | Belt || colspan=2 | Speed\n|-\n'
                 '! Factor || Tiles/sec\n|- align="center"\n'
                 '| align="left" | {{Imagelink|Transport belt}} || 1 || 1.875<br>tiles\n|}')
        self.assertEqual(self.convert(table),
                         '| Belt | Speed | Speed |\n|---|---|---|\n| | Factor | Tiles/sec |\n'
                         '| Transport belt | 1 | 1.875 / tiles |\n'.replace('| |', '|  |'))

    def test_nested_table_becomes_single_cell(self):
        out = self.convert('{|\n! Items/min\n|-\n|\n{|\n|-\n| {{Icon|Gear|150}} || x\n|}\n|}')
        self.assertIn('| 150 × Gear x |', out)

    def test_math_is_protected_from_template_parsing(self):
        out = self.convert(r'Ratio <math>\frac{\mathrm{A}}{\mathrm{B}}</math> holds.')
        self.assertEqual(out, 'Ratio `\\frac{\\mathrm{A}}{\\mathrm{B}}` holds.\n')

    def test_history_template_lists_changes_per_version(self):
        out = self.convert('{{history|2.0.7|\n* Introduced.}}')
        self.assertEqual(out, 'Version 2.0.7:\n- Introduced.\n')

    def test_conversion_is_deterministic(self):
        text = "{{:Infobox:Belt}}\n'''x''' y"
        pages = {'Infobox:Belt': INFOBOX}
        self.assertEqual(self.convert(text, pages), self.convert(text, pages))

    def test_first_sentence_skips_infobox_and_hatnotes(self):
        text = '## Infobox\n- Recipe: 1 s\n\n*For X, see Y.*\n**Coal** is a resource. More text.'
        self.assertEqual(first_sentence(text), 'Coal is a resource.')


def api_reply(pages, redirects=()):
    """Build a fake MediaWiki query response."""
    return json.dumps({'query': {
        'redirects': [{'from': a, 'to': b} for a, b in redirects],
        'pages': {str(i): p for i, p in enumerate(pages)}}}).encode()


class ClientAndIndexTest(unittest.TestCase):
    def test_redirects_and_missing_pages_resolve_per_requested_title(self):
        page = {'title': 'Electric system', 'revisions': [
            {'revid': 7, 'slots': {'main': {'*': 'Body'}}}]}
        reply = api_reply([page, {'title': 'Nope', 'missing': ''}],
                          [('Electricity', 'Electric system')])
        client = fetch_wiki.WikiClient(delay=0, opener=lambda url: reply)
        result = client.get_pages(['Electricity', 'Nope'])
        self.assertEqual(result['Electricity']['title'], 'Electric system')
        self.assertEqual(result['Electricity']['revid'], 7)
        self.assertIsNone(result['Nope'])

    def test_api_error_fails_loudly(self):
        reply = json.dumps({'error': {'code': 'badtitle'}}).encode()
        client = fetch_wiki.WikiClient(delay=0, opener=lambda url: reply)
        with self.assertRaises(RuntimeError):
            client.get_pages(['x'])

    def test_header_and_index_round_trip(self):
        page = {'title': 'Coal', 'revid': 42, 'wikitext': "'''Coal''' burns. Yes."}
        text = fetch_wiki.render_page(page, None, 'coal')
        first = text.split('\n', 1)[0]
        self.assertEqual(first, '<!-- wiki-cache title="Coal" '
                                'url="https://wiki.factorio.com/Coal" revid="42" -->')
        self.assertIn('Requested as: coal (redirect)', text)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertTrue(fetch_wiki.write_if_changed(out / 'Coal.md', text))
            self.assertFalse(fetch_wiki.write_if_changed(out / 'Coal.md', text))
            self.assertEqual(fetch_wiki.build_index(out), 1)
            index = (out / 'INDEX.md').read_text(encoding='utf-8')
            self.assertIn('- [Coal](Coal.md) — Coal burns.', index)

    def test_fetch_reports_missing_titles_without_writing_them(self):
        reply = api_reply([{'title': 'Ghost', 'missing': ''}])
        client = fetch_wiki.WikiClient(delay=0, opener=lambda url: reply)
        with tempfile.TemporaryDirectory() as tmp:
            written, unchanged, missing = fetch_wiki.fetch(['Ghost'], Path(tmp), client)
            self.assertEqual((written, unchanged, missing), ([], [], ['Ghost']))
            self.assertEqual(list(Path(tmp).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
