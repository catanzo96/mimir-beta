# Piattaforme di CI/CD: sintassi minima e trappole

Prima di scrivere, leggi la pipeline esistente e i template condivisi dell'azienda: la sintassi esatta e le funzioni dipendono dalla versione della piattaforma (soprattutto per le installazioni on-premise di GitLab, Azure DevOps Server e Jenkins), quindi controlla la documentazione ufficiale della versione in uso.

## Azure DevOps Pipelines (`azure-pipelines.yml`)

```yaml
trigger:
  branches:
    include: [main]
pool:
  vmImage: ubuntu-latest        # oppure un agent pool aziendale
variables:
  - group: gruppo-variabili     # gruppo di variabili / key vault
stages:
  - stage: Build
    jobs:
      - job: build
        steps:
          - script: ./mvnw -B verify
          - script: cp target/*.jar $(Build.ArtifactStagingDirectory)
          - publish: $(Build.ArtifactStagingDirectory)
            artifact: app
  - stage: DeployCollaudo
    dependsOn: Build
    jobs:
      - deployment: deploy
        environment: collaudo   # gli ambienti hanno approvazioni e controlli
        strategy:
          runOnce:
            deploy:
              steps:
                - download: current
                  artifact: app
```

- Gerarchia: `stages` > `jobs` > `steps`. Un `deployment` job lega il deploy a un **environment**, dove si configurano approvazioni, controlli e storico dei deploy.
- Le **approvazioni si definiscono sull'environment**, non nel YAML: chi modifica il file non le può togliere dal file, ma controlla chi può modificare l'environment.
- **Variabili**: sintassi `$(nome)` (macro, risolta a runtime, lascia il testo se non esiste), `${{ variables.nome }}` (template, in compilazione), `$[ variables.nome ]` (runtime expression). Confonderle è la causa più comune di valori vuoti. I segreti non finiscono nelle variabili d'ambiente dei passi: vanno mappati esplicitamente (`env: { TOKEN: $(token) }`).
- **Artefatti**: `publish`/`download`; tra stage i job non condividono il filesystem, quindi l'artefatto va scaricato.
- **Template** (`template:`) e repository di template condivisi: puoi estendere (`extends`) per imporre passi obbligatori.
- **Cache**: task `Cache@2` con chiave sul lockfile (`key: 'maven | "$(Agent.OS)" | **/pom.xml'`).
- Trappole:
  - un trigger sul ramo che il YAML stesso aggiorna può innescare cicli: usa `[skip ci]` o `trigger: none` nel passo di commit, se esiste;
  - la validazione delle pull request: con repository GitHub o Bitbucket si dichiara nel YAML (`pr:`); con Azure Repos il `pr:` del YAML non vale e la pipeline di validazione si imposta nella **branch policy** del ramo;
  - le pipeline di un fork non ricevono segreti per default;
  - i pool self-hosted mantengono lo stato tra le esecuzioni: pulisci l'area di lavoro (`clean: true`) o i residui falsano la build.
- Stato e log si leggono con `az pipelines runs show` (estensione `azure-devops`) o dall'interfaccia; non lanciare esecuzioni di deploy senza richiesta.

## GitLab CI (`.gitlab-ci.yml`)

```yaml
stages: [build, test, deploy]
default:
  image: maven:3.9.9-eclipse-temurin-21     # versione esatta, non un tag mobile
build:
  stage: build
  script: ./mvnw -B -Dmaven.repo.local=.m2/repository package
  artifacts:
    paths: [target/*.jar]
    expire_in: 1 week
  cache:
    key:
      files: [pom.xml]
    paths: [.m2/repository]
deploy_prod:
  stage: deploy
  script: ./deploy.sh
  environment: produzione
  when: manual
  rules:
    - if: $CI_COMMIT_TAG
```

