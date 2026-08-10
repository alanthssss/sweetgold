import type { Metadata } from "next";
import Link from "next/link";

const github = "https://github.com/alanthssss/sweetgold";

export const metadata: Metadata = {
  title: "常见问题 — SweetGold",
  description: "面向 SweetGold 访客、学习者、研究人员、工程人员、贡献者、合作伙伴和治理团队的常见问题。",
  alternates: { languages: { en: "/faq", "zh-CN": "/zh/faq" } },
};

const groups = [
  ["01", "认识", "初次访客", [
    ["SweetGold 是什么？", "一个以种子化蜂群模拟器为参考环境、可复现且可审计的多智能体 AI 实验室。它连接模拟、训练、配对种子评测、策略晋级、验证分发和决策证据。"],
    ["它只是一个蜜蜂小游戏吗？", "不是。蜜蜂世界是一个容易理解的参考环境，用来研究多个只能看到局部信息的智能体怎样共享有限资源，并在各自行动时形成协作。"],
    ["M14、M15 和 M16 分别是什么？", "M14 是最新正式晋级策略；M15 是最新完成的受约束策略推荐工作流；M16 是支持显式 CPU、MPS 和 CUDA 执行的最新工程里程碑。"],
    ["SweetGold 是生产控制系统吗？", "不是。它是开源研究与证据基础设施。本地服务器是研究接口，真实机器人或工业使用仍需领域仿真、集成、安全、网络防护与合规证据。"],
  ]],
  ["02", "体验", "学习者与评测者", [
    ["没有 AI 背景可以使用吗？", "可以。模拟器、规则策略、基准和网页 Arena 只需 Python 3.10+。只有学习流水线才需要可选的 PyTorch 环境。"],
    ["需要先训练模型吗？", "不需要。先体验 Arena 和配对种子比较；已晋级检查点可以单独下载和验证，无需重新训练。"],
    ["一场 Arena 比赛能证明鲁棒性吗？", "不能。比赛或小型联赛适合演示与调试；正式鲁棒性结论需要预先声明门槛、隔离最终种子、足够回合和多个既定场景。"],
    ["为什么保留失败实验？", "失败揭示可靠性边界，也防止只挑选有利结果。M10–M12 未通过既定门槛，它们被完整保留，并推动了 M14 的结构性改变。"],
  ]],
  ["03", "构建", "研究人员与工程人员", [
    ["为什么使用相同随机种子？", "它让策略面对相同地图、资源和天气，就像参加同一场考试，减少运气对比较结果的影响。"],
    ["为什么不能用最终种子继续调参？", "一旦查看过最终结果，这些种子就不再是未见过的考试。新研究必须分配全新的验证和最终范围，才能保留独立证据。"],
    ["SHA-256 通过是否说明模型安全？", "不是。它只证明文件字节与登记内容一致；适用性、性能、鲁棒性、来源与许可证需要其他证据。"],
    ["当前欢迎哪些贡献？", "范围明确的缺陷、安全、兼容性、安装、可复现性、文档和回归测试改进。新架构需先有具体问题、预算、全新种子和预声明门槛。"],
  ]],
  ["04", "采用", "合作伙伴与治理团队", [
    ["可以直接控制机器人或无人机吗？", "不能。可迁移的是评测与证据工作流，而不是蜂群策略。真实系统还需要动力学、传感器、通信、集成和安全验证。"],
    ["最可信的采用路径是什么？", "先用于教育和能力建设，再把适配器式评测与晋级工具接入现有仿真器或策略来源。"],
    ["为什么“没有合格策略”也是有效答案？", "如果所有候选都违反既定约束，明确拒绝比推荐一个相对最好但仍不合格的策略更安全、更易审计。"],
    ["什么证据值得继续产品投入？", "多个用户反复出现的高成本问题、自助使用、离开 BeeSim 后仍有价值、合作伙伴投入真实资源，以及评测时间、缺陷、审批或审计成本出现可衡量下降。"],
  ]],
] as const;

export default function ChineseFAQPage() {
  return <main>
    <nav className="nav shell" aria-label="常见问题导航"><Link className="brand" href="/zh"><span className="brand-mark">SG</span><span>SweetGold</span></Link><div className="nav-links"><Link href="/zh">首页</Link><a href="#questions">问题分类</a><Link className="language-switch" href="/faq" lang="en">English</Link><a className="nav-cta" href={github}>GitHub ↗</a></div></nav>
    <header className="faq-hero shell"><p className="eyebrow"><span /> 常见问题 / FREQUENTLY ASKED QUESTIONS</p><h1>知道什么已经证实，<br /><em>也知道什么还没有。</em></h1><p className="lede">按不同参与阶段理解、体验、构建和评估 SweetGold，避免把引人入胜的演示误读成生产结论。</p><div className="faq-facts"><span>4 个参与阶段</span><span>16 个关键问答</span><span>完整参考含 55 问</span></div></header>
    <section className="faq-groups shell" id="questions">
      {groups.map(([number, title, audience, questions]) => <section className="faq-group" key={number}><div className="faq-group-heading"><span>{number}</span><div><p>{audience}</p><h2>{title}</h2></div></div><div className="faq-list">{questions.map(([question, answer]) => <details key={question}><summary>{question}<span aria-hidden="true">+</span></summary><p>{answer}</p></details>)}</div></section>)}
    </section>
    <section className="faq-reference shell"><div><p className="eyebrow"><span /> 需要完整参考？</p><h2>继续阅读全部 55 个回答。</h2><p>仓库 FAQ 还涵盖安装、硬件、权威产物、版本发布、许可证、问题分流和提问模板。</p></div><a className="button primary" href={`${github}/blob/main/docs/faq.zh-CN.md`}>阅读完整 FAQ <span>↗</span></a></section>
    <footer className="shell"><div className="footer-brand"><span className="brand-mark">SG</span><div><strong>SweetGold</strong><p>让每个策略用证据赢得晋级。</p></div></div><div className="footer-links"><Link href="/zh">首页</Link><a href={`${github}/blob/main/docs/faq.zh-CN.md`}>完整 FAQ</a><a href={github}>GitHub</a></div><p className="copyright">Apache-2.0 · 全程公开构建</p></footer>
  </main>;
}
