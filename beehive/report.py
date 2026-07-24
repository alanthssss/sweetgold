"""Self-contained HTML benchmark report."""

from __future__ import annotations

import html
import json
from pathlib import Path


def write_report(results: list[dict], output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    ordered = sorted(results, key=lambda x: x["mean_honey"], reverse=True)
    rows = "\n".join(
        "<tr>"
        f"<td>{i}</td><td>{html.escape(r['controller'])}</td>"
        f"<td>{r['mean_honey']:.1f} ± {r['ci95_honey']:.1f}</td>"
        f"<td>{r['survival_rate']:.0%}</td><td>{r['mean_efficiency']:.3f}</td>"
        f"<td>{r['mean_coverage']:.1%}</td><td>{r['mean_deaths']:.2f}</td>"
        f"<td>{r['mean_decision_us']:.2f} μs</td></tr>"
        for i, r in enumerate(ordered, 1)
    )
    payload = json.dumps(ordered, ensure_ascii=False)
    document = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>BeeBench Report</title>
<style>
:root{{--ink:#1d2419;--muted:#697163;--paper:#f7f3e8;--gold:#e8ad2f;--leaf:#477a4b}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}
main{{position:relative;max-width:1100px;margin:auto;padding:48px 24px}}h1{{font:700 48px Georgia,serif;margin:0}}
.lede{{color:var(--muted);max-width:700px}}.card{{background:#fff;border:1px solid #ded8c8;border-radius:18px;padding:24px;margin-top:28px;box-shadow:0 12px 35px #534a3512}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:13px 10px;text-align:right;border-bottom:1px solid #eee9dc}}
th:nth-child(2),td:nth-child(2){{text-align:left}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}
.winner{{display:inline-block;background:var(--gold);border-radius:99px;padding:6px 12px;font-weight:700}}
.language{{position:absolute;right:24px;top:48px;border:1px solid #cbc3ae;background:#fff;border-radius:99px;padding:8px 14px;font-weight:700;cursor:pointer}}
@media(max-width:700px){{.card{{overflow:auto}}.language{{position:static;float:right}}h1{{font-size:38px}}}}
</style>
<main><button class="language" id="language" type="button">中文</button>
<span class="winner" data-en="Matched-seed benchmark" data-zh="匹配随机种子评估">Matched-seed benchmark</span><h1>BeeBench</h1>
<p class="lede" data-en="Controller comparison across {ordered[0]['episodes'] if ordered else 0} identical ecosystem seeds. Honey yield is reported as mean ± 95% confidence interval." data-zh="在 {ordered[0]['episodes'] if ordered else 0} 个完全相同的生态环境种子上比较控制策略。蜂蜜产量以均值 ± 95% 置信区间表示。">Controller comparison across {ordered[0]['episodes'] if ordered else 0} identical ecosystem seeds. Honey yield is reported as mean ± 95% confidence interval.</p>
<section class="card"><table><thead><tr><th>#</th><th data-en="Controller" data-zh="控制策略">Controller</th><th data-en="Honey Yield" data-zh="蜂蜜产量">Honey Yield</th><th data-en="Survival" data-zh="存活率">Survival</th><th data-en="Efficiency" data-zh="能量效率">Efficiency</th><th data-en="Coverage" data-zh="探索覆盖">Coverage</th><th data-en="Deaths" data-zh="死亡数">Deaths</th><th data-en="Decision" data-zh="决策延迟">Decision</th></tr></thead>
<tbody>{rows}</tbody></table></section>
<script type="application/json" id="benchmark-data">{html.escape(payload)}</script>
<script>
const button=document.getElementById("language");
let language=localStorage.getItem("sweetgold-language")||(navigator.language.toLowerCase().startsWith("zh")?"zh":"en");
if(!["en","zh"].includes(language)) language="en";
function translate(){{
  document.documentElement.lang=language==="zh"?"zh-CN":"en";
  document.querySelectorAll("[data-en]").forEach(el=>el.textContent=el.dataset[language]??el.dataset.en??"");
  button.textContent=language==="en"?"中文":"English";
  document.title=language==="en"?"BeeBench Report":"BeeBench 评估报告";
}}
button.addEventListener("click",()=>{{language=language==="en"?"zh":"en";localStorage.setItem("sweetgold-language",language);translate();}});
translate();
</script></main></html>"""
    path = output / "index.html"
    path.write_text(document, encoding="utf-8")
    (output / "results.json").write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path
