---
name: container
description: "Scrivere e rivedere Dockerfile, Compose e basi di Kubernetes. Usala quando tocchi immagini o container, o in progetti con Dockerfile, compose.yaml o manifest k8s."
---

# Container

Si applica insieme a `clean-code` (sicurezza compresa). Per la pipeline che costruisce e pubblica le immagini: `ci-cd`. Kubernetes di base: `references/kubernetes.md`. Prevalgono immagini base, registry e convenzioni del progetto o dell'azienda.

## Immagini
- **Immagine base ufficiale e piccola** (varianti `slim`, distroless, alpine solo se il software la supporta: musl cambia il comportamento di alcune librerie native). Fissa la **versione precisa** del tag, mai `latest`; per riproducibilità forte, anche il digest (`@sha256:...`), aggiornato da un bot o a mano in modo tracciato.
- **Multi-stage**: uno stadio con compilatore e strumenti di build, uno finale con solo il runtime e l'artefatto. Il JDK, npm e i sorgenti non servono in produzione.
- **Utente non root**: crea un utente dedicato (`USER app`) e dai i permessi solo dove serve scrivere. Filesystem di sola lettura e senza capability extra quando l'applicazione lo permette.
- **Un processo per container**, in primo piano come PID 1. Se l'app non gestisce i segnali, `SIGTERM` non arriva e l'arresto diventa un kill dopo il timeout: usa la forma `exec` (`CMD ["java", "-jar", "app.jar"]`, non la forma shell) o un init minimo (`tini`, `--init`).
- **`ENTRYPOINT` e `CMD`** in forma JSON; la configurazione arriva da variabili d'ambiente o file montati, non è incorporata nell'immagine: la stessa immagine va in ogni ambiente.
- Etichette OCI (`org.opencontainers.image.*`: versione, sorgente, revisione) per risalire al commit.
- **Locale e fuso**: imposta esplicitamente locale e `TZ` solo se l'applicazione ne dipende.

## Layer e cache
- L'ordine delle istruzioni è l'ordine di invalidazione: copia prima i file delle dipendenze (`pom.xml`, `package*.json`, lockfile), installa, poi copia il codice. Un cambio di sorgente non deve riscaricare le dipendenze.
- Usa le cache di BuildKit per i gestori di pacchetti (`RUN --mount=type=cache,target=...`) in locale e in pipeline, dove il builder lo supporta.
- Installa e pulisci nello stesso `RUN` (`apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*`): un file cancellato in un layer successivo occupa comunque spazio.
- `COPY` mirato invece di `COPY . .`; usa `COPY --chown` invece di un `chown` a parte.
- **`.dockerignore`** sempre: `.git`, `target`, `node_modules`, `.env`, log, file IDE. Riduce il contesto, velocizza la build e impedisce che segreti locali finiscano nell'immagine.
- Un layer più piccolo si ottiene con meno file, non con meno comandi: non unire tutto in un solo `RUN` se rompe la cache utile.

## Segreti
- Mai un segreto in `ENV`, `ARG`, `COPY` o in un file dell'immagine: resta nella storia dei layer e si legge con `docker history` o estraendo l'immagine. Un `rm` successivo non lo cancella.
- Durante la build usa i secret mount di BuildKit (`RUN --mount=type=secret,...`) per token del registry o credenziali di download.
- A runtime: variabili d'ambiente iniettate dall'orchestratore, file montati da un secret manager, mai incorporate. Tratta come compromesso un segreto finito per errore in un'immagine pubblicata e ruotalo.
- Scansiona le immagini per vulnerabilità con lo strumento già in uso (Trivy, Defender, registry); non aggiungerne senza ok.

## Healthcheck e log
- `HEALTHCHECK` in Docker/Compose con un comando leggero che controlla l'applicazione (endpoint `health`), non solo che il processo viva; `start_period` per un avvio lento. Il comando deve esistere nell'immagine: in una base minimale non c'è `curl`, usa un endpoint raggiungibile da un binario già presente o il probe dell'orchestratore.
- **Log su stdout/stderr**, mai su file nel container: li raccoglie il runtime. Un solo formato (meglio strutturato), niente rotazione dentro l'immagine.
- Dati da conservare in volumi o servizi esterni: il filesystem del container è effimero.

## Compose
- Per sviluppo locale, test di integrazione e piccoli ambienti; non è un orchestratore di produzione per sistemi critici salvo scelta del progetto.
- File base `compose.yaml` + override per ambiente (`compose.override.yaml`, o `-f`). Versioni delle immagini fissate, come nei Dockerfile.
- `depends_on` con `condition: service_healthy` e un healthcheck sul servizio: senza, l'ordine di avvio non garantisce che il DB sia pronto.
- Porte pubblicate solo se servono dall'host (`127.0.0.1:5432:5432` per un DB locale, non su tutte le interfacce).
- Dati con volumi nominati; `docker compose down -v` li cancella: dichiaralo prima di lanciarlo.
- Variabili da file `.env` non versionato, con un `.env.example` senza valori reali.
- Limiti di risorse espliciti quando più servizi condividono la macchina.

## Trappole frequenti
- JVM e memoria: le versioni recenti leggono i limiti del container, ma imposta comunque la percentuale di heap (`-XX:MaxRAMPercentage`) lasciando margine per metaspace e thread.
- Node in container: installa con `npm ci` e `--omit=dev` (o equivalente) nello stadio finale, non copiare `node_modules` dall'host.
- Architetture diverse (sviluppo su ARM, produzione su x86): costruisci per la piattaforma di destinazione.
- Immagine ricostruita "uguale" ma diversa: tag mobile, `apt-get` non fissato, dipendenze senza lockfile.
- Eseguire come root solo per usare porte basse: porta alta nel container, mappa all'esterno.
- Modificare un container in esecuzione a mano (`docker exec` e scrivere file): al prossimo riavvio il lavoro è perso e l'ambiente non è riproducibile.

## Sicurezza dei comandi
Cancellare container, volumi, immagini o reti (`docker rm`, `volume rm`, `system prune`, `down -v`) distrugge dati e stato: chiedi conferma, specifica sempre cosa verrà toccato. Sulle risorse remote (cluster, registry) lavora in sola lettura salvo richiesta esplicita.

## Verifica
- `docker build` (o `docker buildx build`) del Dockerfile modificato, leggendo l'esito e le dimensioni finali (`docker image ls`); se Docker non è disponibile nella sandbox, dichiaralo.
- Avvia l'immagine e controlla: utente (`docker run --rm img id`), healthcheck (`docker inspect` o `docker compose ps`), log su stdout, arresto pulito con `docker stop` entro il timeout.
- Cerca segreti nell'immagine (`docker history --no-trunc`, ispezione dei file) e verifica che `.dockerignore` escluda ciò che deve.
- `docker compose config` valida e mostra il file risolto; poi `docker compose up` e prova dei servizi toccati.
- Linter del progetto (es. hadolint) se già configurato.
