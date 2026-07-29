#!/usr/bin/env node
// Renders one canonical review.json into: chat summary (stdout) + Markdown + self-contained HTML.
// Validates the record first and refuses to render an inconsistent verdict.
// Usage: node render-review.mjs <review.json> [--format chat|md|html|all] [--out-dir <dir>]
//   chat -> full report to stdout, writes nothing | md/html -> that file + short chat summary
//   all  -> both files + short chat summary (default)
// ponytail: hand-rolled validation instead of a JSON Schema validator — no dependency, and the only
// rules that matter here are the verdict/evidence gates. Switch to ajv if the schema outgrows this.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { basename, dirname, join } from "node:path";

const SEVERITIES = ["BLOCKER", "HIGH", "MEDIUM", "LOW"];
const BLOCKING = ["BLOCKER", "HIGH"];
const EVIDENCE = ["VERIFIED", "INFERRED", "UNVERIFIED"];
const STATUS = ["pass", "fail", "not_run"];
const AUDIT = ["skipped", "disabled", "trivial", "implementation_shaped", "missing"];

const L = {
  en: { title: "Code review", verdict: "Verdict", scope: "Reviewed scope", spec: "Specification",
    specSource: "Spec source", blocking: "Blocking findings", nonBlocking: "Non-blocking observations",
    verification: "Verification", command: "Command", status: "Status", result: "Result", reason: "Reason",
    testAudit: "Test audit", totals: "Severity totals", severity: "Severity", count: "Count",
    strengths: "Strengths", remediation: "Required remediation", why: "Why", how: "How",
    evidence: "Evidence", location: "Location", none: "None", generated: "Generated",
    incomplete: "Verification incomplete", pass: "executed, passed", fail: "executed, failed",
    not_run: "not executed", menu: "Apply fixes? (1) one by one (2) all required (3) selected (e.g. \"1,3\") (4) none [+tests]",
    finding: "Finding", subject: "Subject", issue: "Issue", note: "Note", files: "Files",
    noImpact: "Does not affect the verdict." },
  it: { title: "Code review", verdict: "Verdetto", scope: "Ambito revisionato", spec: "Specifica",
    specSource: "Fonte della specifica", blocking: "Rilievi bloccanti", nonBlocking: "Osservazioni non bloccanti",
    verification: "Verifica", command: "Comando", status: "Stato", result: "Risultato", reason: "Motivo",
    testAudit: "Audit dei test", totals: "Totali per severità", severity: "Severità", count: "Numero",
    strengths: "Punti di forza", remediation: "Correzioni richieste", why: "Perché", how: "Come",
    evidence: "Evidenza", location: "Posizione", none: "Nessuno", generated: "Generato",
    incomplete: "Verifica incompleta", pass: "eseguito, superato", fail: "eseguito, fallito",
    not_run: "non eseguito", menu: "Applico le correzioni? (1) una alla volta (2) tutte le richieste (3) selezionate (es. \"1,3\") (4) nessuna [+tests]",
    finding: "Rilievo", subject: "Oggetto", issue: "Problema", note: "Nota", files: "File",
    noImpact: "Non incide sul verdetto." },
};

// ---------- validation ----------
const keys = (obj, allowed, where, errs) => {
  for (const k of Object.keys(obj ?? {})) if (!allowed.includes(k)) errs.push(`${where}: unknown field "${k}"`);
};
const need = (obj, req, where, errs) => {
  for (const k of req) if (obj?.[k] === undefined || obj[k] === null || obj[k] === "") errs.push(`${where}: missing "${k}"`);
};

