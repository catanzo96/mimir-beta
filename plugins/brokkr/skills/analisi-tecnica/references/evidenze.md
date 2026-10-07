# Metodo delle evidenze

Vale per ogni documento di analisi, funzionale o tecnico.

## Verificato ≠ plausibile
Ogni documento separa due cose:
- **Cosa abbiamo accertato**: fatti verificati alla fonte, con il *come* (file, query, ambiente, data).
- **Ipotesi e domande aperte**: tutto il resto.

Nulla passa dalla seconda alla prima senza una verifica esplicita. Un'ipotesi scambiata per un fatto costa poco oggi e molto quando qualcuno ci costruisce sopra.

## Cosa conta come verifica
| Affermazione | Verifica accettabile |
|---|---|
| Esiste una tabella, colonna o campo | catalogo del DB (`information_schema` o equivalente) sull'ambiente indicato, con data |
| Il sistema si comporta così | il punto del codice che lo produce, citato `file:riga` |
| Un valore vale X | la query che lo restituisce, e l'ambiente su cui è girata |
| Una regola di business è questa | il codice **e** il documento normativo o funzionale che la impone |
| Un flusso esce verso l'esterno | il tracciato reale, non la sua descrizione |

- **Modello o configurazione dichiarata ≠ stato reale.** Il modello dice com'è stato disegnato il sistema, il DB o l'ambiente dice com'è. Quando divergono, la divergenza va annotata: è essa stessa un'informazione.
- **I documenti prodotti con l'AI sono un indice, non una fonte.** Nomi plausibili ma inesistenti sono l'errore più frequente. Vale anche per i documenti prodotti da noi.
- **I nomi sono indizi, non prove.** Un campo `stato = 0` può voler dire "non bloccato".

## Da quale versione si legge
- Il riferimento è il **branch che va in produzione** (di norma `master` o `main`). La copia di lavoro può essere su un branch di feature.
- Leggi il codice da lì: `git show origin/<branch>:<percorso>`, `git grep <testo> origin/<branch> -- <percorso>`.
- Ogni documento che cita codice apre con la tabella **Verificato su**:

  | Repository | Commit di `<branch>` | Percorsi | Note |
  |---|---|---|---|

  Quando rileggi su un commit più recente, aggiorna il commit e scrivi nella nota **cosa è cambiato**, anche se è "niente".

## Regole di scrittura
- **Percorsi e righe reali** (`modulo/.../Servizio.java:276`), non descrizioni approssimative.
- **Query eseguibili**, con l'ambiente su cui sono state provate.
- **Date per esteso** (`23/09/2026`). Dove conta, scrivi **quando** hai verificato qualcosa: i fatti invecchiano senza avvisare.
- **Niente dati personali di persone fisiche.** I dati tecnici (schemi, tabelle, host, codici pratica) sì.
- **Non riassumere il codice**: spiega cosa fa e perché, non tradurlo in prosa.

## Rettifiche
Un errore trovato in un documento non si cancella: si corregge e si lascia una nota datata.
> *Rettifica del gg/mm/aaaa.* Qui c'era "…": era sbagliato perché …; il valore corretto è …

## Accesso ai dati
- **Non eseguire query su DB condivisi o di produzione.** Preparale in un [pacchetto di query](../templates/pacchetto-query.md): sola lettura, aggregate quando possibile, con costo stimato. Le esegue l'utente e poi riporta gli esiti.
- **Confronto fra estrazioni prese in momenti diversi**: escludi la finestra fra le due, oppure dichiarala.
- **Le stime statistiche del catalogo** (righe stimate, dimensioni) non si usano per decidere: servono conteggi reali.

## Trappole degli strumenti
Aggiungi le trappole qui quando costano qualcosa.
- **`grep -I` salta in silenzio i file non UTF-8** (per esempio ISO-8859), perché li tratta come binari. **Per affermare un'assenza** usa `grep -a` o `git grep`, che non saltano i file.
- **Encoding misti**: prima di dire "non c'è", verifica quanti file del repo non sono UTF-8 (`file -i`, `iconv -f utf-8 -t utf-8`).
- **Maiuscole nei percorsi**: nei link markdown `pdf/` e `PDF/` sono percorsi diversi.
