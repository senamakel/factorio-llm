"""Resolve crafting prerequisites using observed live recipes rather than fixed costs."""
import math
from brain.logic import decision, inventory_count


def ensure_item(state, player, item, count, experience=None, trail=()):
    """Plan the first missing dependency; return None once count items are held.

    Smelt metals and gather raw resources, recursively resolve enabled item recipes,
    and wait for native crafting. Cycles, locked recipes and fluid ingredients are
    explicit blocked decisions. Products with multiple outputs are counted correctly.
    """
    held = inventory_count(player,item)
    if held >= count:
        return None
    if player.get('crafting_queue'):
        return decision('crafting','Wait for the native crafting batch.',{'kind':'wait','duration':2})
    if item in ('iron-plate','copper-plate'):
        from brain.research_rules.smelting import ensure_plates
        return ensure_plates(state,player,item,count,experience)
    if item in ('iron-ore','copper-ore','coal','stone'):
        from brain.logic import mining_decision
        return mining_decision(state,player,item,experience,count-held)
    if item == 'wood':
        from brain.action_library.gathering.mine_wood import mine_wood
        return mine_wood(state,player,count-held)
    if item in trail:
        return decision('blocked','Cyclic recipe dependency: '+item)
    recipe = state.get('recipes',{}).get(item)
    if not recipe or not recipe.get('enabled'):
        return decision('blocked','Recipe is not unlocked: '+item)
    output = sum(p.get('amount',0) for p in recipe['products'] if p['name']==item)
    if output <= 0:
        return decision('blocked','Recipe has no measured output: '+item)
    crafts = math.ceil((count-held)/output)
    for ingredient in recipe['ingredients']:
        if ingredient.get('type','item') != 'item':
            return decision('blocked','Handcrafting fluid recipes is unsupported: '+item)
        plan = ensure_item(state,player,ingredient['name'],ingredient['amount']*crafts,
                           experience,(*trail,item))
        if plan:
            return plan
    return decision('craft_'+item,'Handcraft the required batch of '+item,
                    {'kind':'craft','player':player['name'],'recipe':item,'count':crafts})
