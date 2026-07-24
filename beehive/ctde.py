"""Centralized training with decentralized execution (CTDE)."""

from __future__ import annotations

import json
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .env import ACTIONS, BeeEnv, EnvConfig
from .evaluator import evaluate
from .ml import (
    FEATURE_SIZE,
    LOCAL_FEATURE_SIZE,
    LocalBehaviorCloningController,
    _build_sized_model,
    _torch,
    encode_bee,
    encode_local_bee,
    seed_split,
    valid_action_mask,
)
from .ppo import _masked_logits


class CTDEController(LocalBehaviorCloningController):
    """A decentralized actor that never receives the critic's global features."""

    name = "ctde-ppo"


def _rollout(
    actor,
    critic,
    config,
    seed,
    torch,
    invalid_penalty,
    death_penalty,
    energy_penalty,
) -> tuple[list[dict], dict]:
    env = BeeEnv(config, seed=seed)
    torch_generator = torch.Generator().manual_seed(seed + 300_000)
    per_bee: dict[int, list[dict]] = {}
    while not env.done:
        observation = env.observe()
        living = [bee for bee in observation["bees"] if bee["alive"]]
        local_list = [encode_local_bee(observation, bee["id"]) for bee in living]
        global_list = [encode_bee(observation, bee["id"]) for bee in living]
        masks = [valid_action_mask(observation, bee["id"]) for bee in living]
        local_features = torch.tensor(local_list, dtype=torch.float32)
        global_features = torch.tensor(global_list, dtype=torch.float32)
        with torch.no_grad():
            logits = _masked_logits(torch, actor(local_features), masks)
            probabilities = torch.softmax(logits, dim=-1)
            sampled = torch.multinomial(
                probabilities, 1, generator=torch_generator
            ).squeeze(-1)
            log_probs = torch.log_softmax(logits, dim=-1).gather(
                1, sampled.unsqueeze(1)
            ).squeeze(1)
            values = critic(global_features).squeeze(-1)
        actions = {
            bee["id"]: ACTIONS[action]
            for bee, action in zip(living, sampled.tolist())
        }
        before = env.metrics()
        env.step(actions)
        after = env.metrics()
        reward = (
            float(after["honey"] - before["honey"])
            - invalid_penalty
            * (after["invalid_actions"] - before["invalid_actions"])
            - death_penalty * (after["deaths"] - before["deaths"])
            - energy_penalty * (after["energy_spent"] - before["energy_spent"])
        )
        for index, bee in enumerate(living):
            per_bee.setdefault(bee["id"], []).append(
                {
                    "local": local_list[index],
                    "global": global_list[index],
                    "mask": masks[index],
                    "action": sampled[index].item(),
                    "old_log_prob": log_probs[index].item(),
                    "value": values[index].item(),
                    "reward": reward,
                    "done": env.done or not env.bees[bee["id"]].alive,
                }
            )

    transitions = []
    for trajectory in per_bee.values():
        advantage = 0.0
        next_value = 0.0
        for transition in reversed(trajectory):
            continuation = 0.0 if transition["done"] else 1.0
            delta = (
                transition["reward"]
                + 0.99 * next_value * continuation
                - transition["value"]
            )
            advantage = delta + 0.99 * 0.95 * continuation * advantage
            transition["advantage"] = advantage
            transition["return"] = advantage + transition["value"]
            next_value = transition["value"]
        transitions.extend(trajectory)
    return transitions, env.metrics()


def _save_actor(torch, actor, path, training=None):
    torch.save(
        {
            "state_dict": actor.state_dict(),
            "feature_size": LOCAL_FEATURE_SIZE,
            "training": training or {},
        },
        path,
    )


def _validation_metrics(actor, path, config, seeds, torch) -> dict:
    _save_actor(torch, actor, path)
    return evaluate(CTDEController(path), config, seeds)


