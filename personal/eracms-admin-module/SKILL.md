---
name: eracms-admin-module
description: >
  Scaffolds a new CRUD module in the eraCms admin panel — migration, model with getFieldSpec(),
  section config, Italian label and tests. Use when an entity has to become manageable from the
  eraCms backend: "create admin section for X", "add module X", "new admin entity", "I need to
  manage X from the backend". Not for changing an existing section's fields, and not for admin
  work outside eraCms.
---

# eraCms Admin Module

Source of truth is the project's own rules — read `.ai/rules/admin.md`, `.ai/rules/models.md` and
`.ai/rules/migrations.md` before writing anything. This skill only sequences the work and records
the traps those files don't cover.

Answer in the language of the user's message.

## 1. Scope — plan mode

Ask only for what the message doesn't already say:

- entity name (singular) and its fields with DB types
- relations (`belongsTo Category`, M2M with `Tag`, …)
- **roles** — always ask, never assume
- translatable? if yes, which fields

These have defaults: state them in the plan instead of asking, unless the user wants to tune them.

| | Default |
|---|---|
| Actions | `edit`, `create`, `delete` on; `copy`, `export`, `selectable`, `preview` off |
| Edit panels | `showMedia`, `showSeo`, `showBlock` off |
| List order | `orderBy: sort`, `orderType: ASC` |
| Sidebar | `home: true`, top-bar `show: true`, `action: ['add']` |
| Template | none (uses `admin.edit` / `admin.view`) |

Present a plan with the files to create and modify, the table schema, roles, translatable fields
and actions. Create no files in plan mode. Wait for explicit confirmation, then call `ExitPlanMode`.

## 2. Build

| What | Where | Read |
|---|---|---|
| Migration **and** the matching `CREATE TABLE` in `db/era_install.sql` | `database/migrations/` | `.ai/rules/migrations.md` — both files, always; no `down()` |
| Factory | `database/factories/[Entity]Factory.php` | house form is `$this->faker` (38 factories against 1 using `fake()`) |
| Builder — only for domain query logic | `app/eraCms/Builders/[Entity]Builder.php` | otherwise point the attribute at `EraCmsBuilder` |
| Model | `app/Models/[Entity].php` | [references/model.md](references/model.md) |
| Section config | `config/eraCms/admin/list.php` | [references/admin-config.md](references/admin-config.md) |
| Italian label | `resources/lang/it/admin.php` → `models.[entities]`, alphabetical | |
| Tests | `tests/Feature/Admin/[Entity]AdminTest.php` | copy the shape of `tests/Feature/Admin/CourseAdminTest.php` |

A seeder only when the user asks for one — the project has two, it is not the house pattern.

Cover list, create form, store (valid and invalid), edit form, update and delete, unless
`.ai/rules/tests.md` argues a case isn't worth it. Route by name (`admin_list`, `admin_create`, …),
not by URL literal.

## 3. Close

```bash
php artisan test --compact tests/Feature/Admin/[Entity]AdminTest.php
vendor/bin/pint --dirty --format agent
```

Summarise files created and modified plus test results. Offer the full suite. Do not call the task
done while a test is red — fix it with the user first.
