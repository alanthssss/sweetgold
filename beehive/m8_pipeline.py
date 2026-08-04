"""One-command M8 decentralized contention-coordination experiment."""

from __future__ import annotations

import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .controllers import CONTROLLERS
from .coordination import CoordinatedCTDEController
from .ctde import CTDEController, train_ctde
from .env import EnvConfig
from .hardware import hardware_snapshot
from .evaluator import evaluate, paired_honey_comparison
from .m7_pipeline import validate_m7_config
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


def validate_m8_config(config: dict) -> dict[str, set[int]]:
    """M8 preserves M7 seed isolation and adds a coordination gate."""
    sets = validate_m7_config(config)
    maximum_contention = config["promotion"].get(
        "maximum_unresolved_contention_rate"
    )
    if maximum_contention is None or not 0 <= maximum_contention <= 1:
        raise ValueError(
            "promotion.maximum_unresolved_contention_rate must be between zero and one"
        )
    return sets


def run_m8_pipeline(
    config_path: str | Path,
    output_root: str | Path = "runs",
    force: bool = False,
) -> dict:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    seed_sets = validate_m8_config(config)
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
        "milestone": "M8",
        "coordination": {
            "scope": "same-flower local peers",
            "protocol": "intent broadcast with rotating-priority reservations",
        },
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
    train_model(
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
        "observation": {"type": "local", "manhattan_radius": 4},
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
            CoordinatedCTDEController(ctde_path),
        )
    ]
    write_report(evaluated, run_dir / "report")
    by_name = {result["controller"]: result for result in evaluated}
    comparison = paired_honey_comparison(
        by_name["coordinated-ctde"], by_name["local-behavior-cloning"]
    )
    coordination_comparison = paired_honey_comparison(
        by_name["coordinated-ctde"], by_name["ctde-ppo"]
    )
    promotion = promotion_decision(
        by_name["coordinated-ctde"],
        by_name["local-behavior-cloning"],
        comparison,
        config["promotion"],
    )
    promotion["checks"]["maximum_unresolved_contention_rate"] = (
        by_name["coordinated-ctde"]["mean_unresolved_contention_rate"]
        <= config["promotion"]["maximum_unresolved_contention_rate"]
    )
    promotion["status"] = (
        "accepted" if all(promotion["checks"].values()) else "rejected"
    )
    results = {
        "dataset": {"counts": counts, "dagger_examples": dagger_examples},
        "local_behavior_cloning": local_bc_metrics,
        "ctde": ctde_summary,
        "evaluation": {name: _summarize(result) for name, result in by_name.items()},
        "paired_comparison": comparison,
        "coordination_vs_uncoordinated": coordination_comparison,
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
