---
name: task-spec-creator
description: Generate a structured task specification markdown file by interviewing the developer. Use this skill whenever the user wants to create a spec, define a task, start a new sprint ticket, document implementation requirements, or says things like "creiamo una specifica", "voglio definire la task", "ho un ticket da implementare", "partiamo dalla specifica". The skill conducts a context-aware interview and produces a ready-to-review TASK_SPEC.md file named after the Trello/Jira ticket ID.
---

# Task Spec Creator

Guida lo sviluppatore attraverso un'intervista strutturata per raccogliere i requisiti di una task e genera un file markdown di specifica revisabile.

---

## Regola fondamentale

**Mai chiedere info già fornite dall'utente.** Prima di ogni domanda, verifica se la risposta è già stata data nel messaggio iniziale o nelle risposte precedenti. Se un'informazione è deducibile dal contesto, non chiederla.

Preferisci **AskUserQuestion** per qualsiasi scelta con opzioni finite (tipo task, contesto, direzione MQTT, metodo HTTP, ecc.). Usa domande testuali libere solo per informazioni veramente aperte (descrizioni, strutture payload, path di file).

---

## Workflow

### Step 1 — Smart Intake (Extract First, Ask Second)

**Fase A — Estrazione automatica.** Analizza il messaggio iniziale dell'utente ed estrai:

| Campo | Come estrarre |
|---|---|
| **Ticket ID** | Numeri isolati o pattern `#1380`, `ticket 1380`, `1380-slug` |
| **Descrizione** | Frase principale che descrive l'obiettivo |
| **Contesto** | Deduci dalla tabella segnali (vedi sotto) |
| **Tipo** | "fix/bug/correzione" → Modifica; "nuovo/aggiungere/creare" → Nuova feature |
| **File coinvolti** | Path menzionati, nomi di classi, componenti |
| **Riferimenti** | Commit, PR, file simili menzionati |

Tabella segnali per il contesto:

| Contesto | Segnali chiave |
|---|---|
| `mqtt-command` | MQTT, comando, macchina, payload, hex, broker, packet |
| `backend-api` | endpoint, controller, API, Symfony, route |
| `frontend` | componente, React, UI, pagina, dashboard |
| `event-sourcing` | evento, aggregate, Broadway, CQRS, command handler |
| `migration` | migrazione, upgrade, PHP, Symfony version |
| `database` | MongoDB, query, aggregation, schema, indice |
| `generic` | nessun segnale specifico |

**Esempi di estrazione:**
- _"ticket 1380 fix product vending MQTT"_ → ticket=1380, contesto=mqtt-command, tipo=Modifica
- _"creare nuovo endpoint per lista macchine filtrate per modello"_ → contesto=backend-api, tipo=Nuova feature
- _"1402 aggiungere grafico consumo prodotti nella dashboard"_ → ticket=1402, contesto=frontend, tipo=Nuova feature

**Fase B — Mostra il riassunto.** Rispondi con:

> **Ecco cosa ho capito:**
> - **Ticket:** {id o "non specificato"}
> - **Descrizione:** {descrizione estratta}
> - **Contesto:** {contesto dedotto}
> - **Tipo:** {Nuova feature | Modifica}
> - **File coinvolti:** {lista o "da definire"}
> - **Riferimenti:** {riferimenti o "nessuno"}

**Fase C — Chiedi solo ciò che manca.** Usa **una singola chiamata AskUserQuestion** (max 4 domande) per le informazioni mancanti che hanno opzioni finite. Aggiungi domande testuali brevi solo per info aperte veramente mancanti.

Domande strutturate candidate (usa solo quelle necessarie):

- **Contesto** — solo se non deducibile → opzioni: mqtt-command, backend-api, frontend, event-sourcing, database, generic
- **Tipo** — solo se ambiguo → opzioni: Nuova feature, Modifica
- **Ticket ID** — solo se non fornito → chiedi come testo libero

Se il messaggio iniziale è sufficientemente completo, salta le domande e vai direttamente allo Step 2.

Aspetta la risposta prima di procedere.

---

### Step 2 — Deep Dive contestuale

In base al contesto confermato (o dedotto), raccogli le informazioni specifiche mancanti.

Usa **una singola chiamata AskUserQuestion** (max 4 domande) per le scelte strutturate. Aggiungi brevi domande testuali solo per info veramente aperte.

**Regola:** salta qualsiasi domanda la cui risposta è già stata fornita nello Step 1.

#### `mqtt-command`
**AskUserQuestion** (scelte finite):
- Direzione → opzioni: Server → Macchina, Macchina → Server, Bidirezionale
- Trigger → opzioni: Evento Broadway, Endpoint API, Console command, Schedulato
- Persistenza MongoDB → opzioni: Sì, No

**Testo libero** (solo se mancanti):
- Byte hex del comando (es. `0x2A`)
- Struttura payload (campi, lunghezza)
- Comando simile come riferimento

#### `backend-api`
**AskUserQuestion** (scelte finite):
- Metodo HTTP → opzioni: GET, POST, PUT, PATCH, DELETE
- Auth richiesta → opzioni: Sì (specificare ruolo), No

