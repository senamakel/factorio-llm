"""Python-owned shoreline layout discovery and inventory-costed steam-power construction."""
import json
import math
import time
from pathlib import Path
from actuator import queries
from brain.logic import decision, distance, move_or_act
from brain.research_rules.recipes import ensure_item

LAYOUT_FILE=Path(__file__).resolve().parents[2]/'server/data/research-layout.json'


def steam_layout(position, direction):
    """Return a connected 2.1 pump/pipes/boiler/engine/pole/lab layout rotated at shore."""
    parts=[('pump','offshore-pump',0,0),('boiler','boiler',2,7.5),
           ('engine','steam-engine',2,3),('pole','small-electric-pole',4,4),('lab','lab',6,4)]
    parts += [(f'water_pipe_{i}','pipe',0,i) for i in range(1,9)]
    parts += [('steam_pipe','pipe',2,6)]
    turns={'north':0,'east':1,'south':2,'west':3}[direction]
    layout=[]
    for role,name,x,y in parts:
        for _ in range(turns): x,y=-y,x
        layout.append({'role':role,'name':name,'position':{'x':position['x']+x,'y':position['y']+y},'direction':direction})
    return layout


def discover_layout(actor_id):
    """Find a collision-free shoreline footprint using short native placement queries."""
    expires=time.monotonic()+25
    state=queries.actor_state(actor_id)
    water={**queries.find_tiles(actor_id,('water','deepwater'),state['position'],256),
           'position':state['position'],'seed':state['seed'],'surface':state['surface']}
    tiles=water['tiles'] or []
    known={(t['x'],t['y']) for t in tiles}
    coastline=[]
    for tile in tiles:
        for direction,dx,dy in (('north',0,-1),('east',1,0),('south',0,1),('west',-1,0)):
            land=(tile['x']-dx,tile['y']-dy)
            if land not in known:
                pos={'x':land[0]+.5,'y':land[1]+.5}
                coastline.append((distance(pos,water['position']),pos,direction))
    for _,pos,direction in sorted(coastline,key=lambda c:c[0])[:500]:
        if time.monotonic()>=expires:raise TimeoutError('shoreline blueprint discovery exceeded 25s')
        layout=steam_layout(pos,direction)
        valid=queries.can_place(actor_id,layout)
        if all(valid):
            from brain.blueprint import create
            create('First research steam and lab',layout,{'layout_type':'connected steam power and lab',
                   'required_connections':['coal in boiler','science in lab']}).save(LAYOUT_FILE.with_name('power-blueprint.json'))
            record={'seed':water['seed'],'surface':water['surface'],'entities':layout}
            LAYOUT_FILE.write_text(json.dumps(record,indent=2)+'\n')
            return {'ok':True,'layout':record}
    raise RuntimeError('No clear connected steam/lab footprint within 256 tiles')


def find_role(state, role):
    """Resolve a planned structure from its observed prototype and position."""
    layout=state.get('power_layout',{}).get('entities',[])
    part=next((p for p in layout if p['role']==role),None)
    if not part:
        return None
    return next((e for e in state.get('entities',[]) if e['name']==part['name'] and
                 distance(e['position'],part['position'])<.1),None)


def build_power(state, player, experience=None):
    """Plan the next missing structure with live crafting costs and placement read-back."""
    if not state.get('power_layout'):
        return decision('plan_power','Find a connected, clear shoreline layout.',{'kind':'plan_power'})
    # Connect fluid machinery before building the pole and lab.
    parts=state['power_layout']['entities']
    order=[p for p in parts if p['name']=='offshore-pump' or p['name']=='pipe']
    order += [p for p in parts if p['name'] not in ('offshore-pump','pipe')]
    from brain.blueprint import create
    blueprint=create('First research steam and lab',order)
    return blueprint.next_action(state,player,allow_existing=True)
