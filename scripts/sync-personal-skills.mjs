#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { cpSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readdirSync, renameSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const personal = join(root, 'personal');
const repos = ['newEra', 'BlazorWCSWebUI_v8', 'teach-english'];
const locations = ['.agents/skills', '.claude/skills', '.vibe/skills'];
const env = { ...process.env, GIT_TERMINAL_PROMPT: '0' };

function git(cwd, ...args) {
    return execFileSync('git', args, { cwd, env, encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'] }).trim();
}

function listSkills(checkout) {
    const skills = new Map();
    for (const location of locations) {
        const base = join(checkout, location);
        if (!existsSync(base)) continue;
        if (!lstatSync(join(checkout, location.split('/')[0])).isDirectory() || !lstatSync(base).isDirectory()) {
            throw new Error(`Percorso sorgente non valido: ${location}`);
        }
        for (const entry of readdirSync(base, { withFileTypes: true })) {
            const { name } = entry;
            if (!entry.isDirectory() || !/^[a-z0-9][a-z0-9-]*$/.test(name) || name === 'deprecated') continue;
            const source = join(base, name);
            const skill = join(source, 'SKILL.md');
            if (existsSync(skill) && lstatSync(skill).isFile() && !skills.has(name)) {
                skills.set(name, { name, location, source });
            }
        }
    }
    return [...skills.values()].sort((a, b) => a.name.localeCompare(b.name));
}

async function sync() {
    const downloads = mkdtempSync(join(tmpdir(), 'personal-skills-'));
    const input = createInterface({ input: process.stdin, output: process.stdout });
    const lines = input[Symbol.asyncIterator]();
    async function ask(prompt) {
        process.stdout.write(prompt);
        const { value, done } = await lines.next();
        if (done) throw new Error('Input terminato: sincronizzazione annullata.');
        return value.trim();
    }

    try {
        const selected = [];
        for (const repo of repos) {
            const checkout = join(downloads, repo);
            console.log(`\n${repo}`);
            git(root, 'clone', '--quiet', '--single-branch', '--filter=blob:none', '--sparse', `https://github.com/marcoax/${repo}.git`, checkout);
            git(checkout, 'sparse-checkout', 'set', ...locations);
            const bucket = repo === 'teach-english' ? 'personal/teach-english' : 'personal';
            const skills = listSkills(checkout).map(skill => ({ ...skill, targetPath: `${bucket}/${skill.name}` }));
            const current = new Set(skills.map(({ name }) => name));
            const history = git(checkout, 'log', '--format=', '--name-only', '--no-renames', 'HEAD', '--',
                ...locations.map(location => `${location}/*/SKILL.md`));
            const removed = [...new Set(history.split('\n').flatMap(path => {
                const parts = path.split('/');
                return parts.length === 4 && parts[3] === 'SKILL.md' && /^[a-z0-9][a-z0-9-]*$/.test(parts[2])
                    && !current.has(parts[2]) ? [parts[2]] : [];
            }))].sort();
            if (removed.length) console.log(`  Nella cronologia, ma non più disponibili: ${removed.join(', ')}`);
            if (!skills.length) {
                console.log('  Nessuna skill trovata.');
                continue;
            }
            skills.forEach(({ name, location, targetPath }, i) => {
                const action = existsSync(join(root, targetPath)) ? 'sostituisci' : 'aggiungi';
                console.log(`  ${i + 1}. ${name} (${action}; ${location})`);
            });
            while (true) {
                const answer = await ask('Numeri separati da spazi o virgole (Invio = salta): ');
                if (!answer) break;
                const numbers = [...new Set(answer.split(/[\s,]+/).map(Number))];
                if (/^\d+(?:[\s,]+\d+)*$/.test(answer) && numbers.every(n => n >= 1 && n <= skills.length)) {
                    selected.push(...numbers.map(n => ({ ...skills[n - 1], repo })));
                    break;
                }
                console.log('Selezione non valida.');
            }
        }

        if (!selected.length) {
            console.log('\nNessuna skill selezionata.');
            return;
        }
        if (new Set(selected.map(({ name }) => name)).size !== selected.length) {
            throw new Error('Una skill è stata selezionata da più repo. Rilancia e scegli una sola sorgente per nome.');
        }
        console.log('\nSincronizzazione proposta:');
        for (const { repo, location, name, targetPath } of selected) console.log(`  ${repo}:${location}/${name} → ${targetPath}`);
        if ((await ask('Le cartelle selezionate saranno sostituite per intero. Confermi? [s/N] ')).toLowerCase() !== 's') {
            console.log('Nessuna modifica.');
            return;
        }

        if (!lstatSync(personal).isDirectory()) throw new Error('personal/ non è una directory reale.');
        const staging = mkdtempSync(join(personal, '.sync-'));
        try {
            for (const { name, source, targetPath } of selected) {
                const parent = dirname(join(root, targetPath));
                if (existsSync(parent) && !lstatSync(parent).isDirectory()) throw new Error(`Directory di destinazione non valida: ${parent}`);
                if (git(root, 'status', '--porcelain', '--untracked-files=all', '--ignored', '--', targetPath)) {
                    throw new Error(`Modifiche locali o file non tracciati in ${targetPath}; mettili al sicuro e riprova.`);
                }
                cpSync(source, join(staging, name), {
                    recursive: true,
                    filter(path) {
                        const stat = lstatSync(path);
                        if (!stat.isDirectory() && !stat.isFile()) throw new Error(`File sorgente non supportato: ${path}`);
                        return true;
                    },
                });
            }
            for (const { name, targetPath } of selected) {
                const target = join(root, targetPath);
                mkdirSync(dirname(target), { recursive: true });
                const backup = join(staging, `backup.${name}`);
                const replacing = existsSync(target);
                if (replacing) renameSync(target, backup);
                try {
                    renameSync(join(staging, name), target);
                } catch (error) {
                    if (replacing) renameSync(backup, target);
                    throw error;
                }
                rmSync(backup, { recursive: true, force: true });
                console.log(`Sincronizzata: ${targetPath}`);
            }
        } finally {
            if (readdirSync(staging).some(name => name.startsWith('backup.'))) {
                console.error(`Backup da conservare: ${staging}`);
            } else {
                rmSync(staging, { recursive: true, force: true });
            }
        }
        execFileSync(process.execPath, [join(root, 'scripts/generate-plugin.mjs')], { stdio: 'inherit' });
    } finally {
        input.close();
        rmSync(downloads, { recursive: true, force: true });
    }
}

sync().catch(error => {
    console.error(error.message);
    process.exitCode = 1;
});
