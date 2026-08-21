---
name: eracms-admin-module
description: >
  Creates a new CRUD module in the eraCms admin panel following the config-driven pattern.
  Use this skill whenever you want to add a new entity manageable from the admin:
  "create admin section for X", "add module X", "new admin entity", "create CRUD admin for X",
  "add X to the admin panel", "new model for the admin", "create management for X in the admin",
  "I need to manage X from the backend". Handles migration, builder, model with getFieldSpec(),
  Italian translation, admin config, and PHPUnit tests — all in a single guided flow.
---

# eraCms Admin Module Creator

Creates a new CRUD module in the eraCms admin panel following the config-driven pattern.

Before anything else, read `.ai/rules/admin.md` (ValueObject vocabulary, list column types, section config)
and `.ai/rules/models.md` (mandatory PHP 8 attributes, `casts()`, accessors, presenters). They are the
source of truth; this skill only sequences the work.

> **Language**: always respond in the language of the user's message.

---

## Step 1: Gather Information — PLAN MODE

Collect the required information. Some may already be in the user's message — do not repeat already-answered questions.

### Required (ask if missing)

| Info | Example |
|---|---|
| Entity name (singular) | "Event" → class `Event`, table `events` |
| Fields and DB types | `title string`, `date_start date`, `is_active boolean default 1` |
| Relations | `belongsTo Category`, M2M with `Tag`, etc. |
| Roles | `['su', 'admin']` — **always ask, never assume** |
| Translatable? | yes/no — if yes: which fields are translated? |

### With defaults (show in the plan; only ask if the user seems to want customisation)

| Info | Default |
|---|---|
| Actions | `edit=1, create=1, delete=1, copy=0` |
| Edit panels | all disabled (showMedia, showSeo, showBlock = 0) |
| List order | `orderBy: sort, orderType: ASC` |
| Sidebar menu | `home=true, top-bar show=true action=[add]` |
| Template | no override (uses admin.edit / admin.view) |

If required information is missing, ask before presenting the plan.

## Step 2: Implementation Plan

Present the plan to the user using this structure:

```
## Plan — Admin Module: [EntityName]

### Files to create
- database/migrations/YYYY_MM_DD_create_[entities]_table.php
- database/factories/[Entity]Factory.php
- database/seeders/[Entity]Seeder.php
- app/eraCms/Builders/[Entity]Builder.php  (only if custom query logic is needed; otherwise use EraCmsBuilder directly)
- app/Models/[Entity].php
- tests/Feature/Admin/[Entity]AdminTest.php

### Files to modify
- config/eraCms/admin/list.php         ← adds '[entities]' section
- resources/lang/it/admin.php          ← adds models.[entities]
- db/era_install.sql                   ← adds the CREATE TABLE
- database/seeders/DatabaseSeeder.php  ← registers [Entity]Seeder

### Table schema
[name] | [type] | [nullable] | [translated]
...

### Roles: [roles]
### Translatable: yes/no [fields: ...]
### Actions: edit, create, delete, ...
```

Wait for explicit confirmation before proceeding.
**Do not create any files in plan mode.**

## ⚠️ Plan Mode Gate

After confirmation, call `ExitPlanMode` and proceed step by step.

---

## Step 3: Migration

```bash
php artisan make:migration create_[entities]_table --no-interaction
```

Edit the generated file. Key conventions:

- Use `foreignId()->constrained()` for foreign keys
- Add `->index()` on columns used frequently in WHERE/ORDER
- Omit the `down()` method entirely — project rule, see `.ai/rules/migrations.md`
- Common types: `string(255)`, `text()->nullable()`, `boolean()->default(1)`, `integer()->default(0)`, `date()->nullable()`

For **translatable** models, also add the translations table:

```php
Schema::create('[entities]_translations', function (Blueprint $table) {
    $table->id();
    $table->foreignId('[entity]_id')->constrained('[entities]')->cascadeOnDelete();
    $table->string('locale', 10)->index();
    // translated fields...
    $table->unique(['[entity]_id', 'locale']);
});
```

Run:
```bash
php artisan migrate --no-interaction
```

### Mirror the schema into `db/era_install.sql`

The schema lives in **two** files. `php artisan eracms:seed` installs a database by importing
`db/era_install.sql`; it never runs the migrations. So the migration is the schema the test suite
has, and the dump is the schema every real installation has — nothing compares the two.

