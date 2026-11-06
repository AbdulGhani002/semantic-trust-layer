const page = document.getElementById("page");
const flyout = document.getElementById("flyout");
const state = { filters: { action: "", found_by: "", kind: "" }, selected: null, tab: "summary", timer: null, busy: new Set() };

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (key === "value") node.value = value;
    else node.setAttribute(key, value === true ? "" : value);
  }
  node.append(...children.flat().filter((child) => child !== null && child !== undefined && child !== false));
  return node;
}

async function api(path, options) {
  const response = await fetch(path, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
  return body;
}

const post = (path, body) => api(path, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
const title = (text) => text.charAt(0).toUpperCase() + text.slice(1);
const kindName = (kind) => (kind === "qr" ? "QR code" : title(kind));
const clock = (seconds) => new Date(seconds * 1000).toLocaleTimeString();
const duration = (seconds) => (seconds >= 1 ? `${seconds.toFixed(1)} s` : `${Math.max(1, Math.round(seconds * 1000))} ms`);
const percent = (value) => (value === null || value === undefined ? "-" : `${(value * 100).toFixed(1)}%`);
const foundBy = (value) => (!value ? "-" : value.includes(",") ? "Both" : title(value.replace("-agent", "")));

function action(value) {
  return el("span", { class: value }, el("span", { class: "sq" }), title(value));
}

function table(headers, rows, onRow) {
  return el(
    "table",
    {},
    el("thead", {}, el("tr", {}, headers.map((name) => el("th", {}, name)))),
    el("tbody", {}, rows)
  );
}

function hideWords(text, record) {
  const labels = record.verdict.labels;
  if (!text || !(labels.includes("hate") || labels.includes("abuse"))) return text;
  const words = [];
  for (const finding of record.verdict.findings) {
    for (const item of finding.evidence) {
      if (item.source === "text model") words.push(...item.detail.split("strongest words are ").pop().split(", "));
    }
  }
  return words.reduce((current, word) => {
    if (word.length < 3) return current;
    const pattern = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return current.replace(new RegExp(pattern, "gi"), (found) => found[0] + "*".repeat(found.length - 1));
  }, text);
}

function findingRows(finding) {
  const rows = [["Risk", finding.available ? finding.risk.toFixed(2) : "No information"]];
  for (const [name, value] of Object.entries(finding.scores)) rows.push([title(name.replace("review_", "review: ").replace("_", " ")), value.toFixed(3)]);
  if (finding.note) rows.push(["Note", finding.note]);
  if (finding.model) rows.push(["Model", finding.model]);
  rows.push(["Time", duration(finding.seconds)]);
  return rows;
}

const pairs = (rows) => el("dl", {}, rows.flatMap(([name, value]) => [el("dt", {}, name), el("dd", {}, String(value))]));

function evidence(record, finding) {
  if (!finding.evidence.length) return null;
  return el("ul", {}, finding.evidence.map((item) => el("li", {}, `${title(item.source)}: ${hideWords(item.detail, record)}`)));
}

function timing(verdict) {
  const [application, network] = verdict.findings;
  const longest = Math.max(application.seconds, network.seconds, 0.001);
  const line = (name, finding) =>
    el(
      "div",
      {},
      el("span", {}, name),
      el("span", {}, el("i", { style: `width:${Math.max(1, (finding.seconds / longest) * 100)}%` })),
      el("span", {}, duration(finding.seconds))
    );
  return el("div", { class: "timing" }, line("Application", application), line("Network", network));
}

function tabBody(record) {
  const { item, verdict, envelope } = record;
  const [application, network] = verdict.findings;
  if (state.tab === "application") {
    return [pairs(findingRows(application)), evidence(record, application)];
  }
  if (state.tab === "network") {
    return [pairs(findingRows(network)), evidence(record, network), item.flows.length ? el("h3", {}, "Recent connections") : null, item.flows.length ? flowTable(item.flows) : null];
  }
  if (state.tab === "signed") {
    const shown = JSON.parse(JSON.stringify(envelope));
    const payload = shown.payload.verdict;
    payload.findings = payload.findings.map((finding) => finding.agent);
    shown.payload.findings = shown.payload.findings.map((part) => ({ signer: part.signer, signature: part.signature }));
    return [
      pairs([["Signature", record.signature_valid ? "Valid, 3 signers" : "NOT VALID"], ["Method", "Ed25519"]]),
      el("pre", {}, hideWords(JSON.stringify(shown, null, 1), record)),
    ];
  }
  const shownText = hideWords([item.subject && `Subject: ${item.subject}`, item.text, item.qr_payloads.join("\n")].filter(Boolean).join("\n"), record);
  return [
    el("p", {}, hideWords(verdict.reason, record)),
    shownText ? [el("h3", {}, "Content"), el("pre", {}, shownText)] : null,
    el("h3", {}, "Both agents ran at the same time"),
    timing(verdict),
    el("h3", {}, "Application Agent"),
    pairs(findingRows(application).filter(([name]) => !["Model", "Time"].includes(name))),
    el("h3", {}, "Network Agent"),
    pairs(findingRows(network).filter(([name]) => !["Model", "Time"].includes(name))),
    el("h3", {}, "Record"),
    pairs([["Signature", record.signature_valid ? "Valid, 3 signers" : "NOT VALID"], ["Flagged by", verdict.flagged_by.map((name) => title(name.replace("-agent", " Agent"))).join(", ") || "Nobody alone"], ["Total time", duration(verdict.seconds)]]),
  ];
}

function flowTable(flows) {
  return table(
    ["Port", "Packets", "Bytes", "Time"],
    flows.slice(-8).reverse().map((flow) => el("tr", {}, el("td", {}, flow.dport), el("td", {}, flow.packets), el("td", {}, flow.bytes), el("td", {}, flow.duration.toFixed(2))))
  );
}

async function openItem(id) {
  state.selected = id;
  const record = await api(`/api/verdicts/${id}`);
  const { item, verdict } = record;
  const name = item.subject || item.file_name || (item.urls && item.urls[0]) || (item.qr_payloads && item.qr_payloads[0]) || title(item.kind);
  const render = () => {
    flyout.replaceChildren(
      el("button", { class: "close", title: "Close", onclick: closeItem }, "×"),
      el("h2", {}, hideWords(name, record)),
      el("div", {}, `${kindName(item.kind)}${item.recipient ? ` to ${item.recipient}` : ""} · ${title(verdict.action)} · Risk ${verdict.risk.toFixed(2)}`),
      el(
        "div",
        { class: "tabs" },
        [["summary", "Summary"], ["application", "Application Agent"], ["network", "Network Agent"], ["signed", "Signed record"]].map(([key, label]) =>
          el("button", { class: state.tab === key ? "on" : "", onclick: () => { state.tab = key; render(); } }, label)
        )
      ),
      ...tabBody(record).flat(2).filter(Boolean)
    );
  };
  render();
  flyout.hidden = false;
  document.querySelectorAll("tr.row").forEach((row) => row.classList.toggle("sel", row.dataset.id === id));
}

function closeItem() {
  state.selected = null;
  flyout.hidden = true;
  document.querySelectorAll("tr.sel").forEach((row) => row.classList.remove("sel"));
}

function verdictRows(rows) {
  return rows.map((row) =>
    el(
      "tr",
      { class: `row${row.id === state.selected ? " sel" : ""}`, "data-id": row.id, onclick: () => openItem(row.id) },
      el("td", { class: "nowrap" }, action(row.action)),
      el("td", {}, row.risk.toFixed(2)),
      el("td", { class: "nowrap" }, kindName(row.kind)),
      el("td", { class: "cut" }, row.summary),
      el("td", { class: "cut" }, row.sender || "-"),
      el("td", {}, foundBy(row.flagged_by)),
      el("td", { class: "cut" }, row.labels.replaceAll(",", ", ") || "-"),
      el("td", { class: "nowrap" }, clock(row.at))
    )
  );
}

const VERDICT_HEADERS = ["Action", "Risk", "Type", "Item", "From", "Found by", "Findings", "Time"];

function countsLine(stats) {
  const a = stats.actions;
  return `Checked ${stats.total} · Allowed ${a.allow || 0} · Warned ${a.warn || 0} · Flagged ${a.flag || 0} · Blocked ${a.block || 0}`;
}

async function queue() {
  const select = (key, label, options) =>
    el(
      "select",
      { "aria-label": label, onchange: (event) => { state.filters[key] = event.target.value; refresh(); } },
      options.map(([value, text]) => el("option", { value, ...(state.filters[key] === value ? { selected: true } : {}) }, text))
    );
  const body = el("tbody", {});
  const counts = el("span", { class: "right" });
  page.replaceChildren(
    el("h1", {}, "Verdict queue"),
    el(
      "div",
      { class: "bar" },
      el("button", { class: "primary", onclick: () => (location.hash = "#scenarios") }, "Run a scenario"),
      el("button", { class: "link", onclick: () => refresh() }, "Refresh"),
      el("button", { class: "link", onclick: async () => { await api("/api/verdicts", { method: "DELETE" }); closeItem(); refresh(); } }, "Clear"),
      counts
    ),
    el(
      "div",
      { class: "filters" },
      select("action", "Action", [["", "Action: Any"], ["block", "Blocked"], ["flag", "Flagged"], ["warn", "Warned"], ["allow", "Allowed"]]),
      select("found_by", "Found by", [["", "Found by: Any"], ["application", "Application Agent"], ["network", "Network Agent"], ["both", "Both agents"]]),
      select("kind", "Type", [["", "Type: Any"], ["email", "Email"], ["message", "Message"], ["link", "Link"], ["qr", "QR code"], ["file", "File"], ["session", "Session"]])
    ),
    el("table", {}, el("thead", {}, el("tr", {}, VERDICT_HEADERS.map((name) => el("th", {}, name)))), body),
    el("div", { class: "note", id: "queue-note" })
  );
  const refresh = async () => {
    const query = new URLSearchParams({ limit: 200, ...state.filters });
    const [rows, stats] = await Promise.all([api(`/api/verdicts?${query}`), api("/api/stats")]);
    if (!body.isConnected) return;
    counts.textContent = countsLine(stats);
    body.replaceChildren(...verdictRows(rows));
    document.getElementById("queue-note").textContent = rows.length ? "" : "Nothing here yet. Run a scenario to see both agents work.";
  };
  await refresh();
  state.timer = setInterval(refresh, 3000);
}

async function overview() {
  const [stats, health, rows] = await Promise.all([api("/api/stats"), api("/api/health"), api("/api/verdicts?limit=6")]);
  const flagged = rows.filter((row) => row.action === "flag" || row.action === "block");
  const state_ = (value, on) => (value ? on : "Not running");
  page.replaceChildren(
    el("h1", {}, "Overview"),
    el("p", { class: "lead" }, "Two AI agents check every item at the same time. The Application Agent reads what the content means. The Network Agent reads how the traffic behaves. The Coordinator joins both into one signed verdict."),
    el("div", { class: "bar" }, el("span", {}, countsLine(stats)), el("span", { class: "right" }, stats.total ? `Mean decision time ${duration(stats.mean_seconds)}` : "")),
    el(
      "div",
      { class: "grid" },
      el(
        "div",
        {},
        el("h2", {}, "Who found the problem"),
        table(
          ["Found by", "Items"],
          [["Application Agent alone", stats.found_by.application], ["Network Agent alone", stats.found_by.network], ["Both agents", stats.found_by.both]].map(([name, count]) => el("tr", {}, el("td", {}, name), el("td", {}, count || 0)))
        ),
        el("h2", {}, "What was found"),
        Object.keys(stats.labels).length
          ? table(["Finding", "Items"], Object.entries(stats.labels).sort((a, b) => b[1] - a[1]).map(([name, count]) => el("tr", {}, el("td", {}, title(name.replace("_", " "))), el("td", {}, count))))
          : el("p", { class: "empty" }, "Nothing found yet.")
      ),
      el(
        "div",
        {},
        el("h2", {}, "System"),
        table(
          ["Part", "State"],
          [
            ["Text model", state_(health.text_model, "Running")],
            ["Link model", state_(health.url_model, "Running")],
            ["Traffic model", state_(health.flow_model, "Running")],
            ["Language model", state_(health.language_model, health.language_model)],
            ["SMTP gateway", state_(health.smtp_gateway, `Port ${health.smtp_gateway}`)],
            ["HTTP proxy", state_(health.http_proxy, `Port ${health.http_proxy}`)],
          ].map(([name, value]) => el("tr", {}, el("td", {}, name), el("td", {}, value)))
        )
      )
    ),
    el("h2", {}, "Latest flagged items"),
    flagged.length ? table(VERDICT_HEADERS, verdictRows(flagged)) : el("p", { class: "empty" }, "Nothing flagged yet. Run a scenario to see both agents work.")
  );
}

async function hosts() {
  const rows = await api("/api/hosts");
  const upload = el("input", { type: "file", accept: ".pcap,.cap", onchange: async (event) => {
    const form = new FormData();
    form.append("file", event.target.files[0]);
    message.textContent = "Reading capture...";
    try {
      const result = await api("/api/check/pcap", { method: "POST", body: form });
      message.textContent = `Checked ${result.checked} of ${result.hosts} hosts.`;
      hosts();
    } catch (error) {
      message.textContent = error.message;
    }
  } });
  const message = el("span", { class: "busy" });
  page.replaceChildren(
    el("h1", {}, "Hosts"),
    el("p", { class: "lead" }, "The Network Agent's view. It knows each host from its recent connections only, and never reads content."),
    el("div", { class: "bar" }, el("label", {}, "Check a traffic capture (pcap)", upload), message),
    rows.length
      ? table(
          ["Host", "Behaviour risk", "Connections", "Summary", "Last seen"],
          rows.map((row) => el("tr", {}, el("td", {}, row.host), el("td", {}, row.risk === null ? "-" : row.risk.toFixed(2)), el("td", {}, row.connections), el("td", {}, row.summary), el("td", { class: "nowrap" }, clock(row.last_seen))))
        )
      : el("p", { class: "empty" }, "No hosts seen yet. Run a scenario or check a capture.")
  );
}

async function agents() {
  const rows = await api("/api/agents");
  page.replaceChildren(
    el("h1", {}, "Agents"),
    table(
      ["Agent", "Layer", "Reads", "Models", "Cut-offs", "Public key"],
      rows.map((row) =>
        el(
          "tr",
          {},
          el("td", { class: "nowrap" }, row.name),
          el("td", {}, row.layer),
          el("td", {}, row.reads),
          el("td", {}, row.models.join(", ") || "-"),
          el("td", {}, Object.entries(row.cut_offs).map(([k, v]) => `${k} ${v.toFixed(3)}`).join(", ") || "-"),
          el("td", {}, el("code", {}, row.key))
        )
      )
    ),
    el("p", { class: "note" }, "Cut-offs are chosen by the data during training. They are not typed in by hand.")
  );
}

async function scenarios() {
  const rows = await api("/api/scenarios");
  const status = el("span", { class: "busy" });
  const start = async (scenario, button) => {
    button.disabled = true;
    status.textContent = `Running: ${scenario.title}. The language model can take several seconds.`;
    try {
      const { id } = await post(`/api/scenarios/${scenario.id}/run`, {});
      status.textContent = "Done.";
      await openItem(id);
      const record = await api(`/api/verdicts/${id}`);
      results.set(scenario.id, record.verdict);
      paint();
    } catch (error) {
      status.textContent = error.message;
    } finally {
      button.disabled = false;
    }
  };
  const results = new Map();
  const body = el("tbody", {});
  const paint = () =>
    body.replaceChildren(
      ...rows.map((scenario) => {
        const verdict = results.get(scenario.id);
        const button = el("button", { class: "plain", onclick: (event) => start(scenario, event.target) }, "Run");
        return el(
          "tr",
          {},
          el("td", {}, button),
          el("td", {}, el("div", {}, scenario.title), el("div", { class: "note", style: "padding-top:0" }, scenario.shows)),
          el("td", { class: "nowrap" }, kindName(scenario.channel)),
          el("td", {}, scenario.expected === "flag" ? "Flag" : "Allow"),
          el("td", { class: "nowrap" }, verdict ? action(verdict.action) : "-"),
          el("td", {}, verdict ? verdict.risk.toFixed(2) : "-"),
          el("td", {}, verdict ? foundBy(verdict.flagged_by.join(",")) : "-")
        );
      })
    );
  page.replaceChildren(
    el("h1", {}, "Run a scenario"),
    el("p", { class: "lead" }, "Each scenario goes through the real agents. Emails travel as real SMTP sessions through the gateway. A bad machine's history comes from real attack traffic the models did not train on."),
    el("div", { class: "bar" }, status),
    el("table", {}, el("thead", {}, el("tr", {}, ["", "Scenario", "Channel", "Should", "Result", "Risk", "Found by"].map((name) => el("th", {}, name)))), body)
  );
  paint();
}

function check() {
  const kind = el("select", { id: "kind", onchange: show }, [["text", "Message or email"], ["link", "Link"], ["file", "QR image or file"]].map(([value, text]) => el("option", { value }, text)));
  const sender = el("input", { placeholder: "Optional", autocomplete: "off" });
  const subject = el("input", { placeholder: "Optional", autocomplete: "off" });
  const text = el("textarea", { rows: 9, placeholder: "Paste the message here" });
  const url = el("input", { class: "wide", placeholder: "https://", autocomplete: "off", hidden: true });
  const file = el("input", { class: "wide", type: "file", hidden: true });
  const details = el("div", { class: "row" }, el("label", {}, "From", sender), el("label", {}, "Subject", subject));
  const status = el("span", { class: "busy" });
  function show() {
    details.hidden = text.hidden = kind.value !== "text";
    url.hidden = kind.value !== "link";
    file.hidden = kind.value !== "file";
  }
  const go = el("button", { class: "primary", type: "submit" }, "Check");
  const submit = async (event) => {
    event.preventDefault();
    go.disabled = true;
    status.textContent = "Both agents are checking this...";
    try {
      let result;
      if (kind.value === "text") result = await post("/api/check/text", { text: text.value, subject: subject.value || null, sender: sender.value || null });
      else if (kind.value === "link") result = await post("/api/check/link", { url: url.value });
      else {
        const form = new FormData();
        form.append("file", file.files[0]);
        result = await api("/api/check/file", { method: "POST", body: form });
      }
      status.textContent = "";
      await openItem(result.id);
    } catch (error) {
      status.textContent = error.message;
    } finally {
      go.disabled = false;
    }
  };
  page.replaceChildren(
    el("h1", {}, "Check an item"),
    el("p", { class: "lead" }, "Paste anything and watch the agents judge it. Links are read as text and are never opened."),
    el("form", { class: "form", onsubmit: submit }, el("div", { class: "row" }, el("label", {}, "Type", kind)), details, text, url, file, el("div", { class: "row" }, go, status))
  );
}

async function codes() {
  const rows = await api("/api/testcodes");
  const status = el("span", { class: "busy" });
  const run = async (row, button) => {
    button.disabled = true;
    status.textContent = "Reading the QR code and checking it...";
    try {
      const { id } = await post(`/api/testcodes/${row.file}/check`, {});
      status.textContent = "";
      await openItem(id);
    } catch (error) {
      status.textContent = error.message;
    } finally {
      button.disabled = false;
    }
  };
  page.replaceChildren(
    el("h1", {}, "Test QR codes"),
    el("p", { class: "lead" }, "Fake codes made for testing. Every fraud code uses a reserved test name that cannot reach any real website."),
    el("div", { class: "bar" }, status),
    el(
      "div",
      { class: "codes" },
      rows.map((row) =>
        el(
          "figure",
          {},
          el("img", { src: `/testcodes/${row.file}`, alt: row.name, loading: "lazy" }),
          el("figcaption", {}, el("b", {}, `${title(row.label)}, ${row.variant}`), el("br"), row.payload.slice(0, 70)),
          el("button", { class: "plain", onclick: (event) => run(row, event.target) }, "Check this code")
        )
      )
    )
  );
}

function scoreTable(rows) {
  return table(
    ["Test", "System", "Precision", "Recall", "F1", "False alarms", "Rows"],
    rows.map((row) => el("tr", {}, el("td", {}, row.test), el("td", {}, row.system), el("td", {}, percent(row.precision)), el("td", {}, percent(row.recall)), el("td", {}, percent(row.f1)), el("td", {}, percent(row.false_alarm_rate)), el("td", {}, row.rows)))
  );
}

const SYSTEM_NAMES = { keyword_filter: "Keyword filter", linear_tfidf: "Linear model", transformer: "STL text model", flow_transformer: "STL traffic model", lightgbm_single_flow: "LightGBM on single flows" };

async function results() {
  const data = await api("/api/results");
  const parts = [el("h1", {}, "Test results"), el("p", { class: "lead" }, "Measured on real data the models never trained on. These numbers are read directly from the result files.")];
  if (data.text) {
    const rows = [];
    for (const [name, set] of Object.entries(data.text.datasets)) {
      for (const [label, systems] of Object.entries(set.labels)) {
        for (const [system, score] of Object.entries(systems)) rows.push({ test: `${name.replaceAll("_", " ")}: ${label}`, system: SYSTEM_NAMES[system] || system, ...score });
      }
    }
    parts.push(el("h2", {}, "Content: does meaning beat keywords?"), scoreTable(rows));
    const semantic = data.text.semantic_test;
    if (semantic) {
      const groups = [["all", "All 57 messages"], ["no_obvious_keyword", "No obvious keyword"], ["language_en", "English"], ["language_ru", "Roman Urdu"], ["language_ur", "Urdu script"]];
      parts.push(
        el("h2", {}, "Hand-written hard messages"),
        table(
          ["Group", "Keyword filter", "Text model", "Text model + language model"],
          groups.map(([key, name]) => {
            const row = semantic[key];
            const cell = (system) => `caught ${row[system].caught}, false alarms ${row[system].false_alarms}`;
            return el("tr", {}, el("td", {}, name), el("td", {}, cell("keyword")), el("td", {}, cell("transformer")), el("td", {}, cell("combined")));
          })
        ),
        el("p", { class: "note" }, "A small hand-written set. It shows the type of errors, and it is not a benchmark.")
      );
      if (semantic.gates) {
        parts.push(
          el("h2", {}, "What if only some items reach the language model?"),
          table(
            ["Fast risk needed", "Harmful caught", "False alarms", "Normal mail read", "Normal comments read"],
            semantic.gates.map((row) => el("tr", {}, el("td", {}, row.gate), el("td", {}, row.caught), el("td", {}, row.false_alarms), el("td", {}, percent(row.normal_mail_read)), el("td", {}, percent(row.normal_comments_read))))
          ),
          el("p", { class: "note" }, "The fast model is too sure of itself on polite and veiled messages, so the language model reads everything by default.")
        );
      }
    }
    const sample = data.text.held_out_sample;
    if (sample && sample.rows) {
      parts.push(
        el("h2", {}, "Language model on real held-out text"),
        table(
          ["Test", "Caught, fast model", "Caught, with language model", "False alarms, fast model", "False alarms, with language model"],
          sample.rows.map((row) => el("tr", {}, el("td", {}, row.name), el("td", {}, `${row.fast_caught}/${row.size_each}`), el("td", {}, `${row.both_caught}/${row.size_each}`), el("td", {}, `${row.fast_wrong}/${row.size_each}`), el("td", {}, `${row.both_wrong}/${row.size_each}`)))
        ),
        el("p", { class: "note" }, "Balanced samples. A message counts when the system would flag it for any reason. Harmless rows carry no harmful label at all.")
      );
    }
  }
  if (data.links) {
    const link = data.links;
    parts.push(
      el("h2", {}, "Links and QR codes"),
      table(
        ["Test", "Result"],
        [
          ["Domains the model never saw", `recall ${percent(link.held_out_domains.recall)}, precision ${percent(link.held_out_domains.precision)}, false alarms ${percent(link.held_out_domains.false_alarm_rate)}`],
          ["Live OpenPhish feed, unseen domains", `recall ${percent(link.openphish_unseen_domains.recall)} on ${link.openphish_unseen_domains.rows} links`],
          ...(link.language_model_sample
            ? [
                ["Real links, link model", `caught ${link.language_model_sample.fast_caught}/${link.language_model_sample.size_each}, false alarms ${link.language_model_sample.fast_wrong}/${link.language_model_sample.size_each}`],
                ["Real links, with language model", `caught ${link.language_model_sample.both_caught}/${link.language_model_sample.size_each}, false alarms ${link.language_model_sample.both_wrong}/${link.language_model_sample.size_each}`],
              ]
            : []),
          ["Fake fraud links, link model", `caught ${link.fixture_links.fraud_caught}, false alarms ${link.fixture_links.normal_false_alarms}`],
          ...(link.fixture_links.with_language_model_caught ? [["Fake fraud links, with language model", `caught ${link.fixture_links.with_language_model_caught}, false alarms ${link.fixture_links.with_language_model_false_alarms}`]] : []),
          ["Fake QR codes", `read ${link.fixture_qr.read_correctly} of ${link.fixture_qr.images}, right verdict ${link.fixture_qr.verdict_correct}`],
        ].map(([name, value]) => el("tr", {}, el("td", {}, name), el("td", {}, value)))
      )
    );
  }
  if (data.link_rule_choice) {
    const choice = data.link_rule_choice;
    const names = [["Link model alone", "Link model alone"], ["Same rule as content", "Language model judges alone"], ["Language model only clears", "Final rule: it can only confirm or lower a link the link model flagged"]];
    const cell = (rule, group) => `${choice.rules[rule][group].flagged} flagged, ${choice.rules[rule][group].warned_or_more} at least warned`;
    parts.push(
      el("h2", {}, "Who should judge a bare link?"),
      table(
        ["Rule", `Phishing (${choice.rows.phishing})`, `Normal (${choice.rows.normal})`, `Popular sites (${choice.rows.popular_normal})`],
        names.map(([rule, name]) => el("tr", {}, el("td", {}, name), el("td", {}, cell(rule, "phishing")), el("td", {}, cell(rule, "normal")), el("td", {}, cell(rule, "popular_normal"))))
      ),
      el("p", { class: "note" }, "Validation links only. The language model claims that ordinary names copy a brand, so it never raises a bare link alone.")
    );
  }
  if (data.flows) {
    const rows = [];
    for (const [name, experiment] of Object.entries(data.flows)) {
      for (const [test, systems] of Object.entries(experiment.tests)) {
        for (const key of ["flow_transformer", "lightgbm_single_flow"]) rows.push({ test: `${name.replaceAll("_", " ")}: ${test.replaceAll("_", " ")}`, system: SYSTEM_NAMES[key], ...systems[key] });
      }
    }
    parts.push(el("h2", {}, "Traffic: does the Network Agent find attacks?"), scoreTable(rows));
  }
  if (data.anomaly) {
    const names = { thursday: "Thursday attacks, never taught", friday: "Friday attacks, never taught" };
    const rows = Object.entries(data.anomaly.tests).map(([name, row]) => ({ test: names[name] || name, system: "Normal-behaviour model", ...row }));
    const both = data.anomaly.both_models_later_flows;
    for (const [key, name] of [["known_attack_model", "Known-attack model"], ["normal_behaviour_model", "Normal-behaviour model"], ["either_model", "Either model"]]) rows.push({ test: "Later flows, all days", system: name, ...both[key] });
    parts.push(
      el("h2", {}, "Traffic: attacks it was never taught"),
      scoreTable(rows),
      el("p", { class: "note" }, "The normal-behaviour model learned only normal traffic. It can warn but it cannot flag alone, because it is only correct on the network it learned.")
    );
  }
  if (data.cross_dataset) {
    const rows = Object.entries(data.cross_dataset).sort(([a], [b]) => Number(a.split("_")[1]) - Number(b.split("_")[1]));
    parts.push(
      el("h2", {}, "A different network"),
      table(
        ["CTU-13 scenario", "Known attacks caught", "Normal-behaviour false alarms"],
        rows.map(([name, row]) => el("tr", {}, el("td", {}, name.replace("ctu_", "Scenario ")), el("td", {}, percent(row.known_attack_model.recall)), el("td", {}, percent(row.normal_behaviour_model.false_alarm_rate))))
      ),
      el("p", { class: "note" }, "Models trained only on CICIDS2017 and tested on CTU-13. They do not carry over. This is why the Network Agent must learn each network where it runs.")
    );
  }
  if (data.backbone) {
    const b = data.backbone;
    parts.push(
      el("h2", {}, "Real Internet backbone traffic"),
      table(
        ["Measure", "Value"],
        [
          ["Trace", b.trace],
          ["Connections read", b.flows_read],
          ["Connections scored", b.flows_scored],
          ["Hosts scored", b.hosts_scored],
          ["Known-attack alerts", percent(b.known_attack_alert_rate)],
          ["Normal-behaviour alerts, model from the lab", percent(b.normal_behaviour_alert_rate)],
          ["Normal-behaviour alerts, after learning half of these hosts", percent(b.trained_on_this_traffic.alert_rate_on_other_hosts)],
          ["Connections per second on the CPU", b.score_flows_per_second_cpu],
        ].map(([name, value]) => el("tr", {}, el("td", {}, name), el("td", {}, value)))
      ),
      el("p", { class: "note" }, "This traffic has no labels, so an alert here is not proven wrong.")
    );
  }
  if (data.review) {
    const r = data.review;
    if (r.link_opinion) {
      parts.push(
        el("h2", {}, "Does the language model copy the first model?"),
        table(
          ["Language model was told", "Fraud links caught", "Normal links wrongly flagged"],
          r.link_opinion.conditions.map((row) => el("tr", {}, el("td", {}, row.name), el("td", {}, row.fraud_caught), el("td", {}, row.normal_flagged)))
        ),
        el("p", { class: "note" }, "This is why the first model's opinion on a link is not passed to the language model.")
      );
    }
    if (r.network_note) {
      const n = r.network_note;
      parts.push(
        el("h2", {}, "Does a note about bad traffic change how it reads?"),
        table(
          ["Language model was told", "Harmful messages caught", "Harmless messages flagged"],
          [
            el("tr", {}, el("td", {}, "Nothing"), el("td", {}, `${n.harmful_caught_alone}/${n.harmful}`), el("td", {}, `${n.harmless_flagged_alone}/${n.harmless}`)),
            el("tr", {}, el("td", {}, "The sender's traffic matches a known attack"), el("td", {}, `${n.harmful_caught_with_note}/${n.harmful}`), el("td", {}, `${n.harmless_flagged_with_note}/${n.harmless}`)),
          ]
        ),
        el("p", { class: "note" }, "This is why the language model reads alone. The Coordinator joins the two agents after both have decided.")
      );
    }
    if (r.disguise) {
      parts.push(
        el("h2", {}, "Disguised messages"),
        table(
          ["Disguise", "Keyword filter", "Text model", "With language model", "False alarms, with language model"],
          r.disguise.rows.map((row) => el("tr", {}, el("td", {}, row.name), el("td", {}, row.keyword), el("td", {}, row.transformer), el("td", {}, row.combined), el("td", {}, row.combined_wrong || "")))
        ),
        el("p", { class: "note" }, "Hand-written messages after each disguise, harmful ones for the first three numbers, harmless ones for the last. A small set, so it shows the type of error.")
      );
    }
    if (r.injection) {
      parts.push(
        el("h2", {}, "Attacks on the language model"),
        table(
          ["Attack text inside the message", "Tried", "Language model fooled", "Still flagged", "Still warned, no floor", "Still warned, with floor", "Flagged with unusual traffic, no floor", "Flagged with unusual traffic, with floor"],
          r.injection.rows.map((row) => el("tr", {}, el("td", {}, row.name), el("td", {}, row.tried), el("td", {}, row.language_model_fooled), el("td", {}, row.still_flagged), el("td", {}, row.warned_no_floor), el("td", {}, row.warned_with_floor), el("td", {}, row.unusual_no_floor), el("td", {}, row.unusual_with_floor)))
        ),
        el("p", { class: "note" }, "Every message here was caught before the attack. The floor keeps a warning when the fast model saw a problem the language model cleared. The traffic columns work out the joined risk if the sender's host looked unusual. Attack traffic flags on its own, so it is not shown.")
      );
    }
  }
  if (data.system) {
    const s = data.system;
    const fast = data.system_no_language_model;
    const rows = ["application_only", "network_only", "both_joined"].map((key) => ({ test: `${s.sessions} sessions`, system: title(key.replace("_", " ")), ...s[key], rows: s.sessions }));
    if (fast) {
      rows.push({ test: `${fast.sessions} sessions`, system: "Both joined, no language model", ...fast.both_joined, rows: fast.sessions });
    }
    const blocked = s.clean_sessions_blocked === undefined ? "" : ` ${s.clean_sessions_blocked} of ${s.sessions / 4} clean sessions were blocked outright.`;
    parts.push(
      el("h2", {}, "Two agents against one"),
      scoreTable(rows),
      el("p", { class: "note" }, `Each session pairs real content with real traffic from separate sources, because no public data links both layers. This tests how the agents combine, and it is not field data.${blocked}`)
    );
  }
  if (data.scenarios) {
    const s = data.scenarios;
    parts.push(
      el("h2", {}, `Demo scenarios: ${s.passed} of ${s.total} behaved as expected`),
      table(
        ["Scenario", "Expected", "Action", "Application", "Network", "Labels", "Language model", "Signature"],
        s.rows.map((row) =>
          el(
            "tr",
            {},
            el("td", {}, row.scenario),
            el("td", {}, title(row.expected)),
            el("td", {}, title(row.action)),
            el("td", {}, row.application_risk.toFixed(2)),
            el("td", {}, row.network_risk.toFixed(2)),
            el("td", {}, row.labels.join(", ") || "None"),
            el("td", {}, row.language_model_used ? "Used" : "Not needed"),
            el("td", {}, row.signature_valid ? "Valid" : "Invalid")
          )
        )
      )
    );
  }
  if (parts.length === 2) parts.push(el("p", { class: "empty" }, "No results yet. They appear here as soon as the tests finish."));
  page.replaceChildren(...parts);
}

const PAGES = { overview, queue, hosts, agents, scenarios, check, codes, results };

async function route() {
  clearInterval(state.timer);
  const name = location.hash.slice(1) || "overview";
  const show = PAGES[name] || overview;
  for (const link of document.querySelectorAll("nav a")) link.classList.toggle("on", link.getAttribute("href") === `#${name}`);
  try {
    await show();
  } catch (error) {
    page.replaceChildren(el("p", { class: "bad" }, error.message));
  }
}

async function health() {
  const data = await api("/api/health").catch(() => null);
  const label = (name, value) => `${name} ${value ? "on" : "off"}`;
  document.getElementById("health").textContent = data
    ? [label("Text model", data.text_model), label("Link model", data.url_model), label("Traffic model", data.flow_model), label("Language model", data.language_model)].join(" · ")
    : "Server not reachable";
}

window.addEventListener("hashchange", route);
health();
route();
setInterval(health, 10000);
