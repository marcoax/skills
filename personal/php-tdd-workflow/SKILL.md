---
name: php-tdd-workflow
description: >
  Esegue un piano tecnico gia definito su un progetto PHP/Laravel, un task alla volta, con gate di
  approvazione, TDD opzionale e un file di progresso sempre aggiornato. Usa questa skill quando
  l'utente ha gia una specifica o un piano concreto e dice "esegui il piano", "partiamo con
  l'implementazione", "implementa questa specifica". Non usarla per TDD generico o test-first senza
  orchestrazione: in quel caso usa tdd.
---

# PHP TDD Workflow

**Un task alla volta. Sempre.** Il ciclo, per ogni task:

```
PROPOSTA → EXPLAIN → APPROVA → IMPLEMENTA → VERIFICA → (COMMIT) → PROGRESS
```

Nessuno step si salta senza conferma esplicita dell'utente. Silenzio non è conferma.

I gate di questa skill sono deliberati: servono a tenere l'utente al comando su codebase legacy.
Non accorparli, non anticipare il task successivo, non "portarti avanti" mentre aspetti risposta.

## Fase -1 — Pre-implementazione

All'avvio proponi tre strade e fermati:

1. **Scrivere la specifica da zero** → `/write-a-prd`, poi torna qui
2. **Stress-testare il piano esistente** → `/grill-me`, poi Fase 0
3. **Andare dritti alla decomposizione** → Fase 0

Se una skill delegata non c'è, dillo e offri le alternative — non reimplementarla.

## Fase 0 — Decomposizione

Analizza il piano e produci task atomiche: 1–3 file, verificabili da sole, con un output
riconoscibile, in ordine di dipendenza. Segnala come **[PARALLELA]** quelle senza dipendenze
reciproche.

Presentale in tabella — `# | Task | File | Verifica attesa | Parallelizzabile` — e chiedi se la
suddivisione va bene prima di toccare qualsiasi cosa.

Alla conferma crea `progress_[progetto].md` nella root: formato in
[references/progress-file.md](references/progress-file.md). È il documento definitivo del piano,
non ne esiste un altro.

## Fase 1 — Il ciclo

**Proposta.** Annuncia `TASK [N] di [TOTALE]`, i file coinvolti, cosa farai in una o due righe, e
le scelte: `[A]` approva `[S]` skippa `[D]` discuti. Aspetta.

**Explain.** Calibra la profondità sul task: due righe e via per un campo o una route; approccio,
pattern esistenti di riferimento e snippet dei punti non ovvi per un controller o una migration con
logica; piano completo, rischi e dipendenze per un modulo nuovo o un refactor. Chiudi con "Procedo
con l'implementazione?" e resta in chat finché non arriva un sì.

**Backend PHP**: prima dell'Explain offri la modalità TDD (`[Y]` red→green→refactor / `[N]`
diretta). Se sceglie TDD carica e segui la skill `/tdd` per tutto il task — è lei la fonte di
verità del ciclo, non reimplementarlo qui.

**Implementa** solo quanto descritto. Un file non dichiarato nell'Explain non si tocca: se serve,
fermati e chiedi.

**Verifica.** Riepiloga file toccati e cosa è cambiato in ciascuno, indica il comando o il
controllo manuale da fare, e chiedi conferma. Verifica fallita = il task resta in corso, si
corregge prima di avanzare.

**Commit** sempre opzionale, mai bloccante: se il progetto non usa git, salta in silenzio.
Conventional commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`).

**Progress** aggiornato subito dopo ogni task, non a fine sessione.

**Rollback** solo su richiesta esplicita: elenca i file toccati dal task, chiedi conferma,
ripristina, segna ↩️ nel progress. Mai automatico.

## Task parallele

Per le task marcate [PARALLELA] proponi la scelta tra farle insieme o in sequenza. Anche se
implementate insieme, verifica e registra ciascuna singolarmente.

## Comandi utente

| Comando | Effetto |
|---|---|
| `status` / `dove siamo` | stato corrente dal progress file |
| `piano` | tabella task con gli stati aggiornati |
| `skip` | salta il task corrente (⏭) |
| `pausa` / `stop` | ferma il workflow, progress salvato |
| `riprendi` | riparte dal primo task non completato |
| `rollback` | procedura di rollback del task corrente, su conferma |

## Imprevisti

Se emerge un problema non previsto: fermati subito, nessuna soluzione improvvisata. Di' cosa è
successo, perché blocca e quali opzioni ci sono, annotalo nel progress, e aspetta la decisione.
