"""Python grid routing around trees, water and existing factory structures."""
import heapq
import math
from brain.io import actor_rpc


def route(cells, target, stop_distance):
    """Find an eight-direction path from (0,0) to reach; disallow corner cutting."""
    start=(0,0); queue=[(0,0,start)]; costs={start:0}; parents={}
    while queue:
        _,cost,node=heapq.heappop(queue)
        if cost!=costs[node]:continue
        if math.hypot(node[0]-target[0],node[1]-target[1])<=stop_distance:
            path=[]
            while node!=start:path.append(node);node=parents[node]
            return list(reversed(path))
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            next_node=(node[0]+dx,node[1]+dy)
            if not cells.get(next_node,False):continue
            if dx and dy and not (cells.get((node[0]+dx,node[1]),False) and cells.get((node[0],node[1]+dy),False)):continue
            candidate=cost+math.hypot(dx,dy)
            if candidate<costs.get(next_node,math.inf):
                costs[next_node]=candidate;parents[next_node]=node
                estimate=max(0,math.hypot(next_node[0]-target[0],next_node[1]-target[1])-stop_distance)
                heapq.heappush(queue,(candidate+estimate,candidate,next_node))
    raise ValueError('no reachable route around nearby obstacles')


def waypoint(actor_id, position, target, stop_distance):
    """Query local walkability and return the end of the first straight route segment."""
    tx,ty=target['x']-position['x'],target['y']-position['y']
    length=math.hypot(tx,ty)
    if length>96:
        tx,ty=tx/length*64,ty/length*64
        stop_distance=3
    coords=[(x,y) for x in range(min(0,math.floor(tx))-8,max(0,math.ceil(tx))+9)
                  for y in range(min(0,math.floor(ty))-8,max(0,math.ceil(ty))+9)]
    if len(coords)>10000:raise ValueError('route grid exceeds planning budget')
    points=[{'x':position['x']+x,'y':position['y']+y} for x,y in coords]
    flags=actor_rpc(actor_id,'local out={}; for _,pos in ipairs(a) do out[#out+1]=s.can_place_entity{name="character",position=pos,force=e.force} end; return out',points)
    cells=dict(zip(coords,flags));cells[(0,0)]=True
    path=route(cells,(tx,ty),stop_distance)
    if not path:return position
    first=path[0];previous=first;end=first
    for node in path[1:]:
        if (node[0]-previous[0],node[1]-previous[1])!=first:break
        end=node;previous=node
    return {'x':position['x']+end[0],'y':position['y']+end[1]}
