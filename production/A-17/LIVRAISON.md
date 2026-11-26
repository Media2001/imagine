# A-17 — Livraison

PRET : 10 assertions PHP, 50 assertions natives classic/HPOS, 7 gardes du runner ; 3 tests Python du lanceur. Tous verts, 0 échec. Deux suites complètes exécutées sous Python **3.14.7 natif Windows**, UTF-8 puis console **cp1252**, `PYTHONUTF8=0`, locale cp1252 mesurée. Les enfants Python des tests fixent eux-mêmes UTF-8. PSR-12 strict : 0 erreur/0 avertissement. `wp/tests/preparer-image.ps1` relancé code 0 avant PRET.

Paquet unique : `preuves/final`. Matrice exacte : `windows-matrix.json` et `*-environment.json` dans le paquet ; dernier run cp1252 conservé, reçus UTF-8 agrégés au même paquet. Essais RED/GREEN et mutations hors dépôt. Base complète, options/Action Scheduler et fichiers identiques avant/après, canaris absents, gardes SQL/mail/HTTP/cron/fichiers réellement tentées. Aucun staging/compte/service/secret/archive réel, aucun PHP Windows.

Contrôle : `python wp/tests/a17/verify.py production/A-17/preuves/final`. Rejeu : `python wp/tests/a17/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a17-rejeu-NOUVEAU`. Mode d’emploi : `wp/outils/bascule/a17/README.md`. Deux lignes du mode d’emploi partagé contrôlées seules, sans empreinte du fichier entier. Manifeste restreint au lot ; aucun GO réel.

Décisions prises à défaut : rôles de gestion selon capacités natives ; absence de journal de connexion ou adaptateur 2FA non reconnu = inconnu, jamais zéro. Réglages originaux lus sans exécuter wp-config ; aucun réglage de protection activé, aucun essai de connexion.
