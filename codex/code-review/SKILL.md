---
name: code-review
description: >
  Revisione codice in plan mode con scope multipli (file, diff branch, commit, uncommitted).
  Usa quando l'utente chiede review/revisione/controllo modifiche o vuole un report con severita e fix suggeriti.
---

# Code Review

Review completa del codice con scope multipli. Opera in plan mode: propone, non esegue.

## Step 0: Selezione scope

Se lo scope e gia specificato (es. "review branch", "review file X"), salta il menu.
Altrimenti mostra:

```
Code Review - Seleziona scope
1. Current file
2. Branch diff
3. Specific commit
4. Uncommitted changes
Scope? (1/2/3/4)
```

Parametri per scope:
- 1: chiedi path file se mancante
- 2: chiedi base branch, mostra current branch
- 3: chiedi hash o usa ultimo commit, mostra recenti
- 4: nessun parametro

## Step 1: Context + diff

Linee guida progetto (se esistono): `CLAUDE.md`, `AGENTS.md`, `AGENT.md`. Se assenti, best practices del linguaggio.

Comandi:
- Current file: `git diff HEAD -- <filepath>`; se vuoto, `git diff HEAD~1 -- <filepath>`
- Branch diff: `git diff <base>..HEAD --stat`, poi `git diff <base>..HEAD`
- Specific commit: `git show <hash> --stat`, poi `git show <hash>`
- Uncommitted: `git status --short`, `git diff`, `git diff --cached`

## Step 2: Checklist (adatta al framework)

- CRITICAL: security, data corruption
- HIGH: bug, performance, error handling
- MEDIUM: architecture, code quality, type safety
- LOW: style, accessibility (UI), testing gaps

## Step 3: Output

Chiedi formato:
```
Output: (1) Inline chat  (2) File markdown report?
```

Template breve:
```markdown
## Review: [scope]
Scope: [file/branch/commit]
Files: [N]
Branch: [current] vs [base] (solo scope 2)

Critical [N]
1. [File:Line] - titolo
   WHY: impatto
   HOW: fix

High [N]
...

Medium [N]
...

Low [N]
...

Punti positivi
- ...

Test suggeriti (se serve)
1. ...

Riepilogo
| Severita | Count |
| Critical | N |
| High | N |
| Medium | N |
| Low | N |
Score: A/B/C/D/F
```

## Step 4: Attendi approvazione

Non eseguire fix senza risposta esplicita.
- "ok/si/tutto": applica tutti
- "1,3": applica selezionati
- "+test": applica + propone test
- "no/skip": non applicare
- "solo critical/high": applica solo quella severita

## Step 5: Esecuzione fix

Applica una modifica alla volta, mostra il diff. Se servono scelte (naming, API), chiedi prima.

## Step 6: Test (se richiesti)

Individua framework test esistente. Proponi i test in plan mode e attendi conferma prima di creare file.

## Regole

- Mai eseguire senza approvazione
- Se nessun diff (scope 1), analizza file intero come nuovo codice
- Sempre indicare file e riga
- Sempre includere WHY e HOW
- Riconosci punti positivi
- Per branch diff grandi: overview e chiedi se procedere file per file
- Lingua: segue CLAUDE/AGENT; se assente, italiano
