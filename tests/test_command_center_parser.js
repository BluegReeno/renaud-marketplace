/**
 * Offline tests for the Command Center daily-log parser.
 *
 * The dashboard joins each daily-log line to `halcrm_tasks` on `<workspace_slug>/<id>`.
 * These tests pin that join against BOTH log shapes: the pre-0.14.0 one (checkboxes,
 * truncated ids, several refs on one line) and the 0.14.0 one (numbered list, one task
 * per line, full 32-char id). No DOM, no connector — run with `node`.
 */
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

const PAGE = path.join(__dirname, "..", "dashboards", "command-center", "index.html");

function loadModule() {
  const html = fs.readFileSync(PAGE, "utf8");
  const m = /<script>([\s\S]*)<\/script>/.exec(html);
  assert.ok(m, "no <script> block found in the dashboard page");
  const sandbox = { module: { exports: {} }, window: undefined, console };
  sandbox.module.exports = {};
  vm.createContext(sandbox);
  vm.runInContext(m[1], sandbox, { filename: "command-center/index.html" });
  return sandbox.module.exports;
}

const CC = loadModule();

// Values built inside the vm sandbox carry that context's prototypes, so
// deepStrictEqual would reject structurally identical objects. Normalize first.
const plain = v => JSON.parse(JSON.stringify(v));

let passed = 0;
function check(name, fn) {
  fn();
  passed++;
  console.log("  ok  " + name);
}

// ── refsIn ────────────────────────────────────────────────────────────────
check("reads a full 32-char ref written in backticks", () => {
  const refs = CC.refsIn("  Liens : réf. hal `renaud/0fd22df8c1284b2f9a0e7d1c3b5a6e88`");
  assert.deepStrictEqual(plain(refs), [{ slug: "renaud", id: "0fd22df8c1284b2f9a0e7d1c3b5a6e88" }]);
});

check("reads a truncated ref with a trailing ellipsis (pre-0.14.0 logs)", () => {
  const refs = CC.refsIn("  Liens : réf. hal `renaud/0fd22df8c...`");
  assert.strictEqual(refs.length, 1);
  assert.strictEqual(refs[0].id, "0fd22df8c");
});

check("reads every ref on a merged line — the defect #94 fixed", () => {
  const line = "  Liens : réf. hal `renaud/efd74f73` `renaud/8a86bdd5` `renaud/a19cef1e`";
  assert.strictEqual(CC.refsIn(line).length, 3);
});

check("reads a ref written without backticks", () => {
  const refs = CC.refsIn("réf. hal renaud/cb5d38c2 — capture d'idée");
  assert.deepStrictEqual(plain(refs), [{ slug: "renaud", id: "cb5d38c2" }]);
});

check("never mistakes a LinkedIn job URL for a task id", () => {
  // `jobs/view/4452451971` is a slug-then-hex-looking pair; only the "réf. hal" run counts.
  const line = "  Liens : Offre `https://www.linkedin.com/jobs/view/4452451971` · réf. hal `renaud/025f8d3471ab4c9e8d2f6b0a3e5c7d19`";
  assert.deepStrictEqual(plain(CC.refsIn(line)),
    [{ slug: "renaud", id: "025f8d3471ab4c9e8d2f6b0a3e5c7d19" }]);
});

check("stops the ref run at the next link label", () => {
  const line = "  Liens : réf. hal `renaud/025f8d3471ab4c9e8d2f6b0a3e5c7d19` · Offre `https://www.linkedin.com/jobs/view/4452451971`";
  assert.deepStrictEqual(plain(CC.refsIn(line)),
    [{ slug: "renaud", id: "025f8d3471ab4c9e8d2f6b0a3e5c7d19" }]);
});

check("finds no ref in a line that has none", () => {
  assert.deepStrictEqual(plain(CC.refsIn("  ▶️ prochaines actions : appeler tante Claire.")), []);
});

// ── parseLog, 0.14.0 shape ────────────────────────────────────────────────
const LOG_0140 = [
  "# Daily log — Renaud (perso) — vendredi 14 août 2026",
  "",
  "## Sprint en cours [Renaud (perso)]",
  "⚠ Sprint `Renaud-7` clos le 07/08 mais toujours `actuel`.",
  "",
  "### jobsearch",
  "1. Dust — écrire la prep de l'onsite du 20/08 · priorité : high · échéance 2026-08-17",
  "  Liens : réf. hal `renaud/a8f1adb0c4d2416e8b7f5a1e9c3d2b60`",
  "  ▶️ prochaines actions : à faire après avoir les 4 noms.",
  "2. Prep screening Streem Energy · priorité : high · échéance 2026-08-14",
  "  Liens : réf. hal `renaud/025f8d3471ab4c9e8d2f6b0a3e5c7d19`",
  "  ▶️ prochaines actions : c'est le levier de négociation Dust.",
  "",
  "## Agenda du jour [Renaud (perso)]",
  "09:00 — Journée Bertrand",
  "",
  "## Notes",
  "(vide)"
].join("\n");

