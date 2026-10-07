# Dev container per il lavoro autonomo

Quando Claude lavora senza chiedere conferme (`--dangerously-skip-permissions` o `bypassPermissions`), il confine non può essere la conferma dell'utente: deve essere l'ambiente. In Mímir il via libera si dà solo dentro un dev container. Riferimento ufficiale: `https://code.claude.com/docs/en/devcontainer.md` e l'esempio in `github.com/anthropics/claude-code/.devcontainer`.

La documentazione stessa avverte: con i permessi saltati, il container **non impedisce l'esfiltrazione di ciò che contiene**, comprese le credenziali di Claude Code nel container. Si usa solo con repository fidati, e si controlla cosa fa.

## Requisiti
- **Utente non root** (`remoteUser`), versione di Claude Code fissata nell'immagine e aggiornamento automatico spento dentro il container (`DISABLE_AUTOUPDATER=1`): l'immagine si aggiorna di proposito.
- **Firewall in uscita con negazione di default** e allowlist minima: API di Anthropic (vedi `network-config` per l'elenco dei domini richiesti), host git del progetto, registry delle dipendenze (Maven, npm). Serve `NET_ADMIN` e `NET_RAW` nei `runArgs`. Se usi la feature ufficiale di Claude Code per dev container, controlla il nome dello script del firewall per non sovrascriverlo.
- **Nessuna credenziale dell'host montata**: niente `~/.ssh`, `~/.aws`, `~/.m2/settings.xml` con password, `~/.docker`. Token di breve durata con scope sul solo repository (es. token di progetto in sola lettura più push su un branch).
- **Configurazione di Claude in un volume** dedicato (`CLAUDE_CONFIG_DIR`), separato da quella dell'host.
- **Policy dentro il container**: le impostazioni non allentabili in `/etc/claude-code/managed-settings.json` del container.
- **Il lavoro torna all'utente come diff**: Claude lavora su un branch dedicato; commit e push verso il remoto restano un'approvazione dell'utente fuori dal container, o un push solo su un branch di lavoro.

## Prova prima dell'uso
Dall'interno del container:
- `curl https://example.com` deve fallire;
- una chiamata all'API di Anthropic (una sessione di Claude Code) deve funzionare;
- l'accesso all'host git e ai registry previsti deve funzionare;
- `ls ~/.ssh ~/.aws` non deve trovare le credenziali dell'host.

## Cosa resta fuori
- Il codice e i dati del progetto dentro il container sono esposti: niente dump di produzione, niente dati personali reali.
- Il container non sostituisce la review: il diff si legge prima di portarlo nel repository del cliente.
