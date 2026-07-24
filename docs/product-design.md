# Product design

## Product 1 — BeeSim

BeeSim has two synchronized representations:

- **abstract state** for algorithms: arrays, entities, actions and seeded transitions;
- **concrete game** for people: an animated grid, season controls, weather,
  flowers, bees, signals and live colony metrics.

The user can select a controller, choose a seed, pause, single-step and replay
the same season. The UI is an observer and operator; it does not contain hidden
game rules.

## Product 2 — BeeBench

BeeBench treats every controller as a policy:

```python
controller.reset(seed)
actions = controller.act(observation)
```

All policies receive the same environment seeds. The evaluator owns transitions
and metrics, preventing a controller from changing evaluation behavior.

## Current hypothesis

The initial benchmark should not prove that a complex policy is better. It
should expose trade-offs:

- Random explores broadly but cannot sustain the colony.
- Greedy efficiently exploits visible resources but creates contention.
- Scout sacrifices short-term yield for information sharing and exploration.

The first measured run confirms the framework can distinguish those behaviors,
but 12 episodes are a smoke test rather than a publishable result.

## M2 experiment

The centralized Assignment controller reserves one flower per bee and keeps
valid reservations across ticks. The benchmark now separates colony survival
from individual bee survival and reports invalid-action rates.

The acceptance experiment compares Assignment against Greedy on 100 matched
seeds. M2 succeeds if Assignment removes most invalid actions and improves bee
survival without materially reducing honey yield. Only after this baseline is
stable should behavior cloning and reinforcement learning be introduced.

## M3 experiment

Energy-aware fleet sizing keeps a stable two-bee reserve during the first half
of the season, then releases the full colony after renewable flowers have
accumulated late-season value. Loaded bees always finish their trips.

Across 100 matched seeds, this raises Assignment's mean energy efficiency from
0.103 to 0.114 while retaining 156.61 mean honey, 95.25% bee survival and a 0%
invalid-action rate. It slightly beats Greedy's 155.91 mean honey, but does not
yet match Greedy's 0.122 energy efficiency.

## M4 experiment

Behavior cloning uses an ego-centric fixed vector containing the complete
flower field and relative states of the other bees. Class-weighted training
protects rare harvest and deposit actions. One DAgger iteration adds teacher
labels for states visited by the learned controller, reducing compounding
errors without contaminating validation or test seeds.

On 30 completely unseen test seeds, the learned controller produces 136.10
mean honey versus Assignment's 140.30 (97.0%), with 95.0% bee survival and a
0.77% invalid-action rate. Offline action accuracy is 83.5%; the result confirms
that online matched-seed performance is the more meaningful selection metric.

## M5 experiment

PPO initializes its actor from the accepted behavior-cloning checkpoint and
trains a separate critic on full-season rollouts. Honey remains the dominant
reward, with small penalties for invalid actions, deaths and energy use.
Checkpoint selection uses ten validation seeds that are disjoint from training
and final test seeds.

Across 100 unseen test seeds, BC+PPO produces 153.98 mean honey versus BC's
145.79. The paired improvement is +8.19 with a 95% confidence interval of
[+3.69, +12.69]. Bee survival rises from 90.88% to 99.0%, energy efficiency
rises from 0.110 to 0.118, and invalid actions remain below 1%. Randomly
initialized PPO produces zero honey after the same 100-episode budget,
demonstrating the practical value of behavior-cloning initialization.

## M6 experiment operations

M6 turns the individual ML commands into a configuration-driven pipeline.
Before execution it expands the actual data, DAgger, PPO training, PPO
validation and final test seed sets and rejects any overlap.

Each run records its configuration, Git commit, runtime, seed manifest,
checkpoints, training history, matched-seed metrics, promotion checks and HTML
report. A candidate enters the model registry only when its paired confidence
interval is above zero and all declared safety and quality thresholds pass.
Core and ML smoke workflows run automatically in CI.
