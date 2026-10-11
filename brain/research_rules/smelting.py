"""Batch smelting for iron and copper, with inventory-backed fuel and output collection."""
from brain.logic import decision, inventory_count, entity_item_count, own_entities, distance, move_or_act


def transfer(player, entity, inventory, item, count, kind='put'):
    """Approach a machine and plan a paced, inventory-costed transfer."""
    return move_or_act(player,{'kind':kind,'player':player['name'],'surface':player['surface'],
        'unit_number':entity['unit_number'],'position':entity['position'],'inventory':inventory,'entity_name':entity['name'],
        'item':item,'count':count},2.7)


def ensure_plates(state, player, item, target, experience=None):
    """Plan smelting until target metal plates are held; avoid mixing furnace inputs."""
    from brain.actions import build_furnace, mine_coal
    from brain.logic import mining_decision
    held = inventory_count(player,item)
    if held >= target:
        return None
    furnaces=sorted(own_entities(state,player,'furnace'),key=lambda f:distance(f['position'],player['position']))
    if not furnaces:
        return build_furnace(state,player,experience)
    furnace=furnaces[0]
    ore=item.replace('plate','ore')
    remaining=target-held
    for metal in ('iron-plate','copper-plate'):
        output=entity_item_count(furnace,'furnace_result',metal)
        loaded=entity_item_count(furnace,'furnace_source',metal.replace('plate','ore'))
        if output and (metal!=item or output>=min(8,remaining) or loaded==0):
            return decision('collect_'+metal,'Collect a smelted batch.',
                            transfer(player,furnace,'furnace_result',metal,output,'take'))
    wrong=entity_item_count(furnace,'furnace_source','copper-ore' if ore=='iron-ore' else 'iron-ore')
    loaded=entity_item_count(furnace,'furnace_source',ore)
    fuel=entity_item_count(furnace,'fuel','coal')
    if fuel<2:
        coal=inventory_count(player,'coal')
        if coal<4:
            return mine_coal(state,player,experience,8-coal)
        return decision('fuel_furnace','Load a coal batch.',transfer(player,furnace,'fuel','coal',coal))
    if wrong:
        return decision('smelting','Finish the previous metal batch before changing inputs.',{'kind':'wait','duration':4})
    output=entity_item_count(furnace,'furnace_result',item)
    needed=max(0,remaining-loaded-output)
    ore_held=inventory_count(player,ore)
    if needed and ore_held:
        return decision('load_'+ore,'Load a smelting batch.',transfer(player,furnace,'furnace_source',ore,min(needed,ore_held)))
    if needed:
        return mining_decision(state,player,ore,experience,min(16,needed))
    return decision('smelting','Wait for a measured output batch.',{'kind':'wait','duration':4})
