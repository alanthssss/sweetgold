const $ = (id) => document.getElementById(id);
let state, timer, events = [], lastRecordedTick = -1;
let language = localStorage.getItem("sweetgold-language")
  || (navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en");
if (!["en", "zh"].includes(language)) language = "en";

const copy = {
  en: {
    clear: "☀ CLEAR", rain: "🌧 RAIN", start: "Start", pause: "Pause",
    seasonEnd: "The season has ended. Start a new season to continue.",
    tickEvent: (tick, honey, alive) => `Tick ${tick}: honey yield ${honey}, ${alive} bees alive`,
    signalEvent: count => `Scout bees advertised ${count} nectar sources`
  },
  zh: {
    clear: "☀ 晴朗", rain: "🌧 降雨", start: "开始", pause: "暂停",
    seasonEnd: "季节结束，请开始一个新季节。",
    tickEvent: (tick, honey, alive) => `第 ${tick} 步：蜂蜜产量 ${honey}，存活 ${alive} 只`,
    signalEvent: count => `侦察蜂广播了 ${count} 个花蜜来源`
  }
};

function translateStatic() {
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-en]").forEach(el => {
    el.textContent = el.dataset[language] ?? el.dataset.en ?? "";
  });
  $("language").textContent = language === "en" ? "中文" : "English";
  document.title = language === "en"
    ? "BeeSim · Bee ecosystem experiment"
    : "BeeSim · 蜂群生态实验";
  if ($("toggle")) $("toggle").textContent = timer ? copy[language].pause : copy[language].start;
}

async function api(path, body) {
  const response = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: {"Content-Type": "application/json"},
    body: body ? JSON.stringify(body) : undefined
  });
  return response.json();
}

function finiteNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function normalizeMetrics(s) {
  const metrics = s && typeof s.metrics === "object" && s.metrics !== null
    ? s.metrics
    : {};
  return {
    // Compatibility with servers started before the nectar → honey migration.
    honey: finiteNumber(
      metrics.honey ?? metrics.nectar ?? s?.stored_honey ?? s?.stored_nectar
    ),
    alive: finiteNumber(metrics.alive),
    coverage: finiteNumber(metrics.coverage),
    efficiency: finiteNumber(metrics.efficiency),
  };
}

function render(s) {
  state = s;
  const metrics = normalizeMetrics(s);
  const world = $("world");
  world.style.gridTemplateColumns = `repeat(${s.config.width},1fr)`;
  world.innerHTML = "";
  const flowers = new Map(s.flowers.map(f => [`${f.row},${f.col}`, f]));
  const bees = new Map();
  s.bees.forEach(b => {
    const key = `${b.row},${b.col}`;
    bees.set(key, [...(bees.get(key) || []), b]);
  });
  const signals = new Set(s.signals.map(x => `${x.row},${x.col}`));
  const targets = new Set(
    s.bees.filter(b => b.alive && Array.isArray(b.target)).map(b => `${b.target[0]},${b.target[1]}`)
  );
  for (let r=0;r<s.config.height;r++) for (let c=0;c<s.config.width;c++) {
    const cell = document.createElement("div");
    const key = `${r},${c}`, flower = flowers.get(key), localBees = bees.get(key) || [];
    cell.className = "cell"
      + (r===s.hive[0] && c===s.hive[1] ? " hive-cell" : "")
      + (targets.has(key) ? " assigned-target" : "");
    if (r===s.hive[0] && c===s.hive[1]) cell.innerHTML += `<span class="entity">🍯</span>`;
    if (flower) cell.innerHTML += `<span class="entity flower-entity ${signals.has(key)?"pulse":""}">🌼<b class="nectar-count">${flower.nectar}</b></span>`;
    if (localBees.length) cell.innerHTML += `<span class="entity ${localBees.every(b=>!b.alive)?"dead":""}">🐝${localBees.length>1?`<b class="nectar-count">×${localBees.length}</b>`:""}</span>`;
    world.appendChild(cell);
  }
  $("tick").textContent=s.tick; $("maxTick").textContent=s.config.season_ticks;
  $("progress").style.width=`${100*s.tick/s.config.season_ticks}%`;
  $("weather").textContent=s.weather==="rain" ? copy[language].rain : copy[language].clear;
  $("honey").textContent=metrics.honey;
  $("alive").textContent=`${metrics.alive}/${finiteNumber(s.config?.bees)}`;
  $("coverage").textContent=`${(100*metrics.coverage).toFixed(0)}%`;
  $("efficiency").textContent=metrics.efficiency.toFixed(2);
  if (s.tick !== lastRecordedTick) {
    if (s.tick && s.tick%20===0) events.unshift({key:"tick",args:[s.tick,metrics.honey,metrics.alive]});
    if (s.signals.length && s.tick%10===0) events.unshift({key:"signal",args:[s.signals.length]});
    if (s.done) events.unshift({key:"end",args:[]});
    lastRecordedTick = s.tick;
  }
  $("events").innerHTML=events.slice(0,7).map(e => {
    const label = e.key === "tick"
      ? copy[language].tickEvent(...e.args)
      : e.key === "signal"
        ? copy[language].signalEvent(...e.args)
        : copy[language].seasonEnd;
    return `<li>${label}</li>`;
  }).join("");
  if(s.done) stop();
}

async function step(){ render(await api("/api/step", {})); }
function stop(){clearInterval(timer);timer=null;$("toggle").textContent=copy[language].start;}
function toggle(){if(timer){stop()}else{timer=setInterval(step,120);$("toggle").textContent=copy[language].pause}}
$("toggle").onclick=toggle; $("step").onclick=step;
$("reset").onclick=async()=>{stop();events=[];lastRecordedTick=-1;render(await api("/api/reset",{seed:+$("seed").value,controller:$("controller").value}))};
$("language").onclick=()=>{
  language=language==="en"?"zh":"en";
  localStorage.setItem("sweetgold-language",language);
  translateStatic();
  if(state) render(state);
};
translateStatic();
api("/api/state").then(render);
