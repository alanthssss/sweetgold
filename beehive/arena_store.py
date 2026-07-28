"""Durable, local artifacts for matched-seed Arena tournaments."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = re.compile(r"arena-[0-9TZ-]+-[0-9a-f]{8}")


class ArenaArtifactStore:
    """Persist tournament requests and results as atomic JSON artifacts."""

    def __init__(self, root: str | Path = "runs/arena") -> None:
        self.root = Path(root)

    def save(
        self,
        request: dict,
        result: dict,
        created_at: datetime | None = None,
    ) -> dict:
        created = created_at or datetime.now(timezone.utc)
        timestamp = created.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        digest = hashlib.sha256(
            json.dumps(
                {"request": request, "result": result},
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()[:8]
        run_id = f"arena-{timestamp}-{digest}"
        document = {
            "schema_version": 1,
            "kind": "arena-tournament",
            "run_id": run_id,
            "created_at": created.astimezone(timezone.utc).isoformat(),
            "request": request,
            "result": result,
        }
        self.root.mkdir(parents=True, exist_ok=True)
        destination = self.root / f"{run_id}.json"
        temporary = self.root / f".{run_id}.{os.getpid()}.tmp"
        temporary.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, destination)
        return self.summary(document)

    def list(self, limit: int = 20) -> list[dict]:
        if not 1 <= limit <= 100:
            raise ValueError("artifact limit must be between 1 and 100")
        if not self.root.is_dir():
            return []
        documents = [self._read(path) for path in self.root.glob("arena-*.json")]
        documents.sort(key=lambda row: row["created_at"], reverse=True)
        return [self.summary(row) for row in documents[:limit]]

    def get(self, run_id: str) -> dict:
        if not RUN_ID.fullmatch(run_id):
            raise ValueError("invalid Arena artifact id")
        path = self.root / f"{run_id}.json"
        if not path.is_file():
            raise ValueError(f"Arena artifact not found: {run_id}")
        return self._read(path)

    @staticmethod
    def summary(document: dict) -> dict:
        result = document["result"]
        leader = result.get("leaderboard", [{}])[0]
        return {
            "run_id": document["run_id"],
            "created_at": document["created_at"],
            "strategies": document["request"]["strategies"],
            "seed": document["request"]["seed"],
            "episodes": document["request"]["episodes"],
            "winner": leader.get("strategy"),
        }

    @staticmethod
    def _read(path: Path) -> dict:
        document = json.loads(path.read_text(encoding="utf-8"))
        if (
            document.get("schema_version") != 1
            or document.get("kind") != "arena-tournament"
        ):
            raise ValueError(f"unsupported Arena artifact: {path.name}")
        return document
