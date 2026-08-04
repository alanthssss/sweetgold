# v1.2.0 发布检查表

[English](release-checklist.md) | [简体中文](release-checklist.zh-CN.md)

## 源码就绪

- [x] `VERSION` 与 `beehive.__version__` 均为 `1.2.0`。
- [x] CLI 输出 `sweetgold 1.2.0`。
- [x] 变更日志和发布说明覆盖 M15、M16、文档与 Pages。
- [x] 中英文发布文档结构一致。
- [x] 项目和晋级模型继续使用 Apache-2.0。
- [x] 不声明新模型；M14 与 `models-v2` 继续作为权威事实。

## 验证

- [x] Python 源码可编译，无依赖测试通过。
- [x] CI 覆盖 M6–M12、M14 和硬件设备冒烟路径。
- [x] M6 BC+PPO 与 M7 CTDE 已在 Apple MPS 本地完成。
- [x] 显式请求不可用 CUDA 时直接失败，不发生回退。
- [ ] 合并发布提交的必需 GitHub Actions 通过。
- [x] 干净克隆通过核心测试并输出版本 `1.2.0`。
- [x] 三个晋级检查点均可从公开 Release 下载并校验。
- [x] GitHub Pages 中英文路由均显示本次发布内容。

## 发布动作

- [ ] 从合并发布提交创建 `v1.2.0` 标签。
- [ ] 使用 `docs/releases/v1.2.0.zh-CN.md` 创建 GitHub Release。
- [ ] 将 v1.2.0 标记为 Latest Release。
- [ ] 验证标签、源码归档、Pages、模型链接和快速开始命令。

## 发布后状态

v1.2.0 后暂停新特性开发。AWS CUDA 验证仍是受预算门槛控制的可选兼容性工作，
不是发布阻塞项。只有存在具体问题、预先声明门槛，并在适用时准备全新评测种子，
才恢复研究。

## 所有权说明

SweetGold 及晋级模型使用 Apache-2.0；Copyright 2026 alanthssss。
