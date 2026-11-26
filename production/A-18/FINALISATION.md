# A-18 — finalisation parent

**État courant : prêt à relire, non clos.** La préparation commune et le rejeu final sont exécutés ; les mentions de gates en attente des reçus candidats décrivent uniquement la remise antérieure et sont remplacées par ce document et `preuves/final/parent-final.json`.

Préparation `wp/tests/preparer-image.ps1` : code 0. Rejeu `wp/tests/rejouer.ps1` : **1 123 tests PHPUnit, 34 569 assertions ; 13 outils, 242 contrôles ; zéro échec, erreur ou ignoré**, dans les deux contextes UTF8 et cp1252. Les matrices natives restent distinctes de ce rejeu. Aucune opération sur le réel, archive, compte ou déploiement.

Paquet unique : `production/A-18/preuves/final/`. Commandes et sorties intégrales de préparation/rejeu incluses. Python natif des matrices : `C:/Python314/python.exe`, **3.14.6**, encodages mesurés dans les reçus. Une vérification parent des sources courantes et des empreintes du paquet précède le marqueur PRET.

Arbitrage de 10 h appliqué : la marque de neutralisation reste inchangée, aucune question pour Imagine sur notre import. Défaut `reading_denied=null` acquis, écart déjà reporté par Claude ; aucun fichier `docs/` modifié. Le parcours natif `cli_and_actual_readonly_guards` lance exactement les trois arguments de la ligne documentée (`--wp-path`, `--audit`, `--output`), sans argument supplémentaire.
