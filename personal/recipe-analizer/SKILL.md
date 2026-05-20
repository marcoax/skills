---
name: recipe-analizer
description: Analizza le ricette delle macchine filtrando per tipo sotto-prodotto (products[].type) e genera statistiche di frequenza sui valori degli attributi tecnici. Produce output in HTML, Markdown e CSV. Usare quando l'utente chiede di analizzare ricette per tipo, fare statistiche su attributi ricette, o dice cose come "statistica ricette tipo=3", "analizza ricette latte", "leggi i file e fai statistica degli attributi delle ricette tipo X".
---

# Skill: Analisi Statistica Ricette per Tipo Sotto-Prodotto

## Trigger

L'utente dirà qualcosa come:

- *"Leggi i file in questa cartella e fai una statistica degli attributi delle ricette di tipo=3"*
- *"Analizza le ricette latte in `C:\work_aa\analisi-latte-silver\`"*
- *"Statistica attributi ricette tipo 3"*
- *"Analizza ricette type=X"*

## Obiettivo

Analizzare le ricette delle macchine filtrando per **tipo sotto-prodotto**, generare statistiche di frequenza sui valori degli attributi tecnici con selezione interattiva, e produrre output in **tre formati**: HTML interattivo, Markdown, CSV.

---

## Modello dati

Il file `machine_recipes.json` è un **array** di oggetti macchina:

```json
[
  {
    "_id": "12855888-cf97-11e7-a753-0800275ae9e7",
    "payload": {
      "machineId": "12855888-cf97-11e7-a753-0800275ae9e7",
      "recipes": {
        "7": {
          "doseRef": 7, "enable": "Y", "...": "...",
          "products": [
            { "type": 5, "foamedMilkPre": 30, "...": "..." },
            { "type": 3, "mixerAMixerSpeed": 95, "mixerADensity": 33, "...": "..." }
          ]
        }
      }
    }
  }
]
```

Regole fondamentali:

- Il filtro `tipo=N` opera su `recipe.products[].type`, **non** su un campo a livello ricetta.
- Ogni sotto-prodotto con `type==N` è **un'osservazione separata**: se una ricetta ha due sotto-prodotti con type=3, contano come due record nelle frequenze.
- Gli attributi analizzabili sono le chiavi del sotto-prodotto (esclusa `type`). Set di attributi diversi per type diversi (es. type=3 ha `mixerA*`/`mixerB*`, type=5 ha `pumpSpeedL*`, ecc.).

---

## Input attesi

### File dati

Nella cartella indicata dall'utente (tipicamente `C:\work_aa\analisi-latte-silver\`):

- **Ricette**: `machine_recipes.json`
- **UUID macchine da includere**: `data\silver_uuid.csv` (CSV con header `id` e una colonna di UUID). L'utente può fornire un path diverso: in quel caso **sostituisce** il default.

### Documentazione di riferimento

- **Mappatura tipi prodotto**: `C:/Users/angelo.asperti/Desktop/Obsidian/Caricare/llm.wiki/wiki/concetti/protocolli/tipi-prodotto-ricette.md`

### Parametro utente

- `tipo` — numerico (`tipo=3`) o nome (`tipo=latte`). La skill risolve il nome → codice tramite il file di mappatura.

---

## Flusso interattivo

### Step 1 — Risoluzione parametri

1. Identifica la cartella di lavoro (argomento utente o cwd).
2. Risolvi il tipo: se numerico usa diretto; se nome, consulta il file di mappatura per ottenere il codice.
3. Decidi il file UUID da usare: quello indicato dall'utente, altrimenti il default `data/silver_uuid.csv`.

### Step 2 — Probe osservazioni e chiedi quali attributi analizzare

Prima di generare i report, esegui lo script in **modalità sondaggio** (con `--attrs all` ma senza scrivere output, oppure leggendo il file JSON direttamente) per sapere quanti sotto-prodotti e quali chiavi sono presenti. In alternativa, parsa il JSON inline per calcolare l'unione delle chiavi osservate.

