"""Optional PyTorch behavior-cloning pipeline.

The simulation remains dependency-free. Importing this module only requires
PyTorch when training a model or constructing BehaviorCloningController.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

from .controllers import AssignmentController
from .env import ACTIONS, BeeEnv, EnvConfig


ACTION_INDEX = {action: index for index, action in enumerate(ACTIONS)}
NEAREST_FLOWERS = 14
OTHER_BEES = 7
FEATURE_SIZE = 13 + NEAREST_FLOWERS * 3 + OTHER_BEES * 5
LOCAL_RADIUS = 4
LOCAL_FLOWERS = 6
LOCAL_BEES = 4
LOCAL_SIGNALS = 3
LOCAL_FEATURE_SIZE = 13 + LOCAL_FLOWERS * 3 + LOCAL_BEES * 5 + LOCAL_SIGNALS * 4


def seed_split(seed: int) -> str:
    """Deterministically assign whole episodes to disjoint dataset splits."""
    bucket = seed % 10
    return "train" if bucket < 7 else "validation" if bucket < 9 else "test"


def encode_bee(observation: dict, bee_id: int) -> list[float]:
    """Encode a global observation from one bee's point of view."""
    config = observation["config"]
    bee = next(bee for bee in observation["bees"] if bee["id"] == bee_id)
    row, col = bee["row"], bee["col"]
    hive_row, hive_col = observation["hive"]
    height = max(1, config["height"] - 1)
    width = max(1, config["width"] - 1)
    features = [
        row / height,
        col / width,
        bee["energy"] / config["max_energy"],
        bee["cargo"] / config["max_cargo"],
        bee["id"] / max(1, config["bees"] - 1),
        (hive_row - row) / height,
        (hive_col - col) / width,
        observation["tick"] / config["season_ticks"],
        float(observation["weather"] == "rain"),
        observation["stored_honey"] / max(1, config["bees"] * config["max_cargo"]),
        sum(other["alive"] for other in observation["bees"]) / config["bees"],
        len(observation["signals"]) / 12,
        float((row, col) == (hive_row, hive_col)),
    ]
    flowers = sorted(
        (flower for flower in observation["flowers"] if flower["nectar"] > 0),
        key=lambda flower: (
            abs(flower["row"] - row) + abs(flower["col"] - col),
            -flower["nectar"],
        ),
    )
    for index in range(NEAREST_FLOWERS):
        if index < len(flowers):
            flower = flowers[index]
            features.extend(
                [
                    (flower["row"] - row) / height,
                    (flower["col"] - col) / width,
                    flower["nectar"] / config["flower_capacity"],
                ]
            )
        else:
            features.extend([0.0, 0.0, 0.0])
    others = sorted(
        (other for other in observation["bees"] if other["id"] != bee_id),
        key=lambda other: (
            abs(other["row"] - row) + abs(other["col"] - col),
            other["id"],
        ),
    )
    for index in range(OTHER_BEES):
        if index < len(others):
            other = others[index]
            features.extend(
                [
                    (other["row"] - row) / height,
                    (other["col"] - col) / width,
                    other["energy"] / config["max_energy"],
                    other["cargo"] / config["max_cargo"],
                    float(other["alive"]),
                ]
            )
        else:
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0])
    return features


