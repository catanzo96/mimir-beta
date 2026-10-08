<#
.SYNOPSIS
Collega Mímir a Claude Code su Windows: trova Python 3.8+ e Git for Windows, poi lancia install.py.

.DESCRIPTION
Se mancano Python o Git propone di installarli con winget. Lancia install.py con -I, come install.sh:
la cartella di Mímir è scrivibile dalla sandbox e l'installer gira fuori, quindi non deve importare
moduli piantati accanto a sé. Su Windows nativo la sandbox di Claude Code non esiste: alla fine
propone WSL2 (wsl --install), solo con una risposta sì o con -InstallWsl, mai implicito con -Yes.
Si lancia da utente normale: da amministratore si ferma, perché install.py e i programmi del PATH,
che senza sandbox una sessione di Claude può modificare, girerebbero elevati. Per WSL eleva solo
wsl --install (richiesta UAC).

Scritto per Windows PowerShell 5.1: niente &&, ||, ??, ternario né parametri solo di pwsh 7.
Il file è in UTF-8 con BOM, perché la 5.1 legge i .ps1 senza BOM come ANSI.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File install.ps1
#>
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '',
    Justification = 'installer interattivo: con Write-Output i messaggi finirebbero nei valori restituiti dalle funzioni')]
[CmdletBinding()]
param(
    # risponde sì alle conferme (per la CI); non vale per WSL
    [switch]$Yes,
    # salta winget e WSL
    [switch]$SkipSystem,
    # propone WSL2 senza chiedere
    [switch]$InstallWsl
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$MimirDir = $PSScriptRoot
$PythonCandidates = @(
    @{ Exe = 'py'; Prefix = @('-3') },
    @{ Exe = 'python'; Prefix = @() }
)

function Confirm-Step {
    param([string]$Question, [bool]$AssumeYes)
    if ($AssumeYes) { return $true }
    # come install.py: input chiuso o risposta diversa da sì valgono no
    if ([Console]::IsInputRedirected) {
        Write-Host "$Question [s/N] "
        $answer = [Console]::In.ReadLine()
    } else {
        $answer = Read-Host "$Question [s/N]"
    }
    if ($null -eq $answer) { return $false }
    return @('s', 'si', 'sì', 'y', 'yes') -contains $answer.Trim().ToLower()
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue)
}

function Find-Python {
    # Lo stub dello Store (python.exe in WindowsApps) esiste nel PATH ma esce con 9009: ogni
    # candidato si prova davvero. In 5.1, con 'Stop', lo stderr di un programma nativo
    # rediretto diventa un errore che interrompe lo script: qui vale 'Continue'.
    $ErrorActionPreference = 'Continue'
    $versionCheck = 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'
    foreach ($candidate in $PythonCandidates) {
        if (-not (Test-Command $candidate.Exe)) { continue }
        # un alias dello Store rotto non si avvia: è un errore, non un codice di uscita
        try {
            & $candidate.Exe @($candidate.Prefix) -I -c $versionCheck 2>&1 | Out-Null
            $exitCode = $LASTEXITCODE
        } catch {
            continue
        }
        if ($exitCode -eq 0) { return $candidate }
    }
    return $null
}

function Update-SessionPath {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseShouldProcessForStateChangingFunctions', '',
        Justification = 'cambia solo il PATH di questo processo')]
    param()
    # Dopo winget il PATH di questa sessione è vecchio: prima le voci del registro, nell'ordine di
    # Windows (Machine, User: il Python appena installato precede lo stub di WindowsApps), poi quelle
    # della sola sessione; senza duplicati né voci vuote, che potrebbero valere come cartella corrente.
    if ($env:OS -ne 'Windows_NT') { return }
    $sources = @(
        [Environment]::GetEnvironmentVariable('Path', 'Machine'),
        [Environment]::GetEnvironmentVariable('Path', 'User'),
        $env:Path
    )
    $entries = New-Object System.Collections.Generic.List[string]
    foreach ($entry in (($sources | Where-Object { $_ }) -join ';') -split ';') {
        $entry = $entry.Trim()
        if ($entry -and -not ($entries -contains $entry)) { $entries.Add($entry) }
    }
    $env:Path = $entries -join ';'
}

