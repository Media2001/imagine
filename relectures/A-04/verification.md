# Vérification A-04 — second tour (vérificateur)

Lot : A-04 `mettre-a-jour`. Base relue : commit de fusion `4addb22` (`corrections/A-04.md`, 2026-11-25 15:48).
Méthode : `git diff 4addb22 HEAD` sur `wp/` et `production/A-04/`, relecture ciblée des zones corrigées, rejeu partiel des tests. Pas de nouvelle relecture complète.

Fichiers A-04 effectivement modifiés depuis la version relue :
`wp/outils/bascule/a04/update.py`, `wp/outils/bascule/mettre-a-jour.md`,
`wp/tests/a04/inside.py`, `test_corrections.py` (nouveau), `test_packages.py`, `test_safety.py`.
`bootstrap.php`, `maintenance.php`, `runtime.php` : **inchangés** (diff vide) — conforme à la consigne de conserver le balayage `(?!)`.

## 1. État des instructions de `corrections/A-04.md`

### Instruction 1 — I3, canonicalisation de l'emplacement de sauvegarde (important) — **Appliquée**
`update.py:117-119`. Les deux chemins sont désormais canonicalisés : refus de tout lien symbolique dans les parents (`not any(parent.is_symlink() for parent in file.parents)`, `A04_SYMLINK`), résolution stricte (`file.resolve(strict=True)`), comparaison `not resolved.is_relative_to(site.resolve())` (`A04_BACKUP_LOCATION`), puis empreinte sur le chemin résolu. Aligné sur `safe_path`. Tests de refus ajoutés : `..` résolu dans le site, parent symbolique vers le site et vers l'extérieur, lien final (`test_corrections.py:35-56`). Vérifié en local (chemins Windows) : sauvegarde externe acceptée ; `..` ramené dans le site refusé `A04_BACKUP_LOCATION`.

### Instruction 2 — I1, identité du fichier principal (important) — **Appliquée**
Voie du défaut retenue (déclaration explicite au plan). `main_file` devient un champ obligatoire du plan avec validation de chemin (`validate_main_file`, `update.py:154-160` ; appelé en `validate_plan:72`) : refus de l'absolu, de `.`/`..`, de l'antislash, de tout suffixe ≠ `.php` ; `core` impose `main_file: null`. La même identité sert aux métadonnées du ZIP (`package_metadata`, `:162`) **et** à la lecture de la version installée (`version`, `:205`), branchées en `:306,308,330,354`. Fixture où dossier et fichier principal diffèrent ajoutée : dossier `a04-rest`, fichier `fiction-entry.php` (`inside.py:47-51`) ; cas unitaire `fixture-box/entry.php` (`test_corrections.py:120-139`). Vérifié en local : déclaration explicite acceptée ; dix valeurs invalides refusées `A04_MAIN_FILE` ; `core` avec `main_file` refusé ; clé absente refusée `A04_PLAN`.

### Instruction 3 — I2, reprise après fenêtre de dix minutes (mineur, défaut : corriger) — **Appliquée**
Démarrage et reprise sont distingués (`update.py:280-290`). À la reprise (`resuming`, état valide déjà validé par `validate_state`), le script vérifie les octets du MU persistant (`require(persistent.is_file() and digest(persistent) == digest(template), 'A04_MAINTENANCE_BYTES')`) **puis** rafraîchit `.maintenance` sous les deux verrous déjà tenus (`refresh_maintenance(site)`). Au premier démarrage, `maintenance(site)` conserve l'exigence de fraîcheur < 600 s. MU absent ou modifié : refus `A04_MAINTENANCE_BYTES`, aucune réinstallation implicite. Tests ajoutés (`inside.py:127-161`) : reprise acceptée après 1200 s avec MU exact (`expired_resume_accepted_with_exact_mu`, exit 75) ; refus si MU disparu ou modifié, avec checkpoint et `.maintenance` intacts et canary de bootstrap non déclenché ; refus si checkpoint invalide ; `.maintenance` rafraîchi sous verrou à horodatage < 600 s ; étape `core` déjà `verified` non rejouée.

### Instruction 4 — Mineur 1, trace d'audit par `bootstrap-only` — **Appliquée**
Au-delà des quatre premières étapes, le plan exige une clé `audit` nommant le composant (`update.py:66-80` : `audit['component'] == key`, `conclusion == 'no-deferred-database-migrations'`, `path` absolu, `sha256` exact). Le fichier d'audit est relu et vérifié avant bootstrap (`check_audit`, `:87-92` ; appelé en `:302`). Le comportement `(?!)` de `runtime.php` est conservé (fichier inchangé) et non élargi. Vérifié en local : `bootstrap-only` sans `audit` refusé `A04_AUDIT` ; audit nommé accepté ; variations de champ refusées.

### Instruction 5 — Mineur 3, alignement du mode d'emploi — **Appliquée**
`wp/outils/bascule/mettre-a-jour.md` : nouvelle section précisant qu'« aucun adaptateur additionnel n'est accepté au-delà des quatre premiers, même qualifié : `validate_plan` le refuse par conception ». Cohérent avec `update.py:74`. Vérifié en local : adaptateur qualifié en 5ᵉ étape refusé `A04_ADAPTER`.

