---
name: architettura-esagonale
description: Linee guida ports & adapters. Usala quando progetti o rivedi la struttura di un servizio, o il progetto ha package come domain, application, infrastructure, ports o adapters (esagonale, clean architecture).
---

# Architettura esagonale

Si applica insieme a `clean-code` e alla skill del linguaggio. La struttura reale del progetto prevale: prima di aggiungere codice, individua come il progetto nomina e organizza i layer. Per modellare il dominio (linguaggio comune, aggregati, bounded context) vale `ddd`.

## Layer e dipendenze
- **Dominio**: modello e regole di business. Non dipende da framework, persistenza o trasporto.
- **Application**: casi d'uso e service applicativi. Orchestrano il dominio e usano le porte.
- **Porte**: interfacce definite dal core.
  - *inbound*: cosa offre l'applicazione;
  - *outbound*: cosa le serve dall'esterno (persistenza, servizi, messaggi).
- **Adapter**: implementano le porte verso tecnologie concrete (REST, DB, code, client esterni).
- Le dipendenze puntano **verso il dominio**, mai il contrario. Il dominio non importa nulla dagli adapter.

## Responsabilità delle entità (dominio ricco)
- **Dentro l'entità**: i comportamenti che usano solo i suoi dati (validazioni, calcoli, transizioni di stato).
- **Fuori**, in service o casi d'uso: ciò che richiede collaborazione con altri oggetti, sistemi esterni o logica che non dipende solo dallo stato interno.
- Evita entity anemiche con tutta la logica nei service: la logica su dati propri va nell'entità (Tell, Don't Ask).

## Interfacce
- Le porte sono sempre interfacce.
- Service applicativi, mapper e adapter: interfaccia più implementazione se è la convenzione del progetto. Altrimenti bastano classi concrete iniettate (vedi `clean-code`, OOP).

## Mapping
- Ogni confine ha i suoi modelli: DTO del trasporto, modello di dominio, entity di persistenza.
- Separare dominio ed entity JPA ha un costo in mapping.
  - Conviene quando il dominio è ricco o la persistenza deve poter cambiare.
  - Se il progetto usa consapevolmente un modello unico, annotato JPA, seguilo. Il DTO di trasporto resta comunque separato.
- La conversione sta in mapper dedicati (es. MapStruct), che vanno testati.
- I modelli di un layer non attraversano gli altri: niente entity JPA esposte dal controller.

## Test per layer
- La struttura dei test rispecchia quella dei package (`application/services`, `application/mappers`...).
- **Service di dominio e applicativi**: unit test con le porte outbound mockate.
- **Mapper, validatori, specification**: unit test diretti.
- **Adapter**: test di integrazione (`*IT`) contro la tecnologia reale o un suo sostituto (es. Testcontainers).
- Dati di test in factory condivise (`*MockFactory`).
