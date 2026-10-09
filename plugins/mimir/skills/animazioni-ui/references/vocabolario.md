# Vocabolario delle animazioni

Per tradurre una descrizione vaga ("quella cosa che si allarga dal bottone") nel termine giusto, così che la richiesta e l'implementazione parlino della stessa cosa. Rispondi con il termine, una riga di definizione e, se serve, il termine vicino con cui non confonderlo. I termini restano in inglese quando è così che si cercano nella documentazione.

## Entrate e uscite
- **Fade**: comparsa o scomparsa solo con l'opacità.
- **Scale in**: comparsa da poco più piccolo (0.95) con dissolvenza. Diverso da **pop**, che supera la dimensione finale e torna indietro.
- **Slide in**: entrata da un lato con traslazione.
- **Reveal**: il contenuto si scopre con una maschera (`clip-path`) invece di muoversi. Diverso da **mask**, che usa un'immagine o un gradiente come maschera e può avere bordi sfumati.
- **Origin-aware**: l'elemento cresce dal punto da cui è stato aperto.

## Sequenze
- **Stagger**: elementi di un gruppo che partono a pochi millisecondi di distanza.
- **Choreography**: più elementi con ruoli e tempi diversi in un'unica transizione.
- **Shared element / morph**: lo stesso elemento passa da una posizione o forma all'altra tra due viste (in CSS: View Transitions).
- **Crossfade**: un contenuto sfuma mentre l'altro appare nello stesso posto.

## Stato e feedback
- **Press feedback**: leggera riduzione alla pressione.
- **Shake**: oscillazione orizzontale breve per un errore. Usala con parsimonia e mai come unico segnale.
- **Skeleton**: segnaposto con la forma del contenuto durante il caricamento; **shimmer** è il riflesso che lo attraversa.
- **Optimistic update**: l'interfaccia mostra subito l'esito e lo corregge se il server rifiuta.
- **Number ticker**: un numero che scorre fino al nuovo valore.

## Scorrimento
- **Scroll reveal**: comparsa quando l'elemento entra nella vista.
- **Scroll-driven**: animazione legata alla posizione dello scorrimento, non al tempo.
- **Parallax**: livelli che scorrono a velocità diverse.
- **Sticky / pinned**: un elemento resta fermo mentre il resto scorre. **Stacking cards**: sezioni che si impilano scorrendo.
- **Scroll snap**: lo scorrimento si aggancia a punti precisi.

## Gesti
- **Drag to dismiss / swipe to dismiss**: chiudere trascinando o con un colpo rapido.
- **Rubber band**: resistenza crescente oltre il bordo.
- **Momentum / inertia**: l'elemento continua dopo il rilascio e rallenta.
- **Snap points**: posizioni di arrivo a cui un pannello si aggancia.

## Curve e fisica
- **Easing**: la curva che distribuisce il movimento nel tempo (ease-out, ease-in-out, linear).
- **Spring**: movimento governato da una molla, senza durata fissa; **damping** è lo smorzamento, **bounce** il rimbalzo.
- **Overshoot**: superare la destinazione e tornare.
- **Anticipation**: piccolo movimento opposto prima di quello principale. **Follow-through**: parti che si assestano dopo l'arresto.

## Ambiente
- **Loop / ambient**: movimento continuo di sfondo. Raro nell'interfaccia, sempre spento con il movimento ridotto.
- **Marquee**: testo o loghi che scorrono senza fine.
- **Hover lift**: un elemento si alza leggermente al passaggio del puntatore.
