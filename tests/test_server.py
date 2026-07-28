from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from beehive.server import ArenaSession, StrategyCatalog, run_tournament


class StrategyCatalogTests(unittest.TestCase):
    def test_registry_only_enables_verified_artifacts(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "model.pt"
            artifact.write_bytes(b"checkpoint")
            registry = root / "models.json"
            audits = root / "audits.json"
            registry.write_text(
                json.dumps(
                    {
                        "models": [
                            {
                                "model": "coordinated-ctde",
                                "artifact": str(artifact),
                                "sha256": hashlib.sha256(
                                    artifact.read_bytes()
                                ).hexdigest(),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            audits.write_text(
                json.dumps(
                    {
                        "audits": [
                            {
                                "candidate": "coordinated-ctde",
                                "status": "failed",
                                "run": "runs/audit",
                                "summary": {
                                    "worst_honey_scenario": "scarce-nectar",
                                    "worst_honey_ratio": 0.74,
                                    "minimum_bee_survival": 0.28,
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            catalog = StrategyCatalog(registry)
            with patch("beehive.server.find_spec", return_value=object()):
                entry = next(
                    row
                    for row in catalog.entries()
                    if row["id"] == "coordinated-ctde"
                )
            self.assertTrue(entry["available"])
            self.assertEqual(entry["integrity"], "verified")
            self.assertIn("CTDE", entry["description_zh"])
            self.assertEqual(
                entry["latest_audit"]["worst_honey_scenario"], "scarce-nectar"
            )
            artifact.write_bytes(b"tampered")
            with patch("beehive.server.find_spec", return_value=object()):
                entry = next(
                    row
                    for row in catalog.entries()
                    if row["id"] == "coordinated-ctde"
                )
            self.assertFalse(entry["available"])
            self.assertEqual(entry["integrity"], "corrupt")

    def test_registry_requires_ml_runtime_for_learned_strategy(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "model.pt"
            artifact.write_bytes(b"checkpoint")
            registry = root / "models.json"
            registry.write_text(
                json.dumps(
                    {
                        "models": [
                            {
                                "model": "bc-ppo",
                                "artifact": str(artifact),
                                "sha256": hashlib.sha256(b"checkpoint").hexdigest(),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with patch("beehive.server.find_spec", return_value=None):
                entry = next(
                    row
                    for row in StrategyCatalog(registry).entries()
                    if row["id"] == "bc-ppo"
                )
            self.assertEqual(entry["integrity"], "verified")
            self.assertEqual(entry["runtime"], "missing-pytorch")
            self.assertFalse(entry["available"])


class ArenaSessionTests(unittest.TestCase):
    def test_lanes_start_from_identical_worlds_and_replay_steps(self):
        arena = ArenaSession()
        initial = arena.reset(seed=73, left="assignment", right="greedy")
        self.assertEqual(initial["left"]["flowers"], initial["right"]["flowers"])
        self.assertEqual(initial["left"]["weather"], initial["right"]["weather"])
        current = arena.step()
        self.assertEqual(current["frame"], 1)
        self.assertEqual(current["frames"], 2)
        replay = arena.frame(0)
        self.assertFalse(replay["live"])
        self.assertEqual(replay["left"]["tick"], 0)
        self.assertEqual(current["left"]["tick"], 1)

    def test_reset_rejects_unknown_strategy(self):
        arena = ArenaSession()
        with self.assertRaisesRegex(ValueError, "unknown strategy"):
            arena.reset(left="not-a-strategy")

    def test_tournament_ranks_shared_seed_results(self):
        result = run_tournament(
            StrategyCatalog(),
            ["assignment", "greedy", "random"],
            seed=91,
            episodes=3,
            config={"season_ticks": 20},
        )
        self.assertEqual(result["seeds"], [91, 92, 93])
        self.assertEqual(len(result["leaderboard"]), 3)
        self.assertEqual(len(result["matches"]), 3)
        self.assertEqual(
            [row["rank"] for row in result["leaderboard"]], [1, 2, 3]
        )
        self.assertTrue(
            all(
                row["match_wins"] + row["match_ties"] + row["match_losses"] == 2
                for row in result["leaderboard"]
            )
        )

    def test_tournament_rejects_invalid_entries(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            run_tournament(StrategyCatalog(), ["assignment"])
        with self.assertRaisesRegex(ValueError, "unavailable"):
            run_tournament(StrategyCatalog(), ["assignment", "unknown"])


if __name__ == "__main__":
    unittest.main()
