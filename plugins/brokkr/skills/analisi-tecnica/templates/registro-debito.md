# Registro del debito e dei rischi: <sistema>

**Stato**: aperto · **Aggiornato**: gg/mm/aaaa

**Verificato su**

| Repository | Commit di `<branch>` | Percorsi | Note |
|---|---|---|---|

Tutto ciò che non va replicato, o che va deciso prima di toccare il sistema. Non è un elenco di bug da correggere: è la memoria di cosa non ripetere.

## Tassonomia
| Codice | Categoria | Cosa ci va |
|---|---|---|
| **S** | Sicurezza | autenticazione, autorizzazione, esposizione di dati, segreti, input non validati |
| **R** | Regole che non funzionano | una regola scritta che non produce effetto: chi legge il codice crede che il controllo esista |
| **D** | Dati incoerenti | dati di produzione che violano le regole del dominio (quanti, quali) |
| **A** | Accumulo e capacità | spazio, file orfani, crescita, prestazioni, contesa (lock, deadlock) |
| **X** | Architettura | accoppiamenti, transazioni che non attraversano i sistemi, duplicazioni di logica, mancanza di riconciliazione |
| **O** | Obsolescenza | versioni fuori supporto, dipendenze con vulnerabilità, tecnologie senza manutenzione |
| **N** | Conformità | obblighi normativi, privacy (GDPR), accessibilità, conservazione documentale |
| **P** | Processo ed esercizio | ambienti mancanti, procedure manuali, fix non rilasciati, assenza di test o monitoraggio |
| **M** | Funzionalità morte | codice o funzioni non più usati: perimetro da non migrare, da confermare con il cliente |

**Gravità**: **Alta** (danno economico, legale o di sicurezza, oppure blocca il rifacimento) · **Media** (errore visibile o lavoro manuale ricorrente) · **Bassa** (costo di manutenzione).

**Stato**: aperto · accettato (noto al cliente, non si corregge ora) · in correzione · risolto (resta come lezione).

## Voci
Stesse colonne per tutte le categorie, così le voci si possono confrontare e filtrare. Una sezione per categoria, in ordine di gravità.

| # | Cosa | Dove | Effetto oggi | Gravità | Per il rifacimento | Stato |
|---|---|---|---|---|---|---|
| S1 | | `file:riga` o sistema | con i numeri, se ci sono | | replicare / non replicare / decidere | |

## Come si usa
- Prima di riprodurre un comportamento del sistema attuale, controlla se è qui.
- Le voci **R** vanno decise una per una. Riprodurle fedelmente significa riprodurre il nulla; toglierle senza dirlo cambia il comportamento atteso.
- Le voci **M** sono la leva per ridurre il perimetro, e vanno confermate con il cliente. Una tabella vuota può essere una funzione morta, oppure una funzione viva che non ha ancora prodotto dati.
