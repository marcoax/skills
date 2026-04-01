# Localizzazione Razor - Workflow Completo

## Comando
`Localizza BlazorWCSWebUI/[path/file.razor]`

## 0. Target Selection

**File**: `Localizza path/file.razor` → procedi con step 1
**Folder**: `Localizza path/folder/` → elenca .razor (no subfolders), checkbox selezione, itera su selezionati

---

## Convenzione di Naming per File RESX

Quando si crea una risorsa di localizzazione nella cartella **Resources**, il file deve essere posizionato nella directory principale seguendo questa convenzione di naming:

### Per pagine
```
Pages.[NomePagina].it.resx
```
**Esempio:** `Pages.Dashboard.it.resx`

### Per componenti
```
[Namespace].[Sottocartella].[NomeComponente].it.resx
```
**Esempio:** `Components.WCS_WEB.DettagliList.it.resx`

### Regole generali
- La lingua viene indicata prima dell'estensione `.resx` (es. `.it` per italiano, `.en` per inglese)
- Il nome deve corrispondere al namespace e al percorso del file
- Mantenere la struttura gerarchica nel naming per facilitare l'identificazione della risorsa

### Mapping Path → RESX (riferimento rapido)

| Percorso Sorgente | File RESX |
|----------|------|
| Pages/X/Y.razor | Resources/Pages.X.Y.it.resx |
| Components/Gestione/Y.razor | Resources/Components.Gestione.Y.it.resx |
| Components/X/Y.razor | Resources/Components.X.Y.it.resx |
| Shared/Y.razor | Resources/Shared.Y.it.resx |

---

## Rilevamento Stringhe IT

**Cercare**: `à è é ì ò ù`, parole IT (che, della, sono, stato)

**Pattern**: `return "..."`, `>testo<`, `Title/Text/Placeholder="..."`

**Escludere**: `@localizer["..."]`, `@commonLabels["..."]`, URL, CSS, date format (`dd/MM/yyyy`), `"true/false/null"`

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
