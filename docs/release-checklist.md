# v1.1.0 release checklist

[English](release-checklist.md) | [简体中文](release-checklist.zh-CN.md)

## Source readiness

- [x] Version is `1.1.0` in `VERSION` and `beehive.__version__`.
- [x] CLI reports `sweetgold 1.1.0`.
- [x] Changelog and release notes cover M12–M14 and Arena workflows.
- [x] Apache-2.0 remains the project and promoted-model license.
- [x] `models-v2` is public with a manifest and exact asset digests.

## Verification

- [x] Python sources compile.
- [x] Dependency-free unit tests pass.
- [x] M6–M12 and M14 smoke pipelines are represented in CI.
- [x] `hierarchical-return-ctde` downloads and verifies from a clean location.
- [x] Arena loads the registered M14 controller and writes evaluation artifacts.

## Post-merge release actions

- [ ] Confirm required GitHub Actions checks pass on `main`.
- [ ] Test a clean clone against the merged release commit.
- [ ] Create tag `v1.1.0` from the merged release commit.
- [ ] Create the GitHub Release using `docs/releases/v1.1.0.md`.
- [ ] Verify the tag, source archives and model links are publicly accessible.

## Ownership note

SweetGold and its promoted model assets are licensed under Apache-2.0.
Copyright 2026 alanthssss.
