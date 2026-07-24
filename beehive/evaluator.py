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
    return {
        "seed": seed,
        **metrics,
        "survived": int(metrics["alive"] > 0),
        "decision_us": decision_ns / max(1, decisions) / 1_000,
    }


def evaluate(controller: Controller, config: EnvConfig, seeds: list[int]) -> dict:
    episodes = [run_episode(controller, config, seed) for seed in seeds]
    honey = [e["honey"] for e in episodes]
    mean = statistics.fmean(honey)
    std = statistics.stdev(honey) if len(honey) > 1 else 0.0
    ci95 = 1.96 * std / math.sqrt(len(honey)) if honey else 0.0
    return {
        "controller": controller.name,
        "episodes": len(episodes),
        "mean_honey": mean,
        "ci95_honey": ci95,
        "survival_rate": statistics.fmean(e["survived"] for e in episodes),
        "mean_efficiency": statistics.fmean(e["efficiency"] for e in episodes),
        "mean_coverage": statistics.fmean(e["coverage"] for e in episodes),
        "mean_deaths": statistics.fmean(e["deaths"] for e in episodes),
        "mean_invalid_actions": statistics.fmean(e["invalid_actions"] for e in episodes),
        "mean_decision_us": statistics.fmean(e["decision_us"] for e in episodes),
        "raw": episodes,
    }
