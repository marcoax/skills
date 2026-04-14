---
name: react-review
description: >
  React-specific code review for React 18/19 SPA projects (Vite, CRA). Applies battle-tested React best
  practices: state management (useReducer vs entangled useState), hooks correctness (Rules of Hooks,
  useEffect as synchronization, useLayoutEffect for DOM measurement), key prop usage (stable keys,
  key-as-reset), rendering performance (state colocation, memoization profiling, React Compiler awareness),
  data fetching (React Query/SWR, AbortController cleanup), component API design (compound components over
  prop soup), single-responsibility splits, state mutation safety, async useEffect patterns.
  Triggers: "review React", "revisiona componente", "check this hook", "controlla questo componente",
  "React code review", "revisiona hook", ".tsx review", "review useEffect", "review JSX", "review props",
  "controlla hook", "review questo componente". Does NOT trigger on generic "review"/"revisiona" alone —
  for generic reviews use code-review. Operates in PLAN MODE - proposes improvements, waits for approval.
---

# React Review

Code review specializzato per React 18/19 SPA (Vite / CRA). Basato sui 10 pattern più comuni di bug React + trasversali fondamentali. Opera in **plan mode**: propone, non esegue.

> **Language rule**: detect the language of the user's input and respond entirely in that language — including section headers, explanations, and questions. Never switch languages mid-conversation.

## Step 0: Scope selection

Se l'invocazione contiene già un path di file → **salta il menu, usa solo quel file** (Scope 1).

Altrimenti mostra il menu e aspetta la risposta:

| Input utente | Scope rilevato | Da chiedere ancora |
|---|---|---|
| `file <path>` / `controlla questo file <path>` | Scope 1 – File specifico | path se non incluso |
| `branch` / `branch diff` / `review branch` | Scope 2 – Branch diff | base branch — **chiedi sempre esplicitamente**, non inferire da git remote (hotfix/release safety) |
| `commit <hash>` | Scope 3 – Commit specifico | niente |
| `commit` (senza hash) | Scope 3 – Commit specifico | "Quale commit? (hash o 'last')" |
| `modifiche` / `uncommitted` / `controlla modifiche` | Scope 4 – Uncommitted | niente |

Se l'input non corrisponde a nessuna riga:

```
## ⚛️ React Review — Seleziona scope

1. 📄 File specifico — Revisiona un file
2. 🌿 Branch diff — Confronta branch corrente vs base
3. 📌 Commit specifico — Revisiona un commit
4. 📝 Modifiche uncommitted — Tutti i file modificati

Scope? (1/2/3/4)
```

### Parametri per scope

**Scope 1**: chiedi path se non fornito.

**Scope 2**: chiedi sempre la base branch esplicitamente; mostra branch corrente con `git rev-parse --abbrev-ref HEAD`. **Non inferire mai da git remote.**

**Scope 3**: se hash non fornito, mostra `git log --oneline -5`.

**Scope 4**: nessun parametro aggiuntivo.

**Formato output** (chiedi per tutti gli scope, prima di ExitPlanMode):
```
Formato output: (1) 💬 Inline chat  (2) 📄 File markdown report  ?
```
Aspetta la risposta. Salva come `[FORMAT]`.

## ⚠️ Plan Mode Gate — Chiama ExitPlanMode ora

Step 0 completo (scope + format confermati). Chiama `ExitPlanMode` prima di eseguire qualsiasi comando git.
I passi seguenti richiedono output git live — il plan mode produce diff vuoti.

## Step 1: Context gathering

### Progetto
```bash
cat CLAUDE.md 2>/dev/null || cat AGENT.md 2>/dev/null || echo "No project guidelines found"
cat package.json 2>/dev/null || echo "No package.json found"
```

Dalla lettura di `package.json`, determina il **project context** che guida i verdetti della checklist:

| Check | Rilevato se | Effetto sulla checklist |
|---|---|---|
| **React Compiler** | `react >= 19.0.0` AND (`babel-plugin-react-compiler` OR `vite-plugin-react-compiler`) in deps | Tip 7 si inverte: memo manuale → 🟡 Medium "remove, compiler handles it" |
| **Data-fetching lib** | `@tanstack/react-query` OR `swr` in deps | Tip T4b: raccomanda quella lib, non AbortController |
| **RTK / thunk** | `@reduxjs/toolkit` OR `redux-thunk` | Tip T4b: non suggerire React Query, usa il pattern Redux esistente |
| **State manager** | `zustand` / `@reduxjs/toolkit` / `jotai` / `mobx-react` / `recoil` / `valtio` / `xstate` | Tip T3: salta valori chiaramente in global store; Tip T4b: adatta fetch recommendation |
| **TypeScript** | `typescript` in deps | Abilita il finding TS typing (🟡 Medium) |
| **Test framework** | `jest` / `vitest` + `@testing-library/react` / `playwright` | Step 6: genera test nel framework corretto |

### Diff per scope
```bash
# Scope 1
git diff HEAD -- <filepath>
# Se nessun diff: git diff HEAD~1 -- <filepath>

# Scope 2
# ⛔ <base-branch> = esattamente quello che l'utente ha digitato. Mai sostituire con main/master/origin/HEAD.
git diff <base-branch>..HEAD --stat
git diff <base-branch>..HEAD
git diff <base-branch>..HEAD --name-only

# Scope 3
git show <commit-hash> --stat
git show <commit-hash>

# Scope 4
git status --short
git diff
git diff --cached
```

### Filtro file React

Dopo aver ottenuto la lista file, calcola:
`{file nello scope} ∩ {*.tsx, *.jsx, oppure file che importa da "react" / "react-dom"}`

- **Set vuoto** → esci: "Nessun file React trovato in questo scope. Usa `code-review` per file non-React."
- **Set parziale** → procedi sui soli file React. Elenca i file non-React ignorati con: "I seguenti file non sono stati analizzati (non-React) — considera `code-review` per un pass separato: [lista]"
- **Scope 2 con ≥10 file React** → mostra `--stat` e chiedi: "Il diff include N file React. Revisiono tutti insieme o file per file?"

**Nota target**: questo skill è ottimizzato per **React SPA classica (Vite/CRA, React 18/19)**. Se rilevi pattern Next.js App Router (`"use client"`, `"use server"`, `app/` directory, Server Components), segnalalo: "Next.js App Router patterns detected — questo skill analizza solo i pattern React puri visibili nel file." Se rilevi React Native (`react-native` import), segnalalo come out-of-scope.

## Step 2: React Review Checklist

Analizza il codice contro questa checklist. I verdetti si adattano al **project context** rilevato nello Step 1.

Per il razionale completo, la meccanica React e gli esempi canonici bad/good di un tip specifico, leggi `references/react-tips.md` alla sezione corrispondente.

---

### 🔴 CRITICAL

**[R-HOOKS] Rules of Hooks violations**
Chiamate hook condizionali (`if (x) useState(...)`), dentro loop, o in funzioni non-component/non-hook.
React dipende dall'ordine stabile delle chiamate hook ad ogni render — violarlo causa crash in produzione.

**[MUTATION] Mutazione diretta dello state**
`items.push(x); setItems(items)` / `obj.name = 'x'; setObj(obj)` / `.splice()`, `.sort()` su state direttamente.
React confronta per riferimento — mutare il vecchio oggetto e ri-settarlo non triggera re-render. Bug silenzioso.

**[T1-IMPOSSIBLE] Stati entangled → UI impossibili**
Tre `useState` separati per loading/error/data aggiornati con setter distinti che possono produrre stati contemporaneamente contraddittori (not-loading + error + data together).
*Adjustment*: applicabile anche se il progetto usa Zustand/Redux (impossible state esiste ovunque).
Fix: `useReducer` con reducer che garantisce transizioni valide.

**[T4C-LEAK] Memory leak: cleanup mancante in `useEffect`**
Subscription, listener, timer, WebSocket aperti dentro `useEffect` senza `return () => cleanup()`.
Il componente smonta ma il listener resta attivo → setState su componente smontato.

