---
name: ci-cd
description: "Progettare e rivedere pipeline CI/CD, deploy e rollback. Usala quando scrivi o correggi una pipeline, o con azure-pipelines.yml, .gitlab-ci.yml o Jenkinsfile."
---

# CI/CD

Si applica insieme a `clean-code` (sicurezza compresa). Per tag, versioni e branch: `git-workflow`. Per le immagini: `container`. Per i rilasci in produzione: `rilascio` (se disponibile). Sintassi e trappole delle piattaforme: `references/piattaforme.md`. Prevalgono la piattaforma, i template condivisi e le convenzioni dell'azienda: estendi la pipeline esistente, non riscriverla.

## Fasi
Una pipeline è una sequenza che dà un segnale sempre più costoso e più fidato:
1. **Build e test veloci** (compilazione, test unitari, lint): minuti, ad ogni commit.
2. **Analisi** (qualità statica, copertura, dipendenze vulnerabili, scansione dei segreti): blocca sul codice nuovo (quality gate), non sul debito storico.
3. **Pacchetto**: un artefatto (jar, immagine, archivio) con versione tracciabile al commit.
4. **Test di integrazione e di sistema** su un ambiente fedele (servizi veri o in container).
5. **Deploy** ad ambienti successivi (sviluppo, collaudo, produzione) con controlli e approvazioni crescenti.

Mettere prima i controlli più rapidi e più probabili a fallire: un errore di lint non deve costare venti minuti di test.

## Un artefatto, tanti ambienti
- Si **costruisce una volta** e si promuove lo stesso artefatto: ciò che hai provato in collaudo è ciò che va in produzione. Ricostruire per ambiente rompe questa garanzia (dipendenze diverse, un altro commit, flag diversi).
- Le differenze stanno nella **configurazione iniettata** al deploy (variabili, file, secret), mai nell'artefatto.
- L'artefatto ha un identificativo immutabile (versione + commit, digest dell'immagine) e si pubblica in un registry o in un feed, non si passa tra job "a mano".
- Il deploy usa l'artefatto prodotto dalla stessa esecuzione (o una versione scelta esplicitamente), non il "più recente" del registry.

## Cache e dipendenze
- Chiave di cache dal **lockfile** o dal descrittore delle dipendenze (`pom.xml`, `package-lock.json`, `Gradle` lock): cambia quando cambiano le dipendenze, non a ogni commit.
- La cache è un'ottimizzazione, non una fonte: la pipeline deve passare anche a cache vuota. Non mettere in cache gli output di build che possono mascherare errori.
- Installazioni riproducibili: `npm ci` (non `npm install`), versioni fissate dei plugin e degli strumenti, immagini del runner con tag fissato.
- Le dipendenze arrivano dal repository aziendale (proxy/mirror) se esiste; una nuova dipendenza segue la regola di Mímir: ok dell'utente.

## Segreti e variabili
- Mai in chiaro nel repo né nei log. Usa i meccanismi della piattaforma: variabili protette/mascherate, gruppi di variabili e collegamenti a un key vault, secret dell'ambiente.
- **Segreti legati all'ambiente** e agli ambienti protetti: il token di produzione è visibile solo ai job di produzione, su branch o tag protetti. Una pipeline lanciata da un fork o da una pull request esterna non deve ricevere segreti.
- Il mascheramento dei log non è una garanzia (un valore trasformato, in base64 o spezzato, sfugge): non stampare mai variabili d'ambiente (`env`, `set -x` in script con segreti).
- Credenziali a vita breve (federazione OIDC, identità gestite) preferibili a token statici, dove la piattaforma e l'azienda li offrono.
- Il contenuto di una pull request (nome del branch, titolo, messaggi) è input non fidato: non interpolarlo in uno script di shell (iniezione di comandi).
- Un segreto finito in un commit o in un log è compromesso: ruotalo, non basta cancellarlo.

