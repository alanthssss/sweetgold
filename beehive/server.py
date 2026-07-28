"""HTTP server for the BeeSim strategy arena."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .controllers import CONTROLLERS
from .env import BeeEnv, EnvConfig
from .model_store import ModelStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_BLOB_URL = "https://github.com/alanthssss/sweetgold/blob/main"
STRATEGY_DESCRIPTIONS = {
    "random": "Uncoordinated random-action control.",
    "greedy": "Each bee pursues its nearest visible flower.",
    "scout": "Rule-based scouts broadcast flower signals.",
    "assignment": "Central controller reserves distinct flower targets.",
    "bc-ppo": "Behavior-cloned actor fine-tuned with PPO.",
    "coordinated-ctde": "Local CTDE actor with harvest-intent reservations.",
    "curriculum-coordinated-ctde": "Robust CTDE actor trained across environment shifts.",
    "interleaved-coordinated-ctde": "CTDE actor trained on balanced interleaved environments.",
}
STRATEGY_DESCRIPTIONS_ZH = {
    "bc-ppo": "从规则示范进行行为克隆，并通过 PPO 微调的策略。",
    "coordinated-ctde": "带有本地采集意图预约机制的 CTDE 策略。",
    "curriculum-coordinated-ctde": "跨环境变化进行课程训练的鲁棒性 CTDE 策略。",
    "interleaved-coordinated-ctde": "在均衡交错环境中训练的 CTDE 策略。",
}


class StrategyCatalog:
    """Discover rule strategies and load accepted registry checkpoints."""

    def __init__(
        self,
        registry_path: str | Path = PROJECT_ROOT / "registry" / "models.json",
        audit_path: str | Path | None = None,
    ) -> None:
        self.registry_path = Path(registry_path)
        self.audit_path = (
            Path(audit_path)
            if audit_path is not None
            else self.registry_path.with_name("audits.json")
        )

    def entries(self) -> list[dict]:
        entries = [
            {
                "id": name,
                "label": name.replace("-", " ").title(),
                "kind": "rule",
                "available": True,
                "description": STRATEGY_DESCRIPTIONS[name],
            }
            for name in ("assignment", "scout", "greedy", "random")
        ]
        latest = {}
        for record in self._registry().get("models", []):
            model = record.get("model")
            if model in (
                "bc-ppo",
                "coordinated-ctde",
                "curriculum-coordinated-ctde",
                "interleaved-coordinated-ctde",
            ):
                latest[model] = record
        audits = {}
        for audit in self._audits().get("audits", []):
            audits[audit.get("candidate")] = audit
        for model, record in latest.items():
            artifact = self._artifact(record)
            local_status = (
                "missing"
                if not artifact.is_file()
                else (
                    "verified"
                    if self._sha_matches(artifact, record.get("sha256"))
                    else "corrupt"
                )
            )
            available = local_status == "verified"
            download = record.get("download", {})
            latest_audit = audits.get(model)
            audit_summary = latest_audit.get("summary", {}) if latest_audit else None
            entries.append(
                {
                    "id": model,
                    "label": model.replace("-", " ").upper(),
                    "kind": "learned",
                    "available": available,
                    "description": STRATEGY_DESCRIPTIONS[model],
                    "description_zh": STRATEGY_DESCRIPTIONS_ZH[model],
                    "mean_honey": record.get("mean_honey"),
                    "run": record.get("run"),
                    "integrity": local_status,
                    "promotion": record.get("promotion", {}).get("status"),
                    "promotion_checks": record.get("promotion", {}).get("checks", {}),
                    "license": download.get("license"),
                    "download_url": download.get("url"),
                    "size_bytes": download.get("size_bytes"),
                    "model_card": download.get("model_card"),
                    "model_card_url": (
                        f"{REPOSITORY_BLOB_URL}/{download['model_card']}"
                        if download.get("model_card")
                        else None
                    ),
                    "latest_audit": (
                        {
                            "status": latest_audit.get("status"),
                            "run": latest_audit.get("run"),
                            "worst_honey_scenario": audit_summary.get(
                                "worst_honey_scenario"
                            ),
                            "worst_honey_ratio": audit_summary.get(
                                "worst_honey_ratio"
                            ),
                            "minimum_bee_survival": audit_summary.get(
                                "minimum_bee_survival"
                            ),
                        }
                        if latest_audit
                        else None
                    ),
                }
            )
        return entries

    def create(self, strategy_id: str):
        if strategy_id in CONTROLLERS:
            return CONTROLLERS[strategy_id]()
        record = next(
            (
                row
                for row in reversed(self._registry().get("models", []))
                if row.get("model") == strategy_id
            ),
            None,
        )
        if not record:
            raise ValueError(f"unknown strategy: {strategy_id}")
        artifact = self._artifact(record)
        if not artifact.is_file():
            raise ValueError(
                f"checkpoint unavailable for {strategy_id}: {artifact}"
            )
        if not self._sha_matches(artifact, record.get("sha256")):
            raise ValueError(f"checkpoint integrity check failed for {strategy_id}")
        if strategy_id == "bc-ppo":
            from .ppo import PPOController

            return PPOController(artifact)
        if strategy_id in (
            "coordinated-ctde",
            "curriculum-coordinated-ctde",
            "interleaved-coordinated-ctde",
        ):
            from .coordination import CoordinatedCTDEController

            return CoordinatedCTDEController(artifact)
        raise ValueError(f"unsupported registered strategy: {strategy_id}")

    def _registry(self) -> dict:
        if not self.registry_path.is_file():
            return {"models": []}
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def _audits(self) -> dict:
        if not self.audit_path.is_file():
            return {"audits": []}
        return json.loads(self.audit_path.read_text(encoding="utf-8"))

    @staticmethod
    def _artifact(record: dict) -> Path:
        path = Path(record.get("artifact", ""))
        return path if path.is_absolute() else PROJECT_ROOT / path

    @staticmethod
    def _sha_matches(path: Path, expected: str | None) -> bool:
        return bool(
            expected
            and hashlib.sha256(path.read_bytes()).hexdigest() == expected
        )


class ArenaLane:
    def __init__(self, strategy: str, controller, config: EnvConfig, seed: int):
        self.strategy = strategy
        self.controller = controller
        self.controller.reset(seed + 100_000)
        self.env = BeeEnv(config, seed=seed)

    def step(self) -> None:
        if not self.env.done:
            self.env.step(self.controller.act(self.env.observe()))

    def state(self) -> dict:
        state = self.env.observe()
        targets = getattr(self.controller, "targets", {})
        for bee in state["bees"]:
            target = targets.get(bee["id"])
            bee["target"] = list(target) if target else None
        state["controller"] = self.strategy
        state["controller_metrics"] = (
            self.controller.episode_metrics()
            if hasattr(self.controller, "episode_metrics")
            else {}
        )
        return state


class ArenaSession:
    """Two matched-seed simulations with server-side replay history."""

    def __init__(self, catalog: StrategyCatalog | None = None) -> None:
        self.lock = threading.RLock()
        self.catalog = catalog or StrategyCatalog()
        self.seed = 42
        self.config = EnvConfig()
        self.left: ArenaLane
        self.right: ArenaLane
        self.history: list[dict] = []
        self._reset_unlocked(self.seed, "assignment", "greedy", {})

    def strategies(self) -> list[dict]:
        return self.catalog.entries()

    def reset(
        self,
        seed: int = 42,
        left: str = "assignment",
        right: str = "greedy",
        config: dict | None = None,
    ) -> dict:
        with self.lock:
            return self._reset_unlocked(seed, left, right, config or {})

    def _reset_unlocked(
        self, seed: int, left: str, right: str, config: dict
    ) -> dict:
        self.seed = seed
        self.config = EnvConfig(**config)
        self.config.validate()
        self.left = ArenaLane(left, self.catalog.create(left), self.config, seed)
        self.right = ArenaLane(right, self.catalog.create(right), self.config, seed)
        self.history = []
        return self._record()

    def step(self) -> dict:
        with self.lock:
            if not self.left.env.done or not self.right.env.done:
                self.left.step()
                self.right.step()
                self._record()
            return self.summary()

    def frame(self, index: int) -> dict:
        with self.lock:
            if not self.history:
                raise ValueError("replay is empty")
            if index < 0:
                index = len(self.history) + index
            if not 0 <= index < len(self.history):
                raise ValueError("replay frame out of range")
            return {
                **self.history[index],
                "frame": index,
                "frames": len(self.history),
                "live": index == len(self.history) - 1,
            }

    def summary(self) -> dict:
        return self.frame(-1)

    def _record(self) -> dict:
        frame = {
            "seed": self.seed,
            "left": self.left.state(),
            "right": self.right.state(),
        }
        self.history.append(frame)
        return self.summary()


def serve(port: int = 8080) -> None:
    web_root = PROJECT_ROOT / "web"
    session = ArenaSession()
    model_store = ModelStore(session.catalog.registry_path)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in ("/api/state", "/api/arena"):
                self._json(200, session.summary())
                return
            if parsed.path == "/api/strategies":
                self._json(200, {"strategies": session.strategies()})
                return
            if parsed.path == "/api/frame":
                try:
                    index = int(parse_qs(parsed.query).get("index", ["-1"])[0])
                    self._json(200, session.frame(index))
                except (TypeError, ValueError) as exc:
                    self._json(400, {"error": str(exc)})
                return
            relative = "index.html" if parsed.path == "/" else parsed.path.lstrip("/")
            path = (web_root / relative).resolve()
            if web_root.resolve() not in path.parents or not path.is_file():
                self.send_error(404)
                return
            body = path.read_bytes()
            self.send_response(200)
            self.send_header(
                "Content-Type",
                mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            )
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                if self.path == "/api/reset":
                    state = session.reset(
                        seed=int(payload.get("seed", 42)),
                        left=str(payload.get("left", "assignment")),
                        right=str(payload.get("right", "greedy")),
                        config=payload.get("config"),
                    )
                elif self.path == "/api/step":
                    state = session.step()
                elif self.path == "/api/models/download":
                    model = str(payload.get("model", ""))
                    state = model_store.download(model)
                else:
                    self._json(404, {"error": "not found"})
                    return
                self._json(200, state)
            except (ValueError, TypeError, json.JSONDecodeError, OSError) as exc:
                self._json(400, {"error": str(exc)})

        def _json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"BeeSim Strategy Arena running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
