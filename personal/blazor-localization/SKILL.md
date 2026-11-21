---
name: blazor-localization
description: Localizza file Razor sostituendo stringhe italiane con riferimenti a risorse .resx. Use when processing Italian text in Razor components.
user-invocable: true
argument-hint: "[path-to-file-or-folder]"
model: sonnet
---

# Blazor Localizza

Localizza file Razor sostituendo stringhe italiane con riferimenti a risorse .resx.

## Uso

**Singolo file:**
```
/blazor-localization BlazorWCSWebUI/Pages/MyPage.razor
```

**Cartella intera:**
```
/blazor-localization BlazorWCSWebUI/Components/Gestione/
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
   ✓ RESX creato: Resources/Components/DialogConferma.it.resx
   ✓ Stringhe localizzate: 5
   ```
3. **Attendere revisione utente**:
   > "Controlla le modifiche. Quando pronto, conferma per passare al file successivo."
   > - [1] **Confermo, procedi** al prossimo file
   > - [2] **Stop** - interrompi qui (riprendi dopo con `/blazor-localization`)
   > - [3] **Annulla ultimo** - ripristina file e riprova

4. **Ripetere** per ogni file fino al completamento o stop utente

### Modalità "Tutti insieme"

- Processa tutti i file senza interruzioni
- Mostra riepilogo finale con tutti i file modificati

## Procedura (singolo file)

> Dettagli di lookup (path RESX, prefissi chiavi, sostituzioni Razor, direttive e template) in [references/localization-workflow.md](references/localization-workflow.md).

### 1. Path RESX