Add the matching `CREATE TABLE` to `db/era_install.sql`, in the same MySQL dump style as the
surrounding tables (`DROP TABLE IF EXISTS`, the `/*!40101 ... */` guards, and the empty
`LOCK TABLES` / `UNLOCK TABLES` block). Keep it in the file's alphabetical table order.
See `.ai/rules/migrations.md`.

---

## Step 4: Factory & Seeder

Create the factory with:
```bash
php artisan make:factory [Entity]Factory --model=[Entity] --no-interaction
```

Edit the generated factory to define meaningful default values for all fillable fields.
Use `$this->faker->...` (the house form: 39 factories against 1 using `fake()`).

Then create a seeder so the module has data in development:

```bash
php artisan make:seeder [Entity]Seeder --no-interaction
```

Give `sort` a deterministic order with a `Sequence` rather than a random number, and register
the seeder in `database/seeders/DatabaseSeeder::run()`.

---

## Step 5: Builder

Create `app/eraCms/Builders/[Entity]Builder.php` **only if** the model has domain-specific query logic (semantic scopes, `active()` overrides, etc.). If not needed, skip the file and use `EraCmsBuilder` directly in the model attribute.

```php
namespace App\eraCms\Builders;

class [Entity]Builder extends EraCmsBuilder
{
    // Only override active() if the logic differs from EraCmsBuilder
    // Add domain-relevant semantic scopes
    public function findPublished(): static
    {
        return $this->active()->orderBy('sort')->orderBy('id');
    }
}
```

---

## Step 6: Model

Create `app/Models/[Entity].php`. Section order: attributes → use → class → traits → properties → casts → relations → getFieldSpec.

Mandatory rules:
- **PHP 8 Attributes**: always use `#[UseFactory]` and `#[UseEloquentBuilder]` — never override `newEloquentBuilder()`.
- **HasFactory**: always include the `HasFactory` trait.
- **Accessor/mutator**: always use the Laravel 9+ `Attribute` pattern (`fn` arrow). Never `getXxxAttribute()` / `setXxxAttribute()`.
- **Dates**: use the `DatePresenter` trait if the model has `date_start`, `date_end`, `valid_from`, `valid_until`. For other date fields, create accessors in the model or in a dedicated presenter trait under `app/eraCms/Domain/[Entity]/`.
- **casts()**: define as a method, not as a `$casts` property (project convention).
- **Image column naming**: `ImagePresenter` resolves an image from the `imageMedia` relation or from a
  column literally named `image` — nothing else. If you use the trait, name the column `image`
  (Team, Course, Links). If the domain wants another name (`logo`, `cover`), do **not** use the trait:
  `getImageUrl()` and `thumbnailUrl()` would silently return `null`, with no error and no failing test.
  Company is the reference for that case — `logo` column, no presenter. Note that `getMediaFolder()`
  comes from the same trait, so without it pass the folder explicitly: `new MediaUploadObject(folder: 'posts')`.
- **M2M**: for every `RelationObject` with `multiple: 1`, add `save{FieldPluralCamelCase}()`:
  ```php
  public function saveTags(array $tags): void { $this->tags()->sync($tags); }
  ```

### Base structure (non-translatable)

```php
namespace App\Models;

use App\eraCms\Admin\Decorators\DataTypeFactory;
use App\eraCms\Builders\[Entity]Builder;
use App\eraCms\Tools\ValueObject\Form\CheckBoxObject;
use App\eraCms\Tools\ValueObject\Form\InputObject;
// ... other ValueObjects
use Database\Factories\[Entity]Factory;
use Illuminate\Database\Eloquent\Attributes\UseEloquentBuilder;
use Illuminate\Database\Eloquent\Attributes\UseFactory;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

#[UseFactory([Entity]Factory::class)]
#[UseEloquentBuilder([Entity]Builder::class)]
class [Entity] extends Model
{
    use HasFactory;

    protected $fillable = ['title', 'is_active', 'sort'];
    protected array $fieldspec = [];

    protected function casts(): array
    {
        return ['is_active' => 'boolean'];
    }

    public function getFieldSpec(): array
    {
        return (new DataTypeFactory(fieldspec: $this->fieldspec))
            ->addId()
            ->add('title', new InputObject(required: true))
            ->add('is_active', (new CheckBoxObject)->setOptions(['default_value' => 1]))
            ->add('sort', new NumberObject)
            ->get();
    }
}
```

> If the model does not need a custom builder, use `#[UseEloquentBuilder(EraCmsBuilder::class)]` instead.

### Addition for translatable models

```php
use App\eraCms\Translatable\MaTranslatableHelperTrait;
use App\eraCms\Translatable\Translatable;

class [Entity] extends Model
{
    use MaTranslatableHelperTrait;
    use Translatable;

    public array $translatedAttributes = ['title', 'description'];
    // Translated fields must NOT be in $fillable
}
```

