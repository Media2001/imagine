# A-16 — finalisation parent

**État courant : prêt à relire, non clos.** La préparation commune et le rejeu final sont exécutés ; les mentions de gates en attente des reçus candidats décrivent uniquement la remise antérieure et sont remplacées par ce document et `preuves/final/parent-final.json`.

Préparation `wp/tests/preparer-image.ps1` : code 0. Rejeu `wp/tests/rejouer.ps1` : **1 123 tests PHPUnit, 34 569 assertions ; 13 outils, 242 contrôles ; zéro échec, erreur ou ignoré**, dans les deux contextes UTF8 et cp1252. Les matrices natives restent distinctes de ce rejeu. Aucune opération sur le réel, archive, compte ou déploiement.

Paquet unique : `production/A-16/preuves/final/`. Commandes et sorties intégrales de préparation/rejeu incluses. Python natif des matrices : `C:/Python314/python.exe`, **3.14.6**, encodages mesurés dans les reçus. Une vérification parent des sources courantes et des empreintes du paquet précède le marqueur PRET.
