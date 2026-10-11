"""Create, analyze, save, export, place and execute calculated Factorio blueprints.

The solver owns throughput/math; the layout module owns physical production cells.
This module validates plans and provides persistence, Factorio exchange strings,
safe ghost placement and inventory-costed execution through the existing brain.
"""
import base64
from collections import Counter
from dataclasses import dataclass, field
import json
from html import escape
import math
from pathlib import Path
import zlib
import time

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
        expires=time.monotonic()+5
        if not self.label or len(self.entities)>5000:raise ValueError('invalid blueprint label or size')
        identifiers=set();boxes=[]
        for e in self.entities:
            if time.monotonic()>=expires:raise TimeoutError('blueprint validation exceeded 5s')
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
            ox,oy=0,0
            if e['name']=='offshore-pump':
                ox,oy={0:(0,-.5),4:(.5,0),8:(0,.5),12:(-.5,0)}.get(code,(0,0))
            box=(pos['x']+ox-w/2,pos['y']+oy-h/2,pos['x']+ox+w/2,pos['y']+oy+h/2)
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

    def render_svg(self, path):
        """Render a portable layout preview with entity/recipe descriptions in hover titles."""
        if not self.entities:raise ValueError('empty blueprint has no layout preview')
        xs=[e['position']['x'] for e in self.entities];ys=[e['position']['y'] for e in self.entities]
        left,top=min(xs)-4,min(ys)-4;width=max(xs)-left+4;height=max(ys)-top+4
        scale=28;colors={'production':'#3977c4','input_buffer':'#f4b54b','output_buffer':'#62b98b','power':'#c9a4ef'}
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width*scale}" height="{height*scale+40}" viewBox="0 0 {width*scale} {height*scale+40}">',
             '<rect width="100%" height="100%" fill="#f5f7fa"/>',f'<text x="12" y="24" font-family="sans-serif" font-size="16">{escape(self.label)}</text>']
        for e in self.entities:
            w,h=DIMENSIONS.get(e['name'],(1,1));x=(e['position']['x']-left-w/2)*scale;y=(e['position']['y']-top-h/2)*scale+35
            color=colors.get(e.get('role'),'#8a9ba8')
            description=escape(e['name']+' '+e.get('recipe','')+' '+e.get('role',''))
            svg.append(f'<rect x="{x}" y="{y}" width="{w*scale}" height="{h*scale}" rx="3" fill="{color}" stroke="#263445"><title>{description}</title></rect>')
        svg.append('</svg>');path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(''.join(svg));return path

    def save(self, path):
        """Save validated JSON with placement history; directories are created if needed."""
        self.validate();path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        from brain.timeouts import deadline
        with deadline(5,'save blueprint'):
            path.write_text(json.dumps({'schema':1,'label':self.label,'entities':self.entities,
                                       'analysis':self.analysis,'placed':self.placed},indent=2,allow_nan=False)+'\n')
        return path

    @classmethod
    def load(cls, path):
        """Load and validate a saved plan; unsupported schemas raise ValueError."""
        from brain.timeouts import deadline
        with deadline(5,'load blueprint'):
            if Path(path).stat().st_size>2_000_000:raise ValueError('saved blueprint exceeds size budget')
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
        expires=time.monotonic()+5
        from brain.research_rules.recipes import ensure_item
        for part in self.positioned(anchor):
            if time.monotonic()>=expires:raise TimeoutError('blueprint action planning exceeded 5s')
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
        from actuator import actions, queries
        rows=self.positioned(anchor)
        for row in rows:
            d=row.get('direction','north');row['direction']=d if isinstance(d,str) else DIRECTION_NAMES[d]
        if not all(queries.can_place(actor_id,rows)):raise RuntimeError('blueprint site occupied')
        return actions.place_ghosts(actor_id,rows)

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


def ideate(targets, recipes, variants):
    """Compare explicit machine/supply/inserter configurations for the same output target.

    Variants contain machines and optional design arguments. Results are ranked by
    entity count then electricity, with complete assumptions retained for review.
    """
    from fractions import Fraction
    if not 1<=len(variants)<=20:raise ValueError('supply 1..20 blueprint variants')
    expires=time.monotonic()+30;candidates=[]
    for v in variants:
        if time.monotonic()>=expires:raise TimeoutError('blueprint ideation exceeded 30s')
        candidates.append(design(targets,recipes,v['machines'],**{k:value for k,value in v.items() if k!='machines'}))
    return sorted(candidates,key=lambda b:(len(b.entities),Fraction(b.analysis['electric_watts'])))


def live_facts(actor_id, recipe_names, machine_names=('stone-furnace','assembling-machine-1'), allow_locked=False):
    """Read normal-quality recipe/machine facts from Factorio 2.1 for the solver.

    Recipe categories, expected output amounts and energy/speed come from the
    running mods. The explicit allow_locked flag supports future blueprint ideas;
    it retains original availability and does not unlock or execute anything.
    """
    from actuator import queries
    recipes=queries.recipes(actor_id,recipe_names)
    missing=[n for n in recipe_names if n not in recipes]
    if missing:raise RuntimeError(f'unknown recipe {missing}')
    for recipe in recipes.values():
        recipe['categories']=[recipe.pop('category')]
        recipe['products']=[{'name':p['name'],'type':p['type'],
                             'amount':p.get('amount',(p.get('amount_min',0)+p.get('amount_max',0))/2)*p.get('probability',1)}
                            for p in recipe['products']]
    protos=queries.entity_prototypes(actor_id,machine_names)
    available=queries.recipes(actor_id,machine_names)
    machines=[{'name':n,'categories':list(protos[n]['crafting_categories'] or {}),'speed':protos[n]['crafting_speed'],
               'power_w':protos[n]['energy_w'],'width':protos[n]['width'],'height':protos[n]['height'],
               'burner':protos[n]['burner'],'available':available.get(n,{}).get('enabled',False)} for n in machine_names]
    facts={'recipes':recipes,'machines':machines,'coal_j':queries.item_facts(actor_id,['coal'])['coal']['fuel_value']}
    for recipe in facts['recipes'].values():
        recipe['currently_enabled']=recipe['enabled']
        if allow_locked:recipe['enabled']=True
    for machine in facts['machines']:
        machine['categories']=list(machine['categories'])
        machine['width']=int(round(machine['width']));machine['height']=int(round(machine['height']))
        machine['currently_available']=machine['available']
        if allow_locked:machine['available']=True
        if machine.pop('burner'):
            machine.update(fuel_item='coal',fuel_value_j=facts['coal_j'])
    return facts