def encode_local_bee(observation: dict, bee_id: int) -> list[float]:
    """Encode only entities within a fixed Manhattan radius of one bee."""
    config = observation["config"]
    bee = next(bee for bee in observation["bees"] if bee["id"] == bee_id)
    row, col = bee["row"], bee["col"]
    hive_row, hive_col = observation["hive"]
    height = max(1, config["height"] - 1)
    width = max(1, config["width"] - 1)
    features = [
        row / height,
        col / width,
        bee["energy"] / config["max_energy"],
        bee["cargo"] / config["max_cargo"],
        bee["id"] / max(1, config["bees"] - 1),
        (hive_row - row) / height,
        (hive_col - col) / width,
        observation["tick"] / config["season_ticks"],
        float(observation["weather"] == "rain"),
        observation["stored_honey"] / max(1, config["bees"] * config["max_cargo"]),
        sum(other["alive"] for other in observation["bees"]) / config["bees"],
        len(observation["signals"]) / 12,
        float((row, col) == (hive_row, hive_col)),
    ]

    def distance(entity: dict) -> int:
        return abs(entity["row"] - row) + abs(entity["col"] - col)

    flowers = sorted(
        (
            flower
            for flower in observation["flowers"]
            if flower["nectar"] > 0 and distance(flower) <= LOCAL_RADIUS
        ),
        key=lambda flower: (distance(flower), -flower["nectar"]),
    )
    for index in range(LOCAL_FLOWERS):
        if index < len(flowers):
            flower = flowers[index]
            features.extend(
                [
                    (flower["row"] - row) / LOCAL_RADIUS,
                    (flower["col"] - col) / LOCAL_RADIUS,
                    flower["nectar"] / config["flower_capacity"],
                ]
            )
        else:
            features.extend([0.0, 0.0, 0.0])

    others = sorted(
        (
            other
            for other in observation["bees"]
            if other["id"] != bee_id and distance(other) <= LOCAL_RADIUS
        ),
        key=lambda other: (distance(other), other["id"]),
    )
    for index in range(LOCAL_BEES):
        if index < len(others):
            other = others[index]
            features.extend(
                [
                    (other["row"] - row) / LOCAL_RADIUS,
                    (other["col"] - col) / LOCAL_RADIUS,
                    other["energy"] / config["max_energy"],
                    other["cargo"] / config["max_cargo"],
                    float(other["alive"]),
                ]
            )
        else:
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0])

    signals = sorted(
        (
            signal
            for signal in observation["signals"]
            if distance(signal) <= LOCAL_RADIUS
        ),
        key=lambda signal: (distance(signal), -signal["tick"]),
    )
    for index in range(LOCAL_SIGNALS):
        if index < len(signals):
            signal = signals[index]
            features.extend(
                [
                    (signal["row"] - row) / LOCAL_RADIUS,
                    (signal["col"] - col) / LOCAL_RADIUS,
                    signal["value"] / config["flower_capacity"],
                    (observation["tick"] - signal["tick"]) / 20,
                ]
            )
        else:
            features.extend([0.0, 0.0, 0.0, 0.0])
    return features


def valid_action_mask(observation: dict, bee_id: int) -> list[bool]:
    bee = next(bee for bee in observation["bees"] if bee["id"] == bee_id)
    row, col = bee["row"], bee["col"]
    config = observation["config"]
    hive = tuple(observation["hive"])
    flower = next(
        (
            flower
            for flower in observation["flowers"]
            if (flower["row"], flower["col"]) == (row, col)
        ),
        None,
    )
    return [
        row > 0,
        row + 1 < config["height"],
        col > 0,
        col + 1 < config["width"],
        bool(flower and flower["nectar"] > 0 and bee["cargo"] < config["max_cargo"]),
        (row, col) == hive and bee["cargo"] > 0,
        True,
        bool(flower and flower["nectar"] > 0),
    ]


def collect_dataset(
    output_path: str | Path,
    episodes: int,
    seed: int,
    config: EnvConfig | None = None,
    encoder=encode_bee,
) -> dict[str, int]:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    counts = {"train": 0, "validation": 0, "test": 0}
    teacher = AssignmentController()
    with output.open("w", encoding="utf-8") as handle:
        for episode_seed in range(seed, seed + episodes):
            env = BeeEnv(config, seed=episode_seed)
            teacher.reset(episode_seed + 100_000)
            split = seed_split(episode_seed)
            while not env.done:
                observation = env.observe()
                actions = teacher.act(observation)
                for bee in observation["bees"]:
                    if not bee["alive"]:
                        continue
                    row = {
                        "seed": episode_seed,
                        "split": split,
                        "bee_id": bee["id"],
                        "features": encoder(observation, bee["id"]),
                        "action": ACTION_INDEX[actions[bee["id"]]],
                    }
                    handle.write(json.dumps(row, separators=(",", ":")) + "\n")
                    counts[split] += 1
                env.step(actions)
    return counts


