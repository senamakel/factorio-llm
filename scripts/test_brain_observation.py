"""Resource searches must retain patches between an empty and an overfull radius."""
import unittest
from unittest.mock import patch
from brain_observation import resource_targets


class ResourceSearchTest(unittest.TestCase):
    def test_dense_distant_patch_is_found_without_shrinking_past_it(self):
        def query(actor, filters, fields, limit=512):
            radius=filters['radius']
            return {'truncated':radius>90,'entities':[] if radius<80 else
                    [{'name':filters['name'],'position':{'x':80,'y':0},'amount':100}]}
        with patch('brain_observation.read_entities',side_effect=query):
            targets, radii=resource_targets(72,{'x':0,'y':0})
        self.assertEqual({r['name'] for r in targets},{'iron-ore','copper-ore','coal','stone'})
        self.assertTrue(all(80<=radius<=90 for radius in radii.values()))
