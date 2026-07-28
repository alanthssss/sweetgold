# SweetGold model artifacts

Promoted SweetGold checkpoints are distributed separately from the Git
repository so a fresh clone stays small. The committed model registry records
the release URL, exact byte size, SHA-256 digest, model card and license for
every downloadable artifact.

Unless a model card states otherwise, weights linked from
`registry/models.json` are copyright 2026 alanthssss and licensed under the
Apache License 2.0. The repository `LICENSE` contains the complete terms.

Download and verify all registered models:

```bash
python3 main.py models list
python3 main.py models download
python3 main.py models verify
```

Downloads are written atomically to the artifact path in the registry. A file
is never installed unless its size and SHA-256 digest match the committed
metadata.
