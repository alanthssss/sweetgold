# v1.0.1 release checklist

## Source readiness

- [x] Version is `1.0.1` in `VERSION` and `beehive.__version__`.
- [x] CLI reports `sweetgold 1.0.1`.
- [x] Changelog and release notes describe the licensing change.
- [x] The official Apache License 2.0 text is included in `LICENSE`.
- [x] `NOTICE` identifies the copyright owner.
- [x] README states the repository license and separates future model and
  dataset licensing.

## Verification

- [x] Apache License text matches the official source.
- [x] Python sources compile.
- [x] Dependency-free unit tests pass.
- [x] M6, M7, M8, M10 and M11 smoke pipelines remain represented in CI.

## Post-merge release actions

- [ ] Confirm required GitHub Actions checks pass on `main`.
- [ ] Create annotated tag `v1.0.1` from the merged release commit.
- [ ] Create the GitHub Release using `docs/releases/v1.0.1.md`.
- [ ] Verify the release tag and source archives are publicly accessible.

## Ownership note

SweetGold is licensed under the Apache License 2.0. Copyright 2026
alanthssss. Separately distributed model checkpoints and datasets may carry
their own license terms.
