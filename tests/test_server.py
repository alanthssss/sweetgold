from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from beehive.server import ArenaSession, StrategyCatalog


class StrategyCatalogTests(unittest.TestCase):
    def test_registry_only_enables_verified_artifacts(self):
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
            catalog = StrategyCatalog(registry)
            entry = next(
                row
                for row in catalog.entries()
                if row["id"] == "coordinated-ctde"
            )
            self.assertTrue(entry["available"])
            artifact.write_bytes(b"tampered")
            entry = next(
                row
                for row in catalog.entries()
                if row["id"] == "coordinated-ctde"
            )
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


if __name__ == "__main__":
    unittest.main()