def collect_dagger(
    dataset_path: str | Path,
    model_path: str | Path,
    episodes: int,
    seed: int,
    config: EnvConfig | None = None,
    encoder=encode_bee,
    controller_class=None,
) -> int:
    """Append teacher labels for states visited by the current learned policy."""
    learner_class = controller_class or BehaviorCloningController
    learner = learner_class(model_path)
    teacher = AssignmentController()
    output = Path(dataset_path)
    written = 0
    candidate = seed
    with output.open("a", encoding="utf-8") as handle:
        while episodes > 0:
            if seed_split(candidate) != "train":
                candidate += 1
                continue
            env = BeeEnv(config, seed=candidate)
            learner.reset(candidate + 200_000)
            teacher.reset(candidate + 100_000)
            while not env.done:
                observation = env.observe()
                labels = teacher.act(observation)
                for bee in observation["bees"]:
                    if not bee["alive"]:
                        continue
                    row = {
                        "seed": candidate,
                        "split": "train",
                        "bee_id": bee["id"],
                        "features": encoder(observation, bee["id"]),
                        "action": ACTION_INDEX[labels[bee["id"]]],
                    }
                    handle.write(json.dumps(row, separators=(",", ":")) + "\n")
                    written += 1
                env.step(learner.act(observation))
            episodes -= 1
            candidate += 1
    return written


def _torch():
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "PyTorch is required for ML commands; install requirements-ml.txt"
        ) from exc
    from .hardware import configure_torch

    configure_torch(torch)
    return torch


def _build_model(torch):
    return _build_sized_model(torch, FEATURE_SIZE)


def _build_sized_model(torch, feature_size: int):
    return torch.nn.Sequential(
        torch.nn.Linear(feature_size, 96),
        torch.nn.ReLU(),
        torch.nn.Linear(96, 96),
        torch.nn.ReLU(),
        torch.nn.Linear(96, len(ACTIONS)),
    )


