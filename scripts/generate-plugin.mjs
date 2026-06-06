#!/usr/bin/env node
// Rigenera .claude-plugin/plugin.json dai bucket pubblici.
// Uso: node scripts/generate-plugin.mjs        (scrive il file)
//      node scripts/generate-plugin.mjs --check (esce 1 se disallineato)
import { readdirSync, statSync, existsSync, writeFileSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const BUCKETS = ["planning", "review", "skill-management", "utilities", "personal"];
const EXCLUDE = new Set(["deprecated", "node_modules", ".git"]);
const PLUGIN_NAME = "marcoax-skills";

const skills = [];
for (const bucket of BUCKETS) {
    const base = join(ROOT, bucket);
    if (!existsSync(base)) continue;
    for (const entry of readdirSync(base)) {
        if (EXCLUDE.has(entry)) continue;                       // salta personal/deprecated
        const dir = join(base, entry);
        if (!statSync(dir).isDirectory()) continue;
        if (existsSync(join(dir, "SKILL.md"))) skills.push(`./${bucket}/${entry}`);
    }
}
skills.sort();

const json = JSON.stringify({ name: PLUGIN_NAME, skills }, null, 2) + "\n";
const out = join(ROOT, ".claude-plugin", "plugin.json");

if (process.argv.includes("--check")) {
    const current = existsSync(out) ? readFileSync(out, "utf8") : "";
    if (current !== json) { console.error("plugin.json non aggiornato: esegui node scripts/generate-plugin.mjs"); process.exit(1); }
    console.log("plugin.json aggiornato ✓");
} else {
    writeFileSync(out, json);
    console.log(`Scritte ${skills.length} skill in .claude-plugin/plugin.json`);
}