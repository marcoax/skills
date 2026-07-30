# Baseline di discoverability — eraCms

Misura del 30/07/2026 su `app/` (772 file PHP, 688 classi, 1007 nomi di metodo pubblico distinti)
e `resources/js/` (185 file). Rimisurabile con `measure_discoverability.py` in questa cartella.

Serve a due cose: giustificare le tre regole della skill, e mostrare quali regole del genere
**non** hanno lavoro da fare qui.

## Nomi di classe: sani, nessuna regola necessaria

| parole nel nome | classi | % globalmente unico |
|---|---|---|
| 1 | 85 | 91% |
| 2 | 242 | 93% |
| 3 | 236 | 98% |
| 4+ | 125 | 99% |
| tutte | 688 | 95% |

I namespace `Domain/<Entity>/` fanno già il lavoro. Dei 32 nomi duplicati che restano, quasi tutti
sono legittimi: `Item`/`Index` ×4 sono Blade component vincolati dal path,
`HtmlMenu`/`HtmlSocial`/`NavigationMenu` sono coppie Facade↔implementazione, i `*Controller` ×2-3
sono i tre ingressi Api/Website/Admin. Genuinamente ambigui: `Features` (Tools vs Domain/Store),
`ProductResource` (Resources vs Domain/Product/Resources), `HtmlHelper.class.php`.

Per confronto, il monorepo da 700k righe su cui è nata la regola "3 parole" stava al 61% a una
parola. eraCms è due ordini di grandezza più piccolo e la regola non si applica.

## Metodi pubblici: la curva esiste, ma i colpevoli sono del framework

| parole nel nome | metodi | % unico nel repo |
|---|---|---|
| 1 | 182 | 58% |
| 2 | 344 | 81% |
| 3 | 284 | 85% |
| 4+ | 197 | 91% |
| tutti | 1007 | 80% |

I nomi più ambigui in assoluto sono **non rinominabili**: `render` ×121, `handle` ×39, `index` ×30,
`show` ×24, `boot` ×18, `register` ×16, `rules` ×15, `authorize` ×15, `toArray` ×45. Una regola che
li segnala produce solo rumore — da cui la sezione "le convenzioni vincono".

`getFieldSpec` ×53 mostra perché l'unicità da sola è la metrica sbagliata: un metodo di contratto
implementato 53 volte risponde *una* domanda in 53 posti, e va bene. Il difetto è quando nomi
diversi rispondono a domande diverse e collidono.

Scelti dal progetto e genuinamente generici — il bersaglio del controllo 2: `execute` ×28,
`process` ×14, `calculate` ×9, `get` ×7, `product` ×6.

## Documentazione: il buco vero

**1093 metodi pubblici su 1726 (63%) senza PHPDoc.**

È il dato più grosso del repo e si compone male col precedente: `execute()` è ambiguo su 28 siti
*e* muto, quindi una ricerca atterra su 28 pareti di codice senza una riga che distingua. Da qui il
controllo 1, che è la regola con più valore per unità di sforzo.

## Regole del reference che qui non servono

- **Keep strings whole / prefissi negli errori.** 3 sole interpolazioni di identificatori, tutte
  `config("eraCms.{$feature}...")` deliberate, e **zero** exception con messaggio che inizia per
  variabile. Non c'è problema da risolvere.
- **Branded types / newtype per gli ID.** Non ha equivalente in PHP 8.3 senza introdurre value
  object in tutto il dominio: è una decisione architetturale, non una regola di naming, e va
  discussa a parte.
- **Filename di ruolo nudo** (`utils.php`, `helpers.php`, `config.php`). Zero occorrenze in `app/`.
  Sul frontend 6 basename duplicati su 185 file, tutti innocui (`bootstrap.js` website/admin,
  `i18n.js` website/admin).

## Fonte

Ispirata a `write-discoverable-code` di modem-dev
(https://github.com/modem-dev/skills/blob/main/write-discoverable-code/SKILL.md), ridotta alle
regole che questa misura giustifica.
