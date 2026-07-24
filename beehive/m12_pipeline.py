"""M12 interleaved robustness training with validation-gated cycles."""

from __future__ import annotations

import json
import platform
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .ctde import train_ctde
from .env import EnvConfig
from .m10_pipeline import _audit, _update_audit_registry, _write_report
from .m11_pipeline import (
    _evaluate_scenarios,
    _scenario_seeds,
    _selection_key,
    _train_seeds,
)
from .pipeline import (
    _git_commit,
    _git_dirty,
    _update_registry,
    prepare_run_dir,
)
from .server import StrategyCatalog


def validate_m12_config(config: dict) -> dict[str, object]:
    required = (
        "experiment",
        "source_model",
        "training",
        "training_scenarios",
        "validation",
        "test",
        "audit",
    )
    missing = [field for field in required if field not in config]
    if missing:
        raise ValueError(f"missing M12 config fields: {', '.join(missing)}")
    if not isinstance(config["experiment"], str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]*", config["experiment"]
    ):
        raise ValueError("experiment may only contain letters, numbers, dot, dash and underscore")

    training = config["training"]
    for field in ("cycles", "episodes_per_cycle", "seed"):
        if not isinstance(training.get(field), int) or training[field] < 1:
            raise ValueError(f"training.{field} must be positive")
    scenarios = config["training_scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("training_scenarios must be non-empty")
    if training["episodes_per_cycle"] % len(scenarios):
        raise ValueError(
            "training.episodes_per_cycle must be divisible by training_scenarios"
        )
    names = set()
    for scenario in scenarios:
        name = scenario.get("name")
        if not isinstance(name, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]*", name
        ):
            raise ValueError("training scenario names must be safe identifiers")
        if name in names:
            raise ValueError(f"duplicate training scenario: {name}")
        names.add(name)
        EnvConfig(**scenario.get("env", {})).validate()

    occupied: dict[str, set[int]] = {}
    internal_validation_episodes = training.get("validation_episodes", 5)
    if (
        not isinstance(internal_validation_episodes, int)
        or internal_validation_episodes < 1
    ):
        raise ValueError("training.validation_episodes must be positive")
    for cycle in range(training["cycles"]):
        cycle_seed = training["seed"] + cycle * 100_000
        occupied[f"train:cycle-{cycle + 1}"] = _train_seeds(
            cycle_seed, training["episodes_per_cycle"]
        )
        occupied[f"internal-validation:cycle-{cycle + 1}"] = set(
            [
                candidate
                for candidate in range(cycle_seed + 10_000, cycle_seed + 20_000)
                if candidate % 10 == 8
            ][:internal_validation_episodes]
        )

    expanded: dict[str, dict[str, list[int]]] = {}
    for section in ("validation", "test"):
        value = config[section]
        if not isinstance(value.get("episodes"), int) or value["episodes"] < 1:
            raise ValueError(f"{section}.episodes must be positive")
        if not isinstance(value.get("seed"), int) or value["seed"] < 1:
            raise ValueError(f"{section}.seed must be positive")
        section_scenarios = value.get("scenarios")
        if not isinstance(section_scenarios, list) or not section_scenarios:
            raise ValueError(f"{section}.scenarios must be non-empty")
        section_names = set()
        for scenario in section_scenarios:
            name = scenario.get("name")
            if name in section_names:
                raise ValueError(f"duplicate {section} scenario: {name}")
            section_names.add(name)
            EnvConfig(**scenario.get("env", {})).validate()
        expanded[section] = _scenario_seeds(
            value["seed"], value["episodes"], section_scenarios
        )
        for name, seeds in expanded[section].items():
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
        **expanded,
    }


def run_m12_pipeline(
    config_path: str | Path,
    output_root: str | Path = "runs",
    force: bool = False,
) -> dict:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    seeds = validate_m12_config(config)
    run_dir = Path(output_root) / config["experiment"]
    prepare_run_dir(run_dir, config["experiment"], force)
    checkpoints = run_dir / "checkpoints"
    checkpoints.mkdir()
    shutil.copyfile(config_path, run_dir / "config.json")
    metadata = {
        "experiment": config["experiment"],
        "milestone": "M12",
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

    selected_checkpoint = checkpoints / "interleaved-ctde.pt"
    shutil.copyfile(source_checkpoint, selected_checkpoint)
    validation_scenarios = config["validation"]["scenarios"]
    validation_rows = _evaluate_scenarios(
        selected_checkpoint, validation_scenarios, seeds["validation"]
    )
    best_audit = _audit(validation_rows, config["audit"])
    best_key = _selection_key(best_audit)
    selection = [{"cycle": 0, "selected": True, "audit": best_audit}]
    cycle_summaries = []
    training = config["training"]
    scenario_configs = [
        (scenario["name"], EnvConfig(**scenario.get("env", {})))
        for scenario in config["training_scenarios"]
    ]

    for cycle in range(training["cycles"]):
        cycle_number = cycle + 1
        cycle_checkpoint = checkpoints / f"cycle-{cycle_number:02d}.pt"
        summary = train_ctde(
            selected_checkpoint,
            cycle_checkpoint,
            episodes=training["episodes_per_cycle"],
            seed=training["seed"] + cycle * 100_000,
            validation_episodes=training.get("validation_episodes", 5),
            rollout_workers=training.get("rollout_workers", 4),
            learning_rate=training.get("learning_rate", 5e-5),
            update_epochs=training.get("update_epochs", 4),
            batch_size=training.get("batch_size", 512),
            validation_interval=training.get(
                "validation_interval", training["episodes_per_cycle"]
            ),
            invalid_penalty=training.get("invalid_penalty", 0.2),
            death_penalty=training.get("death_penalty", 8.0),
            energy_penalty=training.get("energy_penalty", 0.005),
            maximum_validation_invalid_rate=config["audit"][
                "maximum_invalid_action_rate"
            ],
            config=scenario_configs[0][1],
            scenario_configs=scenario_configs,
            save_final=True,
        )
        rows = _evaluate_scenarios(
            cycle_checkpoint, validation_scenarios, seeds["validation"]
        )
        audit = _audit(rows, config["audit"])
        key = _selection_key(audit)
        selected = key > best_key
        if selected:
            best_key = key
            best_audit = audit
            shutil.copyfile(cycle_checkpoint, selected_checkpoint)
        selection.append(
            {"cycle": cycle_number, "selected": selected, "audit": audit}
        )
        cycle_summaries.append(
            {
                "cycle": cycle_number,
                "training": summary,
                "validation": rows,
                "selected": selected,
            }
        )

    test_rows = _evaluate_scenarios(
        selected_checkpoint, config["test"]["scenarios"], seeds["test"]
    )
    final_audit = _audit(test_rows, config["audit"])
    results = {
        "candidate": "interleaved-coordinated-ctde",
        "baseline": "assignment",
        "source_model": config["source_model"],
        "training_scenarios": [
            scenario["name"] for scenario in config["training_scenarios"]
        ],
        "selection": selection,
        "selected_validation_audit": best_audit,
        "cycles": cycle_summaries,
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
            "candidate": "interleaved-coordinated-ctde",
            "baseline": "assignment",
            "checks": final_audit["checks"],
            "robustness": final_audit,
        }
        evaluation = {
            "interleaved-coordinated-ctde": {
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
