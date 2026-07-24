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

## Next experiment

Implement a centralized assignment controller that reserves one flower per bee
and compares it against Greedy. This will test whether reduced contention
improves honey yield and invalid-action rate. Only after this baseline is stable
should behavior cloning and reinforcement learning be introduced.
