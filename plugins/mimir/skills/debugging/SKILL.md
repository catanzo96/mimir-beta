---
name: debugging
description: Metodo per trovare la causa di un difetto in qualsiasi stack. Usala quando qualcosa non funziona, fallisce, è lento o intermittente, prima di proporre un fix.
when_to_use: 'Es.: "non funziona", "dà errore", "il test è rosso", "ogni tanto va in timeout", "è diventato lento", uno stack trace incollato.'
---

# Debugging

Si applica insieme a `clean-code` (per il fix e i test) e alla skill del linguaggio o del framework in uso. Per i difetti segnalati da terzi, se disponibile, vale anche `ticket`; se la diagnosi va consegnata come documento (incidente, causa radice), `analisi-tecnica`. Prevalgono le convenzioni e gli strumenti del progetto.

Regola di fondo: nessun fix senza una causa accertata. Un fix provato "per vedere se passa" nasconde il sintomo e lascia il difetto.

## Quando non usarla
- Errore di compilazione o di build con messaggio chiaro: leggi il messaggio e correggi. Per Spring Boot c'è `spring-boot/references/diagnosi-build.md`.
- Il difetto è già spiegato e serve solo il fix: passa alla sezione "Il fix".

## 1. Un ciclo di riproduzione
Senza un segnale rapido e ripetibile ("succede" / "non succede") ogni ipotesi resta una scommessa. Dedica qui lo sforzo maggiore. Dal più veloce al più lento:
1. test che fallisce, al livello più basso che raggiunge il difetto;
2. replay dello stesso input del caso reale (payload, file, messaggio), ripulito da dati personali e segreti;
3. script o comando su un ambiente locale (chiamata HTTP, CLI con un file di prova);
4. confronto tra due versioni o due configurazioni sullo stesso input;
5. query in sola lettura che mostra lo stato anomalo (ambiente e data dichiarati; se non hai accesso, la lancia l'utente);
6. scenario manuale con passi ed esito atteso scritti.

Poi stringi il ciclo: meno dati, meno passi, meno secondi, finché resta il minimo che riproduce il problema. Un ciclo da 10 minuti si usa tre volte, uno da 5 secondi trenta.

Se non riesci a riprodurre, non indovinare: vai a "Causa non trovata".

## 2. Cosa è cambiato e con cosa confrontare
- **Cosa è cambiato**: rilasci, commit (`git log --since`), configurazione, dati, versioni di librerie, certificati, servizi esterni, ora e fuso. Molti difetti "improvvisi" hanno una data di inizio.
- **Caso che funziona**: altro record, altro utente, altro ambiente, versione precedente. La differenza minima tra i due casi indica dove guardare. Cambia una variabile per volta.
- **Bisezione**: con una versione buona e una cattiva, `git bisect` trova il commit in pochi passi. Se il ciclo è automatico usa `git bisect run <script>` (il codice di uscita dice buono/cattivo; 125 salta i commit non compilabili). Se il difetto è nei dati o nella configurazione, dimezza quelli. Per l'ambiente o la configurazione, dividi in gruppi che coprono tutto, compreso un gruppo "altri", e prova prima il caso con tutti i gruppi: se è buono, la causa è lì. Poi prova ogni gruppo da solo e il tutto meno un gruppo: con l'esclusione da sola, due gruppi che bastano ciascuno non si vedono.

## 3. Restringere
- **Risali dal sintomo all'origine**: parti dal punto in cui il dato è sbagliato e torna indietro (chi l'ha scritto, con quale input, da dove veniva) fino al primo punto in cui è già errato. Lì c'è la causa, non dove si manifesta.
- **Strumenta ai confini**: un log o un'asserzione dove il dato entra ed esce da ogni componente (controller, servizio, query, chiamata esterna, coda) mostra in quale tratto si rompe. Non ovunque: troppo output nasconde il segnale.
- **Un'ipotesi per volta**: scrivila ("il campo arriva nullo dal servizio X perché ..."), scegli la verifica più piccola che può smentirla, eseguila, annota l'esito. Un'ipotesi non verificata resta un'ipotesi.
- **Leggi il messaggio per intero**: stack trace fino alla prima riga della tua applicazione, causa annidata (`Caused by`), codice e testo dell'errore. Spesso la risposta è già lì.
- Prima di dare la colpa a libreria, compilatore o infrastruttura, escludi il tuo codice: succede di rado.

## 4. Dopo 2-3 fix falliti: fermati
Se due o tre correzioni non hanno risolto, o ne hanno fatto emergere altre altrove, l'ipotesi di partenza è sbagliata o il difetto è strutturale. Smetti di aggiungere toppe:
- torna al ciclo di riproduzione e controlla che misuri davvero il difetto;
- riscrivi cosa sai con certezza e cosa hai solo supposto;
- riparti da una nuova ipotesi, oppure dichiara all'utente che il problema è di design e propone le opzioni (se serve, l'agent `mimir:architetto`).

## 5. Problemi intermittenti
Annota quando succede e quando no: ora, carico, utente, ambiente, ordine delle operazioni. Sospetta concorrenza, cache, timeout, stato condiviso tra richieste, dipendenza dall'ora. Una sola riproduzione non basta: ripeti il ciclo molte volte prima e dopo il fix e confronta le frequenze. Tecniche per tipo di problema: `references/tecniche.md`.

## 6. Causa non trovata
È un risultato, non un fallimento da nascondere. Consegna:
- cosa hai provato e cosa hai escluso, con l'evidenza di ciascuna esclusione;
- le ipotesi rimaste, in ordine di probabilità, e la verifica che le separerebbe;
- l'osservabilità da aggiungere (log mirati, metriche, id di correlazione) perché la prossima occorrenza si spieghi da sola, proposta all'utente prima di inserirla;
- cosa serve da fuori (accesso a un ambiente, un dump, un'ora precisa dell'evento).

## Il fix
1. **Test che fallisce prima**: scrivilo, vedilo fallire per il motivo giusto, poi correggi e vedilo passare. Un test mai visto fallire non dimostra nulla. Se non è testabile, di' perché e usa il ciclo di riproduzione come prova.
2. Correggi la causa, non il sintomo. Un controllo difensivo nel punto in cui il dato arriva sbagliato non sostituisce la correzione dove nasce.
3. **Togli la strumentazione temporanea** (log, stampe, asserzioni, flag) prima di consegnare: ricercala nel diff. Se un log serve davvero, tienilo secondo `clean-code/references/errori-logging.md`, senza dati sensibili.
4. Cerca lo stesso difetto altrove (stesso schema, stesso helper) e segnalalo senza correggerlo fuori perimetro.
5. Verifica che il ciclo di riproduzione non fallisca più, ripetuto come sopra se il difetto era intermittente.

## Resoconto
Separa ciò che hai accertato (evidenza: `file:riga`, comando, esito, ambiente e data) da ciò che è ipotesi. Indica la causa, il fix, il test, cosa hai escluso e quali limiti ha la verifica.

## Verifica
Prima di dichiarare finito lancia build, test e linter del progetto (`mvn verify`, `./gradlew check`, `npm test`, `ng lint`, `pytest`, secondo ciò che è configurato) e riporta comandi ed esiti. Controlla il diff: niente strumentazione temporanea, niente file di prova.

## File di supporto
- `references/tecniche.md`: leggilo per memoria e prestazioni, concorrenza, rete e integrazioni, dati e cache.
