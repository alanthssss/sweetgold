# 硬件可移植性与基准

[English](hardware-benchmark.md) | [简体中文](hardware-benchmark.zh-CN.md)

## M16 第一阶段状态

M16 增加硬件感知的可复现性，不改变已晋级 M14 策略或 M15 决策工作流。第一阶段已经完成：

- 所有 ML 命令接受 `--device auto|cpu|mps|cuda`；
- `auto` 按 CUDA、Apple MPS、CPU 的顺序选择；
- 显式请求不可用加速器时直接失败，不静默回退；
- M6–M14 运行元数据记录请求和选中的后端、设备名称、架构、Python、PyTorch 与可用加速器；
- BC 指标记录经过加速器同步的训练时间、吞吐量，以及可用时的 CUDA 峰值显存；
- M6 BC+PPO 和 M7 CTDE 冒烟工作流均可在 Apple MPS 上完成。

## 检查与选择硬件

```bash
.venv-ml/bin/python main.py hardware --device auto
.venv-ml/bin/python main.py pipeline --config experiments/smoke.json --device mps
```

`cpu`、`mps`、`cuda` 是明确的可复现选择。`auto` 方便本地工作，但正式跨硬件比较应声明后端。

## Apple M1 Pro 初步结果

探索性 BC 冒烟基准使用同一份固定的 20 回合数据集、三个 epoch、PyTorch 2.13.0，
两个后端使用完全相同的代码和超参数。

| 后端 | 训练时间 | 训练吞吐量 | 验证准确率 | 测试准确率 |
| --- | ---: | ---: | ---: | ---: |
| M1 Pro CPU | 0.5774 秒 | 138,355 样本/秒 | 50.50% | 48.96% |
| M1 Pro MPS | 3.6764 秒 | 21,730 样本/秒 | 49.34% | 48.57% |

这是工作负载规模结论，不是普遍的 CPU/GPU 性能声明。小型网络和批次不足以抵消加速器调度
开销；本次冒烟运行中 CPU 约快 6.4 倍。不同后端存在小幅数值差异，但不妨碍 MPS 流水线完成。

## 云资源决策门槛

在 profiling 证明工作负载合适前，暂缓 AWS CUDA。只有满足至少一个条件时才使用云 GPU：

- 神经网络训练占据端到端运行时间的大部分；
- 更大批次或并行环境能够持续利用加速器；
- 某次发布需要正式 CUDA 兼容性结果；
- 预计完成时间或单位结果成本优于 M1 CPU 基线。

下一可选阶段是使用相同数据集与清单契约，执行一次预算受限的单 GPU CUDA 运行。
完成当前特性开发周期并不依赖这次云端运行。
