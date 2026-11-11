# IMAGINE - relecture independante d'un lot (ou de tous ceux qui sont PRET)
# Usage manuel :  powershell -ExecutionPolicy Bypass -File scripts\relire.ps1 -Lot lot-01
# Sans -Lot : traite tous les dossiers production\<lot> qui ont PRET et pas encore de relecture.
# Ordre : installation des dependances de test (dans Docker) -> Codex relit -> Claude Code relit -> Claude Code fusionne.
# Si Hermes redepose PRET apres les corrections : passe de verification par Claude (2e et dernier tour).
# Au-dela : rien d'automatique, le lot remonte a Ced.
# Chaque relecteur lit son fichier de role dans relecteurs\ et n'ecrit que son rapport.
# Journal : %LOCALAPPDATA%\IMAGINE\relire.log

param([string]$Lot = '')

$ErrorActionPreference = 'Continue'
$repo   = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $env:LOCALAPPDATA 'IMAGINE'
New-Item -ItemType Directory -Force $logDir | Out-Null
$log    = Join-Path $logDir 'relire.log'
function Write-Log($m) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m" | Add-Content -Encoding utf8 $log; Write-Host $m }

# Options supplementaires pour Codex : a ajuster selon la version
$CodexExtra = @('-c', 'model_reasoning_effort="high"', '-c', 'web_search="live"')
# Modele Claude des relecteurs
$ClaudeModel = 'opus'
# Outils communs des relecteurs Claude : lecture, recherche, lancement des tests. Aucune ecriture hors rapport.
$ClaudeRead = @('Read', 'Glob', 'Grep', 'WebSearch', 'WebFetch', 'Bash(docker compose run --rm:*)')

$lock = Join-Path $repo '.relire.lock'
if (Test-Path $lock) {
    if ((Get-Item $lock).LastWriteTime -gt (Get-Date).AddHours(-3)) { Write-Log 'relecture deja en cours, on saute'; exit 0 }
    Remove-Item $lock -Force
}
New-Item $lock -ItemType File | Out-Null