The full list of ValueObjects is `app/eraCms/Tools/ValueObject/Form/` — read the constructor of the one
you need for its parameters. `.ai/rules/admin.md` lists the ones in active use. For a model that shows most
of the vocabulary at once, read `app/Models/Product.php`.

---

## Step 7: Translation

Open `resources/lang/it/admin.php` and add under the `models` key, in **alphabetical order**:

```php
'[entities]' => 'Italian Label',
```

---

## Step 8: Admin Config

Add the section in `config/eraCms/admin/list.php` → `'section'`:

```php
'[entities]' => [
    'model'  => '[Entity]',
    'title'  => '[Section Title]',
    'icon'   => '[fa-icon]',   // Font Awesome 5, without the fa- prefix
    'section'      => '[group]',        // Optional: sidebar grouping key (e.g. 'cms', 'store')
    'sectionTitle' => '[Group Title]',  // Optional: sidebar group label (e.g. 'Cms', 'Store')
    'roles'  => [/* from data collected in Step 1 */],

    'field' => [
        'id',
        'title' => ['type' => 'text',    'field' => 'title',     'orderable' => true],
        'pub'   => ['type' => 'boolean', 'field' => 'is_active', 'editable' => true, 'orderable' => true],
        'sort'  => ['type' => 'editable','field' => 'sort',       'orderable' => true, 'class' => 'col-1'],
    ],

    'field_searchable' => [
        'title' => ['type' => 'text', 'label' => 'title', 'field' => 'title'],
    ],

    'orderBy'   => 'sort',
    'orderType' => 'ASC',

    'actions' => [
        'edit' => 1, 'create' => 1, 'delete' => 1, 'copy' => 0,
        'export_csv' => 0, 'selectable' => 0, 'preview' => 0,
    ],

    // Add only if export_csv action is enabled:
    // 'field_exportable' => [
    //     'id'    => ['type' => 'integer', 'field' => 'id',    'label' => 'id'],
    //     'title' => ['type' => 'text',    'field' => 'title', 'label' => 'Title'],
    // ],

    // Add only if active:
    // 'showMedia' => 1, 'showSeo' => 1, 'showBlock' => 1,

    'menu' => [
        'home'    => true,
        'top-bar' => ['show' => true, 'action' => ['add']],
    ],
],
```

For translatable models that require a join on the translations table:

```php
'withRelation'   => ['translations'],
'joinTable'      => '[entities]_translations',
'foreignJoinKey' => '[entity]_id',
'localJoinKey'   => 'id',
'whereFilter'    => 'locale="it"',
```

---

## Step 9: PHPUnit Tests

```bash
php artisan make:test Feature/Admin/[Entity]AdminTest --phpunit --no-interaction
```

Use `#[Test]` attribute (from `PHPUnit\Framework\Attributes\Test`) on every test method — do not rely on `test` prefix.

Test setUp pattern:
```php
use App\Models\AdminUser;
use App\Models\Role;
use Illuminate\Foundation\Testing\RefreshDatabase;
use PHPUnit\Framework\Attributes\Test;
use Tests\TestCase;

class [Entity]AdminTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->adminOption = $this->getAdminOptionSetUp();
        $this->adminUser = AdminUser::factory()->create();
        $role_admin = Role::factory()->create(['name' => 'admin', 'level' => 10]);
        $this->adminUser->roles()->attach($role_admin);
    }
}
```

Tests must cover:
1. List — `GET /admin/[entities]` → 200
2. Create form — `GET /admin/[entities]/create` → 200
3. Valid store — `POST /admin/[entities]` with valid data → redirect + record in DB
4. Invalid store — `POST` without required fields → validation errors
5. Edit form — `GET /admin/[entities]/{id}/edit` → 200
6. Update — `PUT /admin/[entities]/{id}` → redirect + DB updated
7. Delete — `DELETE /admin/[entities]/{id}` → record removed from DB

Use `actingAs($this->adminUser, 'admin')` for all requests.

Run:
```bash
php artisan test --compact tests/Feature/Admin/[Entity]AdminTest.php
```

If they pass, ask the user whether they want to run the full test suite with `php artisan test --compact`.

---

## Step 10: Formatting

```bash
vendor/bin/pint --dirty --format agent
```

---

## Step 11: Summary

Show a final summary with created/modified files and test results. If any tests are failing, do not mark the task as complete — help the user resolve the errors before closing.
