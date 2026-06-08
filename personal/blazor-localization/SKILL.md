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

### 1. Path RESX

| Sorgente                    | RESX                                    |
| --------------------------- | --------------------------------------- |
| Pages/X/Y.razor             | Resources.Pages.X.Y.it.resx             |
| Components/Gestione/Y.razor | Resources.Components.Gestione.Y.it.resx |
| Components/X/Y.razor        | Resources.Components.X.Y.it.resx        |
| Shared/Y.razor              | Resources.Shared.Y.it.resx              |

**Path multi-livello**: ogni sottocartella diventa un segmento con punto:
```
Pages/Magazzino/Articoli/Giacenza/Giacenza.razor
→ Resources/Pages.Magazzino.Articoli.Giacenza.Giacenza.it.resx
```

### 2. Rilevamento Stringhe IT

**Cercare**: `àèéìòù`, parole IT (che, della, sono, stato)

**Pattern**: `return "..."`, `>testo<`, `Title/Text/Placeholder="..."`, `testoModale = "..."` (seguito da `alertModal?.ShowAsync(testoModale)`)

**Escludere**: `@localizer["..."]`, `@commonLabels["..."]`, URL, CSS, date format (`dd/MM/yyyy`), `"true/false/null"`, valori parametro usati in condizioni (es. `Mandante == "Pila in ingresso"` sono filtri dati, non etichette UI)

**File da saltare**: file template/esempio (es. `TemplateTab.razor`) che contengono placeholder di sviluppo, non UI reale

**Distinzione messaggi JS**:
- `JS.InvokeVoidAsync("alert", ...)` → messaggi visibili utente, **localizzare**
- `JS.InvokeVoidAsync("console.error", ...)` → log debug, **localizzare** (utile per supporto multilingua)
- `JS.InvokeVoidAsync("console.log", ...)` → log tecnici, valutare se escludere

### 3. Generazione Chiavi

IT→EN, PascalCase, max 100 char

| Prefisso | Uso       |
| -------- | --------- |
| Btn*     | Pulsanti  |
| Err*     | Errori    |
| Lbl*     | Etichette |
| Msg*     | Messaggi  |
| Title*   | Titoli    |
| Col*     | Colonne   |

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

| Contesto     | Prima         | Dopo                                     |
| ------------ | ------------- | ---------------------------------------- |
| Return       | `return "X";` | `return localizer["K"].Value;`           |
| Markup       | `>X<`         | `>@localizer["K"]<`                      |
| @code        | `"X"`         | `localizer["K"].Value`                   |
| Attributo    | `Title="X"`   | `Title="@localizer["K"]"`                |
| HTML interno | `<i>X</i>`    | `@((MarkupString)localizer["K"].Value)`  |
| Interpolata  | `$"X {v}"`    | `string.Format(localizer["K"].Value, v)` |

**Messaggi JavaScript con parametri**:
```csharp
// Prima
await JS.InvokeVoidAsync("alert", $"Errore: {ex.Message} - {ex.StackTrace}");
// Dopo (RESX: <value>Errore: {0} - {1}</value>)
await JS.InvokeVoidAsync("alert", string.Format(Localizer["ErrKey"], ex.Message, ex.StackTrace));

// Per stringhe semplici senza parametri
await JS.InvokeVoidAsync("alert", Localizer["ErrKey"].Value);
```

**CommonLabels**: `commonLabels["Key"]` invece di `localizer["Key"]`

**Stringhe ripetute nello stesso file**: quando la stessa etichetta appare più volte (es. "ID Pallet:" 2 volte), usare `replace_all=true` nell'Edit tool per sostituire tutte le occorrenze in un colpo solo, evitando errori "Found N matches".

### 7. Direttive (se mancanti)

```razor
@using Microsoft.Extensions.Localization
@using BlazorWCSWebUI.Resources
@inject IStringLocalizer<NomeClasse> localizer
@inject IStringLocalizer<CommonLabels> commonLabels
```

`NomeClasse` = nome file senza estensione

**Localizer condiviso**: alcuni componenti usano il localizer di un'altra classe (es. `DettagliMissioneL1Semplificate` usa `IStringLocalizer<DettagliMissione>`). In questo caso:
- Le chiavi vanno nel RESX della classe referenziata (es. `DettagliMissione.it.resx`)
- Se il componente non ha alcun `@inject IStringLocalizer`, aggiungere using + inject con la classe corretta
- Verificare sempre quale `IStringLocalizer<T>` è già in uso prima di aggiungere direttive

### 8. Nuovo RESX

Template: copiare `Resources/Resources.CommonLabels.it.resx`, svuotare `<data>`, aggiungere:

```xml
<data name="Key" xml:space="preserve">
  <value>Testo italiano</value>
</data>
```

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
