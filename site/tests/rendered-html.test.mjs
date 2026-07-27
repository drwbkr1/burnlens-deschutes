import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { access, readFile, stat } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = path.resolve(siteRoot, "..");

async function render(pathname = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request(`http://localhost${pathname}`, {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

async function sha256(filePath) {
  return createHash("sha256").update(await readFile(filePath)).digest("hex");
}

test("renders the evidence-led BurnLens portfolio truth", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>BurnLens .* Evidence before confidence<\/title>/i);
  assert.match(html, /The model failed\./);
  assert.match(html, /The evidence held\./);
  assert.match(html, /RBR baseline/);
  assert.match(html, /Dice 1\.000/);
  assert.match(html, /Bounded U-Net/);
  assert.match(html, /Dice 0\.299/);
  assert.match(html, /Rejected/);
  assert.match(html, /No model superiority/);
  assert.match(html, /Official sources govern/);
  assert.match(html, /Not emergency guidance/);
  assert.match(html, /owner-confirmed, not independent ground truth/);
  assert.match(html, /WCP-002/);
  assert.match(html, /0% MTBS overlap/);
  assert.match(html, /v0\.56\.0-baseline-first-portfolio-release/);
  assert.match(html, /Skip to evidence/);
  assert.match(html, /id="evidence"[^>]*tabindex="-1"/i);
  assert.match(html, /blob\/main\/docs\/case-study\/BURNLENS_CASE_STUDY\.md/);

  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|Codex is working/i);
  assert.doesNotMatch(html, /react-loading-skeleton/i);
  assert.doesNotMatch(html, /C:\\|file:\/\/|LOCALAPPDATA|Downloads\\|OneDrive\\/i);
  assert.doesNotMatch(html, /token|password|secret|retrieval url/i);
});

test("keeps every public evidence copy bound to its canonical tracked source", async () => {
  const manifestPath = path.join(siteRoot, "public", "evidence", "manifest.json");
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));

  assert.equal(manifest.manifest_version, "burnlens-sites-evidence-manifest-v0.1.0");
  assert.equal(manifest.release_version, "0.56.0");
  assert.equal(manifest.release_tag, "v0.56.0-baseline-first-portfolio-release");
  assert.equal(manifest.entries.length, 13);

  for (const entry of manifest.entries) {
    const publicPath = path.join(siteRoot, entry.public_path);
    const sourcePath = path.join(repositoryRoot, entry.source_path);
    const [publicInfo, sourceInfo, publicHash, sourceHash] = await Promise.all([
      stat(publicPath),
      stat(sourcePath),
      sha256(publicPath),
      sha256(sourcePath),
    ]);

    assert.equal(publicInfo.size, entry.bytes, entry.public_path);
    assert.equal(sourceInfo.size, entry.bytes, entry.source_path);
    assert.equal(publicHash, entry.sha256, entry.public_path);
    assert.equal(sourceHash, entry.sha256, entry.source_path);
  }
});

test("ships the complete repository-owned reviewer route without private state", async () => {
  const required = [
    "public/evidence/ward-creek/index.html",
    "public/evidence/ward-creek/overlay-quicklook.png",
    "public/evidence/baseline/index.html",
    "public/evidence/baseline/evaluation.png",
    "public/evidence/model/index.html",
    "public/evidence/model/evaluation.png",
    "public/evidence/model/MODEL-CARD.md",
    "public/models/burnlens-unet-binary-v0.1.0/BOUNDED-UNET-TRAINING-2026-001.html",
    "public/evaluation/phase-three/bounded-unet-test-v0.1.0/BOUNDED-UNET-TEST-EVALUATION-2026-001.html",
  ];

  await Promise.all(required.map((relative) => access(path.join(siteRoot, relative))));

  const page = await readFile(path.join(siteRoot, "app", "page.tsx"), "utf8");
  const layout = await readFile(path.join(siteRoot, "app", "layout.tsx"), "utf8");
  const packageJson = JSON.parse(
    await readFile(path.join(siteRoot, "package.json"), "utf8"),
  );

  assert.equal(packageJson.name, "burnlens-portfolio-site");
  assert.equal(packageJson.version, "0.56.0");
  assert.match(page, /\/evidence\/ward-creek\//);
  assert.match(page, /\/evidence\/baseline\//);
  assert.match(page, /\/evidence\/model\//);
  assert.match(layout, /card: "summary"/);
  assert.doesNotMatch(layout, /og:image|images:/i);
});
