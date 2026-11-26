# A-24 — corrections du réveil du 26 novembre 2026

- **Fait :** comparaison et oracles corrigés ; vrai changement de contenu ajouté ; SHA documentaire et portée réalignés ; prérequis Windows explicités.
- **Prêt à relire :** code et contrôles locaux ; **aucun PRET déposé**.
- **À arbitrer par Ced :** aucune question métier ; aucun GO sur le réel demandé ni utilisé.
- **Restant :** matrice native classique/HPOS dans les deux encodages et reseal, réservés au parent qui sérialise les bancs.
- **Ensuite :** commandes exactes dans `COMMANDES.md`, sans requalifier l’ancien paquet.

## Application des sept instructions

1. `Analysis.php` retire, uniquement pour comparer, les espacements Unicode (`\p{Z}` et `\s`, bords et intérieur), puis compare sans distinction de casse simple Unicode avec PCRE `/iu`. Pas de mbstring/intl, pas de translittération : accents, ponctuation et contenu distinct restent significatifs. Aucune écriture, aucune modification des critères bruts de complétude, du pays ou du regroupement.
2. `unit.php` distingue casse seule, espaces seuls, espace Unicode, vraie rue/code postal différents ; teste aussi accents/ponctuation conservés et complétude brute inchangée. **RED réel avant correctif : 27 contrôles, six FAIL** ; GREEN réel après : 27 PASS. `standard.php` prépare trois contrôles équivalents sur les valeurs relues des getters natifs ; chaque fixture doit effectivement différer avant comparaison. Leurs noms sont obligatoires dans `inside.py`/`verify.py`, classique et HPOS. Ces contrôles natifs sont écrits/lintables, **pas exécutés ici**.
3. La fixture native i3 garde le compte au code postal fictif `1000` et l’abonnement à `1001`. Oracle agrégé corrigé : une vraie divergence globale et BE, zéro « autres pays » ; les variations i1/i2 ne comptent plus. Cela reste une attente native à confirmer, pas une nouvelle photographie exécutée.
4. Le paquet natif antérieur `preuves/final/` est conservé **octet pour octet**. Aucun Docker, WSL, `matrix.py`, `run.py`, `seal.py` opérationnel, préparation globale ou rejeu global lancé pour ces corrections. Le test de refus de `seal.py --source=.../missing` est un test Python sans infrastructure. Le parent doit exécuter la nouvelle matrice et remplacer le paquet seulement après vert réel ; commandes de conservation historique et reseal fournies.
5. L’ancien SHA figé est retiré de `RAPPORT.md` ; renvoi aux vrais `utf8/dependencies.json` et `cp1252/dependencies.json` du paquet. À la lecture de ce réveil, gardien présent et scellé concordent : `c913c79206b6e7b54b8ecb42284952bf5a82d2d9075639f98eddf5479efade97`. Aucun gardien ni fichier commun modifié.
6. Windows réellement mesuré : `C:/Python314/python.exe`, **3.14.6**, pas 3.14.7. Les 14 tests initiaux passent sous UTF-8 et cp1252 avec `TMPDIR/TMP/TEMP` dirigés vers un scratch maîtrisé ; les 15 tests corrigés passent aussi dans les deux contextes. Les six WinError 5 ne sont pas reproduits dans ce cadre. L’environnement de départ exposait `TMPDIR=C:\Users\Ced\AppData\Local\Temp` ; il n’a pas été utilisé pour les fixtures. Le README impose un scratch hors dépôt et les droits création/lecture/renommage/suppression ; nettoyage strict inchangé. Pas de preuve d’une installation Windows neuve, pas de diagnostic antivirus inventé.
7. Mention explicite ajoutée : `wp/tests/rejouer.ps1` ne rejoue pour A-24 que l’unité PHP pure. Le natif (206 contrôles **historiques**), le confinement et Python ne sont pas couverts par cette commande ; leur qualification intégrée demande la matrice scellée. Les contrôles locaux courants sont distincts.

## Tests réellement exécutés

- Python Windows : **15 tests UTF-8 + 15 tests cp1252**, zéro erreur/échec ; stdout/stderr, locale et mode UTF-8 mesurés et enregistrés. Un test additionnel qualifie les reçus nommés ; son RED réel puis son GREEN sont conservés en scratch.
- PHP CLI portable **8.2.36**, uniquement extrait dans le scratch, sans installation système et sans Docker/WSL : **27 contrôles purs PASS**, puis les mêmes avec `-n` et les fonctions écriture/processus désactivées. Pas de WordPress ni base. Binaire absent du PATH initial ; paquet officiel Windows conservé uniquement en scratch, URL/SHA dans le reçu local.
- Contrôles finaux : **9 fichiers PHP lintés sans erreur**, syntaxe de tous les Python du lot validée ; compte exact, sorties et SHA dans `preuves/corrections-locales/local.json`, `lint.json` et `sources.json`. Le reçu local ne contient ni résultat natif synthétique ni faux JUnit. Le prérequis de création/lecture/renommage/suppression a également retourné `A24_SCRATCH_ACCESS_OK` avec les commandes du mode d’emploi.
- Réception de l’ancien paquet sur les sources corrigées : **échec attendu**, pas un vert de livraison. `historical-packet-verifier.log` consigne le refus du code/livraison périmés et des nouveaux contrôles nommés absents ; l’intégrité interne du paquet historique reste vérifiée. Ne pas remplacer ses SHA par ceux du nouveau code.

## Fichiers et périmètre

Modifiés : `wp/outils/bascule/a24/{Analysis.php,README.md}` ; `wp/tests/a24/{unit.php,seed.php,standard.php,inside.py,extended.py,test_verify.py,verify.py,matrix.py}` ; `production/A-24/{RAPPORT.md,COMMANDES.md,notes.md,FINALISATION.md}`. Créés : ce rapport et les reçus locaux sous `production/A-24/preuves/corrections-locales/`.

`production/A-24/PRET` a été copié avant mutation dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-corrections-reveil/PRET.original`, SHA `f1e3afb4c0d1c8d381bff38ab1ad89ca7a7770128ae29f9114247ae76de1b77f`, puis retiré ; il reste absent. RED, baseline, wrappers, scripts de contrôle et PHP portable sont uniquement dans ce scratch. Aucun Git, réel, archive d’Imagine, site, compte, voie 2, verrou ou fichier commun touché. La finalisation de 19 h 21 et les anciens checkpoints sont signalés comme historiques.

## Décisions prises à défaut

Normalisation précise : suppression des espacements, plutôt que simple réduction à un espace, pour neutraliser aussi les variations internes ; repli de casse simple Unicode fourni par le cœur PCRE. Les données brutes ne sont jamais nettoyées. I2 est traité comme prérequis environnemental observé, sans rendre le nettoyage permissif. La régénération native est différée au parent conformément à la consigne explicite de sérialisation ; **aucune clôture/PRET revendiquée**.
