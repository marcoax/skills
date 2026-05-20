---
title: "Output Style di Claude Code: cosa sono e come piegarli al tuo flusso di lavoro"
description: "Una guida pratica agli output style di Claude Code — dai quattro stili predefiniti alla creazione di stili custom su misura."
date: 2026-05-19
tags: [claude-code, ai, sviluppo, produttività]
---

# Output Style di Claude Code: cosa sono e come piegarli al tuo flusso di lavoro

C'è un momento ricorrente in chi usa Claude Code da qualche settimana: ti accorgi di scrivere sempre la stessa frase all'inizio di ogni sessione. *"Spiegami cosa fai mentre lo fai."* Oppure *"Non chiedermi conferma per le cose ovvie, vai."* Oppure ancora *"Rispondimi sempre con un diagramma prima del codice."*

Ripetere la stessa istruzione a ogni conversazione è il sintomo di una configurazione mancante. E la configurazione che risolve esattamente questo problema si chiama **output style**.

Questo articolo parte da zero — cosa sono, perché esistono — e arriva fino alla creazione di uno stile su misura. Lungo il percorso c'è anche una tesi: gli output style non sono solo una comodità di formattazione, ma uno strumento per decidere *quanto* l'AI ti deve far lavorare. Se non li hai mai sentiti nominare, il punto di partenza è qui sotto. Se invece li conosci già e vuoi andare dritto al custom, salta alla penultima sezione.

## Cosa sono, in una frase

Un output style cambia **come** Claude risponde, non **cosa** sa.

È una distinzione che vale la pena fissare subito, perché è il malinteso più comune. Un output style non insegna a Claude nuove nozioni sul tuo progetto, non gli dà accesso a documentazione, non modifica le sue capacità. Agisce su un piano diverso: tono, ruolo, formato della risposta. Tecnicamente lo fa modificando il *system prompt* — le istruzioni di base che Claude riceve all'avvio di ogni sessione.

Se vuoi insegnare a Claude le convenzioni del tuo codebase, lo strumento è un altro (`CLAUDE.md`). L'output style serve quando il *contenuto* va bene ma la *forma* no: troppo verboso, troppo silenzioso, troppo poco didattico per i tuoi gusti.

## I quattro stili predefiniti

Claude Code arriva con quattro output style già pronti. Tre sono pensati per la scrittura di software, uno è semplicemente il comportamento standard.

### Default

È lo stile con cui Claude Code parte se non tocchi niente. Il system prompt classico, ottimizzato per portare a termine task di sviluppo in modo efficiente. Asciutto, orientato all'azione, poche spiegazioni non richieste. Per la maggior parte del lavoro quotidiano è la scelta giusta — gli altri stili sono *deviazioni* mirate da questa base, non sostituti universali.

### Proactive

Lo stile per chi odia le pause. Con Proactive, Claude esegue subito, fa assunzioni ragionevoli al posto di fermarsi a chiedere su decisioni di routine, e in generale preferisce l'azione alla pianificazione.

Un dettaglio importante che spesso sfugge: Proactive applica la stessa logica della *auto mode* **senza** cambiare la tua permission mode. In parole povere — Claude diventa più deciso nel *ragionare e proporre*, ma tu continui a vedere le richieste di permesso prima che gli strumenti vengano effettivamente eseguiti. Non è una rinuncia al controllo, è una rinuncia alle micro-esitazioni.

Quando usarlo: prototipazione rapida, task esplorativi, momenti in cui sai già dove vuoi arrivare e le domande di Claude ti rallentano più che aiutarti.

### Explanatory

Qui si entra nel territorio "Claude come strumento di apprendimento". Con Explanatory, mentre porta avanti il task di sviluppo, Claude inserisce degli *Insights* — brevi spiegazioni didattiche del perché ha fatto una certa scelta implementativa, o di come funziona un pattern del codebase.

È lo stile da attivare quando lavori su una codebase che non conosci, o quando vuoi che ogni modifica ti lasci qualcosa di più della modifica stessa. Non ti chiede nulla: continua a fare il lavoro, ma commenta il *perché* lungo il percorso.

### Learning

Learning è Explanatory che fa un passo in più, e cambia natura. Non si limita a spiegare: ti coinvolge.

Oltre a condividere gli Insights mentre programma, Claude ti chiede di scrivere **tu** dei piccoli pezzi di codice strategici. Concretamente, inserisce nel codice dei marcatori `TODO(human)` — punti precisi dove tocca a te mettere le mani. È una modalità collaborativa, di apprendimento pratico: impari facendo, non guardando.

È lo stile più impegnativo dei quattro, ed è una scelta deliberata. Se stai usando Claude Code per *imparare* — un linguaggio nuovo, un framework, un pattern — Learning trasforma la sessione da "guarda l'esperto" a "lavoriamo insieme". Se invece hai una scadenza, non è il momento.

