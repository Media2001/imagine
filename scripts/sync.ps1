# IMAGINE - synchronisation Git du NUC
# Lance par le Planificateur de taches toutes les 5 minutes.
# 1. commit de ce que le NUC a produit (wp, production, relectures, corrections, files)
# 2. recuperation de ce que Claude a pousse (briefs, doctrine...)
# 3. envoi sur GitHub
# Ne force jamais rien : en cas de conflit, il s'arrete et l'ecrit dans le journal.
# Journal : %LOCALAPPDATA%\TUM\sync.log

$ErrorActionPreference = 'Continue'
$repo   = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $env:LOCALAPPDATA 'IMAGINE'
New-Item -ItemType Directory -Force $logDir | Out-Null
$log    = Join-Path $logDir 'sync.log'
function Write-Log($m) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m" | Add-Content -Encoding utf8 $log }

# Verrou : une seule synchro a la fois (verrou de plus de 30 min = abandonne)
$lock = Join-Path $repo '.sync.lock'
if (Test-Path $lock) {
    if ((Get-Item $lock).LastWriteTime -gt (Get-Date).AddMinutes(-30)) { Write-Log 'verrou present, on saute'; exit 0 }
    Remove-Item $lock -Force
}
New-Item $lock -ItemType File | Out-Null

try {
    Set-Location $repo

    # 1. Ce que le NUC a le droit de pousser
    git add -- wp production relectures corrections files 2>$null
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit -q -m "NUC : synchro $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        Write-Log 'commit local cree'
    }

    # 2. Recuperer les nouveautes (les autres fichiers modifies sont mis de cote puis remis)
    git pull --rebase --autostash -q origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        git rebase --abort 2>$null
        Write-Log 'ERREUR : conflit pendant la recuperation. Intervention manuelle necessaire, rien n a ete force.'
        exit 1
    }

    # 3. Envoyer
    git push -q origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Log 'ERREUR : envoi refuse'; exit 1 }

    Write-Log 'ok'
}
catch { Write-Log "ERREUR : $_"; exit 1 }
finally { Remove-Item $lock -Force -ErrorAction SilentlyContinue }
