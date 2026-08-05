# SweetGold

[English](README.md) | [简体中文](README.zh-CN.md)

<p align="center">
  <img src="docs/assets/sweetgold-social.png" alt="SweetGold — teach a colony to survive the unknown" width="100%">
</p>

<p align="center"><strong>A reproducible multi-agent AI lab where policies earn their promotion.</strong></p>

<p align="center">
  <a href="https://github.com/alanthssss/sweetgold/actions"><img src="https://github.com/alanthssss/sweetgold/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-f4b942.svg" alt="Apache 2.0 license"></a>
  <a href="https://github.com/alanthssss/sweetgold/releases/tag/v1.2.0"><img src="https://img.shields.io/badge/release-v1.2.0-0d110f.svg" alt="v1.2.0"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-83d7aa.svg" alt="Python 3.10+">
</p>

SweetGold combines a deterministic bee-colony simulator, a matched-seed
benchmark, and an interactive Strategy Arena. It supports behavior cloning,
PPO, and centralized training with decentralized execution (CTDE), while
keeping training, validation, and final-test seeds isolated.

<!-- section:start-here -->
## New to the project? Start here

SweetGold begins as a small game: virtual bees move, collect nectar, return
honey, and recharge before a season ends. The research question is how several
independent agents can act locally while cooperating as a reliable colony.

If terms such as PPO, CTDE, promotion gates, or matched seeds are unfamiliar,
read **[Start here: understand SweetGold from zero](docs/getting-started.md)**.
It explains the project without assuming an AI background and provides separate
routes for curious visitors, ML practitioners, and DevOps/MLOps readers.

<!-- section:current-project-stage -->
## Current project stage: M16

M16 phase 1 adds hardware-portable ML execution and evidence. All ML commands
now support explicit CPU, Apple MPS, and NVIDIA CUDA selection; run manifests
record the hardware backend, and unavailable accelerators never silently fall
back. M6 BC+PPO and M7 CTDE smoke workflows complete on an Apple M1 Pro GPU.

The first local benchmark found the small BC workload about 6.4× faster on the
M1 Pro CPU than MPS, so AWS CUDA work is deferred until profiling justifies it.
See the [hardware benchmark](docs/hardware-benchmark.md).

<!-- section:latest-completed-outcome -->
## Latest completed product workflow: M15

M15 is the current project stage. It turns Arena evidence into an explicit,
auditable strategy decision; it does not train or replace the underlying policy.

| M15 workflow capability | Delivered result |
| --- | --- |
| Decision objectives | `balanced`, `yield`, and `safety` |
| Safety constraints | Minimum bee survival and maximum invalid-action rate |
| Decision behavior | Deterministic recommendation or an explicit “no eligible strategy” result |
| Evidence | Linked Arena artifact plus machine-readable JSON and human-readable Markdown |

The first M15 slice is complete on `main`. New feature development is paused
while the project focuses on maintenance, documentation, and releases.

<!-- section:latest-promoted-policy -->
## Latest promoted policy: M14

Because M15 selects among existing strategies, M14 `hierarchical-return-ctde`
remains the latest policy with formal cross-distribution performance results.

| M14 result on untouched final seeds | Result |
| --- | ---: |
| Minimum bee survival across six scenarios | **100%** |
| Maximum invalid-action rate | **0%** |
| Median honey versus Assignment | **148.47%** |
| Worst-case honey versus Assignment | **101.16%** |

> M14 used 50 unseen seeds in each of six environment distributions. See the
> [model card](docs/models/hierarchical-return-ctde.md) and
> [release notes](docs/releases/v1.1.0.md) for scope and methodology.

<!-- section:why-sweetgold -->
## Why SweetGold?

- **Same world, different minds.** Strategies start from identical worlds and
  random seeds, with live metrics and frame-by-frame replay.
- **Failures remain evidence.** M10–M12 missed predeclared robustness gates;
  their audits remain committed and informed M14's structural change.
- **Reproducible by construction.** Seed manifests, leakage checks, immutable
  artifacts, confidence intervals, and SHA-256-verified checkpoints are built in.
- **Useful without an ML stack.** The simulator, rule strategies, benchmark,
  and web Arena run on Python 3.10+ without third-party packages.

<!-- section:quick-start -->
## Quick start

```bash
git clone https://github.com/alanthssss/sweetgold.git
cd sweetgold
python3 main.py play --port 8080
```

Open <http://127.0.0.1:8080>. To create a 30-episode matched-seed report:

```bash
python3 main.py benchmark --episodes 30 --report report
```

List, download, and verify promoted models:

```bash
python3 main.py models list
python3 main.py models download
python3 main.py models verify
```

Run the M15 auditable recommendation workflow:

```bash
python3 main.py arena-agent \
  --strategies assignment greedy scout \
  --objective balanced \
  --min-bee-survival 0.9 \
  --max-invalid-action-rate 0.01 \
  --episodes 10 --seed 42
```

