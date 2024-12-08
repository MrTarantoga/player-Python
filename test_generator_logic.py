"""
Test suite for the game logic module.
Tests map generation, player assignments, action definitions and troop movements.
"""

import generator_logic
import generator_state
import unittest
from utils_test import find_player_base, find_player_bases, find_base_by_uid

class TestMapGeneration(unittest.TestCase):
    """Tests for the random map generation functionality"""

    def test_correct_number_of_bases(self):
        """Verify that the correct number of bases are generated"""
        config = generator_logic.generate_random_map(
            5,
            2,
            [-50, 50],
            [-10, 10],
            [-5, 5]
        )
        self.assertEqual(len([*config]), 5, "Not five bases are generated")

    def test_correct_base_levels(self):
        """Verify that bases are not generated with levels higher than specified"""
        config = generator_logic.generate_random_map(
            5,
            2,
            [-50, 50],
            [-10, 10],
            [-5, 5]
        )
        levels = []
        for c in config:
            levels.append(c.level)
        for n_level in range(3, 15):
            self.assertNotIn(n_level, levels, f"A level higher than 2 is generated: {n_level}")

    def test_base_positions(self):
        """Verify that bases are placed within the specified coordinate ranges"""
        config = [*generator_logic.generate_random_map(
            5,
            2,
            [-50, 50],
            [-10, 10],
            [-5, 5]
        )]
        for c in config:
            self.assertGreaterEqual(c.position[0], -50, f"X is not greater than -50 for base {c.uid}")
            self.assertLessEqual(c.position[0], 50, f"X is not lower than 50 for base {c.uid}")
            self.assertGreaterEqual(c.position[1], -10, f"Y is not greater than -10 for base {c.uid}")
            self.assertLessEqual(c.position[1], 10, f"Y is not lower than 10 for base {c.uid}")
            self.assertGreaterEqual(c.position[2], -5, f"Z is not greater than -5 for base {c.uid}")
            self.assertLessEqual(c.position[2], 5, f"Z is not lower than 5 for base {c.uid}")

class TestMapGenerationExceptions(unittest.TestCase):
    """Tests for error handling in map generation"""

    def test_insufficient_bases(self):
        """Verify that an error is raised when trying to create too few bases"""
        with self.assertRaises(generator_logic.InsufficientBasesError):
            next(generator_logic.generate_random_map(1, 2, [-50, 50], [-10, 10], [-5, 5]))

    def test_invalid_max_level(self):
        """Verify that an error is raised when max level is too high"""
        with self.assertRaises(generator_logic.InvalidBaseLevelError):
            next(generator_logic.generate_random_map(5, 15, [-50, 50], [-10, 10], [-5, 5]))

    def test_invalid_min_level(self):
        """Verify that an error is raised when min level is negative"""
        with self.assertRaises(generator_logic.InvalidBaseLevelError):
            next(generator_logic.generate_random_map(5, -1, [-50, 50], [-10, 10], [-5, 5]))

    def test_invalid_coordinate_ranges(self):
        """Verify that errors are raised for invalid coordinate ranges"""
        with self.assertRaises(generator_logic.InvalidCoordinateRangeError):
            next(generator_logic.generate_random_map(5, 2, [-50, -50], [-10, 10], [-5, 5]))
        with self.assertRaises(generator_logic.InvalidCoordinateRangeError):
            next(generator_logic.generate_random_map(5, 2, [-50, 50], [-10, -10], [-5, 5]))
        with self.assertRaises(generator_logic.InvalidCoordinateRangeError):
            next(generator_logic.generate_random_map(5, 2, [-50, 50], [-10, 10], [-5, -5]))

class TestPlayerAssignment(unittest.TestCase):
    """Tests for player assignment to bases"""

    def setUp(self):
        """Create a test map with bases"""
        self.bases = [*generator_logic.generate_random_map(5, 2, [-50, 50], [-10, 10], [-5, 5])]

    def test_player_assignment(self):
        """Verify that all players are correctly assigned to bases"""
        players = [1, 2, 3]
        updated_bases = generator_logic.assert_player_to_bases(self.bases, players)
        assigned_players = set()
        for base in updated_bases:
            if base.player != 0:
                assigned_players.add(base.player)
        self.assertEqual(assigned_players, set(players))

    def test_invalid_player_count(self):
        """Verify that errors are raised for invalid player counts"""
        with self.assertRaises(generator_logic.PlayerCountError):
            generator_logic.assert_player_to_bases(self.bases, [1])  # Too few players
        with self.assertRaises(generator_logic.PlayerCountError):
            generator_logic.assert_player_to_bases(self.bases, [1, 2, 3, 4, 5, 6])  # Too many players

