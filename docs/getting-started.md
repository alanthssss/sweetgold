# Start here: understand SweetGold from zero

[English](getting-started.md) | [简体中文](getting-started.zh-CN.md)

This guide is for readers who are new to SweetGold, multi-agent learning, or
the engineering practices around machine-learning experiments. You do not need
an AI background to begin.

## The project in one minute

SweetGold starts as a small game. A hive contains several virtual bees. Flowers
hold nectar. Bees can move, harvest, deposit honey, and recharge. A season ends,
and we measure how much honey the colony stored, whether the bees survived, and
whether their actions were valid.

The real question is not about beekeeping:

> How can several independent agents act locally and still cooperate as a
> reliable group?

Several bees may chase the same flower, ignore distant resources, run out of
energy, or fail to return home. SweetGold provides a controlled world where we
can compare solutions to those coordination problems.

## The learning path

The project grows in five understandable steps:

1. **Build the world and referee.** Define the map, flowers, energy, actions,
   scoring, and when an episode ends.
2. **Write rule-based strategies.** Establish understandable baselines before
   asking a model to learn.
3. **Train learned strategies.** First imitate demonstrations, then improve by
   reinforcement learning.
4. **Give every strategy the same exam.** Run competitors on identical random
   seeds and keep training, validation, selection, and final-test data separate.
5. **Publish only with evidence.** A policy must pass declared yield and safety
   gates; models, hashes, reports, and failures remain traceable.

## Why the random seed matters

A seed recreates the same initial world. If strategy A receives an easy map and
strategy B receives a hard one, their scores are not a fair comparison. In
SweetGold, both receive the same seed—like two candidates taking the same exam.

This simple idea is the foundation for matched-seed evaluation, reproducibility,
and many of the project's later engineering controls.

## Where AI enters

The first useful controllers are handwritten rules. They demonstrate actions
such as seeking flowers, returning honey, and recharging. Behavior cloning then
trains a neural network to imitate those demonstrations. PPO provides a later
reinforcement-learning stage, while CTDE lets agents learn with shared global
information but act from local observations.

You do not need to understand those algorithms to use SweetGold. The important
idea is that learned behavior is compared with clear baselines under the same
conditions.

## What M14, M15, and M16 mean

| Label | Plain-language meaning | What it is not |
| --- | --- | --- |
| M14 | The latest policy that passed the formal final exam | Not the newest piece of project work |
| M15 | A referee that recommends or rejects strategies and records why | Not a newly trained model |
| M16 | Hardware-aware execution and CPU/MPS evidence | Not a claim that GPU is always faster |

These labels describe different kinds of progress, so M14 can remain the newest
promoted policy while M16 is the latest engineering milestone.

## What the engineering work protects

- **Determinism:** the same seed recreates the same experiment.
- **Data isolation:** the final exam cannot influence training or model choice.
- **Promotion gates:** success criteria are declared before results are seen.
- **Auditability:** configurations, metrics, decisions, and failed candidates
  remain available.
- **Model integrity:** public checkpoints include immutable links and SHA-256
  verification.
- **Regression protection:** automated tests exercise the simulator and ML
  workflows after changes.

These are production-minded practices around an experimental system. The local
web server itself is not presented as a hardened multi-user production service.

## Choose your next route

- **I just want to see it:** follow the three-command quick start in the
  [README](../README.md#quick-start).
- **I want the research story:** read the
  [product and research design](product-design.md).
- **I work in ML:** inspect the [model catalog](models/README.md) and promotion
  evidence.
- **I work in DevOps or MLOps:** read the [handoff guide](../HANDOFF.md),
  [hardware benchmark](hardware-benchmark.md), and CI configuration.
- **I met an unfamiliar term:** use the [bilingual glossary](glossary.md).

## Current boundary

Version 1.2.0 completes the current feature-development cycle. SweetGold is in
a maintenance phase: critical defects, security, compatibility,
reproducibility, documentation, and release reliability remain in scope, while
unfocused new feature development is paused.

