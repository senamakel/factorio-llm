# Rules of the factory

- The brain (`brain/`) plays Factorio 2.1 (base game, peaceful, rich ore) as one
  character, honestly: it walks, mines, crafts with real ingredients and time,
  and builds from its own inventory. All game access goes through the frozen
  `actuator` package (`actuator.actions`, `actuator.queries`). A gate rejects
  any other route (sockets, subprocess, rcon_client, mcp, harness, actuator.rpc,
  exec/eval/importlib, os.system).
- Entry point the scorer calls: `python -m brain episode --actor ID --wall-secs N`
  (`brain/cli.py`). It must keep working; it receives SIGTERM when time is up.
  Print one JSON object per step (`phase`, `result` with `error` on failure) and
  a final one with `stop_reason`; those become next epoch's failures.
- Scoring (frozen): a fresh seeded world per seed (1, 2, 3); the brain plays for
  the wall budget at game speed 4; then the actor is halted and the world runs
  5 more game-minutes. Rates are measured only in that window, so only
  machine-made output counts. Score = min(red/min,100) + min(green/min,100)
  + 5 per milestone reached.
- Ladder: G1 Automation researched; G2 an assembler crafted something; G3 red
  packs made by machines; G4 ore mined and plates smelted by machines;
  G5/G6/G7 10/30/100 red per minute; G8 logistic science pack researched and an
  electric mining drill built; G9 green packs by machines; G10/G11 10/30 green
  per minute (G11 also Automation 2); G12 100 red + 100 green per minute.
- Changes land only if gates pass (honesty + unit tests) and the paired seed
  test says the candidate beats the incumbent. Every change needs a test.