class TestActionDefinition(unittest.TestCase):
    """Tests for action type determination"""

    def setUp(self):
        """Create a test map with two players"""
        self.bases = [*generator_logic.generate_random_map(3, 2, [-50, 50], [-10, 10], [-5, 5])]
        self.bases = generator_logic.assert_player_to_bases(self.bases, [1, 2])
        self.game_state = generator_state.GameState(1, 0, 2, 2, 1)

    def test_upgrade_action(self):
        """Verify that actions targeting own base are recognized as upgrades"""
        player_base = find_player_base(self.bases, 1)
        
        # Update population in the actual base list
        for base in self.bases:
            if base.uid == player_base.uid:
                base.population = 20  # Ensure enough troops for the test
                break
            
        action = generator_state.UserAction(player_base, player_base, 5)
        action_type = generator_logic.define_action(self.bases, action, self.game_state)
        self.assertEqual(action_type, generator_logic.TroopAction.UPGRADE)

    def test_transfer_action(self):
        """Verify that actions between own bases are recognized as transfers"""
        player_bases = find_player_bases(self.bases, 1)
        if len(player_bases) >= 2:
            action = generator_state.UserAction(player_bases[0], player_bases[1], 5)
            action_type = generator_logic.define_action(self.bases, action, self.game_state)
            self.assertEqual(action_type, generator_logic.TroopAction.TRANSFER)

    def test_attack_action(self):
        """Verify that actions targeting enemy bases are recognized as attacks"""
        src_base = find_player_base(self.bases, 1)
        dest_base = find_player_base(self.bases, 2)
        action = generator_state.UserAction(src_base, dest_base, 5)
        action_type = generator_logic.define_action(self.bases, action, self.game_state)
        self.assertEqual(action_type, generator_logic.TroopAction.ATTACK)

    def test_invalid_source_base(self):
        """Verify that actions from enemy bases are rejected"""
        src_base = find_player_base(self.bases, 2)
        dest_base = find_player_base(self.bases, 1)
        
        # Update population in the actual base list
        for base in self.bases:
            if base.uid == src_base.uid:
                base.population = 20  # Ensure enough troops for the test
                break
            
        action = generator_state.UserAction(src_base, dest_base, 5)
        with self.assertRaises(generator_logic.UserIsNotAllowedToPerformOnBase):
            generator_logic.define_action(self.bases, action, self.game_state)

    def test_no_bases_for_player(self):
        """Verify that error is raised when player has no bases"""
        # Remove all bases for player 1
        for base in self.bases:
            if base.player == 1:
                base.player = 2
                
        src_base = self.bases[0]
        # Ensure enough troops for the test
        src_base.population = 20  # Set higher population before creating action
            
        action = generator_state.UserAction(src_base, src_base, 5)
        
        with self.assertRaises(generator_logic.NoBasesForPlayerError):
            generator_logic.define_action(self.bases, action, self.game_state)

class TestActionComputation(unittest.TestCase):
    """Tests for troop movement and combat mechanics"""

    def setUp(self):
        """Create a test map with two players"""
        self.bases = [*generator_logic.generate_random_map(3, 2, [-50, 50], [-10, 10], [-5, 5])]
        self.bases = generator_logic.assert_player_to_bases(self.bases, [1, 2])
        # Ensure bases have enough population for tests
        for base in self.bases:
            base.population = 20  # Set higher default population
        self.game_state = generator_state.GameState(1, 0, 2, 2, 1)

    def test_troop_movement(self):
        """Verify that troops move correctly each tick"""
        src_base = find_player_base(self.bases, 1)
        dest_base = find_player_base(self.bases, 2)
        src_base.population = 20  # Ensure enough troops
        action = generator_state.Action(1, src_base, dest_base, 5)
        
        result = generator_logic.compute_action(self.bases, action)
        self.assertIsInstance(result, generator_state.Action)
        self.assertEqual(result.travelled, 1)

    def test_troop_arrival(self):
        """Verify that troops are correctly added to destination base upon arrival"""
        src_base = find_player_base(self.bases, 1)
        dest_base = find_player_base(self.bases, 2)
        src_base.population = 20  # Ensure enough troops
        dest_base.population = 10  # Set initial destination population
        initial_dest_population = dest_base.population
        action = generator_state.Action(1, src_base, dest_base, 5)
        action.travelled = generator_state.compute_euclid_distance(src_base.position, dest_base.position) - 1
        
        result = generator_logic.compute_action(self.bases, action)
        self.assertIsInstance(result, generator_state.Base)
        self.assertEqual(result.uid, dest_base.uid)
        self.assertEqual(result.population, initial_dest_population + 5)  # Check population increase

    def test_troop_death(self):
        """Verify that troops die correctly after grace period"""
        src_base = find_player_base(self.bases, 1)
        dest_base = find_player_base(self.bases, 2)
        src_base.population = 20  # Ensure enough troops
        action = generator_state.Action(1, src_base, dest_base, 1)
        action.travelled = 10  # Set to grace period
        
        result = generator_logic.compute_action(self.bases, action)
        self.assertIsNone(result)  # Check if result is None

    def test_base_not_found(self):
        """Verify that appropriate errors are raised when bases cannot be found"""
        src_base = find_player_base(self.bases, 1)
        # Create dummy base for invalid ID
        invalid_base = generator_state.Base(9999, "invalid", 0, 0, 0, (0,0,0), 1)
        
        action = generator_state.Action(1, src_base, invalid_base, 5)  # Use Base object
        with self.assertRaises(generator_logic.BaseNotFoundError):
            generator_logic.compute_action(self.bases, action)
        
        action = generator_state.Action(1, invalid_base, src_base, 5)  # Use Base object
        with self.assertRaises(generator_logic.BaseNotFoundError):
            generator_logic.compute_action(self.bases, action)

    def test_all_troops_die(self):
        """Verify that action returns None when all troops die"""
        src_base = find_player_base(self.bases, 1)
        dest_base = find_player_base(self.bases, 2)
        src_base.population = 20  # Ensure enough troops
        action = generator_state.Action(1, src_base, dest_base, 1)
        action.travelled = 11  # Past grace period
        
        result = generator_logic.compute_action(self.bases, action)
        self.assertIsNone(result)

