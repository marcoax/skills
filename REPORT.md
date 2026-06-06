# Skills Consolidation Report

**Data**: 2026-04-01
**Repo target**: `marcoax/skills`

---

## Risultato

### 20 skill unificate (da 56 originali)

| # | Skill | Origine | Note |
|---|-------|---------|------|
| 1 | agent-md-creator | repo (merge) | Versione repo 9-step, più completa della local 7-step |
| 2 | autoresearch | identica | Repo e local identiche |
| 3 | blazor-localization | solo repo | Skill specifica AF project |
| 4 | code-review | repo (merge) | Repo ha Step 5A/5B espliciti + UI italiana |
| 6 | current-file-review | solo repo | Review file corrente in PLAN MODE |
| 7 | design-an-interface | identica | "Design It Twice" pattern |
| 8 | get-api-docs | identica | Fetch API docs con chub |
| 9 | grill-me | identica | Interview relentless |
| 10 | laracms-code-review | solo repo | Code review specifico LaraCMS |
| 11 | log-analyzer | solo repo | Analisi log Symfony/Carimali |
| 12 | optimize-prompt | solo repo | Ottimizzazione prompt |
| 13 | php-tdd-workflow | solo repo | Workflow TDD PHP/Laravel |
| 14 | planning-with-files | solo repo | Planning con file di sessione |
| 15 | prd-to-issues | identica | PRD → GitHub issues |
| 16 | skill-optimizer | repo + local evals | SKILL.md identico, aggiunto evals.json da local |
| 17 | task-spec-creator | identica | Spec creator italiano |
| 18 | tdd | identica | TDD workflow con reference files |
| 19 | technical-debt-manager-php-laravel | solo repo | Gestione tech debt PHP |
| 20 | write-a-prd | identica | PRD writer |

### Escluse (36 skill)

- **21 skill da pbakaus/impeccable**: adapt, animate, arrange, audit, bolder, clarify, colorize, critique, delight, distill, extract, harden, imp-frontend-design, normalize, onboard, optimize, overdrive, polish, quieter, teach-impeccable, typeset
- **1 cartella vuota**: find-skills
- **1 workspace di eval**: laracms-code-review-workspace

### Merge effettuati

1. **skill-optimizer**: copiato `evals/evals.json` da local → repo (3 test case QA)
2. **agent-md-creator**: usata versione repo (Step 7-8 aggiuntivi per Reference Verification e STACK.md)
3. **code-review**: usata versione repo (branching Step 5A/5B più chiaro + UI italiana)

---

## CLI Tool: `@marcoax/skills`

### Installazione e uso

```bash
# Installa una skill nel progetto corrente
npx @marcoax/skills add grill-me

# Installa più skill
npx @marcoax/skills add grill-me tdd code-review

# Lista tutte le skill disponibili
npx @marcoax/skills list

# Info su una skill
npx @marcoax/skills info grill-me

# Aggiorna una skill
npx @marcoax/skills update grill-me

# Aggiorna tutte
npx @marcoax/skills update --all

# Rimuovi
npx @marcoax/skills remove grill-me

# Cerca
npx @marcoax/skills search "review"

# Installa globalmente (~/.claude/skills/)
npx @marcoax/skills add grill-me --global
```

### Come funziona

- Scarica le skill da `github.com/marcoax/skills/skills/<nome>/`
- Le installa in `.claude/skills/<nome>/` (o `~/.claude/skills/` con `--global`)
- Traccia versioni con `.skills-lock.json` (SHA del commit)
- Zero dipendenze esterne (solo Node.js built-in)

---

## Prossimi passi

1. **Crea il repo** `marcoax/skills` su GitHub
2. **Copia** il contenuto di `unified/skills/` nella root `skills/` del repo
3. **Copia** il contenuto di `unified/cli/` nella root `cli/` del repo (o come sottocartella)
4. **Pubblica** il pacchetto npm: `cd cli && npm publish --access public`
5. **Testa**: `npx @marcoax/skills list`

### Struttura repo consigliata

```
marcoax/skills/
├── skills/
│   ├── agent-md-creator/
│   ├── autoresearch/
│   ├── ... (20 skill)
│   └── write-a-prd/
├── cli/
│   ├── package.json
│   ├── bin/skills.mjs
│   ├── lib/...
│   └── README.md
├── README.md
└── LICENSE
```
