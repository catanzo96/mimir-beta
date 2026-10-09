# Default riconoscibili e alternative

Sono le scelte a cui un modello ricorre quando nessuno ha deciso. Nessuna è vietata in assoluto: la richiesta, il brand o il design system del progetto possono giustificarla. Senza giustificazione, sostituiscila.

Usalo in due modi: mentre costruisci, per accorgerti di un riflesso; in revisione, cercando i segnali nel codice (classi, colori, struttura) oltre che a vista.

## Struttura della pagina
| Segnale | Perché stona | Alternativa |
|---|---|---|
| Riga di tre o più card identiche con icona, titolo e testo | È il contenitore pigro: tutto ha lo stesso peso | Gerarchia: un elemento principale e i secondari, elenco con divisori, griglia con celle di dimensioni diverse |
| Card dentro card | Doppia cornice senza informazione | Un solo livello di contenitore; dentro, spazio e divisori |
| Etichetta maiuscola con spaziatura larga sopra ogni titolo | Ritmo da modello, ripetuto su ogni sezione | Il titolo basta; al massimo una ogni tre sezioni, se porta un'informazione |
| Numeri di sezione decorativi ("01 / 02 / 03"), "Passo 1, Passo 2" | Enumerano ciò che si vede già | Numerare solo se l'ordine conta per chi legge; altrimenti il contenuto fa da titolo |
| Titolo grande a sinistra e paragrafo piccolo che galleggia a destra | Due messaggi in competizione | Titolo e testo uno sotto l'altro, oppure due colonne allineate con un contenuto vero a destra |
| Numero gigante con etichetta piccola e statistiche di contorno come apertura | Formula che riempie senza dire | Mostrare il dato solo se è il messaggio, con contesto (periodo, confronto) |
| Modale per modificare un campo o confermare un'azione reversibile | Interrompe senza bisogno | Modifica in linea, pannello laterale, annulla dopo l'azione |
| Sezione chiara in una pagina scura (o il contrario) | Sembra un altro sito | Un tema; varia la tonalità dentro la stessa famiglia |

## Superfici e colore
| Segnale | Alternativa |
|---|---|
| Gradiente viola o blu, bagliori colorati attorno ai bottoni | Neutri di una famiglia e un accento deciso; profondità da ombra con scostamento e sfocatura morbida |
| Testo in gradiente sui titoli | Enfasi da peso o dimensione |
| Vetro sfocato ovunque | Solo su elementi fissi sopra contenuto che scorre, con alternativa piena per `prefers-reduced-transparency` |
| Bordo laterale colorato spesso su card, avvisi, elenchi | Icona e titolo di stato, sfondo tenue, oppure bordo completo sottile |
| Ombra dura senza sfocatura fuori da un'estetica che l'ha scelta | Un sistema di profondità coerente, o nessuno |
| Bordo e ombra larga insieme sulla stessa card | Uno dei due |
| Nero puro come sfondo, grigi caldi e freddi mischiati | Quasi-nero tinto, una sola famiglia di grigi |
| Più accenti, accento sovrasaturo, un colore nuovo in fondo alla pagina | Un accento usato ovunque; i colori di stato solo per gli stati |
| Grigio neutro su sfondo colorato | Testo secondario tinto con la tinta dello sfondo |
| Righe o griglie disegnate come decorazione | Solo quando organizzano contenuto vero |

## Tipografia
| Segnale | Alternativa |
|---|---|
| Titoli enormi che gridano, quattro righe di titolo | Scala pianificata insieme alle immagini; meno parole o corpo più piccolo |
| Due soli pesi (400 e 700) | Usare anche i pesi intermedi per una gerarchia sottile |
| Parola in un altro font dentro un titolo per "dare interesse" | Corsivo o grassetto dello stesso font |
| Monospace per sembrare tecnico | Monospace per codice, identificativi e dati allineati |
| Paragrafi a tutta larghezza | 60-75 caratteri per riga |
| Parola sola sull'ultima riga di un titolo | `text-wrap: balance` sui titoli, `pretty` sui paragrafi |
| Titoli Con Tutte Le Iniziali Maiuscole | Maiuscola solo all'inizio, come si scrive in italiano |
| Numeri proporzionali in tabelle e prezzi | Cifre tabulari |

## Componenti e icone
| Segnale | Alternativa |
|---|---|
| Sempre un bottone pieno più uno fantasma | Gerarchia a tre livelli: primario, secondario, link |
| Due bottoni con lo stesso intento ed etichette diverse ("Contattaci", "Parliamone") | Un'etichetta per intento, ovunque nella pagina |
| Bottone che va a capo su desktop | Etichetta più corta o bottone più largo |
| Spinner circolare per il caricamento di un'area | Scheletro con la forma del contenuto |
| Pallini colorati prima di ogni voce | Solo per uno stato reale (online, in errore) |
| Pillole ed etichette sopra le foto | Didascalia sotto, o nessuna |
| Emoji o caratteri Unicode come icone | Una libreria di icone, un solo spessore di tratto |
| Metafore scontate (razzo per "lancia", scudo per "sicurezza") | Icone che descrivono l'azione |
| SVG illustrativi disegnati a mano | Illustrazioni vere, foto, o niente; SVG va bene per geometria e diagrammi |
| Schermata di prodotto finta fatta di `div` | Screenshot reale, il componente vero in miniatura, o niente |
| Selezione, scrollbar e focus con i default del browser | Presi dalla palette |
| Cursore del mouse personalizzato | Il cursore di sistema |

## Contenuti e copy
| Segnale | Alternativa |
|---|---|
| Nomi di comodo (Mario Rossi ovunque, Acme, "Nexus") | Dati di esempio plausibili e vari, dichiarati come esempio |
| Numeri finti precisi (99,9%, 4,1×, 48k utenti) | Dati veri della richiesta, o marcati come esempio |
| Verbi gonfi ("rivoluziona", "potenzia", "senza soluzione di continuità") | Il verbo concreto di cosa fa il prodotto |
| Frasi ad effetto che non dicono nulla, giochi di parole forzati | Una frase funzionale, anche se piatta |
| Micro-frasi meta sotto i titoli ("Questa lista resta corta di proposito") | Titolo e testo bastano |
| "Ops!" negli errori, punti esclamativi nei messaggi di successo | Problema e rimedio, tono calmo |
| Registri mescolati (tecnico, poetico, pubblicitario) nella stessa pagina | Un registro, quello del prodotto |
| Lorem ipsum | Bozza di testo reale |
| Indicazioni "Scorri" e frecce animate in fondo al primo schermo | Niente: chi guarda sa scorrere |
| Etichette di versione, città e meteo, contatori finti come decorazione | Solo se sono un'informazione vera per chi legge |
| Trattino lungo usato come vezzo in titoli, bottoni ed etichette | Punto, virgola, due punti o un a capo |

## Codice dell'interfaccia
| Segnale | Alternativa |
|---|---|
| `div` cliccabili, zuppa di `div` | Elementi semantici (vedi `clean-code/references/a11y.md`) |
| Colori e misure scritti a mano nei componenti | Token |
| `z-index: 9999` | Una scala di livelli dichiarata |
| `height: 100vh` per sezioni a schermo intero | `min-height: 100svh` per il primo schermo, `100dvh` per il guscio dell'app (vedi `mobile-web.md`) |
| Link a `#` e bottoni che non fanno nulla | Destinazione vera o elemento disabilitato in modo visibile |
| Import di pacchetti non presenti nel progetto | Controllo del manifest prima di importare |
