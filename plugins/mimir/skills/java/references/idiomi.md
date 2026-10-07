# Idiomi e trappole di Java

Da leggere quando il codice tocca importi, date, uguaglianza, testo o collezioni. Le versioni indicate sono le minime: nel legacy controlla quella del progetto.

## Denaro e numeri
- Importi sempre in `BigDecimal`, mai `double` o `float`.
- Costruiscilo da stringa o da `long`, non da `double`: `new BigDecimal("0.10")`, non `new BigDecimal(0.1)`.
- Confronta con `compareTo`. `equals` considera anche la scala: `1.0` e `1.00` risultano diversi.
- `divide` e `setScale` sempre con scala e `RoundingMode` espliciti: senza, un risultato periodico lancia `ArithmeticException`.
- Somme che possono superare il range: `Math.addExact` e simili lanciano un'eccezione invece di andare in overflow in silenzio.

## Date e ore
- `java.time` (8+) nel codice nuovo: `LocalDate` per le date senza ora, `Instant` per gli istanti, `ZonedDateTime` quando conta il fuso. `Date` e `Calendar` solo ai confini con il codice legacy, convertiti subito.
- Istanti salvati e scambiati in UTC. Il fuso si applica solo in presentazione.
- Il "momento attuale" si ottiene da un `Clock` iniettato, non da `now()` sparsi: così i test controllano il tempo.

## Uguaglianza
- `equals` e `hashCode` si ridefiniscono insieme, sugli stessi campi.
- Un oggetto usato come chiave di una mappa o in un `Set` non deve cambiare i campi che entrano in `hashCode`.
- Mai `==` tra `String` o tra numeri boxed: `Integer` è in cache solo tra -128 e 127, quindi `==` funziona nei test e fallisce in produzione.

## Testo
- Charset sempre esplicito (`StandardCharsets.UTF_8`, o quello del progetto) in lettura, scrittura e conversione di byte. Il default della piattaforma cambia tra macchine e versioni: da Java 18 è UTF-8.
- `toUpperCase` e `toLowerCase` su codici e chiavi con `Locale.ROOT`: con la locale turca la "i" non torna.
- Concatenazione nei cicli con `StringBuilder`. Una concatenazione singola va già bene così.
- Nei log i segnaposto (`log.debug("utente {}", id)`), non la concatenazione: evita il costo quando il livello è spento.

## Collezioni
- `List.of`, `Set.of`, `Map.of` (9+) sono immutabili e rifiutano `null`.
- `stream().toList()` (16+) è immutabile, `Collectors.toList()` no: non scambiarli se qualcuno poi modifica la lista.
- `Arrays.asList` ha dimensione fissa: `add` e `remove` lanciano un'eccezione.
- Rimozioni durante l'iterazione con `removeIf` o l'`Iterator`, non nel `for`: evita `ConcurrentModificationException`.
- `Collectors.toMap` lancia un'eccezione sulle chiavi duplicate: se possono esserci, passa la funzione di merge.

## Generics
- Niente raw type (`List` senza parametro). Un warning `unchecked` si risolve o si sopprime nel punto più piccolo possibile, con il motivo in un commento.
