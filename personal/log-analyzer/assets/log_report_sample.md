# Analisi Log Errori — 2026-03-20

**File:** `log_errori_sample.txt`
**Data:** 2026-03-20
**Totale errori:** 225

## FONTE
- Analisi basata su `log_errori_sample.txt`

---

## Distribuzione oraria

| Ora | Errori | % |
|-----|-------:|--:|
| 04:00 | 37 | 16.4% |
| 05:00 | 40 | 17.8% |
| 06:00 | 30 | 13.3% |
| 07:00 | 50 | 22.2% |
| 08:00 | 68 | 30.2% |
| **Totale** | **225** | **100%** |

> Il picco si concentra nelle fasce **07:xx** e **08:xx** (118 errori, 52.4% del totale).

---

## Occorrenze per tipo di errore

| # | Errore | Count | % | FIXED |
|---|--------|------:|--:|-------|
| 1 | `Process already in progress for serial {N}` | 121 | 53.8% |  |
| 2 | `Get Machine Configuration variable content should be 26 or 27 bytes instead of {N}` | 55 | 24.4% |  |
| 3 | `Aggregate with id '{UUID}' not found` | 35 | 15.6% |  |
| 4 | `Call to a member function getSupportUser() on null` | 5 | 2.2% |  |
| 5 | `Expected response code 250 but got code "451", with message "451 4.4.2 Timeout waiting for data from client. "` | 4 | 1.8% |  |
| 6 | `Invalid date format {values}` | 3 | 1.3% |  |
| 7 | `Command not implemented: '20'` | 1 | 0.4% |  |
| 8 | `invalid argument for replace: empty key` | 1 | 0.4% |  |

> I 3 errori più frequenti (`Process already in progress for serial {N}`, `Get Machine Configuration variable content should be 26 or 27 bytes instead of {N}`, `Aggregate with id '{UUID}' not found`) rappresentano il 93.8% del totale (211/225 errori).