Determina il file RESX mantenendo sotto `Resources/` la stessa struttura di cartelle del file Razor. Non appiattire il path usando punti. Mapping e regole di migrazione → vedi [reference](references/localization-workflow.md#convenzione-path-resx).

### 2. Rilevamento Stringhe IT

Individua le stringhe italiane da localizzare. Pattern da cercare ed esclusioni → vedi [reference](references/localization-workflow.md#rilevamento-stringhe-it).

Includi le **chiavi fantasma** (`localizer["<testo italiano>"]`), anche nei file già localizzati → vedi [reference](references/localization-workflow.md#chiavi-fantasma).

### 3. Generazione Chiavi

IT→EN, PascalCase, max 100 char. Tabella prefissi (Btn/Err/Lbl/Msg/Title/Col) → vedi [reference](references/localization-workflow.md#generazione-chiavi).

### 4. Controllo Duplicati (ordine)

1. Valore esiste in CommonLabels → riusa `commonLabels["Key"]`
2. Valore esiste in page-specific → riusa `localizer["Key"]`
3. Chiave esiste (valore diverso) → suffisso (Key2, Key3...)
4. Nessuna corrispondenza → nuova chiave, nel RESX scelto allo STEP B

**Stringhe duplicate tra file diversi**: se la stessa stringa appare in più file (es. "Panoramica completa delle operazioni..."), segnalare all'utente:
> "Questa stringa appare in N file. Vuoi aggiungerla a CommonLabels per riuso?"

### 5. Interazione Utente

Se la richiesta autorizza già a procedere (es. «sistema tutte», «localizza le stringhe» con file indicato), salta gli STEP B e C: tutte le nuove chiavi nel RESX di pagina, riuso di CommonLabels solo per valori già presenti (punto 4), e dichiaralo nel riepilogo. Altrimenti segui gli STEP A-C.

**STEP A - Mostrare tabella stringhe trovate** (segnalare eventuali typo nelle stringhe rilevate con ⚠️ e proporre correzione nel valore RESX):

```
| # | Stringa | Chiave proposta | Riga |
|---|---------|-----------------|------|
| 1 | "Salva" | BtnSave         | 45   |
| 2 | "Errore di connessione" | ErrConnection | 78 |
```

**STEP B - Chiedere destinazione CommonLabels**:

> "Quali stringhe vuoi in **CommonLabels** (riusabili in tutto il progetto)?
> Indica i numeri separati da virgola, oppure 'nessuna'.
> Le restanti andranno nel file RESX page-specific."

Esempio risposta utente: `1,3,5` oppure `nessuna` oppure `tutte`

**STEP C - Chiedere modalità di elaborazione**:

- [1] Tutte insieme (applica tutte le sostituzioni)
- [2] Una alla volta (conferma per ogni stringa)
- [3] Seleziona gruppo (indica quali numeri processare)

### 6. Sostituzioni Razor

Applica le sostituzioni secondo il contesto (markup, attributo, @code, interpolata, HTML). Tabella contesti e uso CommonLabels → vedi [reference](references/localization-workflow.md#sostituzioni-razor).

### 7. Direttive (se mancanti)

Aggiungi `@using`/`@inject` se assenti → vedi [reference](references/localization-workflow.md#direttive-se-mancanti).

### 8. Nuovo RESX

Crea il RESX se non esiste: copiare `Resources/Resources.CommonLabels.it.resx`, svuotare i `<data>` applicativi e aggiungere le chiavi. Template → vedi [reference](references/localization-workflow.md#nuovo-resx).

### 9. Validazione (ogni file)

Lancia lo script, da rifare dopo ogni rinomina di chiavi (file o cartella):

```
powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/blazor-localization/scripts/verifica-chiavi.ps1 <file.razor|cartella>
```

Copre allineamento chiavi↔RESX in entrambe le direzioni, chiavi fantasma, voci duplicate o vuote, RESX mancante, CommonLabels e `.razor.cs`. Exit 1 = almeno un `KO` da correggere; gli `AVVISO` (voci non usate, righe con accenti) vanno valutati. Se il localizer è di un'altra classe (vedi [reference](references/localization-workflow.md#allineamento-bidirezionale)) passa `-Resx <percorso>`. Niente python: sulla macchina non c'è.

Restano a mano:
- [ ] Stringhe IT residue **senza accenti** (lo script vede solo righe con lettere accentate)
- [ ] Nessun vecchio RESX appiattito rimasto dopo una migrazione di path

### 10. Build e riepilogo (fine lavoro)

**Build una sola volta**, dopo l'ultimo file: `dotnet build BlazorWCSWebUI/BlazorWCSWebUI.csproj`. Rileva `@using`/`@inject` mancanti, sintassi Razor, RESX malformati e i `nameof` dei DTO (10-bis); non rileva le chiavi mancanti, per quelle serve l'allineamento del punto 9.
Se l'app è in esecuzione il build termina con `MSB3027`/`MSB3021` sull'exe: è il lock del processo, non un errore di compilazione. Rilancia con `-p:OutputPath=obj\tmpbuild\`, leggi lì il conteggio errori, poi cancella la cartella temporanea.

**Riepilogo**: file RESX creati/modificati, numero stringhe localizzate, eventuali warning.

### 10-bis. DTO con DataAnnotations

Se il target è un **DTO/model con DataAnnotations** (non un .razor): gli attributi built-in non supportano `IStringLocalizer` → usare il pattern `ErrorMessageResourceType` + classe ponte statica. Creare SEMPRE la coppia `Resources/[Nome]Messages.resx` (neutro, senza `.it`) + `Resources/[Nome]Messages.cs` (a mano). Dettagli e riferimento (commit `069a57b`) → [reference](references/localization-workflow.md#localizzazione-dto-dataannotations).

### 11. Progress

Se il file è tracciato in `progress/localization-components_progress.md`, aggiornalo: task completato con numero stringhe, file `.razor` localizzati e `.resx` creati (NUOVO) o modificati, path RESX corretto dopo eventuali migrazioni.

### 12. Auto-apprendimento

**Durante il processo**, annotare eventuali:
- Pattern nuovi non documentati nella skill
- Casi limite o eccezioni incontrate
- Soluzioni trovate per problemi specifici
- Suggerimenti per migliorare il workflow

**Al termine**, mostrare lista miglioramenti proposti:

```
## Suggerimenti per migliorare /blazor-localization

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
