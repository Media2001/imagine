## Réception des formalités du parent

La préparation commune a réellement terminé code **0** le **26 novembre 2026 à 00:45:29 CET** : reçu `production/A-11/preparer-image-parent.json`, journal `.log`, image T01 vérifiée. Le README partagé contient les deux lignes exactes d'`integration.md` après les ajouts A-10/A-11 ; la commande reste le lanceur Landlock `python3 wp/outils/bascule/a12/confine.py`, jamais le PHP brut.

Nouveau rejeu natif et contrôle PSR-12 strict, sans modifier les sources A-12 ni A-11. Le paquet courant unique est `preuves/final/` avec baseline intégré réellement observé ; 118 assertions natives, 7 unitaires, 7 runner, 6 style et 41 intégrité PASS. L'ancien paquet et ses baselines restent byte à byte au scratch `a10-a13-reception/historical/A-12/`. Les comparaisons strictes des dépendances sont conservées, sans exception README.

Réception PRET sans réserve technique connue. Contrôle parent : `python -B production/A-10/verifier-reception.py`. Aucun accès réel, aucune préparation partagée supplémentaire, aucun Git ni modification de verrou.
