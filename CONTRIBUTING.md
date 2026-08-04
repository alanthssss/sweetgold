# Contributing to SweetGold

SweetGold is currently in maintenance mode. Focused bug fixes, documentation
improvements, reproducibility fixes and small test additions are welcome. New
training architectures or product features should begin with an issue and a
clear experiment proposal before implementation.

## Development setup

The dependency-free suite requires Python 3.10 or newer:

```bash
python3 -m unittest discover -s tests -v
```

Optional learning pipelines require PyTorch dependencies from
`requirements-ml.txt`. Do not make the base simulator depend on them.

## Pull requests

1. Keep the change focused and explain its user-visible effect.
2. Add or update regression tests.
3. Preserve deterministic seeds and existing artifact schemas.
4. Never tune on a final evaluation seed range.
5. Record meaningful behavior changes in `CHANGELOG.md`.

For model work, declare success and safety gates before the final evaluation.
Rejected candidates and negative results are part of the project record.
