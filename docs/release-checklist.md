# v1.2.0 release checklist

[English](release-checklist.md) | [简体中文](release-checklist.zh-CN.md)

## Source readiness

- [x] Version is `1.2.0` in `VERSION` and `beehive.__version__`.
- [x] CLI reports `sweetgold 1.2.0`.
- [x] Changelog and release notes cover M15, M16, documentation, and Pages.
- [x] English and Chinese release documents have matching structure.
- [x] Apache-2.0 remains the project and promoted-model license.
- [x] No new model is claimed; M14 and `models-v2` remain authoritative.

## Verification

- [x] Python sources compile and dependency-free tests pass.
- [x] M6–M12, M14, and hardware-device smoke paths are represented in CI.
- [x] M6 BC+PPO and M7 CTDE complete locally on Apple MPS.
- [x] Explicit unavailable CUDA requests fail without fallback.
- [ ] Required GitHub Actions checks pass on the merged release commit.
- [x] A clean clone passes core tests and reports version `1.2.0`.
- [x] All three promoted checkpoints download and verify from public releases.
- [x] English and Chinese GitHub Pages routes serve the release presentation.

## Release actions

- [ ] Create tag `v1.2.0` from the merged release commit.
- [ ] Create the GitHub Release using `docs/releases/v1.2.0.md`.
- [ ] Mark v1.2.0 as the latest release.
- [ ] Verify tag, source archives, Pages, model links, and quick-start commands.

## Post-release status

New feature development is paused after v1.2.0. AWS CUDA validation remains an
optional, budget-gated compatibility exercise rather than a release blocker.
Resume research only with a specific question, predeclared gates, and fresh
evaluation seeds where applicable.

## Ownership note

SweetGold and its promoted model assets are licensed under Apache-2.0.
Copyright 2026 alanthssss.
