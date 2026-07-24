"""M11 curriculum training across distance, weather and resource shifts."""

from __future__ import annotations

import json
import platform
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .controllers import CONTROLLERS
from .coordination import CoordinatedCTDEController
from .ctde import train_ctde
from .env import EnvConfig
from .evaluator import evaluate, paired_honey_comparison
from .m10_pipeline import (
    _audit,
    _test_seeds,
    _update_audit_registry,
    _write_report,
)
from .ml import seed_split
from .pipeline import (
    _git_commit,
    _git_dirty,
    _summarize,
    _update_registry,
    prepare_run_dir,
)
from .server import StrategyCatalog


def _train_seeds(start: int, count: int) -> set[int]:
    seeds = set()
    candidate = start
    while len(seeds) < count:
        if seed_split(candidate) == "train":
            seeds.add(candidate)
        candidate += 1
    return seeds


def _scenario_seeds(start: int, episodes: int, scenarios: list[dict]) -> dict:
    return {
        scenario["name"]: _test_seeds(start + index * 100_000, episodes)
        for index, scenario in enumerate(scenarios)
    }


def validate_m11_config(config: dict) -> dict[str, object]:
    required = (
        "experiment",
        "source_model",
        "stages",
        "validation",
        "test",
        "audit",
    )
    missing = [field for field in required if field not in config]
    if missing:
        raise ValueError(f"missing M11 config fields: {', '.join(missing)}")
    if not isinstance(config["experiment"], str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]*", config["experiment"]
    ):
        raise ValueError("experiment may only contain letters, numbers, dot, dash and underscore")
    if not isinstance(config["stages"], list) or not config["stages"]:
        raise ValueError("stages must be a non-empty list")
    stage_names = set()
    occupied: dict[str, set[int]] = {}
    for stage in config["stages"]:
        name = stage.get("name")
        if not isinstance(name, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]*", name
        ):
            raise ValueError("stage names must be safe identifiers")
        if name in stage_names:
            raise ValueError(f"duplicate stage name: {name}")
        stage_names.add(name)
        for field in ("episodes", "seed"):
            if not isinstance(stage.get(field), int) or stage[field] < 1:
                raise ValueError(f"stage {name}.{field} must be positive")
        EnvConfig(**stage.get("env", {})).validate()
        occupied[f"train:{name}"] = _train_seeds(
            stage["seed"], stage["episodes"]
        )
        occupied[f"stage-validation:{name}"] = set(
            candidate
            for candidate in range(stage["seed"] + 10_000, stage["seed"] + 20_000)
            if candidate % 10 == 8
        )
        occupied[f"stage-validation:{name}"] = set(
            sorted(occupied[f"stage-validation:{name}"])[
                : stage.get("validation_episodes", 5)
            ]
        )
    for section in ("validation", "test"):
        value = config[section]
        if not isinstance(value.get("episodes"), int) or value["episodes"] < 1:
            raise ValueError(f"{section}.episodes must be positive")
        if not isinstance(value.get("seed"), int) or value["seed"] < 1:
            raise ValueError(f"{section}.seed must be positive")
        scenarios = value.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError(f"{section}.scenarios must be non-empty")
        names = set()
        for scenario in scenarios:
            name = scenario.get("name")
            if name in names:
                raise ValueError(f"duplicate {section} scenario: {name}")
            names.add(name)
            EnvConfig(**scenario.get("env", {})).validate()
        for name, seeds in _scenario_seeds(
            value["seed"], value["episodes"], scenarios
        ).items():
            occupied[f"{section}:{name}"] = set(seeds)
    keys = list(occupied)
    for index, left in enumerate(keys):
        for right in keys[index + 1 :]:
            if occupied[left] & occupied[right]:
                raise ValueError(f"seed leakage detected between {left} and {right}")
    for threshold in (
        "minimum_median_honey_ratio",
        "minimum_worst_honey_ratio",
        "minimum_bee_survival",
        "maximum_invalid_action_rate",
    ):
        value = config["audit"].get(threshold)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"audit.{threshold} must be between zero and one")
    return {
        "occupied": {name: sorted(seeds) for name, seeds in occupied.items()},
        "validation": _scenario_seeds(
            config["validation"]["seed"],
            config["validation"]["episodes"],
            config["validation"]["scenarios"],
        ),
        "test": _scenario_seeds(
            config["test"]["seed"],
            config["test"]["episodes"],
            config["test"]["scenarios"],
        ),
    }


def _evaluate_scenarios(
    checkpoint: Path, scenarios: list[dict], seed_sets: dict[str, list[int]]
) -> list[dict]:
    rows = []
    for scenario in scenarios:
        name = scenario["name"]
        env_config = EnvConfig(**scenario.get("env", {}))
        candidate = evaluate(
            CoordinatedCTDEController(checkpoint), env_config, seed_sets[name]
        )
        baseline = evaluate(
            CONTROLLERS["assignment"](), env_config, seed_sets[name]
        )
        comparison = paired_honey_comparison(candidate, baseline)
        rows.append(
            {
                "name": name,
                "env": scenario.get("env", {}),
                "candidate": _summarize(candidate),
                "baseline": _summarize(baseline),
                "honey_ratio": candidate["mean_honey"]
                / max(1e-9, baseline["mean_honey"]),
                "comparison": comparison,
            }
        )
    return rows


