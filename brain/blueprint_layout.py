"""Generate non-overlapping item-production cells with sized inserter/buffer interfaces."""
from fractions import Fraction
import math


def production_cells(plan, inserter_rate=.83):
    """Layout 2x2/3x3 machines, ports and copper-wire relay poles.

    Ports are external supply/transfer interfaces; internal factory-wide belt routing
    is not fabricated. Fluid recipes need a dedicated layout and are rejected here.
    Inserter counts are sized to desired rates and bounded by available side slots.
    """
    rate=Fraction(str(inserter_rate))
    if rate<=0:raise ValueError('inserter throughput must be positive')
    entities=[];ports=[];index=0
    for recipe in plan['recipes']:
        if any(i.get('type','item')!='item' for i in recipe['ingredients']+recipe['products']):
            raise ValueError('fluid recipes require a dedicated fluid-routing layout')
        width,height=recipe['width'],recipe['height']
        if width!=height or width not in (2,3):raise ValueError('production-cell footprint must be 2x2 or 3x3')
        for machine in range(recipe['machines']):
            x=4+(width%2)*.5+index*10;y=4+(height%2)*.5
            entities.append({'name':recipe['machine'],'position':{'x':x,'y':y},'recipe':recipe['recipe'],'role':'production'})
            desired_in=sum(Fraction(v) for v in recipe['inputs'].values())/recipe['machines']
            desired_out=sum(Fraction(v) for v in recipe['outputs'].values())/recipe['machines']
            inputs=max(1,math.ceil(desired_in/rate));outputs=max(1,math.ceil(desired_out/rate))
            if max(inputs,outputs)>height:raise ValueError('inserter capacity exceeds available machine-side slots')
            for side,count in ((-1,inputs),(1,outputs)):
                for slot in range(count):
                    offset=slot-(height-1)/2
                    px=x+side*(width/2+.5);py=y+offset
                    entities.append({'name':'inserter','position':{'x':px,'y':py},'direction':'east','role':'input_arm' if side<0 else 'output_arm'})
                    buffer={'name':'iron-chest','position':{'x':px+side,'y':py},'role':'input_buffer' if side<0 else 'output_buffer'}
                    entities.append(buffer)
                    ports.append({'recipe':recipe['recipe'],'machine_index':machine,'direction':'input' if side<0 else 'output',
                                  'position':buffer['position'],'rates':recipe['inputs'] if side<0 else recipe['outputs']})
            # Odd machines need two poles to cover the top and bottom side inserters.
            for dy in (-height/2-.5,height/2+.5):
                entities.append({'name':'small-electric-pole','position':{'x':x,'y':y+dy},'role':'power'})
            if index:
                entities.append({'name':'small-electric-pole','position':{'x':x-5,'y':y-height/2-.5},'role':'power_relay'})
            index+=1
    return entities,ports
