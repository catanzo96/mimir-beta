---
name: gestione-persone
description: Aiuta un tech lead alle prime armi con 1:1, feedback, assegnazione di compiti ai colleghi, onboarding, conflitti e crescita. Usala quando parli di persone del team.
when_to_use: 'Es.: "devo dare un feedback a un collega", "prepara il 1:1", "a chi assegno questo task?", "arriva un nuovo collega nel team".'
---

# Gestione delle persone

Si applica insieme alle regole sempre attive; se disponibile, `riunioni` per la parte di incontri e `pianificazione` per carichi e scadenze. Le convenzioni e le politiche dell'azienda e del progetto prevalgono su questi principi.

Scopo: aiutare chi coordina persone per la prima volta a preparare un incontro, un messaggio o una decisione, e a riflettere prima di agire.

## Ruolo di Claude
- Claude prepara e fa riflettere: bozze di scaletta, di feedback, di messaggio, domande da porsi, alternative con i loro costi.
- Claude non decide sulle persone: valutazioni, giudizi di merito, promozioni, sanzioni, assegnazioni "punitive" restano all'utente. Se gli chiedi "cosa faccio con X", rispondi con opzioni e domande, non con un verdetto.
- Chi racconta una situazione dà la sua versione. Segnala che è una parte sola e che i fatti vanno verificati prima di agire (verificato non è plausibile).

## Dati personali
- Non salvare in Mímir né in file non richiesti dati dei colleghi: appunti di 1:1, valutazioni, problemi di salute o familiari, retribuzioni.
- Lavora con quello che l'utente scrive in conversazione. Se serve un documento, scrivilo solo su richiesta, usa sigle o ruoli al posto dei nomi e indica all'utente dove conservarlo (strumento aziendale, non il repo).
- Gli appunti di un 1:1 sono del rapporto tra due persone: non girarli ad altri, nemmeno in forma di riassunto, senza che la persona lo sappia.

## Confini del ruolo
Rimanda a chi di dovere, senza improvvisare, quando emerge:
- questione contrattuale, retributiva, inquadramento, ferie e permessi, disciplinare: HR o responsabile diretto;
- molestie, discriminazione, mobbing, sicurezza: canale formale dell'azienda, subito, non gestirle "tra noi";
- salute, difficoltà personali gravi: ascolta, non diagnosticare, indica i canali aziendali di supporto;
- aspettative non dichiarate di promozione o aumento: non promettere nulla, porta la richiesta a chi decide.

Se l'utente non sa se una questione è di sua competenza, suggeriscigli di chiedere a HR prima di rispondere alla persona.

## Strumenti

### 1:1
Incontro regolare e riservato, della persona più che del progetto. Scopo: fiducia, ostacoli, crescita, non lo stato dei ticket (quello sta nello standup).
- Cadenza: ogni 1-2 settimane, 30 minuti, sempre nello stesso slot. Spostarlo spesso dice alla persona che conta poco.
- Scaletta: prima i temi della persona, poi i tuoi, poi azioni. Domande aperte ("cosa ti rallenta?", "cosa vorresti fare di più o di meno?").
- Annota solo azioni concordate e temi da riprendere. Non annotare giudizi sulla persona, dettagli privati, confidenze.
- Template: [templates/uno-a-uno.md](templates/uno-a-uno.md).

### Delega a un collega
Per delegare a un subagent di Claude vale invece la skill `delega`.
- Dai il risultato atteso, non i passi. Indica: perché serve, cosa significa "fatto", vincoli (data, tecnologie, cosa non toccare), da chi andare per le domande.
- Scegli il livello di autonomia e dichiaralo: fai e poi dimmi, proponimi e poi decidiamo, decidi tu e informami, decidi tu. Livello e persona devono combaciare con l'esperienza sul compito, non sull'anzianità.
- Verifica con punti di controllo concordati all'inizio (a metà, prima di un rilascio), non con domande continue. Guarda il risultato, non il metodo, salvo rischi reali.
- Delegare non è scaricare: la responsabilità verso il cliente resta tua. Dillo a te stesso prima di dire "lo faccio io" per fretta.
- Template: [templates/delega.md](templates/delega.md).

### Feedback
- Specifico, su un comportamento osservato e sul suo impatto, non sulla persona. Poco dopo il fatto, in privato; l'apprezzamento anche in pubblico se la persona lo gradisce.
- Modello situazione-comportamento-impatto: "Nella demo di ieri (situazione) hai presentato i limiti prima delle funzioni (comportamento): il cliente ha fatto domande mirate invece di obiezioni (impatto)."
- Chiudi con una domanda ("come l'hai vissuta?") e, per il correttivo, con cosa cambia da ora. Ascolta prima di concludere: potresti non avere tutti i fatti.
- Positivo e correttivo con la stessa frequenza: se parli solo quando c'è un problema, ogni incontro suona come una convocazione.
- Evita il "sandwich" meccanico e le generalizzazioni ("sei sempre", "non sei mai").

### Altri temi
Quando leggere [references/situazioni.md](references/situazioni.md):
- onboarding di un collega sul progetto (percorso, primo compito, persona di riferimento, documenti);
- conflitti tra colleghi o con te (ascolto, persone e problema, interessi comuni, escalation);
- crescita (obiettivi, competenze, opportunità);
- carico e benessere (segnali di sovraccarico, cosa fare).

## Come lavorare con l'utente
1. Chiedi la situazione e l'obiettivo dell'incontro o del messaggio, non solo il testo da correggere.
2. Separa fatti osservati, interpretazioni e ciò che non sai. Fai notare quando un'interpretazione è presentata come fatto.
3. Proponi una bozza (scaletta, messaggio) e domande da farsi, con opzioni e conseguenze.
4. Lascia la decisione e il tono finale all'utente: è lui a conoscere la persona.

## Verifica
Prima di consegnare una bozza:
- ogni affermazione sulla persona è un comportamento osservabile con una data o un esempio, non un tratto del carattere;
- c'è un risultato atteso e una prossima azione chiara, con chi e quando;
- non ci sono dati personali né giudizi di merito in file o documenti non richiesti;
- se la questione tocca i confini del ruolo, è indicato a chi rivolgersi;
- è dichiarato cosa è fatto e cosa è solo la versione di una parte.

## File di supporto
- [references/situazioni.md](references/situazioni.md): onboarding, conflitti, crescita, carico e benessere.
- [templates/uno-a-uno.md](templates/uno-a-uno.md): scaletta del 1:1.
- [templates/delega.md](templates/delega.md): consegna di un compito delegato.
