import unittest

from dfsmc.simulate import games


class TestGameSimulator(unittest.TestCase):
    
    gamesim: games.GameSimulator
    
    @classmethod
    def setUpClass(cls):
        cls.gamesim = games.GameSimulator()
        
    def test_init(self):
        self.assertEqual(self.gamesim.x, 1)
        
if __name__ == "__main__":
    unittest.main()