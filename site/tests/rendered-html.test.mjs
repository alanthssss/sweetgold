import assert from "node:assert/strict";
import { access } from "node:fs/promises";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request(`https://sweetgold.example${path}`, { headers: { accept: "text/html", "x-forwarded-host": "sweetgold.example", "x-forwarded-proto": "https" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the SweetGold launch page and social metadata", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>SweetGold — A Reproducible Multi-Agent AI Lab<\/title>/i);
  assert.match(html, /Teach a colony/);
  assert.match(html, /148\.47%/);
  assert.match(html, /Strategy Arena/i);
  assert.match(html, /ENGINEERING GUARANTEES/i);
  assert.match(html, /Verified model supply chain/i);
  assert.match(html, /M15/);
  assert.match(html, /href="\/zh"/);
  assert.match(html, /https:\/\/sweetgold\.example\/og\.png/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape/i);
});

test("renders an equal Chinese route with bilingual terminology", async () => {
  const response = await render("/zh");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /可复现的多智能体 AI 实验室/);
  assert.match(html, /最新完成成果 · M15/);
  assert.match(html, /最新晋级策略 · M14/);
  assert.match(html, /安全约束 CONSTRAINTS/);
  assert.match(html, /工程保障 \/ ENGINEERING GUARANTEES/);
  assert.match(html, /经验证的模型供应链/);
  assert.match(html, /M14/);
  assert.match(html, /M15/);
  assert.match(html, /href="\/"/);
});

test("removes disposable starter UI and ships the social card", async () => {
  await assert.rejects(access(new URL("../app/_sites-preview", import.meta.url)));
  await access(new URL("../public/og.png", import.meta.url));
});
