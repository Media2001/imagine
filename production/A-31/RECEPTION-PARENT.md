# A-31 — Réception des corrections du 27 novembre 2026

**Candidat vérifié, livraison bloquée : aucun PRET, aucun manifeste.** Les tests propres à A-31 passent ; les gates globales refusent la dérive d'A-32. Le `pass=true` du lanceur ne suffit pas : ses deux reçus contiennent `packets.failures=[{"lot":"A-32","control":"A32_PACKAGE_DRIFT"}]`. Aucune correction hors A-31 ni réécriture du lanceur n'a été faite.

## Les six instructions

1. Quatre compteurs de liens exacts distincts, sans pool : 0/1/2/3/4/5, seuls et mêlés aux trois autres métriques, classique/HPOS × UTF-8/cp1252. Le témoin RED remet volontairement les scalaires dans des pools dans la seule copie jetable ; le cas rare à 1 le détecte.
2. K5 réservé à `years` et `statuses`. Décision à défaut, selon la consigne courante « années/années-états seulement » : natures et remboursements par année exacts, `autres=0`, total des remboursements égal à la somme exacte des années. La réception précédente, qui fondait aussi ces groupes, est retirée hors dépôt.
3. Analyse PHP, schéma fermé Python, JSON, Markdown et oracles alignés. Les mutations de fin de processus altèrent encore des rapports valides JSON+Markdown : le contrôle SHA-256 les refuse. Le RED Python et le RED PHP sans mutation ont réellement échoué avant correction ; ils restent en scratch.
4. Abonnement à la corbeille présent dans le recensement d'existence, ni vivant ni renouvellement orphelin. Preuve native dans chaque magasin et console.
5. Dates natives locales `2018-01-01T00:30:00+01:00` et `2018-12-31T23:30:00-01:00` : années UTC 2017/2019, ancienneté 2017 lorsque le groupe atteint cinq. Les deux directions sont vérifiées dans les quatre cellules.
6. Import A-28, gardien A-22, outils clos et lanceur gelé inchangés ; aucun Git, site réel, archive, compte, déploiement, voie 2, cron ou verrou modifié. Pas d'aléa partagé observé pendant les gates finales.

Après le vrai neutraliser/anonymiser inchangé sur bases fictives, **seul `natures` est inconnu après neutralisation**, jamais zéro. Années/états, quatre liens, remboursements et oldest restent lisibles ; seul le K5 des années de commandes peut masquer oldest. Vivant = exactement `active`, comme A-19. L'outil ne répare, rattache ni supprime rien.

## Résultats réellement exécutés

- Python Windows `C:/Python314/python.exe` **3.14.6** : 42 tests réussis par console ; stdout/stderr UTF-8 avec mode UTF8=1 puis cp1252 avec mode UTF8=0. `TMPDIR` retiré des enfants et mesuré `null` ; TEMP/TMP dirigés vers le scratch Hermes.
- Par console : 238 assertions PHP pures, 19 de frontière native, 552 contrôles du banc, 15 du runner, 19 du standard installé par magasin. Matrice de 48 scénarios de liens par magasin/console, soit 192 exécutions natives distinctes ; empreintes DB/fichiers identiques avant/après chacune. Canaris sur tous les canaux ; PHP seulement dans des conteneurs jetables déconnectés.
- Vérificateur de candidat : **324 contrôles PASS**, exit 0 ; 35 sources et 65 dépendances gelées. Style strict : 0 erreur, 0 avertissement. Les deux lignes A-31 du mode d'emploi partagé sont exactes, une fois chacune ; son fichier n'a pas été réécrit.
- Préparation réelle de l'image : exit 0 et sonde Python hors ligne PASS. Deux rejeux globaux : chacun 1 204 tests, 36 667 assertions, 0 échec/erreur/ignoré PHP ; 22 outils, 791 contrôles, dont A-31/238, tous verts. Mais **un échec de paquet A-32** : la gate agrégée reste exit 1. Les lecteurs A-20/A-21/A-22/A-28 donnent exit 0.
- `reseal.py` rend réellement exit 1 / `A31_PARENT_GATES_MISSING` ; aucun sceau ni PRET n'est créé. La lecture de livraison sans argument reste un refus `A31_PARTIAL_EVIDENCE`.

## Commandes et preuves

Depuis `C:/Users/Ced/imagine`, commandes finales réellement passées, sérialisées :

```sh
C:/Python314/python.exe -B wp/tests/a31/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-correction-20261127-1738/matrix-final-03
C:/Python314/python.exe -B wp/tests/a31/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-correction-20261127-1738/matrix-final-03
C:/Python314/python.exe -B wp/tests/a31/gates.py --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-correction-20261127-1738/gates-final
C:/Python314/python.exe -B wp/tests/a31/reseal.py --parent-serialized --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-correction-20261127-1738/matrix-final-03 --gates=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-correction-20261127-1738/gates-final
```

`gates.py` a réellement lancé `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1`, puis deux fois `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` avec les deux encodages explicites, puis les quatre lecteurs. Commandes exactes, sorties complètes et SHA-256 : `preuves/final/gates/commands.json`. Sondes Windows, matrices, témoins RED, DB/fichiers et style : `preuves/final/` — **unique paquet candidat, non scellé malgré son nom de répertoire**. La déclaration `rejeu.json` est conservée ; ses 28 journaux sont présents. Relecture native sans mutation :

```sh
C:/Python314/python.exe -B wp/tests/a31/verify.py --evidence=production/A-31/preuves/final
C:/Python314/python.exe -B production/A-31/verify.py
```

La première doit passer les 324 contrôles ; la seconde doit refuser la livraison non scellée. Les reçus authentiques après publication sont dans `verification-candidat.json` et `reception-finale.json` ; ils ne remplacent pas les gates rouges.

Essais et ancien paquet : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-correction-20261127-1738/`. Un premier foreground a été interrompu par le watchdog hôte ; son conteneur exact a été retiré puis son absence vérifiée. Un deuxième essai a été arrêté pour corriger deux avertissements PSR-12 ; même nettoyage exact. Aucun reçu de ces essais n'est présenté comme final ; le dernier rejeu complet est suivi comme processus de fond jusqu'à sa sortie réelle.

## Reprise réservée au parent

Résoudre A-32 dans son périmètre autorisé, rejouer les gates sous un nom scratch neuf, et conserver les sources A-31 telles que gelées si la matrice est réutilisée. Retirer ce candidat de `preuves/final/` vers le scratch avant `reseal.py`, qui refuse un répertoire existant. Ne jamais remplacer les empreintes à la main. Puis lecteur sans argument vert, rejeu canonique post-sceau avec A-31 dans `packets.lots` et aucun échec, et seulement alors PRET. Aucune clôture indépendante ni aucun GO réel n'est prétendu.