### Instruction 6 — Mineur 2, `journal.txt` (statu quo possible) — **Appliquée (documentée)**
Statu quo retenu, désormais explicité dans `mettre-a-jour.md` : « `journal.json` est la source structurée […] ; `journal.txt` reste un en-tête suivi d'une ligne JSON par événement (statu quo accepté, pas une table humaine) ». Non bloquant.

### Décisions techniques (défauts proposés) — **Suivies**
Défaut I1 (déclaration explicite au plan), défaut I2 (rafraîchissement sous verrou conditionné aux octets du MU), défaut `bootstrap-only` (statu quo + trace d'audit obligatoire) : tous appliqués comme ci-dessus.

## 2. Résultat des tests

- **Rejeu Docker indépendant : non reproductible ici.** `docker` est absent du `PATH` de ce poste (`command not found`), exactement la limite déjà signalée en fusion. Je n'ai donc pas pu relancer `wp/tests/a04/run.py` moi-même.
- **Preuve Docker d'Hermès, postérieure aux corrections : verte.** `production/A-04/corrections-20261125/final-run.json` (`observed_at` 2026-11-25 16:31 UTC, après la fusion de 15:48) : `exit_code 0`, paquet `production/A-04/preuves/eb2aea037769`. Contrôles `lint`, `unit`, `integration`, `dependencies_unchanged`, `sources_unchanged`, `isolation_before/after`, `cleanup_exact_owned` tous `ok`. Conteneur `--network none`, `--cap-drop ALL`, sans montage ni port.
- **Rejeu natif Windows des unitaires : échecs attendus, non représentatifs.** `python -m unittest test_corrections` échoue (20 fail / 4 err), mais la cause est la sémantique des chemins POSIX sur Windows : `pathlib.Path('/fixture.zip').is_absolute()` vaut `False`, donc `validate_plan` s'arrête dès l'étape 0 sur `A04_PACKAGE` avant d'atteindre les cas testés ; les liens symboliques et `flock` ne sont pas non plus exerçables nativement. Ce sont les mêmes contraintes qui imposent le banc Docker Linux.
- **Vérification ciblée de la logique corrigée, en contournant l'artefact de chemin (chemins absolus Windows).** `validate_main_file`, la table d'audit, la restriction d'adaptateur et `check_backup` (acceptation externe, refus `..`-dans-le-site) se comportent toutes comme attendu (détails §1). Cela confirme que les échecs natifs sont un artefact de plateforme, pas une régression.

Bilan : la seule exécution d'intégration qui fait foi reste le banc Docker ; elle est au vert dans le paquet d'Hermès mais **n'a pas été reproduite par un relecteur** — report inchangé par rapport à la fusion.

## 3. Régressions et modifications non demandées

- **Aucune régression A-04 détectée.** Les corrections sont circonscrites aux six fichiers A-04 listés ; `bootstrap.php`/`maintenance.php`/`runtime.php` sont inchangés.
- **Réordonnancement de la maintenance : voulu, pas une régression.** L'appel `maintenance(site)` initial a été retiré de sa position d'origine et remplacé par la branche démarrage/reprise après `check_backup`, le hash de `wp-config` et le chargement de l'état (`update.py:280-290`). C'est précisément la correction I2 demandée ; le nouvel ordre est documenté dans `mettre-a-jour.md` (« après acquisition des verrous […], contrôles staging/sauvegarde/identité, […] rafraîchit `.maintenance` avant PHP/WP-CLI »). Le refus en l'absence de MU conforme est conservé (`:287,316`).
- **Hors périmètre A-04.** Le `git diff` sur `wp/` depuis la fusion touche aussi A-05, B-02, B-03, C-09, C-13, C-14 et le thème : ce sont des travaux parallèles d'autres lots, sans rapport avec les corrections A-04 et non évalués ici.
- **Limite de preuve n°1 toujours ouverte.** Pile de départ WordPress 7.0 complète, pas le 6.9.1 réel ; la montée réelle et les migrations historiques premium restent à prouver sur le staging Imagine. Inchangé depuis la fusion, correctement documenté (`risques.md`, `rapport.md`).

## 4. Verdict

**Prêt pour la validation de Ced.**

Les six instructions de la fusion sont appliquées et vérifiables dans le code et le mode d'emploi ; la logique corrigée (I1, I3, audit `bootstrap-only`, restriction d'adaptateur, `check_backup`) a été exercée en local et se comporte comme spécifié ; la preuve Docker d'Hermès postérieure aux corrections est au vert. Aucun problème de fond restant, aucune question métier ou visuelle ouverte pour ce lot.

Réserves à porter à la clôture, sans caractère bloquant pour le lot de code sur fixtures fictives :
1. Le rejeu Docker indépendant n'a été reproduit par **aucun** relecteur (poste sans `docker`) ; la seule exécution d'intégration verte est celle d'Hermès.
2. La preuve réelle (6.9.1 → 7.0 sur pile commerciale, migrations historiques premium) reste à faire sur le staging Imagine vérifié, avec un GO écrit de Ced. La question fermée de la fusion (défaut proposé : oui) reste à confirmer par Ced.

Rappel : ce verdict clôt un lot de code sur fixtures fictives. **Ce n'est pas un GO** : il n'autorise ni mise en ligne, ni accès au réel, ni levée de maintenance.
