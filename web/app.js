const $ = id => document.getElementById(id);
let arena, timer, strategies = [];
let language = localStorage.getItem("sweetgold-language")
  || (navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en");
if (!["en", "zh"].includes(language)) language = "en";

const words = {
  en: {
    run: "Run", pause: "Pause", live: "Live", replay: "Replay",
    even: "Even", leads: name => `${name} leads`,
    unavailable: "Model checkpoint unavailable locally",
    honey: "Honey", alive: "Alive", efficiency: "Efficiency", invalid: "Invalid",
    prevented: "Prevented"
  },
  zh: {
    run: "运行", pause: "暂停", live: "实时", replay: "回放",
    even: "持平", leads: name => `${name} 领先`,
    unavailable: "模型 checkpoint 在本机不可用",
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

async function loadStrategies() {
  strategies = (await api("/api/strategies")).strategies;
  const options = strategies.map(strategy => {
    const suffix = strategy.available ? "" : ` · ${words[language].unavailable}`;
    return `<option value="${strategy.id}" ${strategy.available ? "" : "disabled"}>${strategy.label}${suffix}</option>`;
  }).join("");
  $("leftStrategy").innerHTML = options;
  $("rightStrategy").innerHTML = options;
  $("leftStrategy").value = strategies.some(s => s.id === "coordinated-ctde" && s.available)
    ? "coordinated-ctde" : "assignment";
  $("rightStrategy").value = "assignment";
  const missing = strategies.filter(s => s.kind === "learned" && !s.available);
  $("notice").hidden = missing.length === 0;
  $("notice").textContent = missing.length
    ? `${words[language].unavailable}: ${missing.map(s => s.label).join(", ")}`
    : "";
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
};

translate();
loadStrategies()
  .then(reset)
  .catch(error => {
    $("notice").hidden = false;
    $("notice").textContent = error.message;
  });
