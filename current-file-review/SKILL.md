---
name: current-file-review
description: Review changes in one explicitly identified current or open file against project best practices. Use only when the user clearly refers to the current file, says "this file", "current file", "open file", or provides a single file path to review. Do not use for generic review requests, branch diffs, commits, or repository-wide review; use code-review or a stack-specific review skill instead. Operates in PLAN MODE - proposes improvements, waits for approval before executing.
---

# Current File Review

Review modifiche del file corrente rispetto alle best practices del progetto. Opera in **plan mode**: propone, non esegue.

## Workflow

```
1. Identify   → Trova file corrente e CLAUDE.md/AGENT.md
2. Analyze    → Leggi diff (git) + best practices progetto
3. Propose    → Elenca suggerimenti numerati
4. Wait       → Attendi approvazione esplicita
5. Execute    → Applica solo modifiche approvate
```

## Step 1: Gather Context

```bash
# File corrente (da contesto editor o chiedere)
# Cercare best practices
cat CLAUDE.md 2>/dev/null || cat AGENT.md 2>/dev/null || echo "No project guidelines found"

# Diff del file (modifiche non committate)
git diff HEAD -- <filepath>

# Se nessun diff, mostra ultime modifiche
git diff HEAD~1 -- <filepath>
```

## Step 2: Analyze Against Best Practices

Verificare che le modifiche rispettino:
- Convenzioni definite in CLAUDE.md/AGENT.md
- Pattern e stili del progetto
- Naming conventions
- Error handling richiesto
- Struttura codice attesa

## Step 3: Output Format

Usare la **lingua di CLAUDE.md**. Stile conciso.

```
## Review: [filename]

**Diff analizzato**: [righe modificate]

### Violazioni Best Practices
1. [Riga X] - [problema] → [soluzione]
2. ...

### Miglioramenti Suggeriti
1. [Riga X] - [cosa] → [perché]
2. ...

### 🧪 Test Suggeriti
[Solo se modifiche toccano logica non coperta da test]
1. [Descrizione test] → [cosa verifica]
2. ...

### ✅ OK
- [cosa rispetta le guidelines]

---
Confermi? (tutto / numeri / nessuno / +test)
```

## Step 4: Wait for Approval

**NON eseguire nulla** senza risposta esplicita:
- "ok" / "sì" / "tutto" → applica tutti
- "1, 3" / "solo 1" → applica selezionati  
- "+test" / "con test" → applica + genera test
- "no" / "skip" → non applicare

## Step 5: Execute Approved Changes

Applicare solo le modifiche approvate, una alla volta, mostrando il diff risultante.

## Step 6: Generate Tests (se richiesto)

Se approvato con "+test":
1. Identificare framework test del progetto (da CLAUDE.md o struttura cartelle)
2. Generare test per la logica modificata
3. Posizionare nel path corretto (es. `tests/`, `__tests__/`, `*.test.ts`)
4. Proporre test in plan mode → attendere conferma prima di creare file

## Rules

- **Mai eseguire senza approvazione**
- Se no CLAUDE.md → segnalare, procedere con best practices generali
- Se no diff → analizzare file intero come "nuovo codice"
- Suggerimenti concisi, no verbosità
- Citare sempre la riga specifica
- **Test**: proporre solo se logica non coperta; rispettare framework esistente
