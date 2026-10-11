# harness

Frozen scoring infrastructure for the recursive self-improvement (RSI) loop.

| File | Purpose |
| --- | --- |
| `server.py` | `EpisodeServer`: disposable headless server per episode. Its own write-data dir, a fresh map from a fixed seed (`scripts/world_settings.py`), base game only, free ports. Always stopped on exit. |
| `episode.py` | Plays and measures one episode: stages the candidate `brain/` next to this checkout's frozen packages, spawns the actor, runs `python -m brain episode`, halts the actor, runs the automation window, writes `result.json`, prints `METRIC`/`DIAG`. |
| `milestones.py` | The ladder (G1–G12), window rates and the composite score: `min(red,100) + min(green,100) + 5 × milestones`. |
| `honesty.py` | Static check that `brain/` reaches the game only through `actuator.actions`/`queries`. |
| `gates.py` | The loop's gates on a checkout: honesty, then the offline brain tests (`./factorio gates`). |

Commands:

```sh
./factorio episode --seed 1 --wall-secs 600     # score this checkout's brain
./factorio episode --brain-root PATH --seed 2   # score another checkout's brain
./factorio gates                                # what the loop's gates run
```

Episode output goes to `server/data/episodes/<time>-seed<N>/` unless `--out` is
given: `result.json`, `brain.jsonl`, `brain.err` and the `world/` save. The live
sandbox is never touched. Rates are measured only after the actor is halted, so
they count machine output, not handcrafting.

Verification: `.venv/bin/python -m unittest scripts.test_harness`.
