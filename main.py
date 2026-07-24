"""Command-line entry point for BeeSim and BeeBench."""

from __future__ import annotations

import argparse
import json

from beehive.controllers import CONTROLLERS
from beehive.env import EnvConfig
from beehive.evaluator import evaluate
from beehive.report import write_report
from beehive.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(prog="sweetgold")
    sub = parser.add_subparsers(dest="command", required=True)
    play = sub.add_parser("play", help="start the interactive BeeSim game")
    play.add_argument("--port", type=int, default=8080)
    bench = sub.add_parser("benchmark", help="run matched-seed BeeBench evaluation")
    bench.add_argument("--episodes", type=int, default=30)
    bench.add_argument("--seed", type=int, default=20260724)
    bench.add_argument("--controllers", nargs="+", choices=CONTROLLERS, default=list(CONTROLLERS))
    bench.add_argument("--report", default="report")
    bench.add_argument("--ticks", type=int, default=240)
    args = parser.parse_args()

    if args.command == "play":
        serve(args.port)
        return

    config = EnvConfig(season_ticks=args.ticks)
    seeds = [args.seed + i for i in range(args.episodes)]
    results = [
        evaluate(CONTROLLERS[name](), config, seeds)
        for name in args.controllers
    ]
    path = write_report(results, args.report)
    summary = [
        {key: value for key, value in result.items() if key != "raw"}
        for result in sorted(results, key=lambda x: x["mean_honey"], reverse=True)
    ]
    print(json.dumps(summary, indent=2))
    print(f"\nReport: {path.resolve()}")


if __name__ == "__main__":
    main()
