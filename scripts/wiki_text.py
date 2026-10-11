"""Convert Factorio wiki wikitext into readable Markdown-ish plain text.

The output targets agents that only have shell and file-read tools, so the
converter keeps facts (infobox recipes, costs, speeds, tables) and drops
presentation (images, navboxes, language bars, categories).

Public entry points:

* ``title_to_slug(title)`` -- filesystem-safe file stem for a page title.
* ``wiki_url(title)`` -- canonical wiki.factorio.com URL for a title.
* ``wikitext_to_text(text, transclude=None)`` -- the conversion itself.
  ``transclude`` is an optional callable ``name -> wikitext | None`` used for
  ``{{:Other page}}`` transclusions such as ``{{:Infobox:Lab}}``.
* ``first_sentence(text)`` -- one-line summary used by the index.
"""
import html
import re
import urllib.parse

WIKI_BASE = 'https://wiki.factorio.com/'

# Templates that carry no information for a text reader.
DROP_TEMPLATES = {'languages', 'c', 'achievement', 'clear', 'toc', 'main',
                  'see also', 'stub', 'archived', 'notice', 'spoiler',
                  'collapse', 'tooltip', 'anchor', 'nowrap'}
# Infobox keys that are purely visual.
DROP_INFOBOX_KEYS = {'image', 'map-color', 'image2', 'extra-image'}
QUALITY_TIERS = ('normal', 'uncommon', 'rare', 'epic', 'legendary')
# Infobox keys whose values are "Name, count + Name, count" recipe strings.
RECIPE_KEYS = {'recipe', 'total-raw', 'cost', 'expensive-recipe',
               'expensive-total-raw', 'recycling-results'}
INFOBOX_LABELS = {
    'recipe': 'Recipe', 'total-raw': 'Total raw (per craft)',
    'cost': 'Research cost per unit',
    'cost-multiplier': 'Research units (count)',
    'technology-trigger': 'Research trigger (unlocked by doing this, no science packs)',
    'required-technologies': 'Required technologies',
    'allows': 'Allows (unlocks follow-up techs)', 'effects': 'Effects (unlocks)',
    'internal-name': 'Internal (prototype) name',
    'prototype-type': 'Prototype type', 'crafting-speed': 'Crafting speed',
    'mining-speed': 'Mining speed', 'mining-time': 'Mining time (to pick up)',
    'energy': 'Energy consumption', 'drain': 'Energy drain (idle)',
    'belt-speed': 'Belt speed', 'stack-size': 'Stack size',
    'fuel-value': 'Fuel value', 'power-output': 'Power output',
}


def title_to_slug(title):
    """Map a wiki title to a stable, shell-friendly file stem.

    ``"Automation (research)"`` -> ``"Automation_research"``,
    ``"Tutorial:Main bus"`` -> ``"Tutorial_Main_bus"``. Only ASCII letters,
    digits, ``.``, ``-`` and ``_`` survive; runs of anything else collapse to a
    single underscore. Raises ``ValueError`` when nothing usable remains.
    """
    slug = re.sub(r'[^A-Za-z0-9.\-]+', '_', title.strip()).strip('_.')
    if not slug:
        raise ValueError('title %r has no usable slug' % title)
    return slug


def wiki_url(title):
    """Return the canonical human-facing URL for a wiki page title."""
    return WIKI_BASE + urllib.parse.quote(title.replace(' ', '_'), safe='/:()_,-.')


def _find_close(text, start, opener, closer):
    """Return the index just past the ``closer`` matching ``opener`` at ``start``.

    Nesting of the same delimiter pair is honoured. Returns ``-1`` when the
    construct is unterminated.
    """
    depth, i = 0, start
    while i < len(text):
        if text.startswith(opener, i):
            depth += 1
            i += len(opener)
        elif text.startswith(closer, i):
            depth -= 1
            i += len(closer)
            if depth == 0:
                return i
        else:
            i += 1
    return -1


def split_args(inner):
    """Split template contents on top-level ``|`` (ignoring nested ``{{}}``/``[[]]``)."""
    parts, depth, cur, i = [], 0, [], 0
    while i < len(inner):
        two = inner[i:i + 2]
        if two in ('{{', '[['):
            depth += 1
            cur.append(two)
            i += 2
            continue
        if two in ('}}', ']]') and depth:
            depth -= 1
            cur.append(two)
            i += 2
            continue
        if inner[i] == '|' and depth == 0:
            parts.append(''.join(cur))
            cur = []
        else:
            cur.append(inner[i])
        i += 1
    parts.append(''.join(cur))
    return parts


def _named(args):
    """Split template args into (positional list, named dict); values stripped."""
    pos, named = [], {}
    for arg in args:
        key, eq, value = arg.partition('=')
        if eq and re.fullmatch(r'\s*[\w\- ]+\s*', key) and '[[' not in key:
            named[key.strip().lower()] = value.strip()
        else:
            pos.append(arg.strip())
    return pos, named


