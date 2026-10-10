---
name: refactoring
description: Refactoring sicuro in qualsiasi linguaggio. Usala quando ristrutturi, rinomini, estrai o sposti codice senza cambiarne il comportamento, o ripulisci codice legacy.
---

# Refactoring

Si applica insieme a `clean-code` (i segnali da cercare sono in `clean-code/references/smell.md`) e alla skill del linguaggio. Le convenzioni del progetto prevalgono. Per codice datato e privo di test vale anche `manutenzione-legacy`, se disponibile.

Refactoring significa cambiare la struttura **senza cambiare il comportamento osservabile**. Se cambia il comportamento, non è un refactoring: è una modifica funzionale, da tenere separata.

## Quando non farlo
- Dentro un fix o una feature: prima il cambio di comportamento, minimo; il refactoring a parte. Un diff che mischia i due non si rivede e non si annulla.
- Su codice che non devi toccare: segnala e basta (regola dello scope). Boy Scout solo sul codice che stai già modificando.
- Senza un motivo concreto: "mi piace di più così" non lo è. Il motivo è una modifica imminente che oggi è difficile, un bug che la struttura nasconde, un segnale di `smell.md` che costa davvero.
- Riformattazioni di massa, riordino di import, rename estetici su molti file: sporcano la history e `git blame`. Se servono, un commit a parte e concordato.

## Procedura
1. **Fissa l'obiettivo** in una frase: quale modifica diventa facile dopo il refactoring? Se non lo sai dire, fermati.
2. **Rete di sicurezza.** Esegui i test esistenti e verifica che passino *prima* di toccare nulla. Un test rosso in partenza rende inutile ogni verifica successiva.
   - Se la zona non è coperta, scrivi test di caratterizzazione (sotto) prima di procedere.
   - Se non puoi coprirla, riduci l'ambizione: solo mosse meccaniche garantite dallo strumento (rename, extract dell'IDE) e verifica manuale dichiarata.
3. **Passi piccoli.** Una mossa alla volta, test dopo ogni mossa. Se un test diventa rosso, annulla l'ultima mossa invece di correggere in avanti: così resta chiaro quale passo ha rotto cosa.
4. **Un refactoring per commit** `refactor`, con il codice sempre compilabile e verde a ogni commit. Il messaggio dice quale mossa e perché. Il commit si propone all'utente come da regole.
5. **Verifica finale** (sezione sotto): il comportamento è invariato.

## Test di caratterizzazione
Servono quando il codice non ha test e il comportamento attuale va preservato, anche se discutibile.
- Chiama il codice con input reali o realistici e registra l'output attuale come atteso. Non giudicare se è giusto: fissa ciò che fa oggi.
- Parti dai casi di confine e dai rami che userai: non serve coprire tutto, serve coprire ciò che stai per spostare.
- Per output grandi (report, JSON, HTML) usa snapshot o golden file, se il progetto ha già lo strumento.
- Un bug scoperto così non si corregge nel refactoring: lo segnali, e lo tratti dopo con un commit `fix` (test che lo riproduce prima).
- Marca questi test come "caratterizzazione" nel nome o in un commento: sono provvisori e potranno essere sostituiti da test sul comportamento voluto.