A small league demonstrates the workflow; it does not replace a formal
cross-distribution robustness audit.

<!-- section:products -->
## Three product layers

### BeeSim — bee-colony simulator

A seeded world of terrain, renewable flowers, a hive, bees, and stochastic
weather. `BeeEnv.observe()` returns JSON-compatible state and `BeeEnv.step()`
accepts a bee-ID-to-action mapping, so learning adapters do not modify the core.

### BeeBench — matched-seed evaluation

Controllers run on identical episode seeds. Reports cover honey, colony and
individual survival, energy efficiency, coverage, deaths, invalid actions, and
decision latency, with paired confidence intervals.

### Strategy Arena — interactive comparison

Arena discovers registered rule and learned strategies, verifies model SHA-256
before loading, runs strategies in the same world, and preserves every frame.
M15 converts league evidence into a constrained, traceable recommendation.

<!-- section:engineering-guarantees -->
## Engineering guarantees

SweetGold treats reproducibility and model delivery as product capabilities,
not post-hoc research hygiene.

| Practice | Enforced behavior |
| --- | --- |
| Deterministic execution | Seeded environments and matched episodes make strategy comparisons repeatable. |
| Data isolation | Training, internal validation, model selection, and final-test seed sets are expanded and checked for leakage before execution. |
| Policy-as-code promotion | Confidence, yield, survival, invalid-action, and scenario gates are declared in versioned experiment configs. |
| Auditable evidence | Run bundles preserve configuration, commit, runtime, seed manifest, metrics, decisions, and source-artifact links in machine-readable formats. |
| Verified model supply chain | Immutable release URLs, exact sizes, SHA-256 digests, licenses, model cards, and atomic installation protect distributed checkpoints. |
| Automated regression protection | Dependency-free tests and end-to-end ML smoke pipelines run in CI; failed candidates remain in the audit registry. |

These are enterprise-style engineering practices, not a claim that the local
HTTP server is a hardened multi-user production service. See the
[handoff guide](HANDOFF.md) for sources of truth and operational boundaries.

<!-- section:research-journey -->
## Research journey

| Milestone | Outcome |
| --- | --- |
| M2–M3 | Established the deterministic Assignment baseline and improved formation efficiency. |
| M4 | Behavior cloning + DAgger reached 97% of teacher honey on the test set. |
| M5–M6 | Added BC-initialized PPO and an end-to-end selection and promotion pipeline. |
| M7 | Local-observation CTDE improved over local BC, but failed the 1% invalid-action gate. |
| M8 | Intent broadcasts and rotating priority resolved contention; the candidate passed. |
| M9 | Added same-seed Strategy Arena comparison, metrics, and replay. |
| M10–M12 | Three robustness audits failed declared scarcity/weather gates and were preserved. |
| M13 | Separated model metadata and large artifacts with immutable URLs and SHA-256 checks. |
| M14 | Added a hierarchical return supervisor; all six final scenarios passed. |
| M15 | Added an auditable decision workflow with objectives, constraints, and linked evidence. |

For the full methodology and failure analysis, read the
[product and research design](docs/product-design.md).

<!-- section:optional-ml-pipelines -->
## Optional ML pipelines

Learning features require the PyTorch dependencies in `requirements-ml.txt`.
Representative end-to-end entry points are:

```bash
.venv-ml/bin/python main.py pipeline --config experiments/m6-bc-ppo.json
.venv-ml/bin/python main.py pipeline-m8 --config experiments/m8-coordination.json
.venv-ml/bin/python main.py pipeline-m14 --config experiments/m14-hierarchical-return.json
```

Pipelines expand and validate seed sets before execution to prevent leakage
between training, validation, selection, and final testing. Generated datasets,
weights, and run directories stay outside Git. See the
[handoff guide](HANDOFF.md) for setup, commands, artifacts, and acceptance gates.

<!-- section:documentation -->
## Documentation

| Topic | Document |
| --- | --- |
| Zero-background project introduction and reader routes | [Start here](docs/getting-started.md) |
| Practical impact, customer hypotheses, SWOT, and commercialization gates | [Impact and roadmap](docs/impact-and-roadmap.md) |
| Product architecture and M2–M16 research record | [Product and research design](docs/product-design.md) |
| CPU, MPS, CUDA, and cloud decision evidence | [Hardware portability and benchmark](docs/hardware-benchmark.md) |
| Setup, commands, artifacts, and gates | [Handoff guide](HANDOFF.md) |
| Promoted checkpoints and evidence | [Model catalog](docs/models/README.md) |
| Published results and methodology | [Release notes](docs/releases/v1.2.0.md) |
| New technical terms | [Bilingual glossary](docs/glossary.md) |
| Contributions and project operation | [Contributing](CONTRIBUTING.md) · [Maintenance](MAINTENANCE.md) · [Security](SECURITY.md) |

<!-- section:license -->
## License

SweetGold source code is licensed under the [Apache License 2.0](LICENSE).
Separately distributed models and datasets may have their own terms.
