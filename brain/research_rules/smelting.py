"""Batch smelting for iron and copper, with inventory-backed fuel and output collection."""
from brain.logic import decision, inventory_count, entity_item_count, own_entities, distance, move_or_act
import math

DEFAULT_FUELS={'coal':4000000,'wood':2000000,'solid-fuel':12000000}


def transfer(player, entity, inventory, item, count, kind='put'):
    """Approach a machine and plan a paced, inventory-costed transfer."""
    return move_or_act(player,{'kind':kind,'player':player['name'],'surface':player['surface'],
        'unit_number':entity['unit_number'],'position':entity['position'],'inventory':inventory,'entity_name':entity['name'],
        'item':item,'count':count},2.7)


def refuel(state, player, entity, experience=None):
    """Use measured fuel energy, retaining the fuel type already occupying the slot."""
    from brain.research_rules.recipes import ensure_item
    values=state.get('fuel_values',DEFAULT_FUELS)
    stock=entity.get('inventories',{}).get('fuel',{})
    counts=stock if isinstance(stock,dict) else {i['name']:i['count'] for i in stock}
    energy=entity.get('remaining_burning_fuel',0)+sum(count*values.get(name,0) for name,count in counts.items())
    if energy>=8000000:return None
    fuel=next((name for name,count in counts.items() if count),'coal')
    if not values.get(fuel):return decision('blocked','Cannot calculate energy for the existing fuel: '+fuel)
    needed=max(1,math.ceil((16000000-energy)/values[fuel]))
    plan=ensure_item(state,player,fuel,needed,experience)
    if plan:return plan
    return decision('fuel_'+entity['name'],'Refuel using the existing compatible fuel.',transfer(player,entity,'fuel',fuel,needed))


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
    fueling=refuel(state,player,furnace,experience)
    if fueling:return fueling
    if wrong:
        return decision('smelting','Finish the previous metal batch before changing inputs.',{'kind':'wait','duration':4})
    output=entity_item_count(furnace,'furnace_result',item)
    needed=max(0,remaining-loaded-output)
    ore_held=inventory_count(player,ore)
    batch=min(16,needed)
    if needed and ore_held>=batch:
        return decision('load_'+ore,'Load a smelting batch.',transfer(player,furnace,'furnace_source',ore,min(needed,ore_held)))
    if needed:
        return mining_decision(state,player,ore,experience,max(1,batch-ore_held))
    return decision('smelting','Wait for a measured output batch.',{'kind':'wait','duration':4})