try {
    Set-Location $repo
    $prodRoot = Join-Path $repo 'production'
    if ($Lot) { $lots = @($Lot) }
    else { $lots = Get-ChildItem $prodRoot -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'PRET') } | ForEach-Object { $_.Name } }

    # 0. Dependances de test (vendor/ n'est pas versionne) : dans le conteneur php, une fois par extension qui a un composer.json
    if ($lots -and (Get-Command docker -ErrorAction SilentlyContinue)) {
        Get-ChildItem (Join-Path $repo 'wp\plugins') -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName 'composer.json') } | ForEach-Object {
            & docker compose run --rm -w "/app/$($_.Name)" php composer install --no-interaction --quiet 2>&1 | Out-File -Encoding utf8 (Join-Path $logDir "composer-$($_.Name).txt")
            if ($LASTEXITCODE -ne 0) { Write-Log "ERREUR composer install dans $($_.Name) (voir composer-$($_.Name).txt)" }
        }
    }
    elseif ($lots) { Write-Log 'docker introuvable : les relecteurs ne pourront pas lancer les tests' }

    foreach ($s in $lots) {
        $prod = "production/$s"
        $rel  = "relectures/$s"
        $corr = "corrections/$s.md"
        if (-not (Test-Path (Join-Path $repo "$prod/PRET"))) { Write-Log "$s : pas de PRET, ignore"; continue }
        $briefFile = Get-ChildItem (Join-Path $repo 'briefs') -Filter "$s*.md" | Select-Object -First 1
        if (-not $briefFile) { Write-Log "$s : ERREUR aucun brief briefs/$s*.md, ignore"; continue }
        $brief = "briefs/$($briefFile.Name)"
        New-Item -ItemType Directory -Force (Join-Path $repo $rel) | Out-Null

        # 1. Codex
        if (-not (Test-Path (Join-Path $repo "$rel/codex.md"))) {
            Write-Log "$s : relecture Codex..."
            $p = "Tu es le relecteur Codex independant. Lis relecteurs/AGENTS.md et applique-le strictement au lot $s : brief $brief, production dans $prod et dans wp/. Lance les tests du lot si le brief en prevoit. Ecris ton rapport UNIQUEMENT dans $rel/codex.md, au format de doctrine/grille-relecture.md, en francais. Ne lis pas $rel/claude.md. Ne modifie aucun autre fichier."
            & codex exec --sandbox workspace-write @CodexExtra $p 2>&1 | Out-File -Encoding utf8 (Join-Path $logDir "codex-$s.txt")
            if (Test-Path (Join-Path $repo "$rel/codex.md")) { Write-Log "$s : codex.md ecrit" } else { Write-Log "$s : ERREUR codex.md absent (voir codex-$s.txt)" }
        }

        # 2. Claude Code
        if (-not (Test-Path (Join-Path $repo "$rel/claude.md"))) {
            Write-Log "$s : relecture Claude..."
            $p = "Tu es le relecteur Claude independant. Lis relecteurs/CLAUDE.md et applique-le strictement au lot $s : brief $brief, production dans $prod et dans wp/. Lance les tests du lot si le brief en prevoit (docker compose run --rm -w /app/<extension> php composer test) et deroule a la main les cas du cahier des charges. Ecris ton rapport UNIQUEMENT dans $rel/claude.md, au format de doctrine/grille-relecture.md. N'ouvre PAS $rel/codex.md. Ne fais pas encore la fusion."
            & claude -p $p --model $ClaudeModel --allowedTools @ClaudeRead "Write(/relectures/**)" "Edit(/relectures/**)" 2>&1 | Out-File -Encoding utf8 (Join-Path $logDir "claude-$s.txt")
            if (Test-Path (Join-Path $repo "$rel/claude.md")) { Write-Log "$s : claude.md ecrit" } else { Write-Log "$s : ERREUR claude.md absent (voir claude-$s.txt)" }
        }

        # 3. Fusion par Claude Code
        if ((Test-Path (Join-Path $repo "$rel/codex.md")) -and (Test-Path (Join-Path $repo "$rel/claude.md")) -and -not (Test-Path (Join-Path $repo $corr))) {
            Write-Log "$s : fusion..."
            $p = "Tu es le fusionneur. Lis relecteurs/CLAUDE.md (etape 5) et doctrine/grille-relecture.md (format de fusion). Les deux rapports existent : $rel/claude.md et $rel/codex.md. La ou ils divergent, tranche en relisant le code et le cahier des charges. Ecris la fusion UNIQUEMENT dans $corr. Termine par le rappel : un verdict n'est pas un GO."
            & claude -p $p --model $ClaudeModel --allowedTools @ClaudeRead "Write(/corrections/**)" "Edit(/corrections/**)" 2>&1 | Out-File -Encoding utf8 (Join-Path $logDir "fusion-$s.txt")
            if (Test-Path (Join-Path $repo $corr)) { Write-Log "$s : fusion ecrite" } else { Write-Log "$s : ERREUR fusion absente (voir fusion-$s.txt)" }
        }

        # 4. Passe de verification (2e et dernier tour) : PRET plus recent que les corrections
        $pretF = Join-Path $repo "$prod/PRET"; $corrF = Join-Path $repo $corr; $verF = Join-Path $repo "$rel/verification.md"
        if ((Test-Path $corrF) -and ((Get-Item $pretF).LastWriteTime -gt (Get-Item $corrF).LastWriteTime)) {
            if (-not (Test-Path $verF)) {
                Write-Log "$s : passe de verification..."
                $p = "Tu es le verificateur (2e et dernier tour). Le lot $s a ete corrige par Hermes apres la fusion $corr. Lis relecteurs/CLAUDE.md et doctrine/doctrine.md. Utilise git log et git diff sur wp/ et sur $prod pour voir exactement ce qui a change depuis la version relue. Relance les tests. Ecris UNIQUEMENT $rel/verification.md avec : (1) pour chaque instruction de $corr : Appliquee / Non appliquee / Partiellement, avec le fichier et la ligne ; (2) le resultat des tests ; (3) toute regression ou modification non demandee ; (4) verdict : 'Pret pour la validation de Ced' ou 'Remonte a Ced' (probleme de fond restant). Ne refais pas une relecture complete."
                & claude -p $p --model $ClaudeModel --allowedTools @ClaudeRead "Bash(git log:*)" "Bash(git diff:*)" "Bash(git show:*)" "Write(/relectures/**)" "Edit(/relectures/**)" 2>&1 | Out-File -Encoding utf8 (Join-Path $logDir "verification-$s.txt")
                if (Test-Path $verF) { Write-Log "$s : verification ecrite" } else { Write-Log "$s : ERREUR verification absente (voir verification-$s.txt)" }
            }
            elseif ((Get-Item $pretF).LastWriteTime -gt (Get-Item $verF).LastWriteTime) {
                Write-Log "$s : 3e tour demande -> pas de nouvelle relecture automatique, remonte a Ced"
            }
        }
    }
}
finally { Remove-Item $lock -Force -ErrorAction SilentlyContinue }
