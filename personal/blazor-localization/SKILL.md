---
name: blazor-localization
description: Automate localization workflow for Blazor Razor files in the AF project. Use when the user requests localization with commands like "Localizza BlazorWCSWebUI/[path]" or asks to localize Razor components, pages, or folders. Handles Italian string detection, RESX key generation with specific prefixes (Btn*, Lbl*, Err*, etc.), duplicate checking in CommonLabels, Razor code substitution patterns, and RESX file creation following project naming conventions.
---

# Blazor Localization

Automate the localization workflow for Blazor Razor files in the AF project, including string detection, key generation, duplicate checking, and RESX file management.

## Workflow Overview

When the user requests localization with a command like `Localizza BlazorWCSWebUI/[path]`:

1. **Read the complete workflow** from `references/localization-workflow.md` before starting
2. **Determine target scope**: Single file or folder with multiple files
3. **Follow the step-by-step process** documented in the workflow reference

## Key Capabilities

### String Detection
Detect Italian strings in Razor files using patterns:
- Accented characters: `à è é ì ò ù`
- Italian words: che, della, sono, stato
- Contexts: `return "..."`, `>testo<`, `Title/Text/Placeholder="..."`
- Exclude: already localized strings, URLs, CSS, date formats, boolean values

### Key Generation
Generate RESX keys following conventions:
- Translate Italian → English
- PascalCase format
- Maximum 100 characters
- Use prefixes: Btn*, Err*, Lbl*, Msg*, Title*, Col*

### Duplicate Management
Check for duplicates in this order:
1. Value exists in CommonLabels → reuse with `commonLabels["Key"]`
2. Value exists in page-specific RESX → reuse with `localizer["Key"]`
3. Key exists with different value → add suffix (Key2, Key3...)
4. No match → ask user for decision

### RESX File Naming
Follow project conventions for Resources folder:
- **Pages**: `Pages.[PageName].it.resx`
- **Components**: `[Namespace].[Subfolder].[ComponentName].it.resx`
- **Shared**: `Shared.[ComponentName].it.resx`

### Razor Substitutions
Apply context-specific replacements:
- Return statements: `return localizer["K"].Value;`
- Markup: `>@localizer["K"]<`
- Attributes: `Title="@localizer["K"]"`
- HTML content: `@((MarkupString)localizer["K"].Value)`
- String interpolation: `string.Format(localizer["K"].Value, v)`

## User Interaction Pattern

Present detected strings in a table format:
```
| # | Stringa | Chiave | Riga |
```

Ask user to choose mode:
- [1] Process all strings together
- [2] Process one at a time
- [3] Select specific group

For each string, ask:
- [1] Add to CommonLabels
- [2] Add to page-specific RESX
- [3] Skip this string

## Required Directives

Ensure these directives are present in Razor files:
```razor
@using Microsoft.Extensions.Localization
@using BlazorWCSWebUI.Resources
@inject IStringLocalizer<ClassName> localizer
@inject IStringLocalizer<CommonLabels> commonLabels
```

Where `ClassName` = file name without extension.

## Validation Checklist

Before completing:
- [ ] Razor/XML syntax is correct
- [ ] All strings are substituted
- [ ] Required @using/@inject directives present
- [ ] No Italian strings remain (check for à è é ì ò ù)

## Progress File (MANDATORY)

**Every localization task MUST create/update a progress file** at `BlazorWCSWebUI/progress/localization-progress.md`.

### File Structure
```markdown
# Localization Progress

## Summary
- **Total files processed**: X
- **Total strings localized**: Y
- **Last updated**: YYYY-MM-DD HH:MM

## Processed Files

| File | Strings | Status | Date |
|------|---------|--------|------|
| Components/X/Y.razor | 12 | ✅ Complete | 2025-01-21 |
| Pages/Z.razor | 5 | ✅ Complete | 2025-01-21 |

## Pending Files
- [ ] Components/A/B.razor
- [ ] Pages/C.razor
```

### Update Rules
1. Create `progress/` folder if missing
2. Create file if not exists, otherwise append/update
3. Update summary counts after each task
4. Add processed file to table with string count and timestamp
5. Move files from Pending to Processed when complete

## Complete Workflow Reference

For detailed step-by-step instructions, substitution patterns, RESX templates, and all workflow details, see `references/localization-workflow.md`.
