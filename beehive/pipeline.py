"""Configuration-driven, reproducible SweetGold ML experiment pipeline."""

from __future__ import annotations

import json
import hashlib
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .controllers import CONTROLLERS
from .env import EnvConfig
from .hardware import hardware_snapshot
from .evaluator import evaluate, paired_honey_comparison
from .ml import (
    BehaviorCloningController,
    collect_dagger,
    collect_dataset,
    seed_split,
    train_model,
)
from .ppo import PPOController, train_ppo
from .report import write_report


REQUIRED_SECTIONS = ("experiment", "data", "bc", "dagger", "ppo", "test", "promotion")


def load_config(path: str | Path) -> dict:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def _filtered_seeds(start: int, count: int, split: str) -> list[int]:
    seeds = []
    candidate = start
    while len(seeds) < count:
        if seed_split(candidate) == split:
            seeds.append(candidate)
        candidate += 1
    return seeds


def experiment_seed_sets(config: dict) -> dict[str, set[int]]:
    data_seeds = set(
        range(config["data"]["seed"], config["data"]["seed"] + config["data"]["episodes"])
    )
    dagger_seeds = set(
        _filtered_seeds(
            config["dagger"]["seed"],
            config["dagger"]["episodes"],
            "train",
        )
    )
    ppo_train = set(
        _filtered_seeds(config["ppo"]["seed"], config["ppo"]["episodes"], "train")
    )
    ppo_validation = set(
        candidate
        for candidate in range(
            config["ppo"]["seed"] + 10_000,
            config["ppo"]["seed"] + 20_000,
        )
        if candidate % 10 == 8
    )
    ppo_validation = set(
        sorted(ppo_validation)[: config["ppo"].get("validation_episodes", 10)]
    )
    final_test = set(
        _filtered_seeds(config["test"]["seed"], config["test"]["episodes"], "test")
    )
    return {
        "data": data_seeds,
        "dagger": dagger_seeds,
        "ppo_train": ppo_train,
        "ppo_validation": ppo_validation,
        "final_test": final_test,
    }


def validate_config(config: dict) -> None:
    missing = [section for section in REQUIRED_SECTIONS if section not in config]
    if missing:
        raise ValueError(f"missing pipeline config sections: {', '.join(missing)}")
    if not isinstance(config["experiment"], str) or not config["experiment"].strip():
        raise ValueError("experiment must be a non-empty string")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", config["experiment"]):
        raise ValueError("experiment may only contain letters, numbers, dot, dash and underscore")
    for section in ("data", "dagger", "ppo", "test"):
        for key in ("episodes", "seed"):
            value = config[section].get(key)
            if not isinstance(value, int) or value < 1:
                raise ValueError(f"{section}.{key} must be a positive integer")
    seed_sets = experiment_seed_sets(config)
    names = list(seed_sets)
    overlaps = []
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            shared = seed_sets[left] & seed_sets[right]
            if shared:
                overlaps.append(f"{left}/{right}: {sorted(shared)[:3]}")
    if overlaps:
        raise ValueError("seed leakage detected: " + "; ".join(overlaps))
    EnvConfig(**config.get("env", {})).validate()


def promotion_decision(
    candidate: dict,
    baseline: dict,
    comparison: dict,
    thresholds: dict,
) -> dict:
    lower_bound = (
        comparison["mean_honey_delta"] - comparison["ci95_honey_delta"]
    )
    checks = {
        "paired_ci_above_zero": lower_bound > 0,
        "minimum_honey_ratio": (
            candidate["mean_honey"] / max(1e-9, baseline["mean_honey"])
            >= thresholds.get("minimum_honey_ratio", 1.0)
        ),
        "minimum_bee_survival": (
            candidate["bee_survival_rate"]
            >= thresholds.get("minimum_bee_survival", 0.9)
        ),
        "maximum_invalid_action_rate": (
            candidate["mean_invalid_action_rate"]
            <= thresholds.get("maximum_invalid_action_rate", 0.01)
        ),
    }
    return {
        "status": "accepted" if all(checks.values()) else "rejected",
        "candidate": candidate["controller"],
        "baseline": baseline["controller"],
        "checks": checks,
        "paired_ci95_lower_bound": lower_bound,
    }


def _git_commit() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _git_dirty() -> bool | None:
    try:
        return bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return None


def _summarize(result: dict) -> dict:
    return {key: value for key, value in result.items() if key != "raw"}


