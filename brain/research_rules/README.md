# Research rules

`bootstrap.py` orders production triggers, power, lab, red packs and Automation.
`recipes.py` resolves live enabled recipes with correct output quantities.
`smelting.py` plans copper/iron batches and close transfers. `power.py` rotates
and validates a connected shoreline footprint, storing it privately with map
seed/surface identity. All decisions are Python; Lua only applies game API calls.

Wiki provenance is in `brain/knowledge/red_science.json`; live data overrides
assumptions. Verify with `scripts.test_research` and `scripts.test_brain_live`.