- Gli stage sono sequenziali; per eseguire in parallelo usa **`needs:`** (grafo diretto, non aspetta lo stage precedente).
- **`rules:`** sostituisce `only/except` (legacy). Le regole si valutano in ordine, la prima che corrisponde decide; un job senza regola corrispondente non parte. Attenzione ai **pipeline di merge request** contro quelli di branch: se non controlli `$CI_PIPELINE_SOURCE` ottieni pipeline duplicate.
- **Artifacts** passano file tra job e restano scaricabili; la **cache** è best-effort, per dipendenze, e dipende dal runner (con runner diversi può mancare). Non scambiarle.
- **Variabili protette** (solo su branch/tag protetti) e **mascherate** (con vincoli sul formato del valore). Le variabili protette non arrivano ai job su branch non protetti: se un job "non vede" il segreto, controlla prima questo.
- **`include:`** per template condivisi (progetto, file locale, remoto); `extends:` e `!reference` per riusare blocchi. Il YAML risultante si vede nell'editor di pipeline (vista "full configuration") o con il lint CI.
- **Environments e `when: manual`** con `allow_failure: false` se il passo manuale deve bloccare la pipeline; ambienti protetti con approvatori (a seconda della licenza).
- **Trappole**:
  - un job `when: manual` **fuori da `rules`** ha `allow_failure: true` implicito: la pipeline risulta "passata" senza il passo manuale. Dentro `rules` (come nell'esempio) il default è `false` e la pipeline resta bloccata finché qualcuno non lo avvia;
  - i tag mobili dell'immagine del runner cambiano il comportamento nel tempo;
  - il cache path deve essere dentro la cartella del progetto (`.m2` va rediretto con `-Dmaven.repo.local`);
  - gli `artifacts` dei job si scaricano per default dai job precedenti: `dependencies: []` per non scaricarli quando non servono.
- Validazione: lint CI nell'interfaccia, o `glab ci lint` se la CLI è presente.

## GitHub Actions (`.github/workflows/*.yml`)
Rilevante se il progetto usa GitHub; la sintassi è vicina a quelle sopra.
- Struttura `on` > `jobs` > `steps`; `needs:` per l'ordine; `environment:` con regole di protezione e approvatori.
- **`permissions:`** minimi nel workflow (di default il token può essere troppo ampio); `secrets.*` non arrivano ai workflow da fork.
- **Azioni di terze parti**: fissale a un commit SHA, non a un tag mobile, e valutane l'origine (rischio di supply chain).
- Iniezione di comandi: non scrivere `${{ github.event.pull_request.title }}` dentro `run:`; passalo come variabile d'ambiente.
- `concurrency:` per annullare esecuzioni superate o serializzare i deploy. Validazione con `actionlint`.

## Jenkins (`Jenkinsfile`)

```groovy
pipeline {
  agent none
  options { timeout(time: 30, unit: 'MINUTES'); disableConcurrentBuilds() }
  stages {
    stage('Build') {
      agent { label 'linux' }
      steps { sh './mvnw -B verify' }
      post { always { junit '**/target/surefire-reports/*.xml' } }
    }
    stage('Approvazione') {
      when { branch 'main' }
      steps { input message: 'Deploy in produzione?' }   // nessun executor occupato durante l'attesa
    }
    stage('Deploy') {
      when { branch 'main' }
      agent { label 'linux' }
      steps {
        withCredentials([string(credentialsId: 'token', variable: 'TOKEN')]) { sh './deploy.sh' }
      }
    }
  }
}
```

- Pipeline **dichiarativa** (`pipeline { }`) come default; la scripted (`node { }`) solo se serve flessibilità. Il codice Groovy dentro `script { }` va ridotto al minimo e portato in una shared library.
- **`input`** per le approvazioni: mettilo **fuori da un `agent`** occupato (`agent none` sullo stage), altrimenti un'esecuzione in attesa blocca un executor.
- **Credenziali** solo con `withCredentials`/`credentials()`, mai stampate; il mascheramento ha i limiti già detti. Non usare `sh "echo ${TOKEN}"` con interpolazione Groovy: usa le virgolette singole e lascia espandere la shell.
- **Shared library** per la logica comune, versionata e con tag.
- Trappole: plugin non aggiornati o con vulnerabilità note (aggiornamenti e compatibilità sono compito di chi amministra: segnala, non aggiornare); workspace condiviso e sporco fra esecuzioni (`cleanWs()`); stato sull'agent invece che nel repo; `parallel` senza limitare le risorse dell'agent.
- Validazione: linter dichiarativo (`/pipeline-model-converter/validate` dell'istanza) se accessibile; altrimenti prova su un job di test.
