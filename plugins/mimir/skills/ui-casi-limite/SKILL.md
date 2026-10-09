---
name: ui-casi-limite
description: Mettere alla prova una UI con i dati peggiori plausibili. Usala quando una schermata, una tabella, una card o un form deve reggere dati reali, prima di consegnarla, o quando qualcosa si rompe con certi dati.
when_to_use: 'Es.: "regge i nomi lunghi?", "provala con dati veri", "con tanti record si rompe", "va a capo male", "controlla i casi limite della tabella".'
---

# Casi limite delle interfacce

Si applica insieme a `design-ui` e alla skill del framework. Le correzioni seguono convenzioni e token del progetto.

I dati di esempio sono scelti, quasi sempre senza accorgersene, perché il design venga bene: nomi corti, conteggi tondi, campi facoltativi tutti compilati. Qui si smonta quella scelta un campo alla volta.

Due errori da evitare:
- **dati assurdi**: "aaaaaaa" o un nome di 5000 caratteri non provano niente e chi ha disegnato il componente smette di ascoltare. Ogni valore deve essere plausibile o venire dal limite reale dello schema;
- **fermarsi al testo lungo**: i guasti che arrivano in produzione sono spesso altri: il nome di due lettere, l'avatar mancante, "1 elementi", la lista vuota, l'etichetta tradotta.

## Procedura

### 1. Mappa i valori
Per ogni valore che il componente mostra: campo, sorgente, tipo, limite, facoltativo sì o no. Includi quelli che si dimenticano: conteggi nelle intestazioni, date relative, testi di badge e stati, etichette di bottoni che vengono dai dati, tooltip, immagini, la lunghezza della lista stessa.

Cerca i limiti nella validazione (schema del form, DTO con annotazioni), nelle migrazioni del database, nel contratto dell'API, negli attributi `maxlength`. Se frontend e backend non concordano (50 caratteri nel form, 255 nella colonna), è già un risultato: i dati più lunghi arriveranno da un'importazione o da un'altra applicazione. Un campo senza limite è un risultato anche lui.

Finito quando ogni valore mostrato ha una sorgente e un limite, o "illimitato".

### 2. Costruisci i dati peggiori
Prendi i valori da `references/catalogo.md`. Prepara **un solo** insieme di dati peggiori accanto a quelli di esempio, con la stessa forma e le stesse convenzioni, e distribuisci i guasti sulle prime righe (prima riga nome lungo, seconda email lunga, terza nome di due lettere): è ciò che si vede sullo schermo, ed è così che sono i dati veri.

Prepara anche gli stati che non stanno in un insieme solo: **vuoto** (nessun elemento, nessun risultato), **uno** (un elemento, ogni conteggio a 1), **tanti** (il limite realistico, 1000+ righe se la lista non è paginata: è anche un problema di prestazioni).

I dati entrano dallo stesso confine di quelli di esempio: fixture, mock, props, stub dell'API. Mai modificare markup o CSS per provocare il guasto: proveresti la tua modifica, non il componente.

### 3. Rendilo commutabile
Un selettore solo in sviluppo (parametro nell'URL come `?dati=peggiori`, una route di prova o una storia di Storybook se il progetto lo usa) con le posizioni esempio, peggiori, vuoto, uno, tanti. Il selettore non arriva mai in produzione. Senza un progetto, un file HTML autonomo con il componente e i dati.

### 4. Rompilo
Guarda ogni stato:
- alla **larghezza reale** del contenitore (una lista in una colonna laterale non è una lista a tutta pagina), poi a 320px e alla larghezza massima supportata;
- con lo **zoom al 200%**: il testo cresce, i contenitori no;
- in **tema scuro** e con **`dir="rtl"`** se il prodotto li supporta.

Se hai uno strumento per gli screenshot, confronta gli stati a ogni larghezza. Altrimenti ragiona dal CSS e dichiara cosa hai visto e cosa hai dedotto. Le firme dei guasti tipici, con causa e correzione, sono in `references/catalogo.md`.

Per ogni stringa lunga scegli campo per campo:
- **a capo** per ciò che serve intero a riconoscere qualcosa (nomi, titoli in un dettaglio);
- **troncare alla fine** per metadati secondari dove conta l'inizio, sempre con un modo per leggere il valore intero;
- **troncare in mezzo** quando gli elementi differiscono alla fine (nomi di file, percorsi, codici);
- **limitare a N righe** nelle anteprime delle card, così le altezze restano prevedibili;
- **mai troncare** numeri, importi, date e ciò che l'utente confronta.

### 5. Riporta e fermati
1. **Cosa si rompe**, dal più grave: una riga per guasto con gravità, campo, valore, effetto, correzione e `file:riga`. Gravità: **rotto** (contenuto illeggibile, azione irraggiungibile, dato sbagliato), **brutto** (leggibile ma visibilmente sbagliato), **fragile** (oggi regge, un passo realistico lo rompe: nessun limite, nessun ripiego).
2. **Decisioni per l'utente**: i guasti con più risposte giuste (troncare o andare a capo, cosa mostrare se manca il ruolo, paginare o virtualizzare), con la tua raccomandazione.
3. **Cosa ha retto**: dimostra che la prova era vera e dice cosa non toccare.

Correggi solo ciò che l'utente indica. Le correzioni che cambiano un comportamento (un limite nuovo nello schema, la paginazione) sono proposte, non modifiche.

### 6. Dopo le correzioni
Ripassa tutti gli stati, anche quello di esempio: una correzione per il caso peggiore non deve peggiorare quello normale. Tieni i dati peggiori come prova di regressione, salvo diversa indicazione.

## Verifica
- Ogni valore mostrato è nella mappa con sorgente e limite.
- Ogni riga applicabile del catalogo è stata provata, a ogni larghezza e ambiente richiesto.
- Ogni guasto ha valore, causa, correzione e posizione.
- Nel resoconto è separato ciò che hai visto (screenshot, browser) da ciò che hai dedotto dal codice.

## File di supporto
- `references/catalogo.md`: valori peggiori plausibili per tipo di dato (anche italiani: codici fiscali, ragioni sociali, indirizzi, importi) e firme dei guasti con causa e correzione. Leggilo al passo 2.
