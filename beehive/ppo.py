"""Optional PPO fine-tuning initialized from behavior cloning."""

from __future__ import annotations

import json
import random
from pathlib import Path

from .env import ACTIONS, BeeEnv, EnvConfig
from .evaluator import evaluate
from .ml import (
    FEATURE_SIZE,
    BehaviorCloningController,
    _build_model,
    _torch,
    encode_bee,
    seed_split,
    valid_action_mask,
)


def shaped_reward(
    honey_delta: int,
    invalid_delta: int,
    death_delta: int,
    energy_delta: int,
) -> float:
    """Keep honey dominant while discouraging invalid actions and deaths."""
    return (
        float(honey_delta)
        - 0.02 * invalid_delta
        - 1.0 * death_delta
        - 0.001 * energy_delta
    )


class PPOController(BehaviorCloningController):
    name = "bc-ppo"


class RandomPPOController(PPOController):
    name = "random-ppo"


def _masked_logits(torch, logits, masks):
    mask_tensor = torch.tensor(masks, dtype=torch.bool)
    return logits.masked_fill(~mask_tensor, -1e9)


def _episode_rollout(actor, critic, config, seed, torch) -> tuple[list[dict], dict]:
    env = BeeEnv(config, seed=seed)
    per_bee: dict[int, list[dict]] = {}
    while not env.done:
        observation = env.observe()
        living = [bee for bee in observation["bees"] if bee["alive"]]
        features_list = [encode_bee(observation, bee["id"]) for bee in living]
        masks = [valid_action_mask(observation, bee["id"]) for bee in living]
        features = torch.tensor(features_list, dtype=torch.float32)
        with torch.no_grad():
            logits = _masked_logits(torch, actor(features), masks)
            distribution = torch.distributions.Categorical(logits=logits)
            sampled = distribution.sample()
            log_probs = distribution.log_prob(sampled)
            values = critic(features).squeeze(-1)
        actions = {
            bee["id"]: ACTIONS[action]
            for bee, action in zip(living, sampled.tolist())
        }
        before = env.metrics()
        env.step(actions)
        after = env.metrics()
        reward = shaped_reward(
            after["honey"] - before["honey"],
            after["invalid_actions"] - before["invalid_actions"],
            after["deaths"] - before["deaths"],
            after["energy_spent"] - before["energy_spent"],
        )
        for index, bee in enumerate(living):
            per_bee.setdefault(bee["id"], []).append(
                {
                    "features": features_list[index],
                    "mask": masks[index],
                    "action": sampled[index].item(),
                    "old_log_prob": log_probs[index].item(),
                    "value": values[index].item(),
                    "reward": reward,
                    "done": env.done or not env.bees[bee["id"]].alive,
                }
            )

    transitions: list[dict] = []
    gamma, gae_lambda = 0.99, 0.95
    for trajectory in per_bee.values():
        advantage = 0.0
        next_value = 0.0
        for transition in reversed(trajectory):
            continuation = 0.0 if transition["done"] else 1.0
            delta = (
                transition["reward"]
                + gamma * next_value * continuation
                - transition["value"]
            )
            advantage = delta + gamma * gae_lambda * continuation * advantage
            transition["advantage"] = advantage
            transition["return"] = advantage + transition["value"]
            next_value = transition["value"]
        transitions.extend(trajectory)
    return transitions, env.metrics()


def _validation_honey(actor, checkpoint_path, config, seeds, torch) -> float:
    torch.save({"state_dict": actor.state_dict()}, checkpoint_path)
    result = evaluate(PPOController(checkpoint_path), config, seeds)
    return result["mean_honey"]


def train_ppo(
    bc_model_path: str | Path | None,
    output_path: str | Path,
    episodes: int = 100,
    seed: int = 20290000,
    validation_episodes: int = 10,
    learning_rate: float = 1e-4,
    update_epochs: int = 4,
    batch_size: int = 512,
    validation_interval: int = 10,
    config: EnvConfig | None = None,
) -> dict:
    torch = _torch()
    config = config or EnvConfig()
    torch.manual_seed(seed)
    generator = random.Random(seed)
    actor = _build_model(torch)
    if bc_model_path is not None:
        bc_checkpoint = torch.load(bc_model_path, map_location="cpu", weights_only=True)
        actor.load_state_dict(bc_checkpoint["state_dict"])
    critic = torch.nn.Sequential(
        torch.nn.Linear(FEATURE_SIZE, 96),
        torch.nn.ReLU(),
        torch.nn.Linear(96, 96),
        torch.nn.ReLU(),
        torch.nn.Linear(96, 1),
    )
    optimizer = torch.optim.Adam(
        list(actor.parameters()) + list(critic.parameters()),
        lr=learning_rate,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    candidate_path = output.with_suffix(".candidate.pt")
    validation_seeds = [
        candidate
        for candidate in range(seed + 10_000, seed + 20_000)
        if candidate % 10 == 8
    ][:validation_episodes]
    best_honey = _validation_honey(actor, candidate_path, config, validation_seeds, torch)
    best_episode = 0
    torch.save(
        {
            "state_dict": actor.state_dict(),
            "training": {"best_validation_honey": best_honey, "best_episode": 0},
        },
        output,
    )

    training_seeds = []
    candidate = seed
    while len(training_seeds) < episodes:
        if seed_split(candidate) == "train":
            training_seeds.append(candidate)
        candidate += 1

    history = []
    for episode_index, episode_seed in enumerate(training_seeds, 1):
        actor.eval()
        critic.eval()
        transitions, episode_metrics = _episode_rollout(
            actor, critic, config, episode_seed, torch
        )
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
            for start in range(0, len(indices), batch_size):
                selected = indices[start : start + batch_size]
                features = torch.tensor(
                    [transitions[index]["features"] for index in selected],
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
                batch_advantages = advantages[selected]
                logits = _masked_logits(torch, actor(features), masks)
                distribution = torch.distributions.Categorical(logits=logits)
                log_probs = distribution.log_prob(actions)
                ratio = (log_probs - old_log_probs).exp()
                clipped = ratio.clamp(0.8, 1.2)
                actor_loss = -torch.min(
                    ratio * batch_advantages,
                    clipped * batch_advantages,
                ).mean()
                value_loss = 0.5 * (
                    critic(features).squeeze(-1) - returns
                ).pow(2).mean()
                entropy = distribution.entropy().mean()
                loss = actor_loss + 0.5 * value_loss - 0.01 * entropy
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    list(actor.parameters()) + list(critic.parameters()), 0.5
                )
                optimizer.step()

        history.append(
            {
                "episode": episode_index,
                "seed": episode_seed,
                "honey": episode_metrics["honey"],
                "alive": episode_metrics["alive"],
            }
        )
        if episode_index % validation_interval == 0 or episode_index == episodes:
            actor.eval()
            validation_honey = _validation_honey(
                actor, candidate_path, config, validation_seeds, torch
            )
            history[-1]["validation_honey"] = validation_honey
            if validation_honey > best_honey:
                best_honey = validation_honey
                best_episode = episode_index
                torch.save(
                    {
                        "state_dict": actor.state_dict(),
                        "training": {
                            "best_validation_honey": best_honey,
                            "best_episode": best_episode,
                        },
                    },
                    output,
                )
    candidate_path.unlink(missing_ok=True)
    summary = {
        "initialization": "behavior-cloning" if bc_model_path is not None else "random",
        "episodes": episodes,
        "best_episode": best_episode,
        "best_validation_honey": best_honey,
        "validation_seeds": validation_seeds,
        "history": history,
    }
    output.with_suffix(".json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary
