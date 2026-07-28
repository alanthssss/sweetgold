const $ = id => document.getElementById(id);
let arena, timer, strategies = [];
let language = localStorage.getItem("sweetgold-language")
  || (navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en");
if (!["en", "zh"].includes(language)) language = "en";

const words = {
  en: {
    run: "Run", pause: "Pause", live: "Live", replay: "Replay",
    even: "Even", leads: name => `${name} leads`,
    unavailable: "Learned strategy unavailable in this runtime",
    verified: "Verified locally", missing: "Not downloaded", corrupt: "Integrity failed",
    runtimeMissing: "Verified; PyTorch runtime missing",
    accepted: "Promotion accepted", download: "Download model", downloading: "Downloading…",
    modelCard: "Model card", meanHoney: "Mean honey", license: "License",
    sourceRun: "Source run", laterAudit: "Later robustness audit",
    auditFailed: "failed",
    worstScenario: "Worst yield scenario", minimumSurvival: "Minimum survival",
    noLaterAudit: "No later robustness audit recorded",
    runLeague: "Run league", runningLeague: "Running matched-seed league…",
    selectTwo: "Select at least two available strategies",
    savedArtifact: "Saved evaluation artifact", downloadJson: "Download JSON",
    rank: "Rank", strategy: "Strategy", record: "Record", points: "Points",
    survival: "Colony survival", episodes: "episodes",
    honey: "Honey", alive: "Alive", efficiency: "Efficiency", invalid: "Invalid",
    prevented: "Prevented"
  },
  zh: {
    run: "运行", pause: "暂停", live: "实时", replay: "回放",
    even: "持平", leads: name => `${name} 领先`,
    unavailable: "学习策略在当前运行环境中不可用",
    verified: "本机校验通过", missing: "尚未下载", corrupt: "完整性校验失败",
    runtimeMissing: "制品已校验；缺少 PyTorch 运行环境",
    accepted: "已通过晋级", download: "下载模型", downloading: "正在下载…",
    modelCard: "模型卡", meanHoney: "平均蜂蜜", license: "许可证",
    sourceRun: "来源实验", laterAudit: "后续鲁棒性审计",
    auditFailed: "未通过",
    worstScenario: "最差产量场景", minimumSurvival: "最低生存率",
    noLaterAudit: "暂无后续鲁棒性审计",
    runLeague: "运行联赛", runningLeague: "正在运行同种子联赛…",
    selectTwo: "请至少选择两个可用策略",
    savedArtifact: "评测制品已保存", downloadJson: "下载 JSON",
    rank: "排名", strategy: "策略", record: "战绩", points: "积分",
    survival: "蜂群存活率", episodes: "局",
    honey: "蜂蜜", alive: "存活", efficiency: "效率", invalid: "无效",
    prevented: "避免冲突"
  }
};

async function api(path, body) {
  const response = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: {"Content-Type": "application/json"},
    body: body ? JSON.stringify(body) : undefined
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

function translate() {
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-en]").forEach(node => {
    node.textContent = node.dataset[language] || node.dataset.en;
  });
  $("language").textContent = language === "en" ? "中文" : "English";
  $("toggle").textContent = timer ? words[language].pause : words[language].run;
  document.title = language === "en"
    ? "SweetGold · Strategy Arena" : "SweetGold · 策略竞技场";
  if (arena) render(arena);
}

function metricNumber(value, digits = 0) {
  const number = Number(value || 0);
  return Number.isFinite(number) ? number.toFixed(digits) : "0";
}

function renderWorld(id, state) {
  const world = $(id);
  world.style.gridTemplateColumns = `repeat(${state.config.width},1fr)`;
  const flowers = new Map(state.flowers.map(f => [`${f.row},${f.col}`, f]));
  const bees = new Map();
  state.bees.filter(bee => bee.alive).forEach(bee => {
    const key = `${bee.row},${bee.col}`;
    bees.set(key, [...(bees.get(key) || []), bee]);
  });
  const targets = new Set(state.bees
    .filter(bee => bee.alive && Array.isArray(bee.target))
    .map(bee => `${bee.target[0]},${bee.target[1]}`));
  const cells = [];
  for (let row = 0; row < state.config.height; row++) {
    for (let col = 0; col < state.config.width; col++) {
      const key = `${row},${col}`;
      const flower = flowers.get(key);
      const local = bees.get(key) || [];
      const hive = row === state.hive[0] && col === state.hive[1];
      cells.push(`<div class="cell${hive ? " hive-cell" : ""}${targets.has(key) ? " assigned" : ""}">
        ${hive ? '<span class="entity">🍯</span>' : ""}
        ${flower ? `<span class="entity flower">🌼<b>${flower.nectar}</b></span>` : ""}
        ${local.length ? `<span class="entity bee">🐝${local.length > 1 ? `<b>×${local.length}</b>` : ""}</span>` : ""}
      </div>`);
    }
  }
  world.innerHTML = cells.join("");
}

function metricsHtml(state) {
  const m = state.metrics;
  const c = state.controller_metrics || {};
  const cards = [
    [words[language].alive, `${m.alive}/${state.config.bees}`],
    [words[language].efficiency, metricNumber(m.efficiency, 2)],
    [words[language].invalid, metricNumber(m.invalid_actions)],
  ];
  if (c.prevented_conflicts !== undefined) {
    cards.push([words[language].prevented, metricNumber(c.prevented_conflicts)]);
  }
  return cards.map(([label, value]) =>
    `<span><small>${label}</small><b>${value}</b></span>`).join("");
}

function strategyLabel(id) {
  return strategies.find(item => item.id === id)?.label || id;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
}

function percent(value) {
  return `${metricNumber(Number(value || 0) * 100, 1)}%`;
}

function renderModelCards() {
  const learned = strategies.filter(strategy => strategy.kind === "learned");
  $("modelCards").innerHTML = learned.map(strategy => {
    const status = strategy.integrity === "verified" && strategy.runtime !== "ready"
      ? words[language].runtimeMissing
      : strategy.integrity === "verified"
      ? words[language].verified
      : strategy.integrity === "corrupt"
        ? words[language].corrupt
        : words[language].missing;
    const audit = strategy.latest_audit;
    const auditHtml = audit
      ? `<div class="audit-note">
          <b>${escapeHtml(words[language].laterAudit)} · ${escapeHtml(audit.status === "failed" ? words[language].auditFailed : audit.status)}</b>
          <span>${escapeHtml(words[language].worstScenario)}: ${escapeHtml(audit.worst_honey_scenario || "—")} · ${percent(audit.worst_honey_ratio)}</span>
          <span>${escapeHtml(words[language].minimumSurvival)}: ${percent(audit.minimum_bee_survival)}</span>
        </div>`
      : `<div class="audit-note quiet">${escapeHtml(words[language].noLaterAudit)}</div>`;
    const action = strategy.available
      ? `<span class="model-ready">✓ ${escapeHtml(words[language].verified)}</span>`
      : strategy.integrity === "verified"
        ? `<span class="runtime-missing">${escapeHtml(words[language].runtimeMissing)}</span>`
      : `<button class="download-model" data-model="${escapeHtml(strategy.id)}" type="button">${escapeHtml(words[language].download)}</button>`;
    return `<article class="model-card ${strategy.available ? "is-ready" : "is-missing"}">
      <div class="model-card-head">
        <div>
          <span class="status-dot"></span>
          <small>${escapeHtml(status)}</small>
        </div>
        <span class="promotion">${escapeHtml(words[language].accepted)}</span>
      </div>
      <h3>${escapeHtml(strategy.label)}</h3>
      <p>${escapeHtml(language === "zh" ? strategy.description_zh : strategy.description)}</p>
      <dl>
        <div><dt>${escapeHtml(words[language].meanHoney)}</dt><dd>${metricNumber(strategy.mean_honey, 2)}</dd></div>
        <div><dt>${escapeHtml(words[language].license)}</dt><dd>${escapeHtml(strategy.license || "—")}</dd></div>
        <div><dt>${escapeHtml(words[language].sourceRun)}</dt><dd>${escapeHtml(strategy.run || "—")}</dd></div>
      </dl>
      ${auditHtml}
      <div class="model-actions">
        ${action}
        ${strategy.model_card_url ? `<a href="${escapeHtml(strategy.model_card_url)}" target="_blank" rel="noreferrer">${escapeHtml(words[language].modelCard)} ↗</a>` : ""}
      </div>
    </article>`;
  }).join("");
}

function renderTournamentChoices() {
  const available = strategies.filter(strategy => strategy.available);
  $("tournamentStrategies").innerHTML = available.map((strategy, index) =>
    `<label><input type="checkbox" value="${escapeHtml(strategy.id)}" ${index < 4 ? "checked" : ""}>
      <span>${escapeHtml(strategy.label)}</span></label>`).join("");
}

function renderLeaderboard(result) {
  const rows = result.leaderboard.map(row => `<tr>
    <td><b>#${row.rank}</b></td>
    <td>${escapeHtml(strategyLabel(row.strategy))}</td>
    <td>${metricNumber(row.mean_honey, 1)} <small>±${metricNumber(row.ci95_honey, 1)}</small></td>
    <td>${percent(row.colony_survival_rate)}</td>
    <td>${row.match_wins}-${row.match_ties}-${row.match_losses}</td>
    <td><b>${row.points}</b></td>
  </tr>`).join("");
  $("leaderboard").hidden = false;
  $("leaderboard").innerHTML = `<table>
    <thead><tr>
      <th>${words[language].rank}</th>
      <th>${words[language].strategy}</th>
      <th>${words[language].meanHoney}</th>
      <th>${words[language].survival}</th>
      <th>${words[language].record}</th>
      <th>${words[language].points}</th>
    </tr></thead>
    <tbody>${rows}</tbody>
  </table>`;
  $("tournamentStatus").textContent =
    `${result.episodes} ${words[language].episodes} · seed ${result.seed}–${result.seeds.at(-1)}`;
  if (result.artifact) {
    const runId = escapeHtml(result.artifact.run_id);
    $("tournamentStatus").innerHTML +=
      ` · ${escapeHtml(words[language].savedArtifact)} <code>${runId}</code>
       · <a href="/api/tournaments/${runId}?download=1">${escapeHtml(words[language].downloadJson)}</a>`;
  }
}

async function runTournament() {
  const selected = [...document.querySelectorAll("#tournamentStrategies input:checked")]
    .map(input => input.value);
  if (selected.length < 2) {
    $("tournamentStatus").textContent = words[language].selectTwo;
    return;
  }
  const button = $("runTournament");
  button.disabled = true;
  button.textContent = words[language].runningLeague;
  $("tournamentStatus").textContent = words[language].runningLeague;
  try {
    renderLeaderboard(await api("/api/tournament", {
      strategies: selected,
      seed: Number($("seed").value),
      episodes: Number($("tournamentEpisodes").value)
    }));
  } catch (error) {
    $("tournamentStatus").textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = words[language].runLeague;
  }
}

async function downloadModel(model, button) {
  button.disabled = true;
  button.textContent = words[language].downloading;
  try {
    await api("/api/models/download", {model});
    await loadStrategies(true);
  } catch (error) {
    $("notice").hidden = false;
    $("notice").textContent = error.message;
    button.disabled = false;
    button.textContent = words[language].download;
  }
}

