"""Controller baselines sharing one policy interface."""

from __future__ import annotations

import random
from typing import Protocol

from .env import ACTIONS


class Controller(Protocol):
    name: str

    def reset(self, seed: int) -> None: ...
    def act(self, observation: dict) -> dict[int, str]: ...


def _move_towards(source: tuple[int, int], target: tuple[int, int]) -> str:
    r, c = source
    tr, tc = target
    if abs(tr - r) >= abs(tc - c) and tr != r:
        return "down" if tr > r else "up"
    if tc != c:
        return "right" if tc > c else "left"
    return "rest"


class RandomController:
    name = "random"

    def __init__(self) -> None:
        self._rng = random.Random()

    def reset(self, seed: int) -> None:
        self._rng.seed(seed)

    def act(self, observation: dict) -> dict[int, str]:
        return {
            bee["id"]: self._rng.choice(ACTIONS)
            for bee in observation["bees"]
            if bee["alive"]
        }


class GreedyController:
    """Nearest-flower policy with energy-aware return to hive."""

    name = "greedy"

    def reset(self, seed: int) -> None:
        pass

    def act(self, observation: dict) -> dict[int, str]:
        hive = tuple(observation["hive"])
        flowers = [f for f in observation["flowers"] if f["nectar"] > 0]
        max_cargo = observation["config"]["max_cargo"]
        actions: dict[int, str] = {}
        for bee in observation["bees"]:
            if not bee["alive"]:
                continue
            pos = (bee["row"], bee["col"])
            distance_home = abs(pos[0] - hive[0]) + abs(pos[1] - hive[1])
            must_return = bee["cargo"] >= max_cargo or bee["energy"] <= distance_home + 3
            if pos == hive and bee["cargo"]:
                actions[bee["id"]] = "deposit"
            elif pos == hive and bee["energy"] < observation["config"]["max_energy"] // 2:
                actions[bee["id"]] = "rest"
            elif must_return:
                actions[bee["id"]] = _move_towards(pos, hive)
            else:
                here = next((f for f in flowers if (f["row"], f["col"]) == pos), None)
                if here and bee["cargo"] < max_cargo:
                    actions[bee["id"]] = "harvest"
                elif flowers:
                    target = min(
                        flowers,
                        key=lambda f: abs(f["row"] - pos[0]) + abs(f["col"] - pos[1]),
                    )
                    actions[bee["id"]] = _move_towards(pos, (target["row"], target["col"]))
                else:
                    actions[bee["id"]] = _move_towards(pos, hive)
        return actions


class ScoutController(GreedyController):
    """Role-based policy: scouts spread out; foragers use advertised flowers."""

    name = "scout"

    def __init__(self) -> None:
        self._rng = random.Random()

    def reset(self, seed: int) -> None:
        self._rng.seed(seed)

    def act(self, observation: dict) -> dict[int, str]:
        actions = super().act(observation)
        hive = tuple(observation["hive"])
        max_cargo = observation["config"]["max_cargo"]
        signals = observation["signals"]
        for bee in observation["bees"]:
            if not bee["alive"]:
                continue
            pos = (bee["row"], bee["col"])
            # Roughly one quarter of the colony explores while empty.
            is_scout = bee["id"] % 4 == 0
            distance_home = abs(pos[0] - hive[0]) + abs(pos[1] - hive[1])
            flower_here = next(
                (f for f in observation["flowers"] if (f["row"], f["col"]) == pos and f["nectar"]),
                None,
            )
            if flower_here and bee["cargo"] and bee["cargo"] < max_cargo and is_scout:
                actions[bee["id"]] = "signal"
            elif is_scout and bee["cargo"] == 0 and bee["energy"] > distance_home + 8:
                actions[bee["id"]] = self._rng.choice(("up", "down", "left", "right"))
            elif signals and bee["cargo"] == 0 and bee["energy"] > distance_home + 4:
                target = max(signals, key=lambda s: (s["value"], s["tick"]))
                actions[bee["id"]] = _move_towards(pos, (target["row"], target["col"]))
        return actions


CONTROLLERS = {
    "random": RandomController,
    "greedy": GreedyController,
    "scout": ScoutController,
}
