import type { Metadata } from "next";
import Link from "next/link";

const github = "https://github.com/alanthssss/sweetgold";

export const metadata: Metadata = {
  title: "FAQ — SweetGold",
  description: "Answers for visitors, learners, researchers, engineers, contributors, partners, and governance teams using SweetGold.",
  alternates: { languages: { en: "/faq", "zh-CN": "/zh/faq" } },
};

const groups = [
  ["01", "Understand", "For first-time visitors", [
    ["What is SweetGold?", "A reproducible, auditable multi-agent AI lab built around a seeded bee-colony simulator. It connects simulation, training, matched-seed evaluation, policy promotion, verified distribution, and decision evidence."],
    ["Is it just a bee game?", "No. The bee world is an understandable reference environment for studying agents that share limited resources, see only part of the world, and must coordinate while acting independently."],
    ["What do M14, M15, and M16 mean?", "M14 is the latest formally promoted policy. M15 is the latest completed product workflow for constrained recommendation. M16 is the latest engineering milestone for explicit CPU, MPS, and CUDA execution."],
    ["Is SweetGold a production control system?", "No. It is open-source research and evidence infrastructure. The local server is a research interface, and real robotics or industrial use still requires domain simulation, integration, safety, security, and regulatory evidence."],
  ]],
  ["02", "Try", "For learners and evaluators", [
    ["Do I need an AI background?", "No. The simulator, rule policies, benchmark, and web Arena need only Python 3.10+. PyTorch is optional and required only for learning pipelines."],
    ["Should I train a model first?", "No. Start with the Arena and matched-seed comparison. Promoted checkpoints can be downloaded and verified separately, without retraining."],
    ["Does one Arena match prove robustness?", "No. A match or small league is useful for demonstration and debugging. Formal robustness requires predeclared gates, isolated final seeds, enough episodes, and multiple declared scenarios."],
    ["Why preserve failed experiments?", "Failures expose reliability boundaries and prevent cherry-picking. M10–M12 failed their declared gates, stayed in the record, and motivated the structural change in M14."],
  ]],
  ["03", "Build", "For researchers and engineers", [
    ["Why use matched random seeds?", "They give competing policies the same maps, resources, and weather—the equivalent of the same exam—so luck is less likely to decide the comparison."],
    ["Why can final seeds not be reused for tuning?", "Once final results have been inspected, those seeds are no longer unseen. New research must allocate fresh validation and final ranges to preserve independent evidence."],
    ["Does a valid SHA-256 prove a model is safe?", "No. It proves byte-level identity only. Suitability, performance, robustness, provenance, and licensing require separate evidence."],
    ["Which contributions are welcome now?", "Focused defect, security, compatibility, installation, reproducibility, documentation, and regression-test improvements. New architectures need a concrete question, budget, fresh seeds, and predeclared gates."],
  ]],
  ["04", "Adopt", "For partners and governance teams", [
    ["Can SweetGold directly control robots or drones?", "No. The transferable asset is the evaluation and evidence workflow, not the bee policy. Real systems need dynamics, sensors, communications, integration, and safety validation."],
    ["What is the closest credible adoption path?", "Education and enablement first, then an adapter-based evaluation and promotion toolkit connected to an existing simulator or policy source."],
    ["Why is “no eligible policy” a useful answer?", "If every candidate violates a declared constraint, explicit rejection is safer and more auditable than recommending the least-bad ineligible policy."],
    ["What would justify further product investment?", "Repeated high-cost user problems, self-service use, value outside BeeSim, a partner committing real resources, and measurable reductions in evaluation time, defects, approval time, or audit effort."],
  ]],
] as const;

export default function FAQPage() {
  return <main>
    <nav className="nav shell" aria-label="FAQ navigation"><Link className="brand" href="/"><span className="brand-mark">SG</span><span>SweetGold</span></Link><div className="nav-links"><Link href="/">Home</Link><a href="#questions">Questions</a><Link className="language-switch" href="/zh/faq" lang="zh-CN">中文</Link><a className="nav-cta" href={github}>GitHub ↗</a></div></nav>
    <header className="faq-hero shell"><p className="eyebrow"><span /> FREQUENTLY ASKED QUESTIONS</p><h1>Know what is proven.<br /><em>Know what is not.</em></h1><p className="lede">A role-based guide to understanding, trying, building on, and evaluating SweetGold—without confusing a compelling demonstration with a production claim.</p><div className="faq-facts"><span>4 reader stages</span><span>16 essential answers</span><span>55 in the full reference</span></div></header>
    <section className="faq-groups shell" id="questions">
      {groups.map(([number, title, audience, questions]) => <section className="faq-group" key={number}><div className="faq-group-heading"><span>{number}</span><div><p>{audience}</p><h2>{title}</h2></div></div><div className="faq-list">{questions.map(([question, answer]) => <details key={question}><summary>{question}<span aria-hidden="true">+</span></summary><p>{answer}</p></details>)}</div></section>)}
    </section>
    <section className="faq-reference shell"><div><p className="eyebrow"><span /> NEED THE COMPLETE REFERENCE?</p><h2>Continue with all 55 answers.</h2><p>The repository FAQ also covers installation, hardware, authoritative artifacts, releases, licensing, issue routing, and reporting templates.</p></div><a className="button primary" href={`${github}/blob/main/docs/faq.md`}>Read the full FAQ <span>↗</span></a></section>
    <footer className="shell"><div className="footer-brand"><span className="brand-mark">SG</span><div><strong>SweetGold</strong><p>Build policies that earn their promotion.</p></div></div><div className="footer-links"><Link href="/">Home</Link><a href={`${github}/blob/main/docs/faq.md`}>Full FAQ</a><a href={github}>GitHub</a></div><p className="copyright">Apache-2.0 · Built in the open</p></footer>
  </main>;
}
