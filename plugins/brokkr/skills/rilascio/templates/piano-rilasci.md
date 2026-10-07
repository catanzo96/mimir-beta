# Piano rilasci: <perimetro>

**Stato**: in corso · **Aggiornato**: gg/mm/aaaa

## 0. Principi
<Regole di questo piano: ordine degli ambienti, stesso artefatto, un passo alla volta, cosa non si rilascia insieme.>

## 1. T0: dove siamo
### Cosa gira oggi
| Componente | Ambiente | Versione | Dal |
|---|---|---|---|

### Dove sta il lavoro
| Lavoro | Branch | Stato (sviluppo, collaudo, pronto) | Dipende da |
|---|---|---|---|

## 2. Problemi da risolvere prima
| # | Problema | Blocca | Chi |
|---|---|---|---|

## 3. Timeline
### T1: <contenuto>
- **Contiene**: <…>
- **Prerequisiti**: <…>
- **Ambienti e date**: <…>
- **Rollback**: <…>

## 4. Gate comuni per ogni passo in produzione
- Collaudo concluso con esito Go
- Backup verificato
- Rollback scritto e riletto
- Finestra concordata

## 5. Go / No-Go
| Criterio | Esito |
|---|---|
| Collaudo concluso, difetti aperti solo non bloccanti e accettati | |
| Migrazioni provate su dati con volumi realistici, tempi noti | |
| Passi non reversibili dichiarati e accettati | |
| Configurazione di produzione pronta e verificata | |
| Segnali di rollback e chi decide, definiti | |
| Chi osserva dopo il rilascio, e quando | |

## 6. Rollback
<Per passo: cosa si ripristina e come. I passi non reversibili, dichiarati. Segnali che fanno scattare il rollback, chi decide, entro quanto.>

## 7. Decisioni e punti aperti
| # | Decisione | Opzioni | Chi | Stato |
|---|---|---|---|---|

## 8. Registro dei rilasci
| Data | Passo | Ambiente | Versioni | Esito | Note |
|---|---|---|---|---|---|

## 9. Fuori perimetro
