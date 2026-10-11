"""Exact steady-state material balances and machine sizing for Factorio blueprints.

Uses an original two-phase rational simplex solver. Kirk McDonald's calculator is
the design reference for separating recipe flows, surplus and machine capacities;
no upstream implementation is copied. Layout and execution are separate modules.
"""
from collections import defaultdict
from fractions import Fraction
import math
import time


def number(value):
    """Convert a finite numeric value to an exact rational using its decimal spelling."""
    result=Fraction(str(value))
    return result


def linear_minimum(matrix, targets, costs, limit=2000, timeout=5):
    """Minimize costs*x under matrix*x=targets and x>=0 using two-phase simplex.

    Targets must be nonnegative. Infeasible, unbounded and excessive pivot problems
    raise ValueError rather than returning a plausible but invalid production plan.
    All pivots and comparisons are exact, with Bland ordering to avoid cycling.
    """
    expires=time.monotonic()+timeout
    rows=len(targets); columns=len(costs)
    if timeout<=0 or rows>500 or columns>2000:raise ValueError('solver time/size budget exceeded')
    if not rows or any(len(row)!=columns for row in matrix):
        raise ValueError('invalid balance matrix')
    if any(number(b)<0 for b in targets):
        raise ValueError('negative targets are unsupported')
    tableau=[[number(v) for v in row]+[Fraction(int(i==j)) for j in range(rows)]+[number(targets[i])]
             for i,row in enumerate(matrix)]
    basis=[columns+i for i in range(rows)]

    def pivot(row, column, objective=None):
        scale=tableau[row][column]
        tableau[row]=[v/scale for v in tableau[row]]
        for i in range(len(tableau)):
            if time.monotonic()>=expires:raise TimeoutError('blueprint solver time budget exceeded')
            if i!=row:
                factor=tableau[i][column]
                tableau[i]=[a-factor*b for a,b in zip(tableau[i],tableau[row])]
        if objective is not None:
            factor=objective[column]
            objective[:]=[a-factor*b for a,b in zip(objective,tableau[row])]
        basis[row]=column

    def optimize(weights):
        objective=[number(c) for c in weights]+[Fraction(0)]
        for row,basic in zip(tableau,basis):
            factor=number(weights[basic])
            objective=[a-factor*b for a,b in zip(objective,row)]
        for _ in range(limit):
            if time.monotonic()>=expires:raise TimeoutError('blueprint solver time budget exceeded')
            entering=next((j for j,v in enumerate(objective[:-1]) if v<0),None)
            if entering is None:
                return objective
            leaving=[(row[-1]/row[entering],basis[i],i) for i,row in enumerate(tableau) if row[entering]>0]
            if not leaving:
                raise ValueError('unbounded production problem')
            pivot(min(leaving)[2],entering,objective)
        raise ValueError('production solver pivot limit exceeded')

    phase=optimize([0]*columns+[1]*rows)
    if phase[-1]!=0:
        raise ValueError('infeasible production targets')
    for i in range(len(tableau)-1,-1,-1):
        if basis[i]>=columns:
            entering=next((j for j in range(columns) if tableau[i][j]!=0),None)
            if entering is None:
                del tableau[i];del basis[i]
            else:
                pivot(i,entering)
    tableau[:]=[row[:columns]+[row[-1]] for row in tableau]
    optimize(costs)
    result=[Fraction(0)]*columns
    for row,basic in zip(tableau,basis):result[basic]=row[-1]
    if any(sum(number(a)*x for a,x in zip(row,result))!=number(b) for row,b in zip(matrix,targets)):
        raise ValueError('solver balance verification failed')
    return result


