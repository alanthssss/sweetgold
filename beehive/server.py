"""HTTP game server for BeeSim."""

from __future__ import annotations

import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .controllers import CONTROLLERS
from .env import BeeEnv, EnvConfig


class GameSession:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.env = BeeEnv()
        self.controller_name = "scout"
        self.controller = CONTROLLERS[self.controller_name]()
        self.controller.reset(100_000)

    def reset(self, seed: int = 0, controller: str = "scout", config: dict | None = None) -> dict:
        with self.lock:
            self.controller_name = controller if controller in CONTROLLERS else "scout"
            self.controller = CONTROLLERS[self.controller_name]()
            self.controller.reset(seed + 100_000)
            self.env = BeeEnv(EnvConfig(**(config or {})), seed=seed)
            return self.state()

    def step(self, actions: dict | None = None) -> dict:
        with self.lock:
            if self.env.done:
                return self.state()
            if actions is None:
                actions = self.controller.act(self.env.observe())
            else:
                actions = {int(key): value for key, value in actions.items()}
            self.env.step(actions)
            return self.state()

    def state(self) -> dict:
        state = self.env.observe()
        targets = getattr(self.controller, "targets", {})
        for bee in state["bees"]:
            target = targets.get(bee["id"])
            bee["target"] = list(target) if target else None
        state["controller"] = self.controller_name
        return state


def serve(port: int = 8080) -> None:
    web_root = Path(__file__).resolve().parent.parent / "web"
    session = GameSession()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/api/state":
                self._json(200, session.state())
                return
            relative = "index.html" if self.path == "/" else self.path.lstrip("/")
            path = (web_root / relative).resolve()
            if web_root.resolve() not in path.parents or not path.is_file():
                self.send_error(404)
                return
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                if self.path == "/api/reset":
                    state = session.reset(
                        seed=int(payload.get("seed", 0)),
                        controller=str(payload.get("controller", "scout")),
                        config=payload.get("config"),
                    )
                elif self.path == "/api/step":
                    state = session.step(payload.get("actions"))
                else:
                    self._json(404, {"error": "not found"})
                    return
                self._json(200, state)
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
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
    print(f"BeeSim running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
