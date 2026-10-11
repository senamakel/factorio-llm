# Knowledge cache

A frozen, offline reference for the agent hive that writes the Python brain.
Agents in the hive only have shell and file-read tools, so everything here is
plain text you can `cat`, `grep` and `sed`. Nothing in this folder is fetched at
runtime, and the brain must not depend on network access to the wiki.

The target is Factorio 2.1 with the Space Age mods enabled, played on Nauvis
only: from a fresh map up to 100 automation (red) and 100 logistic (green)
science packs per minute, then chemical (blue). Wiki pages mention Space Age
content (foundry, other planets, quality); for Nauvis early game ignore anything
marked `(Space Age)` unless it is a change to a base recipe.

## Layout

- `wiki/` — one Markdown file per wiki.factorio.com page, named by slug
  (`Automation (research)` → `Automation_research.md`,
  `Tutorial:Main bus` → `Tutorial_Main_bus.md`).
  - Line 1 is a machine-readable header:
    `<!-- wiki-cache title="…" url="…" revid="…" -->`, followed by the title and
    a `Source:` line with the URL and revision id.
  - Infoboxes are rendered as a `## Infobox` bullet list near the top:
    `Recipe: 5 s; 1 × Copper plate + 1 × Iron gear wheel`, crafting/mining speed,
    energy use, the internal prototype name, `Required technologies`,
    research cost per unit and unit count, or a `Research trigger` for
    trigger technologies. Quality tiers appear only in infoboxes; tables keep
    the normal-quality value.
  - Wiki tables become Markdown tables. Spanning header cells are repeated
    across the columns they cover.
- `wiki/INDEX.md` — every cached page with a one-line summary.
- `RATIOS.md` — a short, hand-checked cheat sheet for red/green science.
  Every number cites the cached page it came from.
- `prototypes.json` — **not yet present**. A separate step will dump the exact
  live recipes and technologies from the running game. When it exists it is the
  source of truth; the wiki is secondary and can lag the game version.

## Searching

```sh
grep -ril "steam engine" knowledge/wiki          # which pages mention it
grep -h "^- Recipe:" knowledge/wiki/*.md          # every recipe line
grep -A12 "^## Infobox" knowledge/wiki/Lab.md     # one page's infobox
```

## Refreshing

From the repository root (the primary checkout owns `.venv`):

```sh
.venv/bin/python scripts/fetch_wiki.py                        # default page set
.venv/bin/python scripts/fetch_wiki.py --pages "Lab" "Boiler"  # subset
.venv/bin/python scripts/fetch_wiki.py --index-only           # rebuild INDEX.md
```

The fetcher uses the MediaWiki API (`wiki.factorio.com/api.php`), a descriptive
User-Agent and a 0.3 s delay between requests. HTTP or API errors abort the run;
missing titles are listed and make it exit non-zero. Unchanged pages are not
rewritten, so a refresh shows up in git as real content changes only. After a
refresh, re-check `RATIOS.md` against the new pages.

Verification: `.venv/bin/python -m unittest scripts.test_fetch_wiki` (offline;
also part of `./factorio check`).
