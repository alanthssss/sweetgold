import { cp, mkdir, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputRoot = resolve(siteRoot, "pages-dist");
const workerUrl = pathToFileURL(resolve(siteRoot, "dist/server/index.js"));
workerUrl.searchParams.set("export", Date.now().toString());
const { default: worker } = await import(workerUrl.href);

function addRepositoryBasePath(html, language) {
  const localized = language === "zh-CN"
    ? html.replace('<html lang="en">', '<html lang="zh-CN">')
    : html;
  return localized
    .replace(/<script[\s\S]*?<\/script>/g, "")
    .replaceAll('href="/', 'href="/sweetgold/')
    .replaceAll('src="/', 'src="/sweetgold/')
    .replaceAll('href="/sweetgold/zh"', 'href="/sweetgold/zh/"')
    .replaceAll('https://alanthssss.github.io/og.png', 'https://alanthssss.github.io/sweetgold/og.png')
    .replaceAll('href="https://alanthssss.github.io/"', 'href="https://alanthssss.github.io/sweetgold/"')
    .replaceAll('href="https://alanthssss.github.io/zh"', 'href="https://alanthssss.github.io/sweetgold/zh/"');
}

async function render(route, destination, language) {
  const response = await worker.fetch(
    new Request(`https://alanthssss.github.io${route}`, {
      headers: {
        accept: "text/html",
        "x-forwarded-host": "alanthssss.github.io",
        "x-forwarded-proto": "https",
      },
    }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
  if (!response.ok) throw new Error(`Failed to render ${route}: ${response.status}`);
  const output = resolve(outputRoot, destination);
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, addRepositoryBasePath(await response.text(), language));
}

await rm(outputRoot, { recursive: true, force: true });
await cp(resolve(siteRoot, "dist/client"), outputRoot, { recursive: true });
await render("/", "index.html", "en");
await render("/zh", "zh/index.html", "zh-CN");
await writeFile(resolve(outputRoot, ".nojekyll"), "");
console.log(`Exported GitHub Pages site to ${outputRoot}`);