def _selection_key(audit: dict) -> tuple:
    """Rank only on validation: safety gates, then survival and yield."""
    return (
        sum(audit["checks"].values()),
        audit["minimum_bee_survival"],
        audit["median_honey_ratio"],
        audit["worst_honey_ratio"],
    )


def run_m11_pipeline(
    config_path: str | Path,
    output_root: str | Path = "runs",
    force: bool = False,
) -> dict:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    seeds = validate_m11_config(config)
    run_dir = Path(output_root) / config["experiment"]
    prepare_run_dir(run_dir, config["experiment"], force)
    checkpoints = run_dir / "checkpoints"
    checkpoints.mkdir()
    shutil.copyfile(config_path, run_dir / "config.json")
    metadata = {
        "experiment": config["experiment"],
        "milestone": "M11",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "python": sys.version,
        "platform": platform.platform(),
        "seed_sets": seeds["occupied"],
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    catalog = StrategyCatalog(config.get("registry_path", "registry/models.json"))
    source_checkpoint = checkpoints / "source.pt"
    if config.get("source_checkpoint"):
        shutil.copyfile(config["source_checkpoint"], source_checkpoint)
    else:
        catalog.create(config["source_model"])
        source_record = next(
            row
            for row in reversed(catalog._registry().get("models", []))
            if row.get("model") == config["source_model"]
        )
        shutil.copyfile(catalog._artifact(source_record), source_checkpoint)
    selected_checkpoint = checkpoints / "curriculum-ctde.pt"
    shutil.copyfile(source_checkpoint, selected_checkpoint)
    validation_scenarios = config["validation"]["scenarios"]
    validation_rows = _evaluate_scenarios(
        selected_checkpoint, validation_scenarios, seeds["validation"]
    )
    best_audit = _audit(validation_rows, config["audit"])
    best_key = _selection_key(best_audit)
    selection = [
        {
            "stage": "source",
            "selected": True,
            "audit": best_audit,
        }
    ]
    previous = source_checkpoint
    stage_summaries = []
    for index, stage in enumerate(config["stages"]):
        stage_checkpoint = checkpoints / f"{index + 1:02d}-{stage['name']}.pt"
        summary = train_ctde(
            previous,
            stage_checkpoint,
            episodes=stage["episodes"],
            seed=stage["seed"],
            validation_episodes=stage.get("validation_episodes", 5),
            rollout_workers=stage.get("rollout_workers", 4),
            learning_rate=stage.get("learning_rate", 5e-5),
            update_epochs=stage.get("update_epochs", 4),
            batch_size=stage.get("batch_size", 512),
            validation_interval=stage.get("validation_interval", 20),
            invalid_penalty=stage.get("invalid_penalty", 0.2),
            death_penalty=stage.get("death_penalty", 5.0),
            energy_penalty=stage.get("energy_penalty", 0.003),
            validation_survival_weight=stage.get(
                "validation_survival_weight", 0.0
            ),
            maximum_validation_invalid_rate=config["audit"][
                "maximum_invalid_action_rate"
            ],
            config=EnvConfig(**stage.get("env", {})),
        )
        previous = stage_checkpoint
        rows = _evaluate_scenarios(
            stage_checkpoint, validation_scenarios, seeds["validation"]
        )
        audit = _audit(rows, config["audit"])
        key = _selection_key(audit)
        selected = key > best_key
        if selected:
            best_key = key
            best_audit = audit
            shutil.copyfile(stage_checkpoint, selected_checkpoint)
        selection.append(
            {
                "stage": stage["name"],
                "selected": selected,
                "audit": audit,
            }
        )
        stage_summaries.append(
            {"name": stage["name"], "training": summary, "validation": rows}
        )
    test_rows = _evaluate_scenarios(
        selected_checkpoint, config["test"]["scenarios"], seeds["test"]
    )
    final_audit = _audit(test_rows, config["audit"])
    results = {
        "candidate": "curriculum-coordinated-ctde",
        "baseline": "assignment",
        "source_model": config["source_model"],
        "selection": selection,
        "selected_validation_audit": best_audit,
        "stages": stage_summaries,
        "scenarios": test_rows,
        "audit": final_audit,
    }
    (run_dir / "metrics.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    report = _write_report(run_dir, test_rows, final_audit)
    metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
    metadata["status"] = "complete"
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    if config.get("audit_registry_path"):
        _update_audit_registry(
            Path(config["audit_registry_path"]), run_dir, results, metadata
        )
    if final_audit["status"] == "passed" and config.get("registry_path"):
        promotion = {
            "status": "accepted",
            "candidate": "curriculum-coordinated-ctde",
            "baseline": "assignment",
            "checks": final_audit["checks"],
            "robustness": final_audit,
        }
        evaluation = {
            "curriculum-coordinated-ctde": {
                "mean_honey": sum(
                    row["candidate"]["mean_honey"] for row in test_rows
                )
                / len(test_rows)
            }
        }
        _update_registry(
            Path(config["registry_path"]),
            run_dir,
            selected_checkpoint,
            promotion,
            evaluation,
            metadata,
        )
    return {"run_dir": str(run_dir), "report": str(report), **results}
