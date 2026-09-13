---
name: blazor-localization
description: >
  Localizza file Razor del progetto AF sostituendo le stringhe italiane con riferimenti a risorse
  .resx, creando il RESX di pagina quando manca. Usa quando l'utente dice "Localizza
  BlazorWCSWebUI/[path]" o chiede di localizzare componenti, pagine o cartelle Razor. Non usarla
  per tradurre testo, per file non-Razor, o per altri progetti .NET.
user-invocable: true
argument-hint: "[path-to-file-or-folder]"
---

# Blazor Localizza

Sostituisce le stringhe italiane in un file `.razor` con `localizer["Key"]` / `commonLabels["Key"]`
e scrive le chiavi nel RESX corrispondente.

Tabelle di lookup — path RESX, prefissi chiave, contesti di sostituzione, direttive, template RESX —
in [references/localization-workflow.md](references/localization-workflow.md). Consultale mentre
lavori: sono la convenzione del progetto, non deducibili dal codice.

## Cartella o file singolo

Con un file, vai alla procedura. Con una cartella: elenca i `.razor` ricorsivamente con il conteggio
di stringhe IT per file, poi chiedi come procedere — uno alla volta con revisione (raccomandato),
tutti insieme, o una selezione di numeri.

In modalità "uno alla volta", dopo ogni file mostra cosa hai fatto (file RESX creato o modificato,
numero di stringhe) e fermati: l'utente conferma, interrompe, o chiede di annullare l'ultimo file.

## Procedura per file

1. **Path RESX** — deriva il nome del RESX dal path sorgente
   ([mapping](references/localization-workflow.md#mapping-path-resx)).
2. **Rileva le stringhe IT** — pattern ed esclusioni in
   [Rilevamento](references/localization-workflow.md#rilevamento-stringhe-it).
3. **Genera le chiavi** — IT→EN, PascalCase, max 100 char, prefisso per tipo
   ([tabella](references/localization-workflow.md#generazione-chiavi)).
4. **Controlla i duplicati**, in quest'ordine: valore già in CommonLabels → riusa
   `commonLabels["Key"]`; valore già nel RESX di pagina → riusa `localizer["Key"]`; chiave esistente
   con valore diverso → suffisso numerico; nessuna corrispondenza → chiedi. Se la stessa stringa
   compare in più file della cartella, segnalalo e proponi CommonLabels.
5. **Fai vedere e chiedi.** Mostra la tabella `# | Stringa | Chiave proposta | Riga`, marcando con
   ⚠️ eventuali typo nell'originale e proponendo la correzione nel valore RESX. Poi chiedi
   **sempre** quali stringhe vanno in CommonLabels (numeri, `nessuna`, `tutte`) — è il passaggio
   che non si salta — e con quale modalità applicare le sostituzioni.
6. **Sostituisci** secondo il contesto: markup, attributo, `@code`, interpolata, HTML interno,
   messaggi JS ([tabella contesti](references/localization-workflow.md#sostituzioni-razor)). Per una
   stringa ripetuta identica nello stesso file usa `replace_all`.
7. **Aggiungi le direttive** `@using`/`@inject` se mancano
   ([blocco](references/localization-workflow.md#direttive-se-mancanti)). Se il componente usa il
   localizer di un'altra classe, vale la regola del localizer condiviso descritta lì.
8. **Crea il RESX** se non esiste: copia `Resources/Resources.CommonLabels.it.resx`, svuota i
   `<data>`, aggiungi le chiavi ([template](references/localization-workflow.md#nuovo-resx)).

## Verifica

**Non lanciare `dotnet build`** — solo controllo statico:

- sintassi Razor: direttive presenti, parentesi bilanciate in `@localizer["..."]`, nessun escape errato
- RESX: XML ben formato, ogni `<data name>` ha il suo `<value>`, nessuna chiave duplicata
- `grep àèéìòù` sul file modificato: nessuna stringa IT rimasta

Poi riepiloga RESX creati o modificati e stringhe localizzate per file.

## Progress

Aggiorna sempre `progress/localization-components_progress.md` prima di considerare chiuso il task:
task marcato completato con il numero di stringhe, e **tutti** i file toccati in elenco — `.razor`
localizzati e `.resx` creati (segnalati come NUOVO) o modificati.

## Pattern nuovi

Se incontri un pattern, un'eccezione o un caso limite non coperto dal reference, segnalalo alla fine
in due righe. Se vale la pena tenerlo, l'utente chiede di aggiungerlo al reference.
