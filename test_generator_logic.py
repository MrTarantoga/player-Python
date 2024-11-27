import generator_logic
import unittest

class Testing(unittest.TestCase):
    def test_correct_storing_number_of_bases(self):
        config = generator_logic.generate_random_map(
            5,
            2,
            [-50, 50],
            [-10, 10],
            [-5, 5]
        )
        self.assertEqual(len([*config]), 5, msg="Not five player are generated")

    def test_correct_storing_number_of_bases(self):
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
            self.assertNotIn(n_level, levels, msg="A level higher than 2 is generated")

    def test_corret_y_position_stored(self):
        config = generator_logic.generate_random_map(
            5,
            2,
            [-50, 50],
            [-10, 10],
            [-5, 5]
        )
        for c in config:
            self.assertGreaterEqual(c.position[1], -10, msg=f"Y is not greater than -10 for player {c.uid}")
            self.assertLessEqual(c.position[1], 10, msg=f"Y is not lower than 10 for player {c.uid}")

    def test_corret_z_position_stored(self):
        config = generator_logic.generate_random_map(
            5,
            2,
            [-50, 50],
            [-10, 10],
            [-5, 5]
        )
        for c in config:
            self.assertGreaterEqual(c.position[2], -5, msg=f"Z is not greater than -5 for player {c.uid}")
            self.assertLessEqual(c.position[2], 5, msg=f"Z is not lower than 5 for player {c.uid}")

    def test_corret_x_position_stored(self):
        config = generator_logic.generate_random_map(
            5,
            2,
            [-50, 50],
            [-10, 10],
            [-5, 5]
        )
        for c in config:
            self.assertGreaterEqual(c.position[0], -50, msg=f"X is not greater than -50 for player {c.uid}")
            self.assertLessEqual(c.position[0], 50, msg=f"X is not lower than 50 for player {c.uid}")

    def test_assert_error_number_of_bases(self):
        with self.assertRaises(AssertionError) as cm:
            generator_logic.generate_random_map(
                1,
                2,
                [-50, 50],
                [-10, 10],
                [-5, 5]
            ).__next__()
        self.assertEqual(str(cm.exception), "At least two bases are mandatory")
  
    def test_assert_error_max_level(self):
        with self.assertRaises(AssertionError) as cm:
            generator_logic.generate_random_map(
                5,
                15,
                [-50, 50],
                [-10, 10],
                [-5, 5]
            ).__next__()
        self.assertEqual(str(cm.exception), "Max 14 levels are defined")

    def test_assert_error_min_level(self):
        with self.assertRaises(AssertionError) as cm:
            generator_logic.generate_random_map(
                5,
                -1,
                [-50, 50],
                [-10, 10],
                [-5, 5]
            ).__next__()
        self.assertEqual(str(cm.exception), "Min 0 level are defined")

    def test_assert_error_min_x_distance(self):
        with self.assertRaises(AssertionError) as cm:
            generator_logic.generate_random_map(
                5,
                2,
                [-50, -50],
                [-10, 10],
                [-5, 5]
            ).__next__()
        self.assertEqual(str(cm.exception), "x range must have a difference of at least 1")

    def test_assert_error_min_y_distance(self):
        with self.assertRaises(AssertionError) as cm:
            generator_logic.generate_random_map(
                5,
                2,
                [-50, 50],
                [-10, -10],
                [-5, 5]
            ).__next__()
        self.assertEqual(str(cm.exception), "y range must have a difference of at least 1")

    def test_assert_error_min_z_distance(self):
        with self.assertRaises(AssertionError) as cm:
            generator_logic.generate_random_map(
                5,
                2,
                [-50, 50],
                [-10, 10],
                [-5, -5]
            ).__next__()
        self.assertEqual(str(cm.exception), "z range must have a difference of at least 1")

if __name__ == '__main__':
    unittest.main(verbosity=2)