#!/usr/bin/env python3
"""Dump exact recipe, technology, entity and item facts from Factorio into knowledge/prototypes.json.

Starts a disposable base-game episode server (never the live sandbox), reads
every non-hidden recipe and technology plus the entities/items that matter for
red, green and blue science through the frozen actuator queries, and writes a
deterministic JSON file the hive can read offline. Usage:
``.venv/bin/python scripts/dump_prototypes.py [--out knowledge/prototypes.json]``.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.episode import default_live_data  # noqa: E402
from harness.server import EpisodeServer  # noqa: E402

ENTITIES = ('assembling-machine-1', 'assembling-machine-2', 'stone-furnace', 'steel-furnace', 'burner-mining-drill',
            'electric-mining-drill', 'burner-inserter', 'inserter', 'long-handed-inserter', 'fast-inserter',
            'transport-belt', 'underground-belt', 'splitter', 'fast-transport-belt', 'offshore-pump', 'boiler',
            'steam-engine', 'small-electric-pole', 'medium-electric-pole', 'lab', 'pipe', 'pipe-to-ground',
            'wooden-chest', 'iron-chest', 'character')


def dump(out):
    """Read facts from a fresh seeded world and write them to ``out`` as sorted JSON."""
    with tempfile.TemporaryDirectory(dir=default_live_data()) as tmp, \
            EpisodeServer(Path(tmp) / 'world', 1, default_live_data()) as server:
        os.environ['FACTORIO_CONNECTION_FILE'] = str(Path(tmp) / 'world/connection.json')
        from actuator import queries
        actor = server.lua('return game.surfaces[1].create_entity{name="character",position={0,0},force="player"}.unit_number')
        recipes = queries.recipes(actor)
        items = sorted({p['name'] for r in recipes.values() for p in r['products'] + r['ingredients'] if p['type'] == 'item'})
        facts = {'source': 'live Factorio base game, fresh map; enabled = available at game start',
                 'recipes': recipes, 'technologies': queries.technologies(actor)['technologies'],
                 'entities': queries.entity_prototypes(actor, ENTITIES), 'items': queries.item_facts(actor, items)}
    Path(out).write_text(json.dumps(facts, indent=1, sort_keys=True) + '\n')
    return facts


def main(argv=None):
    """Parse ``--out`` and write the dump, printing a one-line summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(ROOT / 'knowledge/prototypes.json'))
    args = parser.parse_args(argv)
    facts = dump(args.out)
    print(f"wrote {args.out}: {len(facts['recipes'])} recipes, {len(facts['technologies'])} technologies, "
          f"{len(facts['entities'])} entities, {len(facts['items'])} items")


if __name__ == '__main__':
    main()