function render(frame) {
  arena = frame;
  const left = frame.left, right = frame.right;
  renderWorld("leftWorld", left);
  renderWorld("rightWorld", right);
  $("leftMetrics").innerHTML = metricsHtml(left);
  $("rightMetrics").innerHTML = metricsHtml(right);
  const leftLabel = strategyLabel(left.controller);
  const rightLabel = strategyLabel(right.controller);
  ["leftName", "leftTitle"].forEach(id => $(id).textContent = leftLabel);
  ["rightName", "rightTitle"].forEach(id => $(id).textContent = rightLabel);
  $("leftHoney").textContent = left.metrics.honey;
  $("rightHoney").textContent = right.metrics.honey;
  const delta = left.metrics.honey - right.metrics.honey;
  $("honeyDelta").textContent = `${delta > 0 ? "+" : ""}${delta}`;
  $("honeyDelta").className = delta > 0 ? "positive" : delta < 0 ? "negative" : "";
  $("leader").textContent = delta === 0
    ? words[language].even
    : words[language].leads(delta > 0 ? leftLabel : rightLabel);
  $("leftWeather").textContent = left.weather === "rain" ? "🌧" : "☀";
  $("rightWeather").textContent = right.weather === "rain" ? "🌧" : "☀";
  $("tick").textContent = left.tick;
  $("maxTick").textContent = left.config.season_ticks;
  $("timeline").max = Math.max(0, frame.frames - 1);
  $("timeline").value = frame.frame;
  $("replayState").textContent = frame.live ? words[language].live : words[language].replay;
  $("replayState").className = frame.live ? "live" : "";
  if (left.done && right.done) stop();
}

async function loadStrategies(preserve = false) {
  const previousLeft = $("leftStrategy").value;
  const previousRight = $("rightStrategy").value;
  strategies = (await api("/api/strategies")).strategies;
  const options = strategies.map(strategy => {
    const suffix = strategy.available ? "" : ` · ${words[language].unavailable}`;
    return `<option value="${strategy.id}" ${strategy.available ? "" : "disabled"}>${strategy.label}${suffix}</option>`;
  }).join("");
  $("leftStrategy").innerHTML = options;
  $("rightStrategy").innerHTML = options;
  $("leftStrategy").value = preserve && strategies.some(
    strategy => strategy.id === previousLeft && strategy.available
  ) ? previousLeft : strategies.some(
    strategy => strategy.id === "coordinated-ctde" && strategy.available
  ) ? "coordinated-ctde" : "assignment";
  $("rightStrategy").value = preserve && strategies.some(
    strategy => strategy.id === previousRight && strategy.available
  ) ? previousRight : "assignment";
  const missing = strategies.filter(s => s.kind === "learned" && !s.available);
  $("notice").hidden = missing.length === 0;
  $("notice").textContent = missing.length
    ? `${words[language].unavailable}: ${missing.map(s => s.label).join(", ")}`
    : "";
  renderModelCards();
  renderTournamentChoices();
}

async function reset() {
  stop();
  try {
    render(await api("/api/reset", {
      seed: Number($("seed").value),
      left: $("leftStrategy").value,
      right: $("rightStrategy").value
    }));
  } catch (error) {
    $("notice").hidden = false;
    $("notice").textContent = error.message;
  }
}

async function step() {
  if (arena && !arena.live) {
    render(await api(`/api/frame?index=${arena.frames - 1}`));
    return;
  }
  render(await api("/api/step", {}));
}

function stop() {
  clearInterval(timer);
  timer = null;
  $("toggle").textContent = words[language].run;
}

function toggle() {
  if (timer) return stop();
  timer = setInterval(() => step().catch(stop), 110);
  $("toggle").textContent = words[language].pause;
}

$("reset").onclick = reset;
$("step").onclick = () => step();
$("toggle").onclick = toggle;
$("timeline").oninput = async event => {
  stop();
  render(await api(`/api/frame?index=${event.target.value}`));
};
$("language").onclick = async () => {
  language = language === "en" ? "zh" : "en";
  localStorage.setItem("sweetgold-language", language);
  translate();
  renderModelCards();
};
$("modelCards").onclick = event => {
  const button = event.target.closest(".download-model");
  if (button) downloadModel(button.dataset.model, button);
};
$("runTournament").onclick = runTournament;

translate();
loadStrategies()
  .then(reset)
  .catch(error => {
    $("notice").hidden = false;
    $("notice").textContent = error.message;
  });
