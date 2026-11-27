# Vérification A-26 (2e et dernier tour)

Lot : A-26. Fusion vérifiée : `corrections/A-26.md`. Corrections appliquées par Hermès après la fusion.
Méthode : `git diff` depuis la version relue (`05631be2`, commit de la fusion, 27/11 00:43) jusqu'à `HEAD`, sur `production/A-26`, `wp/outils/bascule/a26`, `wp/tests/a26`, `wp/outils/staging` ; relance des vérificateurs en lecture seule. Pas de relecture complète refaite.

## 1. Instructions de `corrections/A-26.md`

### Instruction 1 — Lever B1 (gel des dépendances rejoué sur l'arbre courant) : **Appliquée**
- Le gel `production/A-26/preuves/final/dependencies.json` a été recalculé sur l'arbre vivant. Les sept empreintes de staging **correspondent exactement** au tree courant (vérifié par `sha256sum`) :
  - `wp/outils/staging/command.php` = `25b146ef…` (valeur dérivée signalée dans B1, désormais gelée).
  - `wp/outils/staging/lib.php` = `c6ebdbb9…` (fichier refactoré, voir §3).
  - `engine.php`, `guard.php`, `store.php`, `form-decision-refused.php` : nouveaux fichiers staging, gelés.
- `wp/outils/staging/form-policy.json` = `1d5e2426…` **intégré au gel** et rendu dépendance obligatoire (`wp/tests/a26/run.py:23`, `DEPS`). Deux tests le protègent (`test_form_policy_is_mandatory_frozen_dependency`, `test_missing_form_policy_cannot_silently_shrink_staging_freeze`).
- `production/A-26/verify.py:44` (`freeze['sources']==inventory(freeze['roots'])`) : **frozen_sources = PASS** — plus de `FROZEN_SOURCE_DRIFT`.
- `wp/tests/a26/verify.py:51-52` : plus d'`A26_SOURCE_DRIFT`.
- Sceau et marqueur `PRET` renouvelés (`production/A-26/PRET`, `2026-11-27T05:03:18`), postérieurs aux retouches de staging. Le gel n'est pas un simple remplacement d'empreintes : le refactor réel de staging est reflété fichier par fichier (voir §3).

### Instruction 2 — Lever I1 (parseur HTML à la place des expressions régulières) : **Appliquée**
- `Analysis::htmlUrls` réécrit avec `WP_HTML_Tag_Processor` : `wp/outils/bascule/a26/Analysis.php:147` (instanciation) et `:173` (`get_attribute`). Plus d'extraction par regex de balises/attributs ; seul subsiste un repli « URL nue en début de ligne » sur le texte hors balises. Contrôlé par `test_native_attribute_reader_no_html_regex_fallback`.
- Les deux contre-exemples sont en tests rouges : `wp/tests/a26/html-unit.php:30` (`html_quoted_gt_real_youtube` — iframe `title="a > b"` + src YouTube) et `:36` (`html_title_src_no_phantom_vimeo` — img `title='src="…vimeo…"'` + src local). Ancienne version conservée en référence : `wp/tests/a26/html-regex-before.txt`.
- Vérifiés dans les rapports **classique ET HPOS** : `wp/tests/a26/verify.py:102-143` boucle `storage in ('classic','hpos')` et exige les deux cas rouges + comptes attendus (youtube 4 / vimeo 1 en vert, 3 / 2 en rouge). PASS.

### Instruction 3 — Lever M1 (chemin explicite du README, lignes uniques) : **Appliquée**
- `production/A-26/readme-ajout.txt:1` désigne désormais `wp/outils/bascule/a26/README.md` (chemin résoluble depuis la racine).
- Mode d'emploi commun : `wp/tests/a02-audit/README.md:98-99` — les deux lignes sont identiques à `readme-ajout.txt` et présentes **une seule fois**. Contrôle `shared_document_valid` (`wp/tests/a26/verify.py:41-44`) = PASS ; `test_document_points_to_explicit_root_relative_readme` OK.

## 2. Résultat des tests (relancés en local, lecture seule)

- `wp/tests/a26/verify.py` → `NATIVE_PACKET_VERIFIED_PARENT_GATES_PENDING`, **30 tests Python par console**, sortie propre (exit 0).
- `production/A-26/verify.py` → `exit_code 0` : `package_and_inventory PASS`, **`frozen_sources PASS`**, `parent_gates 19`, `native_packet PASS`, `pret_present true`.
- `wp/tests/a26/test_corrections.py` (unittest) → **6 tests OK** (contrats des trois corrections : parseur sans regex, gel `form-policy`, README explicite, contre-exemples requis classique+HPOS, mutation de méthode exacte).
- Vérification manuelle des empreintes staging (`sha256sum`) → les 7 dépendances du gel correspondent au tree courant.

Les paquets natifs exécutés en conteneur (`run.py`, Docker) relèvent de la production d'Hermès ; ils sont figés dans le paquet scellé et revalidés par les deux `verify.py` ci-dessus. Je n'ai pas relancé Docker (hors droits/périmètre du vérificateur), mais l'intégrité du paquet livré est confirmée.

## 3. Régressions ou modifications non demandées

- Aucune régression dans le périmètre A-26 : les trois instructions sont appliquées et tout le vert tient.
- **Refactor de staging** : `wp/outils/staging/lib.php` a été fortement réduit (−858 lignes), éclaté en `engine.php` / `guard.php` / `store.php` / `form-decision-refused.php`. C'est la « stabilisation de staging » évoquée au §5 de la fusion, et non une dérive A-26 ; le gel reflète fidèlement ces fichiers. Modification lourde mais cohérente avec l'instruction 1 (rejouer sur les dépendances **actuelles**).
- Les autres changements des mêmes commits de synchro (a27, a29, a30, a31, b08, c23, c25, c26, a25, plugin `imagine-site`) sont des travaux parallèles d'autres lots, **hors périmètre A-26** — pas des régressions de cette correction.

## 4. Verdict : **Prêt pour la validation de Ced**

B1, I1 et M1 sont levés et prouvés ; sceau vert rejoué sur les dépendances actuelles ; aucun problème de fond restant côté code. Il subsiste la question ouverte de la fusion (§5), qui relève par nature de Ced :

> Le staging dont dépend la preuve de neutralisation a été refactoré, puis A-26 rescellé **maintenant** (conformément à l'instruction 1). Le défaut prudent proposé était « attendre la stabilisation de staging, puis resceller une seule fois ». Si staging rebouge, A-26 devra être rejoué et rescellé à nouveau.

Ce n'est pas un défaut de correction mais un arbitrage réel adressé à Ced. Rien d'autre ne remonte.

**Rappel : cette vérification n'est pas un GO.** Elle atteste la levée des trois points et la validité du paquet scellé ; la clôture appartient à Ced (question §5).
