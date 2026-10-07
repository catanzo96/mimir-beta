# SSR, prerendering e sicurezza lato client

Da leggere quando il progetto usa SSR o prerendering (`@angular/ssr`, `provideClientHydration`), o quando la modifica tocca HTML dinamico, URL, token o dati sensibili nel browser.

## Codice che gira anche sul server
- Sul server non esistono `window`, `document`, `localStorage`, `navigator`. Il codice che li usa:
  - va eseguito solo nel browser: `isPlatformBrowser(inject(PLATFORM_ID))`, oppure gli hook di rendering (`afterNextRender`) per ciò che tocca il DOM dopo la visualizzazione;
  - per il documento usa il token `DOCUMENT` iniettato, non la variabile globale.
- Timer e `setInterval` avviati al bootstrap tengono il server occupato e ritardano la risposta: avviali solo nel browser.
- Lo stato trasferito dal server al client (transfer state, cache HTTP di idratazione) finisce **dentro l'HTML della pagina**: niente segreti, token o dati di altri utenti.

## HTML e URL dinamici
- Angular sanifica interpolazioni, `[innerHTML]` e gli URL nei binding (`[href]`, `[src]`). La protezione salta con `bypassSecurityTrust*`: usalo solo su contenuti generati da te, mai su input dell'utente o di sistemi esterni, con il motivo in un commento.
- Niente manipolazione diretta del DOM (`ElementRef.nativeElement.innerHTML`, `Renderer2` con HTML costruito a mano): scavalca la sanificazione.
- URL di redirect presi da parametri (`?returnUrl=`): accetta solo percorsi interni, altrimenti diventano un open redirect.

## Token e dati sensibili
- Tutto ciò che arriva al browser è leggibile: niente segreti in `environment.ts`, nei bundle o nei commenti dei template.
- I token in `localStorage` sono leggibili da qualunque script XSS. Se il backend lo consente, meglio un cookie `HttpOnly` e `Secure`. In ogni caso segui la scelta del progetto e segnala il rischio.
- Con autenticazione a cookie, la protezione CSRF di `HttpClient` (header `X-XSRF-TOKEN`) funziona solo se il backend imposta il cookie atteso: verifica che nomi e configurazione coincidano. L'header viene aggiunto solo alle richieste che modificano dati verso URL relativi (stessa origine), non alle chiamate verso altri domini.
- Niente dati personali nei log della console né nei messaggi di errore mostrati.

## Content Security Policy
- Se il progetto usa una CSP, niente script o stili inline aggiunti a mano. Angular supporta il nonce per gli stili che genera (`ngCspNonce`): segui la configurazione esistente.
