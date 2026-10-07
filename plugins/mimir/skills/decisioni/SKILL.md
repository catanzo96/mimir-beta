---
name: decisioni
description: Aiuta a prendere e documentare una decisione non solo tecnica. Usala quando l'utente deve decidere, scegliere tra opzioni, priorizzare, scegliere un fornitore o l'approccio a un progetto.
when_to_use: 'Es.: "meglio A o B?", "cosa faccio prima?", "conviene…?", "aiutami a decidere", "preparami un brief per il responsabile su…".'
---

# Decisioni

Si applica insieme a `pianificazione` quando la decisione genera lavoro. Per le scelte tecniche e di architettura usa l'agent `architetto` e, se disponibile, `analisi-tecnica` (template `analisi-tecnica/templates/adr.md`). Prevalgono le procedure di governance del cliente e dell'azienda (chi approva cosa).

Scopo: arrivare a una decisione chiara, motivata e rintracciabile, con la profondità giusta rispetto a ciò che costa sbagliarla. Se l'utente chiede solo un parere, spiega e raccomanda senza produrre documenti.

## Quando non usarla
- Scelta di design o di architettura del codice: ADR e `architetto`.
- Decisione già presa che va solo comunicata: salta al punto 7.

## 1. Chiarisci la domanda
- Scrivi la decisione in una frase che finisce con un punto di domanda e ammette risposte alternative ("Quale fornitore per X?", non "Fornitore").
- Chiedi chi decide davvero: l'utente decide, propone o è solo consultato? Un parere dato a chi non decide va scritto come raccomandazione.
- Chiedi entro quando serve e cosa succede se non si decide. Spesso il ritardo è già una scelta.
- Se nella domanda serve una "e", sono due decisioni: separale.

### Quando mancano le informazioni
Se la decisione dipende da ciò che sa qualcun altro (cliente, collega, fornitore) e non si ricava da codice o documenti, prepara un questionario. Lo prepari, non lo invii: l'invio lo decide l'utente.
- Se l'utente non conosce il tema, non interrogarlo su quello: chiedigli **a chi va** (ruolo, cosa sa che noi non sappiamo) e **cosa deve tornare indietro**, come elenco concreto;
- da lì scrivi le domande, una per idea, le più importanti per prime: in asincrono spesso arriva un solo giro di risposte;
- una riga di motivo solo dove la domanda si può fraintendere;
- alla fine controlla che ogni cosa da ottenere sia coperta da almeno una domanda.

Forma e regole delle domande da inviare: template `domande` di `analisi-funzionale`, sezione "Forma da inviare", se disponibile.

## 2. Pesa la decisione
Una decisione **a porta girevole** (si torna indietro a basso costo) si prende in fretta, con poca analisi e un punto di revisione. Una **a porta chiusa** (contratti, assunzioni, impegni al cliente, migrazioni di dati, scelte di piattaforma) merita più profondità, più prospettive e un decisore esplicito.

Domande per classificare: quanto costa tornare indietro, in tempo, denaro e credibilità? Chi altro ne è toccato? Quanto durano gli effetti?

Il metodo scala così:
| Tipo | Cosa produrre |
|---|---|
| Porta girevole | Una riga nel registro: scelta, motivo, data di revisione |
| Intermedia | Opzioni, criteri, raccomandazione, registro |
| Porta chiusa | Tutti i passi, almeno un giro di prospettive, conferma esplicita del decisore |