function Install-WithWinget {
    param([string]$Id, [string]$Name)
    if (-not (Test-Command 'winget')) {
        Write-Host "! winget non trovato: installa $Name a mano e rilancia install.ps1"
        return $false
    }
    if (-not (Confirm-Step "Manca $Name. Lo installo con: winget install --id $Id -e?" $Yes)) {
        return $false
    }
    $wingetArgs = @('install', '--id', $Id, '-e', '--source', 'winget')
    if ($Yes) { $wingetArgs += @('--accept-source-agreements', '--accept-package-agreements') }
    # Out-Host: altrimenti l'output di winget (compresi i suoi prompt) finisce nel valore restituito
    & winget @wingetArgs | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host "! installazione di $Name non riuscita (winget: $LASTEXITCODE)"
        return $false
    }
    Update-SessionPath
    return $true
}

function Get-Wsl2DistroName {
    # Le distro registrate stanno in HKCU\...\Lxss; Version 2 = WSL2. Le distro interne di Docker
    # Desktop non servono a Mímir. Da verificare su Windows vero.
    $key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss'
    if (-not (Test-Path $key)) { return @() }
    return @(Get-ChildItem $key | ForEach-Object { Get-ItemProperty $_.PSPath } |
        Where-Object { ($_.PSObject.Properties.Name -contains 'Version') -and $_.Version -eq 2 } |
        ForEach-Object { $_.DistributionName } | Where-Object { $_ -notlike 'docker-desktop*' })
}

function Test-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    return ([Security.Principal.WindowsPrincipal]$identity).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Show-WslInstruction {
    Write-Host @"

Per la protezione completa (sandbox), dentro WSL2:
  sudo apt-get install git python3
  git clone <url del repo> ~/mimir
  ~/mimir/install.sh
  ~/mimir/bin/claude-mimir
"@
}

if ($env:OS -eq 'Windows_NT' -and (Test-Administrator)) {
    Write-Host '✗ install.ps1 è in esecuzione come amministratore: non serve, e farebbe girare install.py e i programmi del PATH con privilegi elevati.'
    Write-Host "  Chiudi questa finestra, apri PowerShell senza 'Esegui come amministratore' e lancia:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit 1
}

$problems = @()

# 1. Python 3.8+
$python = Find-Python
if ($null -eq $python -and -not $SkipSystem) {
    if (Install-WithWinget 'Python.Python.3.13' 'Python 3') { $python = Find-Python }
}
if ($null -eq $python) {
    Write-Host '✗ Python 3.8+ non trovato (py -3 o python). Installalo, riapri il terminale e rilancia install.ps1.'
    exit 1
}

# 2. Git for Windows: gli hook di Mímir girano con il suo bash; senza, i controlli sui commit non partono
if (-not (Test-Command 'git')) {
    if ($SkipSystem -or -not (Install-WithWinget 'Git.Git' 'Git for Windows') -or -not (Test-Command 'git')) {
        Write-Host '! Git for Windows non trovato: gli hook di Mímir non partono. Se winget l''ha appena installato, riapri il terminale e rilancia.'
        $problems += 'Git for Windows'
    }
}

# 3. install.py, con gli stessi flag
$installArgs = @()
if ($Yes) { $installArgs += '--yes' }
if ($SkipSystem) { $installArgs += '--skip-system' }
& $python.Exe @($python.Prefix) -I (Join-Path $MimirDir 'install.py') @installArgs
if ($LASTEXITCODE -ne 0) { $problems += 'install.py' }

# 4. WSL2: mai implicito con -Yes
if (-not $SkipSystem) {
    $distros = @(Get-Wsl2DistroName)  # un array vuoto restituito da una funzione diventa $null
    if ($distros.Count -gt 0) {
        Write-Host "✓ WSL2 presente ($($distros -join ', '))"
        Show-WslInstruction
    } elseif ($InstallWsl -or (-not $Yes -and (Confirm-Step 'Attivo WSL2 (wsl --install, serve un riavvio)?' $false))) {
        # la richiesta UAC eleva solo wsl --install, non questo script
        $wsl = Join-Path $env:SystemRoot 'System32\wsl.exe'
        try {
            $process = Start-Process -FilePath $wsl -ArgumentList '--install' -Verb RunAs -Wait -PassThru
            if ($process.ExitCode -eq 0) {
                Write-Host 'Riavvia Windows, apri la distro installata e segui i passi qui sotto.'
            } else {
                Write-Host "! wsl --install non riuscito (codice $($process.ExitCode))"
                $problems += 'WSL2'
            }
        } catch {
            Write-Host "! wsl --install non avviato ($($_.Exception.Message)): lancialo da un PowerShell da amministratore."
            $problems += 'WSL2'
        }
        Show-WslInstruction
    }
}

if ($problems.Count -gt 0) {
    Write-Host "`n✗ Da sistemare: $($problems -join ', '). Rilancia install.ps1 dopo averli sistemati."
    exit 1
}
exit 0
