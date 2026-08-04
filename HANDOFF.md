# SweetGold handoff

[English](HANDOFF.md) | [简体中文](HANDOFF.zh-CN.md)

## Current status

M14 is the latest promoted policy; M15 is the latest completed product
workflow. The first M15 slice is on `main`, not pending work. New feature
development is paused while the project focuses on maintenance, bilingual
documentation, promotion, and release presentation.

## Milestones and formal decisions

| Milestone | Delivered work | Decision and evidence |
| --- | --- | --- |
| M2 | Centralized Assignment reservations, survival and invalid-action metrics, 100-seed report | 161.23 honey, 94.25% bee survival, 0% invalid actions; deterministic baseline established. |
| M3 | Two-bee early-season reserve and full late-season fleet | About 10% better efficiency for about 2.9% less honey; accepted as the best tested balance. |
| M4 | BC, class weighting, seed isolation, and one DAgger iteration | 136.10 honey on 30 test seeds, 97.0% of teacher; a second DAgger iteration was rejected after online regression. |
| M5 | BC-initialized PPO, GAE, clipped updates, critic, validation selection | +8.19 honey over BC on 100 test seeds, 95% CI [+3.69, +12.69]; random initialization produced zero honey. |
| M6 | One-command pipeline, leakage checks, run bundles, gated promotion, CI | Final tests never select checkpoints; registry writes require confidence, quality, and safety gates. |
| M7 | Radius-four local observation, global training critic, four-worker CTDE | +6.60 honey over local BC, but 1.056% invalid actions exceeded the 1% gate; rejected. |
| M8 | Local harvest-intent broadcasts and rotating-priority reservations | +6.19 honey, 13.51 conflicts prevented, zero invalid and unresolved actions; passed and registered. |
| M9 | Two-strategy Arena, identical worlds, live metrics, server-side replay | Learned dependencies remain optional; digest failures disable models without breaking rule strategies. |
| M10 | Six-scenario cross-distribution audit | Scarce-nectar yield 74.68%, large-map survival 50.25%, harsh-weather survival 7.75%; failed. |
| M11 | Five-stage sequential curriculum and multi-scenario selection | Final harsh-weather survival 6.5%, worst yield 69.85%; failed and recorded. |
| M12 | Balanced interleaved training and five gated cycles | Large-map survival 86.25%, harsh-weather 27.75%, scarce-nectar yield 73.65%; still failed. |
| M13 | Immutable model URLs, sizes, SHA-256, licenses, and model cards | `models list/download/verify` distributes promoted checkpoints without retraining. |
| M14 | Return, deposit, and recharge supervisor above the M8 actor | Six scenarios × 50 fresh seeds: 100% survival, 0% invalid actions, median honey 148.47%, worst 101.16%; all gates passed. |
| M15 | Arena league + declared objective + safety constraints + deterministic recommendation | JSON and Markdown decision evidence includes eligibility, rejection reasons, constraints, and source Arena artifact; first slice complete. |

The detailed product rationale, experimental design, and failure sequence are in
[Product and research design](docs/product-design.md). Promoted evidence is in
the [model catalog](docs/models/README.md) and [release notes](docs/releases/v1.1.0.md).

## Reproduce the maintained workflows

Core simulation, benchmark, Arena, and M15 decision workflow require Python
3.10+ and no third-party packages:

```bash
python3 -m unittest discover -s tests -v
python3 main.py benchmark --episodes 30 --controllers greedy assignment --report report
python3 main.py play --port 8080
python3 main.py arena-agent --strategies assignment greedy scout --objective balanced --episodes 10 --seed 42
```

Promoted model artifacts can be managed separately from training:

```bash
python3 main.py models list
python3 main.py models download
python3 main.py models verify
```

Optional learning workflows require `requirements-ml.txt`. Representative
formal pipelines are:

```bash
.venv-ml/bin/python main.py pipeline --config experiments/m6-bc-ppo.json
.venv-ml/bin/python main.py pipeline-m8 --config experiments/m8-coordination.json
.venv-ml/bin/python main.py pipeline-m14 --config experiments/m14-hierarchical-return.json
```

## Artifacts and sources of truth

| Evidence | Location |
| --- | --- |
| Promoted model identity, local path, digest, and parameters | `registry/models.json` |
| Failed and passed formal audits | `registry/audits.json` |
| Experiment definitions and seed ranges | `experiments/*.json` |
| Arena league and M15 decision artifacts | `runs/arena/` and configured run directories |
| Human-readable policy evidence | `docs/models/` and `docs/releases/` |

Generated datasets, weights, virtual environments, and run bundles stay out of
Git. Registry metadata and committed reports are the durable record; local
generated files are not automatically authoritative.

## Consumed evaluation data

Formal final seeds from M7, M8, M10, M11, M12, and M14 have been consumed.
Future research must allocate fresh validation and final ranges. Never tune on
these results, reuse final seeds for selection, or relax a gate after observing
the outcome.

## Models and releases

- v1.0.0: complete multi-agent experiment and Arena product.
- v1.0.1: explicit Apache-2.0 licensing.
- v1.1.0: M12–M14, model distribution, leagues, and evaluation artifacts.
- `models-v1`: `bc-ppo` and `coordinated-ctde`.
- `models-v2`: adds `hierarchical-return-ctde`; it shares M8 weights, with a
  new identity defined by supervisor code and parameters.
- M15 belongs to the v1.2 development line, but UI and multi-scenario decision
  expansion are paused.

## Maintenance-mode next steps

Accept critical defects, security, compatibility, reproducibility,
documentation, and release work. Resuming feature development requires a
specific research question, predeclared gates, and a budget of untouched final
seeds. A small Arena league must never be presented as a formal robustness audit.