def _update_registry(
    path: Path,
    run_dir: Path,
    checkpoint: Path,
    promotion: dict,
    metrics: dict,
    metadata: dict,
) -> None:
    registry = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"models": []}
    record = {
        "model": promotion["candidate"],
        "run": str(run_dir),
        "artifact": str(checkpoint),
        "sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        "source_commit": metadata["git_commit"],
        "source_dirty": metadata["git_dirty"],
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "mean_honey": metrics[promotion["candidate"]]["mean_honey"],
        "promotion": promotion,
    }
    models = registry.setdefault("models", [])
    models[:] = [
        existing
        for existing in models
        if not (
            existing.get("model") == record["model"]
            and existing.get("run") == record["run"]
        )
    ]
    models.append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def prepare_run_dir(run_dir: Path, experiment: str, force: bool) -> None:
    if run_dir.exists():
        if not force:
            raise FileExistsError(f"run already exists: {run_dir}")
        metadata_path = run_dir / "metadata.json"
        try:
            existing = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"refusing to replace unrecognized run directory: {run_dir}"
            ) from exc
        if existing.get("experiment") != experiment:
            raise ValueError(f"refusing to replace a different experiment: {run_dir}")
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)


def run_pipeline(
    config_path: str | Path,
    output_root: str | Path = "runs",
    force: bool = False,
) -> dict:
    config = load_config(config_path)
    run_dir = Path(output_root) / config["experiment"]
    prepare_run_dir(run_dir, config["experiment"], force)
    checkpoints = run_dir / "checkpoints"
    checkpoints.mkdir()
    report_dir = run_dir / "report"
    dataset_path = run_dir / "assignment.jsonl"
    bc_path = checkpoints / "behavior-cloning.pt"
    ppo_path = checkpoints / "bc-ppo.pt"

    shutil.copyfile(config_path, run_dir / "config.json")
    seed_sets = experiment_seed_sets(config)
    metadata = {
        "experiment": config["experiment"],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "python": sys.version,
        "platform": platform.platform(),
        "hardware": hardware_snapshot(),
        "seed_sets": {key: sorted(value) for key, value in seed_sets.items()},
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    env_config = EnvConfig(**config.get("env", {}))
    dataset_counts = collect_dataset(
        dataset_path,
        config["data"]["episodes"],
        config["data"]["seed"],
        env_config,
    )
    bc_metrics = train_model(
        dataset_path,
        bc_path,
        epochs=config["bc"].get("epochs", 15),
        batch_size=config["bc"].get("batch_size", 512),
        learning_rate=config["bc"].get("learning_rate", 1e-3),
        seed=config["bc"].get("seed", 0),
    )
    dagger_examples = collect_dagger(
        dataset_path,
        bc_path,
        config["dagger"]["episodes"],
        config["dagger"]["seed"],
        env_config,
    )
    dataset_manifest = {
        "teacher": "assignment",
        "path": dataset_path.name,
        "episode_seeds": {
            split: sorted(
                seed for seed in seed_sets["data"] if seed_split(seed) == split
            )
            for split in ("train", "validation", "test")
        },
        "examples": dataset_counts,
        "dagger_episode_seeds": sorted(seed_sets["dagger"]),
        "dagger_examples": dagger_examples,
    }
    (run_dir / "dataset-manifest.json").write_text(
        json.dumps(dataset_manifest, indent=2), encoding="utf-8"
    )
    bc_metrics = train_model(
        dataset_path,
        bc_path,
        epochs=config["bc"].get("epochs", 15),
        batch_size=config["bc"].get("batch_size", 512),
        learning_rate=config["bc"].get("learning_rate", 1e-3),
        seed=config["bc"].get("seed", 0),
    )
    ppo_summary = train_ppo(
        bc_path,
        ppo_path,
        episodes=config["ppo"]["episodes"],
        seed=config["ppo"]["seed"],
        validation_episodes=config["ppo"].get("validation_episodes", 10),
        learning_rate=config["ppo"].get("learning_rate", 1e-4),
        update_epochs=config["ppo"].get("update_epochs", 4),
        batch_size=config["ppo"].get("batch_size", 512),
        validation_interval=config["ppo"].get("validation_interval", 10),
        config=env_config,
    )
    test_seeds = sorted(seed_sets["final_test"])
    evaluated = [
        evaluate(controller, env_config, test_seeds)
        for controller in (
            CONTROLLERS["assignment"](),
            CONTROLLERS["greedy"](),
            BehaviorCloningController(bc_path),
            PPOController(ppo_path),
        )
    ]
    write_report(evaluated, report_dir)
    by_name = {result["controller"]: result for result in evaluated}
    comparison = paired_honey_comparison(
        by_name["bc-ppo"], by_name["behavior-cloning"]
    )
    promotion = promotion_decision(
        by_name["bc-ppo"],
        by_name["behavior-cloning"],
        comparison,
        config["promotion"],
    )
    results = {
        "dataset": {"counts": dataset_counts, "dagger_examples": dagger_examples},
        "behavior_cloning": bc_metrics,
        "ppo": ppo_summary,
        "evaluation": {name: _summarize(result) for name, result in by_name.items()},
        "paired_comparison": comparison,
        "promotion": promotion,
    }
    (run_dir / "metrics.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
    metadata["status"] = "complete"
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    registry_path = config.get("registry_path")
    if promotion["status"] == "accepted" and registry_path:
        _update_registry(
            Path(registry_path),
            run_dir,
            ppo_path,
            promotion,
            results["evaluation"],
            metadata,
        )
    return {"run_dir": str(run_dir), **results}
