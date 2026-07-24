# SweetGold handoff

## Current milestone

M2 tests whether centralized flower assignment reduces internal contention
without materially reducing honey yield.

## Implemented

- `AssignmentController` with persistent, distinct flower reservations.
- Unambiguous colony and individual-bee survival metrics.
- Honey-per-bee and invalid-action-rate metrics.
- Matched-seed Assignment-versus-Greedy summary in the HTML report.
- Assigned-target highlighting in BeeSim.
- Controller and metric regression tests.

## Verification

The 100-seed matched experiment (starting at seed 20260724) passed:

- Assignment: 161.23 mean honey, 94.25% bee survival, 0% invalid actions.
- Greedy: 155.91 mean honey, 67.25% bee survival, 3.36% invalid actions.
- Paired honey delta: Assignment +5.32; 53 wins, 2 ties, 45 losses.
- All 8 automated tests pass.

Reproduce with:

```bash
python3 -m unittest discover -s tests -v
python3 main.py benchmark --episodes 100 --controllers greedy assignment --report report
python3 main.py play --port 8080
```

## Next decision

Use the 100-seed result to decide whether to refine Assignment's energy
efficiency or begin behavior cloning from it. Do not begin reinforcement
learning until the deterministic baseline and evaluation protocol are stable.

## M3 energy-aware fleet sizing

M3 keeps two bees in reserve for the first half of the season and activates the
full surviving colony in the second half. On the same 100 seeds:

- Assignment: 156.61 mean honey, 0.114 efficiency, 95.25% bee survival,
  0% invalid actions.
- Greedy: 155.91 mean honey, 0.122 efficiency, 67.25% bee survival,
  3.36% invalid actions.

Compared with M2 Assignment, energy efficiency improves by about 10% while
mean honey decreases by about 2.9%. The strict aspirational thresholds of 160
honey and 0.115 efficiency were not simultaneously attainable with a static
fleet size; this dynamic schedule is the best tested balance.

## M4 behavior cloning

The optional PyTorch pipeline now supports:

- episode-level train/validation/test seed isolation;
- Assignment trajectory collection;
- class-weighted behavior-cloning training;
- DAgger collection on learner-visited training states;
- action masking and matched-seed BC benchmarking.

The accepted checkpoint uses 100 teacher episodes plus one 50-episode DAgger
iteration. On 30 unseen test seeds:

- Assignment: 140.30 mean honey, 92.5% bee survival.
- Behavior cloning: 136.10 mean honey (97.0% of teacher), 95.0% bee survival,
  0.77% invalid actions.
- Greedy: 139.07 mean honey, 62.5% bee survival, 2.97% invalid actions.

Generated datasets, checkpoints, virtual environments and BC reports are
ignored by Git. A second DAgger iteration was tested and rejected because
online performance regressed; checkpoint selection must use separate online
validation seeds rather than assuming more aggregation always helps.

## M5 BC-initialized PPO

The optional PPO pipeline includes masked stochastic rollouts, GAE, clipped PPO
updates, a learned critic, shaped team rewards and validation-only checkpoint
selection. On 100 unseen test seeds:

- Assignment: 155.78 mean honey, 96.25% bee survival.
- Behavior cloning: 145.79 mean honey, 90.88% bee survival.
- BC+PPO: 153.98 mean honey, 99.0% bee survival, 0.96% invalid actions.
- Random-init PPO: 0 mean honey after the same 100-episode training budget.

BC+PPO improves over BC by +8.19 honey per matched seed; the paired 95%
confidence interval is [+3.69, +12.69], with 65 wins, 3 ties and 32 losses.
The selected checkpoint is episode 50 with validation honey 146.10. Generated
PPO checkpoints, training histories and reports remain ignored by Git.