function validate(r) {
  const e = [];
  if (r?.schema !== "advanced-code-review/1") e.push(`schema must be "advanced-code-review/1"`);
  keys(r, ["schema", "language", "labels", "generated_at", "scope", "spec", "verdict", "verdict_reason",
    "verification", "test_audit", "findings", "observations", "strengths"], "root", e);
  need(r, ["language", "scope", "spec", "verdict", "verdict_reason"], "root", e);

  keys(r.scope, ["kind", "target", "stats", "files"], "scope", e);
  need(r.scope, ["kind", "target"], "scope", e);
  if (r.scope && !["file", "uncommitted", "commit", "branch"].includes(r.scope.kind)) e.push(`scope.kind invalid: ${r.scope.kind}`);

  keys(r.spec, ["source", "text"], "spec", e);
  need(r.spec, ["source", "text"], "spec", e);
  if (/^(the )?(implementation|code|diff)$/i.test(r.spec?.source ?? "")) e.push("spec.source: the spec must not be inferred from the implementation");

  if (!["PASS", "PARTIAL", "FAIL"].includes(r.verdict)) e.push(`verdict invalid: ${r.verdict}`);

  const ver = r.verification;
  if (!Array.isArray(ver)) e.push("verification must be an array");
  else {
    if (ver.length === 0) e.push("verification is empty: record each executed check, or a not_run entry with a reason");
    ver.forEach((v, i) => {
      const w = `verification[${i}]`;
      keys(v, ["command", "status", "result", "reason"], w, e);
      need(v, ["command", "status"], w, e);
      if (!STATUS.includes(v.status)) e.push(`${w}: status invalid: ${v.status}`);
      if (v.status === "not_run" && !v.reason) e.push(`${w}: not_run requires "reason"`);
      if (v.status !== "not_run" && !v.result) e.push(`${w}: ${v.status} requires the real "result" output`);
    });
  }

  const ids = new Set();
  const fin = Array.isArray(r.findings) ? r.findings : (e.push("findings must be an array"), []);
  fin.forEach((f, i) => {
    const w = `findings[${i}]`;
    keys(f, ["id", "severity", "title", "evidence_class", "location", "evidence", "why", "how", "required_fix"], w, e);
    need(f, ["id", "severity", "title", "evidence_class", "why"], w, e);
    if (!/^F\d+$/.test(f.id ?? "")) e.push(`${w}: id must match F<number>`);
    if (ids.has(f.id)) e.push(`${w}: duplicate id ${f.id}`);
    ids.add(f.id);
    if (!SEVERITIES.includes(f.severity)) e.push(`${w}: severity invalid: ${f.severity}`);
    if (!EVIDENCE.includes(f.evidence_class)) e.push(`${w}: evidence_class invalid: ${f.evidence_class}`);
    if (f.evidence_class === "VERIFIED" && !f.location) e.push(`${w}: VERIFIED findings require a file:line location`);
    if (BLOCKING.includes(f.severity) && !f.how) e.push(`${w}: blocking findings require "how" (minimum fix)`);
    if (f.required_fix === true && !BLOCKING.includes(f.severity)) e.push(`${w}: required_fix is only for BLOCKER/HIGH`);
  });

  (r.observations ?? []).forEach((o, i) => {
    const w = `observations[${i}]`;
    keys(o, ["id", "note", "location"], w, e);
    need(o, ["id", "note"], w, e);
    if (!/^O\d+$/.test(o.id ?? "")) e.push(`${w}: id must match O<number>`);
  });
  (r.strengths ?? []).forEach((s, i) => { keys(s, ["text", "location"], `strengths[${i}]`, e); need(s, ["text"], `strengths[${i}]`, e); });
  (r.test_audit ?? []).forEach((t, i) => {
    const w = `test_audit[${i}]`;
    keys(t, ["subject", "issue", "location", "note"], w, e);
    need(t, ["subject", "issue"], w, e);
    if (!AUDIT.includes(t.issue)) e.push(`${w}: issue invalid: ${t.issue}`);
  });

  // verdict gate — derived, not declared
  const c = counts(fin);
  const anyFail = (ver ?? []).some((v) => v.status === "fail");
  const anyNotRun = (ver ?? []).some((v) => v.status === "not_run");
  const allPass = Array.isArray(ver) && ver.length > 0 && ver.every((v) => v.status === "pass");
  let derived = null;
  if (c.BLOCKER > 0 || anyFail) derived = "FAIL";
  else if (c.HIGH > 0 || anyNotRun) derived = "PARTIAL";
  else if (allPass) derived = "PASS";
  if (derived && r.verdict !== derived) {
    e.push(`verdict "${r.verdict}" contradicts the evidence — rules require "${derived}" ` +
      `(BLOCKER=${c.BLOCKER}, HIGH=${c.HIGH}, failed checks=${anyFail}, unrun checks=${anyNotRun})`);
  }
  return { errors: e, counts: c, anyFail, anyNotRun, derived };
}

const counts = (findings) => findings.reduce((a, f) => (a[f.severity] = (a[f.severity] ?? 0) + 1, a),
  { BLOCKER: 0, HIGH: 0, MEDIUM: 0, LOW: 0 });

