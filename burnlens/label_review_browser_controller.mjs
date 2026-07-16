import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";


const OBSERVATION_SCHEMA_VERSION = "burnlens-label-review-browser-observation-v0.1.0";
const EXPECTED_TITLE = "BurnLens offline label-review workbench";
const EXPECTED_PACKET_ID = "LABEL-REVIEW-PACKET-2026-001";
const EXPECTED_PACKET_RUN_ID = "BL-2026-07-16-label-review-packet-r001";
const EXPECTED_REVIEWER_ID = "browser-qa-fixture-not-human";
const EXPECTED_EXPERIENCE = "Automated browser QA fixture; not a human response.";
const EXPECTED_UNIT_COUNT = 56;
const EXPECTED_BLIND_PAGE_COUNT = 8;
const PARTIAL_UNIT_COUNT = 7;
const LABELS = ["burned", "background", "uncertain", "unusable"];
const SUFFICIENCY = ["sufficient", "limited", "insufficient"];
const CONFIDENCE = ["high", "medium", "low"];
const REASONS = [
  "pre-post-change",
  "persistent-darkening",
  "vegetation-loss",
  "source-context-support",
  "source-context-conflict",
  "cloud-smoke-shadow",
  "registration-concern",
  "boundary-ambiguity",
  "low-severity-ambiguity",
  "non-fire-change-possible",
  "other",
];


function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith("--") || value === undefined) {
      throw new Error("arguments must be supplied as --name value pairs");
    }
    values[key.slice(2)] = value;
  }
  for (const required of ["browser", "html", "output-directory"]) {
    if (!values[required]) {
      throw new Error(`missing required argument --${required}`);
    }
  }
  return values;
}


function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}


async function waitFor(predicate, description, timeoutMilliseconds = 15000) {
  const deadline = Date.now() + timeoutMilliseconds;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      const value = await predicate();
      if (value) {
        return value;
      }
    } catch (error) {
      lastError = error;
    }
    await sleep(100);
  }
  const suffix = lastError ? `: ${lastError.message}` : "";
  throw new Error(`timed out waiting for ${description}${suffix}`);
}


async function waitForFile(filePath, description, timeoutMilliseconds = 15000) {
  return waitFor(
    async () => {
      const stats = await fs.stat(filePath);
      return stats.isFile() && stats.size > 0 ? stats : null;
    },
    description,
    timeoutMilliseconds,
  );
}


async function sha256File(filePath) {
  const payload = await fs.readFile(filePath);
  return createHash("sha256").update(payload).digest("hex");
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
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(
        () => reject(new Error(`timed out opening DevTools websocket ${this.url}`)),
        10000,
      );
      this.socket.addEventListener("open", () => {
        clearTimeout(timeout);
        resolve();
      }, { once: true });
      this.socket.addEventListener("error", () => {
        clearTimeout(timeout);
        reject(new Error(`failed to open DevTools websocket ${this.url}`));
      }, { once: true });
    });
    this.socket.addEventListener("message", (event) => this.#onMessage(event.data));
    this.socket.addEventListener("close", () => {
      for (const { reject } of this.pending.values()) {
        reject(new Error("DevTools websocket closed"));
      }
      this.pending.clear();
    });
  }

  #onMessage(payload) {
    const message = JSON.parse(payload);
    if (message.id) {
      const pending = this.pending.get(message.id);
      if (!pending) {
        return;
      }
      this.pending.delete(message.id);
      if (message.error) {
        pending.reject(new Error(`${pending.method}: ${message.error.message}`));
      } else {
        pending.resolve(message.result ?? {});
      }
      return;
    }
    const listeners = this.listeners.get(message.method) ?? [];
    for (const listener of listeners) {
      listener(message.params ?? {});
    }
  }

  on(method, listener) {
    const listeners = this.listeners.get(method) ?? [];
    listeners.push(listener);
    this.listeners.set(method, listeners);
  }

  send(method, params = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return Promise.reject(new Error("DevTools websocket is not open"));
    }
    const id = this.nextId++;
    const payload = JSON.stringify({ id, method, params });
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject, method });
      this.socket.send(payload);
    });
  }

  close() {
    this.socket?.close();
  }
}


async function evaluate(client, expression) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
    userGesture: true,
  });
  if (result.exceptionDetails) {
    const description = result.exceptionDetails.exception?.description
      ?? result.exceptionDetails.text
      ?? "unknown page exception";
    throw new Error(description);
  }
  return result.result?.value;
}


