from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from beehive.controllers import AssignmentController, GreedyController, ScoutController
from beehive.env import BeeEnv, EnvConfig
from beehive.evaluator import evaluate, paired_honey_comparison
from beehive.ml import (
    FEATURE_SIZE,
    collect_dataset,
    encode_bee,
    seed_split,
    valid_action_mask,
)
from beehive.ppo import shaped_reward


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
        for key in ("mean_honey", "ci95_honey", "bee_survival_rate", "raw"):
            self.assertIn(key, result)

    def test_assignment_reserves_distinct_flower_targets(self):
        env = BeeEnv(EnvConfig(bees=3, flowers=4), seed=7)
        controller = AssignmentController()
        controller.reset(7)
        actions = controller.act(env.observe())
        flower_targets = [
            target for target in controller.targets.values() if target != env.hive
        ]
        self.assertEqual(len(actions), 3)
        self.assertEqual(len(flower_targets), len(set(flower_targets)))

    def test_assignment_scales_fleet_with_season_progress(self):
        env = BeeEnv(EnvConfig(bees=8, flowers=14), seed=9)
        controller = AssignmentController()
        controller.reset(9)
        early_actions = controller.act(env.observe())
        self.assertEqual(sum(action == "rest" for action in early_actions.values()), 2)

        observation = env.observe()
        observation["tick"] = observation["config"]["season_ticks"] // 2
        late_actions = controller.act(observation)
        self.assertEqual(sum(action == "rest" for action in late_actions.values()), 0)

    def test_evaluation_exposes_unambiguous_rates(self):
        result = evaluate(
            GreedyController(),
            EnvConfig(season_ticks=5, bees=2, flowers=2),
            [3],
        )
        self.assertIn("colony_survival_rate", result)
        self.assertIn("bee_survival_rate", result)
        self.assertIn("mean_invalid_action_rate", result)

    def test_paired_comparison_uses_shared_seeds(self):
        left = {
            "controller": "left",
            "raw": [{"seed": 1, "honey": 12}, {"seed": 2, "honey": 8}],
        }
        right = {
            "controller": "right",
            "raw": [{"seed": 1, "honey": 10}, {"seed": 2, "honey": 9}],
        }
        comparison = paired_honey_comparison(left, right)
        self.assertEqual(comparison["mean_honey_delta"], 0.5)
        self.assertEqual((comparison["wins"], comparison["losses"]), (1, 1))


class MlDatasetTests(unittest.TestCase):
    def test_seed_splits_are_episode_level_and_disjoint(self):
        self.assertEqual(seed_split(10), "train")
        self.assertEqual(seed_split(17), "validation")
        self.assertEqual(seed_split(19), "test")

    def test_bee_encoding_has_stable_size(self):
        observation = BeeEnv(seed=4).observe()
        self.assertEqual(len(encode_bee(observation, 0)), FEATURE_SIZE)

    def test_action_mask_rejects_impossible_deposit(self):
        observation = BeeEnv(seed=4).observe()
        mask = valid_action_mask(observation, 0)
        self.assertFalse(mask[5])
        self.assertTrue(mask[6])

    def test_collection_writes_all_splits_without_torch(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "examples.jsonl"
            counts = collect_dataset(
                path,
                episodes=10,
                seed=10,
                config=EnvConfig(season_ticks=2, bees=2, flowers=2),
            )
            self.assertTrue(path.is_file())
            self.assertTrue(all(counts[split] > 0 for split in counts))

    def test_ppo_reward_keeps_honey_dominant(self):
        self.assertGreater(shaped_reward(1, 0, 0, 1), 0.9)
        self.assertLess(shaped_reward(0, 1, 1, 1), 0)


if __name__ == "__main__":
    unittest.main()