// ---------- rendering ----------
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
const VERDICT_MARK = { PASS: "✅ PASS", PARTIAL: "⚠️ PARTIAL", FAIL: "❌ FAIL" };
const SEV_MARK = { BLOCKER: "⛔", HIGH: "🟠", MEDIUM: "🟡", LOW: "🟢" };
const scopeLine = (s) => `${s.kind}: ${s.target}${s.stats ? ` (${s.stats})` : ""}`;
const blockingOf = (r) => r.findings.filter((f) => BLOCKING.includes(f.severity));
const requiredOf = (r) => r.findings.filter((f) => f.required_fix !== false && BLOCKING.includes(f.severity));

function markdown(r, t, c) {
  const fence = (s) => "```\n" + String(s).replace(/```/g, "``\u200b`") + "\n```";
  const out = [];
  out.push(`# ${t.title} — ${VERDICT_MARK[r.verdict]}`, "");
  out.push(`- **${t.scope}**: ${scopeLine(r.scope)}`);
  if (r.scope.files?.length) out.push(`- **${t.files}**: ${r.scope.files.join(", ")}`);
  out.push(`- **${t.specSource}**: ${r.spec.source}`);
  out.push(`- **${t.generated}**: ${r.generated_at}`, "");
  out.push(`## ${t.spec}`, "", fence(r.spec.text), "");
  out.push(`## ${t.verdict}: ${VERDICT_MARK[r.verdict]}`, "", r.verdict_reason, "");
  if (r.anyNotRun) out.push(`> ⚠️ ${t.incomplete}`, "");

  out.push(`## ${t.totals}`, "", `| ${t.severity} | ${t.count} |`, "|---|---|");
  for (const s of SEVERITIES) out.push(`| ${SEV_MARK[s]} ${s} | ${c[s]} |`);
  out.push(`| — ${t.nonBlocking} | ${(r.observations ?? []).length} |`, "");

  out.push(`## ${t.verification}`, "", `| ${t.command} | ${t.status} |`, "|---|---|");
  for (const v of r.verification) out.push(`| \`${v.command}\` | ${t[v.status]} |`);
  out.push("");
  for (const v of r.verification) {
    out.push(`### \`${v.command}\` — ${t[v.status]}`, "");
    out.push(v.status === "not_run" ? `${t.reason}: ${v.reason}` : fence(v.result), "");
  }

  out.push(`## ${t.blocking}`, "");
  const bl = blockingOf(r);
  if (!bl.length) out.push(`_${t.none}_`, "");
  for (const f of bl) out.push(...findingMd(f, t));

  const nb = r.findings.filter((f) => !BLOCKING.includes(f.severity));
  if (nb.length || (r.observations ?? []).length) {
    out.push(`## ${t.nonBlocking}`, "", `_${t.noImpact}_`, "");
    for (const f of nb) out.push(...findingMd(f, t));
    for (const o of r.observations ?? []) out.push(`- **${o.id}**${o.location ? ` \`${o.location}\`` : ""} — ${o.note}`);
    out.push("");
  }

  if ((r.test_audit ?? []).length) {
    out.push(`## ${t.testAudit}`, "", `| ${t.subject} | ${t.issue} | ${t.location} | ${t.note} |`, "|---|---|---|---|");
    for (const a of r.test_audit) out.push(`| ${a.subject} | ${a.issue} | ${a.location ?? "—"} | ${a.note ?? "—"} |`);
    out.push("");
  }

  if ((r.strengths ?? []).length) {
    out.push(`## ${t.strengths}`, "");
    for (const s of r.strengths) out.push(`- ${s.text}${s.location ? ` (\`${s.location}\`)` : ""}`);
    out.push("");
  }

  const req = requiredOf(r);
  out.push(`## ${t.remediation}`, "");
  if (!req.length) out.push(`_${t.none}_`, "");
  else {
    req.forEach((f, i) => out.push(`${i + 1}. **${f.id}** ${f.title}${f.location ? ` — \`${f.location}\`` : ""}`,
      `   - ${t.why}: ${f.why}`, `   - ${t.how}: ${f.how}`));
    out.push("", t.menu, "");
  }
  return out.join("\n");
}

const findingMd = (f, t) => {
  const l = [`### ${f.id} — ${SEV_MARK[f.severity]} ${f.severity}: ${f.title}`, ""];
  l.push(`- **${t.location}**: ${f.location ? `\`${f.location}\`` : "—"}`);
  l.push(`- **${t.evidence}** (${f.evidence_class}): ${f.evidence ?? "—"}`);
  l.push(`- **${t.why}**: ${f.why}`);
  if (f.how) l.push(`- **${t.how}**: ${f.how}`);
  l.push("");
  return l;
};

function html(r, t, c) {
  const pre = (s) => `<pre><code>${esc(s)}</code></pre>`;
  const bl = blockingOf(r);
  const nb = r.findings.filter((f) => !BLOCKING.includes(f.severity));
  const req = requiredOf(r);
  const findingHtml = (f) => `<article class="finding sev-${esc(f.severity)}">
<h3><span class="id">${esc(f.id)}</span> <span class="badge">${esc(SEV_MARK[f.severity])} ${esc(f.severity)}</span> ${esc(f.title)}</h3>
<dl><dt>${esc(t.location)}</dt><dd>${f.location ? `<code>${esc(f.location)}</code>` : "—"}</dd>
<dt>${esc(t.evidence)}</dt><dd><span class="ev ev-${esc(f.evidence_class)}">${esc(f.evidence_class)}</span>${f.evidence ? ` ${esc(f.evidence)}` : ""}</dd>
<dt>${esc(t.why)}</dt><dd>${esc(f.why)}</dd>
${f.how ? `<dt>${esc(t.how)}</dt><dd>${esc(f.how)}</dd>` : ""}</dl></article>`;

  return `<!DOCTYPE html>
<html lang="${esc(r.language)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(t.title)} — ${esc(r.verdict)} — ${esc(r.scope.target)}</title>
<style>
:root{--fg:#1b1f24;--bg:#fff;--muted:#5b6570;--line:#d8dee4;--card:#f6f8fa;
--blocker:#b3261e;--high:#b95000;--medium:#8a6d00;--low:#1a7f37;--pass:#1a7f37;--partial:#b95000;--fail:#b3261e}
@media (prefers-color-scheme:dark){:root{--fg:#e6edf3;--bg:#0d1117;--muted:#9aa7b2;--line:#30363d;--card:#161b22;
--blocker:#ff7b72;--high:#ffa657;--medium:#e3b341;--low:#3fb950;--pass:#3fb950;--partial:#ffa657;--fail:#ff7b72}}
*{box-sizing:border-box}
body{margin:0 auto;padding:1.5rem;max-width:60rem;background:var(--bg);color:var(--fg);
font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
h1{font-size:1.6rem;margin:0 0 .5rem}h2{font-size:1.2rem;margin:2rem 0 .5rem;padding-bottom:.3rem;border-bottom:1px solid var(--line)}
h3{font-size:1rem;margin:1.2rem 0 .4rem}
a{color:inherit}code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.875em}
pre{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:.75rem;overflow-x:auto;white-space:pre-wrap;word-break:break-word}
table{border-collapse:collapse;width:100%;margin:.5rem 0}caption{text-align:left;color:var(--muted);padding-bottom:.3rem}
th,td{border:1px solid var(--line);padding:.4rem .6rem;text-align:left;vertical-align:top}
thead th{background:var(--card)}
dl{margin:.3rem 0}dt{font-weight:600;color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.02em;margin-top:.5rem}
dd{margin:.1rem 0 0}
.verdict{display:flex;flex-wrap:wrap;gap:.75rem;align-items:baseline;border:2px solid currentColor;border-radius:8px;padding:.75rem 1rem;margin:1rem 0}
.verdict.v-PASS{color:var(--pass)}.verdict.v-PARTIAL{color:var(--partial)}.verdict.v-FAIL{color:var(--fail)}
.verdict strong{font-size:1.35rem}.verdict p{color:var(--fg);margin:0;flex:1 1 20rem}
.meta{color:var(--muted);font-size:.9rem}
.finding{border-left:4px solid var(--line);padding-left:.9rem;margin:1rem 0}
.finding.sev-BLOCKER{border-color:var(--blocker)}.finding.sev-HIGH{border-color:var(--high)}
.finding.sev-MEDIUM{border-color:var(--medium)}.finding.sev-LOW{border-color:var(--low)}
.badge,.ev{font-size:.75rem;border:1px solid var(--line);border-radius:999px;padding:.05rem .5rem;white-space:nowrap}
.id{font-family:ui-monospace,monospace}
.warn{border:1px solid var(--partial);border-left-width:4px;border-radius:6px;padding:.6rem .9rem;margin:1rem 0}
.st-fail{color:var(--fail);font-weight:600}.st-not_run{color:var(--partial);font-weight:600}.st-pass{color:var(--pass);font-weight:600}
footer{margin-top:2.5rem;color:var(--muted);font-size:.8rem;border-top:1px solid var(--line);padding-top:.75rem}
@media print{:root{--fg:#000;--bg:#fff;--card:#fff;--muted:#333}body{max-width:none;padding:0;font-size:11pt}
pre{white-space:pre-wrap}h2{break-after:avoid}.finding,article,table{break-inside:avoid}}
</style>
</head>
<body>
<header>
<h1>${esc(t.title)}</h1>
<p class="meta"><strong>${esc(t.scope)}:</strong> ${esc(scopeLine(r.scope))}<br>
<strong>${esc(t.specSource)}:</strong> ${esc(r.spec.source)}<br>
<strong>${esc(t.generated)}:</strong> <time datetime="${esc(r.generated_at)}">${esc(r.generated_at)}</time></p>
</header>
<main>
<section aria-labelledby="verdict-h">
<h2 id="verdict-h">${esc(t.verdict)}</h2>
<div class="verdict v-${esc(r.verdict)}" role="status"><strong>${esc(VERDICT_MARK[r.verdict])}</strong><p>${esc(r.verdict_reason)}</p></div>
${r.anyNotRun ? `<p class="warn">⚠️ ${esc(t.incomplete)}</p>` : ""}
<table><caption>${esc(t.totals)}</caption><thead><tr><th scope="col">${esc(t.severity)}</th><th scope="col">${esc(t.count)}</th></tr></thead>
<tbody>${SEVERITIES.map((s) => `<tr><th scope="row">${esc(SEV_MARK[s])} ${esc(s)}</th><td>${c[s]}</td></tr>`).join("")}
<tr><th scope="row">${esc(t.nonBlocking)}</th><td>${(r.observations ?? []).length}</td></tr></tbody></table>
</section>
<section aria-labelledby="spec-h"><h2 id="spec-h">${esc(t.spec)}</h2>${pre(r.spec.text)}</section>
<section aria-labelledby="ver-h"><h2 id="ver-h">${esc(t.verification)}</h2>
<table><caption>${esc(t.verification)}</caption><thead><tr><th scope="col">${esc(t.command)}</th><th scope="col">${esc(t.status)}</th></tr></thead>
<tbody>${r.verification.map((v) => `<tr><th scope="row"><code>${esc(v.command)}</code></th><td class="st-${esc(v.status)}">${esc(t[v.status])}</td></tr>`).join("")}</tbody></table>
${r.verification.map((v) => `<h3><code>${esc(v.command)}</code> — <span class="st-${esc(v.status)}">${esc(t[v.status])}</span></h3>
${v.status === "not_run" ? `<p>${esc(t.reason)}: ${esc(v.reason)}</p>` : pre(v.result)}`).join("")}
</section>
<section aria-labelledby="bl-h"><h2 id="bl-h">${esc(t.blocking)}</h2>
${bl.length ? bl.map(findingHtml).join("") : `<p>${esc(t.none)}</p>`}</section>
${nb.length || (r.observations ?? []).length ? `<section aria-labelledby="nb-h"><h2 id="nb-h">${esc(t.nonBlocking)}</h2>
<p class="meta">${esc(t.noImpact)}</p>
${nb.map(findingHtml).join("")}
${(r.observations ?? []).length ? `<ul>${r.observations.map((o) => `<li><span class="id">${esc(o.id)}</span>${o.location ? ` <code>${esc(o.location)}</code>` : ""} — ${esc(o.note)}</li>`).join("")}</ul>` : ""}
</section>` : ""}
${(r.test_audit ?? []).length ? `<section aria-labelledby="ta-h"><h2 id="ta-h">${esc(t.testAudit)}</h2>
<table><caption>${esc(t.testAudit)}</caption><thead><tr><th scope="col">${esc(t.subject)}</th><th scope="col">${esc(t.issue)}</th><th scope="col">${esc(t.location)}</th><th scope="col">${esc(t.note)}</th></tr></thead>
<tbody>${r.test_audit.map((a) => `<tr><th scope="row">${esc(a.subject)}</th><td>${esc(a.issue)}</td><td>${a.location ? `<code>${esc(a.location)}</code>` : "—"}</td><td>${esc(a.note ?? "—")}</td></tr>`).join("")}</tbody></table></section>` : ""}
${(r.strengths ?? []).length ? `<section aria-labelledby="str-h"><h2 id="str-h">${esc(t.strengths)}</h2>
<ul>${r.strengths.map((s) => `<li>${esc(s.text)}${s.location ? ` <code>${esc(s.location)}</code>` : ""}</li>`).join("")}</ul></section>` : ""}
<section aria-labelledby="rem-h"><h2 id="rem-h">${esc(t.remediation)}</h2>
${req.length ? `<ol>${req.map((f) => `<li><strong>${esc(f.id)}</strong> ${esc(f.title)}${f.location ? ` — <code>${esc(f.location)}</code>` : ""}
<dl><dt>${esc(t.why)}</dt><dd>${esc(f.why)}</dd><dt>${esc(t.how)}</dt><dd>${esc(f.how)}</dd></dl></li>`).join("")}</ol>
<p>${esc(t.menu)}</p>` : `<p>${esc(t.none)}</p>`}</section>
</main>
<footer>advanced-code-review · ${esc(r.schema)} · ${esc(r.verdict)}</footer>
</body>
</html>
`;
}

function chat(r, t, c, links) {
  const bl = blockingOf(r);
  const lines = [`${VERDICT_MARK[r.verdict]} — ${r.verdict_reason}`, "",
    `${t.scope}: ${scopeLine(r.scope)}`,
    `${t.totals}: ⛔ ${c.BLOCKER} · 🟠 ${c.HIGH} · 🟡 ${c.MEDIUM} · 🟢 ${c.LOW} · ${t.nonBlocking} ${(r.observations ?? []).length}`, ""];
  lines.push(`${t.blocking}:`);
  if (!bl.length) lines.push(`- ${t.none}`);
  for (const f of bl) lines.push(`- ${f.id} ${SEV_MARK[f.severity]} ${f.severity} ${f.location ? `\`${f.location}\`` : ""} — ${f.title} [${f.evidence_class}]`);
  lines.push("", `${t.verification}:`);
  for (const v of r.verification) lines.push(`- \`${v.command}\` → ${t[v.status]}${v.status === "not_run" ? ` (${v.reason})` : ""}`);
  if (r.anyNotRun) lines.push(`- ⚠️ ${t.incomplete}`);
  if (links.length) lines.push("", ...links);
  if (requiredOf(r).length) lines.push("", t.menu);
  return lines.join("\n");
}

// ---------- main ----------
const args = process.argv.slice(2);
const flagValue = (name) => (args.includes(name) ? args[args.indexOf(name) + 1] : undefined);
const positional = args.filter((a, i) => !a.startsWith("--") && !args[i - 1]?.startsWith("--"));
const src = positional[0];
const format = flagValue("--format") ?? "all";
if (!src || !["chat", "md", "html", "all"].includes(format)) {
  console.error("usage: render-review.mjs <review.json> [--format chat|md|html|all] [--out-dir <dir>]");
  process.exit(2);
}
const outDir = flagValue("--out-dir") ?? dirname(src);

let record;
try { record = JSON.parse(readFileSync(src, "utf8")); }
catch (err) { console.error(`cannot read ${src}: ${err.message}`); process.exit(2); }

const { errors, counts: c } = validate(record);
if (errors.length) {
  console.error(`✖ ${src} is not a renderable review (${errors.length} problem(s)):`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}

record.generated_at ??= new Date().toISOString();
record.anyNotRun = record.verification.some((v) => v.status === "not_run");
const t = { ...L.en, ...(L[record.language] ?? {}), ...(record.labels ?? {}) };
const stem = basename(src).replace(/\.json$/, "");

// One record, one set of numbers — the chosen format only decides where they are shown.
if (format === "chat") {
  console.log(markdown(record, t, c)); // inline mode: the complete report, in chat, no files written
} else {
  const links = [];
  mkdirSync(outDir, { recursive: true });
  if (format === "md" || format === "all") {
    const p = join(outDir, `${stem}.md`);
    writeFileSync(p, markdown(record, t, c));
    links.push(`📄 ${p}`);
  }
  if (format === "html" || format === "all") {
    const p = join(outDir, `${stem}.html`);
    writeFileSync(p, html(record, t, c));
    links.push(`🌐 ${p}`);
  }
  console.log(chat(record, t, c, links));
}
