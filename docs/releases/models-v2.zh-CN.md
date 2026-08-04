# SweetGold 晋级模型 v2 / Promoted models

[English](models-v2.md) | [简体中文](models-v2.zh-CN.md)

`models-v2` 是第二个不可变模型目录，新增首个通过跨分布审计的
`hierarchical-return-ctde`，同时保留两个 v1 检查点。

## 新晋级策略

M14 把已接受的协调式 CTDE 行动者与确定性的返航、存蜜和充能监督器结合。在六种场景
各 50 个全新最终种子上达到：所有场景 100% 蜜蜂存活、0% 无效动作；蜂蜜中位数为
Assignment 的 148.47%；最差稀缺花蜜场景为 101.16%；恶劣天气为 141.46，对照 99.48。
选中参数为安全余量 6、充能比例 0.8。

## 共享权重

`hierarchical-return-ctde.pt` 与 `coordinated-ctde.pt` 的 SHA-256 相同是有意设计。
M14 没有重训或静默修改神经网络；新策略身份是共享权重加有版本监督器代码和注册参数。

## 文件与校验

发布包含三个模型名称、Apache-2.0、`models-v2-manifest.json`，清单声明字节数、摘要、
模型卡和控制参数。使用 `python main.py models download` 和 `models verify` 安装并校验。
