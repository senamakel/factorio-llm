"""Create, analyze, save, export, place and execute calculated Factorio blueprints.

The solver owns throughput/math; the layout module owns physical production cells.
This module validates plans and provides persistence, Factorio exchange strings,
safe ghost placement and inventory-costed execution through the existing brain.
"""
import base64
from collections import Counter
from dataclasses import dataclass, field
import json
import math
from pathlib import Path
import zlib

from brain.logic import decision, distance, move_or_act
from brain.blueprint_solver import solve

DIRECTIONS={'north':0,'northeast':2,'east':4,'southeast':6,'south':8,'southwest':10,'west':12,'northwest':14}
DIMENSIONS={'stone-furnace':(2,2),'assembling-machine-1':(3,3),'lab':(3,3),
            'steam-engine':(3,5),'boiler':(3,2),'offshore-pump':(1,2)}


@dataclass
class Blueprint:
    """A validated physical plan with analysis, explicit interfaces and placement history."""
    label: str
    entities: list
    analysis: dict = field(default_factory=dict)
    placed: dict = field(default_factory=dict)

    def __post_init__(self):
        for i,entity in enumerate(self.entities,1):entity.setdefault('entity_number',i)
        self.validate()

    def validate(self):
        """Reject duplicate IDs, invalid geometry, overlapping footprints and excess size."""
        if not self.label or len(self.entities)>5000:raise ValueError('invalid blueprint label or size')
        identifiers=set();boxes=[]
        for e in self.entities:
            ident=e['entity_number']; pos=e['position']
            if not isinstance(ident,int) or ident<=0 or ident in identifiers:raise ValueError('duplicate or invalid entity number')
            identifiers.add(ident)
            if not isinstance(e['name'],str) or not e['name']:raise ValueError('entity prototype name missing')
            if not all(isinstance(pos[k],(int,float)) and math.isfinite(pos[k]) for k in ('x','y')):raise ValueError('nonfinite entity position')
            direction=e.get('direction','north')
            code=DIRECTIONS[direction] if isinstance(direction,str) else direction
            if code not in DIRECTIONS.values():raise ValueError('unsupported entity direction')
            w,h=DIMENSIONS.get(e['name'],(1,1))
            if code in (4,12):w,h=h,w
            box=(pos['x']-w/2,pos['y']-h/2,pos['x']+w/2,pos['y']+h/2)
            for other in boxes:
                if box[0]<other[2]-1e-8 and box[2]>other[0]+1e-8 and box[1]<other[3]-1e-8 and box[3]>other[1]+1e-8:
                    raise ValueError('blueprint footprints overlap')
            boxes.append(box)
        return True

    def understand(self):
        """Report construction costs, recipes, interfaces, capacity and execution requirements."""
        return {'label':self.label,'entities':len(self.entities),'construction_items':dict(Counter(e['name'] for e in self.entities)),
                'recipes':sorted({e['recipe'] for e in self.entities if e.get('recipe')}),
                'analysis':self.analysis,'placed':len(self.placed)}

    def save(self, path):
        """Save validated JSON with placement history; directories are created if needed."""
        self.validate();path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'schema':1,'label':self.label,'entities':self.entities,
                                   'analysis':self.analysis,'placed':self.placed},indent=2,allow_nan=False)+'\n')
        return path

    @classmethod
    def load(cls, path):
        """Load and validate a saved plan; unsupported schemas raise ValueError."""
        data=json.loads(Path(path).read_text())
        if data.get('schema')!=1:raise ValueError('unsupported blueprint schema')
        return cls(data['label'],data['entities'],data.get('analysis',{}),data.get('placed',{}))

    def factorio_string(self):
        """Export a standard single-blueprint exchange string for Factorio 2.1.21."""
        self.validate();entities=[]
        for e in self.entities:
            row={k:e[k] for k in ('entity_number','name','position','recipe') if k in e}
            d=e.get('direction','north');row['direction']=DIRECTIONS[d] if isinstance(d,str) else d
            entities.append(row)
        raw=json.dumps({'blueprint':{'item':'blueprint','label':self.label,'entities':entities,
                                    'version':(2<<48)|(1<<32)|(21<<16)}},separators=(',',':')).encode()
        return '0'+base64.b64encode(zlib.compress(raw)).decode()

    @classmethod
    def from_factorio_string(cls, value):
        """Import one exchange string, rejecting books, oversized payloads and invalid plans."""
        if not value.startswith('0'):raise ValueError('unsupported blueprint encoding')
        decoder=zlib.decompressobj()
        raw=decoder.decompress(base64.b64decode(value[1:],validate=True),2_000_001)
        if len(raw)>2_000_000 or not decoder.eof:raise ValueError('blueprint payload exceeds limits')
        data=json.loads(raw)
        if 'blueprint' not in data:raise ValueError('single blueprints only')
        bp=data['blueprint']
        return cls(bp.get('label','Imported blueprint'),bp.get('entities',[]))

    def positioned(self, anchor=None):
        """Translate relative entities to a world anchor without changing the saved plan."""
        anchor=anchor or {'x':0,'y':0}
        return [{**e,'position':{'x':e['position']['x']+anchor['x'],'y':e['position']['y']+anchor['y']}} for e in self.entities]

    def next_action(self, state, player, anchor=None, allow_existing=False):
        """Plan one real craft/build/recipe operation; protect unadopted existing builds."""
        from brain.research_rules.recipes import ensure_item
        for part in self.positioned(anchor):
            existing=next((e for e in state.get('entities',[]) if e['name']==part['name'] and
                           e.get('force')==player.get('force','player') and e.get('surface')==player['surface'] and
                           distance(e['position'],part['position'])<.1),None)
            if existing:
                tracked=self.placed.get(str(part['entity_number']))==existing.get('unit_number')
                if not allow_existing and not tracked:return decision('blocked','An existing build occupies the blueprint; explicit adoption is required.')
                if part.get('recipe') and existing.get('recipe')!=part['recipe']:
                    return decision('configure_'+part['recipe'],'Configure the blueprint recipe.',move_or_act(player,
                        {'kind':'set_recipe','unit_number':existing['unit_number'],'entity_name':existing['name'],
                         'position':part['position'],'recipe':part['recipe'],'surface':player['surface']},2.7))
                continue
            needed=ensure_item(state,player,part['name'],1)
            if needed:return needed
            action={'kind':'build','item':part['name'],'position':part['position'],'direction':part.get('direction','north'),
                    'player':player['name'],'surface':player['surface'],'blueprint_entity_number':part['entity_number']}
            return decision('build_'+part['name'],'Place the next inventory-backed blueprint component.',move_or_act(player,action,2.7))
        return None

    def execute_next(self, actor_id, state, player, anchor=None):
        """Execute one planned operation and retain its placed entity ID; caller handles duration."""
        from brain.execution import execute
        plan=self.next_action(state,player,anchor)
        if plan is None:return {'complete':True}
        if plan['phase']=='blocked':raise ValueError(plan['reason'])
        result=execute(actor_id,plan['action'])
        number=plan['action'].get('blueprint_entity_number')
        if number and result.get('unit_number'):self.placed[str(number)]=result['unit_number']
        return {'complete':False,'decision':plan,'result':result}

    def place_ghosts(self, actor_id, anchor=None):
        """Preflight the full footprint, then place build ghosts; no live production is claimed."""
        from brain.io import actor_rpc
        rows=self.positioned(anchor)
        for row in rows:
            d=row.get('direction','north');row['direction']=DIRECTIONS[d] if isinstance(d,str) else d
        return actor_rpc(actor_id,
            'for _,p in ipairs(a) do assert(s.can_place_entity{name=p.name,position=p.position,direction=p.direction,force=e.force},"blueprint site occupied") end; '
            'local out={}; for _,p in ipairs(a) do local g=s.create_entity{name="entity-ghost",inner_name=p.name,position=p.position,direction=p.direction,force=e.force}; '
            'assert(g,"ghost creation failed"); if p.recipe then g.set_recipe(p.recipe) end; out[#out+1]={name=g.ghost_name,position=g.position} end; return out',rows)

    def measure_rates(self, before, after, seconds, anchor=None):
        """Measure output-buffer stock gains per second, separately from calculated capacity."""
        if seconds<=0:raise ValueError('measurement seconds must be positive')
        from brain.logic import item_count
        totals={}
        for part in self.positioned(anchor):
            if part.get('role')!='output_buffer':continue
            def contents(state):
                e=next((e for e in state.get('entities',[]) if e['name']==part['name'] and distance(e['position'],part['position'])<.1),{})
                return e.get('inventories',{}).get('chest',[])
            a,b=contents(before),contents(after)
            names=set(a)|set(b) if isinstance(a,dict) and isinstance(b,dict) else {i['name'] for i in list(a)+list(b)}
            for name in names:totals[name]=totals.get(name,0)+(item_count(b,name)-item_count(a,name))/seconds
        return totals


def create(label, entities, analysis=None):
    """Create a validated blueprint from explicit entities and optional solver/interface facts."""
    return Blueprint(label,json.loads(json.dumps(entities)),analysis or {})


def design(targets, recipes, machines, **options):
    """Solve rates and design powered buffer-fed production cells with explicit I/O ports."""
    from brain.blueprint_layout import production_cells
    plan=solve(targets,recipes,machines,raw_inputs=options.get('raw_inputs'),input_costs=options.get('input_costs'))
    entities,ports=production_cells(plan,options.get('inserter_rate',.83))
    plan.update({'ports':ports,'automatic_material_routing':False,
                 'required_connections':['supply raw input buffers','transfer intermediate outputs between cells','connect electrical supply'],
                 'layout_type':'buffer-fed production cells'})
    return create(options.get('label','Calculated production cells'),entities,plan)
