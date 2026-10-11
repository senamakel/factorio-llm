# Knowledge and memory

- `knowledge/prototypes.json`: exact live facts from the game — every recipe
  (ingredients, products, seconds, enabled at start), every technology (cost,
  prerequisites, research trigger, unlocked recipes), entity sizes/speeds/power
  and item stack sizes/fuel values. Trust it over memory.
- `knowledge/wiki/INDEX.md` then `knowledge/wiki/<Page>.md`: 70 Factorio wiki
  pages (science packs, machines, inserters, belts, power, mining, research,
  blueprints, tutorials). `knowledge/RATIOS.md`: cited ratio cheat sheet,
  including the machine counts for 100 red + 100 green per minute.
- Shared hive memory (CortexDB), from any checkout:
  `./factorio memory recall "<question>" [--kind lesson|failure|idea|result|goal]`,
  `./factorio memory list --kind result --limit 10`,
  `./factorio memory remember <kind> "<short text>"`. The scorer writes one
  `result` per scored seed. Keep entries short and factual.
- Brain map: `brain/cli.py` (entry), `brain/runner.py` (observe→decide→act
  loop), `brain/observation.py`, `brain/execution.py` (action dicts →
  actuator), `brain/logic.py` + `brain/research_rules/*` (decisions),
  `brain/blueprint*.py` (layout solver), `brain/goal.py`, `brain/score.py`,
  `brain/event_store.py` (SQLite history).
