# Brain

All local behavior lives here. Run `.venv/bin/python -m brain --actor ID` for
100 iron plates, or add `--objective research` for the red-science bootstrap.
Use `FACTORIO_CONNECTION_FILE` to select the running sandbox's private config.

- `actions.py` and `action_library/`: public high-level planners, one action per file.
- `logic.py`: iron-chain decisions and common state helpers.
- `research_rules/`: live recipes, batched smelting, shoreline power and unlock gates.
- `observation.py`: bounded resources, recipes, technologies, machines and inventories.
- `execution.py` and `io.py`: Python timing/navigation and short native API adapters.
- `goal.py`, `score.py`, `runner.py`: objectives, rewards and bounded execution.
- `event_store.py`: separate observations/decisions/actions/outcomes and learning.

The research chain produces 50 iron and 10 copper plates, builds a real powered
lab, handcrafts red packs and lets the lab complete Automation. Crafting uses the
engine queue and real ingredients; structures consume inventory; electricity and
research are read back. Transfers approach machines, face them and use paced batches.

Runtime SQLite, layout plans and logs stay in ignored root `server/data/`.
Refresh wiki facts with `.venv/bin/python scripts/enrich_wiki.py`. Run
`./factorio check`; opt-in checks use `FACTORIO_LIVE_TESTS=1 .venv/bin/python -m
unittest scripts.test_brain_live` on disposable surfaces.
