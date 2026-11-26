# A-16 — Livraison

PRET : 7 assertions PHP, 54 assertions natives classic/HPOS, 7 gardes du runner ; 3 tests Python du lanceur. Tous verts, 0 échec. Deux suites complètes exécutées sous Python **3.14.7 natif Windows**, UTF-8 puis console **cp1252**, `PYTHONUTF8=0`, locale cp1252 mesurée. Les enfants Python des tests fixent eux-mêmes UTF-8. PSR-12 strict : 0 erreur/0 avertissement. `wp/tests/preparer-image.ps1` relancé code 0 avant PRET.

Paquet unique : `preuves/final`. Matrice exacte : `windows-matrix.json` et `*-environment.json` dans le paquet ; dernier run cp1252 conservé, reçus UTF-8 agrégés au même paquet. Essais RED/GREEN et mutations hors dépôt. Base complète, options/Action Scheduler et fichiers identiques avant/après, canaris absents, gardes SQL/mail/HTTP/cron/fichiers réellement tentées. Aucun staging/compte/service/secret/archive réel, aucun PHP Windows.

Contrôle : `python wp/tests/a16/verify.py production/A-16/preuves/final`. Rejeu : `python wp/tests/a16/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a16-rejeu-NOUVEAU`. Mode d’emploi : `wp/outils/bascule/a16/README.md`. Deux lignes du mode d’emploi partagé contrôlées seules, sans empreinte du fichier entier. Manifeste restreint au lot ; aucun GO réel.

Décisions prises à défaut : dates UTC, tous états, égalité par ID décroissant ; fichiers PDF dans uploads = emplacement public, pas preuve HTTP. Liaison opérateur postmeta, post_parent ou taxonomie, sans déduction ; fichiers locaux originaux seulement, médias rattachés via post_parent aux articles. Clé absente, valeur non scalaire ou date ambiguë : refus nommé, jamais valeur révélée. Aucun rattachement.
