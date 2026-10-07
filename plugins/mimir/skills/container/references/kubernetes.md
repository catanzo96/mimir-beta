# Kubernetes: le basi per sviluppare e diagnosticare

Per chi sviluppa applicazioni che girano su Kubernetes, non per amministrare il cluster. Prevalgono gli strumenti del progetto (Helm, Kustomize, manifest semplici, operatori) e le convenzioni dell'azienda.

## Risorse e dimensionamento
- **`requests`**: ciò che lo scheduler riserva; **`limits`**: il tetto. Il superamento del limite di memoria uccide il container (`OOMKilled`); il limite di CPU invece rallenta (throttling).
- Imposta sempre le `requests` (basate su misure reali), e il limite di memoria vicino alla richiesta. Il limite di CPU è controverso: un limite troppo basso causa latenza senza che la CPU sembri satura. Segui la policy del cluster.
- La JVM e altri runtime devono conoscere il limite: heap come percentuale della memoria del container, con margine per il resto.
- Più repliche (almeno due per i servizi che devono restare su) e `PodDisruptionBudget` se il cluster fa manutenzione dei nodi.

## Probe
| Probe | Domanda | Se fallisce |
|---|---|---|
| `startupProbe` | L'app ha finito di avviarsi? | Il container viene riavviato; liveness e readiness restano sospese fino al successo |
| `readinessProbe` | Può ricevere traffico ora? | Il pod esce dal servizio, senza riavvio |
| `livenessProbe` | È bloccata senza speranza? | Il container viene riavviato |

- La **liveness** controlla solo lo stato interno del processo, **mai le dipendenze** (DB, servizi esterni): se il DB cade, riavviare tutti i pod peggiora l'incidente.
- La **readiness** può considerare le dipendenze essenziali, ma con attenzione: se tutti i pod escono insieme, il servizio sparisce.
- Avvio lento: `startupProbe` con soglia ampia, non una liveness con ritardo iniziale enorme.
- Timeout, periodo e soglie ragionevoli: una probe che dura più del suo timeout causa riavvii a catena sotto carico.
- Arresto: l'app deve gestire `SIGTERM` e chiudere in modo ordinato entro `terminationGracePeriodSeconds`. Con traffico via servizio può servire una breve attesa prima di fermarsi (`preStop`), perché la rimozione dagli endpoint non è istantanea.

## Configurazione e segreti
- **ConfigMap** per configurazione non sensibile, **Secret** per le credenziali. Un Secret è codificato in base64, **non cifrato**: chi legge l'oggetto lo legge. Servono RBAC stretto, cifratura a riposo nel cluster o un secret manager esterno (operatori che sincronizzano da un vault).
- Mai segreti nei manifest versionati in chiaro: usa lo strumento dell'azienda (sealed secrets, SOPS, vault esterno) o crea il Secret fuori dal repo.
- Come arrivano ai pod: variabili d'ambiente (leggi solo all'avvio, un cambio richiede un riavvio) o file montati (aggiornati dopo un po', ma l'app deve rileggerli).
- Il cambio di una ConfigMap non riavvia da solo i pod: usa un hash nel template (Helm/Kustomize) o un rollout esplicito.

## Rollout e rollback
- Strategia `RollingUpdate` con `maxUnavailable` e `maxSurge` adeguati; con una readiness corretta il traffico non va ai pod non pronti.
- Rilascia con **tag immutabile** dell'immagine (versione o digest), non `latest`: con `latest` un rollback non è riproducibile e i nodi possono avere versioni diverse.
- `kubectl rollout status deploy/nome` per seguire; `kubectl rollout undo deploy/nome` per tornare alla revisione precedente (è una scrittura: solo con l'ok dell'utente). Il rollback dei manifest non annulla le migrazioni di database: ecco perché gli schemi devono essere compatibili tra versioni (`database`).
- In GitOps il rollback è un revert nel repo: modificare l'oggetto a mano nel cluster viene annullato dallo strumento.

## Risorse per ambiente
- Gli ambienti differiscono per **valori** (repliche, risorse, host, configurazione), non per manifest scritti da zero: Kustomize con overlay o Helm con file di valori per ambiente.
- Stessa immagine in ogni ambiente (`ci-cd`): cambia solo la configurazione iniettata.
- Namespace per ambiente o per team, con quote e policy di rete dove il cluster le usa.
- Label coerenti (`app.kubernetes.io/name`, `version`...) e selettori stabili: il selettore di un Deployment non si può cambiare dopo la creazione.

## Sicurezza dei pod
- `runAsNonRoot`, `readOnlyRootFilesystem` dove possibile, `allowPrivilegeEscalation: false`, capability ridotte (`drop: ["ALL"]`). Account di servizio dedicato con i soli permessi necessari; niente accesso all'API di Kubernetes se non serve (`automountServiceAccountToken: false`).
- Immagini da registry fidati, tag fissati.

## Diagnosticare con kubectl (sola lettura)
Usa solo comandi di lettura, verso il namespace giusto (`-n`) e dopo aver controllato il contesto (`kubectl config current-context`: errore comune è lavorare sul cluster sbagliato). Non lanciare `delete`, `apply`, `edit`, `scale`, `rollout restart`, `rollout undo`, `exec` con scritture o `port-forward` su produzione senza richiesta esplicita.

| Sintomo | Comando |
|---|---|
| Stato generale | `kubectl get pods -n ns -o wide` |
| Perché un pod non parte | `kubectl describe pod nome -n ns` (sezione Events) |
| Log | `kubectl logs nome -n ns --tail=200`; `--previous` dopo un riavvio; `-c contenitore` |
| Eventi recenti | `kubectl get events -n ns --sort-by=.lastTimestamp` |
| Configurazione effettiva | `kubectl get deploy nome -n ns -o yaml` |
| Consumo | `kubectl top pod -n ns` (se il metrics server c'è) |

Stati e cause tipiche:
- **`Pending`**: nessun nodo con risorse sufficienti, PVC non legato, regole di affinità o taint. Lo dice `describe`.
- **`ImagePullBackOff`**: tag o registry sbagliati, credenziali mancanti (`imagePullSecrets`).
- **`CrashLoopBackOff`**: il processo termina all'avvio: leggi i log `--previous` (configurazione mancante, DB irraggiungibile, segreto assente).
- **`OOMKilled`** (in `describe`, `Last State`): limite di memoria troppo basso o perdita di memoria.
- **Pod `Running` ma non `Ready`**: la readiness fallisce: guarda l'endpoint e i log, non riavviare a caso.
- **Il servizio non risponde**: controlla che i pod siano Ready, che il selettore del servizio corrisponda alle label (`kubectl get endpoints nome`), e la porta di destinazione.

Riporta nel resoconto il comando, il contesto/namespace e l'output letto, separando ciò che hai verificato dalle ipotesi.
