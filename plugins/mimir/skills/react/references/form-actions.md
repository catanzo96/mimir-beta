# Form e Actions (React 19)

Si applica insieme a `SKILL.md`. Verifica la versione: sotto la 19 queste API non esistono (`useFormState` di `react-dom` era il predecessore di `useActionState`).

## useActionState
- `const [stato, azione, inCorso] = useActionState(fn, statoIniziale)`. `fn(statoPrecedente, formData)` ritorna il nuovo stato: tipicamente `{ errori }` o l'esito.
- Le chiamate sono accodate e vengono eseguite in sequenza: non assumere che due invii ravvicinati siano paralleli.
- Gli errori attesi (validazione) si ritornano come stato; quelli inattesi si lanciano e li prende un error boundary.
- Con `<form action={azione}>` i campi non controllati si svuotano dopo l'invio: se vuoi mantenerli, ritorna i valori nello stato e usa `defaultValue`.

## useFormStatus
- Legge lo stato del `<form>` **padre**: va chiamato in un componente figlio del form, non nel componente che lo renderizza.

## useOptimistic
- Mostra lo stato "sperato" mentre l'azione è in corso; a fine azione torna al valore reale, quindi se l'azione fallisce l'interfaccia si ripristina da sola.
- Si aggiorna dentro un'Action (`startTransition` o una prop `action`). Fuori da lì React avvisa.
- Il reducer opzionale deve essere puro.
- Mostra anche un segnale di "in attesa" sugli elementi ottimistici (es. opacità o etichetta), e prevedi cosa vede l'utente se fallisce.

## Con una libreria dati
- Se il progetto usa TanStack Query, per le scritture resta la sua `useMutation` (con i suoi `onMutate` per l'ottimistico): non mescolare i due modelli sullo stesso flusso.

## Accessibilità
- Errori collegati al campo (`aria-describedby`, `aria-invalid`), esito annunciato con `aria-live="polite"`, focus sul primo campo errato dopo un invio fallito.