class TestUserActionComputation(unittest.TestCase):
    """Tests for user action processing"""

    def setUp(self):
        """Create a test map with two players"""
        self.bases = [*generator_logic.generate_random_map(3, 2, [-50, 50], [-10, 10], [-5, 5])]
        self.bases = generator_logic.assert_player_to_bases(self.bases, [1, 2])
        
        # Update populations in the actual base list
        for base in self.bases:
            base.population = 20  # Set higher default population
            base.units_until_upgrade = 10  # Set reasonable upgrade cost
        self.game_state = generator_state.GameState(1, 0, 2, 2, 1)

    def test_upgrade_computation(self):
        """Verify that upgrade actions are processed correctly"""
        player_base = find_player_base(self.bases, 1)
        # Update population in the actual base list
        for base in self.bases:
            if base.uid == player_base.uid:
                base.population = 15  # Set population for upgrade
                base.units_until_upgrade = 10
                initial_level = base.level
                break
            
        action = generator_state.UserAction(player_base, player_base, 10)
        result = generator_logic.compute_user_action(self.bases, action, self.game_state)
        self.assertIsInstance(result, list)
        
        # Find the upgraded base in the result list using helper function
        updated_base = find_base_by_uid(result, player_base.uid)
        self.assertEqual(updated_base.level, initial_level + 1)  # Compare with initial level

    def test_failed_upgrade_max_level(self):
        """Verify that upgrades fail when base is at max level"""
        player_base = find_player_base(self.bases, 1)
        player_base.level = 14
        player_base.population = 15
        action = generator_state.UserAction(player_base, player_base, 10)
        
        with self.assertRaises(generator_logic.NoFurtherUpgradesPossible):
            generator_logic.compute_user_action(self.bases, action, self.game_state)

    def test_insufficient_troops_for_action(self):
        """Verify that actions fail when there are not enough troops"""
        player_base = find_player_base(self.bases, 1)
        player_base.population = 5  # Set population lower than required troops
        action = generator_state.UserAction(player_base, player_base, 1) 
        action.amount = 10 # Change 1 to 10 to bypass validation
        with self.assertRaises(generator_logic.NotEnoughTroopsInBase):
            generator_logic.compute_user_action(self.bases, action, self.game_state)

    def test_transfer_computation(self):
        """Verify that transfer actions are processed correctly"""
        bases = [b for b in self.bases if b.player == 1]
        if len(bases) >= 2:
            src_base = bases[0]
            src_base.population = 15
            action = generator_state.UserAction(src_base, bases[1], 10)
            
            result = generator_logic.compute_user_action(self.bases, action, self.game_state)
            self.assertIsInstance(result, generator_state.Action)
            self.assertEqual(result.amount, 10)
            self.assertEqual(src_base.population, 5)

    def test_attack_computation(self):
        """Verify that attack actions are processed correctly"""
        src_base = find_player_base(self.bases, 1)
        dest_base = find_player_base(self.bases, 2)
        src_base.population = 15
        action = generator_state.UserAction(src_base, dest_base, 10)
        
        result = generator_logic.compute_user_action(self.bases, action, self.game_state)
        self.assertIsInstance(result, generator_state.Action)
        self.assertEqual(result.amount, 10)
        self.assertEqual(src_base.population, 5)

    def test_failed_upgrade_insufficient_troops(self):
        """Verify that upgrades fail when not enough troops are provided"""
        player_base = find_player_base(self.bases, 1)
        
        # Update values in the actual base list
        for base in self.bases:
            if base.uid == player_base.uid:
                base.population = 15
                base.units_until_upgrade = 20
                initial_level = base.level  # Store level from actual base in list
                break
            
        action = generator_state.UserAction(player_base, player_base, 4)
        result = generator_logic.compute_user_action(self.bases, action, self.game_state)
        self.assertIsInstance(result, list)
        
        # Find the base in the result list and compare with initial level
        updated_base = find_base_by_uid(result, player_base.uid)
        self.assertEqual(updated_base.level, initial_level)  # Level should not change

    def test_euclidean_distance(self):
        """Verify that Euclidean distance is calculated correctly"""
        src_pos = (0, 0, 0)
        dest_pos = (3, 4, 0)  # Should form a 3-4-5 triangle in 2D
        
        distance = generator_state.compute_euclid_distance(src_pos, dest_pos)
        self.assertEqual(distance, 25)  # 3² + 4² + 0² = 25

if __name__ == '__main__':
    unittest.main(verbosity=2)