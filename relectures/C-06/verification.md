# Vérification C-06 — second et dernier tour

Date : 21/11/2026. Vérificateur : Claude Code (NUC). Objet : contrôler que les
corrections de `corrections/C-06.md` ont été appliquées par Hermès après la fusion,
rejouer les tests, repérer toute régression, et trancher le verdict.

Méthode : `git diff 6c7b826..HEAD` sur `wp/` et `production/C-06/` (le commit `6c7b826`
est celui qui a introduit `corrections/C-06.md`). Concordance des sources vérifiée par
empreinte SHA-256 entre l'arbre de travail actuel et les preuves scellées
(`production/C-06/replays/corrections-21nov-1505/final.json` et `artifact-verification.json`).
Ce n'est **pas** une relecture complète : seuls les écarts depuis la version relue sont examinés.

---

## 1. Application des instructions de `corrections/C-06.md`

### Instruction 1 (Important) — Brancher la suite Acces sur `composer test` → **Appliquée**

- `wp/plugins/imagine-pilotage/phpunit.xml:7` : ajout de
  `<testsuite name="Acces"><directory>tests/Acces</directory></testsuite>`, à côté de
  `Numeros`, `Robots`, `Entreprise`. Exactement la forme suggérée dans la fusion.
- Mécanisme complété comme demandé (« vérifier que la commande standard exécute bien les 50
  tests ») :
  - `wp/tests/acces-runner/run.py:55-57` : suppression du détournement qui injectait
    `--configuration tests/Acces/phpunit.xml` ; la commande scellée redevient
    `composer test -- --log-junit /tmp/result.xml` (`run.py:102`).
  - `wp/tests/acces-runner/check-standard-suite.py` (nouveau) : garde de non-régression qui
    refuse une commande standard n'exécutant pas les quatre suites et vérifie `Acces >= 50`.
  - `wp/tests/acces-runner/verify.py:30-32` : assertions ajoutées exigeant la commande standard
    et `Configuration: /work/phpunit.xml` dans le journal.
- Preuve scellée : `final.xml` racine `name="/work/phpunit.xml"` → 234 tests, dont Acces 50 ;
  la suite Acces est donc bien jouée par la commande standard. Preuves republiées après rejeu
  (`replays/corrections-21nov-1505/`) comme demandé.

### Instruction 2 (Mineur) — Documenter C-06 dans le README → **Appliquée**

- `wp/plugins/imagine-pilotage/README.md` : nouvelle section « ## C-06 — décision d'accès pure »
  (titre du fichier mis à jour en « C-01 à C-06 »). Contient le contrat d'arguments du moteur
  (clés exactes des tableaux contenu/visiteur/robot, formes des droits), les réglages
  obligatoires de la découverte (`DureeDecouverte`, `NombreArticlesDecouverte`, sans valeur par
  défaut) et la procédure de tests en conteneur cohérente avec l'instruction 1 (`composer test`
  standard, `check-standard-suite.py`). L'information ne vit plus uniquement dans
  `production/C-06/notes.md`.

### Instruction 3 (Mineur) — Partager ou documenter la liste blanche des robots → **Appliquée** (option « documenter »)

- `wp/plugins/imagine-pilotage/src/Acces/Moteur.php:32-33` : commentaire au-dessus du bloc de
  validation (la liste `['google', 'bing']` est consommée ligne 37) indiquant que la liste est
  synchronisée **manuellement** avec `config/robots.php` et qu'un nouveau robot approuvé impose
  de toucher les deux fichiers, sinon accès fermé en extrait.
- README : paragraphe « Robot » répétant explicitement la double modification.
- Couplage vérifié réel : `config/robots.php:22-23` définit bien les identités `google` et
  `bing`. La fusion laissait le choix entre « constante partagée » et « documenter aux deux
  endroits » ; Hermès a retenu la documentation. Conforme.

---

## 2. Résultat des tests

**Je n'ai pas pu rejouer PHPUnit dans cet environnement** : aucun runtime de conteneur
autorisé (exécution `docker`/`php` refusée par le bac à sable), même situation que
« Docker refusé côté Claude » au premier tour. La vérification repose donc sur la concordance
d'empreintes, pas sur un rejeu indépendant frais.

