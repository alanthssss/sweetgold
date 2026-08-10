"""Decentralized execution with local harvest-intent reservations."""

from __future__ import annotations

from pathlib import Path

from .ctde import CTDEController
from .env import ACTIONS
from .ml import encode_local_bee, valid_action_mask


def local_reservations(
    bee_ids: list[int], supply: int, priority_offset: int, bee_count: int
) -> tuple[list[int], list[int]]:
    """Grant a scarce local resource fairly without a central assignment."""
    ordered = sorted(
        bee_ids,
        key=lambda bee_id: ((bee_id - priority_offset) % bee_count, bee_id),
    )
    grants = max(0, min(supply, len(ordered)))
    return ordered[:grants], ordered[grants:]


class CoordinatedCTDEController(CTDEController):
    """CTDE actor with a local, deterministic resource reservation protocol.

    Bees still choose from radius-four observations. Before execution they
    broadcast harvest intents only to peers occupying the same flower. A
    rotating local priority grants at most the observed nectar supply and
    denied bees take their next-best valid action.
    """

    name = "coordinated-ctde"

    def __init__(self, model_path: str | Path) -> None:
        super().__init__(model_path)
        self.reset(0)

    def reset(self, seed: int) -> None:
        self._seed = seed
        self._tick = 0
        self._harvest_intents = 0
        self._contested_intents = 0
        self._reservation_grants = 0
        self._prevented_conflicts = 0
        self._unresolved_conflicts = 0

    def act(self, observation: dict) -> dict[int, str]:
        living = [bee for bee in observation["bees"] if bee["alive"]]
        if not living:
            return {}
        features = self.torch.tensor(
            [encode_local_bee(observation, bee["id"]) for bee in living],
            dtype=self.torch.float32,
            device=self.device,
        )
        with self.torch.no_grad():
            scores = self.model(features).tolist()
        masks = {
            bee["id"]: valid_action_mask(observation, bee["id"])
            for bee in living
        }
        preferred = {
            bee["id"]: self._best(scores[index], masks[bee["id"]])
            for index, bee in enumerate(living)
        }
        by_position: dict[tuple[int, int], list[int]] = {}
        for bee in living:
            if ACTIONS[preferred[bee["id"]]] == "harvest":
                by_position.setdefault((bee["row"], bee["col"]), []).append(bee["id"])

        self._harvest_intents += sum(len(ids) for ids in by_position.values())
        denied: set[int] = set()
        bee_count = max(1, observation["config"]["bees"])
        priority_offset = (self._seed + observation["tick"]) % bee_count
        flower_supply = {
            (flower["row"], flower["col"]): flower["nectar"]
            for flower in observation["flowers"]
        }
        for position, bee_ids in by_position.items():
            supply = flower_supply.get(position, 0)
            granted, rejected = local_reservations(
                bee_ids, supply, priority_offset, bee_count
            )
            self._reservation_grants += len(granted)
            if rejected:
                self._contested_intents += len(bee_ids)
                denied.update(rejected)
                self._prevented_conflicts += len(rejected)

        actions = {}
        for index, bee in enumerate(living):
            bee_id = bee["id"]
            mask = list(masks[bee_id])
            if bee_id in denied:
                mask[ACTIONS.index("harvest")] = False
            actions[bee_id] = ACTIONS[self._best(scores[index], mask)]
        self._tick += 1
        return actions

    @staticmethod
    def _best(scores: list[float], mask: list[bool]) -> int:
        return max(
            (candidate for candidate, valid in enumerate(mask) if valid),
            key=lambda candidate: scores[candidate],
        )

    def episode_metrics(self) -> dict:
        return {
            "harvest_intents": self._harvest_intents,
            "contested_intents": self._contested_intents,
            "reservation_grants": self._reservation_grants,
            "prevented_conflicts": self._prevented_conflicts,
            "unresolved_conflicts": self._unresolved_conflicts,
            "contention_rate": (
                self._contested_intents / max(1, self._harvest_intents)
            ),
            "reservation_success_rate": (
                self._reservation_grants / max(1, self._harvest_intents)
            ),
            "unresolved_contention_rate": (
                self._unresolved_conflicts / max(1, self._harvest_intents)
            ),
        }
