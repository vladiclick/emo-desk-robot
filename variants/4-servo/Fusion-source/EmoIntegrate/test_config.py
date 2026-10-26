"""Geometry-independent checks for the four-servo integration configuration."""
import math
import unittest

import config


class ConfigurationTests(unittest.TestCase):
    def test_default_dimensions_are_valid(self):
        self.assertEqual(config.validate(), ())
        self.assertEqual(config.HIP_X, (-62.5, -7.5))
        self.assertEqual(config.OLED_PCB, (29.2, 26.7, 6.2))

    def test_neutral_is_first_and_samples_are_unique(self):
        samples = config.motion_samples()
        self.assertIsInstance(samples, tuple)
        self.assertEqual(samples[0], (0.0, 0.0, 0.0, 0.0))
        self.assertEqual(len(samples), 49)
        self.assertEqual(len(set(samples)), len(samples))

    def test_samples_cover_each_extreme_and_stay_within_limits(self):
        samples = config.motion_samples(20, 10)
        for index, limit in enumerate((20, 20, 10, 10)):
            self.assertEqual(min(sample[index] for sample in samples), -limit)
            self.assertEqual(max(sample[index] for sample in samples), limit)
            for fraction in (-1, -.75, -.5, -.25, .25, .5, .75, 1):
                single = tuple(limit * fraction if axis == index else 0.0
                               for axis in range(4))
                self.assertIn(single, samples)
        corners = {sample for sample in samples if all(angle != 0 for angle in sample)}
        self.assertEqual(len(corners), 16)

    def test_invalid_motion_limits_raise(self):
        for invalid in (0, -1, 181, math.nan, math.inf, "25", None, True):
            for position in (0, 1):
                args = (invalid, 15) if position == 0 else (25, invalid)
                with self.subTest(args=args), self.assertRaises(ValueError):
                    config.motion_samples(*args)

    def test_invalid_dimensions_are_reported(self):
        for key in ("servo_length", "servo_width", "servo_case_depth", "clearance", "head_lift"):
            for value in (0, -1, math.nan, math.inf, "bad", True):
                with self.subTest(key=key, value=value):
                    self.assertTrue(config.validate(**{key: value}))
        for pcb in ((29, 26), (29, 26, 0), (29, math.inf, 6), None):
            with self.subTest(pcb=pcb):
                self.assertTrue(config.validate(oled_pcb=pcb))


if __name__ == "__main__":
    unittest.main()
