---
name: runbook
description: Interventi operativi documentati. Usala quando devi intervenire su server, servizi, istanze cloud, configurazioni d'ambiente o certificati, o documentare un intervento fatto o da fare.
when_to_use: 'Es.: "documenta il rinnovo del certificato", "devo riavviare il servizio in produzione", "scrivi la procedura per…", "annota cosa ho fatto sul server". Anche per note di intervento in un wiki o vault.'
---

# Runbook e interventi operativi

Due tipi di documento:

| Tipo | Cos'è | Template |
|---|---|---|
| **Runbook** | procedura riutilizzabile per un sistema: come si controlla, si riavvia, si diagnostica | [runbook.md](templates/runbook.md) |
| **Intervento** | il resoconto di un'operazione specifica: cosa è successo, cosa si è fatto, con quale esito | [intervento.md](templates/intervento.md) |

Un intervento che si ripete diventa un runbook. Il resoconto poi rimanda al runbook come "caso di riferimento".

## Contesto del progetto
Dal `CLAUDE.md` del progetto ricava:
- ambienti, host e accessi (chi li ha: di norma l'utente, non Claude);
- servizi e come si gestiscono;
- dove vanno i documenti;
- finestre di manutenzione e a chi comunicarle.

## Sequenza di un intervento
1. **Leggi lo stato**: versioni, configurazione, processi, spazio, conteggi, ultimi errori nei log. È la fotografia "prima", da confrontare alla fine.
2. **Diagnostica prima di riparare**: capisci perché il sistema è in quello stato. Un riavvio che toglie il sintomo senza una causa è un rimedio, e va dichiarato come tale.
3. **Modifica**: con comandi o file preparati e riletti, non digitati a mano sul momento. Una modifica per volta.
4. **Prova**: un esito reale end-to-end (la pagina risponde, il job gira e produce l'output, la connessione si stabilisce), non solo "il servizio risulta attivo".
5. **Resoconto**: cosa è cambiato, cosa si è osservato, cosa resta aperto. La fotografia "dopo" accanto a quella "prima".

## Regole di esecuzione
- **I comandi sulle macchine remote li esegue chi ha l'accesso**, uno alla volta, ciascuno con il suo **esito atteso**. Se l'esito reale è diverso ci si ferma: non si prosegue "per vedere".
- **Sempre backup, poi modifica, poi verifica.** Prima di cambiare un file di configurazione: copia datata (`cp file file.bak-aaaammgg`). Dopo: verifica che il servizio sia su e che faccia ciò che deve.
- **Rollback scritto prima di iniziare**: la procedura inversa deve esistere prima della modifica, non dopo.
- **In produzione**: ok esplicito dell'utente per ogni passo che cambia lo stato, finestra concordata, eventuale banner o avviso agli utenti.
- **Separare i fatti dalle proposte.** Ciò che si è fatto va in "Procedura" ed "Esito". Le idee di miglioramento vanno in "Proposte (non applicate)".
- **Nessun segreto nel documento**: né password, né token, né chiavi. Indica *dove* si trovano (vault, secret manager), mai il valore. Prima di incollare log, configurazioni o variabili d'ambiente, oscura i valori sensibili.
- **Perimetro dichiarato**: host, servizi e directory su cui si interviene. Ciò che è fuori non si tocca, anche se sembra collegato: si segnala.
- **Comandi distruttivi** (cancellazioni ricorsive, `DROP`, `TRUNCATE`, `DELETE` senza `WHERE`, sovrascrittura di file di configurazione, riavvii in produzione, rinnovo o revoca di certificati) si riconfermano uno per uno, anche dentro una procedura già approvata.

## Scrittura
- La sezione **"Se hai fretta"** apre il documento: i 3-5 comandi essenziali, per chi deve intervenire di notte.
- Coordinate precise: host, istanza, percorsi, nome del servizio, porte, versioni.
- Il percorso d'indagine include le **piste scartate**, con il motivo: evita di ripercorrerle.
- Date e orari per esteso, con il fuso se conta.
