# Scoring Checklist — log-analyzer

Usa questa checklist per valutare ogni output del log-analyzer.
**Tutte e 4 le domande devono rispondere SÌ per considerare l'output corretto.**

---

## Checklist (4 domande Sì/No)

| # | Domanda | SÌ / NO |
|---|---------|---------|
| Q1 | Il file `error_trend.html` contiene i dati di **tutti** i giorni precedenti presenti in `error_history.json`, non solo quello corrente? | |
| Q2 | I nuovi tipi di errore (non presenti in `known_errors.txt`) sono elencati **esplicitamente nel messaggio in chat** — non solo nello stdout grezzo dello script? | |
| Q3 | Il contenuto completo del `log_report_*.md` è stato mostrato all'utente **prima** della domanda sulle nuove regole di pulizia? | |
| Q4 | Il report `.md` include tutte e 3 le sezioni obbligatorie: distribuzione oraria · tabella errori per tipo · nota riassuntiva top-3? | |

**SCORE: ___/4 — PASS ≥ 4/4 · FAIL < 4/4**

---

## Note per l'applicazione

- **Q1** si verifica aprendo `error_trend.html` e controllando che il grafico mostri più di un giorno (se sono stati analizzati log multipli in passato)
- **Q2** si verifica leggendo l'output della conversazione: i nuovi errori devono apparire come lista nel messaggio, non solo come righe di terminale
- **Q3** si verifica nell'ordine della conversazione: prima il markdown del report, poi la domanda
- **Q4** si verifica aprendo il `log_report_*.md` generato e cercando le tre sezioni
