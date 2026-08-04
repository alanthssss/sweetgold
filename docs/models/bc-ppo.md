# BC+PPO model card

[English](bc-ppo.md) | [简体中文](bc-ppo.zh-CN.md)

## Identity

- Registry ID: `bc-ppo`
- Milestone: M6
- Architecture: local behavior-cloning actor initialized from Assignment
  demonstrations and fine-tuned with PPO
- Artifact: `bc-ppo.pt`
- License: Apache-2.0

## Intended use

This checkpoint is intended for SweetGold experiments, matched-seed strategy
comparison and educational demonstrations. It requires the optional PyTorch
dependencies and is not a general-purpose agent.

## Evaluation

On 100 unseen matched seeds, BC+PPO produced 153.98 mean honey versus 145.79
for behavior cloning. The paired improvement was +8.19 honey with a 95%
confidence interval of [+3.69, +12.69]. Bee survival was 99.0%, and the
invalid-action rate was 0.96%.

## Limitations

The model was promoted before the cross-distribution M10–M12 robustness
program. Its result applies to the declared in-distribution evaluation, not to
large maps, scarce resources or harsh weather. Do not treat it as a production
control policy.

## Provenance

Training data was generated entirely inside the seeded SweetGold simulation.
The registry records the source run, source commit, promotion checks and exact
artifact digest.
