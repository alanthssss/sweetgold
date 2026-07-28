"""Hierarchical safety supervisor for the coordinated CTDE actor."""

from __future__ import annotations

import math
from pathlib import Path

from .coordination import CoordinatedCTDEController


class HierarchicalReturnCTDEController(CoordinatedCTDEController):
    """Use a high-level return/recharge mode above the learned local actor."""

    name = "hierarchical-return-ctde"

    def __init__(
        self,
        model_path: str | Path,
        safety_margin: int = 4,
        recharge_fraction: float = 0.75,
    ) -> None:
        if safety_margin < 0:
            raise ValueError("safety_margin must be non-negative")
        if not 0 < recharge_fraction <= 1:
            raise ValueError("recharge_fraction must be between zero and one")
        self.safety_margin = safety_margin
        self.recharge_fraction = recharge_fraction
        super().__init__(model_path)

    def reset(self, seed: int) -> None:
        super().reset(seed)
        self._returning: set[int] = set()
        self._return_entries = 0
        self._forced_moves = 0
        self._forced_deposits = 0
        self._forced_recharges = 0

    def act(self, observation: dict) -> dict[int, str]:
        actions = super().act(observation)
        hive_row, hive_col = observation["hive"]
        config = observation["config"]
        remaining = config["season_ticks"] - observation["tick"]
        expected_move_cost = 1.0 + config["rain_chance"]

        for bee in observation["bees"]:
            if not bee["alive"]:
                self._returning.discard(bee["id"])
                continue
            bee_id = bee["id"]
            distance = abs(bee["row"] - hive_row) + abs(bee["col"] - hive_col)
            required_energy = (
                math.ceil(distance * expected_move_cost) + self.safety_margin
            )
            full = bee["cargo"] >= config["max_cargo"]
            low_energy = distance > 0 and bee["energy"] <= required_energy
            closing = bee["cargo"] > 0 and remaining <= distance + 2
            if bee_id not in self._returning and (full or low_energy or closing):
                self._returning.add(bee_id)
                self._return_entries += 1

            if bee_id not in self._returning:
                continue
            if distance:
                actions[bee_id] = self._toward_hive(
                    bee["row"], bee["col"], hive_row, hive_col
                )
                self._forced_moves += 1
            elif bee["cargo"]:
                actions[bee_id] = "deposit"
                self._forced_deposits += 1
            elif bee["energy"] < math.ceil(
                config["max_energy"] * self.recharge_fraction
            ):
                actions[bee_id] = "rest"
                self._forced_recharges += 1
            else:
                self._returning.discard(bee_id)
        return actions

    @staticmethod
    def _toward_hive(row: int, col: int, hive_row: int, hive_col: int) -> str:
        if row < hive_row:
            return "down"
        if row > hive_row:
            return "up"
        if col < hive_col:
            return "right"
        return "left"

    def episode_metrics(self) -> dict:
        return {
            **super().episode_metrics(),
            "return_entries": self._return_entries,
            "forced_return_moves": self._forced_moves,
            "forced_deposits": self._forced_deposits,
            "forced_recharges": self._forced_recharges,
        }