Poi **chiedi sempre all'utente**:

> "Ho trovato **N osservazioni** (sotto-prodotti type=3) su M macchine. Quali attributi vuoi analizzare?
>
> Attributi disponibili: `mixerASequence, mixerAWaterVolume, mixerAMixerSpeed, mixerAPosWaterVolume, mixerADensity, mixerBSequence, mixerBWaterVolume, mixerBMixerSpeed, mixerBPosWaterVolume, mixerBDensity, pauseSolDrink, repetitions`
>
> Indica la lista (separati da virgola), oppure rispondi `tutti` / vuoto per analizzarli tutti."

**Perché chiedere sempre**: ogni dataset ha attributi significativi diversi; analizzarli tutti automaticamente produce rumore su decine di colonne irrilevanti. La selezione guidata è il punto centrale della skill, non un dettaglio opzionale. **Non assumere mai un default silenzioso**.

Comportamento:
- Lista fornita → passa solo quegli attributi allo script
- `tutti` / vuoto → passa `all`
- Attributo inesistente → lo script emette warning su stderr e procede con quelli validi

### Step 3 — Esegui lo script

Delega l'intero calcolo e rendering a `scripts/analyze_recipes.py`. Non reimplementare statistiche o generazione HTML a mano.

```
python <skill_dir>/scripts/analyze_recipes.py \
  --recipes <work_dir>/machine_recipes.json \
  --type 3 \
  --uuid-file <path>                     # opzionale; default = <work_dir>/data/silver_uuid.csv
  --attrs mixerAMixerSpeed,mixerADensity \
  --out-dir <work_dir>/output/
```

Lo script stampa su stdout i path dei tre file generati più un mini-riepilogo (osservazioni, macchine, attributi).

### Step 4 — Comunicazione finale

Riporta all'utente:

- Path assoluti dei tre file (`.html`, `.md`, `.csv`)
- Riepilogo: numero osservazioni, numero macchine coinvolte, numero attributi analizzati
- Opzionalmente: i 2-3 attributi con maggiore varianza (ricavabili dal CSV o dal summary)
- Offri di aprire l'HTML nel browser

---

## Formati di output (generati dallo script)

Tutti i file hanno lo stesso prefisso `statistiche_tipo-<N>_YYYY-MM-DD_HHMM`:

- **CSV** (`UTF-8 con BOM`, separatore `,`, long format):
  ```csv
  attributo,valore,occorrenze,percentuale
  mixerAMixerSpeed,50,45,51.7
  mixerAMixerSpeed,70,22,25.3
  ```
- **Markdown** (tabelle GitHub-flavored, una per attributo, ordinate per occorrenze desc).
- **HTML** standalone (CSS inline, nessuna CDN), con header metadati, indice cliccabile, tabelle zebrate con barra di progresso CSS per la percentuale, stampabile.

---

## Requisiti tecnici

- HTML **self-contained**: nessun CDN, nessuna risorsa esterna, apribile offline.
- CSV con separatore `,` e encoding UTF-8 con BOM (compatibilità Excel IT).
- Markdown con tabelle GitHub-flavored.
- Tutti i file con stesso prefisso/timestamp per correlazione.
- Path di output sempre assoluti nella risposta finale.
- Lo script usa solo stdlib Python (nessun `pip install`).

---

## Criteri di qualità

- L'agent **deve sempre chiedere** quali attributi analizzare prima di procedere (mai assumere).
- Se il tipo non è specificato, chiederlo prima di procedere.
- Produrre **tutti e tre i formati** (HTML + MD + CSV), mai solo uno — garantito dallo script.
- Non inventare valori: file mancanti o tipi sconosciuti vanno segnalati chiaramente (exit code ≠ 0 dello script).
- Tabelle sempre ordinate per occorrenze decrescenti.
- Percentuale calcolata sul numero di osservazioni che hanno quell'attributo (non sul totale complessivo), così attributi presenti solo in una parte dei record non risultano artificialmente "bassi".