## Un avvertimento onesto sui costi

C'è un compromesso che la documentazione dichiara apertamente e che è giusto conoscere prima di affezionarsi a uno stile.

Gli stili Explanatory e Learning, **per costruzione**, producono risposte più lunghe del Default. Più Insights, più spiegazioni, più testo. Questo significa più token di output — e quindi un consumo maggiore. Non è un bug, è il loro funzionamento: stai pagando le spiegazioni che hai chiesto.

Sul lato input, aggiungere istruzioni al system prompt aumenta i token in ingresso, ma qui il *prompt caching* attutisce il colpo dopo la prima richiesta della sessione.

La conclusione pratica: Explanatory e Learning sono ottimi quando l'obiettivo è capire o imparare. Sono uno spreco se li lasci attivi per il lavoro di routine, dove il Default fa lo stesso lavoro con meno parole.

## Una digressione che non è una digressione: l'atrofia delle competenze

Fin qui Learning ed Explanatory possono sembrare due opzioni di comodo — Claude che parla un po' di più, per chi ha voglia di leggere. Ma c'è una lettura più seria, ed è quella che dà a questi due stili un peso che la documentazione, da sola, non lascia intuire.

Addy Osmani — figura nota nella comunità del frontend e della developer experience — ha dato un nome a un fenomeno che molti sviluppatori sentono ma faticano a mettere a fuoco: la **skill atrophy**, l'atrofia delle competenze. L'idea è semplice e scomoda. Quando ogni problema viene risolto descrivendolo a un'AI e accettando la risposta in pochi secondi, si guadagna velocità oggi e si perde qualcosa domani: la *mappa mentale* del codebase, l'istinto su dove probabilmente si annida un bug, la comprensione profonda del sistema che si è chiamati a mantenere.

Non è solo una sensazione. Esiste una ricerca, citata in questo dibattito, secondo cui gli sviluppatori che usano l'AI per generare codice ottengono punteggi più bassi — intorno al 17% — nei test di comprensione, rispetto a chi quel codice lo ha scritto a mano. Un singolo studio non è un verdetto, ma l'intuizione regge: c'è differenza tra chi *capisce* un sistema e chi sa solo *azionarlo*.

Qui gli output style smettono di essere un dettaglio di configurazione e diventano una scelta di metodo. Lo stesso Osmani sostiene da tempo che non si è obbligati a subire il comportamento di default dell'AI: lo si può guidare. E il suo consiglio ricorrente è di trattare l'AI come uno strumento di apprendimento, non come una stampella — quando l'agente produce codice che non capisci, quello è il segnale per fermarti e scavare, non per tirare dritto.

Explanatory e Learning sono esattamente questo: **attrito reintrodotto di proposito**. Explanatory ti obbliga a passare accanto al *perché* di ogni scelta. Learning ti obbliga a scrivere tu i pezzi strategici, con i suoi marcatori `TODO(human)`. Sono più lenti del Default, costano più token — e questo, in questa luce, non è un difetto ma il prezzo esplicito di non perdere la mappa.

La conclusione non è "usa sempre Learning". È più sottile: la velocità del Default è giusta quando stai eseguendo qualcosa che già padroneggi, e l'attrito di Explanatory o Learning è giusto quando stai lavorando su qualcosa che dovresti capire e non capisci ancora. Saper scegliere tra i due, sessione per sessione, è una competenza in sé.

## Come si cambia stile

Due strade.

**La via del menu.** Lanci `/config`, selezioni *Output style* e scegli dal menu. La tua scelta viene salvata in `.claude/settings.local.json`, a livello di progetto locale.

**La via del file.** Se preferisci saltare il menu, modifichi direttamente il campo `outputStyle` in un file di settings:

```json
{
  "outputStyle": "Explanatory"
}
```

Dove metti questo campo dipende da quanto vuoi che la scelta sia "larga":

- `~/.claude/settings.json` — vale per tutti i tuoi progetti
- `.claude/settings.json` — vale per il progetto ed è condivisibile col team via git
- `.claude/settings.local.json` — vale per il progetto, ma solo per te (non versionato)

Un dettaglio sul *timing* che evita confusione: l'output style viene impostato nel system prompt all'avvio della sessione. Se lo cambi mentre Claude Code è in esecuzione, la modifica **non** ha effetto subito — devi avviare una nuova sessione. È una scelta voluta: mantenere il system prompt stabile per tutta la conversazione permette al prompt caching di ridurre latenza e costo.

## Creare uno stile su misura

Qui arriva la parte interessante. I quattro stili predefiniti sono punti di partenza, ma il vero potere è scriverne uno tuo.

