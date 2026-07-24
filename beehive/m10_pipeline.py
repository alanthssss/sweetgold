"""M10 cross-distribution generalization and robustness audit."""

from __future__ import annotations

import html
import json
import platform
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .env import EnvConfig
from .evaluator import evaluate, paired_honey_comparison
from .ml import seed_split
from .pipeline import _git_commit, _git_dirty, _summarize, prepare_run_dir
from .server import StrategyCatalog


def _test_seeds(start: int, count: int) -> list[int]:
    seeds = []
    candidate = start
    while len(seeds) < count:
        if seed_split(candidate) == "test":
            seeds.append(candidate)
        candidate += 1
    return seeds


def validate_m10_config(config: dict) -> dict[str, list[int]]:
    for section in ("experiment", "candidate", "baseline", "episodes", "seed", "scenarios", "audit"):
        if section not in config:
            raise ValueError(f"missing M10 config field: {section}")
    if not isinstance(config["experiment"], str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]*", config["experiment"]
    ):
        raise ValueError("experiment may only contain letters, numbers, dot, dash and underscore")
    if not isinstance(config["episodes"], int) or config["episodes"] < 1:
        raise ValueError("episodes must be a positive integer")
    if not isinstance(config["seed"], int) or config["seed"] < 1:
        raise ValueError("seed must be a positive integer")
    if not isinstance(config["scenarios"], list) or not config["scenarios"]:
        raise ValueError("scenarios must be a non-empty list")
    names = []
    seed_sets = {}
    for index, scenario in enumerate(config["scenarios"]):
        name = scenario.get("name")
        if not isinstance(name, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]*", name
        ):
            raise ValueError("scenario names must be safe identifiers")
        if name in names:
            raise ValueError(f"duplicate scenario name: {name}")
        names.append(name)
        EnvConfig(**scenario.get("env", {})).validate()
        scenario_start = config["seed"] + index * 100_000
        seed_sets[name] = _test_seeds(scenario_start, config["episodes"])
    flattened = [seed for seeds in seed_sets.values() for seed in seeds]
    if len(flattened) != len(set(flattened)):
        raise ValueError("scenario seed leakage detected")
    for threshold in (
        "minimum_median_honey_ratio",
        "minimum_worst_honey_ratio",
        "minimum_bee_survival",
        "maximum_invalid_action_rate",
    ):
        value = config["audit"].get(threshold)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"audit.{threshold} must be between zero and one")
    return seed_sets


def _audit(scenarios: list[dict], thresholds: dict) -> dict:
    ratios = [row["honey_ratio"] for row in scenarios]
    survivals = [row["candidate"]["bee_survival_rate"] for row in scenarios]
    invalid_rates = [
        row["candidate"]["mean_invalid_action_rate"] for row in scenarios
    ]
    sorted_ratios = sorted(ratios)
    middle = len(sorted_ratios) // 2
    median = (
        sorted_ratios[middle]
        if len(sorted_ratios) % 2
        else (sorted_ratios[middle - 1] + sorted_ratios[middle]) / 2
    )
    checks = {
        "minimum_median_honey_ratio": median
        >= thresholds["minimum_median_honey_ratio"],
        "minimum_worst_honey_ratio": min(ratios)
        >= thresholds["minimum_worst_honey_ratio"],
        "minimum_bee_survival": min(survivals)
        >= thresholds["minimum_bee_survival"],
        "maximum_invalid_action_rate": max(invalid_rates)
        <= thresholds["maximum_invalid_action_rate"],
    }
    return {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "median_honey_ratio": median,
        "worst_honey_ratio": min(ratios),
        "worst_honey_scenario": min(scenarios, key=lambda row: row["honey_ratio"])[
            "name"
        ],
        "minimum_bee_survival": min(survivals),
        "maximum_invalid_action_rate": max(invalid_rates),
    }


