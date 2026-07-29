---
name: discoverable-code-check
description: >
  Checkpoint di discoverability sul codice appena scritto: verifica che ogni simbolo nuovo sia
  raggiungibile con una sola ricerca testuale. Si invoca a mano a implementazione finita, prima
  della code review. Non usarla mentre scrivi il codice, e non usarla come review di correttezza,
  performance o sicurezza — per quelle ci sono code-review, optimistic-code-review e
  security-review.
---

# Discoverability check

Un agente trova il codice cercando stringhe e leggendo la finestra attorno al match: niente hover,
niente jump-to-definition, niente memoria tra sessioni. Ogni identificatore è una query, e ogni
ricerca che manca il bersaglio costa letture sprecate. Questo controllo verifica che il codice
appena scritto risponda in una ricerca sola.

## Le convenzioni vincono

Le convenzioni di Laravel e quelle del progetto hanno la precedenza su ogni rilievo di questa
skill. Quando un nome è imposto, **il nome resta e si documenta**:

- hook del framework — `render`, `handle`, `boot`, `register`, `index`, `show`, `store`, `rules`,
  `authorize`, `toArray`, `toMail`, `via`
- classi risolte dal path — Blade component (`Website/News/Index.php` ↔ `<x-website.news.index>`),
  controller paralleli Api/Website/Admin, migration, Facade accanto alla loro implementazione
- metodi di contratto implementati da molte classi — `getFieldSpec`, i builder, i cast

Non proporre mai una rinomina che rompa la risoluzione del framework o che spezzi un pattern già
usato altrove nel repo. In dubbio guarda i sibling e allineati: una collisione di nomi coerente
con il resto del codice non è un difetto.

## Ambito

Solo il codice toccato in questo lavoro (`git diff` contro la base del branch). Il debito
preesistente non è oggetto del controllo — segnalalo solo se il codice nuovo lo peggiora, per
esempio aggiungendo il quinto `execute()` muto a un gruppo che ne aveva quattro.

## I tre controlli

**1. La doc-line dove atterra la ricerca.** Ogni metodo pubblico e ogni classe nuovi vogliono una
riga di PHPDoc con due lavori: il vincolo che la firma non può esprimere (unità di misura,
timezone, ownership, ordinamento, side effect, quale delle due date) e la frase in parole piane
che qualcuno cercherebbe. I nomi camelCase sono invisibili alle ricerche in linguaggio naturale:
`getFieldSpec` non matcha una grep per "field spec", `SessionExpiryChecker` non matcha "session
expired". La riga sopra la definizione è tutto il messaggio che arriva a chi cerca. Non è un
commento che rispiega il codice: se la firma già dice tutto e il nome è cercabile, salta.

**2. Verbi generici senza oggetto.** `execute`, `process`, `calculate`, `handle`, `get`, `run` su
codice nuovo in `Domain/`, `Tools/`, `Builders/` — dove il nome è libero — vogliono il loro
oggetto: `calculateShippingCost`, non `calculate`. Qualifica quanto serve a essere unico, poi
fermati; il resto va nella doc-line. Se il verbo nudo è imposto da un'interfaccia o da Laravel,
vale la sezione precedente: resta, e prende la doc-line.

**3. Un solo sito di definizione.** Se questo lavoro ha spostato o duplicato codice, verifica che
sia sparito dall'origine nello stesso commit. Un helper copiato in due posti fa atterrare ogni
ricerca futura su entrambi, e uno dei due invecchia in silenzio. Stessa cosa per i nomi diventati
bugiardi: se il comportamento è cambiato, il nome cambia adesso.

## Output

Elenca i rilievi come `file:riga — cosa manca` in ordine di costo per chi cercherà, distinguendo
quelli che ricadono sotto "le convenzioni vincono" (da documentare) da quelli dove il nome si può
migliorare. Se non c'è niente, dillo in una riga. Poi chiedi quali applicare prima di modificare
i file: questo è un checkpoint, non un refactor automatico.

Chiudi con le sei domande di verifica:

1. Una sola ricerca per ogni nome nuovo basta a trovarne l'implementazione?
2. I verbi generici nuovi hanno il loro oggetto, o una convenzione che li giustifica?
3. La cosa che il chiamante deve sapere ma la firma non dice è scritta alla definizione?
4. Le stringhe di log/errore nuove esistono verbatim nel sorgente, senza interpolazione iniziale?
5. Qualcosa ha cambiato comportamento senza cambiare nome?
6. Il codice spostato è sparito da dove stava?

## Perché queste tre e non altre venti

Le regole sono tagliate sulla misura di questo repo, non su un elenco generico:
`reference/eracms-baseline.md`. Rimisura con `reference/measure_discoverability.py` se vuoi
verificare che valgano ancora.
