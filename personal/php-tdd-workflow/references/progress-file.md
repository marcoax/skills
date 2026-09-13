# Il file di progresso

`progress_[nome-progetto].md`, nella root del progetto. Creato alla conferma della decomposizione,
aggiornato subito dopo ogni task. È il report definitivo del piano.

Stati: ⏳ in attesa · 🔄 in corso · ✅ completato · ⏭ skippato · ↩️ rollback

```markdown
# Progress — [Nome Progetto]

**Avviato**: [data]
**Ultimo aggiornamento**: [data]
**Piano**: [breve descrizione]

## Task

| # | Task | Stato | Note |
|---|------|-------|------|
| 1 | Migration blocked_dates | ✅ completato | |
| 2 | Model BlockedDate | ✅ completato | Aggiunto scope active() |
| 3 | Integrazione SlotGenerator | 🔄 in corso | |
| 4 | Variabile modale | ⏳ in attesa | |
| 5 | Snippet blade | ⏭ skippato | Rimandato a sprint successivo |

## Log

- [2026-03-21 10:15] Task 1 completata — migration eseguita senza errori
- [2026-03-21 10:32] Task 2 completata — model con scope e metodi statici
- [2026-03-21 10:45] Task 3 iniziata

## Note

[osservazioni trasversali, problemi incontrati, decisioni prese durante l'implementazione]
```

In modalità TDD il log registra comunque avvio e chiusura del task, qualunque cosa faccia
internamente la skill `/tdd`:

```markdown
- [10:15] Task 3 — TDD avviato (skill /tdd)
- [10:30] Task 3 — ✅ completato (tutti i test verdi)
```
