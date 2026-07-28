# SweetGold promoted models v2

`models-v2` is the second immutable SweetGold model catalog. It adds the first
cross-distribution accepted policy, `hierarchical-return-ctde`, while retaining
the two v1 checkpoints for complete, clean installations.

## New promoted policy

The M14 policy combines the accepted coordinated CTDE actor with a
deterministic high-level return, deposit and recharge supervisor. On 50 fresh
final seeds in each of six declared scenarios it achieved:

- 100% bee survival and 0% invalid actions everywhere;
- median honey equal to 148.47% of Assignment;
- worst-case honey equal to 101.16% under scarce nectar;
- harsh-weather honey of 141.46 versus Assignment's 99.48.

The selected supervisor uses safety margin 6 and recharge fraction 0.8.

## Shared weights

`hierarchical-return-ctde.pt` and `coordinated-ctde.pt` intentionally have the
same SHA-256 digest. M14 did not retrain or silently mutate the neural actor.
Its new policy identity is the shared checkpoint plus the versioned supervisor
code and parameters in the registry.

## Assets and verification

The release contains all three promoted checkpoint names, the Apache-2.0
license and `models-v2-manifest.json`. The manifest declares exact byte sizes,
SHA-256 digests, model-card paths and controller parameters.

Use SweetGold to download and verify registered artifacts:

```bash
python main.py models download
python main.py models verify
```