Concordance SHA-256 — arbre de travail actuel vs preuves scellées — **identique sur les 7
fichiers modifiés par la correction** :

| Fichier | SHA-256 | Source scellée |
|---|---|---|
| `src/Acces/Moteur.php` | `b7bd0ad1…0321c0` | final.json + artifact ✓ |
| `phpunit.xml` | `236d592c…6c57f` (racine) | final.json ✓ |
| `README.md` | `c4cfe93a…a14248` | final.json ✓ |
| `config/robots.php` | `c42a9988…fdc78b` | final.json ✓ (inchangé) |
| `wp/tests/acces-runner/run.py` | `24815aaf…04a0c` | final.json `wrapper_sha256` + artifact ✓ |
| `wp/tests/acces-runner/verify.py` | `d9017501…d832f` | artifact ✓ |
| `wp/tests/acces-runner/check-standard-suite.py` | `5af8608e…1d1bc6` | artifact ✓ |

Les preuves scellées correspondent donc exactement au code présent dans l'arbre.

Résultat scellé (`final.json`, `final.xml`, `artifact-verification.json`) :

- **234 tests / 29 516 assertions**, dont **Acces : 50 tests / 9 536 assertions**.
- Répartition : Numeros 42, Robots 101, Entreprise 41, Acces 50 (42+101+41+50 = 234, cohérent).
- 0 échec, 0 erreur, 0 ignoré ; `exit_code = 0`.
- PSR-12 `0`, syntaxe `0`, `composer validate --strict` `0`.
- PHP 8.2.36, conteneur jetable, réseau détaché, aucun montage/port/base, absence du conteneur
  vérifiée après coup (`container_absence_verified: true`).
- La garde de couverture a été exercée rouge-avant/vert-après
  (`replays/corrections-21nov-1505-red/`), ce qui prouve que le branchement de la suite change
  réellement le résultat de la commande standard.

Limite assumée : résultat vérifié par concordance d'empreintes, non par un rejeu frais de ma
part. Un rejeu dans un environnement autorisé reste souhaitable pour la clôture.

---

## 3. Régressions ou modifications non demandées

- Diff total depuis la version relue limité à : `README.md`, `phpunit.xml`, `Moteur.php`
  (+2 lignes de commentaire **uniquement**, aucune modification de logique), plus les trois
  scripts du lanceur (`run.py`, `verify.py`, `check-standard-suite.py`) et les artefacts de
  `production/C-06/`. **Aucune autre zone de `wp/` touchée.**
- Les modifications des scripts du lanceur ne sont pas du hors-périmètre : elles sont le
  mécanisme exact exigé par l'instruction 1 (faire jouer Acces par la commande standard, puis
  garder cette propriété). Elles ne modifient aucune règle métier.
- Le moteur d'accès est **inchangé** fonctionnellement (seul un commentaire ajouté) : aucun
  risque de régression métier introduit par la remise corrective.
- Les suites `Numeros`, `Robots`, `Entreprise` restent au vert (comptes inchangés) : pas de
  régression croisée du branchement de la nouvelle suite.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les trois instructions de `corrections/C-06.md` (1 Important, 2 Mineures) sont **toutes
appliquées** et correctes ; les tests scellés sont au vert et concordent au bit près avec le
code actuel ; aucune régression ni modification non demandée. **Aucun problème de fond
restant** ne justifie un retour à Hermès.

Rappels pour la validation de Ced (sans quoi la clôture n'est pas acquise — un verdict n'est
jamais un GO) :

- Les questions d'arbitrage du §5 de la fusion restent **ouvertes** et relèvent de Ced, pas
  d'Hermès : sortie future fermée pour tous (`Moteur.php:46`), robot vérifié `complet` sur PDF
  (`Moteur.php:66-67`), PDF antérieur à l'abonnement (`Moteur.php:102-103`). Ces comportements
  n'ont pas été modifiés par la remise corrective ; ils attendent une décision métier.
- Le résultat des tests est vérifié par concordance d'empreintes, **pas par un rejeu
  indépendant** de ma part (environnement non autorisé). Un dernier rejeu de la suite complète
  en environnement autorisé confirmerait la preuve.
