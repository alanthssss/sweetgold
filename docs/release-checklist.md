# v1.0.0 release checklist

## Source readiness

- [x] Version is `1.0.0` in `VERSION` and `beehive.__version__`.
- [x] CLI reports `sweetgold 1.0.0`.
- [x] Changelog and release notes describe M1–M11.
- [x] Known model and server limitations are explicit.
- [x] Failed M10 and M11 audits remain committed.
- [x] Generated data, runs, environments and checkpoints remain ignored.

## Verification

- [x] Python sources compile.
- [x] Dependency-free unit tests pass.
- [x] M6, M7, M8, M10 and M11 smoke pipelines are represented in CI.
- [x] Strategy Arena has been checked at desktop and mobile widths.
- [x] Registered artifacts are digest-verified before loading.

## Post-merge release actions

- [ ] Confirm required GitHub Actions checks pass on `main`.
- [ ] Create annotated tag `v1.0.0` from the merged release commit.
- [ ] Create the GitHub Release using `docs/releases/v1.0.0.md`.
- [ ] Verify the release tag and source archives are publicly accessible.

## Ownership note

No license is added by this release. Selecting a software license changes the
rights granted to downstream users and remains an explicit repository-owner
decision.
