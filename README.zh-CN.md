# SweetGold

[English](README.md) | [简体中文](README.zh-CN.md)

<p align="center">
  <img src="docs/assets/sweetgold-social.png" alt="SweetGold：训练蜂群在未知环境中生存" width="100%">
</p>

<p align="center"><strong>一个让策略用证据赢得晋级的可复现多智能体 AI 实验室。</strong></p>

<p align="center">
  <a href="https://github.com/alanthssss/sweetgold/actions"><img src="https://github.com/alanthssss/sweetgold/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-f4b942.svg" alt="Apache 2.0 许可证"></a>
  <a href="https://github.com/alanthssss/sweetgold/releases/tag/v1.2.0"><img src="https://img.shields.io/badge/release-v1.2.0-0d110f.svg" alt="v1.2.0"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-83d7aa.svg" alt="Python 3.10+">
</p>

SweetGold 同时包含确定性蜂群模拟器（deterministic bee-colony simulator）、
配对种子基准（matched-seed benchmark）和交互式策略竞技场（Strategy Arena）。
它支持行为克隆（Behavior Cloning）、PPO 和集中训练分散执行（CTDE），并严格隔离
训练、验证和最终测试种子。

<!-- section:start-here -->
## 第一次接触？从这里开始

SweetGold 最初是一个小游戏：虚拟蜜蜂移动、采集花蜜、返巢存蜜，并在季节结束前充能。
真正研究的问题是，多个独立智能体怎样在各自行动的同时形成可靠的蜂群协作。

如果 PPO、CTDE、晋级门槛或配对种子这些词对你还很陌生，请先读
**[从这里开始：零基础理解 SweetGold](docs/getting-started.zh-CN.md)**。它不预设 AI
背景，并为普通访客、ML 从业者以及 DevOps/MLOps 读者提供不同的阅读路线。

<!-- section:current-project-stage -->
## 当前项目阶段：M16

M16 第一阶段增加硬件可移植的 ML 执行与证据。所有 ML 命令现在都能明确选择 CPU、
Apple MPS 和 NVIDIA CUDA；运行清单记录硬件后端，不可用加速器不会静默回退。
M6 BC+PPO 和 M7 CTDE 冒烟工作流均可在 Apple M1 Pro GPU 上完成。

第一轮本地基准显示，小型 BC 工作负载在 M1 Pro CPU 上约比 MPS 快 6.4 倍，因此在
profiling 证明有必要前暂缓 AWS CUDA。详见[硬件基准](docs/hardware-benchmark.zh-CN.md)。

<!-- section:latest-completed-outcome -->
## 最新完成产品工作流：M15

M15 是当前项目阶段。它把 Arena 证据转化成明确、可审计的策略决策；它不会训练或替换底层策略。

| M15 工作流能力 | 已交付结果 |
| --- | --- |
| 决策目标 | `balanced`（平衡）、`yield`（产量）和 `safety`（安全） |
| 安全约束 | 最低蜜蜂存活率和最大无效动作率 |
| 决策行为 | 确定性推荐，或明确返回“没有合格策略” |
| 决策证据 | 链接 Arena 原始产物，同时输出机器可读 JSON 和人类可读 Markdown |

M15 第一阶段已经进入 `main`。项目目前暂停新特性开发，重点转向维护、文档和发布。

<!-- section:latest-promoted-policy -->
## 最新晋级策略：M14

因为 M15 负责从已有策略中选择，M14 `hierarchical-return-ctde` 仍是最近一个
拥有正式跨分布性能结果的策略。

| M14 在未使用最终种子上的结果 | 结果 |
| --- | ---: |
| 六种场景中的最低蜜蜂存活率 | **100%** |
| 最大无效动作率 | **0%** |
| 相对 Assignment 的蜂蜜中位数 | **148.47%** |
| 相对 Assignment 的最差场景蜂蜜 | **101.16%** |

> M14 在六种环境分布中各使用 50 个从未参与训练或选型的最终种子。完整范围与方法见
> [M14 模型卡](docs/models/hierarchical-return-ctde.zh-CN.md)和
> [v1.1.0 发布说明](docs/releases/v1.1.0.zh-CN.md)。

<!-- section:why-sweetgold -->
## 为什么做 SweetGold？

- **同一个世界，不同的思维。** 策略从完全相同的世界和随机种子出发，实时比较并逐帧回放。
- **失败仍然是证据。** M10–M12 没通过预先声明的鲁棒性门槛；审计记录被完整保留，
  并推动了 M14 的结构性改变。
- **从结构上保证可复现。** 种子清单、泄漏检查、不可变产物、置信区间和
  SHA-256 模型校验都内置于工作流。
- **没有 ML 环境也能运行。** 模拟器、规则策略、基准和网页 Arena 只需 Python 3.10+，
  不依赖第三方包。

<!-- section:quick-start -->
## 快速开始

```bash
git clone https://github.com/alanthssss/sweetgold.git
cd sweetgold
python3 main.py play --port 8080
```

浏览器打开 <http://127.0.0.1:8080>。生成 30 回合配对种子报告：

```bash
python3 main.py benchmark --episodes 30 --report report
```

列出、下载和校验已晋级模型：

```bash
python3 main.py models list
python3 main.py models download
python3 main.py models verify
```

运行 M15 可审计建议工作流：

```bash
python3 main.py arena-agent \
  --strategies assignment greedy scout \
  --objective balanced \
  --min-bee-survival 0.9 \
  --max-invalid-action-rate 0.01 \
  --episodes 10 --seed 42
```

