# SweetGold 晋级模型 v1 / Promoted models

[English](models-v1.md) | [简体中文](models-v1.zh-CN.md)

该发布分发首批通过预先声明晋级门槛的两个 SweetGold 检查点，版权为 Copyright 2026
alanthssss，使用 Apache License 2.0。

## 文件

| 文件 | 注册表 ID | 大小 | SHA-256 |
| --- | --- | ---: | --- |
| `bc-ppo.pt` | `bc-ppo` | 78,025 字节 | `441e1770146962dd963df6f1b699c57b186a03c043e6d691a358f51911158f1d` |
| `coordinated-ctde.pt` | `coordinated-ctde` | 68,065 字节 | `86fd605a1f013638ea89e95e1a71b65c0da243c003b7b22cf90e27dfe4397a68` |

源码归档包含完整 Apache-2.0 许可证和模型卡。已提交注册表是模型身份、下载地址、
本地产物路径和摘要之间的权威映射。

## 安装

```bash
python3 main.py models download
python3 main.py models verify
```

执行学习策略需要可选 PyTorch 依赖，下载和校验不需要。

## 适用范围

`bc-ppo` 和 `coordinated-ctde` 只通过原始同分布晋级门槛。M10–M12 证明两者都不能被
描述为普遍鲁棒或生产控制策略。预期用途与限制见关联模型卡和审计注册表。
