# Vérification A-19 — 2e et dernier tour (après corrections d'Hermès)

Date : 2026-11-26. Vérificateur : Claude, depuis la racine du dépôt.
Base de comparaison : commit `23f6055d` (dépôt de `corrections/A-19.md`) → `HEAD`.
Je ne refais pas une relecture complète ; je vérifie l'application des corrections, je relance
les tests, je signale régressions et modifications non demandées. Ce verdict n'est pas un GO réel.

## 1. Application des instructions de `corrections/A-19.md` §4

### Instruction 1 — Lever A19-CX-01 (`--as-of` facultatif dans le lanceur). **Appliquée.**
- `wp/outils/bascule/a19/confine.py:16` : la garde `.issubset` ne porte plus que sur les trois
  chemins `{'--wp-path','--output','--audit'}` ; `--as-of` n'est plus obligatoire.
- Refus des arguments répétés conservé (`confine.py:13`, `key in o → A19_USAGE`).
- Défaut UTC fixé côté PHP une seule fois (`Command.php:58`, inchangé).
- La commande livrée est désormais cohérente : `production/A-19/readme-ajout.txt:1` et sa reprise
  `wp/tests/a02-audit/README.md:75` (sans date) s'exécutent sans renvoyer `A19_USAGE`. Aligné sur
  `README.md:24` (« `--as-of` facultatif »).

### Instruction 2 — Couvrir le parcours sans date. **Appliquée.**
- `wp/tests/a19/test_launcher.py:16` : nouveau cas `test_three_paths_without_date_reach_path_validation`
  — trois chemins sans `--as-of` → ne renvoie **pas** `A19_USAGE` (atteint la validation de chemin,
  `A19_CONFINEMENT_FAILED`). Cas `test_repeated_date_refused_with_all_paths` ajouté.
- Banc natif rejoué avec et sans date : `wp/tests/a19/inside.py:67-80` ajoute
  `explicit_clock_retained`, `three_paths_without_date_native`, `default_clock_is_current_utc`,
  `default_clock_single_frozen_reference`, `repeated_clock_refused`.
- Preuves correspondantes présentes : `preuves/final/{classic,hpos}-default-clock/` et
  `-default-frozen/` (classic, hpos, utf8). `verify.py:33` contrôle que rapport par défaut et
  rapport à date explicite gelée sont identiques — PASS.

### Instruction 3 — Câbler les 9 assertions de `unit.php` dans T01. **Appliquée.**
- `wp/plugins/imagine-pilotage/tests/Administration/A19SubscriptionCoherenceTest.php` (27 lignes) :
  importe les neuf mêmes assertions de `wp/tests/a19/unit.php` via DataProvider, sans recopier les
  règles. Découvert par la suite `Administration` existante, sans modifier la configuration T01.
- `wp/tests/a19/unit.php:57-60` : en inclusion, retourne `$checks` sans écrire ni sortir du
  processus ; en exécution autonome, conserve son reçu JSON.
- Sonde de frontière pure (`php -n`, écritures/processus désactivés) :
  `wp/tests/a19/t01-probe.php` + runner `wp/tests/a19/t01.py`. `verify.py` atteste
  `t01_current_sources_and_genuine_nine_cases` et `t01_junit_nine_assertions_zero_skipped` — PASS.
- Limite documentée : `README.md` (« Couverture T01 et gate commune ») indique que les matrices
  natives classic/HPOS restent hors T01, comme pour A02/A11/A12.
- **Preuve directe au rejeu** : la suite globale `rejouer.ps1` fait apparaître le testsuite
  `A19SubscriptionCoherenceTest` avec 9 cas / 9 assertions / 0 échec (voir §2).

### Instruction 4 — Ne pas toucher au seau `automatic_payment_reference_unknown`. **Appliquée.**
- `git diff 23f6055d HEAD` sur `Analysis.php`, `Command.php`, `Inventory.php`,
  `inventorier-coherence` : **aucun changement**. Le seau et la logique métier sont intacts.

## 2. Résultat des tests (relancés)

- **Commande de rejeu autorisée** `./wp/tests/rejouer.ps1` (conteneur jetable, hors réseau, dépôt
  monté en lecture seule) :
  `REJEU : 1123 tests, 34569 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS` ;
  `OUTILS : 13 outils, 242 contrôles, 0 échecs`.
  Le testsuite `A19SubscriptionCoherenceTest` y figure : **9 tests, 9 assertions, 0 échec**.
  La réserve du 1er tour est levée : la commande autorisée couvre désormais la logique métier pure
  d'A-19 (au tour précédent : 1111 tests, 0 mention d'A-19).
- **`python -B wp/tests/a19/test_launcher.py`** : `Ran 5 tests … OK` (était 3).
- **`python -B wp/tests/a19/verify.py production/A-19/preuves/final`** : **40 PASS, 0 FAIL**,
  `exit_code 0`, `status CANDIDAT_GATE_PARENT`.
- Banc natif complet (`run.py`, Docker + extensions commerciales) : hors de portée du vérificateur,
  comme au 1er tour ; vérifié par le paquet de preuves et le rejeu ci-dessus.

## 3. Régressions ou modifications non demandées

- **Aucune régression métier** : code métier A-19 inchangé (instruction 4) ; non-régression globale
  prouvée par le rejeu T01 (0 échec).
- **`verify.py`** renvoie désormais `CANDIDAT_GATE_PARENT` (au lieu d'un résultat simple) : choix
  délibéré et cohérent — le paquet n'atteste que le candidat ; préparation commune, rejeu global et
  `PRET` relèvent du parent. `production/A-19/PRET` présent et daté, `FINALISATION.md` décrit ces
  gates exécutées (préparation code 0, rejeu PASS). Pas une modification non demandée.
- **Infra T01 modifiée** (`wp/tests/t01/tools.php`, `tools-contract.php`, `executer.php`, etc.) :
  `git diff` → **0 occurrence d'`a19`**. Ces changements relèvent du lot **T-02 « rejeu des outils »**
  (confirmé par `FINALISATION.md` : « rattaché à T-02 »), pas d'A-19. Hors de mon périmètre, sans
  effet sur A-19.
- Modifications périphériques attendues : `verify.py`, `run.py`, `style.py` étendus pour inclure le
  nouveau fichier de test dans les empreintes de sources (`OWN`) — cohérent avec l'ajout.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les quatre instructions de la fusion sont appliquées et vérifiées. Les tests relancés sont au vert,
y compris la couverture A-19 désormais câblée dans la commande de rejeu autorisée (réserve du 1er
tour levée). Aucune régression, aucune modification non demandée touchant A-19. Aucune question
visuelle ni touchant au réel n'est ouverte pour Ced (la seule question métier restante — garder
« schéma de passerelle inconnu » distinct de « moyen absent » — est pour Imagine, défaut prudent
« garder » déjà appliqué). Aucun problème de fond restant.

**Rappel : un verdict de vérification n'est pas un GO** au sens du §3 de la doctrine ; il ne vaut
que pour la clôture d'un lot de code.
