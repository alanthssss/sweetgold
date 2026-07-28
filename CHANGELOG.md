# Changelog

## Unreleased

- Add a matched-seed Arena league with automated round-robin comparisons,
  confidence intervals, survival metrics and a bilingual leaderboard.
- Persist league requests and full results as versioned JSON artifacts exposed
  through the browser, HTTP API and an automation-friendly CLI.
- Add M14 hierarchical return control, validation-only supervisor selection,
  fresh six-scenario auditing and the first cross-distribution accepted model.

All notable SweetGold changes are documented here. The project uses semantic
versioning from v1.0.0 onward.

## [Unreleased]

### Added

- M12 balanced interleaved CTDE training with validation-gated cycles,
  pairwise seed-isolation checks and CI smoke coverage.
- M13 model cards and an integrity-checked `models list`, `models verify` and
  `models download` workflow for separately published checkpoints.
- Strategy Arena model registry cards with promotion provenance, integrity
  state, later audit failures, model-card links and verified local download.

### Scientific results

- M12 improved harsh-weather survival from M11's 6.5% to 27.75% and large-map
  survival from 60.25% to 86.25%, while retaining 0% invalid actions.
- The candidate was rejected because scarce-nectar yield reached only 73.65%
  of Assignment, below the predeclared 75% floor, and minimum survival
  remained below the 75% gate.

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
  not stored in Git; a fresh clone exposes rule strategies until checkpoints
  are reproduced locally.
- The accepted learned policy is validated for its original distribution but
  is not generally robust to large maps, scarce resources or harsh weather.
- The local HTTP server is an experimentation interface, not a hardened
  multi-user production service.
- Repository licensing remains an owner decision; this release does not add or
  imply a software license.

[Unreleased]: https://github.com/alanthssss/sweetgold/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/alanthssss/sweetgold/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/alanthssss/sweetgold/releases/tag/v1.0.0