def format_recipe(value):
    """Render ``"Time, 5 + Copper plate, 1 = Item, 2"`` as readable text.

    Example output: ``"5 s; 1 × Copper plate -> 2 × Item"``. Values that are not
    in the recipe shape are returned unchanged.
    """
    def side(chunk):
        items, time = [], None
        for part in chunk.split('+'):
            name, _, count = part.strip().rpartition(',')
            name, count = name.strip(), count.strip()
            if not name:
                items.append(part.strip())
            elif name.lower() == 'time':
                time = count + ' s'
            else:
                items.append('%s × %s' % (count, name))
        return time, items
    ingredients, arrow, products = value.partition('=')
    time, items = side(ingredients)
    out = ((time + '; ') if time else '') + (' + '.join(items) or 'nothing')
    if arrow:
        out += ' -> ' + ' + '.join(side(products)[1])
    return out


def render_infobox(args, expand):
    """Render an ``{{Infobox|key = value ...}}`` call as a bullet list."""
    _, named = _named(args)
    lines = ['', '**Infobox**', '']
    for key, raw in named.items():
        if key in DROP_INFOBOX_KEYS or not raw:
            continue
        value = expand(raw)
        if key in RECIPE_KEYS or key.endswith('-recipe'):
            value = format_recipe(value)
        elif key == 'technology-trigger':
            value = value.replace(',', ' ×', 1) if value.count(',') == 1 else value
        elif ' + ' in value:
            value = ', '.join(v.strip() for v in value.split(' + '))
        label = INFOBOX_LABELS.get(key) or key.replace('-', ' ').capitalize()
        lines.append('- %s: %s' % (label, ' '.join(value.split())))
    return '\n'.join(lines) + '\n\n'


def render_template(inner, expand, transclude, depth):
    """Render one template call (contents without the outer braces)."""
    args = split_args(inner)
    name = args[0].strip()
    lname = name.lower().replace('_', ' ')
    if name.startswith(':'):
        if transclude is None or depth > 3:
            return ''
        body = transclude(name[1:].strip())
        return _expand_templates(_strip_noinclude(body), transclude, depth + 1) if body else ''
    rest = args[1:]
    pos, named = _named(rest)
    if lname == 'infobox':
        return render_infobox(rest, expand)
    if lname in DROP_TEMPLATES or lname.endswith('nav') or lname.startswith('#'):
        return ''
    if lname == 'quality':
        vals = [expand(p) for p in pos]
        if len(vals) <= 1:
            return ''.join(vals)
        tiers = ' / '.join(vals)
        return '%s (by quality %s: %s)' % (vals[0], '/'.join(QUALITY_TIERS[:len(vals)]), tiers)
    if lname in ('translation', 'tr'):
        return expand(pos[0]) if pos else ''
    if lname in ('icon', 'imagelink', 'iconnumber'):
        if not pos:
            return ''
        item = expand(pos[0])
        return '%s × %s' % (expand(pos[1]), item) if len(pos) > 1 and pos[1] else item
    if lname == 'history':
        return '\n- Version %s: %s\n' % (expand(pos[0]) if pos else '?',
                                         expand('|'.join(pos[1:])).strip())
    if lname in ('dlc', 'space age', 'sa'):
        return '(Space Age)'
    # Unknown template: keep positional text, the most likely carrier of meaning.
    return ' '.join(expand(p) for p in pos if p)


def _strip_noinclude(text):
    """Drop ``<noinclude>`` blocks and unwrap ``<includeonly>`` content."""
    text = re.sub(r'<noinclude>.*?(</noinclude>|$)', '', text, flags=re.S)
    return re.sub(r'</?includeonly>', '', text)


def _expand_templates(text, transclude, depth=0):
    """Replace every ``{{...}}`` call (outermost first, recursively)."""
    def expand(sub):
        return _expand_templates(sub, transclude, depth)
    out, i = [], 0
    while True:
        j = text.find('{{', i)
        if j < 0:
            out.append(text[i:])
            return ''.join(out)
        end = _find_close(text, j, '{{', '}}')
        if end < 0:
            out.append(text[i:])
            return ''.join(out)
        out.append(text[i:j])
        out.append(render_template(text[j + 2:end - 2], expand, transclude, depth))
        i = end


def _convert_links(text):
    """Turn wiki and external links into their visible text; drop files/categories."""
    def internal(match):
        target, _, label = match.group(1).partition('|')
        target = target.strip()
        low = target.lower().lstrip(':')
        if low.startswith(('file:', 'image:', 'media:')):
            return ''
        if low.startswith('category:') and not target.startswith(':'):
            return ''
        if re.match(r'^[a-z]{2}(-[a-z]+)?:', low):
            return ''  # interlanguage link
        label = label.split('|')[-1] if label else target.lstrip(':').split('#')[0]
        return label or target
    prev = None
    while prev != text:  # nested links inside file captions
        prev = text
        text = re.sub(r'\[\[([^\[\]]*)\]\]', internal, text)
    return re.sub(r'\[(https?://\S+)(?: ([^\]]*))?\]',
                  lambda m: m.group(2) or '', text)


