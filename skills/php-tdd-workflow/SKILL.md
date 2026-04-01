---
name: php-tdd-workflow
description: "Workflow strutturato per implementazione di piani tecnici PHP/Laravel con supporto TDD. Usa questa skill per progetti PHP/Laravel ogni volta che l'utente ha un piano, una specifica tecnica, o dice 'implementa questo', 'esegui il piano', 'partiamo con l'implementazione'. Gestisce l'intero ciclo: specifica, stress-test, decomposizione task, TDD, verifica, commit, delegando a /write-a-prd, /grill-me e /tdd quando disponibili. Garantisce un task alla volta, nessun salto di step, file di progresso sempre aggiornato."
---

# PHP TDD Workflow Skill

Skill per l'esecuzione interattiva e strutturata di piani di implementazione tecnica.

---

## Principio fondamentale

**Un task alla volta. Sempre.**

Il ciclo è:

```
DECOMPOSIZIONE → [per ogni task] PROPOSTA → EXPLAIN → APPROVA → IMPLEMENTA → VERIFICA → (COMMIT) → PROGRESS UPDATE
```

Nessuno step può essere saltato senza conferma esplicita dell'utente.

---

## Fase -1 — Pre-implementazione

All'avvio, mostrare un unico blocco compatto:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRE-IMPLEMENTAZIONE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] Scrivi una specifica da zero   → /write-a-prd
[2] Rivedi/stress-test il piano    → /grill-me
[3] Vai direttamente al piano      → decomposizione task
```

**Opzione 1 — `/write-a-prd`**: crea una specifica tramite intervista interattiva, esplora il codebase, produce un PRD strutturato. Al termine, tornare qui e procedere con l'opzione 2 o 3.

**Opzione 2 — `/grill-me`**: stress-test del piano esistente. L'agente intervista su ogni branch del decision tree finché non c'è comprensione condivisa completa. Al termine, procedere con la Fase 0.

**Opzione 3**: procedere direttamente alla decomposizione del piano.

Se una skill non è presente, notificare:
```
⚠️  Skill /[nome] non trovata.
Installala con: npx skills@latest add mattpocock/skills/[nome]
```

---

## Fase 0 — Decomposizione del piano

Prima di iniziare qualsiasi implementazione, analizzare il piano e produrre una lista di task atomiche.

### Criteri per un task atomico
- Tocca un numero limitato di file (idealmente 1-3)
- È verificabile in modo indipendente
- Ha un output chiaro (file creato, metodo aggiunto, test passato, ecc.)
- Non dipende da task non ancora completate (rispetta l'ordine)
- Se due task possono essere svolte in parallelo senza dipendenze reciproche, segnalarle come **[PARALLELA]**

### Output della decomposizione

Presentare la lista task in formato tabella:

```
| # | Task | File coinvolti | Verifica attesa | Parallelizzabile |
|---|------|---------------|-----------------|-----------------|
| 1 | ... | ... | ... | No |
| 2 | ... | ... | ... | No |
| 3 | ... | ... | ... | Sì (con #4) |
| 4 | ... | ... | ... | Sì (con #3) |
```

Dopo la tabella, chiedere:
> "Questa suddivisione ti sembra corretta? Vuoi aggiungere, rimuovere o accorpare task prima di iniziare?"

**Attendere conferma prima di procedere.**

### File di progresso

Alla conferma del piano, creare il file `progress_[nome-progetto].md` nella root del progetto:

```markdown
# Progress — [Nome Progetto]

**Avviato**: [data]
**Ultimo aggiornamento**: [data]
**Piano**: [breve descrizione]

## Task

| # | Task | Stato | Note |
|---|------|-------|------|
| 1 | ... | ⏳ in attesa | |
| 2 | ... | ⏳ in attesa | |

## Log

<!-- aggiornato automaticamente dopo ogni task -->
```

---

## Fase 1 — Ciclo per ogni task

### Step 1.1 — Proposta task

L'agente annuncia il task successivo:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK [N] di [TOTALE]: [Nome task]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File coinvolti: [lista]
Cosa farò: [1-2 righe descrizione]

[A] Approva e vai in Explain Mode
[S] Skippa questo task
[D] Discuti / chiedi spiegazioni
```

Attendere risposta utente.

### Step 1.2 — Explain Mode (se approvato)

Il livello di dettaglio dell'Explain Mode dipende dalla complessità del task:

**Task semplice** (es. aggiungere un campo a un model, una route, un piccolo metodo):
- 2-3 righe di descrizione
- Nessuno snippet se il pattern è ovvio
- Diretta: "Aggiungo X in Y perché Z. Procedo?"

**Task media** (es. un nuovo controller, una migration con logica, integrazione tra classi):
- Descrizione dell'approccio
- Pattern utilizzati (con riferimento a codice esistente se rilevante)
- Snippet dei blocchi non ovvi (non tutto il codice)

**Task complessa** (es. nuovo modulo, refactor significativo, logica algoritmica):
- Piano dettagliato con tutti i passaggi
- Snippet dei blocchi chiave
- Rischi e dipendenze esplicitate
- Eventuale discussione prima di confermare

Terminare sempre con:
> "Procedo con l'implementazione?"

**Attendere conferma. Se l'utente vuole discutere, restare in modalità chat finché non c'è conferma esplicita.**

### Step 1.3 — Implementazione

- Implementare solo ciò descritto nell'Explain Mode
- Nessuna modifica extra non discussa
- Aggiornare il file progress: task → 🔄 in corso

### Step 1.4 — Verifica

Al termine, presentare un riepilogo:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TASK [N] — Implementazione completata
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File modificati/creati:
  - [file 1]: [cosa è stato fatto]
  - [file 2]: [cosa è stato fatto]

Verifica suggerita: [comando o azione manuale]
```

Chiedere:
> "Hai verificato? Le modifiche sono corrette?"

Opzioni:
- **OK / Approvato** → procedere al commit step
- **C'è un problema** → correggere prima di avanzare (task resta 🔄 in corso)
- **Skip verifica** → procedere al commit step senza verifica

### Step 1.5 — Commit (sempre opzionale)

```
Vuoi committare le modifiche di questo task?
[Y] Sì  [N] No — vai al task successivo
```

Se sì:
```bash
git add [file modificati]
git commit -m "[tipo]: [descrizione concisa]"
```

Conventional commits: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`

Il commit step è sempre opzionale e non bloccante — se il progetto non usa git, saltare silenziosamente.

### Step 1.6 — Rollback (solo su richiesta esplicita)

Se l'utente chiede esplicitamente di annullare un task già implementato:

1. Elencare i file modificati dal task
2. Chiedere conferma: "Ripristino questi file allo stato precedente?"
3. Se confermato: eseguire `git checkout -- [file]` oppure ripristinare da backup se disponibile
4. Aggiornare progress: task → ↩️ rollback

L'agente **non esegue rollback automatici** — solo su richiesta esplicita.

### Step 1.7 — Aggiornamento progress file

Aggiornare `progress_[nome-progetto].md` **subito dopo** ogni task:

- Stato tabella: ✅ completato / ⏭ skippato / ↩️ rollback
- Aggiungere riga nel Log con timestamp e nota sintetica
- Questo file è il report definitivo del piano — non esiste un documento separato

---

## Formato del file di progresso (completo)

```markdown
# Progress — [Nome Progetto]

**Avviato**: [data]
**Ultimo aggiornamento**: [data]
**Piano**: [breve descrizione]

## Task

| # | Task | Stato | Note |
|---|------|-------|------|
| 1 | Migration blocked_dates | ✅ completato | |
| 2 | Model BlockedDate | ✅ completato | Aggiunto scope active() |
| 3 | Integrazione SlotGenerator | 🔄 in corso | |
| 4 | Variabile modale | ⏳ in attesa | |
| 5 | Snippet blade | ⏭ skippato | Rimandato a sprint successivo |
| 6 | Admin CRUD | ⏳ in attesa | |

## Log

- [2026-03-21 10:15] Task 1 completata — migration eseguita senza errori
- [2026-03-21 10:32] Task 2 completata — model con scope e metodi statici
- [2026-03-21 10:45] Task 3 iniziata

## Note

[osservazioni trasversali, problemi incontrati, decisioni prese durante l'implementazione]
```

---

## Modalità TDD (backend PHP)

Quando un task riguarda logica backend PHP (controller, service, model, command, ecc.), l'agente propone la modalità TDD **prima** dell'Explain Mode:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK [N]: [Nome task] — Backend PHP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vuoi implementare in modalità TDD?
[Y] Sì — ciclo red → green → refactor
[N] No — implementazione diretta
```

### Delega alla skill TDD

Se l'utente sceglie TDD, l'agente **deve caricare e seguire la skill `/tdd`** per l'intera esecuzione del task. Tutta la logica TDD (rilevamento framework, ciclo red→green→refactor, esecuzione test) è definita lì.

Se la skill `/tdd` **non è presente** nel progetto o non è disponibile, notificare l'utente:

```
⚠️  Skill /tdd non trovata.
Per usare la modalità TDD installa la skill oppure scegli
[N] per procedere con l'implementazione diretta.
```

Non implementare logica TDD autonomamente — la skill `/tdd` è la fonte di verità per quel workflow.

### Aggiornamento progress file in modalità TDD

Indipendentemente da come la skill /tdd gestisce internamente il ciclo, al completamento del task aggiornare il log con:

```markdown
- [10:15] Task 3 — TDD avviato (skill /tdd)
- [10:30] Task 3 — ✅ completato (tutti i test verdi)
```

---

## Task parallele

Quando due o più task sono marcate come **[PARALLELA]** nella tabella iniziale, l'agente può proporle insieme:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK PARALLELE: [#3] e [#4]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Queste task non hanno dipendenze reciproche e possono
essere implementate insieme.

[A] Implementa entrambe insieme
[S] Implementale in sequenza (prima #3, poi #4)
```

Le task parallele vengono comunque verificate e registrate singolarmente nel progress file.

---

## Regole hard

1. **Mai implementare più task in uno step** — salvo task marcate esplicitamente come parallele
2. **Mai procedere senza conferma esplicita** — silenzio = stop
3. **Mai modificare file non dichiarati nell'Explain Mode** — se emerge la necessità, dichiararlo e richiedere conferma
4. **Correggere prima di avanzare** — verifica fallita = task resta in corso
5. **Il progress file si aggiorna dopo ogni task** — è il documento definitivo del piano
6. **Rollback solo su richiesta esplicita** — mai automatico

---

## Comandi speciali utente

| Comando | Effetto |
|---------|---------|
| `status` / `dove siamo` | Mostrare stato corrente del progress file |
| `skip` | Saltare task corrente (⏭ nel progress) |
| `pausa` / `stop` | Fermare il workflow (progress salvato) |
| `riprendi` | Riprendere dal primo task non completato |
| `piano` | Mostrare tabella task con stati aggiornati |
| `rollback` | Avviare procedura rollback task corrente (su conferma) |

---

## Gestione errori e imprevisti

Se durante l'implementazione emerge un problema non previsto:

1. **Fermarsi immediatamente** — nessuna soluzione improvvisata
2. **Segnalare**: cosa è successo, perché blocca, opzioni disponibili
3. **Aspettare decisione** utente prima di procedere
4. Aggiornare progress con nota del problema

---

## Note contestuali (progetto astore)

Per il progetto `astore_new.test` / francoastore.it:
- Stack: Laravel 5.7, PHP 7.2, Vue 2, Bootstrap 3
- Prima di implementare admin CRUD: consultare `guidelines/ADMIN_ARCHITECTURE.md`
- Il file di progresso va nella root del progetto
- Conventional commits in italiano sono accettati se il progetto lo richiede
