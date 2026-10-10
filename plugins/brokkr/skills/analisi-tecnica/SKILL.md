---
name: analisi-tecnica
description: Analisi tecnica fondata su evidenze. Usala quando l'utente chiede di diagnosticare un problema o un incidente, stimare l'impatto di una modifica, confrontare versioni, censire debito e rischi, scrivere un ADR o documentare un sistema esistente.
when_to_use: 'Es.: "perché in produzione succede X?", "quanto impatta cambiare Y?", "che differenze ci sono tra le due versioni?", "documenta com''è fatto questo sistema".'
---

# Analisi tecnica

Documenta **come funziona davvero** un sistema, con evidenze che chiunque può ricontrollare. Per il *cosa* e il *perché* del dominio usa `analisi-funzionale`. Spesso i due documenti si scrivono in coppia.

Il metodo, cioè cosa conta come verifica, la tabella "Verificato su", le rettifiche e le trappole degli strumenti, è in [references/evidenze.md](references/evidenze.md). **Leggilo sempre prima di scrivere.**

## Quando non usarla
- Documentazione da tenere per chi legge dopo (README, guide, onboarding, mappa del repo): `documentazione-tecnica`. Qui il sistema si documenta con evidenze ricontrollabili, per decidere, diagnosticare o censire.
- Un difetto da correggere: `debugging` per trovare la causa, `ticket` per il flusso fino al rilascio. Questa skill entra quando la diagnosi diventa un documento (incidente in produzione, causa radice da rendicontare).

## Contesto del progetto
Dal `CLAUDE.md` del progetto ricava:
- ambienti e DB (quali puoi interrogare e quali no);
- piattaforme e convenzioni di dominio;
- dove vanno i documenti e come si nominano;
- codici dei ticket.

Se manca qualcosa, chiedi. Non inventare.

## Procedura
1. **Inquadra la domanda.** Cosa si vuole sapere e perché. Scrivi come la interpreti, prima di partire.
2. **Inventario delle fonti**: repo e branch di riferimento, documenti esistenti, ambienti, ticket collegati.
3. **Raccogli le evidenze** dal branch di produzione: `git show` e `git grep` su `origin/<branch>`. Per le assenze usa `grep -a`. Le query non le esegui tu: le prepari.
   - Per capire un comportamento ricostruisci il flusso: punto d'ingresso (endpoint, job, evento), catena di chiamate, confini asincroni (code, scheduler, callback), percorsi d'errore, dati letti e scritti.
   - Se la lettura è ampia (molti file o repository), delegala a un subagent e tieni nella conversazione solo il risultato con le evidenze.
4. **Separa** accertato e ipotesi. Ogni ipotesi diventa una domanda aperta, con chi può rispondere.
5. **Scrivi** con il template adatto. Le sezioni che non servono si tolgono: nessuna sezione vuota per forma.
6. **Rileggi le citazioni**: ogni `file:riga` va riaperto sul commit dichiarato.

## Template
| Template | Quando |
|---|---|
| [diagnosi.md](templates/diagnosi.md) | un problema tecnico o un incidente: sintomo, cause escluse, causa, correzioni |
| [analisi-impatto.md](templates/analisi-impatto.md) | l'effetto di un cambiamento (aggiornamento di piattaforma, API, schema) su uno o più repository |
| [delta.md](templates/delta.md) | confronto tra due versioni di modello, schema, configurazione o dipendenze |
| [pacchetto-query.md](templates/pacchetto-query.md) | estrazioni da far eseguire all'utente, con il file degli esiti |
| [registro-debito.md](templates/registro-debito.md) | censimento di debito e rischi, con la tassonomia dei codici |
| [adr.md](templates/adr.md) | una decisione tecnica, con conseguenze e alternative |
| [audit-dipendenze.md](templates/audit-dipendenze.md) | inventario di versioni, fine supporto e vulnerabilità |
| [audit-rilascio.md](templates/audit-rilascio.md) | prontezza al rilascio di un'evolutiva o di un sistema: cosa può rompersi in produzione, con esito go, no-go o con riserva |

## Decisioni (ADR)
- Prima di proporne uno, cerca gli ADR esistenti sullo stesso tema: una decisione già presa non si riscrive, se ne scrive una nuova che la **supera** e lo dichiara.
- L'ADR propone e raccomanda; decide l'utente o chi indica.
- Per decisioni di architettura o di design di un servizio, passa in rassegna [references/checklist-design.md](references/checklist-design.md) e riporta solo i punti pertinenti.

## Giudizi di prontezza
Un giudizio di rilascio è **go**, **no-go** o **go con riserva**, con i bloccanti separati dalle riserve e un'evidenza per ciascuno. Niente punteggi numerici: danno una precisione che l'analisi non ha.

## Diagrammi
Le tabelle sono la fonte. Un diagramma mermaid (`sequenceDiagram` per i flussi, `flowchart` per le architetture) si aggiunge **solo se chiarisce**, e deve dire le stesse cose della tabella.

## Cosa non fare
- Non correggere i difetti mentre li censisci. Si annotano nel registro; se sono urgenti, diventano un ticket.
- Non progettare il sistema nuovo dentro un'analisi AS-IS. Le idee vanno in un ADR o in una sezione "Proposte (non applicate)".
- Non dichiarare "non esiste" senza una ricerca che non salti file.
- Non eseguire modifiche su ambienti condivisi. Una diagnosi propone gli interventi, non li applica.
