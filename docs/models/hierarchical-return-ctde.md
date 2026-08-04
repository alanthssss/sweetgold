# Hierarchical return CTDE model card

[English](hierarchical-return-ctde.md) | [简体中文](hierarchical-return-ctde.zh-CN.md)

## Identity

- Registry ID: `hierarchical-return-ctde`
- Milestone: M14
- Architecture: accepted M8 coordinated CTDE actor under a deterministic
  high-level return, deposit and recharge supervisor
- Shared weight artifact: `coordinated-ctde.pt`
- Controller parameters: safety margin 6, recharge fraction 0.8
- License: Apache-2.0

## Intended use

This is SweetGold's first cross-distribution accepted strategy. It is intended
for matched-seed research, Arena comparisons and workflow demonstrations. The
checkpoint alone is not the complete policy: reproducibility also requires the
versioned hierarchical controller and its registered parameters.

## Evaluation

Four supervisor configurations were compared only on fresh validation seeds.
The selected configuration was then evaluated once on 50 new seeds in each of
six scenarios. It achieved 100% bee survival and 0% invalid actions in every
scenario. Median honey was 148.47% of Assignment; the worst ratio was 101.16%
under scarce nectar. Harsh-weather honey was 141.46 versus 99.48 for
Assignment.

## Design

The lower actor still chooses local actions and uses decentralized harvest
reservations. The supervisor enters return mode when cargo is full, energy
approaches an expected travel budget, or the season is ending. It then moves
the bee to the hive, deposits cargo and recharges before returning control to
the learned actor.

## Limitations

This result covers the six declared simulator distributions, not arbitrary
real-world robotics or previously unseen environment mechanics. The high-level
supervisor is deterministic and hand-designed; the result demonstrates the
value of hybrid structure, not a fully learned hierarchy.

## Provenance

The actor weights are byte-identical to the Apache-2.0 M8
`coordinated-ctde` asset. M14 changes deployed policy behavior through
versioned controller code and registered parameters. Validation and final seed
sets are recorded in the ignored local run bundle and the committed audit.
