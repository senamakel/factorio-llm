# loops/factorio-brain

A [tinyrsi](https://github.com/tinyhumansai/tinyrsi) loop: a hive of OpenHuman
agents improves `brain/`, and the frozen harness scores each candidate on
disposable Factorio worlds. Only measured improvements are promoted to `rsi/main`.

| Path | Purpose |
| --- | --- |
| `rsi.json` | Manifest. Git subject `../..` on branch `rsi/main`. The hive may edit `brain/` and the brain tests; `actuator/`, `harness/`, `knowledge/`, `loops/` and the rest are frozen. Paired seed test on seeds 1–3, target 260. Budget $4 per run, $18 total (the other $2 of the $20 cap is left for CortexDB enrichment). |
| `brief.md` | The brief each epoch: the ladder, the score and the task. |
| `hive/` | tinyhivemind package. Seats: `orchestrator` (lead, read-only), `builder` (edits a candidate), `critic` (read-only reviewer). Roles `researcher` and `toolsmith` are declared for v2. Context: rules, knowledge and memory commands. |
| `scorers/episode.py` | Runs the incumbent's `harness.episode` on `$RSI_CANDIDATE` for `$RSI_SEED`, then writes the outcome to hive memory. |
| `gates/` | `honesty.py` and `green.py`, both delegating to `harness.gates`. |

Run (needs `OPENROUTER_API_KEY`, Docker for memory, and a set-up sandbox):

```sh
./factorio memory up
export TINYRSI_HOME=~/.tinyrsi-factorio   # separate $18 ledger
tinyrsi check loops/factorio-brain
tinyrsi score loops/factorio-brain --label baseline
tinyrsi run loops/factorio-brain           # UI on http://127.0.0.1:8787
```

Episode length and speed come from `env` in `rsi.json`
(`EPISODE_WALL_SECS`, `EPISODE_GAME_SPEED`, `EPISODE_WINDOW_MIN`). Raise the wall
time as the factory grows.
