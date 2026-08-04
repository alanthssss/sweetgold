"""M14 hierarchical return-control selection and robustness audit."""

from __future__ import annotations

import json
import platform
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .controllers import CONTROLLERS
from .env import EnvConfig
from .hardware import hardware_snapshot
from .evaluator import evaluate, paired_honey_comparison
from .hierarchical import HierarchicalReturnCTDEController
from .m10_pipeline import _audit, _update_audit_registry, _write_report
from .m11_pipeline import _scenario_seeds, _selection_key
from .pipeline import (
    _git_commit,
    _git_dirty,
    _summarize,
    _update_registry,
    prepare_run_dir,
)
from .server import StrategyCatalog


def validate_m14_config(config: dict) -> dict[str, object]:
    required = (
        "experiment",
        "source_model",
        "candidates",
        "validation",
        "test",
        "audit",
    )
    missing = [field for field in required if field not in config]
    if missing:
        raise ValueError(f"missing M14 config fields: {', '.join(missing)}")
    if not isinstance(config["experiment"], str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]*", config["experiment"]
    ):
        raise ValueError("experiment may only contain safe identifier characters")
    candidates = config["candidates"]
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidates must be a non-empty list")
    seen = set()
    for candidate in candidates:
        margin = candidate.get("safety_margin")
        recharge = candidate.get("recharge_fraction")
        if not isinstance(margin, int) or margin < 0:
            raise ValueError("candidate safety_margin must be non-negative")
        if not isinstance(recharge, (int, float)) or not 0 < recharge <= 1:
            raise ValueError("candidate recharge_fraction must be in (0, 1]")
        key = (margin, float(recharge))
        if key in seen:
            raise ValueError("duplicate M14 candidate")
        seen.add(key)

    expanded = {}
    occupied = {}
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
            if not isinstance(name, str) or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._-]*", name
            ):
                raise ValueError(f"{section} scenario names must be safe")
            if name in names:
                raise ValueError(f"duplicate {section} scenario: {name}")
            names.add(name)
            EnvConfig(**scenario.get("env", {})).validate()
        expanded[section] = _scenario_seeds(
            value["seed"], value["episodes"], scenarios
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


def _evaluate_candidate(
    checkpoint: Path,
    parameters: dict,
    scenarios: list[dict],
    seed_sets: dict[str, list[int]],
) -> list[dict]:
    rows = []
    for scenario in scenarios:
        name = scenario["name"]
        env_config = EnvConfig(**scenario.get("env", {}))
        candidate = evaluate(
            HierarchicalReturnCTDEController(checkpoint, **parameters),
            env_config,
            seed_sets[name],
        )
        baseline = evaluate(
            CONTROLLERS["assignment"](), env_config, seed_sets[name]
        )
        rows.append(
            {
                "name": name,
                "env": scenario.get("env", {}),
                "candidate": _summarize(candidate),
                "baseline": _summarize(baseline),
                "honey_ratio": candidate["mean_honey"]
                / max(1e-9, baseline["mean_honey"]),
                "comparison": paired_honey_comparison(candidate, baseline),
            }
        )
    return rows


def run_m14_pipeline(
    config_path: str | Path,
    output_root: str | Path = "runs",
    force: bool = False,
) -> dict:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    seeds = validate_m14_config(config)
    run_dir = Path(output_root) / config["experiment"]
    prepare_run_dir(run_dir, config["experiment"], force)
    checkpoints = run_dir / "checkpoints"
    checkpoints.mkdir()
    shutil.copyfile(config_path, run_dir / "config.json")
    metadata = {
        "experiment": config["experiment"],
        "milestone": "M14",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "python": sys.version,
        "platform": platform.platform(),
        "hardware": hardware_snapshot(),
        "seed_sets": seeds["occupied"],
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    catalog = StrategyCatalog(config.get("registry_path", "registry/models.json"))
    checkpoint = checkpoints / "hierarchical-return-ctde.pt"
    source_record = None
    if config.get("source_checkpoint"):
        shutil.copyfile(config["source_checkpoint"], checkpoint)
    else:
        catalog.create(config["source_model"])
        source_record = next(
            row
            for row in reversed(catalog._registry().get("models", []))
            if row.get("model") == config["source_model"]
        )
        shutil.copyfile(catalog._artifact(source_record), checkpoint)

    selection = []
    best = None
    for parameters in config["candidates"]:
        normalized = {
            "safety_margin": parameters["safety_margin"],
            "recharge_fraction": float(parameters["recharge_fraction"]),
        }
        rows = _evaluate_candidate(
            checkpoint,
            normalized,
            config["validation"]["scenarios"],
            seeds["validation"],
        )
        audit = _audit(rows, config["audit"])
        item = {
            "parameters": normalized,
            "scenarios": rows,
            "audit": audit,
            "selected": False,
        }
        selection.append(item)
        if best is None or _selection_key(audit) > _selection_key(best["audit"]):
            best = item
    assert best is not None
    best["selected"] = True
    selected = best["parameters"]

    test_rows = _evaluate_candidate(
        checkpoint, selected, config["test"]["scenarios"], seeds["test"]
    )
    final_audit = _audit(test_rows, config["audit"])
    results = {
        "candidate": "hierarchical-return-ctde",
        "baseline": "assignment",
        "source_model": config["source_model"],
        "selection": selection,
        "selected_parameters": selected,
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
            "candidate": results["candidate"],
            "baseline": results["baseline"],
            "checks": final_audit["checks"],
            "robustness": final_audit,
        }
        mean_honey = sum(
            row["candidate"]["mean_honey"] for row in test_rows
        ) / len(test_rows)
        _update_registry(
            Path(config["registry_path"]),
            run_dir,
            checkpoint,
            promotion,
            {results["candidate"]: {"mean_honey": mean_honey}},
            metadata,
        )
        registry_path = Path(config["registry_path"])
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["models"][-1]["controller_config"] = selected
        if source_record and source_record.get("download"):
            download = dict(source_record["download"])
            if config.get("model_card"):
                download["model_card"] = config["model_card"]
            registry["models"][-1]["download"] = download
        registry_path.write_text(
            json.dumps(registry, indent=2) + "\n", encoding="utf-8"
        )
    return {"run_dir": str(run_dir), "report": str(report), **results}
