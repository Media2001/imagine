# Banc PHP isolé C-03

Depuis le checkout `C:/Users/Ced/imagine`, rien à installer sur Windows/WSL :

```sh
python wp/tests/robots-runner/run.py prepare
python wp/tests/robots-runner/run.py run --name final
python wp/tests/robots-runner/extra_checks.py
python wp/tests/robots-runner/regression_c04.py
python wp/tests/robots-runner/run.py close
python wp/tests/robots-runner/check_artifacts.py
```

`run` exécute réellement `composer test`, `composer lint`, la syntaxe PHP de
`src/tests` et `composer validate --strict --no-check-publish`, depuis la copie
dans `/work`. `extra_checks.py` couvre aussi le fichier de configuration.
`regression_c04.py` copie C-04 dans `/regression-c04`, copie seulement les
outils de développement présents dans le runner et régénère son autoload hors
réseau ; il ne modifie pas le plugin ni les preuves C-04 sur l’hôte.

Le wrapper importe le banc existant `wp/tests/numeros-runner/run.py` **sans le
modifier**, sans bytecode Python, avec label `org.imagine.c03-runner`, état et
preuves dans `production/C-03/tests/`. La préparation ne réécrit pas le lock
C-01 : elle compare les octets du lock copié. L’image synthétique préexistante
est réutilisée avec `sleep` comme entrée, sans web, WordPress ou base. Composer
et les dépendances publiques sont obtenus uniquement dans le conteneur jetable.
Le réseau bridge est détaché avant toute suite ; pas de montage, volume, port,
socket Docker, privilège ou service lancé. L’état de ces limites est contrôlé
avant utilisation. `close` supprime seulement le runner portant le label C-03
et relit son absence.

Un filtre simple de classe/méthode est possible :

```sh
python wp/tests/robots-runner/run.py run --name verification-dns --filter VerificateurTest
```

Ne pas passer de regex avec `|` ni de métacaractère : le transport WSL peut les
interpréter avant PHP. Le wrapper les refuse. Il retire aussi l’ancien JUnit du
runner **avant** chaque exécution pour ne pas recycler un résultat périmé en cas
d’échec de commande. Chaque nom de preuve doit être nouveau lors d’une relecture.

Le hash `runner_sha256` du reçu hérité désigne le lanceur C-01 importé ; les
empreintes du wrapper C-03 et des scripts annexes figurent dans la vérification
d’artefacts. `protected-before.json` protège l’inventaire C-01/C-04 et le socle
pilotage. Seuls l’ajout de suite dans `phpunit.xml`, l’appendice C-03 du README
pilotage et les nouveaux dossiers/fichier propres à C-03 sont autorisés.

`check_artifacts.py` est purement local, sans Docker ni réseau : il vérifie les
sources contre les reçus de tests, les décomptes JUnit, la préservation des lots
voisins, le nettoyage et les scripts, puis écrit `artifact-verification.json`
et `fichiers-livres.json`. Une absence de preuve fait échouer ce contrôle ;
aucun résultat de test n’est inventé. Les notes et le bilan restent dans
`production/C-03/` ; ce banc n’installe et n’active rien sur un site.
