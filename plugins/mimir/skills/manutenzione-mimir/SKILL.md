---
name: manutenzione-mimir
description: "Audit periodico di Mímir: sovrapposizioni, peso del contesto, skill inutilizzate, riferimenti rotti, versioni datate. Solo manuale: /manutenzione-mimir."
disable-model-invocation: true
---

# Manutenzione di Mímir

Si applica insieme a `scrivi-skill` (standard da seguire per ogni modifica) e a `contesto-e-costi` (come si misura il contesto). Complementa `retro`: `retro` raccoglie ciò che emerge da una sessione, questa skill controlla lo stato dell'insieme. Cartella di Mímir: la root del marketplace che contiene questa skill.

Obiettivo: un elenco di proposte motivate, con evidenze. Non si modifica nulla senza ok; non si fa commit né push.

## Procedura

1. **Inventario e misure.** Parti dai numeri, poi giudica. Gli script sono in `references/misure.md`; provali prima su un caso con errore noto, come indicato lì.
   - Skill e agent per plugin, lunghezza di ogni description, righe di ogni SKILL.md.
   - Costo fisso: `claude plugin details <plugin>` (always-on in token), `/doctor` (stima della lista delle skill), `/context` (peso di CLAUDE.md, regole e skill in una sessione reale).
   - Peso delle regole e del profilo: sono in contesto a ogni sessione.
2. **Controlli sulle description.** Ognuna deve dire quando usare la skill, con i segnali concreti (richieste, file, manifest). Segnala: manca il "quando"; riassume il metodo; supera ~300 caratteri; due skill con trigger che si sovrappongono; frontmatter con campi esclusi dallo standard `scrivi-skill` (`model`, `paths`, `allowed-tools`), anche se Claude Code li accetta.
3. **Sovrapposizioni e contraddizioni.** Cerca lo stesso contenuto in più posti e indicazioni che si smentiscono (per esempio un modello diverso per lo stesso lavoro, un limite di righe diverso). Il metodo di lettura sta in `references/misure.md`; il giudizio è tuo: leggi i passaggi, non fidarti del solo grep.
4. **Regole ripetute da distillare.** Se la stessa istruzione compare in tre o più skill, proponi di spostarla in una regola (`rules/`, se vale per ogni compito), in un riferimento comune (come `clean-code/references/`) o in un rimando. Se è controllabile meccanicamente, proponi un hook o un permesso.
5. **Skill mai usate.** Lancia `/skill-doctor` (richiede Claude Code 2.1.252 o successivo; non c'è nelle sessioni che saltano il fetch dei feature flag): mostra costo e frequenza e segnala le skill mai invocate. Verifica prima che il comando esista nella versione in uso. Una skill mai usata non è per forza da togliere: può essere nuova, stagionale o solo manuale. Le opzioni sono tenerla, accorciarne la description, passarla a manuale (`disable-model-invocation: true`) o toglierla; l'ultima solo con l'ok dell'utente.
6. **Riferimenti rotti.** File di `references/` e `templates/` citati ma assenti, rimandi a skill che non esistono più, voci dell'indice del README senza cartella (e viceversa), file orfani non citati dal corpo.
7. **Versioni datate.** Cerca nelle skill versioni e date (`grep` di `Claude Code 2.`, "dalla 20", "verificato il"). Per ogni affermazione legata a versione o a un comportamento di Claude Code controlla ancora la documentazione ufficiale prima di proporre la modifica. I documenti prodotti con l'AI, compreso questo audit, sono un indice, non una fonte.
8. **Inbox.** Le voci aperte di `inbox.md`: per ciascuna proponi dove vanno (regola, hook, skill, agent, progetto) o che si chiudono. Lo smaltimento vero lo fa `retro`.
9. **Budget della lista delle skill.** Somma delle description rispetto al budget (`skillListingBudgetFraction`, 1% della finestra per default, 3% in Mímir). Il segnale che si è sforzato il budget è un avviso nel log di debug (`--debug`) o descrizioni mancanti in `/context`.
10. **Valida.** `claude plugin validate plugins/<plugin> --strict` e il controllo YAML del frontmatter (`validate` non rileva un YAML non valido: vedi `scrivi-skill/references/prova-skill.md`).

## Cosa produrre
Un elenco numerato di proposte, ognuna con:
- **evidenza**: file e riga, numero, output del comando (con la versione di Claude Code);
- **problema** in una riga e **proposta** concreta (testo o modifica);
- **impatto** (token risparmiati, rischio di mancata attivazione, contraddizione risolta) e **priorità**;
- se la proposta cambia comportamento o aggiunge una funzione: l'opzione consigliata, come da `rules/working-style.md`.

Chiudi con ciò che non hai potuto controllare (comando assente, file illeggibile) e con cosa hai verificato come accertato e cosa è ipotesi.

## Dopo l'ok
Applica solo le proposte approvate, secondo `scrivi-skill`: aggiorna indici del README e `CHANGELOG.md`, incrementa `version` del plugin toccato, ripeti la validazione. Poi proponi il messaggio di commit e attendi l'autorizzazione.

## Cosa non fare
- Non accorciare le description o togliere skill per risparmiare token senza provare che la skill si attiva ancora (`scrivi-skill/references/prova-skill.md`).
- Non riscrivere in blocco: il refactoring delle skill va a proposte separate, una per tema.
- Non estendere l'audit ai progetti: qui c'è Mímir, non i repo dei clienti.
- Per l'audit completo di più plugin lancia le misure per plugin, ma delega a un subagent `haiku` in sola lettura la lettura di molte skill (vedi `delega`) e controlla tu le evidenze.

## Verifica
- Ogni proposta ha un'evidenza riproducibile; nessuna si basa su una sensazione.
- Gli script di misura sono stati visti segnalare un caso con errore noto prima di fidarsi del loro esito "pulito".
- Le versioni citate sono state riverificate sulla documentazione.
- Nessun file è stato modificato prima dell'ok.

## File di supporto
- `references/misure.md`: script di misura (lunghezza delle description e validità YAML, riferimenti rotti, ricerca dei duplicati), con il caso noto per provarli. Leggilo al passo 1.
