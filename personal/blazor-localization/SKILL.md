---
name: blazor-localization
description: Localizza file Razor sostituendo stringhe italiane con riferimenti a risorse .resx. Use when processing Italian text in Razor components.
user-invocable: true
argument-hint: "[path-to-file-or-folder]"
---

# Blazor Localizza

Localizza file Razor sostituendo stringhe italiane con riferimenti a risorse .resx.

## ⚠️ Controllo Modello

**Modello consigliato: Sonnet**

Prima di iniziare, verificare il modello in uso. Se NON è Sonnet, mostrare:

> "⚠️ **Attenzione**: stai usando il modello [NOME_MODELLO].
> Per questa skill è consigliato **Sonnet** (miglior rapporto qualità/costo per task di localizzazione).
>
> - Haiku: rischio errori sintassi XML/Razor
> - Opus: funziona ma costo eccessivo per task ripetitivo
>
> Vuoi continuare?"
> - [1] **Continua** con modello attuale
> - [2] **Interrompi** - cambierò modello a Sonnet

## Uso

**Singolo file:**
```
/blazor-localizza BlazorWCSWebUI/Pages/MyPage.razor
```

**Cartella intera:**
```
/blazor-localizza BlazorWCSWebUI/Components/Gestione/
```

## Modalità Cartella

Quando il path è una cartella:

1. **Elencare** tutti i file `.razor` nella cartella (ricorsivo)
2. **Mostrare riepilogo**:
   ```
   | # | File                    | Stringhe IT |
   |---|-------------------------|-------------|
   | 1 | DialogConferma.razor    | 5           |
   | 2 | TabellaOrdini.razor     | 12          |
   ```
3. **Chiedere modalità**:
   - [1] **Uno alla volta con revisione** (Raccomandato) - processa un file, attendi conferma utente, poi il successivo
   - [2] **Tutti insieme** - processa tutti i file senza interruzioni
   - [3] **Seleziona file** - indica numeri: `1,3,5`

### Modalità "Uno alla volta con revisione"

Per ogni file nella lista:

1. **Processare** il file (sezioni 1-9)
2. **Mostrare riepilogo file**:
   ```
   ✓ File: DialogConferma.razor
   ✓ RESX creato: Resources.Components.DialogConferma.it.resx
   ✓ Stringhe localizzate: 5
   ```
3. **Attendere revisione utente**:
   > "Controlla le modifiche. Quando pronto, conferma per passare al file successivo."
   > - [1] **Confermo, procedi** al prossimo file
   > - [2] **Stop** - interrompi qui (riprendi dopo con `/blazor-localizza`)
   > - [3] **Annulla ultimo** - ripristina file e riprova

4. **Ripetere** per ogni file fino al completamento o stop utente

### Modalità "Tutti insieme"

- Processa tutti i file senza interruzioni
- Mostra riepilogo finale con tutti i file modificati

## Procedura (singolo file)

> Dettagli di lookup (tabelle path RESX, prefissi chiavi, sostituzioni Razor, direttive, template RESX) in [references/localization-details.md](references/localization-details.md).

### 1. Path RESX

