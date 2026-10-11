"""Fetch Factorio wiki pages into a frozen, offline Markdown cache.

Usage (from the repository root)::

    .venv/bin/python scripts/fetch_wiki.py                 # default page set
    .venv/bin/python scripts/fetch_wiki.py --pages "Lab" "Boiler"
    .venv/bin/python scripts/fetch_wiki.py --index-only    # rebuild INDEX.md

Each page is written to ``knowledge/wiki/<Slug>.md``. Its first line is a
machine-readable header comment with the title, source URL and revision id;
``knowledge/wiki/INDEX.md`` is rebuilt from the headers of every cached file, so
refreshing a subset with ``--pages`` keeps the rest of the index intact.

Only the standard library is used. Requests go to the MediaWiki API with a
descriptive User-Agent and a fixed delay between calls. HTTP and API errors
raise immediately; titles that do not exist are reported and make the process
exit non-zero after the remaining pages are written. Re-running is idempotent:
files whose content is unchanged are not rewritten.
"""
import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.wiki_text import first_sentence, title_to_slug, wiki_url, wikitext_to_text

API_URL = 'https://wiki.factorio.com/api.php'
USER_AGENT = ('recursive-factorio-wiki-cache/1.0 '
              '(offline reference builder; Python urllib; low request rate)')
REQUEST_DELAY = 0.3
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / 'knowledge' / 'wiki'
HEADER_RE = re.compile(r'^<!-- wiki-cache title="(.*?)" url="(.*?)" revid="(\d+)"')

# Early game through logistic (green) science, plus the chemical pack preview.
DEFAULT_PAGES = [
    # Science and research
    'Research', 'Technologies', 'Automation science pack', 'Logistic science pack',
    'Military science pack', 'Chemical science pack', 'Lab',
    # Machines and logistics
    'Assembling machine 1', 'Assembling machine 2', 'Inserters', 'Inserter',
    'Burner inserter', 'Long-handed inserter', 'Fast inserter', 'Transport belt',
    'Underground belt', 'Splitter', 'Transport belts/Physics', 'Burner mining drill',
    'Electric mining drill', 'Furnace', 'Stone furnace', 'Steel furnace',
    'Wooden chest', 'Iron chest',
    # Power
    'Offshore pump', 'Boiler', 'Steam engine', 'Small electric pole',
    'Medium electric pole', 'Power production', 'Pipe', 'Pipe to ground',
    'Electric system', 'Tutorial:Applied power math',
    # Items and resources
    'Iron gear wheel', 'Copper cable', 'Electronic circuit', 'Iron stick',
    'Iron plate', 'Copper plate', 'Steel plate', 'Stone brick', 'Iron ore',
    'Copper ore', 'Coal', 'Stone', 'Wood',
    # Mechanics and guides
    'Mining', 'Crafting', 'Fuel', 'Belt transport system', 'Blueprint', 'Time',
    'Player', 'Tutorial:Main bus', 'Tutorial:Quick start guide',
    # Technologies
    'Automation science pack (research)', 'Steam power (research)',
    'Electronics (research)', 'Automation (research)', 'Logistics (research)',
    'Automation 2 (research)', 'Logistics 2 (research)',
    'Electric mining drill (research)', 'Logistic science pack (research)',
    'Advanced material processing (research)', 'Steel processing (research)',
    'Electric energy distribution 1 (research)', 'Fast inserter (research)',
]


def ssl_context():
    """Return a verifying SSL context, falling back to known CA bundles.

    python.org macOS builds ship without a populated trust store; in that case
    use ``certifi`` when importable, else the system ``/etc/ssl/cert.pem``.
    Verification is never disabled.
    """
    ctx = ssl.create_default_context()
    if ctx.cert_store_stats().get('x509_ca', 0):
        return ctx
    try:
        import certifi  # optional, not required
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    for path in ('/etc/ssl/cert.pem', '/etc/ssl/certs/ca-certificates.crt'):
        if os.path.exists(path):
            return ssl.create_default_context(cafile=path)
    return ctx


