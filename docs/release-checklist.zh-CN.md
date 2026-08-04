# v1.1.0 发布检查表

[English](release-checklist.md) | [简体中文](release-checklist.zh-CN.md)

## 源码就绪

- [x] `VERSION` 与 `beehive.__version__` 均为 `1.1.0`。
- [x] CLI 输出 `sweetgold 1.1.0`。
- [x] Changelog 和发布说明覆盖 M12–M14 与 Arena 工作流。
- [x] 项目和晋级模型继续使用 Apache-2.0。
- [x] `models-v2` 已公开，包含清单和精确摘要。

## 验证

- [x] Python 源码可编译。
- [x] 无依赖单元测试通过。
- [x] CI 覆盖 M6–M12 和 M14 冒烟流水线。
- [x] `hierarchical-return-ctde` 可从干净位置下载并校验。
- [x] Arena 可加载 M14 控制器并写出评测产物。

## 合并后发布动作

- [ ] 确认 `main` 的必需 GitHub Actions 通过。
- [ ] 对合并提交执行干净克隆测试。
- [ ] 从合并发布提交创建 `v1.1.0` 标签。
- [ ] 使用 `docs/releases/v1.1.0.zh-CN.md` 创建 GitHub Release。
- [ ] 确认标签、源码归档和模型链接公开可用。

## 所有权说明

SweetGold 及晋级模型使用 Apache-2.0；Copyright 2026 alanthssss。