check("splits the 0.14.0 log into its ## sections", () => {
  const secs = CC.parseLog(LOG_0140);
  assert.deepStrictEqual(plain(secs.map(s => s.title)), [
    "Sprint en cours [Renaud (perso)]",
    "Agenda du jour [Renaud (perso)]",
    "Notes"
  ]);
});

check("reads one entry per numbered line, each with one full id", () => {
  const sprint = CC.parseLog(LOG_0140)[0];
  const entries = sprint.entries.filter(e => !e.sub);
  assert.strictEqual(entries.length, 2);
  entries.forEach(e => {
    assert.strictEqual(e.refs.length, 1, "one line = one task");
    assert.strictEqual(e.refs[0].id.length, 32, "the join key must survive whole");
  });
  assert.ok(entries[0].said.startsWith("Dust — écrire la prep"));
  assert.ok(entries[0].next.startsWith("à faire après avoir"));
});

check("keeps the ### tag subsection as a heading, not as a task", () => {
  const sprint = CC.parseLog(LOG_0140)[0];
  assert.deepStrictEqual(plain(sprint.entries.filter(e => e.sub).map(e => e.sub)), ["jobsearch"]);
});

check("keeps the sprint guard line as prose", () => {
  const sprint = CC.parseLog(LOG_0140)[0];
  assert.ok(sprint.prose.join("\n").includes("clos le 07/08"));
});

// ── parseLog, pre-0.14.0 shape (the logs that exist today) ────────────────
const LOG_OLD = [
  "# Daily log — Renaud (perso) — mercredi 12 août 2026",
  "",
  "## Sprint en cours [Renaud (perso)]",
  "",
  "### jobsearch",
  "- [ ] 🔴 Dust — bloc quotidien « maîtrise du produit » · échéance 2026-08-19",
  "  Liens : réf. hal `renaud/0fd22df8c...`",
  "  ▶️ prochaines actions : 30-45 min/jour sur dust.tt.",
  "- [ ] Relances en retard : Arcom, OpenAI FDE, OWKIN",
  "  Liens : réf. hal `renaud/c1fad83c` `renaud/6542e199` `renaud/eedb1327`",
  "  ▶️ prochaines actions : une seule session de relances au retour."
].join("\n");

check("reads the pre-0.14.0 checkbox entries and their refs", () => {
  const sprint = CC.parseLog(LOG_OLD)[0];
  const entries = sprint.entries.filter(e => !e.sub);
  assert.strictEqual(entries.length, 2);
  assert.strictEqual(entries[0].refs.length, 1);
  assert.strictEqual(entries[1].refs.length, 3, "a merged line still surfaces all its refs");
  assert.ok(!entries[0].said.includes("[ ]"), "the checkbox marker is stripped from the text");
});

// ── resolveRef ────────────────────────────────────────────────────────────
const FULL_A = "a8f1adb0c4d2416e8b7f5a1e9c3d2b60";
const FULL_B = "a8f1adb0ffffffffffffffffffffffff";

function seed(rows) {
  const S = CC.__state;
  S.tasks = { renaud: { todo: { rows: rows, err: null, stamp: 1, capped: false } } };
}

check("a full id joins exactly", () => {
  seed([{ id: FULL_A, status: "todo", title: "prep onsite" }]);
  const r = CC.resolveRef({ slug: "renaud", id: FULL_A });
  assert.strictEqual(r.state, "exact");
  assert.strictEqual(r.task.title, "prep onsite");
});

check("a full id with no matching task reports missing, never a false join", () => {
  seed([{ id: FULL_A, status: "todo", title: "prep onsite" }]);
  assert.strictEqual(CC.resolveRef({ slug: "renaud", id: FULL_B }).state, "missing");
});

check("a truncated id resolves only when exactly one task matches the prefix", () => {
  seed([{ id: FULL_A, status: "todo", title: "prep onsite" }]);
  const r = CC.resolveRef({ slug: "renaud", id: "a8f1adb0" });
  assert.strictEqual(r.state, "prefix");
  assert.strictEqual(r.task.id, FULL_A);
});

check("a truncated id matching several tasks stays unresolved", () => {
  seed([
    { id: FULL_A, status: "todo", title: "prep onsite" },
    { id: FULL_B, status: "todo", title: "autre tâche" }
  ]);
  const r = CC.resolveRef({ slug: "renaud", id: "a8f1adb0" });
  assert.strictEqual(r.state, "ambiguous");
  assert.strictEqual(r.n, 2);
});

check("a workspace whose tasks are not loaded reports unloaded, not missing", () => {
  seed([{ id: FULL_A, status: "todo", title: "prep onsite" }]);
  assert.strictEqual(CC.resolveRef({ slug: "blue-green", id: FULL_A }).state, "unloaded");
});

console.log("\n" + passed + " checks passed.");
