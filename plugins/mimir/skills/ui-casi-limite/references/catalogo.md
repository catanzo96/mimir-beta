# Catalogo dei casi limite

Valori plausibili che rompono le interfacce, per tipo di dato. Scegli quelli che il componente mostra davvero e mescolali tra le righe. Dove lo schema ha un limite, usa il limite esatto.

## Persone
| Caso | Esempio | Cosa rompe |
|---|---|---|
| Nome e cognome lunghi | Maria Addolorata Benedetta Sant'Ambrogio Della Rovere | Righe, card, intestazioni |
| Nome cortissimo | Jo Li | Iniziali, allineamenti pensati per testo lungo |
| Apostrofi e particelle | D'Alessandro, De' Medici, dell'Orto | Ordinamento, iniziali, escape |
| Accenti e diacritici | Niccolò Šimić, Zoë Łukasiewicz | Font senza glifi, maiuscole, confronti |
| Più parole nel cognome, suffissi | García Márquez, Henry Ford III | Iniziali, divisione nome e cognome |
| Alfabeti non latini | 王小明, Алексей Смирнов, محمد | Font di ripiego, altezza di riga |
| Emoji o lettera composta in testa | 🌟 Martina, nome con emoji di famiglia | Iniziali calcolate per carattere invece che per grafema |
| Campo facoltativo assente | nessun ruolo, nessun telefono, nessuna foto | Righe vuote, trattini orfani, spazi riservati a vuoto |

## Aziende e indirizzi
| Caso | Esempio |
|---|---|
| Ragione sociale lunga | Società Cooperativa Agricola Produttori Ortofrutticoli della Piana del Sele S.c.a.r.l. |
| Sigle e punteggiatura | F.lli Rossi & C. S.n.c. |
| Indirizzo lungo | Via Lungotevere dei Vallati, 2/B, scala C, interno 14 |
| Località composte | San Giovanni in Fiore, Reggio nell'Emilia, Castelnuovo di Garfagnana |
| Estero | indirizzo senza CAP, CAP alfanumerico, provincia assente |

## Identificativi
| Caso | Esempio | Cosa rompe |
|---|---|---|
| Email lunga senza spazi | amministrazione.contabilita@cooperativa-produttori-agricoli-piana.example.it | Nessun punto di a capo: esce dal contenitore |
| URL lungo | percorso con parametri di 200 caratteri | Come sopra |
| Codice fiscale, partita IVA, IBAN | IT60X0542811101000000123456 | Troncamento che rende i codici indistinguibili; servono cifre a spaziatura fissa |
| UUID, hash | 3f2b9c1e-…-a7d4 | Troncare in mezzo, non alla fine |
| Nomi di file | Verbale_riunione_comitato_tecnico_2026-10-09_v12_definitivo_DAVVERO.pdf | La differenza è alla fine |

## Numeri e importi
| Caso | Esempio | Cosa rompe |
|---|---|---|
| Importi grandi | 1.234.567.890,12 € | Colonne strette, allineamento |
| Negativi | −1.250,00 € | Segno, colore come unico segnale |
| Zero e assenza | 0, nessun valore, `null` | "0" e "—" non sono la stessa cosa |
| Decimali sporchi | 0,1 + 0,2 | 0,30000000000000004 mostrato così |
| Formato locale | 1.234,5 contro 1,234.5 | Separatori sbagliati, parsing dell'input |
| Percentuali estreme | 0,01%, 100%, 1.250% | Barre che escono dal contenitore |
| Conteggi | 0, 1, 2, 1.000, 1.000.000 | Plurali ("1 elementi"), badge che si allargano |

## Testo libero
| Caso | Esempio |
|---|---|
| Parola lunghissima | precipitevolissimevolmente, codici e composti tedeschi |
| Testo con a capo e spazi multipli | note incollate da una mail |
| Markup e caratteri speciali | `<b>`, `&amp;`, `**grassetto**`, virgolette tipografiche |
| Etichette tradotte | "Salva" diventa "Speichern und schließen" |
| Testo lunghissimo | descrizione di 4000 caratteri dove ci si aspettano due righe |

## Collezioni
| Caso | Cosa rompe |
|---|---|
| Vuota | Stato vuoto mancante, intestazioni orfane |
| Un elemento | Plurali, layout pensati per una griglia |
| Molti elementi (1000+) | Prestazioni, scorrimento, paginazione assente |
| Molti tag o badge su un elemento | A capo, altezza della riga |
| Elementi annidati profondi | Rientri che escono dal contenitore |

