"""Command-line entry point for BeeSim and BeeBench."""

from __future__ import annotations

import argparse
import json

from beehive import __version__
from beehive.controllers import CONTROLLERS
from beehive.env import EnvConfig
from beehive.evaluator import evaluate, paired_honey_comparison
from beehive.report import write_report
from beehive.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(prog="sweetgold")
    parser.add_argument(
        "--version", action="version", version=f"sweetgold {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    play = sub.add_parser("play", help="start the interactive BeeSim game")
    play.add_argument("--port", type=int, default=8080)
    bench = sub.add_parser("benchmark", help="run matched-seed BeeBench evaluation")
    bench.add_argument("--episodes", type=int, default=30)
    bench.add_argument("--seed", type=int, default=20260724)
    bench.add_argument("--controllers", nargs="+", choices=CONTROLLERS, default=list(CONTROLLERS))
    bench.add_argument("--report", default="report")
    bench.add_argument("--ticks", type=int, default=240)
    dataset = sub.add_parser("collect", help="collect Assignment behavior-cloning data")
    dataset.add_argument("--episodes", type=int, default=100)
    dataset.add_argument("--seed", type=int, default=20270000)
    dataset.add_argument("--output", default="data/assignment.jsonl")
    train = sub.add_parser("train-bc", help="train an optional PyTorch behavior clone")
    train.add_argument("--data", default="data/assignment.jsonl")
    train.add_argument("--model", default="models/behavior-cloning.pt")
    train.add_argument("--epochs", type=int, default=15)
    dagger = sub.add_parser("collect-dagger", help="label learner-visited states")
    dagger.add_argument("--data", default="data/assignment.jsonl")
    dagger.add_argument("--model", default="models/behavior-cloning.pt")
    dagger.add_argument("--episodes", type=int, default=50)
    dagger.add_argument("--seed", type=int, default=20271000)
    bc_bench = sub.add_parser("benchmark-bc", help="benchmark a trained behavior clone")
    bc_bench.add_argument("--model", default="models/behavior-cloning.pt")
    bc_bench.add_argument("--episodes", type=int, default=30)
    bc_bench.add_argument("--seed", type=int, default=20280009)
    bc_bench.add_argument("--report", default="report-bc")
    bc_bench.add_argument("--ticks", type=int, default=240)
    ppo = sub.add_parser("train-ppo", help="fine-tune behavior cloning with PPO")
    ppo.add_argument("--bc-model", default="models/behavior-cloning.pt")
    ppo.add_argument("--model", default="models/bc-ppo.pt")
    ppo.add_argument("--episodes", type=int, default=100)
    ppo.add_argument("--seed", type=int, default=20290000)
    ppo.add_argument("--random-init", action="store_true")
    ppo_bench = sub.add_parser("benchmark-ppo", help="benchmark BC and PPO checkpoints")
    ppo_bench.add_argument("--bc-model", default="models/behavior-cloning.pt")
    ppo_bench.add_argument("--ppo-model", default="models/bc-ppo.pt")
    ppo_bench.add_argument("--random-model")
    ppo_bench.add_argument("--episodes", type=int, default=100)
    ppo_bench.add_argument("--seed", type=int, default=20300009)
    ppo_bench.add_argument("--report", default="report-ppo")
    pipeline = sub.add_parser("pipeline", help="run a configured end-to-end ML experiment")
    pipeline.add_argument("--config", required=True)
    pipeline.add_argument("--output-root", default="runs")
    pipeline.add_argument("--force", action="store_true")
    m7 = sub.add_parser("pipeline-m7", help="run local-observation CTDE experiment")
    m7.add_argument("--config", required=True)
    m7.add_argument("--output-root", default="runs")
    m7.add_argument("--force", action="store_true")
    m8 = sub.add_parser("pipeline-m8", help="run decentralized coordination experiment")
    m8.add_argument("--config", required=True)
    m8.add_argument("--output-root", default="runs")
    m8.add_argument("--force", action="store_true")
    m10 = sub.add_parser("pipeline-m10", help="run generalization and robustness audit")
    m10.add_argument("--config", required=True)
    m10.add_argument("--output-root", default="runs")
    m10.add_argument("--force", action="store_true")
    m11 = sub.add_parser("pipeline-m11", help="run curriculum robustness training")
    m11.add_argument("--config", required=True)
    m11.add_argument("--output-root", default="runs")
    m11.add_argument("--force", action="store_true")
    m12 = sub.add_parser("pipeline-m12", help="run interleaved robustness training")
    m12.add_argument("--config", required=True)
    m12.add_argument("--output-root", default="runs")
    m12.add_argument("--force", action="store_true")
    models = sub.add_parser("models", help="manage registered model artifacts")
    model_commands = models.add_subparsers(dest="models_command", required=True)
    for command in ("list", "verify"):
        model_command = model_commands.add_parser(
            command, help=f"{command} registered models"
        )
        model_command.add_argument("names", nargs="*")
        model_command.add_argument("--registry", default="registry/models.json")
    model_download = model_commands.add_parser(
        "download", help="download and verify registered models"
    )
    model_download.add_argument("names", nargs="*")
    model_download.add_argument("--registry", default="registry/models.json")
    model_download.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.command == "play":
        serve(args.port)
        return
    if args.command == "collect":
        from beehive.ml import collect_dataset

        print(json.dumps(collect_dataset(args.output, args.episodes, args.seed), indent=2))
        return
    if args.command == "train-bc":
        from beehive.ml import train_model

        print(json.dumps(train_model(args.data, args.model, epochs=args.epochs), indent=2))
        return
    if args.command == "collect-dagger":
        from beehive.ml import collect_dagger

        written = collect_dagger(args.data, args.model, args.episodes, args.seed)
        print(json.dumps({"dagger_examples": written}, indent=2))
        return
    if args.command == "benchmark-bc":
        from beehive.ml import BehaviorCloningController

        config = EnvConfig(season_ticks=args.ticks)
        seeds = [
            candidate
            for candidate in range(args.seed, args.seed + args.episodes * 10)
            if candidate % 10 == 9
        ][: args.episodes]
        results = [
            evaluate(controller, config, seeds)
            for controller in (
                CONTROLLERS["assignment"](),
                CONTROLLERS["greedy"](),
                BehaviorCloningController(args.model),
            )
        ]
        path = write_report(results, args.report)
        print(
            json.dumps(
                [{k: v for k, v in row.items() if k != "raw"} for row in results],
                indent=2,
            )
        )
        print(f"\nReport: {path.resolve()}")
        return
    if args.command == "train-ppo":
        from beehive.ppo import train_ppo

        summary = train_ppo(
            None if args.random_init else args.bc_model,
            args.model,
            episodes=args.episodes,
            seed=args.seed,
        )
        print(json.dumps(summary, indent=2))
        return
    if args.command == "benchmark-ppo":
        from beehive.ml import BehaviorCloningController
        from beehive.ppo import PPOController, RandomPPOController

        config = EnvConfig()
        seeds = [
            candidate
            for candidate in range(args.seed, args.seed + args.episodes * 10)
            if candidate % 10 == 9
        ][: args.episodes]
        controllers = [
            CONTROLLERS["assignment"](),
            BehaviorCloningController(args.bc_model),
            PPOController(args.ppo_model),
        ]
        if args.random_model:
            controllers.append(RandomPPOController(args.random_model))
        results = [evaluate(controller, config, seeds) for controller in controllers]
        path = write_report(results, args.report)
        summaries = [{k: v for k, v in row.items() if k != "raw"} for row in results]
        comparisons = [
            paired_honey_comparison(result, results[1])
            for result in results[2:]
        ]
        print(
            json.dumps(
                {
                    "results": summaries,
                    "vs_behavior_cloning": comparisons,
                },
                indent=2,
            )
        )
        print(f"\nReport: {path.resolve()}")
        return
    if args.command == "pipeline":
        from beehive.pipeline import run_pipeline

        result = run_pipeline(args.config, args.output_root, force=args.force)
        print(json.dumps(result, indent=2))
        return
    if args.command == "pipeline-m7":
        from beehive.m7_pipeline import run_m7_pipeline

        result = run_m7_pipeline(args.config, args.output_root, force=args.force)
        print(json.dumps(result, indent=2))
        return
    if args.command == "pipeline-m8":
        from beehive.m8_pipeline import run_m8_pipeline

        result = run_m8_pipeline(args.config, args.output_root, force=args.force)
        print(json.dumps(result, indent=2))
        return
    if args.command == "pipeline-m10":
        from beehive.m10_pipeline import run_m10_pipeline

        result = run_m10_pipeline(args.config, args.output_root, force=args.force)
        print(json.dumps(result, indent=2))
        return
    if args.command == "pipeline-m11":
        from beehive.m11_pipeline import run_m11_pipeline

        result = run_m11_pipeline(args.config, args.output_root, force=args.force)
        print(json.dumps(result, indent=2))
        return
    if args.command == "pipeline-m12":
        from beehive.m12_pipeline import run_m12_pipeline

        result = run_m12_pipeline(args.config, args.output_root, force=args.force)
        print(json.dumps(result, indent=2))
        return
    if args.command == "models":
        from beehive.model_store import ModelStore

        store = ModelStore(args.registry)
        names = args.names or store.names()
        if args.models_command == "download":
            result = [store.download(name, force=args.force) for name in names]
        else:
            result = [store.verify(name) for name in names]
        print(json.dumps(result, indent=2))
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
