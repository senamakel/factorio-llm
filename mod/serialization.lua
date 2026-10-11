-- Convert event data to JSON-safe values without retaining live LuaObjects.
local M = {}
function M.copy(value, depth, seen)
    depth = depth or 0
    local kind = type(value)
    if kind == "nil" or kind == "boolean" or kind == "number" or kind == "string" then return value end
    if kind == "function" then return "<function>" end
    local ok, object_name = pcall(function() return value.object_name end)
    if ok and object_name then
        local result = {object_name=object_name}
        for _, key in ipairs({"valid","name","type","unit_number","index","amount","health"}) do
            local good, v = pcall(function() return value[key] end)
            if good and (type(v)=="string" or type(v)=="boolean" or type(v)=="number") then result[key]=v end
        end
        local good, pos = pcall(function() return value.position end)
        if good and pos then result.position={x=pos.x,y=pos.y} end
        local good_surface, s = pcall(function() return value.surface end)
        if good_surface and s then result.surface=s.name end
        return result
    end
    if kind ~= "table" then return tostring(value) end
    if depth > 12 then return {truncated=true,reason="nesting limit"} end
    seen = seen or {}
    if seen[value] then return "<cycle>" end
    seen[value] = true
    local out = {}
    for k, v in pairs(value) do
        if type(k)=="string" or type(k)=="number" then out[k]=M.copy(v,depth+1,seen) end
    end
    seen[value] = nil
    return out
end
return M