## 3. Criteri e pesi
- Ricava 3-6 criteri da ciò che conta davvero (costo, tempi, rischio, competenze, vincoli contrattuali o normativi, impatto sul cliente).
- Distingui i **vincoli** (eliminano un'opzione) dai **criteri** (la fanno preferire).
- Assegna i pesi **prima** di guardare le opzioni, altrimenti li aggiusti per far vincere quella che preferisci. Se due criteri si contraddicono, fai scegliere all'utente.

## 4. Opzioni
- Da 2 a 4, sempre compresa **non fare nulla** (o rimandare): è il termine di paragone onesto.
- Cerca anche l'opzione "ibrida" o a fasi (provare in piccolo prima), che spesso trasforma una porta chiusa in girevole.
- Per ogni opzione: pro, contro, rischi, costo e tempo, **costo di tornare indietro**.
- Distingui fatti verificati da stime e ipotesi (come in `rules/working-style.md`): un costo stimato va marcato come tale, un prezzo di listino va confrontato con la fonte.

## 5. Prospettive
Per le decisioni intermedie e a porta chiusa fai almeno un giro critico prima di raccomandare:
- **Avvocato del diavolo**: argomenta contro l'opzione favorita come se dovessi farla fallire. Cosa deve essere vero perché sia una scelta sbagliata?
- **Pre-mortem**: tra un anno la scelta si è rivelata un errore; perché?
- **Punti di vista**: cliente, chi esegue, chi paga, chi manutiene dopo.

Quando il contesto è grosso o le posizioni vanno tenute separate, delega a subagent (uno per prospettiva, a contesto pulito) e fai riportare un resoconto breve con le obiezioni. Il dettaglio sta in [references/prospettive.md](references/prospettive.md): leggilo quando devi condurre il giro.

## 6. Raccomanda
- Una raccomandazione sola, motivata con i criteri del punto 3, con ciò che la farebbe cambiare ("se X si rivela falso, passa all'opzione B").
- Dichiara dubbi e dati mancanti. Non nascondere un'incertezza dietro un punteggio: i pesi numerici aiutano a ragionare, non sostituiscono il giudizio.
- La decisione resta dell'utente o di chi ha l'autorità: presenta, non anticipare.

### Brief da inoltrare (1-3-1)
Quando la proposta va girata a chi decide (responsabile, cliente, direzione), riducila a una pagina: **un** problema in una frase, sul cosa e non sul come; **tre** opzioni, cioè le più diverse tra quelle del punto 4 (non varianti della stessa), con pro e contro; **una** raccomandazione con il motivo. "Non fare nulla" resta tra le tre, oppure scrivi in una riga perché è escluso; se le opzioni davvero diverse sono solo due, presentane due invece di inventarne una. Sotto, legati alla raccomandazione: criteri per dire che è fatta e primi passi. Se il decisore sceglie un'altra opzione, riscrivi criteri e passi per quella. Il brief lo prepari tu, l'invio lo decide l'utente. Template in [templates/registro-decisioni.md](templates/registro-decisioni.md).

## 7. Registra e comunica
- Appena presa, proponi di registrare la decisione ([templates/registro-decisioni.md](templates/registro-decisioni.md)): data, decisione, motivo, chi, alternative scartate, data di revisione. Senza il motivo, tra sei mesi nessuno sa se vale ancora. Dove salvarlo lo proponi tu e lo decide l'utente: mai nei repo dei clienti senza ok.
- Per le decisioni tecniche rilevanti usa l'ADR al posto della riga di registro e rimanda dal registro.
- Comunica a chi è toccato: cosa è deciso, perché, cosa cambia per loro, da quando, a chi rivolgersi. Per il cliente usa un testo breve con le virgolette dritte "…". Il testo lo prepari tu, l'invio lo decide l'utente.
- Fissa la revisione: se cambia un presupposto o scade la data, la decisione si riapre. Una decisione superata si marca come tale, non si cancella.

## Verifica
- La domanda ammette risposte alternative e il decisore è nominato per ruolo.
- Porta girevole o chiusa dichiarato, con la motivazione, e la profondità è coerente.
- Ci sono "non fare nulla" e il costo di tornare indietro per ogni opzione.
- I pesi sono stati fissati prima del confronto; fatti e ipotesi sono separati.
- Almeno un'obiezione seria è riportata, con la risposta data.
- Nel registro: data, decisione, motivo, decisore, revisione. Nessun dato personale o del cliente nei file di metodo.

## File di supporto
- [references/prospettive.md](references/prospettive.md): conduzione di avvocato del diavolo, pre-mortem e subagent. Leggilo per le decisioni a porta chiusa.
- [templates/registro-decisioni.md](templates/registro-decisioni.md): registro, scheda di decisione intermedia e brief 1-3-1 da inoltrare.