def train_ctde(
    local_bc_path: str | Path,
    output_path: str | Path,
    episodes: int = 100,
    seed: int = 20500000,
    validation_episodes: int = 10,
    rollout_workers: int = 4,
    learning_rate: float = 1e-4,
    update_epochs: int = 4,
    batch_size: int = 512,
    validation_interval: int = 20,
    invalid_penalty: float = 0.1,
    death_penalty: float = 1.0,
    energy_penalty: float = 0.001,
    validation_survival_weight: float = 0.0,
    maximum_validation_invalid_rate: float = 0.01,
    config: EnvConfig | None = None,
) -> dict:
    torch = _torch()
    torch.set_num_threads(1)
    config = config or EnvConfig()
    torch.manual_seed(seed)
    generator = random.Random(seed)
    actor = _build_sized_model(torch, LOCAL_FEATURE_SIZE)
    checkpoint = torch.load(local_bc_path, map_location="cpu", weights_only=True)
    actor.load_state_dict(checkpoint["state_dict"])
    critic = torch.nn.Sequential(
        torch.nn.Linear(FEATURE_SIZE, 96),
        torch.nn.ReLU(),
        torch.nn.Linear(96, 96),
        torch.nn.ReLU(),
        torch.nn.Linear(96, 1),
    )
    optimizer = torch.optim.Adam(
        list(actor.parameters()) + list(critic.parameters()), lr=learning_rate
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate_path = output.with_suffix(".candidate.pt")
    validation_seeds = [
        candidate
        for candidate in range(seed + 10_000, seed + 20_000)
        if candidate % 10 == 8
    ][:validation_episodes]
    initial_validation = _validation_metrics(
        actor, candidate_path, config, validation_seeds, torch
    )
    best_honey = initial_validation["mean_honey"]
    best_validation_score = (
        best_honey
        + validation_survival_weight * initial_validation["bee_survival_rate"]
    )
    best_episode = 0
    _save_actor(
        torch,
        actor,
        output,
        {"best_validation_honey": best_honey, "best_episode": 0},
    )
    training_seeds = []
    candidate = seed
    while len(training_seeds) < episodes:
        if seed_split(candidate) == "train":
            training_seeds.append(candidate)
        candidate += 1

    history = []
    completed = 0
    for start_seed in range(0, len(training_seeds), rollout_workers):
        batch_seeds = training_seeds[start_seed : start_seed + rollout_workers]
        actor.eval()
        critic.eval()
        with ThreadPoolExecutor(max_workers=rollout_workers) as executor:
            rollouts = list(
                executor.map(
                    lambda episode_seed: _rollout(
                        actor,
                        critic,
                        config,
                        episode_seed,
                        torch,
                        invalid_penalty,
                        death_penalty,
                        energy_penalty,
                    ),
                    batch_seeds,
                )
            )
        transitions = [
            transition for rollout, _metrics in rollouts for transition in rollout
        ]
        advantages = torch.tensor(
            [transition["advantage"] for transition in transitions],
            dtype=torch.float32,
        )
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        indices = list(range(len(transitions)))
        actor.train()
        critic.train()
        for _ in range(update_epochs):
            generator.shuffle(indices)
            for batch_start in range(0, len(indices), batch_size):
                selected = indices[batch_start : batch_start + batch_size]
                local = torch.tensor(
                    [transitions[index]["local"] for index in selected],
                    dtype=torch.float32,
                )
                global_features = torch.tensor(
                    [transitions[index]["global"] for index in selected],
                    dtype=torch.float32,
                )
                masks = [transitions[index]["mask"] for index in selected]
                actions = torch.tensor(
                    [transitions[index]["action"] for index in selected],
                    dtype=torch.long,
                )
                old_log_probs = torch.tensor(
                    [transitions[index]["old_log_prob"] for index in selected],
                    dtype=torch.float32,
                )
                returns = torch.tensor(
                    [transitions[index]["return"] for index in selected],
                    dtype=torch.float32,
                )
                distribution = torch.distributions.Categorical(
                    logits=_masked_logits(torch, actor(local), masks)
                )
                log_probs = distribution.log_prob(actions)
                ratio = (log_probs - old_log_probs).exp()
                actor_loss = -torch.min(
                    ratio * advantages[selected],
                    ratio.clamp(0.8, 1.2) * advantages[selected],
                ).mean()
                value_loss = 0.5 * (
                    critic(global_features).squeeze(-1) - returns
                ).pow(2).mean()
                loss = (
                    actor_loss
                    + 0.5 * value_loss
                    - 0.01 * distribution.entropy().mean()
                )
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    list(actor.parameters()) + list(critic.parameters()), 0.5
                )
                optimizer.step()

        for episode_seed, (_rollout_data, metrics) in zip(batch_seeds, rollouts):
            completed += 1
            history.append(
                {
                    "episode": completed,
                    "seed": episode_seed,
                    "honey": metrics["honey"],
                    "alive": metrics["alive"],
                }
            )
        if completed % validation_interval == 0 or completed == episodes:
            actor.eval()
            validation = _validation_metrics(
                actor, candidate_path, config, validation_seeds, torch
            )
            validation_honey = validation["mean_honey"]
            validation_score = (
                validation_honey
                + validation_survival_weight * validation["bee_survival_rate"]
            )
            history[-1]["validation_honey"] = validation_honey
            history[-1]["validation_invalid_action_rate"] = validation[
                "mean_invalid_action_rate"
            ]
            history[-1]["validation_bee_survival_rate"] = validation[
                "bee_survival_rate"
            ]
            history[-1]["validation_score"] = validation_score
            if (
                validation_score > best_validation_score
                and validation["mean_invalid_action_rate"]
                <= maximum_validation_invalid_rate
            ):
                best_honey = validation_honey
                best_validation_score = validation_score
                best_episode = completed
                _save_actor(
                    torch,
                    actor,
                    output,
                    {
                        "best_validation_honey": best_honey,
                        "best_episode": best_episode,
                    },
                )
    candidate_path.unlink(missing_ok=True)
    summary = {
        "episodes": episodes,
        "rollout_workers": rollout_workers,
        "invalid_penalty": invalid_penalty,
        "death_penalty": death_penalty,
        "energy_penalty": energy_penalty,
        "validation_survival_weight": validation_survival_weight,
        "maximum_validation_invalid_rate": maximum_validation_invalid_rate,
        "best_episode": best_episode,
        "best_validation_honey": best_honey,
        "best_validation_score": best_validation_score,
        "validation_seeds": validation_seeds,
        "history": history,
    }
    output.with_suffix(".json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary
