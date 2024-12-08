"""
Test suite for the game state module.
Tests base management, action creation, and game state tracking.
"""

import unittest
from generator_state import *

class TestEuclideanDistance(unittest.TestCase):
    """Tests for the Euclidean distance calculation"""

    def test_zero_distance(self):
        """Verify that distance to same point is zero"""
        pos = (1, 2, 3)
        self.assertEqual(compute_euclid_distance(pos, pos), 0)

    def test_positive_distance(self):
        """Verify that distance is calculated correctly"""
        src = (0, 0, 0)
        dest = (3, 4, 0)
        self.assertEqual(compute_euclid_distance(src, dest), 25)  # 3² + 4² + 0² = 25

    def test_negative_coordinates(self):
        """Verify that distance works with negative coordinates"""
        src = (-1, -1, -1)
        dest = (2, 2, 2)
        self.assertEqual(compute_euclid_distance(src, dest), 27)  # 3² + 3² + 3² = 27

class TestBase(unittest.TestCase):
    """Tests for the Base class"""

    def test_valid_base_creation(self):
        """Verify that valid base can be created"""
        base = Base(
            uid=1,
            name="test_base",
            player=1,
            population=10,
            units_until_upgrade=5,
            position=(0, 0, 0),
            level=1
        )
        self.assertEqual(base.uid, 1)
        self.assertEqual(base.name, "test_base")
        self.assertEqual(base.population, 10)

    def test_negative_population(self):
        """Verify that negative population raises error"""
        with self.assertRaises(NegativePopulationError):
            Base(1, "test", 1, -1, 5, (0, 0, 0), 1)

    def test_negative_upgrade_units(self):
        """Verify that negative upgrade units raises error"""
        with self.assertRaises(NegativeUnitsError):
            Base(1, "test", 1, 10, -5, (0, 0, 0), 1)

    def test_invalid_level(self):
        """Verify that invalid levels raise error"""
        with self.assertRaises(InvalidBaseLevelError):
            Base(1, "test", 1, 10, 5, (0, 0, 0), -1)
        with self.assertRaises(InvalidBaseLevelError):
            Base(1, "test", 1, 10, 5, (0, 0, 0), 15)

    def test_base_to_dict(self):
        """Verify that base is correctly converted to dictionary"""
        base = Base(1, "test", 1, 10, 5, (1, 2, 3), 1)
        dict_data = base.to_dict()
        self.assertEqual(dict_data["uid"], 1)
        self.assertEqual(dict_data["position"]["x"], 1)
        self.assertEqual(dict_data["position"]["y"], 2)
        self.assertEqual(dict_data["position"]["z"], 3)

class TestBaseLevel(unittest.TestCase):
    """Tests for the BaseLevel class"""

    def test_base_level_creation(self):
        """Verify that base level configuration can be created"""
        level = BaseLevel(max_population=100, upgrade_cost=50, spawn_rate=5)
        self.assertEqual(level.max_population, 100)
        self.assertEqual(level.upgrade_cost, 50)
        self.assertEqual(level.spawn_rate, 5)

    def test_base_level_to_dict(self):
        """Verify that base level is correctly converted to dictionary"""
        level = BaseLevel(max_population=100, upgrade_cost=50, spawn_rate=5)
        dict_data = level.to_dict()
        self.assertEqual(dict_data["max_population"], 100)
        self.assertEqual(dict_data["upgrade_cost"], 50)
        self.assertEqual(dict_data["spawn_rate"], 5)

class TestUserAction(unittest.TestCase):
    """Tests for the UserAction class"""

    def setUp(self):
        """Create test bases for actions"""
        self.src_base = Base(1, "source", 1, 20, 10, (0, 0, 0), 1)
        self.dest_base = Base(2, "dest", 2, 10, 10, (3, 4, 0), 1)

    def test_valid_action_creation(self):
        """Verify that valid user action can be created"""
        action = UserAction(self.src_base, self.dest_base, 10)
        self.assertEqual(action.amount, 10)
        self.assertEqual(action.src_base, self.src_base.uid)
        self.assertEqual(action.dest_base, self.dest_base.uid)

    def test_invalid_troop_amount(self):
        """Verify that invalid troop amounts raise error"""
        with self.assertRaises(InvalidTroopAmountError):
            UserAction(self.src_base, self.dest_base, 0)
        with self.assertRaises(InvalidTroopAmountError):
            UserAction(self.src_base, self.dest_base, -5)

    def test_insufficient_troops(self):
        """Verify that requesting too many troops raises error"""
        with self.assertRaises(InsufficientTroopsError):
            UserAction(self.src_base, self.dest_base, 25)

    def test_action_to_dict(self):
        """Verify that user action is correctly converted to dictionary"""
        action = UserAction(self.src_base, self.dest_base, 10)
        dict_data = action.to_dict()
        self.assertEqual(dict_data["src"], 1)
        self.assertEqual(dict_data["dest"], 2)
        self.assertEqual(dict_data["amount"], 10)

class TestGameState(unittest.TestCase):
    """Tests for the GameState class"""

    def test_game_state_creation(self):
        """Verify that game state can be created"""
        state = GameState(1, 10, 4, 3, 2)
        self.assertEqual(state.uid, 1)
        self.assertEqual(state.tick, 10)
        self.assertEqual(state.player_count, 4)
        self.assertEqual(state.remaining_players, 3)
        self.assertEqual(state.player, 2)

    def test_game_state_to_dict(self):
        """Verify that game state is correctly converted to dictionary"""
        state = GameState(1, 10, 4, 3, 2)
        dict_data = state.to_dict()
        self.assertEqual(dict_data["uid"], 1)
        self.assertEqual(dict_data["tick"], 10)
        self.assertEqual(dict_data["player_count"], 4)
        self.assertEqual(dict_data["remaining_players"], 3)
        self.assertEqual(dict_data["player"], 2)

class TestPaths(unittest.TestCase):
    """Tests for the Paths class"""

    def test_default_values(self):
        """Verify that default values are set correctly"""
        paths = Paths()
        self.assertEqual(paths.grace_period, 10)
        self.assertEqual(paths.death_rate, 1)

    def test_custom_values(self):
        """Verify that custom values can be set"""
        paths = Paths(grace_period=15, death_rate=2)
        self.assertEqual(paths.grace_period, 15)
        self.assertEqual(paths.death_rate, 2)

    def test_paths_to_dict(self):
        """Verify that paths configuration is correctly converted to dictionary"""
        paths = Paths(grace_period=15, death_rate=2)
        dict_data = paths.to_dict()
        self.assertEqual(dict_data["grace_period"], 15)
        self.assertEqual(dict_data["death_rate"], 2)

class TestAction(unittest.TestCase):
    """Tests for the Action class"""

    def setUp(self):
        """Create test bases for actions"""
        self.src_base = Base(1, "source", 1, 20, 10, (0, 0, 0), 1)
        self.dest_base = Base(2, "dest", 2, 10, 10, (3, 4, 0), 1)

    def test_action_creation(self):
        """Verify that action can be created and correctly stores base information"""
        action = Action(1, self.src_base, self.dest_base, 10)
        
        # Check basic attributes
        self.assertEqual(action.player, 1)
        self.assertEqual(action.amount, 10)
        self.assertEqual(action.travelled, 0)
        
        # Check base IDs are correctly stored
        self.assertEqual(action.src_base, self.src_base.uid)
        self.assertEqual(action.dest_base, self.dest_base.uid)
        
        # Check positions are correctly stored
        self.assertEqual(action.src_position, (0, 0, 0))
        self.assertEqual(action.dest_position, (3, 4, 0))

    def test_action_to_dict(self):
        """Verify that action is correctly converted to dictionary"""
        action = Action(1, self.src_base, self.dest_base, 10)
        dict_data = action.to_dict()
        
        # Check basic data
        self.assertEqual(dict_data["player"], 1)
        self.assertEqual(dict_data["src"], self.src_base.uid)
        self.assertEqual(dict_data["dest"], self.dest_base.uid)
        self.assertEqual(dict_data["amount"], 10)
        
        # Check progress data
        self.assertEqual(dict_data["progress"]["amount"], 0)
        expected_distance = compute_euclid_distance(
            self.src_base.position, 
            self.dest_base.position
        )
        self.assertEqual(dict_data["progress"]["distance"], expected_distance)

    def test_action_with_same_base(self):
        """Verify that action works with same source and destination base"""
        action = Action(1, self.src_base, self.src_base, 5)
        self.assertEqual(action.src_base, action.dest_base)
        self.assertEqual(action.src_position, action.dest_position)

    def test_action_uuid_generation(self):
        """Verify that each action gets a unique UUID"""
        action1 = Action(1, self.src_base, self.dest_base, 5)
        action2 = Action(1, self.src_base, self.dest_base, 5)
        self.assertNotEqual(action1.uuid, action2.uuid)

if __name__ == '__main__':
    unittest.main(verbosity=2) 