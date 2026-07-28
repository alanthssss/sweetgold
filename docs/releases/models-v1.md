# SweetGold promoted models v1

This release distributes the first two SweetGold checkpoints that passed their
predeclared promotion gates. The weights are copyright 2026 alanthssss and
licensed under the Apache License 2.0.

## Assets

| Asset | Registry ID | Size | SHA-256 |
| --- | --- | ---: | --- |
| `bc-ppo.pt` | `bc-ppo` | 78,025 bytes | `441e1770146962dd963df6f1b699c57b186a03c043e6d691a358f51911158f1d` |
| `coordinated-ctde.pt` | `coordinated-ctde` | 68,065 bytes | `86fd605a1f013638ea89e95e1a71b65c0da243c003b7b22cf90e27dfe4397a68` |

The repository source archive contains the complete Apache-2.0 license and
model cards. The committed registry is the authoritative mapping from model
identity to asset URL, local artifact path and digest.

## Install

From a SweetGold checkout at or after the M13 model-distribution milestone:

```bash
python3 main.py models download
python3 main.py models verify
```

Optional PyTorch dependencies are required to execute the learned strategies,
but not to download or verify them.

## Scope

`bc-ppo` and `coordinated-ctde` passed their original in-distribution
promotion gates. M10–M12 demonstrate that neither should be described as a
generally robust or production control policy. See the linked model cards and
audit registry for their intended uses and limitations.
