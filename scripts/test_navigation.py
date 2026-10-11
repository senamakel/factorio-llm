"""Local walking paths must detour and must not pass through blocked corners."""
import unittest
from brain.navigation import route


class NavigationTest(unittest.TestCase):
    def test_detours_around_a_factory_wall(self):
        cells={(x,y):True for x in range(-2,10) for y in range(-5,6)}
        for y in range(-2,3):cells[(3,y)]=False
        path=route(cells,(8,0),1)
        self.assertTrue(any(abs(y)>=3 for x,y in path))
        self.assertTrue(all(cells[p] for p in path))

    def test_cannot_cut_an_obstructed_diagonal_corner(self):
        with self.assertRaises(ValueError):route({(0,0):True,(1,1):True},(1,1),.1)