## Produzione: approvazioni e controlli
- Il deploy in produzione richiede **approvazione manuale** (ambiente protetto con approvatori, gate manuale) e parte da un artefatto già validato negli ambienti precedenti.
- Branch e tag di rilascio protetti; chi approva non coincide con chi ha scritto la modifica, quando la policy lo prevede.
- Un solo deploy alla volta per ambiente (concorrenza/lock di ambiente): due pipeline che deployano insieme sovrascrivono lo stato.
- Prima del deploy: controlli di salute dell'ambiente, finestra di rilascio rispettata, migrazioni compatibili (`database`).
- Dopo: smoke test e controllo di salute automatici; se falliscono, la pipeline segnala e, dove previsto, torna indietro da sola.
- Una pipeline non fa commit, tag o push automatici su branch protetti se non è un processo concordato e documentato.

## Pipeline veloci e affidabili
- **Test instabili (flaky)**: non si risolvono con un retry silenzioso. Isola e segnala il test, apri un ticket, correggi la causa (tempo, ordine, dati condivisi, risorse esterne). Un retry automatico limitato e visibile è una misura temporanea, non la cura; un test instabile ignorato insegna a ignorare i fallimenti.
- **Parallelismo**: dividi i test in più job o in shard, i job indipendenti partono insieme (grafo di dipendenze tra job, non fasi rigide). I test paralleli non condividono database o porte fisse.
- Esegui solo ciò che serve: filtri per percorso o per tipo di modifica (la documentazione non lancia l'intera suite), ma senza saltare controlli sul ramo principale.
- Annulla le esecuzioni superate sullo stesso branch; timeout per job così che un blocco non occupi un runner per ore.
- Misura i tempi per fase: ottimizza la fase più lunga, non quella più comoda.
- **Fail fast, ma con report completi**: un fallimento dà log leggibili e artefatti (report di test, copertura) conservati, non solo "exit code 1".
- Le pipeline sono codice: versionate, riviste, con template condivisi invece di copia-incolla fra repository.

## Versioni, tag, rollback
- Versione dell'artefatto derivata dal tag o dal commit (regole in `git-workflow`), mai da un numero modificato a mano in fase di build. Il numero di versione e il tag Git devono corrispondere.
- Il **rollback** è ridistribuire l'artefatto precedente (già disponibile e identificato), non ricostruire il vecchio codice. Verifica che l'artefatto vecchio sia ancora nel registry (politiche di pulizia!) e che lo schema del database sia compatibile.
- Documenta nella pipeline o nel runbook (`runbook`, se disponibile) come tornare indietro e chi lo decide.
- Le modifiche irreversibili (migrazioni distruttive, invio di messaggi) vanno separate dal deploy ed eseguite con ok esplicito.

## Modificare una pipeline
- Una pipeline si prova in un ramo o su un progetto di prova, perché il suo effetto è su ambienti condivisi. Cambiamenti ai passi di deploy: descrivi cosa cambia per ogni ambiente e chiedi conferma.
- Non lanciare, rilanciare o annullare pipeline di deploy per conto dell'utente senza richiesta esplicita; lo stesso vale per le variabili di progetto.
- Non indebolire un controllo (quality gate, test, approvazione) per far passare una pipeline: segnala il problema.
- La sintassi si valida con gli strumenti della piattaforma (vedi `references/piattaforme.md`) prima di spingere.

## Verifica
- Valida la sintassi con lo strumento della piattaforma (lint del CI di GitLab, l'editor delle pipeline di Azure DevOps, che valida il YAML, `actionlint`, `Jenkinsfile` linter) quando disponibile; dichiara cosa non hai potuto provare in locale.
- Riproduci in locale i comandi dei passi (build, test, analisi) con gli stessi comandi della pipeline e riporta l'esito.
- Rileggi il diff: nessun segreto, nessun tag mobile, cache con chiave corretta, deploy di produzione ancora protetto da approvazione, artefatto promosso e non ricostruito.
- Dopo il push (con ok dell'utente), leggi l'esito reale della pipeline: "la configurazione sembra corretta" non è un risultato.

## Riferimenti
| File | Quando leggerlo |
|---|---|
| [references/piattaforme.md](references/piattaforme.md) | Scrivi o correggi una pipeline su Azure DevOps, GitLab CI, GitHub Actions o Jenkins |
