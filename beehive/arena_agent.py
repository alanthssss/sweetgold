"""Auditable strategy recommendations built from Arena tournament evidence."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


OBJECTIVES = ("balanced", "yield", "safety")


def recommend_strategy(
    tournament: dict,
    objective: str = "balanced",
    min_bee_survival: float = 0.0,
    max_invalid_action_rate: float = 1.0,
) -> dict:
    """Select an eligible strategy and retain the evidence behind the decision."""
    if objective not in OBJECTIVES:
        raise ValueError(f"objective must be one of: {', '.join(OBJECTIVES)}")
    if not 0.0 <= min_bee_survival <= 1.0:
        raise ValueError("minimum bee survival must be between 0 and 1")
    if not 0.0 <= max_invalid_action_rate <= 1.0:
        raise ValueError("maximum invalid-action rate must be between 0 and 1")

    eligible = []
    rejected = []
    for row in tournament.get("leaderboard", []):
        reasons = []
        if row["bee_survival_rate"] < min_bee_survival:
            reasons.append(
                f"bee survival {row['bee_survival_rate']:.2%} is below "
                f"{min_bee_survival:.2%}"
            )
        if row["mean_invalid_action_rate"] > max_invalid_action_rate:
            reasons.append(
                f"invalid actions {row['mean_invalid_action_rate']:.2%} exceed "
                f"{max_invalid_action_rate:.2%}"
            )
        if reasons:
            rejected.append({"strategy": row["strategy"], "reasons": reasons})
        else:
            eligible.append(row)

    if not eligible:
        return {
            "status": "no_eligible_strategy",
            "objective": objective,
            "recommendation": None,
            "constraints": {
                "min_bee_survival": min_bee_survival,
                "max_invalid_action_rate": max_invalid_action_rate,
            },
            "eligible": [],
            "rejected": rejected,
            "rationale": "No strategy passed every declared safety constraint.",
        }

    if objective == "yield":
        key = lambda row: (
            row["mean_honey"],
            row["bee_survival_rate"],
            -row["mean_invalid_action_rate"],
        )
    elif objective == "safety":
        key = lambda row: (
            row["bee_survival_rate"],
            -row["mean_invalid_action_rate"],
            row["mean_honey"],
        )
    else:
        key = lambda row: (
            row["points"],
            row["mean_honey"],
            row["bee_survival_rate"],
            -row["mean_invalid_action_rate"],
        )
    winner = max(eligible, key=key)
    evidence = {
        key: winner[key]
        for key in (
            "rank",
            "points",
            "mean_honey",
            "ci95_honey",
            "bee_survival_rate",
            "colony_survival_rate",
            "mean_invalid_action_rate",
            "match_wins",
            "match_ties",
            "match_losses",
        )
    }
    rationale = {
        "balanced": "Highest Arena standing among strategies that passed the constraints.",
        "yield": "Highest mean honey among strategies that passed the constraints.",
        "safety": "Highest bee survival, then lowest invalid-action rate, among eligible strategies.",
    }[objective]
    return {
        "status": "recommended",
        "objective": objective,
        "recommendation": winner["strategy"],
        "constraints": {
            "min_bee_survival": min_bee_survival,
            "max_invalid_action_rate": max_invalid_action_rate,
        },
        "eligible": [row["strategy"] for row in eligible],
        "rejected": rejected,
        "rationale": rationale,
        "evidence": evidence,
    }


class AgentDecisionStore:
    """Persist a machine-readable decision and a human-readable companion."""

    def __init__(self, root: str | Path = "runs/agent") -> None:
        self.root = Path(root)

    def save(
        self,
        arena_artifact: dict,
        tournament: dict,
        decision: dict,
        created_at: datetime | None = None,
    ) -> dict:
        created = created_at or datetime.now(timezone.utc)
        payload = {
            "schema_version": 1,
            "kind": "arena-agent-decision",
            "created_at": created.astimezone(timezone.utc).isoformat(),
            "arena_artifact": arena_artifact,
            "tournament": tournament,
            "decision": decision,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:8]
        timestamp = created.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        decision_id = f"decision-{timestamp}-{digest}"
        payload["decision_id"] = decision_id
        self.root.mkdir(parents=True, exist_ok=True)
        json_path = self.root / f"{decision_id}.json"
        markdown_path = self.root / f"{decision_id}.md"
        self._atomic_write(
            json_path, json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
        self._atomic_write(markdown_path, self._markdown(payload))
        return {
            "decision_id": decision_id,
            "json": str(json_path),
            "markdown": str(markdown_path),
            "recommendation": decision["recommendation"],
            "status": decision["status"],
        }

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)

    @staticmethod
    def _markdown(payload: dict) -> str:
        decision = payload["decision"]
        lines = [
            "# SweetGold Arena Agent Decision",
            "",
            f"- Decision ID: `{payload['decision_id']}`",
            f"- Objective: `{decision['objective']}`",
            f"- Status: `{decision['status']}`",
            f"- Recommendation: `{decision['recommendation'] or 'none'}`",
            f"- Arena artifact: `{payload['arena_artifact']['run_id']}`",
            "",
            "## Rationale",
            "",
            decision["rationale"],
            "",
            "## Constraints",
            "",
            f"- Minimum bee survival: {decision['constraints']['min_bee_survival']:.2%}",
            f"- Maximum invalid-action rate: "
            f"{decision['constraints']['max_invalid_action_rate']:.2%}",
            "",
            "## Rejected strategies",
            "",
        ]
        if decision["rejected"]:
            for row in decision["rejected"]:
                lines.append(f"- `{row['strategy']}`: {'; '.join(row['reasons'])}")
        else:
            lines.append("- None")
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                "This recommendation is deterministic and is limited to the declared "
                "strategies, environment configuration and matched seeds. Treat a small "
                "league as workflow evidence, not as a replacement for a formal robustness "
                "audit.",
                "",
            ]
        )
        return "\n".join(lines)