**[XSS] XSS via `dangerouslySetInnerHTML`**
Input utente inserito direttamente senza sanitizzazione (`dangerouslySetInnerHTML={{ __html: userInput }}`).

---

### 🟠 HIGH

**[ASYNC-EFFECT] `async` function passata direttamente a `useEffect`**
`useEffect(async () => { ... })` — la funzione ritorna una Promise, non una cleanup function. Il cleanup non funziona.
Fix: definire la `async` inside l'effect, chiamarla, ritornare il cleanup separatamente.
```js
// ❌
useEffect(async () => { const data = await fetch(...); setData(data); }, []);
// ✅
useEffect(() => {
  let cancelled = false;
  async function load() { const data = await fetch(...); if (!cancelled) setData(data); }
  load();
  return () => { cancelled = true; };
}, []);
```

**[T4B-FETCH] `useEffect` per data fetching**
`useEffect` con `fetch().then(setState)` senza cancellazione, caching, deduplicazione o race condition handling.
*Adjustment contestuale*:
- Se `@tanstack/react-query` o `swr` nel progetto → fix con quella lib (già installata, zero costo)
- Se `@reduxjs/toolkit` / thunk → usa il pattern Redux esistente (RTK Query / createAsyncThunk)
- Se nessuna lib → AbortController + cleanup + nota architetturale 🟡 "Consider adopting React Query/SWR"

**[T4A-DERIVED] `useEffect` per derivare state da altro state**
Usare `useEffect` che osserva uno state e ne aggiorna un altro — il valore derivato può essere calcolato in render.
Fix: calcolo diretto durante il render o `useMemo` (se costoso).

**[T5-KEY] `key={index}` su lista con children stateful**
Lista con `items.map((item, i) => <Component key={i} .../>)` dove Component ha state interno (input, form, useState).
React ricicla il DOM node sbagliato quando un item viene rimosso/riordinato → lo state rimane attaccato all'indice, non all'item.
*Severity adjustment*: lista puramente display (no state interno nei children) → scala a 🟢 Low.
Fix: `key={item.id}` — usa un ID stabile e unico dai dati.

**[T6-KEY-RESET] Reset di state via `useEffect` che osserva una prop**
`useEffect(() => { resetForm(); }, [userId])` per resettare state quando cambia una prop.
È fragile, si desincronizza, e causa un render intermedio con lo state "vecchio".
Fix: `<UserSettingsForm key={userId} userId={userId} />` — il cambio di key unmonta/rimonta il componente fresh.

**[T2-WRONG-TOOL] `useTransition` vs `debounce` confusi**
`useTransition` usato per operazioni network-bound (non risolve il bottleneck — il problema è il network, non il render).
Oppure: `debounce` usato per filtraggio in-memory di liste grandi (il bottleneck è il CPU/render, non la frequenza).
*Severity adjustment*: solo 🟠 High se il wrong-tool produce lag reale percepibile dall'utente.

**[T9-FLICKER] `useEffect` per misurazioni DOM che causano flicker**
`getBoundingClientRect` / `offsetHeight` / `scrollHeight` usati in `useEffect` per posizionamento stile (tooltip, dropdown, popover).
`useEffect` parte **dopo** il paint → flash di un frame nella posizione sbagliata.
Fix: `useLayoutEffect` — parte dopo il DOM update ma prima del paint.
*Reverse case* (🟢 Low): `useLayoutEffect` usato per operazioni che non necessitano misurazioni DOM → rimuovere, blocca il paint inutilmente.

---

### 🟡 MEDIUM

**[FUNC-UPDATE] Functional update mancante su setState**
`setCount(count + 1)` dentro un timer, listener, o `useEffect` con deps array vuota o parziale.
`count` viene catturato dalla closure al momento della creazione dell'effect — ogni aggiornamento usa il valore stale.
Fix: `setCount(c => c + 1)` — functional update legge il valore corrente dallo state interno di React.
*Trigger*: segnala solo quando il setter usa una variabile di state come operando dentro callback/timer/listener con possibile stale closure.

