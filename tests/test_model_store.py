from __future__ import annotations

import hashlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from beehive.model_store import ModelStore


class ModelStoreTests(unittest.TestCase):
    def _store(self, root: Path, payload: bytes = b"checkpoint") -> ModelStore:
        registry = root / "registry.json"
        registry.write_text(
            json.dumps(
                {
                    "models": [
                        {
                            "model": "test-model",
                            "artifact": "runs/test/model.pt",
                            "sha256": hashlib.sha256(payload).hexdigest(),
                            "download": {
                                "url": "https://example.invalid/model.pt",
                                "size_bytes": len(payload),
                                "license": "Apache-2.0",
                                "model_card": "docs/models/test.md",
                            },
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return ModelStore(registry, project_root=root)

    def test_download_is_atomic_and_verified(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"checkpoint"
            store = self._store(root, payload)

            def opener(_url, timeout):
                self.assertEqual(timeout, 30)
                return io.BytesIO(payload)

            result = store.download("test-model", opener=opener)
            self.assertTrue(result["downloaded"])
            self.assertEqual(result["status"], "verified")
            self.assertEqual(
                (root / "runs/test/model.pt").read_bytes(), payload
            )
            second = store.download("test-model", opener=opener)
            self.assertFalse(second["downloaded"])

    def test_bad_digest_is_rejected_without_installing_file(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = self._store(root)

            def opener(_url, timeout):
                return io.BytesIO(b"tamperxxxx")

            with self.assertRaisesRegex(ValueError, "SHA-256"):
                store.download("test-model", opener=opener)
            self.assertFalse((root / "runs/test/model.pt").exists())

    def test_artifact_cannot_escape_project_root(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            store = self._store(root)
            registry = json.loads(store.registry_path.read_text())
            registry["models"][0]["artifact"] = "../escape.pt"
            store.registry_path.write_text(json.dumps(registry), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes"):
                store.verify("test-model")


if __name__ == "__main__":
    unittest.main()
