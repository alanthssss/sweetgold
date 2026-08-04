# Coordinated CTDE model card

[English](coordinated-ctde.md) | [简体中文](coordinated-ctde.zh-CN.md)

## Identity

- Registry ID: `coordinated-ctde`
- Milestone: M8
- Architecture: radius-four decentralized actor trained with a centralized
  critic and wrapped in local harvest-intent reservations
- Artifact: `coordinated-ctde.pt`
- License: Apache-2.0

## Intended use

This is SweetGold's accepted learned strategy for local matched-seed
experiments and Strategy Arena comparisons. It requires the optional PyTorch
dependencies. The local reservation layer is part of the deployed controller.

## Evaluation

On 100 fresh final seeds, coordinated CTDE produced 147.57 mean honey versus
141.38 for local behavior cloning. The paired improvement was +6.19 with a 95%
confidence interval of [+3.41, +8.97]. It prevented 13.51 conflicts per
episode on average, with 0% invalid actions and zero unresolved contention.

## Limitations

M10–M12 show that the feed-forward actor is not generally robust. M12 improved
large-map survival to 86.25% and harsh-weather survival to 27.75%, but
scarce-nectar yield remained below its promotion gate. The registered M8 model
must therefore be described as an in-distribution accepted model, not a
generally robust policy.

## Provenance

Training data was generated entirely inside the seeded SweetGold simulation.
The registry records the source run, source commit, promotion checks and exact
artifact digest.
