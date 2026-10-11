"""Python plans native movement; the frozen actuator applies honest game actions."""
import math
from actuator import actions, queries


def walking_instruction(position, target, stop_distance, speed, confident=False):
    """Choose an eight-direction leg and bounded duration, without crossing the target."""
    dx, dy = target['x'] - position['x'], target['y'] - position['y']
    remaining = max(0, math.hypot(dx, dy) - stop_distance)
    if not remaining:
        return {'direction':'north','duration':0}
    if speed <= 0:
        raise ValueError('game or actor is not moving')
    if abs(dx) > 2 * abs(dy):
        direction, leg = ('east' if dx > 0 else 'west'), abs(dx)
    elif abs(dy) > 2 * abs(dx):
        direction, leg = ('south' if dy > 0 else 'north'), abs(dy)
    else:
        direction = ('south' if dy > 0 else 'north') + ('east' if dx > 0 else 'west')
        leg = min(abs(dx), abs(dy)) * math.sqrt(2)
    return {'direction':direction,'duration':min(8 if confident else 2, min(leg, remaining) / speed)}


def mining_duration(count, mining_time, speed, progress, amount, game_speed, confident):
    """Estimate a batch's wall time from prototype speed/progress; cap uncertain work."""
    if speed <= 0 or game_speed <= 0:
        raise ValueError('game or actor cannot mine')
    cycles = min(max(1,count),amount)
    estimate = max(0,cycles-min(1,max(0,progress))) * mining_time / speed / game_speed
    return min(8 if confident else 2, estimate + .05)


def route_samples(position, plan, speed):
    """Sample a straight leg at half-tile spacing for engine collision checks."""
    vectors={'north':(0,-1),'northeast':(1,-1),'east':(1,0),'southeast':(1,1),
             'south':(0,1),'southwest':(-1,1),'west':(-1,0),'northwest':(-1,-1)}
    dx,dy=vectors[plan['direction']]
    norm=math.hypot(dx,dy)
    distance=plan['duration']*speed
    return [{'x':position['x']+dx/norm*d,'y':position['y']+dy/norm*d}
            for d in [i*.5 for i in range(2,math.ceil(distance*2)+1)]]


def execute(actor_id, action):
    """Start a native instruction or apply a costed transfer; caller owns duration/stop.

    Every game interaction goes through the frozen ``actuator`` package, which
    enforces reach, inventory costs and real crafting/mining time.
    """
    kind = action['kind']
    if kind == 'halt':
        return actions.halt(actor_id, action.get('cancel_crafting', False))
    if kind == 'wait':
        result = actions.halt(actor_id)
        return {**result, 'duration': min(8, max(0, action.get('duration', 0)))}
    if kind == 'plan_power':
        from brain.research_rules.power import discover_layout
        return discover_layout(actor_id)
    if kind == 'research':
        return actions.research(actor_id, action['technology'])
    if kind == 'set_recipe':
        return actions.set_recipe(actor_id, action['position'], action['recipe'], action.get('unit_number'))
    if kind == 'move':
        state = queries.actor_state(actor_id)
        speed = state['running_speed'] * 60 * state['game_speed']
        candidate = walking_instruction(state['position'], action['position'], action.get('stop_distance', 1), speed, True)
        samples = route_samples(state['position'], candidate, speed)
        clear = queries.can_place(actor_id, [{'name': 'character', 'position': p} for p in samples])
        enemies = queries.count_entities(actor_id, {'force': 'enemy', 'position': state['position'],
                                                    'radius': candidate['duration'] * speed + 24})
        confident = bool(samples) and all(clear) and enemies == 0
        target, stop_distance = action['position'], action.get('stop_distance', 1)
        if samples and not all(clear):
            from brain.navigation import waypoint
            target = waypoint(actor_id, state['position'], target, stop_distance)
            stop_distance = 0
            confident = enemies == 0
        plan = walking_instruction(state['position'], target, stop_distance, speed, confident)
        result = actions.walk(actor_id, plan['direction']) if plan['duration'] > 0 else actions.halt(actor_id)
        return {**result, **plan, 'confidence': 'high' if confident else 'low'}
    if kind in ('mine', 'mine_tree'):
        state = queries.actor_state(actor_id)
        enemies = queries.count_entities(actor_id, {'force': 'enemy', 'position': state['position'], 'radius': 32})
        result = actions.mine(actor_id, action['position'], action['resource'])
        confident = enemies == 0 and state['health'] >= 75
        amount = 1 if kind == 'mine_tree' else result.get('amount') or 1
        duration = mining_duration(action.get('count', 1), result['mining_time'], state['mining_speed'],
                                   state['mining_progress'], amount, state['game_speed'], confident)
        return {**result, 'duration': duration, 'resource': action['resource'], 'confidence': 'high' if confident else 'low'}
    if kind == 'craft':
        if not isinstance(action.get('count'), int) or not 1 <= action['count'] <= 100:
            raise ValueError('craft count must be 1..100')
        actions.halt(actor_id)
        result = actions.craft(actor_id, action['recipe'], action['count'])
        speed = queries.tick()['speed']
        return {**result, 'seconds': result['game_seconds'] / speed, 'duration': min(8, result['game_seconds'] / speed + .05)}
    if kind == 'build':
        actions.halt(actor_id)
        return actions.build(actor_id, action['item'], action['position'], action.get('direction') or 'north')
    if kind not in ('put', 'take'):
        raise ValueError('unsupported action')
    inventory = INVENTORIES.get(action.get('inventory'), action.get('inventory'))
    actions.halt(actor_id)
    if kind == 'put':
        result = actions.put(actor_id, action['position'], action['item'], action['count'], inventory, action.get('unit_number'))
    else:
        result = actions.take(actor_id, action['position'], action['item'], action['count'], inventory, action.get('unit_number'))
    if not result['ok']:
        result['error'] = 'destination full or incompatible; existing contents preserved'
    return {**result, 'duration': min(1.2, .3 + .03 * result['transferred'])}


INVENTORIES = {'furnace_source': 'crafter_input', 'furnace_result': 'crafter_output'}
