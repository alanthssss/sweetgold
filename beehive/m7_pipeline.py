"""One-command M7 local-observation CTDE experiment."""

from __future__ import annotations

import json
import platform
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .controllers import CONTROLLERS
from .ctde import CTDEController, train_ctde
from .env import EnvConfig
from .hardware import hardware_snapshot
from .evaluator import evaluate, paired_honey_comparison
from .ml import (
    LocalBehaviorCloningController,
    collect_dagger,
    collect_dataset,
    encode_local_bee,
    seed_split,
    train_model,
)
from .pipeline import (
    _git_commit,
    _git_dirty,
    _summarize,
    _update_registry,
    prepare_run_dir,
    promotion_decision,
)
from .report import write_report


def _filtered(start: int, count: int, split: str) -> list[int]:
    seeds = []
    candidate = start
    while len(seeds) < count:
        if seed_split(candidate) == split:
            seeds.append(candidate)
        candidate += 1
    return seeds


def validate_m7_config(config: dict) -> dict[str, set[int]]:
    required = (
        "experiment",
        "data",
        "local_bc",
        "dagger",
        "ctde",
        "test",
        "promotion",
    )
    missing = [section for section in required if section not in config]
    if missing:
        raise ValueError(f"missing M7 config sections: {', '.join(missing)}")
    if not isinstance(config["experiment"], str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]*", config["experiment"]
    ):
        raise ValueError("experiment may only contain letters, numbers, dot, dash and underscore")
    for section in ("data", "dagger", "ctde", "test"):
        for key in ("episodes", "seed"):
            if not isinstance(config[section].get(key), int) or config[section][key] < 1:
                raise ValueError(f"{section}.{key} must be a positive integer")
    sets = {
        "data": set(
            range(
                config["data"]["seed"],
                config["data"]["seed"] + config["data"]["episodes"],
            )
        ),
        "dagger": set(
            _filtered(
                config["dagger"]["seed"],
                config["dagger"]["episodes"],
                "train",
            )
        ),
        "ctde_train": set(
            _filtered(
                config["ctde"]["seed"],
                config["ctde"]["episodes"],
                "train",
            )
        ),
        "ctde_validation": set(
            candidate
            for candidate in range(
                config["ctde"]["seed"] + 10_000,
                config["ctde"]["seed"] + 20_000,
            )
            if candidate % 10 == 8
        ),
        "final_test": set(
            _filtered(config["test"]["seed"], config["test"]["episodes"], "test")
        ),
    }
    sets["ctde_validation"] = set(
        sorted(sets["ctde_validation"])[
            : config["ctde"].get("validation_episodes", 10)
        ]
    )
    names = list(sets)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            if sets[left] & sets[right]:
                raise ValueError(f"seed leakage detected between {left} and {right}")
    EnvConfig(**config.get("env", {})).validate()
    return sets


def run_m7_pipeline(
    config_path: str | Path,
    output_root: str | Path = "runs",
    force: bool = False,
) -> dict:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    seed_sets = validate_m7_config(config)
    run_dir = Path(output_root) / config["experiment"]
    prepare_run_dir(run_dir, config["experiment"], force)
    checkpoints = run_dir / "checkpoints"
    checkpoints.mkdir()
    dataset_path = run_dir / "local-assignment.jsonl"
    local_bc_path = checkpoints / "local-behavior-cloning.pt"
    ctde_path = checkpoints / "ctde-ppo.pt"
    shutil.copyfile(config_path, run_dir / "config.json")
    metadata = {
        "experiment": config["experiment"],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "python": sys.version,
        "platform": platform.platform(),
        "hardware": hardware_snapshot(),
        "seed_sets": {name: sorted(seeds) for name, seeds in seed_sets.items()},
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    env_config = EnvConfig(**config.get("env", {}))
    counts = collect_dataset(
        dataset_path,
        config["data"]["episodes"],
        config["data"]["seed"],
        env_config,
        encoder=encode_local_bee,
    )
    local_bc_metrics = train_model(
        dataset_path,
        local_bc_path,
        epochs=config["local_bc"].get("epochs", 15),
        batch_size=config["local_bc"].get("batch_size", 512),
        learning_rate=config["local_bc"].get("learning_rate", 1e-3),
        seed=config["local_bc"].get("seed", 0),
    )
    dagger_examples = collect_dagger(
        dataset_path,
        local_bc_path,
        config["dagger"]["episodes"],
        config["dagger"]["seed"],
        env_config,
        encoder=encode_local_bee,
        controller_class=LocalBehaviorCloningController,
    )
    dataset_manifest = {
        "teacher": "assignment",
        "observation": {
            "type": "local",
            "manhattan_radius": 4,
        },
        "path": dataset_path.name,
        "episode_seeds": {
            split: sorted(
                seed for seed in seed_sets["data"] if seed_split(seed) == split
            )
            for split in ("train", "validation", "test")
        },
        "examples": counts,
        "dagger_episode_seeds": sorted(seed_sets["dagger"]),
        "dagger_examples": dagger_examples,
    }
    (run_dir / "dataset-manifest.json").write_text(
        json.dumps(dataset_manifest, indent=2), encoding="utf-8"
    )
    local_bc_metrics = train_model(
        dataset_path,
        local_bc_path,
        epochs=config["local_bc"].get("epochs", 15),
        batch_size=config["local_bc"].get("batch_size", 512),
        learning_rate=config["local_bc"].get("learning_rate", 1e-3),
        seed=config["local_bc"].get("seed", 0),
    )
    ctde_summary = train_ctde(
        local_bc_path,
        ctde_path,
        episodes=config["ctde"]["episodes"],
        seed=config["ctde"]["seed"],
        validation_episodes=config["ctde"].get("validation_episodes", 10),
        rollout_workers=config["ctde"].get("rollout_workers", 4),
        learning_rate=config["ctde"].get("learning_rate", 1e-4),
        update_epochs=config["ctde"].get("update_epochs", 4),
        batch_size=config["ctde"].get("batch_size", 512),
        validation_interval=config["ctde"].get("validation_interval", 20),
        invalid_penalty=config["ctde"].get("invalid_penalty", 0.1),
        maximum_validation_invalid_rate=config["promotion"].get(
            "maximum_invalid_action_rate", 0.01
        ),
        config=env_config,
    )
    test_seeds = sorted(seed_sets["final_test"])
    evaluated = [
        evaluate(controller, env_config, test_seeds)
        for controller in (
            CONTROLLERS["assignment"](),
            LocalBehaviorCloningController(local_bc_path),
            CTDEController(ctde_path),
        )
    ]
    write_report(evaluated, run_dir / "report")
    by_name = {result["controller"]: result for result in evaluated}
    comparison = paired_honey_comparison(
        by_name["ctde-ppo"], by_name["local-behavior-cloning"]
    )
    promotion = promotion_decision(
        by_name["ctde-ppo"],
        by_name["local-behavior-cloning"],
        comparison,
        config["promotion"],
    )
    results = {
        "dataset": {"counts": counts, "dagger_examples": dagger_examples},
        "local_behavior_cloning": local_bc_metrics,
        "ctde": ctde_summary,
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
    if promotion["status"] == "accepted" and config.get("registry_path"):
        _update_registry(
            Path(config["registry_path"]),
            run_dir,
            ctde_path,
            promotion,
            results["evaluation"],
            metadata,
        )
    return {"run_dir": str(run_dir), **results}