def train_model(
    dataset_path: str | Path,
    model_path: str | Path,
    epochs: int = 8,
    batch_size: int = 512,
    learning_rate: float = 1e-3,
    seed: int = 0,
) -> dict:
    torch = _torch()
    from .hardware import hardware_snapshot, peak_memory_bytes, resolve_device, synchronize

    selected_device = resolve_device(torch)
    torch.manual_seed(seed)
    rows = [
        json.loads(line)
        for line in Path(dataset_path).read_text(encoding="utf-8").splitlines()
        if line
    ]
    grouped = {
        split: [row for row in rows if row["split"] == split]
        for split in ("train", "validation", "test")
    }
    if not all(grouped.values()):
        raise ValueError("dataset must contain train, validation and test episodes")
    feature_size = len(grouped["train"][0]["features"])
    model = _build_sized_model(torch, feature_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    action_counts = [0] * len(ACTIONS)
    for row in grouped["train"]:
        action_counts[row["action"]] += 1
    observed_counts = [count for count in action_counts if count]
    largest = max(observed_counts)
    class_weights = [
        (largest / count) ** 0.5 if count else 0.0
        for count in action_counts
    ]
    loss_fn = torch.nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights, dtype=torch.float32)
    )
    generator = random.Random(seed)

    synchronize(torch, selected_device)
    training_started = time.perf_counter()
    for _epoch in range(epochs):
        model.train()
        generator.shuffle(grouped["train"])
        for start in range(0, len(grouped["train"]), batch_size):
            batch = grouped["train"][start : start + batch_size]
            features = torch.tensor([row["features"] for row in batch], dtype=torch.float32)
            labels = torch.tensor([row["action"] for row in batch], dtype=torch.long)
            optimizer.zero_grad()
            loss = loss_fn(model(features), labels)
            loss.backward()
            optimizer.step()
    synchronize(torch, selected_device)
    training_seconds = time.perf_counter() - training_started

    def classification_metrics(split: str) -> tuple[float, dict[str, float]]:
        model.eval()
        correct = 0
        action_correct = [0] * len(ACTIONS)
        action_total = [0] * len(ACTIONS)
        with torch.no_grad():
            for start in range(0, len(grouped[split]), batch_size):
                batch = grouped[split][start : start + batch_size]
                features = torch.tensor([row["features"] for row in batch], dtype=torch.float32)
                labels = torch.tensor([row["action"] for row in batch], dtype=torch.long)
                predictions = model(features).argmax(dim=1)
                correct += int((predictions == labels).sum())
                for prediction, label in zip(predictions.tolist(), labels.tolist()):
                    action_total[label] += 1
                    action_correct[label] += int(prediction == label)
        recalls = {
            action: action_correct[index] / action_total[index]
            for index, action in enumerate(ACTIONS)
            if action_total[index]
        }
        return correct / len(grouped[split]), recalls

    validation_accuracy, validation_recall = classification_metrics("validation")
    test_accuracy, test_recall = classification_metrics("test")

    metrics = {
        "train_examples": len(grouped["train"]),
        "validation_examples": len(grouped["validation"]),
        "test_examples": len(grouped["test"]),
        "validation_accuracy": validation_accuracy,
        "test_accuracy": test_accuracy,
        "validation_recall": validation_recall,
        "test_recall": test_recall,
        "training_seconds": training_seconds,
        "training_examples_per_second": (
            len(grouped["train"]) * epochs / training_seconds
            if training_seconds
            else None
        ),
        "peak_device_memory_bytes": peak_memory_bytes(torch, selected_device),
        "hardware": hardware_snapshot(selected_device),
    }
    output = Path(model_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "feature_size": feature_size,
            "metrics": metrics,
        },
        output,
    )
    return metrics


class BehaviorCloningController:
    name = "behavior-cloning"

    def __init__(self, model_path: str | Path) -> None:
        self.torch = _torch()
        checkpoint = self.torch.load(model_path, map_location="cpu", weights_only=True)
        self.model = _build_sized_model(
            self.torch, checkpoint.get("feature_size", FEATURE_SIZE)
        )
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()

    def reset(self, seed: int) -> None:
        pass

    def act(self, observation: dict) -> dict[int, str]:
        living = [bee for bee in observation["bees"] if bee["alive"]]
        if not living:
            return {}
        features = self.torch.tensor(
            [encode_bee(observation, bee["id"]) for bee in living],
            dtype=self.torch.float32,
        )
        with self.torch.no_grad():
            logits = self.model(features)
        actions = {}
        for index, bee in enumerate(living):
            mask = valid_action_mask(observation, bee["id"])
            scores = logits[index].tolist()
            action_index = max(
                (candidate for candidate, valid in enumerate(mask) if valid),
                key=lambda candidate: scores[candidate],
            )
            actions[bee["id"]] = ACTIONS[action_index]
        return actions


class LocalBehaviorCloningController(BehaviorCloningController):
    name = "local-behavior-cloning"

    def act(self, observation: dict) -> dict[int, str]:
        living = [bee for bee in observation["bees"] if bee["alive"]]
        if not living:
            return {}
        features = self.torch.tensor(
            [encode_local_bee(observation, bee["id"]) for bee in living],
            dtype=self.torch.float32,
        )
        with self.torch.no_grad():
            logits = self.model(features)
        actions = {}
        for index, bee in enumerate(living):
            mask = valid_action_mask(observation, bee["id"])
            scores = logits[index].tolist()
            action_index = max(
                (candidate for candidate, valid in enumerate(mask) if valid),
                key=lambda candidate: scores[candidate],
            )
            actions[bee["id"]] = ACTIONS[action_index]
        return actions
