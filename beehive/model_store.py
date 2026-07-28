"""Download and verify promoted SweetGold model artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = PROJECT_ROOT / "registry" / "models.json"


class ModelStore:
    """Resolve the model registry into safe, integrity-checked local artifacts."""

    def __init__(
        self,
        registry_path: str | Path = DEFAULT_REGISTRY,
        project_root: str | Path = PROJECT_ROOT,
    ) -> None:
        self.registry_path = Path(registry_path)
        self.project_root = Path(project_root).resolve()

    def records(self) -> list[dict]:
        registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        latest = {}
        for record in registry.get("models", []):
            latest[record["model"]] = record
        return list(latest.values())

    def names(self) -> list[str]:
        return [record["model"] for record in self.records()]

    def describe(self, name: str) -> dict:
        record = self._record(name)
        artifact = self._artifact(record)
        state = self._state(artifact, record["sha256"])
        download = record.get("download", {})
        return {
            "model": name,
            "status": state,
            "artifact": str(artifact.relative_to(self.project_root)),
            "sha256": record["sha256"],
            "size_bytes": download.get("size_bytes"),
            "url": download.get("url"),
            "license": download.get("license"),
            "model_card": download.get("model_card"),
            "mean_honey": record.get("mean_honey"),
        }

    def verify(self, name: str) -> dict:
        return self.describe(name)

    def download(
        self,
        name: str,
        force: bool = False,
        opener=urlopen,
    ) -> dict:
        record = self._record(name)
        target = self._artifact(record)
        before = self._state(target, record["sha256"])
        if before == "verified" and not force:
            result = self.describe(name)
            result["downloaded"] = False
            return result

        metadata = record.get("download", {})
        url = metadata.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise ValueError(f"model {name} has no trusted HTTPS download URL")
        expected_size = metadata.get("size_bytes")
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=f".{target.name}.",
                suffix=".download",
                dir=target.parent,
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                digest = hashlib.sha256()
                size = 0
                with opener(url, timeout=30) as response:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        temporary.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
            if expected_size is not None and size != expected_size:
                raise ValueError(
                    f"model {name} size mismatch: expected {expected_size}, got {size}"
                )
            if digest.hexdigest() != record["sha256"]:
                raise ValueError(f"model {name} SHA-256 verification failed")
            os.replace(temporary_path, target)
        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise

        result = self.describe(name)
        result["downloaded"] = True
        return result

    def _record(self, name: str) -> dict:
        for record in reversed(self.records()):
            if record.get("model") == name:
                return record
        raise ValueError(f"unknown registered model: {name}")

    def _artifact(self, record: dict) -> Path:
        relative = Path(record.get("artifact", ""))
        if relative.is_absolute():
            raise ValueError("registered artifact paths must be relative")
        artifact = (self.project_root / relative).resolve()
        try:
            artifact.relative_to(self.project_root)
        except ValueError as error:
            raise ValueError("registered artifact escapes the project root") from error
        return artifact

    @staticmethod
    def _state(path: Path, expected_sha256: str) -> str:
        if not path.is_file():
            return "missing"
        digest = hashlib.sha256()
        with path.open("rb") as artifact:
            while True:
                chunk = artifact.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        digest = digest.hexdigest()
        return "verified" if digest == expected_sha256 else "corrupt"
