# Optimization Log — log-analyzer SKILL.md

Metodologia: Karpathy autoresearch (una modifica per round, scored vs checklist binaria)
Checklist: `assets/SCORING_CHECKLIST.md` (4 domande Sì/No, target ≥ 4/4)

---

## Baseline — Round 0

**Score: 3/4 (75%)**

| Q | Domanda | Score | Motivazione |
|---|---------|-------|-------------|
| Q1 | HTML preserva storia | PASS | Meccanismo `update_error_history` verificato con test 2-giorni |
| Q2 | Nuovi errori visibili in chat | **FAIL** | SKILL.md diceva solo "leggi il .md" — i nuovi errori stanno nello stdout, non nel .md |
| Q3 | Report mostrato prima della domanda | PASS | Già fixato in sessione precedente con passi espliciti |
| Q4 | 3 sezioni nel report | PASS | Verificato sul file generato da `log_errori_sample.txt` |

---

## Round 1 — Target: Q2

**Cambio applicato:** Aggiunto passo esplicito nel post-analysis step:
- Controlla stdout per `*** NEW ERROR TYPES DETECTED`
- Se presente: mostra i nuovi errori come blocco prominente con `⚠️` in chat
- Se assente: nessuna azione

**Motivo:** Q2 falliva perché i nuovi errori appaiono solo nello stdout grezzo dello script,
non nel file `.md`. Il SKILL.md non aveva istruzione per estrarre e riportare queste righe.

**Risultato:** PASS → score sale a **4/4**

---

## Score finale — Round 1

**Score: 4/4 (100%) ✓ TARGET RAGGIUNTO**

| Q | Score |
|---|-------|
| Q1 | ✅ PASS — verificato con simulazione 2 giorni |
| Q2 | ✅ PASS — istruzione esplicita aggiunta |
| Q3 | ✅ PASS — ordine esplicito: report → domanda |
| Q4 | ✅ PASS — tutte e 3 le sezioni presenti nel report generato |

---

## Modifiche totali applicate a SKILL.md in questa sessione

| # | Modifica | Tipo | Impatto |
|---|---------|------|---------|
| F6 | Frontmatter description: trigger limitati a Symfony/caricare, guard per non-Symfony | Trigger | Riduce falsi positivi |
| F4 | Guard "se path mancante → chiedi prima" | Istruzione | Elimina crash su path assente |
| F2 | Doc output dir: CWD, non dir input | Documentazione | Elimina info errata |
| F1 | Post-analysis: leggi .md e mostralo integralmente | Istruzione | Output deterministico |
| F3 | Manual fallback: 6 passi concreti | Istruzione | Elimina "applica manualmente" vuoto |
| F5 | Template helper per nuove regole + posizione in clean_block() | Istruzione | Sync regole deterministico |
| R1 | New errors da stdout → blocco prominente in chat | Istruzione | Q2 portato a PASS |

**Nessun cambio revertito.**
