# Codice a oggetti

## SOLID
- **SRP**: una classe ha un solo motivo per cambiare.
- **OCP**: estendi il comportamento aggiungendo codice, non modificando quello stabile.
- **LSP**: una sottoclasse è sostituibile alla base senza alterare la correttezza.
- **ISP**: interfacce piccole e specifiche.
- **DIP**: il codice di alto livello dipende da astrazioni, non da dettagli.

## Dipendenze
- **Injection tramite costruttore**, mai tramite campi o setter. Le dipendenze diventano esplicite, immutabili e testabili.
- **Interfacce ai confini**: porte, adapter, integrazioni esterne, punti con più implementazioni reali o previste.
  - Non servono per fare mock: una classe concreta con una sola implementazione non ha bisogno di interfaccia.
  - Se il progetto ha una convenzione diversa, segui quella.
- Niente prefisso `I` sulle interfacce, salvo i linguaggi in cui è la convenzione (C#).

## Coesione
- Pochi campi (segnale: più di circa 5, esclusi DTO ed entity), e usati da più metodi.
- Se gruppi di metodi usano sottoinsiemi diversi di campi, la classe ha più responsabilità: dividila.
- Classi di circa 200 righe al massimo, come segnale.

## Tipi che proteggono le regole
- Un buon tipo rende impossibili gli stati non validi: l'invariante si controlla nel costruttore o nella factory, non in chi lo usa.
- Niente setter che permettono di aggirare l'invariante, niente collezioni interne restituite modificabili.
- Value object per i concetti con regole (`CodiceFiscale`, `Importo`, `Intervallo`) invece di stringhe e numeri sciolti.
- Nel codice esistente si applica a ciò che si scrive di nuovo: non si convertono i tipi dentro un fix.

## Legge di Demetra e Tell, Don't Ask
- Un metodo chiama solo metodi di: se stesso, oggetti che crea, argomenti ricevuti, componenti che possiede.
- Evita le catene che attraversano la struttura interna (`lavoratore.getIndirizzo().getCitta().getCap()`).
- **Tell, Don't Ask**: di' all'oggetto cosa fare invece di chiedergli i dati e decidere al posto suo.
- **Feature envy**: un metodo che usa più dati di un'altra classe che della propria probabilmente appartiene a quella classe.
- **Eccezioni ammesse**:
  - DTO, record e modelli di persistenza, quando li si attraversa per fare mapping: navigazione ammessa;
  - le entity di *dominio* non sono contenitori di dati: espongono comportamento e seguono Tell, Don't Ask;
  - interfacce fluenti e builder;
  - DSL e API di configurazione (`query().filter().sort().limit()`);
  - stream e pipeline funzionali.

## Polimorfismo e switch
- Il **comportamento** che varia per tipo va nel polimorfismo, non in switch o if ripetuti in più punti.
- Lo switch **esaustivo** su tipi chiusi (sealed, enum) con pattern matching è idiomatico per trasformare *dati*.
- Da evitare: switch su stringhe o flag, e lo stesso switch duplicato in più punti.
- Le factory possono usare switch per creare oggetti polimorfici.

## Classi utility e metodi statici
- Evita classi utility con logica di dominio o logica da testare in isolamento: usa componenti iniettabili.
- Statici ammessi se puri, senza stato né contesto: conversioni semplici, factory statiche (`of`, `from`), costanti.