小规模联赛只用于演示工作流，不能替代正式的跨分布鲁棒性审计。

<!-- section:products -->
## 三个产品层

### BeeSim — 蜂群模拟器

这是由地形、可再生花丛、蜂巢、蜜蜂和随机天气组成的种子化世界。
`BeeEnv.observe()` 输出 JSON 兼容状态，`BeeEnv.step()` 接受“蜜蜂 ID → 动作”的映射，
因此学习适配器不需要修改环境核心。

### BeeBench — 配对种子评测

控制器在相同回合种子上运行。报告包含蜂蜜、群体与个体存活率、能量效率、覆盖率、
死亡数、无效动作率和决策延迟，并提供配对置信区间。

### Strategy Arena — 交互式策略比较

Arena 发现已注册的规则与学习策略，加载前验证模型 SHA-256，在相同世界中运行策略并
保存每一帧。M15 把联赛证据转化成受约束、可追溯的建议。

<!-- section:engineering-guarantees -->
## 工程保障

SweetGold 把可复现性和模型交付当作产品能力，而不是实验结束后补写的规范。

| 实践 | 强制行为 |
| --- | --- |
| 确定性执行 | 种子化环境和配对回合让策略比较可以重复。 |
| 数据隔离 | 执行前展开训练、内部验证、模型选择和最终测试种子，并检查泄漏。 |
| 策略即代码的晋级 | 置信度、产量、存活、无效动作和场景门槛声明在有版本的实验配置中。 |
| 可审计证据 | 运行包用机器可读格式保存配置、提交、运行环境、种子清单、指标、决策和源产物链接。 |
| 经验证的模型供应链 | 不可变发布地址、精确大小、SHA-256、许可证、模型卡和原子安装保护分发的检查点。 |
| 自动化回归保护 | CI 运行无依赖测试和端到端 ML 冒烟流水线；失败候选继续保留在审计注册表。 |

这些是企业级工程实践，但不代表本地 HTTP 服务器是经过加固的多用户生产服务。
事实来源和运行边界见[交接指南](HANDOFF.zh-CN.md)。

<!-- section:research-journey -->
## 研究历程

| 里程碑 | 结果 |
| --- | --- |
| M2–M3 | 建立 Assignment 确定性基线，并改善动态编队能效。 |
| M4 | 行为克隆 + DAgger；测试集达到教师蜂蜜的 97%。 |
| M5–M6 | 加入从 BC 初始化的 PPO，以及端到端选型和晋级流水线。 |
| M7 | 局部观察 CTDE 优于局部 BC，但没有通过 1% 无效动作门槛。 |
| M8 | 意图广播和轮换优先级解决资源争用；候选通过门槛。 |
| M9 | 加入同种子 Strategy Arena 比较、指标和回放。 |
| M10–M12 | 三次鲁棒性审计没有通过既定稀缺/天气门槛，失败被完整保留。 |
| M13 | 分离模型元数据与大文件，加入不可变地址和 SHA-256 校验。 |
| M14 | 加入分层返航监督器；六种最终场景全部通过。 |
| M15 | 加入含目标、约束和证据链接的可审计决策工作流。 |

完整方法与失败分析请阅读[产品与研究设计](docs/product-design.zh-CN.md)。

<!-- section:optional-ml-pipelines -->
## 可选 ML 流水线

学习功能需要 `requirements-ml.txt` 中的 PyTorch 依赖。代表性的端到端入口为：

```bash
.venv-ml/bin/python main.py pipeline --config experiments/m6-bc-ppo.json
.venv-ml/bin/python main.py pipeline-m8 --config experiments/m8-coordination.json
.venv-ml/bin/python main.py pipeline-m14 --config experiments/m14-hierarchical-return.json
```

流水线在执行前展开并校验种子集合，防止训练、验证、选型和最终测试之间发生泄漏。
生成的数据集、权重和运行目录不进入 Git。环境配置、命令、产物和验收门槛见
[交接指南](HANDOFF.zh-CN.md)。

<!-- section:documentation -->
## 文档导航

| 主题 | 文档 |
| --- | --- |
| 零背景项目介绍与分类阅读路线 | [从这里开始](docs/getting-started.zh-CN.md) |
| 实际意义、客户假设、优劣势与商业化门槛 | [实际意义与路线](docs/impact-and-roadmap.zh-CN.md) |
| 产品架构与 M2–M16 研究记录 | [产品与研究设计](docs/product-design.zh-CN.md) |
| CPU、MPS、CUDA 与云资源决策证据 | [硬件可移植性与基准](docs/hardware-benchmark.zh-CN.md) |
| 环境、命令、产物与门槛 | [交接指南](HANDOFF.zh-CN.md) |
| 已晋级检查点与证据 | [模型目录](docs/models/README.zh-CN.md) |
| 已发布结果与方法 | [发布说明](docs/releases/v1.2.0.zh-CN.md) |
| 新技术术语 | [中英术语表](docs/glossary.md) |
| 贡献与项目运行 | [贡献指南](CONTRIBUTING.zh-CN.md) · [维护模式](MAINTENANCE.zh-CN.md) · [安全策略](SECURITY.zh-CN.md) |

<!-- section:license -->
## 许可证

SweetGold 源代码使用 [Apache License 2.0](LICENSE)。单独分发的模型和数据集可能有各自条款。