**[T3-COLOCATION] State tenuto troppo in alto → re-render cascata** ⚠️ `[SUGGEST ONLY]`
State in un componente parent che triggera re-render di siblings che non lo usano.
*Adjustment*: skip se i valori sono chiaramente in un global store (già colocato correttamente).
Fix: estrarre un wrapper component che contiene lo state + i figli che ne hanno bisogno. Da valutare prima di `React.memo`.

**[T8-SRP] Componente con ≥4 responsabilità distinte** ⚠️ `[SUGGEST ONLY]`
Componente che fa fetch + loading + error handling + rendering (quattro "reasons to change" distinti).
Fix: estrarre un custom hook (`useXxxData`) per la logica di dati, lasciare il componente solo presentazionale.
*Prima di proporre*: verifica se esiste già un hook riutilizzabile in `src/hooks/` o simili.

**[T10-PROP-SOUP] Prop soup con render props accumulate** ⚠️ `[SUGGEST ONLY]`
Componente con `renderHeader`, `renderBody`, `onToggle`, `isOpen`, `items` tutti come props — API che collassa su customizzazioni.
Fix: Compound Components pattern — parent + sub-component comunicano via Context.

**[TS-TYPING] Tipizzazione debole** *(solo progetti TypeScript)*
`any` espliciti, return type assenti su custom hook, props senza interface/type, asserzioni `as` non giustificate.

---

### 🟢 LOW

**[T7-MEMO] `useMemo`/`useCallback` su computazioni triviali**
Memoizzazione di string concatenation, arithmetic semplice, boolean, array di 2-3 elementi.
Il costo del hook (deps shallow-compare ad ogni render) supera il costo della computazione.
*Se React Compiler attivo (React 19 + plugin)* → scala a 🟡 Medium: "Remove — React Compiler handles memoization automatically; manual useMemo may interfere."

**[A11Y] Accessibilità JSX**
Input senza label/`htmlFor`, elementi interattivi non-button senza `role`/`onKeyDown`, modal senza focus trap, immagini senza `alt`.

**[CONVENTION] Convenzioni React**
Hook non denominati `useXxx`, componenti non PascalCase, side effect in render body (fuori da useEffect).

---

## Formato output

Usa il template seguente nel formato `[FORMAT]` scelto nello Step 0. Includi sempre tutte e 4 le sezioni severity — se vuota scrivi `_Nessun finding._`

I finding `SUGGEST ONLY` (T3, T8, T10) hanno il tag visibile e **non compaiono negli apply modes** — l'utente li valuta separatamente.

```markdown
## ⚛️ React Review: [scope description]

**Scope**: [file / branch / commit]
**File analizzati**: [N file React, M righe cambiate]
**Branch**: [corrente] vs [base] (solo scope 2)
**Project context**: React [version] · [data-fetching lib o "none"] · [state manager o "none"] · [React Compiler: yes/no]

---

### 🔴 Critical [N]
1. **[File:Line]** — [ID finding] [titolo]
   - **WHY**: [impatto]
   - **HOW**: [fix con codice]

### 🟠 High [N]
1. **[File:Line]** — [ID finding] [titolo]
   - **WHY**: [spiegazione]
   - **HOW**: [fix]

### 🟡 Medium [N]
1. **[File:Line]** — [ID finding] [titolo]
   - **WHY**: [spiegazione]
   - **HOW**: [fix] *(per SUGGEST ONLY: descrizione del refactor)*
   - ⚠️ `[SUGGEST ONLY — refactor, apri un task dedicato]` *(se applicabile)*

### 🟢 Low [N]
1. **[File:Line]** — [ID finding] [titolo]
   - **HOW**: [suggerimento]

### ✅ Positives
- [cosa è fatto bene e perché — es. key stabili usati correttamente, custom hook estratto per fetch, compound components in uso, nessun useEffect per derived state]

---

### 📊 Summary
| Severity | Count |
|----------|-------|
| 🔴 Critical | N |
| 🟠 High | N |
| 🟡 Medium | N |
| 🟢 Low | N |

**Overall score**: [A/B/C/D/F]
- **A**: 0 critical, 0 high, ≤2 medium
- **B**: 0 critical, 1–3 high, ≤2 medium
- **C**: 0 critical, AND (4+ high OR 3+ medium)
- **D**: esattamente 1 critical
- **F**: 2+ critical

---
Come vuoi procedere con i fix?
(1) 🔁 Uno alla volta — propongo ogni fix con spiegazione, tu decidi sì/skip
(2) ✅ Tutti insieme — applico tutto in una volta
(3) 🔢 Seleziona — dimmi i numeri (es. "1,3")
(4) ⏭️ Nessuno — solo review, niente modifiche

> I finding `[SUGGEST ONLY]` non sono inclusi nelle opzioni sopra — per realizzarli apri un task dedicato.
```