## Catalogo essenziale
| Mossa | Quando | Attenzione |
|---|---|---|
| Rinomina | Il nome mente o è vago | Usa lo strumento semantico (sotto), non cerca e sostituisci |
| Estrai metodo/funzione | Blocco con un nome possibile, commento che spiega il *cosa*, condizione complessa | Parametri e valori restituiti: se ne servono più di 2-3, forse il blocco è sbagliato |
| Inline | Metodo il cui corpo è chiaro quanto il nome, o indirezione inutile | Prima di eliminare un metodo pubblico, verifica i chiamanti esterni al repo |
| Estrai classe/modulo | Classe con due responsabilità, gruppi di campi usati solo da certi metodi | Sposta prima i dati, poi i metodi; tieni una delega temporanea se i chiamanti sono molti |
| Sposta metodo/campo | Il metodo usa più dati di un'altra classe che della sua (feature envy) | Controlla dipendenze circolari tra package dopo lo spostamento |
| Introduci oggetto parametro | Gruppo di argomenti che viaggia sempre insieme | Dagli un nome di dominio, non `Params` o `Context` |
| Sostituisci condizionale con polimorfismo | Stesso `switch`/`if` su un tipo ripetuto in più punti | Con un solo punto di decisione l'`if` resta più semplice: non farlo |
| Sostituisci flag con due metodi | Argomento booleano che seleziona il comportamento | Aggiorna tutti i chiamanti nello stesso commit |
| Sostituisci temporanea con query | Variabile locale che ostacola l'estrazione | Verifica che la query non abbia effetti collaterali né costi |
| Guard clause | Annidamenti profondi, `else` dopo `return` | Mantieni l'ordine di valutazione se ci sono effetti collaterali |
| Rimuovi codice morto | Nessun riferimento (anche da reflection, config, template) | Cerca nei file non di codice; la history conserva il resto |

Ogni mossa ha il suo contrario: se dopo averla fatta il codice è più difficile da leggere, annullala.

## Rinomina e spostamenti sicuri
- Preferisci gli strumenti **semantici**: rename e move dell'IDE o del language server (LSP), o gli strumenti di navigazione per simboli disponibili in sessione, se presenti. Conoscono scope e overload; grep no.
- Dopo il rename controlla ciò che lo strumento non vede: stringhe e reflection, file di configurazione, nomi in template/SQL/YAML, serializzazione (il nome di un campo può essere un contratto JSON), documentazione, API pubbliche usate da altri repo.
- Un simbolo pubblico di una libreria o di un'API non si rinomina in-place: aggiungi il nuovo nome, marca il vecchio deprecato, rimuovilo in un secondo momento.
- Prima di cancellare, cerca i riferimenti con una ricerca che non salti file (anche non di codice).

## Refactoring ampi
Quando i passi non stanno in una sessione o in un commit, il codice non deve restare rotto in mezzo. Proponi un piano all'utente prima di partire.
- **Branch by abstraction**: introduci un'interfaccia davanti al vecchio componente, sposta i chiamanti su di essa, scrivi la nuova implementazione dietro la stessa interfaccia, passa a quella nuova, poi rimuovi la vecchia. Il trunk resta sempre integrabile.
- **Strangler**: il nuovo sistema prende a poco a poco i casi d'uso del vecchio (per rotta, per funzione, per tipo di richiesta) finché il vecchio non serve più. Richiede un punto di instradamento e un modo per confrontare i risultati.
- **Parallel run**: per calcoli critici esegui vecchio e nuovo insieme, restituisci il vecchio e registra le differenze, senza dati sensibili nei log.
- **Expand/contract** per interfacce e schemi: aggiungi il nuovo, migra i chiamanti, rimuovi il vecchio, in release separate.
- Ogni fase termina con test verdi e un commit che si può rilasciare.

## Cosa NON fare
- Cambiare comportamento "già che ci sono" (messaggi, ordinamenti, arrotondamenti, gestione degli errori).
- Correggere i test per farli passare dopo una mossa: un test che si rompe è un'informazione. Cambia un test solo se verificava un dettaglio d'implementazione, e dichiaralo.
- Mescolare rename, spostamenti e riscritture nello stesso commit: git non riconosce più gli spostamenti.
- Astrarre per un caso solo (YAGNI): estrai quando c'è una seconda necessità reale.
- Refactoring su codice non verde o su un branch con test già falliti non spiegati.

## Verifica
- Test dell'intero modulo (non solo quelli della classe toccata), compilazione e linter/analisi statica del progetto, come da `clean-code`.
- Confronta il diff: ogni modifica deve essere spiegabile come una mossa del catalogo. Una riga che non lo è, probabilmente è un cambio di comportamento.
- Controlla che la superficie pubblica sia invariata (firma, nomi serializzati, query, rotte), salvo ciò che era l'obiettivo dichiarato.
- Nel resoconto: quale rete di test c'era, quali comandi hai lanciato con esito, cosa non era coperto e come l'hai verificato.
