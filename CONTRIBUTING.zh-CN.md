# 为 SweetGold 贡献 / Contributing

[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

SweetGold 目前处于维护模式。欢迎聚焦明确的缺陷修复、文档改进、可复现性修复和小型
测试补充。新训练架构或产品特性应先创建 Issue，明确研究问题和实验方案，再开始实现。

## 开发环境

无第三方依赖的测试套件需要 Python 3.10 或更高版本：

```bash
python3 -m unittest discover -s tests -v
```

可选学习流水线需要 `requirements-ml.txt` 中的 PyTorch 依赖。不要让基础模拟器依赖它们。

## Pull Request 要求

1. 保持改动聚焦，并说明用户可见影响。
2. 新增或更新回归测试。
3. 保持确定性种子和已有产物格式兼容。
4. 禁止使用最终评测种子调参。
5. 行为发生实质变化时更新 `CHANGELOG.md`。

模型工作必须在最终评测前声明成功和安全门槛。被拒绝的候选和负面结果同样属于项目记录。
