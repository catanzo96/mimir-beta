# Prestazioni

Si guardano quando una modifica aggiunge o cambia query, filtri, cicli su dati,
chiamate di rete, paginazione o lavoro eseguito a ogni interazione dell'utente.

## Domande
- Quante chiamate o query parte per ogni azione dell'utente (tasto, scroll, salvataggio)?
  Una chiamata in più per pagina è diversa da una per riga (N+1).
- Su quante righe lavora davvero? Conta sui dati reali, non sulla stima del catalogo.
- I filtri e gli ordinamenti usano un indice? Con un ORM o un low-code, l'indice
  si dichiara dove lo gestisce lo strumento, non a mano sul DB.
- Si caricano dati per poi scartarli? Un filtro applicato dal client dopo la
  paginazione può lasciare pagine quasi vuote e nascondere risultati.
- Le chiamate ripetute (digitazione, scroll) sono contenute: debounce, annullamento
  della richiesta precedente, cache delle risposte stabili?

## Misura
Un giudizio sulle prestazioni ("è veloce", "è lento", "l'indice serve") vale solo
con una misura: piano di esecuzione, tempi, numero di chiamate osservato. Senza misura
è un'ipotesi e si dichiara come tale, con la misura che la chiuderebbe.
Una tabella piccola non giustifica un indice per precauzione; una chiamata in più
per interazione si accetta solo dopo averla contata.
