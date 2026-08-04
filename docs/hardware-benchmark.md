# Hardware portability and benchmark

[English](hardware-benchmark.md) | [简体中文](hardware-benchmark.zh-CN.md)

## M16 phase 1 status

M16 adds hardware-aware reproducibility without changing the promoted M14
policy or the M15 decision workflow. The first phase is complete:

- every ML command accepts `--device auto|cpu|mps|cuda`;
- `auto` prefers CUDA, then Apple MPS, then CPU;
- explicitly requested unavailable accelerators fail instead of falling back;
- M6–M14 run metadata records the requested and selected backend, device name,
  architecture, Python, PyTorch, and available accelerators;
- BC metrics record accelerator-synchronized training time, throughput, and
  CUDA peak memory when available;
- M6 BC+PPO and M7 CTDE smoke workflows complete on Apple MPS.

## Inspect and select hardware

```bash
.venv-ml/bin/python main.py hardware --device auto
.venv-ml/bin/python main.py pipeline --config experiments/smoke.json --device mps
```

`cpu`, `mps`, and `cuda` are explicit reproducibility choices. `auto` is a
convenience for local work and should not replace a declared backend in formal
cross-hardware comparisons.

## Initial Apple M1 Pro result

An exploratory BC smoke benchmark used one fixed 20-episode dataset, three
epochs, PyTorch 2.13.0, and the same code and hyperparameters on both backends.

| Backend | Training time | Training throughput | Validation accuracy | Test accuracy |
| --- | ---: | ---: | ---: | ---: |
| M1 Pro CPU | 0.5774 s | 138,355 examples/s | 50.50% | 48.96% |
| M1 Pro MPS | 3.6764 s | 21,730 examples/s | 49.34% | 48.57% |

This is a workload-sizing result, not a general CPU-versus-GPU claim. The small
network and batches do not amortize accelerator dispatch overhead; CPU was
about 6.4× faster in this smoke run. Small numerical differences across
backends are expected and did not prevent the MPS pipelines from completing.

## Cloud decision gate

AWS CUDA work is deferred until profiling demonstrates a suitable workload.
Use cloud GPU resources only when at least one condition is met:

- neural-network training dominates end-to-end runtime;
- larger batches or parallel environments keep the accelerator occupied;
- a formal CUDA compatibility result is needed for a release;
- projected time-to-result or cost-to-result improves over the M1 CPU baseline.

The next optional phase is a short, budget-capped single-GPU CUDA run with the
same dataset and manifest contract. It is not required to close the current
feature-development cycle.
