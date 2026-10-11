# memory

A dedicated CortexDB (v0.9.9) for the hive's shared memory. It is separate from
OpenHuman's `cortexdb-local`.

```sh
./factorio memory up                      # docker compose; key in server/data/memory.json
./factorio memory remember lesson "..."   # kinds: lesson failure idea result goal
./factorio memory recall "question" [--kind failure]
./factorio memory list --kind result --limit 10
./factorio memory down                    # data stays in server/data/cortexdb
```

Every worktree, including tinyrsi candidates, shares the primary checkout's
store. The loop's scorer writes one `result` per scored seed. Enrichment and
embeddings call OpenRouter (`OPENROUTER_API_KEY`) with one cheap model
(`FACTORIO_MEMORY_MODEL`, default `z-ai/glm-5.3-flash`), so keep writes short.
To reset, stop the store and delete `server/data/cortexdb`.