**Testo libero** (solo se mancanti):
- Route prevista
- Input atteso (body, query params)
- Output atteso (struttura risposta)
- Controller simile come riferimento

#### `frontend`
**AskUserQuestion** (scelte finite):
- Dati da → opzioni: API esistente, Nuova API da creare, Dati locali/props

**Testo libero** (solo se mancanti):
- Pagina o sezione dell'app coinvolta
- Interazioni utente previste
- Componente simile come riferimento

#### `event-sourcing`
**AskUserQuestion** (scelte finite):
- Trigger del Command → opzioni: Controller, Listener, Console command
- Serve Projector → opzioni: Sì, No
- Serve MQTT Listener → opzioni: Sì, No

**Testo libero** (solo se mancanti):
- Nome del Command e del relativo Event

#### `migration`
**Testo libero:**
- Versione di partenza e versione target
- Componenti coinvolti (PHP, Symfony, dipendenze specifiche)
- Breaking changes noti

#### `database`
**AskUserQuestion** (scelte finite):
- Tipo di operazione → opzioni: Query, Aggregation, Nuovo indice, Schema change

**Testo libero** (solo se mancanti):
- Collezione/tabella coinvolta
- Volume dati stimato / performance requirements

#### `generic`
**Testo libero:**
- Input e output attesi
- Dipendenze note
- Vincoli tecnici o di business

---

### Step 3 — Generazione del file

Dopo aver raccolto tutte le risposte, genera il file con questo nome:

```
{ticket-id}.md               # se solo ID numerico
{ticket-id}-{slug}.md        # se fornito anche lo slug
```

Usa il template qui sotto, compilando solo le sezioni pertinenti al contesto. Ometti sezioni vuote o non applicabili.

---

## Template TASK_SPEC.md

```markdown
# {ticket-id} — {titolo task}

**Contesto:** {mqtt-command | backend-api | frontend | event-sourcing | migration | database | generic}  
**Tipo:** {Nuova feature | Modifica}  
**Data:** {data corrente}

---

## Descrizione

{descrizione fornita dallo sviluppatore}

---

## File / Funzionalità coinvolti

{lista file o funzionalità da modificare, se task di modifica}

---

## Requisiti tecnici

{sezione compilata in base al contesto — vedi sotto}

---

## Implementazione

### Componenti da creare / modificare

{lista strutturata dei componenti, con path e descrizione breve}

### Flusso

{descrizione del flusso tecnico, es. trigger → command → handler → event → listener → MQTT}

---

## Riferimenti

{file o pattern esistenti da seguire come riferimento}

---

## Note aperte

{dubbi, punti da verificare, dipendenze esterne}
```

---

## Sezioni contestuali per "Requisiti tecnici"

### mqtt-command
```markdown
| Campo | Valore |
|---|---|
| Comando (hex) | `0xXX` |
| Direzione | Server → Macchina |
| Trigger | Evento Broadway / endpoint API / console command |
| Payload | {struttura campi se nota} |
| Persistenza MongoDB | Sì / No |
| Riferimento esistente | {path file simile} |
```

### backend-api
```markdown
| Campo | Valore |
|---|---|
| Method + Route | `GET /api/v1/...` |
| Input | {parametri} |
| Output | {struttura risposta} |
| Auth | {ruolo/permesso richiesto} |
| Riferimento | {controller esistente} |
```

### frontend
```markdown
| Campo | Valore |
|---|---|
| Sezione | {pagina/sezione app} |
| Dati | {provenienza e struttura} |
| Interazioni | {azioni utente} |
| Riferimento | {componente simile} |
```

### event-sourcing
```markdown
| Campo | Valore |
|---|---|
| Command | `{CommandName}` |
| Event | `{EventName}` |
| Trigger | {chi dispatcha il command} |
| Projector | Sì / No — {read model aggiornato} |
| MQTT Listener | Sì / No |
```

---

## Comportamento

- Fai le domande in italiano se l'utente scrive in italiano
- Non generare il file prima di aver ricevuto le risposte alle domande contestuali
- Se una risposta è ambigua, chiedi chiarimento prima di procedere
- Dopo aver generato il file, mostralo e chiedi: "Vuoi modificare qualcosa prima di salvarlo?"
- Salva il file nella directory corrente o in `docs/specs/` se esiste nel progetto
- Dopo il salvataggio, proponi la creazione di test se pertinente al contesto:
  - `mqtt-command` → test su PacketHandler/PacketSender, mock del broker
  - `backend-api` → test funzionali sul controller (WebTestCase Symfony)
  - `frontend` → non proporre test di default (chiedere esplicitamente)
  - `event-sourcing` → test su Command Handler e Aggregate (Broadway InMemoryEventStore)
  - `database` → test sull'aggregation pipeline con fixture MongoDB
  - Per gli altri contesti, valuta caso per caso e proponi solo se ha senso
- Formula la proposta così: "Vuoi che aggiunga una sezione **Test** alla specifica?" e se confermato aggiungi la sezione al file con i test case suggeriti (non il codice, solo la descrizione di cosa testare)
