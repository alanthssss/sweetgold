const github = "https://github.com/alanthssss/sweetgold";

const milestones = [
  ["M4", "Imitation", "Behavior cloning + DAgger"],
  ["M7", "Decentralize", "Local actors, global critic"],
  ["M10–12", "Fail honestly", "Robustness gaps preserved"],
  ["M14", "Pass the gates", "Hierarchical return control"],
  ["M15", "Decide with evidence", "Auditable agent workflow"],
];

export default function Home() {
  return (
    <main>
      <nav className="nav shell" aria-label="Primary navigation">
        <a className="brand" href="#top" aria-label="SweetGold home">
          <span className="brand-mark">SG</span>
          <span>SweetGold</span>
        </a>
        <div className="nav-links">
          <a href="#start-here">Start here</a>
          <a href="#impact">Impact</a>
          <a href="#evidence">Evidence</a>
          <a href="#arena">Arena</a>
          <a href="#engineering">Engineering</a>
          <a href="/faq">FAQ</a>
          <a href="#start">Quick start</a>
          <a className="language-switch" href="/zh" lang="zh-CN">中文</a>
          <a className="nav-cta" href={github}>GitHub ↗</a>
        </div>
      </nav>

      <section className="hero shell" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span /> OPEN-SOURCE MULTI-AGENT AI LAB</p>
          <h1>Teach a colony<br />to survive the <em>unknown.</em></h1>
          <p className="lede">
            A deterministic bee simulation where strategies compete on identical
            worlds, learned policies face predeclared safety gates, and failed
            experiments stay in the record.
          </p>
          <div className="hero-actions">
            <a className="button primary" href={`${github}#quick-start`}>Run the arena <span>→</span></a>
            <a className="button secondary" href={github}>View source <span>↗</span></a>
          </div>
          <div className="proof-strip" aria-label="Project facts">
            <div><strong>53</strong><span>tests passing</span></div>
            <div><strong>6</strong><span>audit scenarios</span></div>
            <div><strong>Apache 2.0</strong><span>open source</span></div>
          </div>
        </div>

        <div className="colony-card" aria-label="Stylized live colony simulation">
          <div className="card-top"><span>COLONY / 042</span><span className="live">● LIVE</span></div>
          <div className="sim-grid">
            <span className="hive">⬡</span>
            <span className="flower f1">✦</span><span className="flower f2">✦</span>
            <span className="flower f3">✦</span><span className="flower f4">✦</span>
            <span className="bee b1">●</span><span className="bee b2">●</span>
            <span className="bee b3">●</span><span className="bee b4">●</span>
            <i className="trail t1" /><i className="trail t2" /><i className="trail t3" />
          </div>
          <div className="sim-stats">
            <div><span>HONEY</span><strong>223.68</strong><small>+52.6%</small></div>
            <div><span>SURVIVAL</span><strong>100%</strong><small>6 / 6</small></div>
            <div><span>INVALID</span><strong>0.00%</strong><small>safe</small></div>
          </div>
        </div>
      </section>

      <section className="orientation shell" id="start-here">
        <div className="section-heading orientation-heading">
          <p className="eyebrow"><span /> NEW HERE? BEGIN BEFORE THE JARGON</p>
          <h2>A small bee game.<br />A serious cooperation problem.</h2>
        </div>
        <div className="plain-story">
          <article><b>01</b><h3>Build the world</h3><p>A hive, flowers, energy, weather, and several virtual bees. The season ends; we count honey, survival, and invalid actions.</p></article>
          <article><b>02</b><h3>Try different minds</h3><p>Handwritten rules and learned policies solve the same problem: act independently without wasting the colony&apos;s shared resources.</p></article>
          <article><b>03</b><h3>Give them the same exam</h3><p>The same random seed recreates the same world, so a strategy cannot win merely by receiving an easier map.</p></article>
          <article><b>04</b><h3>Publish the evidence</h3><p>Declared gates, isolated final tests, model hashes, and retained failures make each promoted result traceable.</p></article>
        </div>
        <div className="reader-routes" aria-label="Choose a reading route">
          <div><span>I AM NEW TO AI</span><strong>Understand the game and question</strong><a href={`${github}/blob/main/docs/getting-started.md`}>Start with the plain-language guide →</a></div>
          <div><span>I WORK IN ML</span><strong>Inspect training and evidence</strong><a href={`${github}/blob/main/docs/models/README.md`}>Open the model catalog →</a></div>
          <div><span>I WORK IN DEVOPS / MLOPS</span><strong>Trace delivery and controls</strong><a href={`${github}/blob/main/HANDOFF.md`}>Read the engineering handoff →</a></div>
        </div>
        <p className="concept-line"><strong>The whole journey:</strong> bee simulator → rule baselines → learned policies → fair exams → evidence-backed release.</p>
      </section>

      <section className="impact shell" id="impact">
        <div className="section-heading">
          <p className="eyebrow"><span /> WHY IT MATTERS BEYOND BEES</p>
          <h2>A small world for<br />high-stakes habits.</h2>
        </div>
        <p className="impact-lede">SweetGold does not sell a bee policy. It makes coordination, fair evaluation, promotion, and audit evidence understandable in one end-to-end system. The workflow may transfer; each industry claim still needs domain validation.</p>
        <div className="impact-grid">
          <article><span>PRACTICAL VALUE TODAY</span><h3>Inspect the complete AI lifecycle</h3><p>From simulator and baselines to learned policies, isolated final tests, verified models, and auditable decisions.</p></article>
          <article><span>TRANSFER SCENARIOS</span><h3>Shared-resource coordination</h3><p>Warehouse and robot fleets, drone inspection, mobility research, games, AI evaluation, and technical education.</p></article>
          <article><span>CUSTOMER HYPOTHESES</span><h3>Teams that teach, test, or govern AI</h3><p>Universities, corporate academies, ML platforms, governance teams, simulation R&amp;D, and technical consultancies.</p></article>
        </div>
        <div className="truth-grid">
          <div><span>ADVANTAGE</span><strong>Evidence is the product</strong><p>Deterministic comparisons, predeclared gates, retained failures, model integrity, and bilingual explanation form one coherent workflow.</p></div>
          <div><span>LIMITATION</span><strong>The domain is still a proxy</strong><p>No customer discovery, paid pilot, real fleet integration, multi-user hardening, or measured business outcome exists yet.</p></div>
        </div>
        <div className="commercial-path"><div><span>01</span><strong>Interview</strong><p>Validate one repeated, urgent buyer problem.</p></div><div><span>02</span><strong>Transfer</strong><p>Connect one external or customer simulator.</p></div><div><span>03</span><strong>Pilot</strong><p>Measure time, defect, or audit reduction.</p></div><div><span>04</span><strong>Productize</strong><p>Standardize only what repeats.</p></div></div>
        <div className="strategy-band"><div><span>COMPETE</span><strong>Own evaluation and promotion</strong><p>Integrate PettingZoo, RLlib, Isaac Lab, and model registries. Do not compete on environment count, algorithm breadth, GPU scale, or generic tracking.</p></div><div><span>OPEN-SOURCE REALITY</span><strong>The code may be copied</strong><p>Apache-2.0 permits compliant use, modification, redistribution, and commercial reuse. The defense is trusted upstream, brand, adapters, evidence, community, and customer context.</p></div><div><span>NEXT FEATURE</span><strong>Prove transfer first</strong><p>After customer interviews, connect one PettingZoo environment and publish a stable evidence schema before adding more algorithms or a SaaS dashboard.</p></div></div>
        <p className="impact-boundary">Most credible first paths: education and enablement, then an adapter-based evaluation and promotion toolkit. Direct industrial control remains a hypothesis until domain-specific evidence exists.</p>
        <a className="impact-link" href={`${github}/blob/main/docs/impact-and-roadmap.md`}>Read the full customer, SWOT, commercialization, and roadmap analysis →</a>
      </section>

      <section className="current-outcome shell" id="evidence">
        <div className="section-heading">
          <p className="eyebrow"><span /> PRODUCT WORKFLOW · M15</p>
          <h2>Evidence in.<br />Auditable decision out.</h2>
        </div>
        <div className="outcome-grid">
          <article><span>OBJECTIVES</span><strong>3</strong><p>balanced · yield · safety</p></article>
          <article><span>SAFETY CONSTRAINTS</span><strong>2</strong><p>survival · invalid actions</p></article>
          <article><span>EVIDENCE FORMATS</span><strong>2</strong><p>JSON · Markdown</p></article>
          <article><span>DECISION</span><strong>Deterministic</strong><p>recommend or reject explicitly</p></article>
        </div>
        <p className="method-note">M15 selects among existing strategies; it does not train a new policy. M16 is the latest engineering milestone.</p>
      </section>

      <section className="faq-preview shell" id="faq">
        <div className="section-heading"><p className="eyebrow"><span /> QUESTIONS BEFORE CLAIMS</p><h2>Start with the<br />important distinctions.</h2></div>
        <div className="faq-preview-grid">
          <article><span>01 · POSITION</span><h3>Is SweetGold just a bee game?</h3><p>No. The bee world is a reference environment for multi-agent coordination. The durable product is the reproducible evaluation and evidence workflow.</p></article>
          <article><span>02 · EVIDENCE</span><h3>Does one Arena win prove robustness?</h3><p>No. A small league is a demonstration. Formal claims require predeclared gates, isolated final seeds, and cross-scenario evidence.</p></article>
          <article><span>03 · BOUNDARY</span><h3>Can it control real robots today?</h3><p>No. The workflow may transfer, but every physical domain still needs its own simulator, integration, safety, and regulatory validation.</p></article>
        </div>
        <div className="faq-preview-action"><p>Answers for visitors, learners, researchers, engineers, contributors, partners, and governance teams.</p><a className="button primary" href="/faq">Explore the FAQ <span>→</span></a></div>
      </section>

      <section className="evidence shell">
        <div className="section-heading">
          <p className="eyebrow"><span /> LATEST PROMOTED POLICY · M14</p>
          <h2>Formal performance<br />of the newest policy.</h2>
        </div>
        <div className="scorecard">
          <div className="score-main"><strong>148.47%</strong><span>median honey vs. Assignment</span></div>
          <div className="score"><strong>101.16%</strong><span>worst-case yield</span><small>scarce nectar</small></div>
          <div className="score"><strong>100%</strong><span>minimum survival</span><small>every scenario</small></div>
          <div className="score"><strong>0%</strong><span>invalid actions</span><small>every scenario</small></div>
        </div>
        <p className="method-note">M14 · 50 untouched seeds in each of 6 scenarios · selected only on disjoint validation seeds · M15 does not change these results</p>
      </section>

      <section className="arena shell" id="arena">
        <div className="arena-panel">
          <div className="arena-copy">
            <p className="eyebrow"><span /> STRATEGY ARENA</p>
            <h2>Same world.<br />Different minds.</h2>
            <p>Run two policies from the same seed. Compare honey, survival, efficiency and invalid actions live—then replay every frame.</p>
            <ul>
              <li><b>01</b> Matched-seed tournaments</li>
              <li><b>02</b> Verified model registry</li>
              <li><b>03</b> Auditable agent recommendations</li>
            </ul>
          </div>
          <div className="matchup">
            <div className="match-head"><span>MATCH 04 / SEED 202607</span><span>SEASON 86%</span></div>
            <div className="lane"><div><span>A</span><b>Hierarchical CTDE</b></div><strong>218</strong></div>
            <div className="bar"><i style={{width:"88%"}} /></div>
            <div className="lane"><div><span>B</span><b>Assignment</b></div><strong>146</strong></div>
            <div className="bar muted"><i style={{width:"59%"}} /></div>
            <div className="match-result"><span>Δ HONEY</span><strong>+72</strong><span>ALL BEES ALIVE</span></div>
          </div>
        </div>
      </section>

      <section className="engineering shell" id="engineering">
        <div className="section-heading">
          <p className="eyebrow"><span /> ENGINEERING GUARANTEES</p>
          <h2>Research rigor,<br />built into the system.</h2>
        </div>
        <div className="engineering-grid">
          <article><b>01</b><h3>Deterministic execution</h3><p>Seeded environments and matched episodes make every comparison repeatable.</p></article>
          <article><b>02</b><h3>Isolated evaluation data</h3><p>Preflight checks block leakage across training, validation, selection and final tests.</p></article>
          <article><b>03</b><h3>Policy-as-code gates</h3><p>Confidence, yield and safety thresholds live in versioned experiment configs.</p></article>
          <article><b>04</b><h3>Verified model supply chain</h3><p>Immutable releases, exact sizes, SHA-256, licenses and atomic installs protect checkpoints.</p></article>
          <article><b>05</b><h3>Traceable artifacts</h3><p>JSON run bundles retain commits, runtimes, seed manifests, metrics and decision links.</p></article>
          <article><b>06</b><h3>Automated regression defense</h3><p>Core tests and end-to-end ML smoke pipelines run in CI; failed audits stay visible.</p></article>
        </div>
        <p className="engineering-boundary">Enterprise-style engineering practices with an explicit boundary: the built-in server is a local experimentation interface, not a hardened multi-user production service.</p>
        <div className="hardware-note"><span>LATEST ENGINEERING MILESTONE · M16</span><strong>CPU, Apple MPS, and NVIDIA CUDA are explicit execution targets.</strong><p>On the measured small behavior-cloning workload, the M1 Pro CPU was about 6.4× faster than MPS because accelerator overhead outweighed useful parallel work. Hardware evidence—not “GPU is always faster”—drives the decision.</p><a href={`${github}/blob/main/docs/hardware-benchmark.md`}>Read the hardware benchmark →</a></div>
      </section>

      <section className="journey shell">
          <div className="section-heading compact"><p className="eyebrow"><span /> 15 MILESTONES, ONE AUDIT TRAIL</p><h2>The failures built the policy.</h2></div>
        <div className="milestones">
          {milestones.map(([id,title,text]) => <article key={id}><span>{id}</span><h3>{title}</h3><p>{text}</p></article>)}
        </div>
        <p className="failure-note">M10–M12 failed their declared gates. SweetGold records why instead of moving the goalposts.</p>
        <p className="failure-note"><strong>M14</strong> is the latest promoted policy. <strong>M15</strong> is the latest completed workflow: it turns Arena evidence into a constrained, auditable recommendation.</p>
      </section>

      <section className="start shell" id="start">
        <div><p className="eyebrow"><span /> ZERO-DEPENDENCY START</p><h2>From clone to colony<br />in three commands.</h2></div>
        <div className="terminal">
          <div className="terminal-top"><i /><i /><i /><span>sweetgold — zsh</span></div>
          <pre><code><b>$</b> git clone https://github.com/alanthssss/sweetgold.git{`\n`}<b>$</b> cd sweetgold{`\n`}<b>$</b> python3 main.py play --port 8080{`\n\n`}<span>✓ Arena ready at http://127.0.0.1:8080</span></code></pre>
        </div>
      </section>

      <footer className="shell">
        <div className="footer-brand"><span className="brand-mark">SG</span><div><strong>SweetGold</strong><p>Build policies that earn their promotion.</p></div></div>
        <div className="footer-links"><a href="/faq">FAQ</a><a href={github}>GitHub</a><a href={`${github}/releases`}>Releases</a><a href={`${github}/blob/main/docs/models/hierarchical-return-ctde.md`}>Model card</a></div>
        <p className="copyright">Apache-2.0 · Built in the open</p>
      </footer>
    </main>
  );
}
