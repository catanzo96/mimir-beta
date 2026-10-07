# Pacchetto query <n>: <obiettivo>

**Stato**: da eseguire | eseguito il gg/mm/aaaa · **Ambiente**: <quale DB, sola lettura> · **Esiti**: `ESITI-<n>.md`

Regole:
- solo `SELECT`, aggregate quando possibile, nessun dato personale nell'output;
- costo stimato indicato per ogni query;
- una query alla volta, confrontando l'esito con quello atteso prima di passare alla successiva.

## <ID>: <scopo>
- **Serve a**: <quale domanda aperta chiude>
- **Ambiente**: <…> · **Costo**: basso | medio (tabella grande, indici) | alto (evitare in orario di punta)
- **Esito atteso**: <cosa ci si aspetta, e cosa significherebbe un esito diverso>

```sql
-- <ID>
SELECT …
```