## Step 4: Attendi approvazione

**Non eseguire nulla** senza risposta esplicita:
- `"1"` / `"uno alla volta"` → Step 5A (interattivo)
- `"2"` / `"ok"` / `"tutti"` / `"all"` → Step 5B (bulk)
- `"3"` / `"1,3"` → Step 5B (selezionati)
- `"+tests"` → applica tutti + genera test
- `"4"` / `"no"` / `"skip"` / `"nessuno"` → niente fix
- `"only critical"` / `"solo 🔴"` → applica solo quella severity

## Step 5A: Modalità uno-per-uno

Per ogni fix (ordine: 🔴 → 🟠 → 🟡 → 🟢), **esclusi i finding SUGGEST ONLY**:

```
### Fix #N — [emoji] [severity]: [ID] [titolo]

**WHY**: [1-2 frasi di impatto]

**Modifica** in `file:riga`:
\`\`\`
// PRIMA
[codice vecchio]

// DOPO
[codice nuovo]
\`\`\`

Applico? (`sì` / `skip`)
```

Aspetta risposta prima di passare al fix successivo. Dopo tutti: mostra tabella riassuntiva applicati/saltati.

## Step 5B: Applica (bulk)

1. Applica i fix approvati in sequenza senza pause
2. Mostra tabella riassuntiva finale
3. Se un fix richiede una scelta (naming, pattern), chiedi prima di procedere

## Step 6: Test on-demand

**Non generare test spontaneamente.** Solo se il post-review prompt include `+tests`:
1. Rileva framework (dal project context Step 1: jest/vitest + `@testing-library/react`)
2. Genera test mirati **ai fix effettivamente applicati** (non a tutti i finding)
3. Path corretto: `__tests__/`, `*.test.ts`, `*.spec.tsx` in base alle convenzioni del progetto
4. Proponi in plan mode → attendi conferma prima di creare i file

## Step 7: Offerta revisione Codex

Al termine (fix applicati, saltati, o dopo i test), mostra **sempre**:

---
> Vuoi eseguire una revisione approfondita con **Codex**?
> Rispondi `sì` per lanciare `/codex:review`, oppure `no` per terminare.
---

- `sì` / `yes` / `ok` → invocare `Skill` con `skill: "codex:review"`
- `no` / `skip` / `n` → termina

## Rules

- **Mai eseguire senza approvazione**
- Se nessun `CLAUDE.md` → procedi con le best practice React di questo skill
- Se nessun diff per Scope 1 → analizza l'intero file come "new code"
- Cita sempre `file:riga` per ogni finding
- WHY = impatto concreto sul comportamento; HOW = fix con codice minimo
- I finding SUGGEST ONLY (T3, T8, T10) vanno nel template con tag visibile ma non negli apply modes
- Prima di proporre un nuovo custom hook, cerca in `src/hooks/`, `src/features/*/hooks/` — preferisci riuso
- Se il progetto usa un state manager esterno: Tip T3 non segnala valori già in global store; Tip T4b adatta la raccomandazione di fetch al pattern esistente (RTK Query, Zustand actions, ecc.)
- Target esplicito: React SPA classica. Next.js App Router, Remix, React Native = out-of-scope: segnala e limita il review ai pattern React puri visibili
- **Language**: rispondi nella stessa lingua dell'input utente
