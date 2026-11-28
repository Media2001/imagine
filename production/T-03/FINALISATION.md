# T-03 — finalisation et lecture de l'état PRET

La consigne du 28 novembre 2026, 7 h 30 autorise la clôture après le nouveau PRET d'A-33. A-31/A-32/A-33 restent immuables pendant T-03. **A-20 est inclus**. Aucun fichier t01/rejouer/import/gardien/outil clos/voie 2 modifié. Les anciens paquets sont historiques dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-cloture-20261128/historique-T03/` ; paquet unique `preuves/final/`.

Le lecteur final ne compare plus les photographies des paquets voisins ou des dossiers gelés à leurs fichiers courants. Ces photographies deviennent un reçu daté de préservation au sceau (`cloture/preservation-receipt.json`). Le lecteur vérifie toujours les fichiers propres et la liste fermée `OWN_TOOLS` de `qualifier-corrections.py`, tous les reçus et le marqueur exact. Après clôture, un nouveau paquet voisin ne demande aucun rescellage de T-03.

## Séquence finale

1. Qualification sur les sources finales : `qualifier-corrections.py --output <nouveau-Scratch> --nominal`, 14 commandes, UTF-8/cp1252 sans TMPDIR mesuré ; remplacement du seul paquet courant.
2. `native-copy-proof.ps1 -Output <nouveau-Scratch>` : 13 paquets verts, A-32/A-33 compris, puis exactement un octet A-28 sur copie jetable, A-28 PACKAGE_DRIFT seul, dernier REJEU identique ; deux conteneurs/copie absents, reçu original intact. Preuve dans `preuves/final/native/`.
3. `test-cloture.py` (4 tests), `test-finalisation.py` (4 tests), dans les deux consoles ; parse PowerShell et préparation image. Exits/flux/sources dans `preuves/final/cloture/closure-checks.json`. Le test ajouté conserve les preuves authentiques et change seulement l'arbre vivant des voisins : lecture inchangée. Gel exact import/t01 et A-31/A-32/A-33 relu une fois au reçu.
4. `sceller-candidat.py` puis `finaliser.py` : lecteur candidat et toutes les gates, calcul du manifeste final, contrôle avant marqueur, pose PRET, lecture finale. Rollback manifeste/marqueur sur erreur ; aucune empreinte manuelle.
5. Réception séparée postPRET hors paquet : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-cloture-20261128/postpret/reception.json`, deux rejeux séquentiels et inventaire exact avant/après. Ne pas la réinjecter dans le sceau.

L'état final est `status:PRET`, `readiness_claimed:true`, `parent_final_gates_pending:false` ; `pret_sha256` lie le marqueur exact. Une commande rouge laisse le candidat sans PRET et la livraison incomplète.

## Commandes parent read-only, depuis C:/Users/Ced/imagine

```text
C:/Python314/python.exe -B production/T-03/verify-final.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Exiger lecteur PASS et PRET exact ; PAQUETS 13 vérifiés, 0 échecs, aucune exclusion ; A-20…A-28/A-30/A-31/A-32/A-33 présents ; OUTILS vert, REJEU PASS, conteneur absent. Pas de runner concurrent.

`verify-corrections.py` reste **avant PRET seulement** : son refus après PRET est intentionnel. Le lecteur final réutilise ses assertions d'évidence sans assouplir son entrée publique. Aucun `verify.py`/`rejeu.json` T-03 ajouté : pas de paquet T-03 opt-in supplémentaire. Matrices métier natives hors rejeu. Aucun GO réel.
