<#
.SYNOPSIS
Avvia Claude Code con Mímir attivo su Windows nativo, senza sandbox.

.DESCRIPTION
Come bin/claude-mimir: regole (CLAUDE.md di Mímir), plugin letti da plugins/ a ogni avvio, regole
ask/deny e hook su commit, push e tag. Se mimir@mimir o brokkr@mimir sono anche installati, tienili
disabilitati: sarebbero una seconda copia.
Su Windows nativo la sandbox non esiste e con failIfUnavailable Claude Code non parte: il launcher
passa a --settings sandbox\windows.settings.json, cioè sandbox.settings.json con la sandbox spenta in
modo esplicito, così non vale nemmeno un blocco sandbox dei settings personali. Il file sta in sandbox\,
dove install.py chiede conferma per Edit e Write; si confronta a ogni avvio con quello calcolato e si
riscrive se è diverso, perché senza sandbox Claude può modificarlo con la shell.
Non esporta MIMIR_MAVEN_SETTINGS: l'hook di Maven la legge come segno di una sessione nella sandbox e
farebbe lanciare le build offline.

Scritto per Windows PowerShell 5.1, in UTF-8 con BOM come install.ps1. Senza param(): tutti gli
argomenti arrivano in $args e passano a claude. Limite della 5.1: verso i programmi nativi gli
argomenti vuoti si perdono e i doppi apici dentro un argomento non arrivano.

.EXAMPLE
powershell -NoProfile -ExecutionPolicy Bypass -File bin\claude-mimir.ps1 --add-dir C:\progetti\app

.EXAMPLE
powershell -NoProfile -ExecutionPolicy Bypass -File bin\claude-mimir.ps1 agents
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$MimirDir = Split-Path -Parent $PSScriptRoot
$SourceSettings = Join-Path $MimirDir 'sandbox.settings.json'
$WindowsSettings = Join-Path (Join-Path $MimirDir 'sandbox') 'windows.settings.json'
$Utf8NoBom = New-Object System.Text.UTF8Encoding $false

function Write-Notice {
    param([string]$Message)
    [Console]::Error.WriteLine($Message)
}

function Get-WindowsSettingsJson {
    $text = [IO.File]::ReadAllText($SourceSettings, [Text.Encoding]::UTF8)
    # ConvertFrom-Json srotola un array: [{...}] passerebbe per l'oggetto
    if (-not $text.TrimStart().StartsWith('{')) {
        throw 'sandbox.settings.json non contiene un oggetto JSON'
    }
    $settings = $text | ConvertFrom-Json
    $settings | Add-Member -NotePropertyName 'sandbox' -NotePropertyValue ([PSCustomObject]@{ enabled = $false }) -Force
    return $settings | ConvertTo-Json -Depth 10
}

function Sync-WindowsSettingsFile {
    param([string]$Json)
    # Confronto ordinale sul testo letto byte per byte: un BOM aggiunto conta come modifica. -cne
    # confronta secondo la cultura e ignora i caratteri come il BOM (U+FEFF).
    $current = $null
    if (Test-Path -LiteralPath $WindowsSettings -PathType Leaf) {
        $current = [Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($WindowsSettings))
    }
    if (-not [string]::Equals($current, $Json, [StringComparison]::Ordinal)) {
        [IO.File]::WriteAllText($WindowsSettings, $Json, $Utf8NoBom)
    }
}

Write-Notice '! Windows nativo: comandi senza sandbox, con rete e file (credenziali comprese) liberi per la shell. Restano attivi le regole ask/deny degli strumenti di Claude e gli hook di Mímir; per la protezione completa usa WSL2.'

try {
    Sync-WindowsSettingsFile (Get-WindowsSettingsJson)
} catch {
    Write-Notice "! impossibile preparare $WindowsSettings da sandbox.settings.json: $($_.Exception.Message)"
    exit 1
}

# il percorso risolto, non il nome: una funzione o un alias claude del profilo non devono prevalere
$claude = Get-Command 'claude' -CommandType Application, ExternalScript -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($null -eq $claude) {
    Write-Notice '! claude non trovato nel PATH: installa Claude Code e rilancia.'
    exit 1
}

$env:CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD = '1'
# passaggi di consegne tra sessioni (hook handoff.py, Ratatoskr): senza, l'hook non fa nulla.
# Fuori da Mímir, come in bin/claude-mimir, anche se qui la sandbox non c'è. Dalla variabile, come
# XDG_STATE_HOME in bin/claude-mimir: GetFolderPath nella 5.1 restituisce '' se la cartella non esiste.
# Senza percorso il passaggio resta spento e claude parte lo stesso.
# Con -p/--print no, e si toglie anche se arriva dall'ambiente (un -p lanciato da una sessione del
# launcher): SessionStart archivierebbe il passaggio della cartella senza che nessuno lo veda.
# Un prompt uguale a "-p" spegne i passaggi per quel lancio: caso accettato.
$printMode = $false
foreach ($arg in $args) {
    if ($arg -ceq '-p' -or $arg -ceq '--print') {
        $printMode = $true
    }
}
if ($printMode) {
    Remove-Item Env:MIMIR_HANDOFF_DIR -ErrorAction SilentlyContinue
} elseif ([string]::IsNullOrEmpty($env:LOCALAPPDATA)) {
    Write-Notice '! LOCALAPPDATA non impostata: passaggio di consegne tra sessioni (Ratatoskr) spento.'
} else {
    $env:MIMIR_HANDOFF_DIR = Join-Path (Join-Path $env:LOCALAPPDATA 'mimir') 'handoff'
}
$mimirArgs = @('--settings', $WindowsSettings, '--add-dir', $MimirDir, '--plugin-dir', (Join-Path $MimirDir 'plugins'))

$userArgs = @($args)
if ($userArgs.Count -gt 0 -and $userArgs[0] -ceq 'agents') {
    $claudeArgs = @('agents') + $mimirArgs + @($userArgs | Select-Object -Skip 1)
} else {
    $claudeArgs = $mimirArgs + $userArgs
}
& $claude.Source @claudeArgs
exit $LASTEXITCODE
