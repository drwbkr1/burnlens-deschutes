import { createHash } from "node:crypto";
import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SURFACE_ID = "OWNER-REVIEW-SURFACE-2026-001";
const UNIT_COUNT = 56;
const RADIO_COUNT = 168;

function parseArgs(values) {
  const result = {};
  for (let index = 0; index < values.length; index += 2) {
    const key = values[index];
    if (!key?.startsWith("--") || values[index + 1] === undefined) {
      throw new Error("arguments must be --name value pairs");
    }
    result[key.slice(2)] = values[index + 1];
  }
  for (const key of ["browser", "html", "output-directory"]) {
    if (!result[key]) throw new Error(`missing --${key}`);
  }
  return result;
}

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function waitFor(callback, label, timeout = 15000) {
  const deadline = Date.now() + timeout;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      const value = await callback();
      if (value) return value;
    } catch (error) {
      lastError = error;
    }
    await sleep(75);
  }
  throw new Error(`${label} timed out${lastError ? `: ${lastError.message}` : ""}`);
}

async function waitForFile(directory, prefix) {
  return waitFor(async () => {
    const names = await fs.readdir(directory).catch(() => []);
    const name = names.find((item) => item.startsWith(prefix) && item.endsWith(".json") && !item.endsWith(".crdownload"));
    if (!name) return null;
    const file = path.join(directory, name);
    const stats = await fs.stat(file);
    return stats.size > 0 ? file : null;
  }, `download ${prefix}`);
}

function sha256(data) {
  return createHash("sha256").update(data).digest("hex");
}

class CdpClient {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
  }
  async connect() {
    this.socket = new WebSocket(this.url);
    this.socket.addEventListener("message", (event) => this.handle(JSON.parse(event.data)));
    await new Promise((resolve, reject) => {
      this.socket.addEventListener("open", resolve, { once: true });
      this.socket.addEventListener("error", reject, { once: true });
    });
  }
  handle(message) {
    if (message.id) {
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(`${pending.method}: ${message.error.message}`));
      else pending.resolve(message.result ?? {});
      return;
    }
    for (const listener of this.listeners.get(message.method) ?? []) listener(message.params ?? {});
  }
  on(method, listener) {
    const values = this.listeners.get(method) ?? [];
    values.push(listener);
    this.listeners.set(method, values);
  }
  send(method, params = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) throw new Error("DevTools socket is not open");
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject, method });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }
  close() { this.socket?.close(); }
}

async function evaluate(client, expression) {
  const result = await client.send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true, userGesture: true });
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.exception?.description ?? result.exceptionDetails.text ?? "page exception");
  }
  return result.result?.value;
}

async function screenshot(client, outputPath) {
  const value = await client.send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
  await fs.writeFile(outputPath, Buffer.from(value.data, "base64"), { flag: "wx" });
}

