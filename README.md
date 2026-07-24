# SweetGold

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

**Version 1.0.1 — reproducible multi-agent AI experimentation platform**

SweetGold connects a deterministic simulation, strategy baselines, imitation
and reinforcement learning, model promotion, robustness audits and an
interactive comparison product.

- **Strategy Arena** runs two policies from the same seed with live metrics and
  replay.
- **BeeBench** provides matched-seed evaluation and confidence intervals.
- **ML pipelines** cover BC, DAgger, PPO, CTDE, model registration and audits.

SweetGold promotes models only when their predeclared quality and safety gates
pass. Failed M10–M12 robustness experiments are preserved as first-class
results rather than hidden or retroactively retuned.

## Quick start

Requires Python 3.10+ and no third-party packages.

```bash
# Run tests
python3 -m unittest discover -s tests -v

# Print the release version
python3 main.py --version

# Run a benchmark and write report/index.html
python3 main.py benchmark --episodes 30 --report report

# Open the interactive game
python3 main.py play --port 8080
```

Then visit <http://127.0.0.1:8080>.

Rule strategies work in a fresh clone. Learned checkpoints are generated
locally and intentionally excluded from Git; the arena disables unavailable
models and verifies the hashes of checkpoints that are present.

See [v1.0.1 release notes](docs/releases/v1.0.1.md),
[changelog](CHANGELOG.md), and the
[release checklist](docs/release-checklist.md).

## License

SweetGold is licensed under the [Apache License 2.0](LICENSE).
Copyright 2026 alanthssss. Model checkpoints and datasets distributed
separately may have their own license terms.

## Products

### BeeSim

The simulation is represented as arrays and small records:

- a `height × width` terrain matrix;
- renewable flower patches with nectar;
- a hive with stored food;
- bees with position, energy, cargo and role;
- stochastic weather and movement driven by a seeded RNG.

At each tick, every living bee chooses one action:

`up`, `down`, `left`, `right`, `harvest`, `deposit`, `rest`, or `signal`.

The game ends when the configured season length is reached or all bees die.

### BeeBench

BeeBench evaluates controllers on identical episode seeds and reports:

- colony survival rate;
- honey delivered to the hive;
- energy efficiency;
- exploration coverage;
- deaths;
- invalid-action rate;
- decision latency.

Included baselines:

- `random`
- `greedy`
- `scout`
- `assignment` — centralized, persistent one-flower-per-bee reservations

Assignment uses a stable early-season reserve and expands to the full fleet in
the second half of the season, improving energy efficiency without introducing
resource contention.

## Architecture

```text
beehive/
  env.py          seeded ecosystem and transition rules
  controllers.py unified policy interface and baselines
  evaluator.py    matched-seed evaluation and aggregation
  report.py       self-contained HTML leaderboard
  server.py       game HTTP API and static UI
web/
  index.html      interactive visual game
  app.js
  styles.css
```

## Learning-agent extension

`BeeEnv.observe()` returns JSON-compatible state and `BeeEnv.step()` accepts a
mapping from bee IDs to actions. A future learning adapter can convert the
observation to tensors without changing the environment or evaluator.

Recommended progression:

1. validate `assignment` against `greedy` on at least 100 matched seeds;
2. single-bee DQN against `greedy`;
3. behavior cloning from `assignment`;
4. centralized PPO with all-bee observations;
5. centralized training/decentralized execution with local observations.

Do not claim an RL improvement until it beats `behavior-cloning-only` on
unseen, fixed seeds with confidence intervals.

## Optional behavior cloning

The simulation and rule-based benchmarks remain dependency-free. The M4
learning pipeline uses optional PyTorch dependencies:

```bash
python3 -m venv .venv-ml
.venv-ml/bin/pip install -r requirements-ml.txt
.venv-ml/bin/python main.py collect --episodes 100
.venv-ml/bin/python main.py train-bc --epochs 15
.venv-ml/bin/python main.py collect-dagger --episodes 50
.venv-ml/bin/python main.py train-bc --epochs 15
.venv-ml/bin/python main.py benchmark-bc --episodes 30
```

Whole episode seeds are assigned to train, validation or test before examples
are written. DAgger only appends training-seed states, so validation and test
episodes remain unseen.

## Optional PPO fine-tuning

PPO starts from the accepted behavior-cloning checkpoint and uses separate
training, validation and test seeds:

```bash
.venv-ml/bin/python main.py train-ppo --episodes 100
.venv-ml/bin/python main.py benchmark-ppo --episodes 100
```

For the initialization control:

```bash
.venv-ml/bin/python main.py train-ppo --random-init \
  --model models/random-ppo.pt --episodes 100
.venv-ml/bin/python main.py benchmark-ppo --random-model models/random-ppo.pt
```

The trainer saves only checkpoints that improve deterministic online validation
honey. Final reports include paired BC-versus-PPO confidence intervals.

## End-to-end experiment pipeline

M6 connects data generation, training, validation, final testing, reporting and
model promotion:

```bash
.venv-ml/bin/python main.py pipeline \
  --config experiments/m6-bc-ppo.json
```

