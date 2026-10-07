---
name: retro
description: "Retrospettiva: trasforma correzioni e preferenze emerse nella sessione in miglioramenti di Mímir. Si avvia con /retro."
disable-model-invocation: true
---

# Retro: migliorare Mímir

Obiettivo: trasformare ciò che è emerso lavorando in miglioramenti concreti di Mímir (cartella: la root del marketplace che contiene questa skill). "Niente da proporre" è un esito legittimo: meglio nessuna modifica che una regola sbagliata.

## Passi

1. **Raccogli**
   - Le correzioni, le preferenze e le frustrazioni dell'utente emerse nella sessione corrente ("non fare X", "così no", una richiesta ripetuta due volte).
   - Le voci aperte in `inbox.md`.
   - Le procedure ripetute che varrebbe la pena codificare.
   - Se esiste, l'ultimo report di `/insights` (`~/.claude/usage-data/report.html`): attriti e richieste fraintese su più sessioni. Non lanciarlo tu: consuma limiti del piano; proponilo all'utente ogni tanto, non a ogni retro.
2. **Filtra**: non catturare
   - errori di ambiente o passeggeri (rete, permessi, una versione installata);
   - giudizi su uno strumento ("X è rotto"): invecchiano presto e bloccano prove future;
   - compiti fatti una volta sola, raccontati come procedura;
   - problemi non risolti: un tentativo fallito non diventa un "metodo consigliato";
   - ciò che sta già nel codice, in git o nel CHANGELOG.
3. **Scegli la destinazione**, in quest'ordine: la prima che va bene vince.
   1. La skill usata nella sessione, se la lezione riguarda il suo compito.
   2. Una skill o una regola esistente che copre già il tema.
   3. Un file in `references/` di una skill esistente, se è dettaglio da consultare.
   4. Solo per una classe di casi, mai per un singolo episodio, un elemento nuovo. Il tipo segue il README, sezione "Dove va una cosa":
      - vale per ogni compito → regola in `rules/*.md` (breve, imperativa);
      - deve valere al 100% → hook o permesso (`plugins/mimir/hooks/`, `settings.template.json`);
      - vale per un tipo di compito o una tecnologia → skill (`mimir` se vale in ogni ambito, `brokkr` solo per il lavoro);
      - serve un contesto isolato, lavoro in parallelo o tool ristretti → agent in `plugins/<plugin>/agents/`;
      - riguarda un solo progetto → il CLAUDE.md di quel progetto, non Mímir.

   Un fatto sta in un solo posto. Una preferenza legata a un compito va nella skill di quel compito; nella memoria o nel profilo solo se nessuna skill ne è titolare.
4. **Dai forma alla lezione**
   - Una regola generale più il suo perché, in una o due righe.
   - Niente date, ticket, nomi di progetti o clienti: il metodo in Mímir, i dati nei progetti.
   - Se la stessa lezione c'è già, fondi le due in una regola sola invece di aggiungerne una vicina.
   - Se una regola esistente è sbagliata, correggila dove sta: niente note "UPDATE" in coda.
   - Scrivi o modifica secondo la skill `scrivi-skill`.
5. **Leggi prima di modificare**: apri il file attuale e parti da quello, non da quanto ne ricordi nella conversazione.
6. **Igiene della memoria** (la memoria automatica di Claude Code per il progetto)
   - Le memorie sono fatti stabili, scritti come fatti ("l'utente preferisce…"), non un diario: lo stato del lavoro sta in git, nel CHANGELOG e in `inbox.md`.
   - Se un file di memoria supera ~1.500 caratteri, o una voce ripete ciò che sta in Mímir, proponi di consolidarlo prima di aggiungere altro.
7. **Proponi** le modifiche come elenco, ciascuna con il file coinvolto e il testo proposto. Aspetta l'ok.
8. **Applica** le modifiche approvate:
   - Aggiungi una riga a `CHANGELOG.md`.
   - Rimuovi da `inbox.md` le voci gestite.
   - Se è cambiato un plugin, incrementa `version` in `plugins/<plugin>/.claude-plugin/plugin.json`.
9. **Non fare commit o push**: proponi il messaggio di commit e aspetta l'autorizzazione.
