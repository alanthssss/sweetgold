# SweetGold 中英术语表 / Bilingual glossary

[English / 双语主表](glossary.md) | [简体中文入口](glossary.zh-CN.md)

| English | 中文 | 在 SweetGold 中的含义 |
| --- | --- | --- |
| agent | 智能体 | 独立观察环境并选择动作的实体；通常是一只蜜蜂或一个决策工作流。 |
| policy | 策略 | 把观察映射成动作的规则或神经网络。 |
| controller | 控制器 | 实现统一动作接口的策略对象，可为规则型或学习型。 |
| baseline | 基线 | 用来判断新策略是否真的改善的参照方法。 |
| deterministic | 确定性 | 给定相同初始状态、种子和动作时，结果可重复。 |
| random seed | 随机种子 | 控制伪随机过程的整数；相同种子产生相同随机序列。 |
| matched seed | 配对种子 | 两个策略使用完全相同的回合种子，减少环境运气造成的偏差。 |
| train / validation / test | 训练 / 验证 / 测试 | 学习参数、选择模型、最终评估三个必须隔离的数据阶段。 |
| seed leakage | 种子泄漏 | 最终测试种子被训练或选型提前使用，导致结果虚高。 |
| behavior cloning (BC) | 行为克隆 | 用监督学习模仿教师策略的动作。 |
| DAgger | 数据集聚合 | 让学习者访问状态，再由教师标注这些状态以减少分布偏移。 |
| reinforcement learning (RL) | 强化学习 | 智能体通过奖励信号学习策略。 |
| PPO | 近端策略优化 | 使用裁剪目标稳定更新策略的一种强化学习算法。 |
| actor / critic | 行动者 / 评论家 | Actor 选动作；Critic 估计状态或动作的长期价值。 |
| CTDE | 集中训练、分散执行 | 训练时评论家可看全局信息，部署时各行动者只看局部信息。 |
| local observation | 局部观察 | 单只蜜蜂可见范围内的花、蜜蜂和信号，而非整个地图。 |
| action masking | 动作屏蔽 | 在选择动作前排除当前不合法的动作。 |
| robustness | 鲁棒性 | 环境发生距离、资源、天气或能量变化时仍保持可接受表现。 |
| distribution shift | 分布变化 | 测试环境与常规训练环境不同。 |
| promotion gate | 晋级门槛 | 模型进入注册表前必须通过的预先声明指标条件。 |
| confidence interval (CI) | 置信区间 | 表示配对改善估计的不确定范围；这里通常使用 95% 区间。 |
| model registry | 模型注册表 | 保存已接受模型身份、指标、来源、许可证和完整性信息的清单。 |
| checkpoint | 检查点 / 权重文件 | 某个训练时刻保存的模型参数。 |
| SHA-256 digest | SHA-256 摘要 | 用于确认下载文件没有损坏或被替换的内容指纹。 |
| immutable artifact | 不可变产物 | 一旦记录便不应静默修改的配置、报告、模型或运行证据。 |
| Strategy Arena | 策略竞技场 | 同种子并排执行、比较和回放策略的交互产品。 |
| auditable | 可审计 | 输入、约束、淘汰原因、结果和来源证据都能被检查。 |
| hierarchical control | 分层控制 | 高层安全规则在特定条件下接管低层学习策略。 |
| maintenance mode | 维护模式 | 暂停新特性，只接受关键修复、兼容性和文档工作。 |
