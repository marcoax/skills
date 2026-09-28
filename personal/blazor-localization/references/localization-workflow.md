# Localizzazione Razor - Workflow Completo

## Comando
`Localizza BlazorWCSWebUI/[path/file.razor]`

## 0. Target Selection

**File**: `Localizza path/file.razor` → procedi con step 1
**Folder**: `Localizza path/folder/` → elenca i `.razor` ricorsivamente, mostra selezione, itera sui file scelti

---

## Convenzione Path RESX

La struttura sotto `Resources/` deve rispecchiare la struttura del file Razor sotto la root del progetto. Si sostituisce soltanto `.razor` con `.<cultura>.resx`.

### Regola

```text
BlazorWCSWebUI/<percorso>/<Componente>.razor
→ BlazorWCSWebUI/Resources/<percorso>/<Componente>.<cultura>.resx
```

Non appiattire le directory usando punti nel nome del file.

### Mapping Path → RESX

| Percorso sorgente | File RESX |
|---|---|
| `Pages/X/Y.razor` | `Resources/Pages/X/Y.it.resx` |
| `Components/Gestione/Y.razor` | `Resources/Components/Gestione/Y.it.resx` |
| `Components/Ui/Form/Y.razor` | `Resources/Components/Ui/Form/Y.it.resx` |
| `Shared/Y.razor` | `Resources/Shared/Y.it.resx` |

Esempio:

```text
Components/Ui/Form/AggiungiArticoloModal.razor
→ Resources/Components/Ui/Form/AggiungiArticoloModal.it.resx
```

### Eccezione: RESX di validazione (DataAnnotations)

I RESX neutri usati dalle classi-ponte per i messaggi `DataAnnotations` **restano piatti** in `Resources/`, perché il nome segue la classe-ponte (che vive nel namespace `BlazorWCSWebUI.Resources`), non un componente Razor:

```
Resources/DismettiArticoloModalFormMessages.cs
Resources/DismettiArticoloModalFormMessages.resx
```

**⚠️ MAI ripetere "Resources" nel path o nel nome file**, anche se `Resources/Resources.CommonLabels.it.resx` sembra suggerirlo. `IStringLocalizer<T>` risolve il resource name dal namespace del tipo `T` (che rispecchia il percorso cartelle del `.razor`) più `ResourcesPath` (`"Resources"`, impostato in `Program.cs` con `AddLocalization`). Il segmento `Resources/` è già fornito da `ResourcesPath`: aggiungerlo di nuovo produce un nome che non verrà mai risolto e il localizer restituirà silenziosamente la chiave.

