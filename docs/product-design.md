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

## M7 decentralized execution

M7 introduces centralized training with decentralized execution. Actors see
only entities within Manhattan radius four, while the critic may use the full
state during PPO updates. Deployment therefore has no dependency on the global
critic. Rollouts use four deterministic per-seed workers.

On 100 untouched final seeds, CTDE produces 159.71 mean honey versus local
behavior cloning's 153.11 and Assignment's 157.41. The paired CTDE improvement
is +6.60 with a 95% confidence interval of [+3.28, +9.92]. Survival is 91.0%.
The candidate is rejected rather than registered because its 1.056% invalid
action rate narrowly exceeds the predeclared 1% threshold. This identifies
decentralized contention as the next concrete research problem.

## M8 local coordination

M8 keeps the M7 actor unchanged at execution time except for a local protocol
between bees that simultaneously intend to harvest the same flower. Each
flower acts as a resource with capacity equal to its currently observed
nectar. A seed- and tick-dependent rotating priority grants reservations, and
denied bees select their next-highest-scoring legal action.

The experiment records harvest intents, contested intents, reservation grants,
prevented conflicts, unresolved conflicts and their rates. Across 100 fresh
final seeds, coordinated CTDE produces 147.57 mean honey against local behavior
cloning's 141.38. The paired delta is +6.19 with a 95% confidence interval of
[+3.41, +8.97]. It prevents 13.51 conflicts per episode on average, resolves
all observed oversubscription, and reduces invalid actions from the equivalent
uncoordinated actor's 0.742% to 0%.

The coordination layer changes honey by only +0.11 ± 2.20 relative to the same
uncoordinated actor. Its benefit is therefore safety rather than a claimed
yield improvement. The candidate passes the predeclared yield, survival,
invalid-action and unresolved-contention gates.

## M9 product loop

The strategy arena exposes SweetGold's research results as a user-facing
comparison workflow. The user selects two strategies and one seed; both lanes
receive identical flower layouts and the same stochastic seed. The scoreboard
shows the live yield delta while each lane reports survival, efficiency,
invalid actions and, when applicable, prevented conflicts.

The server reads the accepted model registry, verifies each checkpoint digest
before loading it and keeps rule strategies available when optional PyTorch
artifacts are absent. Replay frames are retained on the server so scrubbing the
timeline never mutates or recomputes the live match.