class WikiClient:
    """Minimal rate-limited MediaWiki API client.

    ``get_pages(titles)`` returns ``{requested_title: page}`` where ``page`` is a
    dict with ``title``, ``revid`` and ``wikitext`` (after redirects), or
    ``None`` for missing pages. Raises ``RuntimeError`` on HTTP/API errors.
    """

    def __init__(self, delay=REQUEST_DELAY, opener=None):
        """Create a client; ``opener(url) -> bytes`` may be injected for tests."""
        self.delay = delay
        self._opener = opener or self._urlopen
        self._last = 0.0
        self._ctx = None

    def _urlopen(self, url):
        """Fetch ``url`` with the polite User-Agent; raise on any HTTP error."""
        if self._ctx is None:
            self._ctx = ssl_context()
        request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=30, context=self._ctx) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            raise RuntimeError('HTTP %s for %s' % (exc.code, url)) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError('network error for %s: %s' % (url, exc.reason)) from exc

    def query(self, params):
        """Run one API request (honouring the delay) and return decoded JSON."""
        wait = self._last + self.delay - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        url = API_URL + '?' + urllib.parse.urlencode(dict(params, format='json'))
        try:
            data = json.loads(self._opener(url))
        finally:
            self._last = time.monotonic()
        if 'error' in data:
            raise RuntimeError('API error for %s: %s' % (url, data['error']))
        return data

    def get_pages(self, titles):
        """Fetch current wikitext and revision ids for up to 50 titles."""
        data = self.query({'action': 'query', 'prop': 'revisions', 'redirects': 1,
                           'rvprop': 'content|ids', 'rvslots': 'main',
                           'titles': '|'.join(titles)})['query']
        alias = {}
        for step in ('normalized', 'redirects'):
            for item in data.get(step, []):
                alias[item['from']] = item['to']
        by_title = {}
        for page in data.get('pages', {}).values():
            if 'missing' in page or 'invalid' in page or not page.get('revisions'):
                continue
            rev = page['revisions'][0]
            by_title[page['title']] = {'title': page['title'], 'revid': rev['revid'],
                                       'wikitext': rev['slots']['main']['*']}
        result = {}
        for requested in titles:
            final = requested
            for _ in range(5):
                if final not in alias:
                    break
                final = alias[final]
            result[requested] = by_title.get(final)
        return result


def render_page(page, transclude, requested=None):
    """Return the cache file text for one fetched page dict."""
    url = wiki_url(page['title'])
    body = wikitext_to_text(page['wikitext'], transclude)
    lines = ['<!-- wiki-cache title="%s" url="%s" revid="%s" -->'
             % (page['title'], url, page['revid']),
             '# ' + page['title'], '',
             'Source: %s (revision %s)' % (url, page['revid'])]
    if requested and requested != page['title']:
        lines.append('Requested as: %s (redirect)' % requested)
    return '\n'.join(lines) + '\n\n' + body


def write_if_changed(path, text):
    """Write ``text`` to ``path`` only when it differs; return True if written."""
    if path.exists() and path.read_text(encoding='utf-8') == text:
        return False
    path.write_text(text, encoding='utf-8')
    return True


def build_index(out_dir):
    """Rebuild ``INDEX.md`` from the header line of every cached page."""
    entries = []
    for path in sorted(out_dir.glob('*.md')):
        if path.name == 'INDEX.md':
            continue
        text = path.read_text(encoding='utf-8')
        match = HEADER_RE.match(text)
        if not match:
            continue
        body = text.split('\n', 4)[-1]
        entries.append((match.group(1), path.name, first_sentence(body)))
    entries.sort(key=lambda e: e[0].lower())
    lines = ['# Factorio wiki cache index', '',
             'Frozen offline copy of wiki.factorio.com pages (Factorio 2.x). '
             'One file per page; `grep -ril <term> knowledge/wiki` to search.',
             '', '%d pages.' % len(entries), '']
    lines += ['- [%s](%s) — %s' % e for e in entries]
    write_if_changed(out_dir / 'INDEX.md', '\n'.join(lines) + '\n')
    return len(entries)


def fetch(titles, out_dir, client):
    """Fetch ``titles`` into ``out_dir``; return (written, unchanged, missing)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cache = {}

    def transclude(name):
        """Return wikitext for a transcluded page such as ``Infobox:Lab``."""
        if name not in cache:
            page = client.get_pages([name])[name]
            cache[name] = page['wikitext'] if page else None
        return cache[name]

    written, unchanged, missing = [], [], []
    for title in titles:
        page = client.get_pages([title])[title]
        if page is None:
            print('MISSING  %s' % title, file=sys.stderr)
            missing.append(title)
            continue
        path = out_dir / (title_to_slug(page['title']) + '.md')
        changed = write_if_changed(path, render_page(page, transclude, title))
        (written if changed else unchanged).append(path.name)
        print('%s %s -> %s' % ('WROTE   ' if changed else 'SAME    ', title, path.name),
              file=sys.stderr)
    return written, unchanged, missing


def main(argv=None):
    """Command-line entry point; returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--pages', nargs='+', metavar='TITLE',
                        help='fetch only these titles instead of the default set')
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT,
                        help='output directory (default: knowledge/wiki)')
    parser.add_argument('--index-only', action='store_true',
                        help='only rebuild INDEX.md from cached files')
    parser.add_argument('--delay', type=float, default=REQUEST_DELAY,
                        help='seconds between API requests (default 0.3)')
    args = parser.parse_args(argv)
    missing = []
    if not args.index_only:
        written, unchanged, missing = fetch(args.pages or DEFAULT_PAGES, args.out,
                                            WikiClient(delay=args.delay))
        print('%d written, %d unchanged, %d missing'
              % (len(written), len(unchanged), len(missing)), file=sys.stderr)
    count = build_index(args.out)
    print('INDEX.md lists %d pages' % count, file=sys.stderr)
    if missing:
        print('ERROR: missing titles: %s' % ', '.join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