def _cell_text(cell):
    """Strip a leading ``attr="x" |`` block from a table cell and tidy it."""
    attr, sep, content = cell.partition('|')
    if sep and re.search(r'\w+\s*=\s*', attr) and '[' not in attr:
        cell = content
    cell = re.sub(r'<br\s*/?>', ' / ', cell)
    return ' '.join(cell.split()).replace('|', '/')


def _table_rows(body):
    """Parse the inside of ``{| ... |}`` into (caption, rows-of-cells, header flags)."""
    rows, caption, current = [], '', None
    for line in body.split('\n')[1:]:  # first line holds table attributes
        s = line.strip()
        if not s:
            continue
        if s.startswith('|+'):
            caption = _cell_text(s[2:])
        elif s.startswith('|-'):
            current = None
        elif s[0] in '|!':
            if current is None:
                current = []
                rows.append(current)
            sep = '!!' if s[0] == '!' else '||'
            current.extend(_cell_text(c) for c in s[1:].split(sep))
        elif current:
            current[-1] = (current[-1] + ' ' + _cell_text(s)).strip()
    return caption, [r for r in rows if any(r)]


def render_table(body, nested):
    """Render one wikitable as a Markdown table (or a compact line if nested)."""
    caption, rows = _table_rows(body)
    if nested:
        return '; '.join(' '.join(c for c in r if c) for r in rows)
    if not rows:
        return ''
    width = max(len(r) for r in rows)
    lines = ['', caption] if caption else ['']
    for n, row in enumerate(rows):
        row = row + [''] * (width - len(row))
        lines.append('| ' + ' | '.join(row) + ' |')
        if n == 0:
            lines.append('|' + '---|' * width)
    return '\n'.join(lines) + '\n'


def _convert_tables(text):
    """Convert tables innermost-first so nested tables become single cells."""
    pattern = re.compile(r'^[ \t]*\{\|((?:(?!\{\|).)*?)^[ \t]*\|\}', re.S | re.M)
    while True:
        m = pattern.search(text)
        if not m:
            return text
        before = text[:m.start()]
        nested = len(re.findall(r'^[ \t]*\{\|', before, re.M)) > len(
            re.findall(r'^[ \t]*\|\}', before, re.M))
        text = before + render_table(m.group(1), nested) + text[m.end():]


def wikitext_to_text(text, transclude=None):
    """Convert raw page wikitext into readable Markdown-ish text.

    ``transclude(name)`` is called for ``{{:name}}`` and should return that
    page's wikitext or ``None``. The result has normalised blank lines and no
    trailing whitespace; it is deterministic for identical inputs.
    """
    text = _strip_noinclude(text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'<ref[^>/]*/>|<ref[^>]*>.*?</ref>', '', text, flags=re.S)
    text = re.sub(r'<gallery[^>]*>.*?</gallery>', '', text, flags=re.S)
    text = re.sub(r'__[A-Z]+__', '', text)
    text = _expand_templates(text, transclude)
    text = _convert_links(text)
    text = _convert_tables(text)
    text = re.sub(r"'''(.+?)'''", r'**\1**', text)
    text = re.sub(r"''(.+?)''", r'*\1*', text)
    text = re.sub(r'^(=+)\s*(.*?)\s*\1\s*$',
                  lambda m: '#' * min(len(m.group(1)), 6) + ' ' + m.group(2), text, flags=re.M)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</?(span|div|sup|sub|small|big|center|code|nowiki|p|u|s|font|abbr)[^>]*>', '', text)
    text = re.sub(r'^([*#]+)\s*', lambda m: '  ' * (len(m.group(1)) - 1) +
                  ('1. ' if m.group(1)[-1] == '#' else '- '), text, flags=re.M)
    text = re.sub(r'^;\s*(.*)$', r'**\1**', text, flags=re.M)
    text = re.sub(r'^:+\s*', '', text, flags=re.M)
    text = html.unescape(text).replace('\xa0', ' ')
    lines = [line.rstrip() for line in text.split('\n')]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip() + '\n'


def first_sentence(text, limit=180):
    """Return the first prose sentence of converted text, for the index."""
    for line in text.split('\n'):
        s = line.strip()
        if not s or s[0] in '#|-<>' or s.startswith(('**Infobox', '1. ')) or s[0].isdigit():
            continue
        if s.startswith('*') and not s.startswith('**'):
            continue  # italic hatnote such as "For X, see Y."
        s = re.sub(r'\*+', '', s)
        m = re.match(r'(.+?[.!?])(\s|$)', s)
        s = m.group(1) if m else s
        return s if len(s) <= limit else s[:limit - 3].rstrip() + '...'
    return '(no summary)'
