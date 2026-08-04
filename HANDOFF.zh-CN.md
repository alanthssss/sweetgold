# SweetGold 交接记录

[English](HANDOFF.md) | [简体中文](HANDOFF.zh-CN.md)

## 当前状态

M16 是当前工程里程碑；第一阶段提供 CPU/MPS/CUDA 设备选择、硬件感知运行清单和本地
CPU/MPS 证据。M14 仍是最新晋级策略，M15 仍是最新完成产品工作流。AWS CUDA 在出现
工作负载依据前暂缓。M16 文档和可移植性工作结束后，项目重新进入维护模式。

## 里程碑与正式结论

| 里程碑 | 已完成内容 | 决策与证据 |
| --- | --- | --- |
| M2 | 集中式 Assignment 预约、存活与无效动作指标、100 种子报告 | 蜂蜜 161.23，蜜蜂存活 94.25%，无效动作 0%；确定性基线建立。 |
| M3 | 前半季保留两只蜜蜂，后半季扩编 | 能效约提高 10%，蜂蜜约下降 2.9%；接受为测试过的最佳平衡。 |
| M4 | BC、类别权重、种子隔离、一次 DAgger | 30 个测试种子上蜂蜜 136.10，为教师 97.0%；第二次 DAgger 因在线退化被拒绝。 |
| M5 | BC 初始化 PPO、GAE、裁剪更新、评论家、验证选型 | 100 个测试种子比 BC 多 +8.19 蜂蜜，95% CI [+3.69, +12.69]；随机初始化蜂蜜为 0。 |
| M6 | 一键流水线、泄漏检查、运行包、门槛晋级、CI | 最终测试不参与选型；只有置信度、质量和安全门槛全部通过才写注册表。 |
| M7 | 半径 4 局部观察、全局训练评论家、四工作线程 CTDE | 比局部 BC 多 +6.60 蜂蜜，但 1.056% 无效动作超过 1% 门槛；拒绝。 |
| M8 | 本地采集意图广播、轮换优先预约 | 蜂蜜 +6.19，避免 13.51 次冲突，无效动作和未解决冲突为 0；通过并注册。 |
| M9 | 双策略 Arena、相同世界、实时指标、服务器回放 | 学习依赖可选；摘要不符时禁用模型，不影响规则策略。 |
| M10 | 六场景跨分布审计 | 稀缺花蜜产量 74.68%，大地图存活 50.25%，恶劣天气 7.75%；失败。 |
| M11 | 五阶段顺序课程和多场景选型 | 最终恶劣天气存活 6.5%，最差产量 69.85%；失败并记录。 |
| M12 | 平衡交错训练和五个门控周期 | 大地图存活 86.25%，恶劣天气 27.75%，稀缺花蜜产量 73.65%；仍失败。 |
| M13 | 不可变模型地址、大小、SHA-256、许可证和模型卡 | `models list/download/verify` 无需重训即可分发晋级模型。 |
| M14 | M8 行动者上方增加返航、存蜜、充能监督器 | 六场景各 50 个全新种子：100% 存活、0% 无效动作、蜂蜜中位数 148.47%、最差 101.16%；全部通过。 |
| M15 | Arena 联赛 + 明确目标 + 安全约束 + 确定性推荐 | JSON 和 Markdown 证据包含合格集、拒绝原因、约束和源 Arena 产物；第一阶段完成。 |
| M16 | 明确选择 CPU/MPS/CUDA、硬件清单、同步计时和加速器冒烟覆盖 | M6、M7 已在 MPS 完成；小型 BC 在 M1 Pro CPU 上约比 MPS 快 6.4 倍，因此暂缓 AWS。 |

完整的产品理由、实验设计和失败过程见[产品与研究设计](docs/product-design.zh-CN.md)。
晋级证据见[模型目录](docs/models/README.zh-CN.md)和[发布说明](docs/releases/v1.1.0.zh-CN.md)。

## 复现维护中的工作流

核心模拟、基准、Arena 和 M15 决策工作流只需要 Python 3.10+：

```bash
python3 -m unittest discover -s tests -v
python3 main.py benchmark --episodes 30 --controllers greedy assignment --report report
python3 main.py play --port 8080
python3 main.py arena-agent --strategies assignment greedy scout --objective balanced --episodes 10 --seed 42
```

晋级模型可以与训练分开管理：

```bash
python3 main.py models list
python3 main.py models download
python3 main.py models verify
```

可选学习工作流需要 `requirements-ml.txt`。代表性的正式流水线为：

```bash
.venv-ml/bin/python main.py pipeline --config experiments/m6-bc-ppo.json
.venv-ml/bin/python main.py pipeline-m8 --config experiments/m8-coordination.json
.venv-ml/bin/python main.py pipeline-m14 --config experiments/m14-hierarchical-return.json
```

## 产物与事实来源

| 证据 | 位置 |
| --- | --- |
| 晋级模型身份、本地路径、摘要和参数 | `registry/models.json` |
| 失败与通过的正式审计 | `registry/audits.json` |
| 实验定义和种子范围 | `experiments/*.json` |
| Arena 联赛与 M15 决策产物 | `runs/arena/` 和配置的运行目录 |
| 人类可读的策略证据 | `docs/models/` 和 `docs/releases/` |

生成的数据集、权重、虚拟环境和运行包不进入 Git。注册表元数据和已提交报告是持久记录；
本地生成文件不会自动成为权威事实。

## 已消费的评测数据

M7、M8、M10、M11、M12、M14 的正式最终种子均已消费。未来研究必须分配全新的验证与
最终范围。不能根据这些结果调参、用最终种子选型，或看到结果后放宽门槛。

## 模型与版本

- v1.0.0：完整多智能体实验与 Arena 产品。
- v1.0.1：明确 Apache-2.0 许可证。
- v1.1.0：M12–M14、模型分发、联赛和评测产物。
- `models-v1`：`bc-ppo`、`coordinated-ctde`。
- `models-v2`：增加 `hierarchical-return-ctde`；它与 M8 共享权重，新身份由监督器代码和参数定义。
- M15 属于 v1.2 开发线，但 UI 和多场景决策扩展目前暂停。
- M16 第一阶段已在本地完成；预算受限的 CUDA 运行是可选项，不是返回维护模式的前置条件。

## 维护模式下的下一步

只接受关键缺陷、安全、兼容性、可复现性、文档和发布工作。恢复特性开发前必须提出具体
研究问题、预先声明门槛，并预留未使用的最终种子。小规模 Arena 联赛不得包装成正式鲁棒性审计。
