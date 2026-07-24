# Sweetgold Lab

Sweetgold Lab contains two products built on the same deterministic simulation:

1. **BeeSim** — an abstract grid-based bee ecosystem and a playable web game.
2. **BeeBench** — a reproducible controller benchmark with JSON and HTML reports.

The first milestone deliberately uses transparent rule-based controllers. They
establish baselines before learning agents are added.

## Quick start

Requires Python 3.10+ and no third-party packages.

```bash
# Run tests
python3 -m unittest discover -s tests -v

# Run a benchmark and write report/index.html
python3 main.py benchmark --episodes 30 --report report

# Open the interactive game
python3 main.py play --port 8080
```

Then visit <http://127.0.0.1:8080>.

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
