# Localizzazione Razor — tabelle di lookup

Convenzioni del progetto AF. La procedura sta in `SKILL.md`; qui ci sono solo i dati che servono
a eseguirla.

## Mapping path RESX

I file di risorsa stanno tutti nella directory principale `Resources/`, con il nome che ricalca il
percorso del sorgente e la lingua prima dell'estensione (`.it`, `.en`).

| Percorso sorgente | File RESX |
|---|---|
| `Pages/X/Y.razor` | `Resources/Pages.X.Y.it.resx` |
| `Components/Gestione/Y.razor` | `Resources/Components.Gestione.Y.it.resx` |
| `Components/X/Y.razor` | `Resources/Components.X.Y.it.resx` |
| `Shared/Y.razor` | `Resources/Shared.Y.it.resx` |

Per un percorso più profondo, continua a concatenare i segmenti nello stesso ordine:
`Components.WCS_WEB.DettagliList.it.resx`.

## Rilevamento stringhe IT

**Cerca**: accenti `à è é ì ò ù`; parole italiane comuni (`che`, `della`, `sono`, `stato`);
i pattern `return "..."`, `>testo<`, `Title=`/`Text=`/`Placeholder="..."`.

**Escludi**: `@localizer["..."]`, `@commonLabels["..."]`, URL, classi CSS, formati data
(`dd/MM/yyyy`), letterali `"true"` / `"false"` / `"null"`.

I messaggi destinati a JavaScript seguono le stesse regole ma si sostituiscono nel contesto `@code`.

## Generazione chiavi

IT→EN, PascalCase, massimo 100 caratteri, prefisso per tipo:

| Prefisso | Uso |
|---|---|
| `Btn*` | Pulsanti |
| `Err*` | Errori |
| `Lbl*` | Etichette |
| `Msg*` | Messaggi |
| `Title*` | Titoli |
| `Col*` | Colonne di tabella |

## Sostituzioni Razor

| Contesto | Prima | Dopo |
|---|---|---|
| Return | `return "X";` | `return localizer["K"].Value;` |
| Markup | `>X<` | `>@localizer["K"]<` |
| `@code` | `"X"` | `localizer["K"].Value` |
| Attributo | `Title="X"` | `Title="@localizer["K"]"` |
| HTML interno | `<i>X</i>` | `@((MarkupString)localizer["K"].Value)` |
| Interpolata | `$"X {v}"` | `string.Format(localizer["K"].Value, v)` |

Per una stringa che va in CommonLabels, `commonLabels["Key"]` al posto di `localizer["Key"]`.

## Direttive (se mancanti)

```razor
@using Microsoft.Extensions.Localization
@using BlazorWCSWebUI.Resources
@inject IStringLocalizer<NomeClasse> localizer
@inject IStringLocalizer<CommonLabels> commonLabels
```

`NomeClasse` è il nome del file senza estensione. Un componente che deve condividere il localizer
di un'altra classe inietta quella classe al posto della propria: in quel caso le chiavi finiscono
nel RESX della classe iniettata, non in uno nuovo.

## Nuovo RESX

Copia `Resources/Resources.CommonLabels.it.resx`, svuota i nodi `<data>` e aggiungi:

```xml
<data name="Key" xml:space="preserve">
  <value>Testo italiano</value>
</data>
```
