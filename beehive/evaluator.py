"""Matched-seed controller evaluation."""

from __future__ import annotations

import math
import statistics
import time

from .controllers import Controller
from .env import BeeEnv, EnvConfig


def run_episode(controller: Controller, config: EnvConfig, seed: int) -> dict:
    env = BeeEnv(config, seed=seed)
    controller.reset(seed + 100_000)
    decision_ns = 0
    decisions = 0
    while not env.done:
        obs = env.observe()
        started = time.perf_counter_ns()
        actions = controller.act(obs)
        decision_ns += time.perf_counter_ns() - started
        decisions += len(actions)
        env.step(actions)
    metrics = env.metrics()
    controller_metrics = (
        controller.episode_metrics()
        if hasattr(controller, "episode_metrics")
        else {}
    )
    total_actions = config.bees * env.tick
    return {
        "seed": seed,
        **metrics,
        **controller_metrics,
        "colony_survived": int(metrics["alive"] > 0),
        "bee_survival_rate": metrics["alive"] / config.bees,
        "honey_per_bee": metrics["honey"] / config.bees,
        "invalid_action_rate": metrics["invalid_actions"] / max(1, total_actions),
        "decision_us": decision_ns / max(1, decisions) / 1_000,
    }


def evaluate(controller: Controller, config: EnvConfig, seeds: list[int]) -> dict:
    episodes = [run_episode(controller, config, seed) for seed in seeds]
    honey = [e["honey"] for e in episodes]
    mean = statistics.fmean(honey)
    std = statistics.stdev(honey) if len(honey) > 1 else 0.0
    ci95 = 1.96 * std / math.sqrt(len(honey)) if honey else 0.0
    result = {
        "controller": controller.name,
        "episodes": len(episodes),
        "mean_honey": mean,
        "ci95_honey": ci95,
        "colony_survival_rate": statistics.fmean(e["colony_survived"] for e in episodes),
        "bee_survival_rate": statistics.fmean(e["bee_survival_rate"] for e in episodes),
        "mean_alive_bees": statistics.fmean(e["alive"] for e in episodes),
        "mean_honey_per_bee": statistics.fmean(e["honey_per_bee"] for e in episodes),
        "mean_efficiency": statistics.fmean(e["efficiency"] for e in episodes),
        "mean_coverage": statistics.fmean(e["coverage"] for e in episodes),
        "mean_deaths": statistics.fmean(e["deaths"] for e in episodes),
        "mean_invalid_actions": statistics.fmean(e["invalid_actions"] for e in episodes),
        "mean_invalid_action_rate": statistics.fmean(e["invalid_action_rate"] for e in episodes),
        "mean_decision_us": statistics.fmean(e["decision_us"] for e in episodes),
        "raw": episodes,
    }
    for metric in (
        "harvest_intents",
        "contested_intents",
        "reservation_grants",
        "prevented_conflicts",
        "unresolved_conflicts",
        "contention_rate",
        "reservation_success_rate",
        "unresolved_contention_rate",
    ):
        if all(metric in episode for episode in episodes):
            result[f"mean_{metric}"] = statistics.fmean(
                episode[metric] for episode in episodes
            )
    return result


def paired_honey_comparison(left: dict, right: dict) -> dict:
    """Compare two evaluated controllers on their shared episode seeds."""
    right_by_seed = {row["seed"]: row["honey"] for row in right["raw"]}
    differences = [
        row["honey"] - right_by_seed[row["seed"]]
        for row in left["raw"]
        if row["seed"] in right_by_seed
    ]
    if not differences:
        raise ValueError("evaluations do not share any seeds")
    mean = statistics.fmean(differences)
    std = statistics.stdev(differences) if len(differences) > 1 else 0.0
    ci95 = 1.96 * std / math.sqrt(len(differences))
    return {
        "left": left["controller"],
        "right": right["controller"],
        "episodes": len(differences),
        "mean_honey_delta": mean,
        "ci95_honey_delta": ci95,
        "wins": sum(value > 0 for value in differences),
        "ties": sum(value == 0 for value in differences),
        "losses": sum(value < 0 for value in differences),
    }
