<#
.SYNOPSIS
Solo per la CI su runner ospitati da GitHub: lancia un comando come utente locale non amministratore.

.DESCRIPTION
Sui runner Windows di GitHub i processi girano come amministratore, con UAC disabilitato, e
install.ps1 da amministratore si ferma. Questo script crea (o riusa) un utente locale nel gruppo Users
e fuori da Administrators, con una password casuale che non esiste mai in chiaro, e gli dà la modifica
della cartella del checkout. Poi lancia il comando con il suo profilo, quindi con una HOME pulita, e
riporta l'output e il codice di uscita.
Non è un confine di sicurezza: gli step precedenti eseguono lo stesso codice da amministratore. Serve
a provare che installer e test funzionano senza elevazione.
Codici di uscita propri: 97 se il comando girerebbe elevato, 98 se il comando non ha lasciato un
codice di uscita (per esempio non è partito).
Le variabili in -PassEnv passano al comando, perché con il profilo dell'utente l'ambiente del runner
non arriva. Finiscono in un file leggibile dall'utente: mai segreti.
Scritto per Windows PowerShell 5.1 (New-LocalUser è del modulo LocalAccounts).

.EXAMPLE
powershell -NoProfile -ExecutionPolicy Bypass -File .github\scripts\run-as-user.ps1 -UserName mimirci -Command 'python -I x.py' -PassEnv PATH
#>
param(
    [Parameter(Mandatory = $true)][string]$UserName,
    [Parameter(Mandatory = $true)][string]$Command,
    [string[]]$PassEnv = @()
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# crea utenti e cambia ACL: mai su una macchina che non sia un runner effimero di GitHub
if ($env:GITHUB_ACTIONS -ne 'true' -or $env:RUNNER_ENVIRONMENT -ne 'github-hosted') {
    throw 'run-as-user.ps1 gira solo sui runner ospitati da GitHub'
}

function Get-RandomPassword {
    # costruita carattere per carattere: la password non esiste mai come stringa in chiaro
    $alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789'
    $bytes = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $password = New-Object Security.SecureString
    foreach ($byte in $bytes) { $password.AppendChar($alphabet[$byte % $alphabet.Length]) }
    # i caratteri finali soddisfano la policy di complessità
    foreach ($char in 'aA1!'.ToCharArray()) { $password.AppendChar($char) }
    $password.MakeReadOnly()
    return $password
}

function ConvertTo-DecodedExpression {
    # in base64 nessun carattere del valore (apici, anche tipografici) arriva al parser del launcher
    param([string]$Value)
    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Value))
    return "[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('$encoded'))"
}

function Grant-UserAccess {
    param([string]$Path, [string]$Grant)
    & icacls $Path /grant "${UserName}:$Grant" /Q | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "icacls su $Path non riuscito ($LASTEXITCODE)" }
}

function Test-GroupMember {
    param([string]$Sid)
    $members = @(Get-LocalGroupMember -SID $Sid | Where-Object { $_.Name -like "*\$UserName" })
    return $members.Count -gt 0
}

$administrators = 'S-1-5-32-544'
$users = 'S-1-5-32-545'
$password = Get-RandomPassword
if (Get-LocalUser -Name $UserName -ErrorAction SilentlyContinue) {
    # un amministratore esistente non si tocca, nemmeno la password
    if (Test-GroupMember $administrators) { throw "$UserName è nel gruppo Administrators" }
    Set-LocalUser -Name $UserName -Password $password
} else {
    New-LocalUser -Name $UserName -Password $password -PasswordNeverExpires -AccountNeverExpires | Out-Null
}
# New-LocalUser non aggiunge a nessun gruppo: senza Users niente logon locale né lettura di Program Files
if (-not (Test-GroupMember $users)) { Add-LocalGroupMember -SID $users -Member $UserName }
if (Test-GroupMember $administrators) { throw "$UserName è nel gruppo Administrators" }

$workDir = (Get-Location).Path
Grant-UserAccess $workDir '(OI)(CI)M'
if ($env:pythonLocation) { Grant-UserAccess $env:pythonLocation '(OI)(CI)RX' }

$runDir = Join-Path $env:RUNNER_TEMP ('run-as-user-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $runDir | Out-Null
try {
    $lines = @("`$ErrorActionPreference = 'Stop'")
    foreach ($name in $PassEnv) {
        if ($name -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') { throw "nome di variabile non valido: $name" }
        $value = [Environment]::GetEnvironmentVariable($name)
        if ($null -ne $value) { $lines += "`$env:$name = $(ConvertTo-DecodedExpression $value)" }
    }
    $lines += @(
        "Set-Location -LiteralPath ($(ConvertTo-DecodedExpression $workDir))",
        '$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()',
        '$elevated = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)',
        'Write-Output "utente: $env:USERNAME, amministratore: $elevated, HOME: $env:USERPROFILE"',
        'if ($elevated) { exit 97 }',
        "`$ErrorActionPreference = 'Continue'",
        '$global:LASTEXITCODE = $null',
        $Command,
        # un comando che non parte non imposta LASTEXITCODE, ed exit $null varrebbe 0
        'if ($LASTEXITCODE -isnot [int]) { Write-Output "nessun codice di uscita: il comando non è partito"; exit 98 }',
        'exit $LASTEXITCODE'
    )
    $launcher = Join-Path $runDir 'comando.ps1'
    [IO.File]::WriteAllText($launcher, ($lines -join "`r`n"), (New-Object System.Text.UTF8Encoding $true))
    Grant-UserAccess $runDir '(OI)(CI)RX'

    $credential = New-Object Management.Automation.PSCredential ($UserName, $password)
    $stdout = Join-Path $runDir 'stdout.txt'
    $stderr = Join-Path $runDir 'stderr.txt'
    $process = Start-Process -FilePath 'powershell.exe' -Credential $credential -LoadUserProfile -Wait -PassThru `
        -WorkingDirectory $workDir -RedirectStandardOutput $stdout -RedirectStandardError $stderr `
        -ArgumentList @('-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', "`"$launcher`"")
    Get-Content -LiteralPath $stdout
    Get-Content -LiteralPath $stderr | ForEach-Object { [Console]::Error.WriteLine($_) }
    if ($null -eq $process.ExitCode) { throw 'codice di uscita del processo non disponibile' }
    $exitCode = $process.ExitCode
} finally {
    Remove-Item -LiteralPath $runDir -Recurse -Force -ErrorAction SilentlyContinue
}
exit $exitCode
