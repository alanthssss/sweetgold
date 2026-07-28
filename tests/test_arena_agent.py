import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from beehive.arena_agent import AgentDecisionStore, recommend_strategy


def tournament():
    return {
        "leaderboard": [
            {
                "strategy": "fast",
                "rank": 1,
                "points": 3,
                "mean_honey": 150.0,
                "ci95_honey": 2.0,
                "bee_survival_rate": 0.8,
                "colony_survival_rate": 1.0,
                "mean_invalid_action_rate": 0.02,
                "match_wins": 1,
                "match_ties": 0,
                "match_losses": 0,
            },
            {
                "strategy": "safe",
                "rank": 2,
                "points": 0,
                "mean_honey": 140.0,
                "ci95_honey": 1.0,
                "bee_survival_rate": 1.0,
                "colony_survival_rate": 1.0,
                "mean_invalid_action_rate": 0.0,
                "match_wins": 0,
                "match_ties": 0,
                "match_losses": 1,
            },
        ]
    }


class ArenaAgentTests(unittest.TestCase):
    def test_objectives_and_constraints_are_auditable(self):
        self.assertEqual(
            recommend_strategy(tournament(), objective="yield")["recommendation"],
            "fast",
        )
        self.assertEqual(
            recommend_strategy(tournament(), objective="safety")["recommendation"],
            "safe",
        )
        constrained = recommend_strategy(
            tournament(), min_bee_survival=0.95, max_invalid_action_rate=0.01
        )
        self.assertEqual(constrained["recommendation"], "safe")
        self.assertEqual(constrained["rejected"][0]["strategy"], "fast")
        self.assertEqual(constrained["evidence"]["bee_survival_rate"], 1.0)

    def test_no_eligible_strategy_is_an_explicit_result(self):
        impossible_tournament = tournament()
        impossible_tournament["leaderboard"][1]["bee_survival_rate"] = 0.99
        impossible = recommend_strategy(
            impossible_tournament,
            min_bee_survival=1.0,
            max_invalid_action_rate=0.0,
        )
        self.assertEqual(impossible["status"], "no_eligible_strategy")
        self.assertIsNone(impossible["recommendation"])

    def test_store_writes_json_and_markdown(self):
        with TemporaryDirectory() as directory:
            decision = recommend_strategy(tournament(), objective="safety")
            artifact = AgentDecisionStore(directory).save(
                {"run_id": "arena-test", "winner": "fast"},
                tournament(),
                decision,
                created_at=datetime(2026, 7, 28, tzinfo=timezone.utc),
            )
            document = json.loads(
                Path(artifact["json"]).read_text(encoding="utf-8")
            )
            markdown = Path(artifact["markdown"]).read_text(encoding="utf-8")
            self.assertEqual(document["kind"], "arena-agent-decision")
            self.assertEqual(document["decision"]["recommendation"], "safe")
            self.assertIn("workflow evidence", markdown)

    def test_invalid_policy_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "objective"):
            recommend_strategy(tournament(), objective="magic")
        with self.assertRaisesRegex(ValueError, "survival"):
            recommend_strategy(tournament(), min_bee_survival=1.1)


if __name__ == "__main__":
    unittest.main()
