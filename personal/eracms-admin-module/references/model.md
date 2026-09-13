# The model

`.ai/rules/models.md` carries the full rules (PHP 8 attributes, `Attribute` accessors, `casts()` as a
method, calendar dates, eager loading). Read it. Real references: `app/Models/Course.php` for a plain
module with image, relation and date window; `app/Models/Product.php` for the whole `getFieldSpec()`
vocabulary at once.

Section order: attributes → `use` → class → traits → properties → `casts()` → relations →
`getFieldSpec()`.

```php
#[UseFactory(EventFactory::class)]
#[UseEloquentBuilder(EventBuilder::class)]   // or EraCmsBuilder::class when there is no custom builder
class Event extends Model
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

The value objects live in `app/eraCms/Tools/ValueObject/Form/` — read the constructor of the one you
need. `.ai/rules/admin.md` lists the ones in active use.

## Traps

**`ImagePresenter` only resolves the `imageMedia` relation or a column named literally `image`.**
Name the column `image` if you use the trait (Team, Course, Links). If the domain wants `logo` or
`cover`, don't use the trait at all: `getImageUrl()` and `thumbnailUrl()` return `null` in silence,
with no error and no failing test — `app/Models/Company.php` is the reference for that case.
`getMediaFolder()` comes from the same trait, so without it pass the folder explicitly:
`new MediaUploadObject(folder: 'posts')`.

**Every `RelationObject` with `multiple: 1` needs a saver**, named for the field in plural camelCase:

```php
public function saveTags(array $tags): void { $this->tags()->sync($tags); }
```

**Dates.** Use the `DatePresenter` trait for `date_start` / `date_end` / `valid_from` / `valid_until`.
Other date fields get an accessor on the model or a presenter trait under
`app/eraCms/Domain/[Entity]/`.

## Translatable models

```php
use App\eraCms\Translatable\MaTranslatableHelperTrait;
use App\eraCms\Translatable\Translatable;

class Event extends Model
{
    use MaTranslatableHelperTrait;
    use Translatable;

    public array $translatedAttributes = ['title', 'description'];
}
```

Translated fields must **not** appear in `$fillable`. The migration adds a companion table:

```php
Schema::create('events_translations', function (Blueprint $table) {
    $table->id();
    $table->foreignId('event_id')->constrained('events')->cascadeOnDelete();
    $table->string('locale', 10)->index();
    // translated columns…
    $table->unique(['event_id', 'locale']);
});
```

`$with` may contain `translations` and nothing else — see `.ai/rules/models.md`.
