# A-21 — finalisation parent

**État courant : sources intégrées au gardien commun A22, nouvelles matrices en cours ; aucun PRET.** L’ancien PRET a été retiré. Les lignes de préparation/rejeu ci-dessous sont historiques, invalidées pour les nouvelles sources ; elles ne sont pas des gates exécutées par cet enfant. Un nouveau paquet scellé remplacera l’ancien après le retour réel des matrices.

Préparation `wp/tests/preparer-image.ps1` : code 0. Rejeu `wp/tests/rejouer.ps1` : **1 123 tests PHPUnit, 34 569 assertions ; 13 outils, 242 contrôles ; zéro échec, erreur ou ignoré**, dans les deux contextes UTF8 et cp1252. Les matrices natives restent distinctes de ce rejeu. Aucune opération sur le réel, archive, compte ou déploiement.

Paquet unique : `production/A-21/preuves/final/`. Commandes et sorties intégrales de préparation/rejeu incluses. Python natif des matrices : `C:/Python314/python.exe`, **3.14.6**, encodages mesurés dans les reçus. Une vérification parent des sources courantes et des empreintes du paquet précède le marqueur PRET.