Determina il file RESX dal path sorgente. Mapping e regola path multi-livello → vedi [reference](references/localization-details.md#path-resx).

### 2. Rilevamento Stringhe IT

Individua le stringhe italiane da localizzare. Pattern da cercare, esclusioni, file da saltare e distinzione messaggi JS → vedi [reference](references/localization-details.md#rilevamento-stringhe-it).

### 3. Generazione Chiavi

IT→EN, PascalCase, max 100 char. Tabella prefissi (Btn/Err/Lbl/Msg/Title/Col) → vedi [reference](references/localization-details.md#generazione-chiavi).

### 4. Controllo Duplicati (ordine)

1. Valore esiste in CommonLabels → riusa `commonLabels["Key"]`
2. Valore esiste in page-specific → riusa `localizer["Key"]`
3. Chiave esiste (valore diverso) → suffisso (Key2, Key3...)
4. Nessuna corrispondenza → chiedi utente

**Stringhe duplicate tra file diversi**: se la stessa stringa appare in più file (es. "Panoramica completa delle operazioni..."), segnalare all'utente:
> "Questa stringa appare in N file. Vuoi aggiungerla a CommonLabels per riuso?"

### 5. Interazione Utente

**STEP A - Mostrare tabella stringhe trovate** (segnalare eventuali typo nelle stringhe rilevate con ⚠️ e proporre correzione nel valore RESX):

```
| # | Stringa | Chiave proposta | Riga |
|---|---------|-----------------|------|
| 1 | "Salva" | BtnSave         | 45   |
| 2 | "Errore di connessione" | ErrConnection | 78 |
```

**STEP B - OBBLIGATORIO: Chiedere destinazione CommonLabels**:

> "Quali stringhe vuoi in **CommonLabels** (riusabili in tutto il progetto)?
> Indica i numeri separati da virgola, oppure 'nessuna'.
> Le restanti andranno nel file RESX page-specific."

Esempio risposta utente: `1,3,5` oppure `nessuna` oppure `tutte`

**STEP C - Chiedere modalità di elaborazione**:

- [1] Tutte insieme (applica tutte le sostituzioni)
- [2] Una alla volta (conferma per ogni stringa)
- [3] Seleziona gruppo (indica quali numeri processare)

### 6. Sostituzioni Razor

Applica le sostituzioni secondo il contesto (markup, attributo, @code, interpolata, HTML, messaggi JS). Tabella contesti, esempi JS con parametri, uso CommonLabels e nota `replace_all` per stringhe ripetute → vedi [reference](references/localization-details.md#sostituzioni-razor).

### 7. Direttive (se mancanti)

Aggiungi `@using`/`@inject` se assenti. Blocco direttive e regola del localizer condiviso (componente che usa il localizer di un'altra classe) → vedi [reference](references/localization-details.md#direttive-se-mancanti).

### 8. Nuovo RESX

Crea il RESX se non esiste: copiare `Resources/Resources.CommonLabels.it.resx`, svuotare `<data>`, aggiungere le chiavi. Template → vedi [reference](references/localization-details.md#nuovo-resx).

### 9. Validazione

- [ ] Sintassi razor/XML corretta
- [ ] Tutte stringhe sostituite
- [ ] @using/@inject presenti
- [ ] No stringhe IT rimaste (`grep àèéìòù`)

### 10. Verifica Codice

**NON eseguire `dotnet build`** - solo controllo correttezza codice:

1. **Verificare sintassi Razor**:
   - Direttive `@using`/`@inject` presenti e corrette
   - Parentesi bilanciate in `@Localizer["..."]`
   - Nessun carattere escapato errato

2. **Verificare RESX**:
   - XML ben formato
   - Tutti i `<data name="...">` hanno `<value>`
   - Nessuna chiave duplicata

3. **Controllo stringhe IT rimaste**:
   - Grep per `àèéìòù` nel file modificato
   - Segnalare eventuali stringhe non sostituite

4. **Riepilogo finale**:
   - File RESX creati/modificati
   - Numero stringhe localizzate
   - Eventuali warning

### 11. Aggiornamento Progress

**⚠️ OBBLIGATORIO** - Aggiornare SEMPRE `progress/localization-components_progress.md`:

1. **Marcare task come completato** nella tabella con numero stringhe
2. **Aggiungere TUTTI i file** modificati/creati alla lista:
   - File `.razor` localizzati
   - File `.resx` creati (indicare NUOVO) o modificati
3. **Indicare numero stringhe** localizzate per ogni file

**NON considerare il task completato finché il file progress non è aggiornato.**

### 12. Auto-apprendimento

**Durante il processo**, annotare eventuali:
- Pattern nuovi non documentati nella skill
- Casi limite o eccezioni incontrate
- Soluzioni trovate per problemi specifici
- Suggerimenti per migliorare il workflow

**Al termine**, mostrare lista miglioramenti proposti:

```
## Suggerimenti per migliorare /blazor-localizza

| # | Tipo | Descrizione |
|---|------|-------------|
| 1 | Pattern | Nuovo pattern per X trovato in Y.razor |
| 2 | Eccezione | Caso speciale per stringhe con HTML embedded |
| 3 | Workflow | Proposta: aggiungere controllo Z |
```

> "Vuoi aggiungere questi miglioramenti alla skill?"
> - [1] **Sì, tutti** - aggiorna SKILL.md con tutti i punti
> - [2] **Seleziona** - indica numeri: `1,3`
> - [3] **No** - ignora suggerimenti

**Obiettivo**: la skill migliora progressivamente con l'uso reale.