const metricsExpression = `(() => ({
  title: document.title,
  ready: document.readyState,
  width: innerWidth,
  height: innerHeight,
  document_width: document.documentElement.scrollWidth,
  horizontal_overflow: document.documentElement.scrollWidth > innerWidth + 1,
  unit_count: document.querySelectorAll('[data-sample]').length,
  radio_count: document.querySelectorAll('input[type=radio]').length,
  image_count: document.images.length,
  loaded_images: Array.from(document.images).filter(i => i.complete && i.naturalWidth === 1800).length,
  broken_images: Array.from(document.images).filter(i => i.complete && i.naturalWidth === 0).length,
  local_evidence_scrollers: Array.from(document.querySelectorAll('.evidence-scroll')).filter(e => e.scrollWidth > e.clientWidth).length,
  progress: document.getElementById('progress').textContent,
  status: document.getElementById('status').textContent,
  invalid_units: document.querySelectorAll('.unit.invalid').length,
  disabled_radios: document.querySelectorAll('input[type=radio]:disabled').length,
  overflowing_elements: Array.from(document.querySelectorAll('body *')).filter(e => { const r=e.getBoundingClientRect(); return r.right > innerWidth + 1 || r.left < -1; }).slice(0,20).map(e => ({tag:e.tagName, id:e.id, classes:e.className, left:Math.round(e.getBoundingClientRect().left), right:Math.round(e.getBoundingClientRect().right), scrollWidth:e.scrollWidth, clientWidth:e.clientWidth})),
}))()`;

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const browserPath = path.resolve(args.browser);
  const htmlPath = path.resolve(args.html);
  const outputDirectory = path.resolve(args["output-directory"]);
  const profileDirectory = path.join(outputDirectory, "profile");
  const downloadDirectory = path.join(outputDirectory, "downloads");
  await fs.mkdir(outputDirectory, { recursive: false });
  await fs.mkdir(profileDirectory);
  await fs.mkdir(downloadDirectory);
  const desktopPath = path.join(outputDirectory, "desktop.png");
  const mobilePath = path.join(outputDirectory, "mobile.png");
  const observationPath = path.join(outputDirectory, "observation.json");
  const htmlBytes = await fs.readFile(htmlPath);
  const htmlUrl = pathToFileURL(htmlPath).href;
  const child = spawn(browserPath, [
    "--headless=new", "--remote-debugging-address=127.0.0.1", "--remote-debugging-port=0",
    `--user-data-dir=${profileDirectory}`, "--no-first-run", "--no-default-browser-check",
    "--disable-background-networking", "--disable-component-update", "--disable-sync",
    "--disable-breakpad", "--allow-file-access-from-files", "--window-size=1440,1000", htmlUrl,
  ], { windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
  const startup = [];
  child.stdout.on("data", (chunk) => startup.push(chunk.toString("utf8")));
  child.stderr.on("data", (chunk) => startup.push(chunk.toString("utf8")));
  let browserClient = null;
  let pageClient = null;
  try {
    const portFile = path.join(profileDirectory, "DevToolsActivePort");
    await waitFor(async () => fs.readFile(portFile, "utf8").catch(() => null), "DevToolsActivePort");
    const [port, browserSocket] = (await fs.readFile(portFile, "utf8")).trim().split(/\r?\n/);
    const endpoint = `http://127.0.0.1:${port}`;
    const version = await waitFor(async () => {
      const response = await fetch(`${endpoint}/json/version`);
      return response.ok ? response.json() : null;
    }, "browser version");
    const targets = await waitFor(async () => {
      const response = await fetch(`${endpoint}/json/list`);
      if (!response.ok) return null;
      const values = await response.json();
      return values.find((item) => item.type === "page") ? values : null;
    }, "page target");
    browserClient = new CdpClient(version.webSocketDebuggerUrl);
    pageClient = new CdpClient(targets.find((item) => item.type === "page").webSocketDebuggerUrl);
    await browserClient.connect();
    await pageClient.connect();
    const consoleErrors = [];
    const runtimeExceptions = [];
    const logErrors = [];
    const schemes = {};
    pageClient.on("Runtime.consoleAPICalled", (event) => { if (["error", "assert"].includes(event.type)) consoleErrors.push(event.type); });
    pageClient.on("Runtime.exceptionThrown", (event) => runtimeExceptions.push(event.exceptionDetails?.text ?? "runtime exception"));
    pageClient.on("Log.entryAdded", (event) => { if (event.entry?.level === "error") logErrors.push(event.entry.source ?? "browser"); });
    pageClient.on("Network.requestWillBeSent", (event) => {
      const scheme = (() => { try { return new URL(event.request.url).protocol.replace(":", ""); } catch { return "invalid"; } })();
      schemes[scheme] = (schemes[scheme] ?? 0) + 1;
    });
    await Promise.all(["Page", "Runtime", "DOM", "Network", "Log"].map((domain) => pageClient.send(`${domain}.enable`)));
    await browserClient.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: downloadDirectory, eventsEnabled: true });
    await pageClient.send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false, screenWidth: 1440, screenHeight: 1000 });
    await pageClient.send("Page.navigate", { url: htmlUrl });
    await waitFor(async () => (await evaluate(pageClient, metricsExpression)).loaded_images === 112, "all evidence images");
    const initial = await evaluate(pageClient, metricsExpression);
    if (initial.unit_count !== UNIT_COUNT || initial.radio_count !== RADIO_COUNT || initial.broken_images !== 0) throw new Error("surface inventory mismatch");
    await evaluate(pageClient, `document.getElementById('review-complete').click(); true`);
    const incomplete = await evaluate(pageClient, metricsExpression);
    if (incomplete.invalid_units !== UNIT_COUNT) throw new Error("incomplete review did not fail visibly");
    await evaluate(pageClient, `(() => { const values=['yes','no','uncertain']; document.querySelectorAll('[data-sample]').forEach((card,index) => { const radio=card.querySelector('input[value="'+values[index%3]+'"]'); radio.checked=true; radio.dispatchEvent(new Event('change',{bubbles:true})); }); const a=document.getElementById('attestation'); a.checked=true; a.dispatchEvent(new Event('change',{bubbles:true})); return true; })()`);
    await evaluate(pageClient, `document.getElementById('review-complete').click(); true`);
    const complete = await evaluate(pageClient, metricsExpression);
    if (!complete.status.includes("ready for exact-byte export")) throw new Error("complete state did not pass");
    await evaluate(pageClient, `document.getElementById('save-draft').click(); true`);
    const draftPath = await waitForFile(downloadDirectory, `${SURFACE_ID}-DRAFT-`);
    const draftBytes = await fs.readFile(draftPath);
    const draft = JSON.parse(draftBytes.toString("utf8"));
    if (draft.completed !== false || draft.responses.length !== UNIT_COUNT) throw new Error("draft contract mismatch");
    await evaluate(pageClient, `(() => { document.querySelectorAll('input[type=radio]').forEach(i=>i.checked=false); document.getElementById('attestation').checked=false; document.querySelectorAll('[data-notes]').forEach(n=>n.value=''); document.dispatchEvent(new Event('change',{bubbles:true})); return true; })()`);
    const document = await pageClient.send("DOM.getDocument", { depth: -1, pierce: true });
    const fileInput = await pageClient.send("DOM.querySelector", { nodeId: document.root.nodeId, selector: "#load-response" });
    await pageClient.send("DOM.setFileInputFiles", { files: [draftPath], nodeId: fileInput.nodeId });
    await waitFor(async () => (await evaluate(pageClient, metricsExpression)).status.includes("Loaded exact bytes"), "draft reload");
    const restored = await evaluate(pageClient, metricsExpression);
    if (restored.progress !== "56 of 56 decisions") throw new Error("draft reload lost decisions");
    await evaluate(pageClient, `document.getElementById('export-complete').click(); true`);
    const responsePath = await waitForFile(downloadDirectory, `${SURFACE_ID}-RESPONSE-`);
    const responseBytes = await fs.readFile(responsePath);
    const response = JSON.parse(responseBytes.toString("utf8"));
    const counts = Object.fromEntries(["yes", "no", "uncertain"].map((value) => [value, response.responses.filter((item) => item.decision === value).length]));
    const locked = await evaluate(pageClient, metricsExpression);
    if (response.completed !== true || locked.disabled_radios !== RADIO_COUNT) throw new Error("response export did not lock");
    await screenshot(pageClient, desktopPath);
    await pageClient.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: false, screenWidth: 390, screenHeight: 844 });
    await evaluate(pageClient, `window.scrollTo(0,0); true`);
    await sleep(200);
    const mobile = await evaluate(pageClient, metricsExpression);
    await screenshot(pageClient, mobilePath);
    if (mobile.width !== 390 || mobile.horizontal_overflow || mobile.local_evidence_scrollers !== 112) {
      throw new Error(`mobile viewport or local-scroll contract failed: ${JSON.stringify(mobile)}`);
    }
    const observation = {
      observation_version: "owner-review-browser-qa-v0.1.0",
      input: { html: path.basename(htmlPath), bytes: htmlBytes.length, sha256: sha256(htmlBytes) },
      browser: { product: version.Browser, protocol: version["Protocol-Version"], user_agent: version["User-Agent"] },
      initial, incomplete, complete, restored, locked, mobile,
      draft: { filename: path.basename(draftPath), bytes: draftBytes.length, sha256: sha256(draftBytes), completed: draft.completed },
      response: { filename: path.basename(responsePath), bytes: responseBytes.length, sha256: sha256(responseBytes), completed: response.completed, counts },
      screenshots: {
        desktop: { bytes: (await fs.stat(desktopPath)).size, sha256: sha256(await fs.readFile(desktopPath)) },
        mobile: { bytes: (await fs.stat(mobilePath)).size, sha256: sha256(await fs.readFile(mobilePath)) },
      },
      runtime: { console_errors: consoleErrors, runtime_exceptions: runtimeExceptions, log_errors: logErrors, request_schemes: schemes, startup_message_count: startup.length },
      software_fixture_only: true,
      owner_response_created: false,
      label_created: false,
    };
    if (consoleErrors.length || runtimeExceptions.length || logErrors.length || Object.keys(schemes).some((item) => !["file", "blob", "data"].includes(item))) throw new Error("runtime or network boundary failed");
    await fs.writeFile(observationPath, `${JSON.stringify(observation, null, 2)}\n`, { flag: "wx" });
    process.stdout.write(`${observationPath}\n`);
  } finally {
    try { await browserClient?.send("Browser.close"); } catch { child.kill(); }
    pageClient?.close();
    browserClient?.close();
    await Promise.race([new Promise((resolve) => child.once("exit", resolve)), sleep(3000)]);
    if (child.exitCode === null) child.kill();
  }
}

main().catch((error) => {
  process.stderr.write(`OWNER_REVIEW_BROWSER_QA_FAILED: ${error.message}\n`);
  process.exitCode = 2;
});
