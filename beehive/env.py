"""Seeded array-based bee ecosystem.

The environment is dependency-free and intentionally small. It is suitable
for a web game, algorithm benchmarks, and later Gymnasium/RL adapters.
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from typing import Mapping


ACTIONS = ("up", "down", "left", "right", "harvest", "deposit", "rest", "signal")
MOVES = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}


@dataclass(frozen=True)
class EnvConfig:
    width: int = 14
    height: int = 10
    bees: int = 8
    flowers: int = 14
    season_ticks: int = 240
    max_energy: int = 30
    max_cargo: int = 5
    flower_capacity: int = 12
    flower_regen_chance: float = 0.08
    rain_chance: float = 0.08

    def validate(self) -> None:
        if self.width < 5 or self.height < 5:
            raise ValueError("world must be at least 5×5")
        if self.bees < 1 or self.flowers < 1 or self.season_ticks < 1:
            raise ValueError("bees, flowers and season_ticks must be positive")
        if self.flowers >= self.width * self.height:
            raise ValueError("too many flowers for the world")


@dataclass
class Bee:
    id: int
    row: int
    col: int
    energy: int
    cargo: int = 0
    alive: bool = True
    role: str = "forager"
    target: tuple[int, int] | None = None


@dataclass
class Flower:
    row: int
    col: int
    nectar: int


class BeeEnv:
    """Multi-agent cooperative environment with a global team objective."""

    def __init__(self, config: EnvConfig | None = None, seed: int = 0) -> None:
        self.config = config or EnvConfig()
        self.config.validate()
        self.seed = seed
        self._rng = random.Random(seed)
        self.hive = (self.config.height // 2, self.config.width // 2)
        self.tick = 0
        self.stored_honey = 0
        self.total_energy_spent = 0
        self.invalid_actions = 0
        self.signals: list[dict] = []
        self.visited: set[tuple[int, int]] = set()
        self.weather = "clear"
        self.bees: list[Bee] = []
        self.flowers: list[Flower] = []
        self.reset(seed)

    def reset(self, seed: int | None = None) -> dict:
        if seed is not None:
            self.seed = seed
        self._rng = random.Random(self.seed)
        self.tick = 0
        self.stored_honey = 0
        self.total_energy_spent = 0
        self.invalid_actions = 0
        self.signals = []
        self.visited = {self.hive}
        self.weather = "clear"
        hr, hc = self.hive
        self.bees = [
            Bee(id=i, row=hr, col=hc, energy=self.config.max_energy)
            for i in range(self.config.bees)
        ]
        occupied = {self.hive}
        self.flowers = []
        while len(self.flowers) < self.config.flowers:
            cell = (
                self._rng.randrange(self.config.height),
                self._rng.randrange(self.config.width),
            )
            if cell in occupied:
                continue
            occupied.add(cell)
            self.flowers.append(
                Flower(*cell, nectar=self._rng.randint(5, self.config.flower_capacity))
            )
        return self.observe()

    @property
    def done(self) -> bool:
        return self.tick >= self.config.season_ticks or not any(b.alive for b in self.bees)

    def observe(self) -> dict:
        """Return a stable JSON-compatible global observation."""
        return {
            "seed": self.seed,
            "tick": self.tick,
            "done": self.done,
            "weather": self.weather,
            "hive": list(self.hive),
            "stored_honey": self.stored_honey,
            "config": asdict(self.config),
            "bees": [
                {
                    **asdict(bee),
                    "target": list(bee.target) if bee.target else None,
                }
                for bee in self.bees
            ],
            "flowers": [asdict(flower) for flower in self.flowers],
            "signals": self.signals[-12:],
            "metrics": self.metrics(),
        }

    def metrics(self) -> dict:
        alive = sum(bee.alive for bee in self.bees)
        return {
            "honey": self.stored_honey,
            "alive": alive,
            "deaths": self.config.bees - alive,
            "coverage": len(self.visited) / (self.config.width * self.config.height),
            "energy_spent": self.total_energy_spent,
            "efficiency": self.stored_honey / max(1, self.total_energy_spent),
            "invalid_actions": self.invalid_actions,
        }

    def step(self, actions: Mapping[int, str]) -> tuple[dict, float, bool, dict]:
        if self.done:
            raise RuntimeError("episode is complete; call reset()")
        before = self.stored_honey
        self.signals = [s for s in self.signals if self.tick - s["tick"] <= 20]
        self.weather = "rain" if self._rng.random() < self.config.rain_chance else "clear"

        for bee in self.bees:
            if not bee.alive:
                continue
            action = actions.get(bee.id, "rest")
            if action not in ACTIONS:
                action = "rest"
                self.invalid_actions += 1
            self._apply(bee, action)

        for flower in self.flowers:
            if (
                flower.nectar < self.config.flower_capacity
                and self._rng.random() < self.config.flower_regen_chance
            ):
                flower.nectar += 1
        self.tick += 1
        reward = float(self.stored_honey - before)
        if self.done and not any(bee.alive for bee in self.bees):
            reward -= 5.0
        return self.observe(), reward, self.done, self.metrics()

    def _apply(self, bee: Bee, action: str) -> None:
        energy_cost = 0
        if action in MOVES:
            dr, dc = MOVES[action]
            nr, nc = bee.row + dr, bee.col + dc
            if 0 <= nr < self.config.height and 0 <= nc < self.config.width:
                bee.row, bee.col = nr, nc
                energy_cost = 2 if self.weather == "rain" else 1
                self.visited.add((nr, nc))
            else:
                self.invalid_actions += 1
        elif action == "harvest":
            flower = self._flower_at(bee.row, bee.col)
            if flower and flower.nectar and bee.cargo < self.config.max_cargo:
                flower.nectar -= 1
                bee.cargo += 1
                energy_cost = 1
            else:
                self.invalid_actions += 1
        elif action == "deposit":
            if (bee.row, bee.col) == self.hive and bee.cargo:
                self.stored_honey += bee.cargo
                bee.cargo = 0
            else:
                self.invalid_actions += 1
        elif action == "rest":
            if (bee.row, bee.col) == self.hive:
                bee.energy = min(self.config.max_energy, bee.energy + 4)
        elif action == "signal":
            flower = self._flower_at(bee.row, bee.col)
            if flower and flower.nectar:
                self.signals.append(
                    {"row": flower.row, "col": flower.col, "value": flower.nectar, "tick": self.tick}
                )
                energy_cost = 1
            else:
                self.invalid_actions += 1

        bee.energy -= energy_cost
        self.total_energy_spent += energy_cost
        if bee.energy <= 0:
            bee.energy = 0
            bee.alive = False

    def _flower_at(self, row: int, col: int) -> Flower | None:
        return next((f for f in self.flowers if (f.row, f.col) == (row, col)), None)
