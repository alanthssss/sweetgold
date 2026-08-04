# SweetGold 宣传站 / Launch site

[English / 双语说明](README.md) | [简体中文](README.zh-CN.md)

## 简体中文

这是 SweetGold 的中英双语宣传站，英文首页位于 `/`，等价中文首页位于 `/zh`。两页使用
同一视觉系统、相同实验指标和相同功能入口。技术词第一次出现时保留英文原词，便于对照学习。

```bash
npm install
npm run dev
npm test
```

需要 Node.js 22.13 或更高版本。`.openai/hosting.json` 保存 Sites 项目和可选 D1/R2
逻辑绑定；站点目前不使用数据库、上传或登录。`npm test` 构建生产产物，并验证两种语言、
M14/M15 阶段说明和社交元数据。

## English

This is the bilingual SweetGold launch site. `/` is the English page and
`/zh` is its equal Chinese counterpart. Both routes present the same visual
system, evidence, milestones and actions; first-use Chinese technical terms
retain their English equivalents for learning.

Requires Node.js 22.13+. Run `npm install`, `npm run dev`, and `npm test`.
The hosting manifest stores the Sites project and optional logical bindings;
the current public-information site uses no database, uploads or sign-in.
