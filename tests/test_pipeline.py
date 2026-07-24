from __future__ import annotations

import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from beehive.pipeline import (
    experiment_seed_sets,
    prepare_run_dir,
    promotion_decision,
    validate_config,
)
from beehive.m7_pipeline import validate_m7_config
from beehive.m8_pipeline import validate_m8_config


def valid_config() -> dict:
    return {
        "experiment": "test-run",
        "data": {"episodes": 10, "seed": 1000},
        "bc": {"epochs": 1},
        "dagger": {"episodes": 2, "seed": 2000},
        "ppo": {"episodes": 2, "seed": 3000, "validation_episodes": 2},
        "test": {"episodes": 2, "seed": 5009},
        "promotion": {
            "minimum_honey_ratio": 1.0,
            "minimum_bee_survival": 0.9,
            "maximum_invalid_action_rate": 0.01,
        },
    }


class PipelineConfigTests(unittest.TestCase):
    def test_valid_config_has_disjoint_seed_sets(self):
        config = valid_config()
        validate_config(config)
        sets = list(experiment_seed_sets(config).values())
        for index, left in enumerate(sets):
            for right in sets[index + 1 :]:
                self.assertFalse(left & right)

    def test_seed_leakage_is_rejected(self):
        config = valid_config()
        config["test"]["seed"] = config["data"]["seed"] + 9
        with self.assertRaisesRegex(ValueError, "seed leakage"):
            validate_config(config)

    def test_unsafe_experiment_name_is_rejected(self):
        config = valid_config()
        config["experiment"] = "../../escape"
        with self.assertRaisesRegex(ValueError, "experiment may only"):
            validate_config(config)

    def test_force_refuses_unrecognized_directory(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "existing"
            path.mkdir()
            (path / "user-file.txt").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unrecognized"):
                prepare_run_dir(path, "existing", force=True)
            self.assertTrue((path / "user-file.txt").is_file())

    def test_promotion_requires_significant_safe_improvement(self):
        baseline = {"controller": "behavior-cloning", "mean_honey": 100.0}
        candidate = {
            "controller": "bc-ppo",
            "mean_honey": 110.0,
            "bee_survival_rate": 0.95,
            "mean_invalid_action_rate": 0.005,
        }
        comparison = {"mean_honey_delta": 10.0, "ci95_honey_delta": 4.0}
        accepted = promotion_decision(
            candidate, baseline, comparison, valid_config()["promotion"]
        )
        self.assertEqual(accepted["status"], "accepted")

        uncertain = copy.deepcopy(comparison)
        uncertain["ci95_honey_delta"] = 12.0
        rejected = promotion_decision(
            candidate, baseline, uncertain, valid_config()["promotion"]
        )
        self.assertEqual(rejected["status"], "rejected")

    def test_m7_config_rejects_seed_leakage(self):
        config = {
            "experiment": "m7-test",
            "data": {"episodes": 10, "seed": 1000},
            "local_bc": {"epochs": 1},
            "dagger": {"episodes": 1, "seed": 2000},
            "ctde": {"episodes": 2, "seed": 3000, "validation_episodes": 2},
            "test": {"episodes": 2, "seed": 5009},
            "promotion": {},
        }
        validate_m7_config(config)
        config["test"]["seed"] = 1009
        with self.assertRaisesRegex(ValueError, "seed leakage"):
            validate_m7_config(config)

        config["test"]["seed"] = 5009
        config["experiment"] = "../escape"
        with self.assertRaisesRegex(ValueError, "experiment may only"):
            validate_m7_config(config)

    def test_m8_config_requires_unresolved_contention_gate(self):
        config = {
            "experiment": "m8-test",
            "data": {"episodes": 10, "seed": 1000},
            "local_bc": {"epochs": 1},
            "dagger": {"episodes": 1, "seed": 2000},
            "ctde": {"episodes": 2, "seed": 3000, "validation_episodes": 2},
            "test": {"episodes": 2, "seed": 5009},
            "promotion": {"maximum_unresolved_contention_rate": 0.0},
        }
        validate_m8_config(config)
        del config["promotion"]["maximum_unresolved_contention_rate"]
        with self.assertRaisesRegex(ValueError, "maximum_unresolved"):
            validate_m8_config(config)


if __name__ == "__main__":
    unittest.main()
