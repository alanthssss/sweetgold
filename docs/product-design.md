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
