"""Plan native tree mining for wooden electric poles."""


def mine_wood(state, player, count=1):
    """Select the nearest observed tree and approach it before harvesting."""
    from logic import decision, distance, move_or_act
    trees=state.get('trees',[])
    if not trees:
        return decision('blocked','No tree is observed for pole construction.')
    tree=min(trees,key=lambda t:distance(t['position'],player['position']))
    return decision('mine_wood','Harvest wood for electric poles.',
        move_or_act(player,{'kind':'mine_tree','player':player['name'],'position':tree['position'],
                           'surface':player['surface'],'resource':tree['name'],'count':1},2.7))
