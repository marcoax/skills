---
name: laracms-code-review
description: Review code changes against LaraCMS admin architecture guidelines and Laravel best practices. Use when the project context is clearly LaraCMS or Laravel admin work, or when the user mentions LaraCMS, admin architecture, guidelines/ADMIN_ARCHITECTURE.md, admin modules, resources, controllers, or other LaraCMS-specific conventions. Do not claim generic review requests outside clear LaraCMS context; use code-review for generic review and current-file-review only for explicit single-file review. Operates in PLAN MODE - proposes improvements, waits for approval before executing.
---

# LaraCMS Code Review

Review modifiche correnti rispetto a **guidelines/ADMIN_ARCHITECTURE.md** + best practices generali. Opera in **plan mode**: propone, non esegue.

## Workflow

```
1. Gather    → Leggi ADMIN_ARCHITECTURE.md + CLAUDE.md + diff
2. Analyze   → Confronta modifiche con regole architetturali + qualità generale
3. Propose   → Suggerimenti numerati, divisi per categoria
4. Wait      → Attendi approvazione esplicita
5. Execute   → Applica solo modifiche approvate
6. Learn     → Se scoperte nuove best practice, proponi di salvarle
```

## Step 1: Gather Context

Leggere **tutti** questi file prima di analizzare:

1. **Guidelines architetturali**: `guidelines/ADMIN_ARCHITECTURE.md` — fonte primaria delle regole
2. **Project guidelines**: `CLAUDE.md` — convenzioni generali del progetto
3. **Diff corrente**: tutte le modifiche non committate

```bash
# Diff completo (staged + unstaged)
git diff HEAD

# Se nessun diff, ultime modifiche committate
git diff HEAD~1
```

Se il diff tocca **più file**, analizzarli tutti — non solo il file "corrente".

## Step 2: Architecture Compliance Check

Verificare le modifiche rispetto a ADMIN_ARCHITECTURE.md. Checklist obbligatoria:

### Model (`app/*.php`)
- [ ] `$fillable` definito e completo
- [ ] `$casts` usato SOLO per boolean — mai per date
- [ ] `getFieldSpec()` presente con tipi corretti (`string`, `text`, `boolean`, `relation`, `date`, `select`, `media`, `component`)
- [ ] `newEloquentBuilder()` presente e punta al Builder corretto
- [ ] Nessun `scopeActive()` (già in `LaraCmsBuilder`)
- [ ] Logica query nel Builder, non nel model
- [ ] Wrapper statici sottili se necessari (delegano al Builder)
- [ ] PHP 7.2 compatibile: no arrow functions, no named args, no match, no nullsafe `?->`

### Date
- [ ] Datepicker usa getter/setter, MAI `$casts`
- [ ] Campi `date`/`date_end` → trait `DatePresenter`
- [ ] Altri nomi (`start_date`, `end_date`, ecc.) → getter/setter espliciti con `Carbon::parse()`
- [ ] Getter formatta `d-m-Y`, setter salva con `Carbon::parse($value)`

### Builder (`app/laraCms/Builders/*.php`)
- [ ] Estende `LaraCmsBuilder`
- [ ] Non ridefinisce `active()` / `inactive()` / `published()` (ereditati)
- [ ] Metodi query domain-specific presenti qui, non nel model

### Config admin (`config/laraCms/admin/list.php`)
- [ ] Chiave sezione coerente con nome tabella
- [ ] `model` punta alla classe corretta
- [ ] `roles` esplicitamente definiti
- [ ] `field` con tipi corretti (`text`, `relation`, `boolean`)
- [ ] Font Awesome 5 icon (senza prefisso `fa-`)

### Traduzione (`resources/lang/it/admin.php`)
- [ ] Entry sotto `models` in ordine alfabetico
- [ ] Nome italiano corretto

### Migration (`database/migrations/`)
- [ ] Nessun metodo `down()`
- [ ] File creato manualmente (no artisan)

### View / Controller
- [ ] Nessun controller custom se non esplicitamente richiesto
- [ ] Nessuna view custom se non esplicitamente richiesta

## Step 3: General Code Quality Check

Oltre all'architettura, verificare:
- Naming: `camelCase` (metodi/variabili), `PascalCase` (classi)
- No commenti superflui — codice autoesplicativo
- SOLID, DRY, Single Responsibility
- Nessuna vulnerabilità (SQL injection, XSS, ecc.)
- CSS in `rem` (non `px`) per nuovo codice
- Font Awesome 5 (`fas`, `far`, `fab` — no suffix `-o`)

## Step 4: Output Format

Italiano, **ultra-conciso**. Una riga per punto, niente spiegazioni ovvie. No snippet di codice salvo fix non banali. La sezione OK elenca solo 2-3 punti chiave, non tutto ciò che va bene.

```
## Review: [file(s)]

### Violazioni Architettura
1. `File:Riga` — [cosa] → [fix]

### Best Practices
1. `File:Riga` — [cosa] → [fix]

### Suggerimenti
1. `File:Riga` — [cosa]

### OK
- [2-3 punti principali che rispettano le guidelines]

Confermi? (tutto / numeri / nessuno)
```

Omettere sezioni vuote. Se tutto OK → "Nessuna violazione." e basta.

## Step 5: Wait for Approval

**NON eseguire nulla** senza risposta esplicita:
- "ok" / "sì" / "tutto" → applica tutti
- "1, 3" / "solo 1" → applica selezionati
- "+test" / "con test" → applica + genera test
- "no" / "skip" → non applicare

## Step 6: Execute Approved Changes

Applicare solo le modifiche approvate, una alla volta.

## Step 7: Auto-Learning

Durante la review, se noti un pattern o best practice che:
- Si ripete nel codebase ma NON è documentato in ADMIN_ARCHITECTURE.md
- Potrebbe prevenire errori futuri
- È specifico di LaraCMS (non una regola generica ovvia)

**Proponi di aggiungerlo** alla fine della review:

```
### Nuova Best Practice Scoperta
- [descrizione regola]
- [perché è importante]
- Aggiungo a ADMIN_ARCHITECTURE.md? (sì/no)
```

Se approvato, appendere la regola nella sezione appropriata di `guidelines/ADMIN_ARCHITECTURE.md`, mantenendo lo stile e il formato esistente.

**Non aggiungere mai senza approvazione.**

## Rules

- Mai eseguire senza approvazione
- Leggere SEMPRE `guidelines/ADMIN_ARCHITECTURE.md` fresco ad ogni review (potrebbe essere cambiato)
- Le violazioni architetturali hanno priorità maggiore delle best practice generali
- Se no diff → analizzare file intero come "nuovo codice"
- Citare sempre file e riga specifica
- Test: proporre solo se logica non coperta; rispettare framework esistente

## Debt Analysis Reminder

Alla fine di ogni review, se le modifiche toccano file ad **alto churn** (model, service, observer, config admin) o introducono logica non banale, aggiungere questa riga:

```
> Per un'analisi del debito tecnico su queste modifiche: `/technical-debt-manager-php-laravel revisiona le modifiche`
```

Non aggiungere il suggerimento se la review riguarda solo view, blade, o fix banali.