## Tempo
| Caso | Esempio |
|---|---|
| Date relative ai limiti | "adesso", "1 minuto fa", "ieri" a mezzanotte, "tra 3 giorni" |
| Fusi orari e ora legale | evento alle 02:30 dell'ultima domenica di marzo |
| Date molto lontane | 1900, 2099, data di nascita prima del 1970 |
| Durate lunghe | 1.234 ore, 3 anni e 2 mesi |

## Immagini e media
| Caso | Cosa rompe |
|---|---|
| Immagine assente o che non si carica | Icona dell'immagine rotta, spazio vuoto |
| Proporzioni estreme | Foto molto larga o molto alta |
| Immagine pesante | Caricamento lento, salti di layout |
| Trasparenza | Logo nero trasparente su tema scuro |

## Stati e ambiente
- Caricamento lento, errore del server, errore di rete, permessi mancanti, sessione scaduta a metà.
- Zoom al 200%, corpo del testo aumentato dal sistema.
- Tema scuro, contrasto elevato, scrittura da destra a sinistra.
- Larghezza 320px, schermo molto largo, tastiera virtuale aperta.

## Firme dei guasti
| Cosa vedi | Causa | Correzione |
|---|---|---|
| Avatar o icona schiacciati in un ovale | L'elemento flex si restringe | `flex-shrink: 0` su avatar, icone e riquadri a dimensione fissa |
| Testo che esce invece di andare a capo o troncarsi | Figlio di flex o grid con `min-width: auto` | `min-width: 0` sulla colonna di testo; `minmax(0, 1fr)` in grid |
| Email o URL fuori dal bordo | Nessun punto di a capo nella stringa | `overflow-wrap: anywhere` sull'elemento |
| Azione finale (menu, bottone) spinta fuori o tagliata | Il contenuto centrale prende tutto lo spazio | `min-width: 0` al centro, `flex-shrink: 0` sull'azione |
| Badge su due righe | Il badge può restringersi | `white-space: nowrap` e `flex-shrink: 0`; decidi cosa cede al suo posto |
| Avatar centrato accanto a un nome su tre righe | `align-items: center` con righe di altezza variabile | Allineamento in alto quando il testo può andare a capo |
| Ultima riga tagliata a metà | Contenitore ad altezza fissa senza indizio di scorrimento | Barra di scorrimento visibile o sfumatura; `overflow` voluto |
| Parola spezzata a caso in un titolo | `word-break: break-all` | `overflow-wrap: anywhere`, che spezza solo quando serve |
| Iniziali sbagliate o carattere rotto | Prima lettera presa per indice | Iniziali per grafema (`Intl.Segmenter`), prima e ultima parola, icona di ripiego |
| Trattino o riga vuota al posto di un campo assente | Segnaposto per un facoltativo mancante | Ometti la riga o riserva lo spazio di proposito |
| "1 elementi", "0 elemento" | Plurale scritto a mano | `Intl.PluralRules` o stringhe distinte per conteggio |
| Numeri che ballano aggiornandosi, colonne storte | Cifre proporzionali | `font-variant-numeric: tabular-nums` |
| `1234`, `NaN`, `undefined`, decimali infiniti | Numero mostrato grezzo | `Intl.NumberFormat` con la lingua dell'utente; controllo del valore assente |
| Etichetta tradotta che esce dal bottone | Bottone a larghezza fissa | Larghezza dal contenuto con `min-width` |
| Accenti o scritture alte tagliati sopra o sotto | `line-height` stretta con `overflow: hidden` | Interlinea più ampia, niente ritaglio sui testi |
| Icona dell'immagine rotta | Nessun ripiego in caso di errore | Iniziali o segnaposto; `object-fit: cover` |
| Testo troncato che non si può leggere | Solo `text-overflow: ellipsis` | Tooltip o `title` e il valore intero in un dettaglio |
| Scorrimento di 1000 righe a scatti | Tutte le righe nel DOM | Virtualizzazione o paginazione, dichiarando quale |
| Markup mostrato come testo, o testo interpretato come markup | Escape al livello sbagliato | Escape una volta, al rendering; mai HTML grezzo da dati dell'utente |
