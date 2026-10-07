# Naming

La **lingua** degli identificatori la decide il progetto (vedi la regola di adattività). Su un progetto nuovo, chiedi.

## Regole generali
- **Significativi**: il nome dice scopo o comportamento. Evita nomi generici come `Manager` senza contesto, `Utils`, `Helper`, `data`, `info`, `esegui()`, `gestisci()`.
- **Pronunciabili**: niente sigle criptiche.
- **Niente abbreviazioni inventate**. Ammesse solo quelle consolidate: `id`, `dto`, `api`, `url`, `http`.
- **Brevi ma espressivi**: al massimo circa 6 parole.
- **Coerenti**: un concetto, un nome in tutto il codice.

## Forma
| Elemento | Forma | Esempio |
|---|---|---|
| Classe, tipo, enum, record | sostantivo | `ComunicazioneObbligatoria`, `TipoDocumento` |
| Interfaccia | come le classi, senza prefisso `I` (salvo C#) | `ArchivioDocumenti` |
| Metodo | verbo + oggetto | `calcolaDataScadenza()` |
| Variabile, campo | sostantivo | `dataFineAdesione` |
| Booleano | prefisso `is`, `has`, `can`, `should` | `isAttivo`, `hasDocumentiCompleti` |
| Costante | la convenzione del linguaggio (es. `SCREAMING_SNAKE_CASE`) | `MAX_TENTATIVI` |

Case (camelCase, snake_case, PascalCase) e struttura dei package o moduli seguono la convenzione del linguaggio.

## Termini inglesi consolidati
Ammessi anche in un codice in italiano, se coerenti con il progetto:
- **prefissi**: `get`, `set`, `is`, `has`, `can`, `should`;
- **suffissi di ruolo**: `Controller`, `Service`, `Repository`, `Mapper`, `Factory`, `Handler`, `Provider`, `Filter`, `Port`, `Adapter`, `UseCase`;
- **factory statiche**: `of()`, `from()`, `valueOf()`, `empty()`.

## Verbi
- Preferisci verbi specifici: `valida`, `verifica`, `calcola`, `registra`, `invia`, `trova`, `aggiorna`, `elimina`, `mappa`.
- Evita `fai`, `gestisci`, `esegui`, `processa`, salvo quando sono davvero esplicativi.
- Guard e validazione: `valida<Condizione>`, `verifica<Condizione>`.
- Operazioni che possono fallire gestendo l'errore: `prova<Azione>` (in inglese `try<Action>`).

## Test
Il nome esprime comportamento e condizione:
- `dovrebbe<Comportamento>Quando<Condizione>` (in inglese `should<Behavior>When<Condition>`);
- ✅ `dovrebbeLanciareErroreQuandoTokenScaduto()`
- ❌ `test1()`, `verificaPagamento()`
