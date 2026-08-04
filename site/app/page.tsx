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
          <a href="#evidence">Evidence</a>
          <a href="#arena">Arena</a>
          <a href="#engineering">Engineering</a>
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
            <div><strong>49</strong><span>tests passing</span></div>
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

      <section className="current-outcome shell" id="evidence">
        <div className="section-heading">
          <p className="eyebrow"><span /> LATEST COMPLETED OUTCOME · M15</p>
          <h2>Evidence in.<br />Auditable decision out.</h2>
        </div>
        <div className="outcome-grid">
          <article><span>OBJECTIVES</span><strong>3</strong><p>balanced · yield · safety</p></article>
          <article><span>SAFETY CONSTRAINTS</span><strong>2</strong><p>survival · invalid actions</p></article>
          <article><span>EVIDENCE FORMATS</span><strong>2</strong><p>JSON · Markdown</p></article>
          <article><span>DECISION</span><strong>Deterministic</strong><p>recommend or reject explicitly</p></article>
        </div>
        <p className="method-note">M15 is the current project stage. It selects among existing strategies; it does not train a new policy.</p>
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
        <div className="footer-links"><a href={github}>GitHub</a><a href={`${github}/releases`}>Releases</a><a href={`${github}/blob/main/docs/models/hierarchical-return-ctde.md`}>Model card</a></div>
        <p className="copyright">Apache-2.0 · Built in the open</p>
      </footer>
    </main>
  );
}