Uno stile custom è semplicemente un file Markdown: un blocco di *frontmatter* con i metadati, seguito dalle istruzioni da aggiungere al system prompt. Lo salvi in uno di tre posti, a seconda dello scope:

- `~/.claude/output-styles` — livello utente
- `.claude/output-styles` — livello progetto
- la directory dei *managed settings* — per policy gestite a livello di organizzazione

Il nome del file diventa il nome dello stile, a meno che tu non specifichi un campo `name` nel frontmatter.

### Un esempio concreto

Supponiamo tu voglia uno stile che apra ogni spiegazione con un diagramma, ma senza rinunciare al modo in cui Claude scrive codice. Il file potrebbe essere così:

```markdown
---
name: Diagrams first
description: Apri ogni spiegazione con un diagramma
keep-coding-instructions: true
---

Quando spieghi codice, architettura o flussi di dati, parti
da un diagramma Mermaid che mostra la struttura, poi prosegui
con la spiegazione in prosa.

## Convenzioni per i diagrammi

Usa `flowchart TD` per il control flow e `sequenceDiagram`
per i percorsi di richiesta. Tieni i diagrammi sotto i 15 nodi.
```

### Il campo che fa la differenza: `keep-coding-instructions`

C'è una decisione di fondo da prendere ogni volta che crei uno stile custom, ed è racchiusa in un campo del frontmatter.

Per impostazione predefinita, uno stile custom **rimuove** le istruzioni di ingegneria del software integrate in Claude Code — quelle che gli dicono come delimitare le modifiche, come scrivere i commenti, come verificare il lavoro. Questo ha senso quando Claude *non* sta facendo sviluppo: se lo stai trasformando in un assistente di scrittura o in un analista di dati, quelle istruzioni sono solo rumore.

Ma se invece stai solo cambiando *come comunica* — come nell'esempio del diagramma — e vuoi che continui a programmare esattamente come prima, devi impostare `keep-coding-instructions: true`. Dimenticarlo è l'errore più comune: ti ritrovi con uno stile che parla bene ma ha perso il rigore sul codice.

La regola mnemonica: **stai cambiando il mestiere o solo la voce?** Se cambi il mestiere, lascia il campo a `false` (il default). Se cambi solo la voce, mettilo a `true`.

### Gli altri campi del frontmatter

Oltre a `name`, `description` e `keep-coding-instructions`, c'è un quarto campo che riguarda chi distribuisce stili tramite plugin: `force-for-plugin`. Se impostato, applica lo stile automaticamente quando il plugin è attivo, scavalcando la scelta dell'utente. È uno strumento per chi pacchettizza configurazioni per altri, non per l'uso quotidiano.

## Output style o qualcos'altro?

Gli output style sono uno strumento tra tanti per personalizzare Claude Code, e usarli al posto sbagliato è facile. Qui sotto la bussola.

- **Output style** — vuoi un ruolo, un tono o un formato di risposta diverso a *ogni* turno. Modifica il system prompt.
- **`CLAUDE.md`** — vuoi che Claude conosca *sempre* le convenzioni e il contesto del tuo progetto. Aggiunge un messaggio dopo il system prompt.
- **`--append-system-prompt`** — vuoi un'aggiunta usa-e-getta per una singola invocazione.
- **Agents** — vuoi un assistente separato, con un suo system prompt, modello e strumenti, per un compito circoscritto.
- **Skills** — hai un flusso di lavoro ripetibile da caricare solo quando serve.

La sintesi: l'output style è la scelta giusta quando il problema è *come Claude si presenta a ogni risposta*. Per tutto il resto — contesto di progetto, aggiunte una tantum, workflow — esistono strumenti più adatti.

## In conclusione

Gli output style sono una di quelle funzionalità che sembrano un dettaglio finché non le usi. Il loro valore non è nei quattro stili predefiniti — per quanto Learning ed Explanatory siano notevoli — ma in due idee di fondo. La prima, pratica: smettere di ri-promptare la stessa cosa, e codificarla una volta. La seconda, più importante: scegliere consapevolmente quanta velocità e quanto attrito vuoi, invece di subire il default. In un'epoca in cui è facilissimo lasciare che l'AI faccia tutto e capire sempre meno, avere una leva esplicita su quel compromesso non è poco.

Il consiglio per iniziare è minimale. Prova Explanatory per qualche giorno su un progetto che non conosci bene, e osserva se gli Insights ti servono davvero o ti distraggono. Se ti accorgi di volere un comportamento ricorrente che nessuno dei quattro stili copre — quello è il momento di scrivere il tuo file Markdown.

La documentazione ufficiale completa, con tutti i dettagli sui campi e sul debug, è su `code.claude.com/docs/en/output-styles`.
