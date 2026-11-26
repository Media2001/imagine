# T-02 — remise de correction au parent

**État courant : correction vérifiée, sans PRET, non clos.** L’ancien marqueur a été retiré. Aucun gate parent n’est revendiqué dans cette passe ; les anciennes preuves de préparation ont été déplacées hors dépôt avec l’ancien paquet.

Rejeu réel `wp/tests/rejouer.ps1` : **1 123 tests PHPUnit, 34 569 assertions ; 14 outils, 279 contrôles ; zéro échec, erreur ou ignoré**, en UTF-8 et cp1252. T-02 : **24/24 contrats PHP**, **7/7 contrats de sortie** ; suppression de la garde dans un miroir : **5 échecs détectés**, reçu mixte indûment PASS, puis restauration exacte et PASS réel. Les matrices natives restent hors de ce rejeu.

Paquet unique : `production/T-02/preuves/final/`. Commandes, sorties complètes et empreintes internes cohérentes incluses ; anciennes sorties candidates retirées. Python natif : `C:/Python314/python.exe`, **3.14.6**, encodages mesurés. `production/T-02/verifier.py` est en lecture seule, compatible avec le futur marqueur parent ; il vérifie les preuves de correction, jamais les gates futures. Le parent reste responsable de la préparation commune, du rejeu après intégration et de PRET.

L’intégration des neuf assertions pures A-19 dans PHPUnit est rattachée à **T-02**, conformément à la file de 10 h 30. Raccord existant réutilisé, pas de doublon. A-19 : schéma de passerelle inconnu conservé distinct de moyen absent (défaut prudent), question métier seulement.