`Resources.CommonLabels.it.resx` porta il prefisso SOLO perché la classe `CommonLabels` vive davvero nel namespace `BlazorWCSWebUI.Resources` (è un tipo C# in `Resources/`, non un componente Razor) — caso speciale, non un modello da imitare.

**Verifica prima di procedere**: se il file `.razor` non ha `@namespace` esplicito né `.razor.cs` con namespace custom, il namespace è `RootNamespace + percorso cartelle` (es. `Components/Ui/Form/X.razor` → `BlazorWCSWebUI.Components.Ui.Form.X`). Il RESX va nello stesso percorso sotto `Resources/`: `Resources/Components/Ui/Form/X.it.resx`.

### Migrazione da path appiattiti

Quando una risorsa esistente viene spostata:

1. Spostare, non copiare, il `.resx` nel path speculare.
2. Eliminare il vecchio file appiattito o ibrido.
3. Verificare che non esistano due file con lo stesso nome logico di risorsa.
4. Verificare che tutte le chiavi usate dal Razor siano presenti nel file spostato.
5. Aggiornare il path nel progress.
6. Segnalare che serve arrestare l'app e fare `dotnet clean` prima del successivo avvio: uno spostamento può conservare un timestamp precedente e lasciare `.resources` incrementali obsoleti.

La skill non esegue la build, ma deve riportare esplicitamente questa istruzione nel riepilogo di una migrazione.

---

## Rilevamento Stringhe IT

**Cercare**: `à è é ì ò ù`, parole IT (che, della, sono, stato)

**Pattern**: `return "..."`, `>testo<`, `Title/Text/Placeholder="..."`

**Escludere**: `@commonLabels["..."]`, URL, CSS, date format (`dd/MM/yyyy`), `"true/false/null"`

### ⚠️ Chiavi fantasma — `localizer["<testo italiano>"]`

**Non escludere `@localizer["..."]` a scatola chiusa.** Se la chiave è *testo italiano*
(`localizer["Codice"]`, `localizer["Conferma dismissione"]`) sono due problemi in uno:

1. viola la convenzione IT→EN;
2. quasi sempre **la voce nel RESX non esiste**.

Sembra funzionare perché `IStringLocalizer` **restituisce la chiave stessa** quando la voce manca —
e per un'intestazione di colonna la chiave *è* il testo giusto. Nulla lo segnala: il compilatore non
vede le chiavi, il build passa, la pagina è corretta a schermo.

Trovarle:

```bash
grep -o 'localizer\["[^"]*"\]' File.razor | grep -E 'localizer\["[^"]*(à|è|é|ì|ò|ù| )'
```

Euristica: chiave con **spazi** o **accenti** → è testo, non una chiave. Rinominare secondo i prefissi
e aggiungere la voce al RESX.

Caso reale: `DismettiArticolo.razor` ne aveva **11** (`Codice`, `Descrizione1`, `Componente`,
`Conferma dismissione`, `BtnEditPopup`…), sopravvissute a una localizzazione precedente.

---

## Generazione Chiavi

IT→EN, PascalCase, max 100 char

| Prefisso | Uso |
|----------|-----|
| Btn* | Pulsanti |
| Err* | Errori |
| Lbl* | Etichette |
| Msg* | Messaggi |
| Title* | Titoli |
| Col* | Colonne |

---

## Controllo Duplicati (ordine)

1. Valore esiste in CommonLabels → riusa `commonLabels["Key"]`
2. Valore esiste in page-specific → riusa `localizer["Key"]`
3. Chiave esiste (valore diverso) → suffisso (Key2, Key3...)
4. Nessuna corrispondenza → chiedi utente

---

## Interazione Utente

**Mostrare tabella**:
```
| # | Stringa | Chiave | Riga |
```

**Chiedere modalità**:
- [1] Tutte insieme
- [2] Una alla volta
- [3] Seleziona gruppo

**Per ogni stringa**:
- [1] CommonLabels
- [2] Page-specific
- [3] Skip

---

## Sostituzioni Razor

| Contesto | Prima | Dopo |
|----------|-------|------|
| Return | `return "X";` | `return localizer["K"].Value;` |
| Markup | `>X<` | `>@localizer["K"]<` |
| @code | `"X"` | `localizer["K"].Value` |
| Attributo | `Title="X"` | `Title="@localizer["K"]"` |
| HTML interno | `<i>X</i>` | `@((MarkupString)localizer["K"].Value)` |
| Interpolata | `$"X {v}"` | `string.Format(localizer["K"].Value, v)` |

**CommonLabels**: `commonLabels["Key"]` invece di `localizer["Key"]`

---

## Direttive (se mancanti)

```razor
@using Microsoft.Extensions.Localization
@using BlazorWCSWebUI.Resources
@inject IStringLocalizer<NomeClasse> localizer
@inject IStringLocalizer<CommonLabels> commonLabels
```

`NomeClasse` = nome file senza estensione

---

## Nuovo RESX

Template: copiare `Resources/Resources.CommonLabels.it.resx`, svuotare `<data>`, aggiungere:

```xml
<data name="Key" xml:space="preserve">
  <value>Testo italiano</value>
</data>
```

---

## Validazione

- [ ] Sintassi razor/XML corretta
- [ ] Tutte stringhe sostituite
- [ ] @using/@inject presenti
- [ ] No stringhe IT rimaste (`grep à è é ì ò ù`)
- [ ] Nessuna chiave fantasma: nessun `localizer["..."]` con spazi o accenti
- [ ] **Allineamento chiavi↔RESX in entrambe le direzioni** (vedi sotto)
- [ ] Nessun RESX appiattito/ibrido duplicato dopo una migrazione
- [ ] Path riportato correttamente in `progress/localization-components_progress.md`

### Allineamento bidirezionale

Non basta «ogni chiave esiste nel RESX». Servono **due** confronti, per due difetti diversi:

| Direzione | Difetto | Effetto |
|---|---|---|
| usata → RESX | chiave senza voce | a runtime esce **la chiave** al posto del testo |
| RESX → usata | voce senza chiave | chiave morta, residuo di rinomine o copia-incolla |

```bash
R=Resources/Components/<path>/<Nome>.it.resx
Z=<path>/<Nome>.razor

grep -o 'data name="[^"]*"' "$R" | sed 's/data name="//;s/"//' \
  | grep -v 'Name1\|Color1\|Bitmap1\|Icon1' | sort > /tmp/resx.txt
grep -o 'localizer\["[^"]*"\]' "$Z" | sed 's/localizer\["//;s/"\]//' | sort -u > /tmp/used.txt

echo "usate senza voce:"; comm -13 /tmp/resx.txt /tmp/used.txt
echo "voci non usate:";   comm -23 /tmp/resx.txt /tmp/used.txt
```

Entrambe le liste vuote = allineato. Da rifare **dopo ogni rinomina di chiavi**: è lì che si creano
gli orfani.

⚠️ Vale anche per le **classi-ponte** dei messaggi di validazione
(`Resources/XxxMessages.cs` ↔ `XxxMessages.resx`): il `!` di `Rm.GetString(nameof(X))!` nasconde la
voce mancante al compilatore, e a runtime il messaggio di errore esce **vuoto**.

---

## Localizzazione DTO (DataAnnotations)

**Riferimento funzionante: commit `9152178` "localizza dto"** (ArticoloCreateDto + ArticoloCreateMessages.resx/.cs + RequiredIfAttribute).

Gli `ErrorMessage` degli attributi built-in (`[Required]`, `[StringLength]`, `[Range]`) devono essere costanti compile-time → `IStringLocalizer` NON è utilizzabile. Il pattern è `ErrorMessageResourceType` + classe ponte statica.

**Per ogni nuovo DTO da localizzare creare SEMPRE la coppia:**

1. `Resources/[Nome]Messages.resx` — **neutro, SENZA suffisso `.it`** (senza risorsa neutra `ResourceManager.GetString` lancia `MissingManifestResourceException` per culture ≠ it). Nessuna voce nel csproj: nei progetti SDK il .resx è `EmbeddedResource` automatico. Niente Designer/codegen (`PublicResXFileCodeGenerator` gira solo in VS, non con `dotnet build`).

2. `Resources/[Nome]Messages.cs` — classe ponte scritta a mano, minimale: una proprietà `static string` per OGNI chiave del RESX (è il punto di aggancio via reflection: se manca, `InvalidOperationException` a runtime):

```csharp
public static class ArticoloCreateMessages
{
    private static readonly ResourceManager Rm = new(
        "BlazorWCSWebUI.Resources.ArticoloCreateMessages",
        typeof(ArticoloCreateMessages).Assembly);

    public static string ErrCodeRequired => Rm.GetString(nameof(ErrCodeRequired))!;
}
```

3. **Nel DTO**, per ogni attributo:

```csharp
[Required(
    ErrorMessageResourceType = typeof(ArticoloCreateMessages),
    ErrorMessageResourceName = nameof(ArticoloCreateMessages.ErrCodeRequired))]
```

**Regole:**
- Chiavi in inglese, PascalCase, prefisso `Err` (stessa convenzione della sezione Generazione Chiavi)
- Usare sempre `nameof(...)` per il resource name → errori di battitura rilevati a compile-time
- Placeholder `{0}` (nome campo) e `{1}`/`{2}` (parametri attributo, es. max di StringLength) vengono formattati da `FormatErrorMessage` → preferire `"Il codice non può superare {1} caratteri"` a valori duplicati nel testo
- **Attributi custom** (`ValidationAttribute`): costruire il messaggio con `FormatErrorMessage(validationContext.DisplayName)`, MAI leggendo `ErrorMessage` direttamente — altrimenti la coppia resource viene ignorata (fix fatto in `RequiredIfAttribute`)
- Verifica: harness console con `Validator.TryValidateObject` su DTO vuoto/invalido