def solve(targets, recipes, machines, raw_inputs=None, input_costs=None):
    """Calculate crafts/s, raw inputs, surplus, I/O and rounded machine counts.

    Recipes supply ingredients/products, energy seconds, category and optional
    explicit machine selection. Machines supply name, speed, categories, power_w,
    and optional fuel_item/fuel_value_j. Recipe alternatives and joint products are
    balanced together; disabled recipes are excluded. Electricity and burner fuel
    are calculated from active utilization. Modules can be represented by effective
    speed/productivity facts. Rates are steady-state capacities, not proof of live
    throughput; startup inventory for catalytic loops and transport remain separate.
    """
    targets={k:number(v) for k,v in targets.items()}
    if not targets or any(v<=0 for v in targets.values()):
        raise ValueError('output targets must be positive rates per second')
    modeled=[]
    for name,recipe in sorted(recipes.items()):
        if not recipe.get('enabled',True):continue
        candidates=[m for m in machines if recipe.get('machine')==m['name'] or
                    (not recipe.get('machine') and recipe.get('category','crafting') in m.get('categories',[]))]
        if not candidates:continue
        machine=max(candidates,key=lambda m:number(m['speed']))
        speed=number(machine['speed']);time=number(recipe['energy'])
        if speed<=0 or time<=0:raise ValueError('machine speed and recipe time must be positive')
        inputs=defaultdict(Fraction);outputs=defaultdict(Fraction)
        for ing in recipe['ingredients']:inputs[ing['name']]+=number(ing['amount'])
        productivity=number(machine.get('productivity',0))
        for product in recipe['products']:
            amount=number(product.get('amount',(product.get('amount_min',0)+product.get('amount_max',0))/2))
            probability=number(product.get('probability',product.get('independent_probability',1)))
            ignored=number(product.get('ignored_by_productivity',0))
            outputs[product['name']]+=probability*(amount+max(0,amount-ignored)*productivity)
        fuel=machine.get('fuel_item')
        if fuel:
            value=number(machine.get('fuel_value_j',0))
            if value<=0:raise ValueError('fuel energy must be supplied for burner machines')
            inputs[fuel]+=number(machine.get('power_w',0))*time/speed/value
        modeled.append((name,recipe,machine,dict(inputs),dict(outputs),time/speed))
    produced={item for _,_,_,_,out,_ in modeled for item in out}
    consumed={item for _,_,_,ins,_,_ in modeled for item in ins}
    raw=sorted(set(raw_inputs) if raw_inputs is not None else consumed-produced)
    items=sorted(produced|consumed|set(targets)|set(raw))
    surplus=sorted(produced)
    matrix=[]
    for item in items:
        row=[out.get(item,Fraction(0))-ins.get(item,Fraction(0)) for _,_,_,ins,out,_ in modeled]
        row += [Fraction(int(item==r)) for r in raw]
        row += [Fraction(-int(item==s)) for s in surplus]
        matrix.append(row)
    costs=[Fraction(1,1000)*time for _,_,_,_,_,time in modeled]
    costs += [number((input_costs or {}).get(r,1)) for r in raw]+[Fraction(0)]*len(surplus)
    if any(c<0 for c in costs):raise ValueError('costs must be nonnegative')
    rates=linear_minimum(matrix,[targets.get(i,Fraction(0)) for i in items],costs)
    details=[];electric=Fraction(0)
    for rate,(name,recipe,machine,ins,out,seconds) in zip(rates,modeled):
        if not rate:continue
        utilization=rate*seconds
        count=math.ceil(utilization)
        if not machine.get('fuel_item'):
            electric+=number(machine.get('power_w',0))*utilization+number(machine.get('drain_w',0))*count
        details.append({'recipe':name,'machine':machine['name'],'crafts_per_second':str(rate),
                        'machines':count,'utilization':str(utilization),
                        'capacity_crafts_per_second':str(Fraction(count)/seconds),
                        'inputs':{k:str(v*rate) for k,v in ins.items()},
                        'outputs':{k:str(v*rate) for k,v in out.items()},
                        'ingredients':recipe['ingredients'],'products':recipe['products'],
                        'width':machine.get('width',3),'height':machine.get('height',3)})
    start=len(modeled)
    return {'targets':{k:str(v) for k,v in targets.items()},'recipes':details,
            'raw_inputs':{k:str(v) for k,v in zip(raw,rates[start:start+len(raw)]) if v},
            'surplus':{k:str(v) for k,v in zip(surplus,rates[start+len(raw):]) if v},
            'electric_watts':str(electric),
            'assumptions':['steady-state rates','effective machine facts supplied by caller',
                           'transport and startup inventory must be validated separately'],
            'reference':'https://github.com/KirkMcDonald/kirkmcdonald.github.io/tree/349ebfb5f0fe09145169b4b47bc1771f55c1a896'}
