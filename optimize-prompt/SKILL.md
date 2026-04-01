---
name: optimize-prompt
description: Riformula un prompt per renderlo più efficace per un agent AI. Usa quando vuoi migliorare un prompt prima di eseguirlo.
disable-model-invocation: true
---

# Prompt Optimizer

Riformula il prompt per massimizzare efficacia con agent AI, poi eseguilo.

## Principi

- **Tono senior developer**: formula come farebbe uno sviluppatore esperto (salvo diversa indicazione)
- **Chiarezza > brevità**: aggiungi contesto se serve
- **Esplicita l'implicito**: requisiti, vincoli, output atteso
- **Struttura**: usa bullet/step se il task è complesso
- **Imperativo**: verbi d'azione diretti
- **No fluff**: elimina solo cortesie e premesse inutili

## Quando aggiungere

- Contesto mancante (linguaggio, framework, file)
- Output atteso non chiaro
- Vincoli o requisiti impliciti
- Step intermedi se task complesso

## Quando rimuovere

- "Ciao", "per favore", "grazie", "vorrei che tu"
- Spiegazioni del perché serve
- Ripetizioni

## Workflow

1. Input: `$ARGUMENTS`
2. Analizza: cosa manca? cosa è superfluo?
3. Riformula per massima efficacia
4. Mostra:

```
## Prompt Ottimizzato
[prompt riformulato]

Confermi? (s/n)
```

5. Se "s" → esegui `/clear`, poi stampa SOLO il prompt ottimizzato (nient'altro, pronto per copia/incolla o invio)
