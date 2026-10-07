# ASP.NET Core

Da leggere quando scrivi o rivedi endpoint, middleware, validazione, gestione errori o autenticazione. Le versioni sono le minime: controlla il `TargetFramework`.

## Minimal API o controller
- Segui lo stile già presente nel progetto: non mescolarli nella stessa area.
- Minimal API: meno cerimonia, ottime per servizi piccoli e medi. Raggruppa con `MapGroup`, un file di estensione per feature (`MapOrdini()`), handler come metodi con nome (non lambda da 40 righe).
- Controller: filtri, model binding avanzato e convenzioni consolidate; `[ApiController]` dà validazione automatica del modello e `ProblemDetails` sui 400.
- Ritorna tipi espliciti: `TypedResults` (minimal) o `ActionResult<T>` (controller), così OpenAPI e test vedono i codici di risposta.
- Il codice di dominio non dipende da `HttpContext` né dai tipi di ASP.NET: l'endpoint traduce e delega a un servizio. Vedi `architettura-esagonale` per la separazione.

## Pipeline e middleware
- L'ordine conta: gestione eccezioni, HTTPS/HSTS, routing, CORS, `UseAuthentication`, `UseAuthorization`, poi gli endpoint. `UseAuthorization` prima di `UseAuthentication` non autentica nessuno.
- Middleware solo per ciò che è trasversale alla richiesta (correlation id, logging di richiesta). La logica di business non va in un middleware.
- Un middleware è un singleton: non iniettare servizi scoped nel costruttore, ma nel parametro di `InvokeAsync`.
- Non leggere il body due volte senza `EnableBuffering`; evita di bufferizzare richieste grandi.

## Validazione
- Valida ai confini, sempre: l'input HTTP non è fidato. Lunghezze massime, range, enumerazioni.
- Con `[ApiController]` il modello è validato da solo (400 automatico).
- Minimal API: da .NET 10 `builder.Services.AddValidation()` valida con DataAnnotations parametri e body (anche su `record`); `DisableValidation()` per escludere un endpoint. Prima della 10 non c'è validazione integrata: usa il meccanismo già adottato dal progetto (FluentValidation, filtri di endpoint). Con il generatore di sorgente, i tipi sono scoperti solo nell'assembly dove chiami `AddValidation`.
- Le regole di dominio (invarianti) restano nel dominio: la validazione dell'input non le sostituisce.
- Mass assignment: non bindare le entity direttamente. DTO di ingresso dedicati, senza i campi che il client non deve poter impostare.

## Errori e ProblemDetails
- Risposte d'errore in formato `ProblemDetails` (RFC 9457): `AddProblemDetails()` + `IExceptionHandler` (.NET 8+) per tradurre le eccezioni note in 4xx e le altre in 500 senza esporre stack trace né messaggi interni.
- `UseExceptionHandler()` in tutti gli ambienti; la pagina dettagliata degli errori solo in Development.
- Eccezioni di dominio mappate a codici precisi (404, 409, 422), non tutto 400 o 500.
- Il log dell'errore completo resta sul server, con un id di correlazione restituito al client.

## Autenticazione e autorizzazione
- Non scrivere crittografia o gestione di token a mano: JWT Bearer (`AddJwtBearer`) o OpenID Connect con un IdP, `ASP.NET Core Identity` se il progetto ha gli utenti in casa. Valida emittente, audience, scadenza e firma; chiavi e segreti fuori dal repo.
- Autorizzazione di default restrittiva: `FallbackPolicy` che richiede utente autenticato, e `[AllowAnonymous]` esplicito dove serve.
- Policy e requisiti (`AddAuthorizationBuilder().AddPolicy(...)`) invece di controlli sui ruoli sparsi nel codice. Controlla anche **la proprietà della risorsa** (l'ordine appartiene a questo utente?), non solo il ruolo: è la causa tipica di IDOR.
- Da .NET 10 le richieste API non autenticate (controller con `[ApiController]`, minimal API JSON) ricevono 401/403 invece del redirect al login del cookie: è un cambio di comportamento da ricordare negli aggiornamenti.
- CORS con origini esplicite, mai `AllowAnyOrigin` con credenziali. Antiforgery per i form con cookie.
- Rate limiting nativo (`AddRateLimiter`) sugli endpoint sensibili (login, ricerche costose).

## OpenAPI
- Da .NET 9 la generazione è integrata (`AddOpenApi`, `MapOpenApi`); da .NET 10 il default è OpenAPI 3.1. Se il progetto usa Swashbuckle o NSwag, resta quello.
- Documenta i codici di risposta reali (`.Produces<>`, `TypedResults`), non solo il 200.

## Hosting e salute
- `BackgroundService` per i lavori in background; gestisci il `CancellationToken` di arresto e cattura le eccezioni nel ciclo, altrimenti il processo si ferma.
- Health check (`AddHealthChecks`) separati per liveness e readiness. Nessun dato sensibile nelle risposte.
- Un'API che chiama altri servizi: timeout e resilienza (`Microsoft.Extensions.Http.Resilience`) sul `HttpClient`, se già nel progetto.
