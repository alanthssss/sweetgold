# Changelog

[English](CHANGELOG.md) | [简体中文](CHANGELOG.zh-CN.md)

All notable SweetGold changes are documented here. The project uses semantic
versioning from v1.0.0 onward.

## [Unreleased]

## [1.2.0] - 2026-08-04

### Added

- M15 auditable Arena agent workflow with explicit objectives, safety
  constraints, deterministic recommendations and paired JSON/Markdown
  decision artifacts.
- M16 phase 1 hardware portability with explicit `auto`, `cpu`, `mps`, and
  `cuda` device selection across ML commands.
- Hardware-aware run manifests, synchronized BC timing and throughput metrics,
  accelerator inspection, and CPU/MPS PPO and CTDE smoke coverage.

## [1.1.0] - 2026-07-28

### Added

- M12 balanced interleaved CTDE training with validation-gated cycles,
  pairwise seed-isolation checks and CI smoke coverage.
- M13 model cards and integrity-checked model listing, download and
  verification.
- Model registry cards with promotion provenance, integrity state, model-card
  links and one-click verified download.
- Matched-seed Arena leagues with round-robin rankings, confidence intervals
  and survival metrics.
- Versioned JSON evaluation artifacts exposed through the browser, HTTP API
  and automation-friendly CLI.
- M14 hierarchical return, deposit and recharge control with validation-only
  parameter selection and a fresh six-scenario audit.
- The immutable `models-v2` catalog with a machine-readable manifest.

### Scientific results

- M12 raised harsh-weather survival from 6.5% to 27.75% and large-map survival
  from 60.25% to 86.25%, but was correctly rejected for failing declared
  scarce-resource and survival gates.
- M14 achieved 100% bee survival and 0% invalid actions across all six final
  scenarios.
- M14 median honey was 148.47% of Assignment and its worst ratio was 101.16%
  under scarce nectar, passing every predeclared promotion gate.

## [1.0.1] - 2026-07-25

### Added

- Apache License 2.0 terms and an explicit project copyright notice.

## [1.0.0] - 2026-07-24

### Added

- Deterministic multi-agent bee ecosystem with seeded weather and resources.
- Random, Greedy, Scout and centralized Assignment rule baselines.
- Behavior cloning, DAgger, PPO and local-observation CTDE workflows.
- Decentralized harvest-intent reservations with zero unresolved contention in
  the accepted M8 evaluation.
- Configuration-driven training, evaluation, promotion and audit pipelines.
- Model registry with artifact digest verification.
- Cross-distribution robustness and curriculum-training audits.
- Side-by-side Strategy Arena with matched seeds, live metrics and replay.
- English and Chinese responsive user interface.
- Core and end-to-end ML smoke coverage in GitHub Actions.

### Scientific results

- M8 coordinated CTDE improved over local behavior cloning by +6.19 honey per
  matched seed, with a 95% confidence interval of [+3.41, +8.97].
- M8 reduced invalid actions from 0.742% to 0% and was promoted.
- M10 and M11 robustness candidates were rejected and recorded rather than
  promoted after failing scarce-resource and harsh-weather gates.

### Known limitations

- Learned checkpoints and experiment bundles are generated artifacts and are
  not stored directly in Git.
- The local HTTP server is an experimentation interface, not a hardened
  multi-user production service.

[Unreleased]: https://github.com/alanthssss/sweetgold/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/alanthssss/sweetgold/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/alanthssss/sweetgold/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/alanthssss/sweetgold/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/alanthssss/sweetgold/releases/tag/v1.0.0