def _write_report(run_dir: Path, rows: list[dict], audit: dict) -> Path:
    table = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['name'])}</td>"
        f"<td>{row['candidate']['mean_honey']:.2f}</td>"
        f"<td>{row['baseline']['mean_honey']:.2f}</td>"
        f"<td>{row['honey_ratio']:.1%}</td>"
        f"<td>{row['comparison']['mean_honey_delta']:+.2f} ± {row['comparison']['ci95_honey_delta']:.2f}</td>"
        f"<td>{row['candidate']['bee_survival_rate']:.1%}</td>"
        f"<td>{row['candidate']['mean_invalid_action_rate']:.2%}</td>"
        "</tr>"
        for row in rows
    )
    document = f"""<!doctype html><html><meta charset="utf-8">
<title>SweetGold M10 Robustness Audit</title>
<style>
body{{margin:0;background:#f1eddf;color:#171c17;font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1100px;margin:auto;padding:50px 24px}}h1{{font:800 48px Georgia,serif;margin:8px 0}}
.status{{display:inline-block;padding:7px 12px;border-radius:99px;background:{'#3e6947' if audit['status']=='passed' else '#b64c3f'};color:white;font-weight:800}}
.card{{margin-top:25px;background:#fffdf7;border:1px solid #d8d1bd;border-radius:16px;padding:20px;overflow:auto}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:12px 10px;border-bottom:1px solid #e7e1d2;text-align:right}}th:first-child,td:first-child{{text-align:left}}
th{{font-size:11px;letter-spacing:.08em;color:#697066;text-transform:uppercase}}
</style><main><span class="status">{audit['status'].upper()}</span>
<h1>Generalization audit</h1>
<p>Median yield ratio {audit['median_honey_ratio']:.1%}; worst case {audit['worst_honey_ratio']:.1%} in {html.escape(audit['worst_honey_scenario'])}.</p>
<section class="card"><table><thead><tr><th>Scenario</th><th>Candidate</th><th>Baseline</th><th>Ratio</th><th>Paired delta</th><th>Survival</th><th>Invalid</th></tr></thead><tbody>{table}</tbody></table></section>
</main></html>"""
    path = run_dir / "report.html"
    path.write_text(document, encoding="utf-8")
    return path


def _update_audit_registry(
    path: Path, run_dir: Path, results: dict, metadata: dict
) -> None:
    registry = (
        json.loads(path.read_text(encoding="utf-8"))
        if path.exists()
        else {"audits": []}
    )
    record = {
        "run": str(run_dir),
        "candidate": results["candidate"],
        "baseline": results["baseline"],
        "status": results["audit"]["status"],
        "source_commit": metadata["git_commit"],
        "source_dirty": metadata["git_dirty"],
        "audited_at": metadata["completed_at"],
        "summary": results["audit"],
        "scenarios": [
            {
                "name": row["name"],
                "honey_ratio": row["honey_ratio"],
                "bee_survival_rate": row["candidate"]["bee_survival_rate"],
                "invalid_action_rate": row["candidate"][
                    "mean_invalid_action_rate"
                ],
            }
            for row in results["scenarios"]
        ],
    }
    audits = registry.setdefault("audits", [])
    audits[:] = [row for row in audits if row.get("run") != record["run"]]
    audits.append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def run_m10_pipeline(
    config_path: str | Path,
    output_root: str | Path = "runs",
    force: bool = False,
) -> dict:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    seed_sets = validate_m10_config(config)
    run_dir = Path(output_root) / config["experiment"]
    prepare_run_dir(run_dir, config["experiment"], force)
    shutil.copyfile(config_path, run_dir / "config.json")
    metadata = {
        "experiment": config["experiment"],
        "milestone": "M10",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "python": sys.version,
        "platform": platform.platform(),
        "seed_sets": seed_sets,
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    catalog = StrategyCatalog(config.get("registry_path", "registry/models.json"))
    rows = []
    for scenario in config["scenarios"]:
        name = scenario["name"]
        env_config = EnvConfig(**scenario.get("env", {}))
        candidate = evaluate(
            catalog.create(config["candidate"]), env_config, seed_sets[name]
        )
        baseline = evaluate(
            catalog.create(config["baseline"]), env_config, seed_sets[name]
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
    audit = _audit(rows, config["audit"])
    results = {
        "candidate": config["candidate"],
        "baseline": config["baseline"],
        "scenarios": rows,
        "audit": audit,
    }
    (run_dir / "metrics.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    report = _write_report(run_dir, rows, audit)
    metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
    metadata["status"] = "complete"
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    if config.get("audit_registry_path"):
        _update_audit_registry(
            Path(config["audit_registry_path"]), run_dir, results, metadata
        )
    return {"run_dir": str(run_dir), "report": str(report), **results}
