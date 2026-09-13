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

Add `'showMedia'`, `'showSeo'`, `'showBlock'` only when the panel is actually wanted.

## Traps

**A column `type` must have a case in `App\eraCms\Admin\Dictionary\ListFieldType`.** An unknown type
raises `UnknownListFieldTypeException` at render time — it does not fall back to the raw value — and
`ListFieldTypeComplianceTest` goes red. Adding a type means adding the case and pointing
`component()` at its `AdminList*Component`; never build a component class name from the config string.

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
