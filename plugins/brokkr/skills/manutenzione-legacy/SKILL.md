---
name: manutenzione-legacy
description: Modifiche sicure su codice datato. Usala quando il progetto ha versioni vecchie (Java 6/8, Spring Boot 1.x/2.x, Angular fino alla 13, AngularJS, Ant, Node datati) o non ha una rete di test. Prevale sulle skill di linguaggio e framework.
when_to_use: 'Es.: "devo toccare questo codice vecchio", "non ci sono test", "aggiorna questa libreria su Java 8". Vale anche per un fix piccolo.'
---

# Manutenzione legacy

Obiettivo: **cambiare solo ciò che serve, senza rompere ciò che funziona**, su codice che non ha una rete di sicurezza.

Precedenza: le skill `java`, `spring-boot`, `typescript` e `angular` descrivono lo stato dell'arte. **Su un progetto legacy vale questa skill**: si scrive codice compatibile con le versioni del progetto, nello stile del codice circostante.

## 1. Prima di toccare: le versioni reali
Ricava le versioni da manifest e configurazione, non dal codice che "sembra":

| Cosa | Dove |
|---|---|
| Java | `maven.compiler.source/target`, `<release>`, `sourceCompatibility`, `build.xml` |
| Spring Boot / Spring | parent o BOM nel `pom.xml`, `build.gradle` |
| Node | `engines` in `package.json`, `.nvmrc`, immagine nel Jenkinsfile o nel Dockerfile |
| Angular, TypeScript, RxJS | `package.json` (versioni installate: `package-lock.json`) |
| Encoding e fine riga | `.editorconfig`, `.gitattributes`, `file -i <file>` sui file da modificare |

Usa il runtime giusto per build e test (es. `nvm use`, un JDK specifico). Mai aggiornare il runtime o le dipendenze come effetto collaterale di un fix.

## 2. Sintassi e API da non usare
**Java**
| Non disponibile prima di | Cosa |
|---|---|
| 7 | try-with-resources, diamond `<>`, multi-catch, switch su stringhe |
| 8 | lambda, stream, `Optional`, `java.time`, metodi default |
| 9-11 | `List.of`, `var`, `Optional.isEmpty` |
| 14-17 | switch expression, text block, `record`, pattern matching |

Spring Boot fino alla 2.x usa `javax.*`, non `jakarta.*`. Con Java 6 o 7 i test JUnit sono spesso alla versione 4.

**TypeScript e Angular**
| Non disponibile prima di | Cosa |
|---|---|
| TypeScript 3.7 | optional chaining `?.`, nullish coalescing `??` |
| TypeScript 3.8 | `import type`, campi privati `#` |
| Angular 14 | `inject()`, typed forms, componenti standalone |
| Angular 16-17 | signals, `input()`/`output()`, `takeUntilDestroyed`, control flow `@if`/`@for` |

Con RxJS 6 si usano gli operatori con `pipe()`; per chiudere le subscription, `takeUntil(this.destroy$)` con un `Subject` completato in `ngOnDestroy`.

## 3. Diff minimo
- Tocca solo le righe necessarie. **Niente reformat**, niente riordino degli import, niente rinomina "già che ci sono": sporcano il diff e nascondono il fix.
- Stile del codice circostante, anche se non è quello delle skill moderne. Per ricavarlo:
  - scegli 2-3 file **esemplari** vicini a quello da modificare (stesso modulo, stesso tipo: DAO, controller, servizio) e osserva come gestiscono errori, log, nomi, ordine dei membri, utility;
  - prima di scrivere, dichiara in una riga quale esemplare segui;
  - se nel progetto convivono due stili quasi alla pari, chiedi quale usare invece di scegliere tu; uno stile raro segue quello prevalente;
  - non copiare i difetti dell'esemplare (eccezioni inghiottite, query concatenate): segnalali.
- Miglioramenti fuori perimetro: segnalali o proponili in un commit `refactor` separato.
- Niente nuove dipendenze. Se proprio servono, compatibili con le versioni del progetto e con l'ok dell'utente.
- Per ripristinare le dipendenze usa `npm ci`, non `npm install`, e non modificare il lockfile senza motivo.

## 4. Encoding e fine riga
- **Prima di modificare un file, controllane l'encoding** (`file -i`). Molti progetti legacy hanno file ISO-8859-1 o Windows-1252. Salvarli in UTF-8 corrompe le lettere accentate e genera un diff su tutto il file.
- Se un file non è UTF-8, modificalo in modo che l'encoding resti quello originale (es. `iconv` avanti e indietro, oppure `sed` sui soli byte ASCII), poi verifica con `git diff` che siano cambiate solo le righe volute.
- Mantieni i fine riga originali (CRLF o LF).

## 5. Capire prima di cambiare
- Trova tutti i chiamanti del codice che modifichi (`git grep -a`), comprese le chiamate via riflessione, XML, configurazione e template.
- Leggi la storia: `git log -L <inizio>,<fine>:<file>` e `git blame` spiegano perché una stranezza esiste. Spesso è un vecchio fix.
- Classi enormi: isola il punto da cambiare. Non spezzare la classe dentro un fix.
- **Rimuovere codice che sembra morto**: solo se è nel perimetro, altrimenti segnalalo.
  - Classifica prima:
    - *sicuro*: privato, senza riferimenti;
    - *cautela*: pubblico ma senza chiamanti trovati;
    - *rischioso*: raggiungibile per nome (riflessione, XML Spring, `web.xml`, template, stringhe, job schedulati, altri repo che lo usano come libreria).
  - Cerca i riferimenti anche come stringa e nei file non Java (`git grep -a -i`).
  - Togli un blocco per volta e verifica dopo ciascuno. Nel dubbio resta *rischioso*: si segnala, non si rimuove.

## 6. Verificare senza test
In ordine di preferenza:
1. **Test di caratterizzazione**: prima della modifica, un test che fotografa il comportamento attuale; poi la modifica. Se il progetto ha un minimo di infrastruttura di test, è la strada migliore.
   - Copri il caso normale, i bordi (vuoto, zero, massimo, date a cavallo) e un errore. Fotografa anche i comportamenti strani: si correggono in un altro passo, se richiesto.
   - Per isolare il codice cerca il punto di aggancio più piccolo: un costruttore che accetta la dipendenza, un metodo `protected` da sovrascrivere nel test, una factory. Non introdurre un'architettura nuova per poter testare.
2. **Confronto PRIMA/DOPO**: lo stesso input, gli stessi output confrontati (risposta API, file generato, esito di una query).
3. **Build e controlli statici**: compilazione, lint, type check, con il runtime del progetto. Se il build ufficiale non gira in locale e ricostruisci un controllo a mano (classpath, sourcepath, stub), usa le **versioni esatte** del progetto e non le più recenti in cache, passa come file espliciti quelli che servono ai processori di annotazioni (Lombok non elabora i file letti dal sourcepath) e prima di fidarti verifica che il controllo segnali un errore noto.
4. **Scenario manuale**: passi precisi da far eseguire all'utente, con l'esito atteso, in un ambiente non di produzione.

Dichiara sempre quale livello di verifica hai raggiunto. Un "compila" non è un "funziona".

## 7. Documentazione del progetto
Se il `CLAUDE.md` del progetto contiene indicazioni false (es. `npm test` indicato come funzionante mentre non lo è), segnalalo e proponi la correzione. La prossima sessione partirebbe da un'informazione sbagliata.
