# A-24 — commandes exactes après corrections du 26 novembre 2026

Depuis `C:/Users/Ced/imagine`, bash Git Bash du poste Windows. Aucun Git. Interpréteur mesuré : `C:/Python314/python.exe`, Python **3.14.6**. Les cibles de matrice et d’historique doivent être neuves.

## Prérequis Windows — avant tous les rejeux

```sh
mkdir -p C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-windows-fixtures
export TMPDIR=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-windows-fixtures
export TMP="$TMPDIR" TEMP="$TMPDIR" PYTHONDONTWRITEBYTECODE=1
'C:/Python314/python.exe' -B -c "import os,tempfile;from pathlib import Path;t=tempfile.TemporaryDirectory(prefix='a24-access-',dir=os.environ['TMPDIR']);p=Path(t.name)/'a';p.mkdir();f=p/'probe';f.write_bytes(b'fixture');assert f.read_bytes()==b'fixture';f.rename(p/'renamed');(p/'renamed').unlink();p.rmdir();t.cleanup();print('A24_SCRATCH_ACCESS_OK')"
```

Le compte doit pouvoir créer/lire/renommer/supprimer dans ce scratch local hors dépôt, sans règle antivirus/EDR interdisant ces opérations. Un refus bloque le rejeu : ne pas masquer le nettoyage ni désactiver une protection. Les 14 tests initiaux puis les 15 tests corrigés ont passé sous UTF-8 et cp1252 avec scratch explicite sur ce poste ; ce n’est pas une qualification d’une installation Windows neuve.

## Matrice complète — parent uniquement, à sérialiser

**Non exécutée par l’enfant pour ces corrections.** Après gel des sources/dépendances, sans autre banc concurrent :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-corrections-matrice-20261126-01
```

Cette commande lance séquentiellement les suites PHP pure et native classique/HPOS en conteneurs jetables, puis tous les `test_*.py` Windows sous UTF-8 et cp1252. Chaque sous-processus Python fixe son encodage. Les deux contextes photographient l’interpréteur, l’encodage effectif et les mêmes sources/dépendances. L’image locale du banc est épinglée dans `wp/tests/a02-audit/run.py` ; aucune préparation d’image globale ni téléchargement.

La fixture i3 comporte désormais un vrai changement de code postal : oracle attendu, une différence globale, une BE, zéro dans les autres pays. Les contrôles natifs nommés casse/espace/vrai contenu et `*-standard.json` doivent passer sur les deux stockages. Les 206 contrôles de l’ancien paquet ne prouvent pas ce nouveau code ; aucun total natif anticipé n’est déclaré réussi.

## Rejouer séparément

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B -m unittest discover -s wp/tests/a24 -p 'test_*.py' -v
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 'C:/Python314/python.exe' -B -m unittest discover -s wp/tests/a24 -p 'test_*.py' -v
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-rejeu-independant-neuf
```

`run.py`, y compris `--unit-only`, utilise Docker/WSL et reste réservé au parent. Les deux commandes unittest seules n’en utilisent pas. Pas de site en argument au banc : exclusivement sa fixture fictive.

### PHP pur local sans Docker/WSL

PHP portable 8.2.36 a été préparé uniquement en scratch, sans installation système. Commande réelle, sans extensions optionnelles ni fonctions d’écriture/processus :

```sh
A24_PURE_PROBE=1 'C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-corrections-reveil/php-portable/php.exe' -n -d disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open -r "require 'C:/Users/Ced/imagine/wp/outils/bascule/a24/Analysis.php'; require 'C:/Users/Ced/imagine/wp/tests/a24/unit.php';"
```

Résultat courant : `A24_PURE_OK 27`. Cela ne prouve ni les getters natifs ni Landlock. Pour le banc isolé du parent seulement, `run.py --unit-only` demeure disponible.

## Scellement et réception

**Parent uniquement.** Une fois la matrice réellement verte et les quatre documents de livraison finalisés, conserver le paquet existant intact hors dépôt avant remplacement (la cible historique doit être absente) :

```sh
'C:/Python314/python.exe' -B -c "from pathlib import Path;s=Path('C:/Users/Ced/imagine/production/A-24/preuves/final');d=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-final-historique-avant-corrections-20261126-01');assert s.is_dir() and not s.is_symlink() and not d.exists();s.rename(d);print('A24_HISTORICAL_PACKET_MOVED')"
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/seal.py --source=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a24-corrections-matrice-20261126-01
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/verify.py --require-shared
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 'C:/Python314/python.exe' -B wp/tests/a24/verify.py --require-shared
```

`seal.py` n’écrase jamais un paquet : il vérifie d’abord en scratch, prouve la réception avec/sans futur PRET sur un miroir jetable, refuse trois mutations et publie `production/A-24/preuves/final` seulement au vert. Le paquet est unique ; tous les essais intermédiaires restent dans le scratch. Un nouveau rejeu se conserve d’abord hors dépôt et se vérifie avec `verify.py --packet=CHEMIN_DU_PAQUET_SCELLE` ; le remplacement d’un paquet publié appartient au parent, jamais à ce worker.

En cas de refus, garder la matrice échouée et le paquet historique. Ne jamais resealer d’anciennes preuves avec de nouveaux SHA. Une dépendance commune modifiée pendant le rejeu impose une matrice neuve sous une nouvelle cible.

Après intégration des deux lignes de `readme-ajout.txt` par le parent, réception finale du contrat partagé :

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 'C:/Python314/python.exe' -B wp/tests/a24/verify.py --require-shared
```

Sans cette option, la réception dit explicitement `delta_pending_parent`, jamais « README partagé intégré ». Les autres ajouts au fichier partagé sont ignorés ; seules les deux lignes exactes, uniques et terminées sont contrôlées. PRET reste au parent, ainsi que préparer-image/rejeu globaux.

**Portée :** `wp/tests/rejouer.ps1` ne rejoue pour A-24 que `unit.php`, pas l’adaptateur natif, le confinement ni Python. Aucun PRET n’est déposé pour ces corrections ; les preuves natives courantes restent à produire par le parent.

## Parcours de l’inventaire

Commande opérateur à rejouer par la matrice du parent avec ses seuls trois arguments sur chaque stockage et chaque contexte (historique déjà exercé, correction courante non exécutée nativement par l’enfant) :

```sh
python3 wp/outils/bascule/a24/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/expedition-date
```

Sur une copie uniquement anonymisée/vérifiée sous Linux isolé ; pas sur le poste Windows, pas sur la production, pas avant un GO pour tout futur accès au réel. Voir les prérequis et l’interprétation des comptes dans le README propre à A-24.
