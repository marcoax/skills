---
name: recipe-analizer
description: Analizza le ricette delle macchine filtrando per tipo prodotto (productType) e genera statistiche di frequenza sui valori degli attributi tecnici. Produce output in HTML, Markdown e CSV. Usare quando l'utente chiede di analizzare ricette per tipo, fare statistiche su attributi ricette, o dice cose come "statistica ricette tipo=3", "analizza ricette latte", "leggi i file e fai statistica degli attributi delle ricette tipo X".
---

# Skill: Analisi Statistica Ricette per Tipo Prodotto

## Trigger

L'utente dirà qualcosa come:

- *"Leggi i file in questa cartella e fai una statistica degli attributi delle ricette di tipo=3"*
- *"Analizza le ricette latte in `C:\work_aa\analisi-latte-silver\`"*
- *"Statistica attributi ricette tipo 3"*
- *"Analizza ricette productType=X"*

## Obiettivo

Analizzare le ricette delle macchine filtrando per tipo prodotto, generare statistiche di frequenza sui valori degli attributi tecnici con selezione interattiva, e produrre output in **tre formati**: HTML interattivo, Markdown, CSV.

---

## Input attesi

### File dati

Nella cartella indicata dall'utente (tipicamente `C:\work_aa\analisi-latte-silver\`):

- **Ricette**: `machine_recipes.json`
- **Matricole da analizzare**: `data\silver_serial.csv`

### Documentazione di riferimento

- **Mappatura tipi prodotto**: `C:/Users/angelo.asperti/Desktop/Obsidian/Caricare/llm.wiki/wiki/concetti/protocolli/tipi-prodotto-ricette.md`

### Parametro utente

- `tipo` — numerico (`tipo=3`) o nome (`tipo=latte`). La skill risolve il nome → codice tramite il file di mappatura.

---

## Flusso interattivo

### Step 1 — Lettura e filtro

1. Carica le matricole dal CSV `silver_serial.csv`
2. Carica le ricette da `machine_recipes.json`
3. Risolvi il tipo richiesto (nome → codice se necessario, consultando il file di mappatura)
4. Filtra le ricette: appartenenti alle matricole del CSV **E** con `recipe.productType` = tipo richiesto
5. Comunica all'utente quante ricette sono state trovate

### Step 2 — Selezione attributi (interattiva)

Dopo il filtro, **l'agent deve chiedere all'utente**:

> "Ho trovato **N ricette** di tipo=3 (latte). Quali attributi vuoi analizzare?
>
> Attributi disponibili nelle ricette filtrate:
> `mixerASequence`, `mixerAWaterVolume`, `mixerAMixerSpeed`, `mixerAPosWaterVolume`, `mixerADensity`, `mixerBSequence`, `mixerBWaterVolume`, `mixerBMixerSpeed`, `mixerBPosWaterVolume`, `mixerBDensity`, `pauseSolDrink`, …
>
> Indica la lista (separati da virgola) oppure rispondi `tutti` / vuoto per analizzarli tutti."

**Comportamento in base alla risposta:**

- Lista fornita → analizza solo gli attributi specificati
- `tutti` / vuoto → analizza **tutti** gli attributi presenti
- Attributo inesistente → warning e chiedi conferma se procedere con gli altri

### Step 3 — Calcolo statistiche

Per ogni attributo selezionato, calcola la distribuzione di frequenza dei valori osservati nelle ricette filtrate (conteggio assoluto + percentuale).

### Step 4 — Generazione output

L'agent **deve sempre produrre tutti e tre i file**, salvandoli in una sottocartella `output/` nella cartella di lavoro, con timestamp nel nome:

```
output/
├── statistiche_tipo-3_2026-04-22_1430.html
├── statistiche_tipo-3_2026-04-22_1430.md
└── statistiche_tipo-3_2026-04-22_1430.csv
```

#### 4.1 — File Markdown (`.md`)

Una tabella per ogni attributo, ordinata per occorrenze decrescenti:

```markdown
# Statistiche ricette — tipo=3 (latte)

**Totale ricette analizzate:** 87
**Matricole coinvolte:** 42
**Data analisi:** 2026-04-22 14:30

## mixerAMixerSpeed
5 valori distinti

| valore | occorrenze | %     |
|--------|------------|-------|
| 50     | 45         | 51.7% |
| 70     | 22         | 25.3% |
| ...    | ...        | ...   |

## mixerADensity
...
```

#### 4.2 — File CSV (`.csv`)

Formato long, un record per ogni coppia attributo-valore:

```csv
attributo,valore,occorrenze,percentuale
mixerAMixerSpeed,50,45,51.7
mixerAMixerSpeed,70,22,25.3
mixerAMixerSpeed,60,15,17.2
mixerADensity,20,60,69.0
...
```

#### 4.3 — File HTML (`.html`)

Report standalone **single-file** (CSS inline, nessuna dipendenza esterna), con:

- **Header**: titolo, tipo prodotto (codice + nome), totale ricette, totale matricole, data analisi
- **Indice** cliccabile degli attributi analizzati
- **Una sezione per ogni attributo** con:
  - titolo + conteggio valori distinti
  - tabella ordinata per occorrenze decrescenti (colonne: valore, occorrenze, %)
  - barra di progresso visuale (CSS) per la percentuale
  - opzionalmente: mini bar chart (HTML/CSS puro o inline SVG)
- **Styling**: design pulito, tabelle zebrate, font sans-serif, responsive, stampabile
- **Palette colori** coerente (es. verde `#78b53e` / blu `#3a6fb5` per gli header, oppure palette neutra professionale)
- **Footer**: percorso dei file sorgente analizzati

### Step 5 — Comunicazione finale

Al termine, l'agent comunica:

- Percorso assoluto dei tre file generati
- Breve riepilogo a schermo (es. i 3 attributi con maggiore varianza)
- Offre di aprire l'HTML nel browser

---

## Requisiti tecnici

- HTML **self-contained**: nessun CDN, nessuna risorsa esterna, apribile offline
- CSV con separatore `,` e encoding UTF-8 con BOM (compatibilità Excel IT)
- Markdown con tabelle GitHub-flavored
- Tutti i file con stesso prefisso/timestamp per correlazione
- Path di output sempre assoluti nella risposta finale

---

## Criteri di qualità

- ✅ L'agent **deve sempre chiedere** quali attributi analizzare prima di procedere (mai assumere)
- ✅ Se il tipo non è specificato, chiederlo prima di procedere
- ✅ Produrre **tutti e tre i formati** (HTML + MD + CSV), mai solo uno
- ✅ Non inventare valori: file mancanti o tipi sconosciuti vanno segnalati chiaramente
- ✅ HTML deve essere visivamente pulito e stampabile, non un dump grezzo
- ✅ Tabelle sempre ordinate per occorrenze decrescenti
- ✅ Includere sempre percentuale oltre al conteggio assoluto

---

## Esempi di output atteso

### Esempio tabella per `tipo=3`, attributo `mixerAMixerSpeed`

**`mixerAMixerSpeed`** — 5 valori distinti su 87 ricette

| valore | occorrenze | %     |
|--------|------------|-------|
| 50     | 45         | 51.7% |
| 70     | 22         | 25.3% |
| 60     | 15         | 17.2% |
| 40     | 3          | 3.4%  |
| 80     | 2          | 2.3%  |

*(una tabella separata per ogni attributo analizzato)*
