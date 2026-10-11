-- Append all registered engine events and bridge actions to a durable server journal.
-- Tick events use lossless runs (first_tick, last_tick, count) rather than 60 rows/sec.
local json = require("serialization")
local M = {unsupported={}}
local first_tick, last_tick
local fresh_load = true
local filename = "recursive-factorio/events.jsonl"
function M.record(kind, data)
    storage.journal = storage.journal or {}
    storage.journal[#storage.journal+1] = helpers.table_to_json({tick=game.tick,kind=kind,data=json.copy(data)}) .. "\n"
end
function M.flush()
    if first_tick then
        M.record("on_tick",{first_tick=first_tick,last_tick=last_tick,count=last_tick-first_tick+1})
        first_tick=nil
    end
    if storage.journal and #storage.journal>0 then
        helpers.write_file(filename,table.concat(storage.journal),true,0)
        storage.journal={}
    end
end
local names={}
for name, id in pairs(defines.events) do names[id]=name end
for id, name in pairs(names) do
    if id ~= defines.events.on_tick then
        local ok = pcall(script.on_event,id,function(event) M.record(names[event.name] or "unknown",event) end)
        if not ok then M.unsupported[#M.unsupported+1]=name end
    end
end
script.on_event(defines.events.on_tick,function(event)
    if fresh_load then
        fresh_load=false
        M.record("session_started",{bridge_version="0.3.0",unsupported=M.unsupported})
    end
    first_tick=first_tick or event.tick
    last_tick=event.tick
    if event.tick%60==0 or (storage.journal and #storage.journal>=256) then M.flush() end
end)
script.on_init(function() M.record("on_init",{}) end)
script.on_configuration_changed(function(event) M.record("on_configuration_changed",event) end)
return M