async function captureScreenshot(client, outputPath) {
  const result = await client.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  await fs.writeFile(outputPath, Buffer.from(result.data, "base64"), { flag: "wx" });
}


function pageSnapshotExpression() {
  return `(() => {
    const images = Array.from(document.querySelectorAll(".page-block > img"));
    const cards = Array.from(document.querySelectorAll(".response-card"));
    return {
      title: document.title,
      ready_state: document.readyState,
      unit_fieldsets: cards.length,
      blind_images: images.length,
      loaded_blind_images: images.filter((image) => image.complete && image.naturalWidth === 1800 && image.naturalHeight >= 2500).length,
      progress: document.getElementById("progress").textContent,
      review_summary: document.getElementById("review-summary").textContent,
      error_summary: document.getElementById("error-summary").textContent,
      error_summary_visible: document.getElementById("error-summary").classList.contains("show"),
      invalid_cards: document.querySelectorAll(".response-card.invalid").length,
      active_element_id: document.activeElement?.id || null,
      viewport_width: window.innerWidth,
      viewport_height: window.innerHeight,
      document_width: document.documentElement.scrollWidth,
      horizontal_overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
      local_storage_entries: localStorage.length,
      cookie: document.cookie,
    };
  })()`;
}


function fillPartialExpression() {
  return `(() => {
    const setText = (id, value) => {
      const control = document.getElementById(id);
      control.value = value;
      control.dispatchEvent(new Event("input", {bubbles:true}));
      control.dispatchEvent(new Event("change", {bubbles:true}));
    };
    setText("reviewer-id", ${JSON.stringify(EXPECTED_REVIEWER_ID)});
    setText("reviewer-experience", ${JSON.stringify(EXPECTED_EXPERIENCE)});
    for (const id of ["independent", "not-seen", "attestation"]) {
      const control = document.getElementById(id);
      control.checked = true;
      control.dispatchEvent(new Event("change", {bubbles:true}));
    }
    const cards = Array.from(document.querySelectorAll(".response-card")).slice(0, ${PARTIAL_UNIT_COUNT});
    cards.forEach((card, index) => {
      const setSelect = (field, value) => {
        const control = card.querySelector('[data-field="' + field + '"]');
        control.value = value;
        control.dispatchEvent(new Event("change", {bubbles:true}));
      };
      setSelect("first_pass_label", ${JSON.stringify(LABELS)}[index % ${LABELS.length}]);
      setSelect("evidence_sufficiency", ${JSON.stringify(SUFFICIENCY)}[index % ${SUFFICIENCY.length}]);
      setSelect("confidence", ${JSON.stringify(CONFIDENCE)}[index % ${CONFIDENCE.length}]);
      const reason = card.querySelector('input[type="checkbox"][value="' + ${JSON.stringify(REASONS)}[index % ${REASONS.length}] + '"]');
      reason.checked = true;
      reason.dispatchEvent(new Event("change", {bubbles:true}));
    });
    return document.getElementById("progress").textContent;
  })()`;
}


function clearFormExpression() {
  return `(() => {
    const form = document.getElementById("review-form");
    form.reset();
    form.dispatchEvent(new Event("change", {bubbles:true}));
    return {
      progress: document.getElementById("progress").textContent,
      reviewer_id: document.getElementById("reviewer-id").value,
    };
  })()`;
}


function completeAllExpression() {
  return `(() => {
    const labels = ${JSON.stringify(LABELS)};
    const sufficiency = ${JSON.stringify(SUFFICIENCY)};
    const confidence = ${JSON.stringify(CONFIDENCE)};
    const reasons = ${JSON.stringify(REASONS)};
    const setText = (id, value) => {
      const control = document.getElementById(id);
      control.value = value;
      control.dispatchEvent(new Event("input", {bubbles:true}));
      control.dispatchEvent(new Event("change", {bubbles:true}));
    };
    setText("reviewer-id", ${JSON.stringify(EXPECTED_REVIEWER_ID)});
    setText("reviewer-experience", ${JSON.stringify(EXPECTED_EXPERIENCE)});
    for (const id of ["independent", "not-seen", "attestation"]) {
      const control = document.getElementById(id);
      control.checked = true;
      control.dispatchEvent(new Event("change", {bubbles:true}));
    }
    Array.from(document.querySelectorAll(".response-card")).forEach((card, index) => {
      const setSelect = (field, value) => {
        const control = card.querySelector('[data-field="' + field + '"]');
        control.value = value;
        control.dispatchEvent(new Event("change", {bubbles:true}));
      };
      setSelect("first_pass_label", labels[index % labels.length]);
      setSelect("evidence_sufficiency", sufficiency[index % sufficiency.length]);
      setSelect("confidence", confidence[index % confidence.length]);
      card.querySelectorAll('input[type="checkbox"]').forEach((control) => {
        control.checked = control.value === reasons[index % reasons.length];
      });
      card.querySelector('input[type="checkbox"]:checked').dispatchEvent(new Event("change", {bubbles:true}));
      const notes = card.querySelector('[data-field="notes"]');
      notes.value = "";
    });
    return document.getElementById("progress").textContent;
  })()`;
}