The command rejects seed leakage before doing work and writes an immutable run
bundle under `runs/<experiment>/` containing the configuration, metadata,
dataset manifest, checkpoints, metrics, training history and HTML report.

An accepted model is appended to `registry/models.json`. Promotion requires a
positive paired 95% confidence-interval lower bound plus the survival,
invalid-action and yield thresholds declared in the experiment config.

GitHub Actions runs the zero-dependency test suite and a small end-to-end ML
pipeline smoke test. Full experiments remain explicit because they are more
expensive and are used for final model promotion.

## Local-observation CTDE

M7 limits each deployed actor to flowers, bees and signals within Manhattan
radius four. During training only, a centralized critic receives the global
observation. Four environment rollouts run in parallel:

```bash
.venv-ml/bin/python main.py pipeline-m7 \
  --config experiments/m7-ctde.json
```

The local encoder pads visible entities to a fixed size and ignores all
out-of-radius state. The M7 pipeline applies the same seed isolation,
checkpoint, paired-comparison and promotion rules as M6.

The first formal M7 candidate significantly improves over local behavior
cloning but is intentionally not registered: its 1.056% invalid-action rate is
slightly above the predeclared 1% safety threshold.

## Decentralized contention coordination

M8 adds a local intent-and-reservation protocol around the CTDE actor:

```bash
.venv-ml/bin/python main.py pipeline-m8 \
  --config experiments/m8-coordination.json
```

Bees broadcast a harvest intent only to peers on the same flower. A rotating
priority grants the observed nectar supply; denied bees take their next-best
valid action. The protocol does not assign global targets and the actor still
uses only its radius-four observation.

On 100 new final seeds, coordinated CTDE scores 147.57 mean honey versus
141.38 for local behavior cloning. The paired improvement is +6.19 with a 95%
confidence interval of [+3.41, +8.97]. It prevents 13.51 oversubscribed
harvests per episode on average and reduces the uncoordinated CTDE invalid
action rate from 0.742% to 0%, with no unresolved resource conflicts. The
candidate passes every predeclared promotion gate and is registered.

## Strategy Arena

M9 turns BeeSim into a matched-seed strategy comparison product:

```bash
.venv-ml/bin/python main.py play --port 8080
```

The arena discovers rule strategies and accepted learned policies from
`registry/models.json`, verifies checkpoint hashes before loading them, and
clearly disables models whose generated artifacts are not present locally.
Two strategies run from identical initial worlds and the same stochastic seed.
Live honey deltas, survival, efficiency, invalid actions and coordination
metrics are displayed side by side. Every server-side frame can be revisited
with the replay timeline without changing the live simulation.

## Generalization and robustness audit

M10 evaluates an accepted model without retraining it across declared
environment shifts:

```bash
.venv-ml/bin/python main.py pipeline-m10 \
  --config experiments/m10-robustness.json
```

The pipeline allocates a disjoint test-seed range to every scenario, compares
the candidate with Assignment on matched episodes, writes a JSON/HTML audit,
and checks median and worst-case yield, survival and invalid-action thresholds.

The first coordinated-CTDE audit fails as intended rather than weakening its
gates. Its median yield is 99.56% of Assignment and it retains 0% invalid
actions, but scarce nectar falls to 74.68% of baseline yield. Survival falls
to 50.25% on the large map and 7.75% under high rain with reduced energy.
These failures define M11's curriculum targets.

## Curriculum robustness training

M11 fine-tunes the accepted coordinated actor through independently seeded
default, distance, weather/energy, scarcity and recovery stages:

```bash
.venv-ml/bin/python main.py pipeline-m11 \
  --config experiments/m11-curriculum.json
```

Each stage is scored on a fixed, disjoint multi-scenario validation suite.
Checkpoint selection favors the number of predeclared gates passed before
survival and normalized yield; final test scenarios remain untouched until the
selection is complete. Stage trainers can weight validation survival without
changing the default M7/M8 checkpoint semantics.

The first sequential curriculum does not pass promotion. Validation weather
training raises worst-case survival from 4.17% to 17.71%, but loses the
scarce-resource yield gate, so the balanced default-refresh checkpoint is
selected. On new final seeds it retains a 99.51% median yield ratio and 0%
invalid actions, but harsh-weather survival is 6.5% and worst-case yield is
69.85%. The candidate is audited but not registered.

## Interleaved robustness training

M12 replaces sequential curriculum stages with balanced round-robin rollouts
from default, large-map, scarce-nectar and harsh-weather environments:

```bash
.venv-ml/bin/python main.py pipeline-m12 \
  --config experiments/m12-interleaved.json
```

Each training cycle gives every scenario the same episode budget. A cycle may
replace the current checkpoint only through a disjoint four-scenario
validation suite; the final scenario seeds are evaluated once after selection.

Interleaving substantially improves the failed M11 candidate without passing
promotion. On fresh final seeds, harsh-weather survival rises from 6.5% to
27.75%, large-map survival reaches 86.25%, median yield is 99.23% of
Assignment and invalid actions remain at 0%. Scarce-nectar yield is still only
73.65% of Assignment, below the predeclared 75% floor, so the model is audited
but not registered.
