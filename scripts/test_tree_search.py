"""Bounded tree queries must choose nearby harvestable trees, not a truncated far chunk."""
import unittest
from unittest.mock import patch


class TreeSearchTest(unittest.TestCase):
    def test_dense_forest_is_requeried_to_find_a_nearby_tree(self):
        from brain.observation import tree_targets
        def query(actor,filters,fields,limit=512):
            near={'name':'tree-01','position':{'x':8,'y':0},'mineable':True,'wood_yield':4}
            far={'name':'tree-01','position':{'x':100,'y':0},'mineable':True,'wood_yield':4}
            return {'truncated':filters['radius']>16,'entities':[far] if filters['radius']>16 else [near]}
        with patch('brain.observation.read_entities',side_effect=query):
            trees=tree_targets(14,{'x':0,'y':0})
        self.assertEqual(trees[0]['position'],{'x':8,'y':0})