async function main() {
  const args = parseArgs(process.argv.slice(2));
  const browserPath = path.resolve(args.browser);
  const htmlPath = path.resolve(args.html);
  const outputDirectory = path.resolve(args["output-directory"]);
  const profileDirectory = path.join(outputDirectory, "browser-profile");
  const downloadDirectory = path.join(outputDirectory, "downloads");
  const desktopScreenshotPath = path.join(outputDirectory, "desktop.png");
  const mobileScreenshotPath = path.join(outputDirectory, "mobile.png");
  const observationPath = path.join(outputDirectory, "observation.json");
  const draftName = `${EXPECTED_PACKET_ID}-DRAFT-${EXPECTED_REVIEWER_ID}.json`;
  const responseName = `${EXPECTED_PACKET_ID}-RESPONSE-${EXPECTED_REVIEWER_ID}.json`;
  const draftPath = path.join(downloadDirectory, draftName);
  const responsePath = path.join(downloadDirectory, responseName);

  await fs.mkdir(outputDirectory, { recursive: false });
  await fs.mkdir(profileDirectory);
  await fs.mkdir(downloadDirectory);
  const htmlStats = await fs.stat(htmlPath);
  const browserStats = await fs.stat(browserPath);
  if (!htmlStats.isFile() || !browserStats.isFile()) {
    throw new Error("browser and HTML inputs must be files");
  }

  const htmlUrl = pathToFileURL(htmlPath).href;
  const browserArguments = [
    "--headless=new",
    "--remote-debugging-address=127.0.0.1",
    "--remote-debugging-port=0",
    `--user-data-dir=${profileDirectory}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-breakpad",
    "--disable-crash-reporter",
    "--disable-search-engine-choice-screen",
    "--metrics-recording-only",
    "--password-store=basic",
    "--allow-file-access-from-files",
    "--window-size=1440,1000",
    htmlUrl,
  ];
  const browserProcess = spawn(browserPath, browserArguments, {
    windowsHide: true,
    stdio: ["ignore", "pipe", "pipe"],
  });
  const startupMessages = [];
  browserProcess.stdout.on("data", (chunk) => startupMessages.push(chunk.toString("utf8")));
  browserProcess.stderr.on("data", (chunk) => startupMessages.push(chunk.toString("utf8")));

  let browserClient = null;
  let pageClient = null;
  try {
    const activePortPath = path.join(profileDirectory, "DevToolsActivePort");
    await waitForFile(activePortPath, "Chrome DevToolsActivePort");
    const [portText, browserWebSocketPath] = (
      await fs.readFile(activePortPath, "utf8")
    ).trim().split(/\r?\n/);
    const port = Number(portText);
    if (!Number.isInteger(port) || !browserWebSocketPath) {
      throw new Error("Chrome DevToolsActivePort is invalid");
    }
    const endpoint = `http://127.0.0.1:${port}`;
    const version = await waitFor(
      async () => {
        const response = await fetch(`${endpoint}/json/version`);
        return response.ok ? response.json() : null;
      },
      "Chrome DevTools version endpoint",
    );
    const targets = await waitFor(
      async () => {
        const response = await fetch(`${endpoint}/json/list`);
        if (!response.ok) {
          return null;
        }
        const values = await response.json();
        return values.some((item) => item.type === "page") ? values : null;
      },
      "Chrome page target",
    );
    const pageTarget = targets.find((item) => item.type === "page");
    browserClient = new CdpClient(version.webSocketDebuggerUrl);
    await browserClient.connect();
    pageClient = new CdpClient(pageTarget.webSocketDebuggerUrl);
    await pageClient.connect();

    const consoleErrors = [];
    const runtimeExceptions = [];
    const logErrors = [];
    const requestSchemes = {};
    const externalRequestSchemes = {};
    pageClient.on("Runtime.consoleAPICalled", (event) => {
      if (event.type === "error" || event.type === "assert") {
        consoleErrors.push(event.type);
      }
    });
    pageClient.on("Runtime.exceptionThrown", (event) => {
      runtimeExceptions.push(event.exceptionDetails?.text ?? "runtime exception");
    });
    pageClient.on("Log.entryAdded", (event) => {
      if (event.entry?.level === "error") {
        logErrors.push(event.entry.source ?? "browser");
      }
    });
    pageClient.on("Network.requestWillBeSent", (event) => {
      const url = event.request?.url ?? "";
      let scheme = "unknown";
      try {
        scheme = new URL(url).protocol.replace(":", "");
      } catch {
        scheme = "invalid";
      }
      requestSchemes[scheme] = (requestSchemes[scheme] ?? 0) + 1;
      if (!["file", "blob", "data"].includes(scheme)) {
        externalRequestSchemes[scheme] = (externalRequestSchemes[scheme] ?? 0) + 1;
      }
    });

    await Promise.all([
      pageClient.send("Page.enable"),
      pageClient.send("Runtime.enable"),
      pageClient.send("DOM.enable"),
      pageClient.send("Network.enable"),
      pageClient.send("Log.enable"),
    ]);
    await browserClient.send("Browser.setDownloadBehavior", {
      behavior: "allow",
      downloadPath: downloadDirectory,
      eventsEnabled: true,
    });
    await pageClient.send("Emulation.setDeviceMetricsOverride", {
      width: 1440,
      height: 1000,
      deviceScaleFactor: 1,
      mobile: false,
      screenWidth: 1440,
      screenHeight: 1000,
    });
    await pageClient.send("Page.navigate", { url: htmlUrl });
    await waitFor(
      async () => {
        const value = await evaluate(pageClient, "document.readyState");
        return value === "complete" ? value : null;
      },
      "workbench document readiness",
    );
    await waitFor(
      async () => {
        const snapshot = await evaluate(pageClient, pageSnapshotExpression());
        return snapshot.loaded_blind_images === EXPECTED_BLIND_PAGE_COUNT ? snapshot : null;
      },
      "all proposal-blinded images",
    );

    const initial = await evaluate(pageClient, pageSnapshotExpression());
    if (
      initial.title !== EXPECTED_TITLE
      || initial.unit_fieldsets !== EXPECTED_UNIT_COUNT
      || initial.blind_images !== EXPECTED_BLIND_PAGE_COUNT
      || initial.loaded_blind_images !== EXPECTED_BLIND_PAGE_COUNT
    ) {
      throw new Error("initial browser surface does not match the handoff contract");
    }

    await evaluate(
      pageClient,
      'document.getElementById("review-button").click(); true',
    );
    const invalidReview = await evaluate(pageClient, pageSnapshotExpression());
    await evaluate(
      pageClient,
      'document.getElementById("export-button").click(); true',
    );
    await sleep(500);
    const blockedExport = await evaluate(pageClient, pageSnapshotExpression());
    const responseExistsAfterBlockedExport = await fs.stat(responsePath)
      .then(() => true)
      .catch(() => false);

    const partialProgress = await evaluate(pageClient, fillPartialExpression());
    await evaluate(
      pageClient,
      'document.getElementById("save-draft-button").click(); true',
    );
    const draftStats = await waitForFile(draftPath, "downloaded draft JSON");
    const draft = JSON.parse(await fs.readFile(draftPath, "utf8"));
    const cleared = await evaluate(pageClient, clearFormExpression());

    const document = await pageClient.send("DOM.getDocument", { depth: -1, pierce: true });
    const fileInput = await pageClient.send("DOM.querySelector", {
      nodeId: document.root.nodeId,
      selector: "#load-draft",
    });
    if (!fileInput.nodeId) {
      throw new Error("draft file input is unavailable");
    }
    await pageClient.send("DOM.setFileInputFiles", {
      files: [draftPath],
      nodeId: fileInput.nodeId,
    });
    await waitFor(
      async () => {
        const snapshot = await evaluate(pageClient, pageSnapshotExpression());
        return snapshot.review_summary.startsWith("Draft loaded.") ? snapshot : null;
      },
      "draft load completion",
    );
    const restored = await evaluate(
      pageClient,
      `(() => ({
        snapshot: ${pageSnapshotExpression()},
        reviewer_id: document.getElementById("reviewer-id").value,
        reviewer_experience: document.getElementById("reviewer-experience").value,
        first_label: document.querySelector(".response-card [data-field=first_pass_label]").value,
      }))()`,
    );

    const completedProgress = await evaluate(pageClient, completeAllExpression());
    await evaluate(
      pageClient,
      'document.getElementById("review-button").click(); true',
    );
    const completedReview = await evaluate(pageClient, pageSnapshotExpression());
    await evaluate(
      pageClient,
      'document.getElementById("export-button").click(); true',
    );
    const responseStats = await waitForFile(responsePath, "downloaded completed response JSON");
    await waitFor(
      async () => {
        const snapshot = await evaluate(pageClient, pageSnapshotExpression());
        return snapshot.review_summary.startsWith("Completed response reviewed.")
          ? snapshot
          : null;
      },
      "completed response export summary",
    );
    await evaluate(
      pageClient,
      'document.getElementById("finalize-heading").scrollIntoView({block:"start"}); true',
    );
    await sleep(150);
    const desktop = await evaluate(pageClient, pageSnapshotExpression());
    await captureScreenshot(pageClient, desktopScreenshotPath);

    await pageClient.send("Emulation.setDeviceMetricsOverride", {
      width: 390,
      height: 844,
      deviceScaleFactor: 1,
      mobile: true,
      screenWidth: 390,
      screenHeight: 844,
    });
    await evaluate(pageClient, "window.scrollTo(0, 0); true");
    await sleep(150);
    const mobile = await evaluate(pageClient, pageSnapshotExpression());
    await captureScreenshot(pageClient, mobileScreenshotPath);
    await pageClient.send("Emulation.clearDeviceMetricsOverride");

    const response = JSON.parse(await fs.readFile(responsePath, "utf8"));
    const labelCounts = {};
    for (const item of response.responses ?? []) {
      labelCounts[item.first_pass_label] = (labelCounts[item.first_pass_label] ?? 0) + 1;
    }
    const observation = {
      observation_schema_version: OBSERVATION_SCHEMA_VERSION,
      node_version: process.version,
      browser: {
        product: version.Browser,
        protocol_version: version["Protocol-Version"],
        user_agent: version["User-Agent"],
        javascript_version: version["V8-Version"],
      },
      input: {
        html_filename: path.basename(htmlPath),
        packet_id: EXPECTED_PACKET_ID,
        packet_run_id: EXPECTED_PACKET_RUN_ID,
      },
      initial,
      invalid_state: {
        review: invalidReview,
        blocked_export: blockedExport,
        response_file_created: responseExistsAfterBlockedExport,
      },
      draft_roundtrip: {
        partial_progress: partialProgress,
        draft_filename: draftName,
        draft_bytes: draftStats.size,
        draft_sha256: await sha256File(draftPath),
        draft_completed: draft.completed,
        draft_response_count: draft.responses?.length ?? null,
        cleared,
        restored,
      },
      completed_roundtrip: {
        progress_before_review: completedProgress,
        review: completedReview,
        response_filename: responseName,
        response_bytes: responseStats.size,
        response_sha256: await sha256File(responsePath),
        response_completed: response.completed,
        response_reviewer_id: response.reviewer?.reviewer_id ?? null,
        response_count: response.responses?.length ?? null,
        label_counts: labelCounts,
      },
      viewports: {
        desktop,
        mobile,
        desktop_screenshot: {
          filename: path.basename(desktopScreenshotPath),
          bytes: (await fs.stat(desktopScreenshotPath)).size,
          sha256: await sha256File(desktopScreenshotPath),
        },
        mobile_screenshot: {
          filename: path.basename(mobileScreenshotPath),
          bytes: (await fs.stat(mobileScreenshotPath)).size,
          sha256: await sha256File(mobileScreenshotPath),
        },
      },
      runtime: {
        console_error_count: consoleErrors.length,
        runtime_exception_count: runtimeExceptions.length,
        log_error_count: logErrors.length,
        request_schemes: requestSchemes,
        external_request_schemes: externalRequestSchemes,
        startup_message_count: startupMessages.length,
      },
    };
    await fs.writeFile(
      observationPath,
      `${JSON.stringify(observation, null, 2)}\n`,
      { encoding: "utf8", flag: "wx" },
    );
    process.stdout.write(`${observationPath}\n`);
  } finally {
    try {
      await browserClient?.send("Browser.close");
    } catch {
      browserProcess.kill();
    }
    pageClient?.close();
    browserClient?.close();
    await Promise.race([
      new Promise((resolve) => browserProcess.once("exit", resolve)),
      sleep(3000),
    ]);
    if (browserProcess.exitCode === null) {
      browserProcess.kill();
    }
  }
}


main().catch((error) => {
  process.stderr.write(`LABEL_REVIEW_BROWSER_CONTROLLER_FAILED: ${error.message}\n`);
  process.exitCode = 2;
});
