# Discoverability baseline — eraCms

Measured on 30/07/2026 on `app/` (772 PHP files, 688 classes, 1007 distinct public method names)
and `resources/js/` (185 files). Re-measure with `measure_discoverability.py` in this folder.

It serves two purposes: justifying the skill's three rules, and showing which rules of this kind
have **no** work to do here.

## Class names: healthy, no rule needed

| words in the name | classes | % globally unique |
|---|---|---|
| 1 | 85 | 91% |
| 2 | 242 | 93% |
| 3 | 236 | 98% |
| 4+ | 125 | 99% |
| all | 688 | 95% |

The `Domain/<Entity>/` namespaces already do the work. Of the 32 remaining duplicate names, almost
all are legitimate: `Item`/`Index` ×4 are path-bound Blade components,
`HtmlMenu`/`HtmlSocial`/`NavigationMenu` are Facade↔implementation pairs, the `*Controller` ×2-3
are the three Api/Website/Admin entry points. Genuinely ambiguous: `Features` (Tools vs
Domain/Store), `ProductResource` (Resources vs Domain/Product/Resources).

For comparison, the 700k-line monorepo where the "3 words" rule was born stood at 61% one-word
names. eraCms is two orders of magnitude smaller and the rule does not apply.

## Public methods: the curve exists, but the culprits belong to the framework

| words in the name | methods | % unique in the repo |
|---|---|---|
| 1 | 182 | 58% |
| 2 | 344 | 81% |
| 3 | 284 | 85% |
| 4+ | 197 | 91% |
| all | 1007 | 80% |

The most ambiguous names overall **cannot be renamed**: `render` ×121, `handle` ×39, `index` ×30,
`show` ×24, `boot` ×18, `register` ×16, `rules` ×15, `authorize` ×15, `toArray` ×45. A rule that
flags them produces only noise — hence the "Conventions win" section.

`getFieldSpec` ×53 shows why uniqueness alone is the wrong metric: a contract method implemented
53 times answers *one* question in 53 places, and that is fine. The defect is when different names
answer different questions and collide.

Chosen by the project and genuinely generic — the target of check 2: `execute` ×28,
`process` ×14, `calculate` ×9, `get` ×7, `product` ×6.

## Documentation: the real gap

**1093 public methods out of 1726 (63%) without PHPDoc.**

It is the biggest figure in the repo and compounds badly with the previous one: `execute()` is
ambiguous across 28 sites *and* silent, so a search lands on 28 walls of code without a line that
tells them apart. Hence check 1, the rule with the most value per unit of effort.

## Reference rules not needed here

- **Keep strings whole / prefixes in errors.** Only 3 identifier interpolations, all deliberate
  `config("eraCms.{$feature}...")`, and **zero** exceptions whose message starts with a variable.
  There is no problem to solve.
- **Branded types / newtype for IDs.** No equivalent in PHP 8.3 without introducing value objects
  across the whole domain: it is an architectural decision, not a naming rule, and should be
  discussed separately.
- **Bare role filenames** (`utils.php`, `helpers.php`, `config.php`). Zero occurrences in `app/`.
  On the frontend, 6 duplicate basenames out of 185 files, all harmless (`bootstrap.js`
  website/admin, `i18n.js` website/admin).

## Source

Inspired by modem-dev's `write-discoverable-code`
(https://github.com/modem-dev/skills/blob/main/write-discoverable-code/SKILL.md), reduced to the
rules this measurement justifies.
