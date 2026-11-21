# The section config

Lives in `config/eraCms/admin/list.php` under `'section'`. `.ai/rules/admin.md` has the rules; read
the `products` section for a full example (searchable, exportable, joins, roles) and `faqs` or `tags`
for a small modal-based one.

```php
'events' => [
    'model' => 'Event',
    'title' => 'Eventi',
    'icon'  => 'calendar',        // Font Awesome 5, without the fa- prefix
    'section'      => 'cms',      // optional sidebar grouping key
    'sectionTitle' => 'Cms',      // optional sidebar group label
    'roles' => ['su', 'admin'],

    'field' => [
        'id',
        'title' => ['type' => 'text',     'field' => 'title',     'orderable' => true],
        'pub'   => ['type' => 'boolean',  'field' => 'is_active', 'editable' => true, 'orderable' => true],
        'sort'  => ['type' => 'editable', 'field' => 'sort',      'orderable' => true, 'class' => 'col-1'],
    ],

    'field_searchable' => [
        'title' => ['type' => 'text', 'label' => 'title', 'field' => 'title'],
    ],

    'orderBy'   => 'sort',
    'orderType' => 'ASC',

    'actions' => [
        'edit' => 1, 'create' => 1, 'delete' => 1,
        'copy' => 0, 'export' => 0, 'selectable' => 0, 'preview' => 0, 'view' => 0,
    ],

    'menu' => [
        'home'    => true,
        'top-bar' => ['show' => true, 'action' => ['add']],
    ],
],
```

Modal variants of the actions exist (`edit-modal`, `create-modal`, `copy-modal`) with a sibling
`'modal' => ['fullscreen' => false]`; use them for small entities edited in place, the way `faqs` and
`tags` do. A single action can carry its own role restriction instead of a flag:
`'delete' => ['roles' => ['su']]`.

`'read_only' => true` makes the server refuse every write route of the section (create, store, edit,
update, duplicate, delete, their JSON and modal shortcuts, the notification resend and
Placeholder Content items) to every role, `su` included; list,
view and export keep working. Absent means false. The `actions` flags alone are not enforced on
those routes. `ai_generations` uses it.

Add `'showMedia'`, `'showSeo'`, `'showBlock'` only when the panel is actually wanted.

**Placeholder Content is opt-in per section**, declared in the section itself in `list.php`:
`'placeholder_content' => ['roles' => ['su', 'admin'], 'fields' => ['description']]` when the user
wants the form button and the list dialog that fill the `required` text fields, plus the optional
ones named under `fields`, with filler text. A missing `roles` means no role sees it. It shows only
with the `admin:placeholder_content` Setting on; the list dialog also needs the `create` (or
`create-modal`) action. Sizes, quantities and the marker are global, in
`config/eraCms/admin/placeholder_content.php`. Ask — it is a construction-site aid, not a default.

**Text Revision is opt-in per section** too:
`'text_revision' => ['roles' => ['su', 'admin'], 'fields' => ['title', 'subtitle']]` puts the command
beside the named text fields (input, textarea or wysiwyg; a wysiwyg keeps its markup) of the form. It shows only
with the `admin:text_revision` Setting on and the provider key set; provider, model and limits are
global, in `config/eraCms/admin/text_revision.php`.

**SEO Suggestions are opt-in per section too**, declared in the section in `list.php`:
`'seo_suggestion' => ['fields' => ['title', 'description'], 'roles' => ['su', 'admin']]` for a section
whose model uses `HasSeoFields`. A missing `roles` means every role on the section. Tones, driver,
limits and the rest are global, in `config/eraCms/admin/seo_suggestion.php`.

## Traps

**A column `type` must have a case in `App\eraCms\Admin\Dictionary\ListFieldType`.** An unknown type
raises `UnknownListFieldTypeException` when the list data is built — it does not fall back to the raw
value — and `ListFieldTypeComplianceTest` goes red. Adding a type means adding the case and its branch
in `AdminListCellProjection`.

**Export is the `export` action plus a non-empty `field_exportable`.** `export_csv` is the legacy key
and must not be used. The same fields and permission govern CSV and XLSX.

```php
'field_exportable' => [
    'id'    => ['type' => 'integer', 'field' => 'id',    'label' => 'id'],
    'title' => ['type' => 'text',    'field' => 'title', 'label' => 'Title'],
],
```

**Tools menu entries** go under `menu.tool` with `show` and `order`; they reuse the section `icon`
and `roles`. Never hardcode a Tools link or repeat the role check in the Blade navbar.

**The admin list derives its own eager loading** from `withRelation` merged with fields of type
`relation` — *not* `relation_image`, which relies on automatic eager loading.

## Translatable sections

When the list must sort or search on a translated column:

```php
'withRelation'   => ['translations'],
'joinTable'      => 'events_translations',
'foreignJoinKey' => 'event_id',
'localJoinKey'   => 'id',
'whereFilter'    => 'locale="it"',
```
