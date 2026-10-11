# Power actions

`build_steam_power.py` plans the next inventory-backed component in the pump,
pipes, boiler, engine, pole and lab chain. It delegates pure planning to
`brain.research_rules.power`; execution checks live placement.
