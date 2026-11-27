# Réception T-03 — corrections du 27 novembre 2026

Le document courant est **RECEPTION-CORRECTIONS.md**. **A-20 est dans le rejeu** par consigne postérieure de 7 h 30, sans changement de ses contrôles. L'ancien PRET de 8 h 14 et son paquet complet ont été archivés en Scratch avant cette correction ; ils ne qualifient pas les sources courantes.

**État final : PRET posé par `finaliser.py` après toutes les gates**, manifeste `status:PRET`, `readiness_claimed:true`, `parent_final_gates_pending:false`. A-31/A-32 reçus verts, immuables ; les rouges de 18 h 42 sont historiques. Le lecteur de corrections reste **avant PRET seulement** ; `verify-final.py` est le lecteur final en lecture seule. Aucun hash modifié à la main.

Depuis `C:/Users/Ced/imagine` :

```text
C:/Python314/python.exe -B production/T-03/verify-final.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Exiger PASS, marqueur exact, 12 paquets sans échec/exclusion ; OUTILS 22/791 et REJEU 1204 tests/36667 assertions PASS. Le code 0 global seul ne suffit pas. Voir `FINALISATION.md`.

Reçu postPRET hors paquet : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-final-20261127-postPRET/reception.json` (deux consoles sans TMPDIR, SHA-256 exacts avant/après). Le parent peut refaire sa propre réception sans mutation. Aucun lot voisin rescellé, aucun fichier commun gelé changé ; verrou parent intact. Aucun GO.
