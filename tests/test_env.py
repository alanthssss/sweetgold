from __future__ import annotations

import unittest

from beehive.controllers import GreedyController, ScoutController
from beehive.env import BeeEnv, EnvConfig
from beehive.evaluator import evaluate


class EnvTests(unittest.TestCase):
    def test_seeded_reset_is_deterministic(self):
        first = BeeEnv(seed=42).observe()
        second = BeeEnv(seed=42).observe()
        self.assertEqual(first["flowers"], second["flowers"])
        self.assertEqual(first["bees"], second["bees"])

    def test_harvest_and_deposit(self):
        env = BeeEnv(EnvConfig(bees=1, flowers=1), seed=1)
        bee = env.bees[0]
        flower = env.flowers[0]
        bee.row, bee.col = flower.row, flower.col
        env.step({0: "harvest"})
        self.assertEqual(bee.cargo, 1)
        bee.row, bee.col = env.hive
        env.step({0: "deposit"})
        self.assertEqual(env.stored_honey, 1)

    def test_episode_terminates_at_season_end(self):
        env = BeeEnv(EnvConfig(season_ticks=3), seed=0)
        for _ in range(3):
            env.step({bee.id: "rest" for bee in env.bees})
        self.assertTrue(env.done)

    def test_out_of_bounds_action_is_counted(self):
        env = BeeEnv(EnvConfig(bees=1), seed=0)
        bee = env.bees[0]
        bee.row = 0
        env.step({0: "up"})
        self.assertEqual(env.invalid_actions, 1)


class EvaluationTests(unittest.TestCase):
    def test_matched_seed_evaluation_is_reproducible(self):
        config = EnvConfig(season_ticks=30, bees=3, flowers=4)
        a = evaluate(GreedyController(), config, [10, 11])
        b = evaluate(GreedyController(), config, [10, 11])
        self.assertEqual(a["mean_honey"], b["mean_honey"])

    def test_scout_returns_complete_summary(self):
        result = evaluate(
            ScoutController(),
            EnvConfig(season_ticks=20, bees=3, flowers=4),
            [1, 2],
        )
        for key in ("mean_honey", "ci95_honey", "survival_rate", "raw"):
            self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main()
