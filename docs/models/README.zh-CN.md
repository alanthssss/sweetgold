# SweetGold 模型产物 / Model artifacts

[English](README.md) | [简体中文](README.zh-CN.md)

已晋级的 SweetGold 检查点与 Git 仓库分开分发，以保持全新克隆体积较小。提交到仓库的
模型注册表为每个可下载文件记录发布地址、精确字节数、SHA-256 摘要、模型卡和许可证。

除非模型卡另有说明，`registry/models.json` 链接的权重版权为 Copyright 2026
alanthssss，并使用 Apache License 2.0。完整条款见仓库 `LICENSE`。

```bash
python3 main.py models list
python3 main.py models download
python3 main.py models verify
```

下载使用原子写入。只有大小和 SHA-256 都与已提交元数据相符，文件才会安装到注册表指定路径。
