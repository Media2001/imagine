# Vérification B-13 — second et dernier tour

Vérificateur indépendant. Objet : contrôler l'application des huit instructions de `corrections/B-13.md` par Hermès, rejouer les tests, détecter régressions et modifications non demandées. Pas de relecture complète refaite.

Méthode : `git diff 74b59d9a..HEAD` (commit du 27/11 22:33, état relu) sur `wp/` et `production/B-13`, lecture du code corrigé, rejeu des tests hors-ligne autorisés au relecteur (`verifier.py`, `qualifier.py`). Le live (`--live`) exige un staging ouvert : hors de mes droits, non joué.

## 1. Application des instructions

| # | Instruction | État | Preuve |
|---|---|---|---|
| 1 | B13-01 — illustrer chaque article de la sélection, sans remplacer un récent par un ancien | **Appliquée** | `b13-seed.php:13-52` ($finish) : pour chaque article sélectionné sans vignette, pose la couverture synthétique du numéro (`set_post_thumbnail`, :40) ; l'article reste le même, aucun remplacement. Preuve navigateur : 54 assertions `_image_article_` (une par article × 6 surfaces), 9 images par surface. RED témoin `red-illustrations-V2.json` = `AssertionError('anonyme_0_image_article_44')`. |
| 2 | B13-01 — décider/documenter le cas « récent sans image » et appliquer le défaut technique | **Appliquée** | Défaut retenu (laisser sans image, ni placeholder ni exclusion) documenté dans `README.md` (bloc « Corrections B13-01 à B13-04 ») et `A-VOIR.md`. Test `recent_sans_image_garde_sans_placeholder` (`b13-runtime.php:75`) : `<li>` présent, zéro `<img>`. |
| 3 | B13-02 — rendre le raccord « S'abonner » idempotent au rejeu, avant le retour anticipé | **Appliquée** | $finish appelé **aussi** sur le chemin de re-seed (`b13-seed.php:57`, branche `$old`) et le chemin initial (:101) ; il revérifie l'entrée `abonnement` détenue et réapplique `_menu_item_url` sans changer d'identifiant. |
| 4 | B13-02 — test de séquence B-08 → B-13 → B-08 → B-13 (destination finale + pas de doublon) | **Appliquée** | `b13-runtime.php:18-29` : boucle 2 passages sur les **vrais** seeds. `b08_retablit_ancre_*` (ancienne ancre réintroduite), `b13_repare_destination_*` (réparée vers `abonnementUrl()`), `sequence_ids_et_nombre_conserves_*` (mêmes IDs/nombre d'entrées → pas de doublon). RED témoin `red-reseed-V2.json`. |
| 5 | B13-03 — ajouter le hook `deleted_term_relationships` + test du retrait direct | **Appliquée** | Hook ajouté `Navigation.php:16`. Test `b13-runtime.php:77-82` : cache d'abord présent, `wp_remove_object_terms`, cache vidé, article absent et thématique devenue vide conservée. RED témoin `red-retrait-direct-V2.json`. |
| 6 | B13-04 — comparer les IDs exacts par thématique pour les réglages 1, 3, 10 (date DESC puis ID DESC) + cas vide distinct | **Appliquée** | `b13-runtime.php:84-112` : deux thématiques temporaires de 12 articles, oracle trié indépendant, `selection_exacte_{1,3,10}_terme_*` (6 assertions, confirmé par `verifier.py`). Cas thématique vide gardé distinct (instruction 5). |
| 7 | Claude — filtrer la sur-invalidation `save_post` **ou** la laisser et le noter | **Appliquée** (option « laisser + noter ») | Laissée telle quelle, notée dans `README.md` et `A-VOIR.md` (« sans risque métier »). Choix autorisé par l'instruction. |
| 8 | Claude — noter au README la dépendance à la classe `imagine-nav-thematiques` | **Appliquée** | `README.md` (bloc corrections) : disparition silencieuse si la classe de l'entrée B-08 est retirée, fragilité héritée documentée. Code inchangé (`Navigation.php:84`). |

Décisions techniques du §5 de la fusion appliquées conformément : ordre alphabétique des thématiques conservé ; article récent sans image laissé sans image.

## 2. Résultat des tests

- `python -B production/B-13/verifier.py` → **PASS** :
  `{"B13":"PASS","native":34,"browser":123,"surfaces":6,"phpunit":1,"replay_tests":1208,"replay_assertions":36685,"tools":{"failures":0},"foreign_packets":[]}`
  - 34 contrôles natifs (dont séquence re-seed, retrait direct, 6 × `selection_exacte_`), 123 navigateur sur 6 surfaces (54 assertions d'image, 9 images/surface) ;
  - 1 test PHPUnit scellé `NavigationB13Test` sans échec ; rejeu 1208 tests / 36685 assertions, 0 échec d'outil, 0 paquet étranger ;
  - les trois RED (`red-illustrations`, `red-reseed`, `red-retrait-direct`) prouvent chaque correctif par discipline RED→GREEN.
- `python -B production/B-13/qualifier.py` → **PASS** (9/9) : bloc bootstrap et section README bornés, exacts, uniques ; voisins préservés.
- Intégrité des preuves : `verifier.py` assert `native['sources'] == browser['sources'] == sources()` → les JSON archivés ont été produits sur les **octets actuels** de `Navigation.php`, `b13-seed.php`, `b13-runtime.php`, etc. Les preuves ne sont donc pas périmées par rapport au code relu. Le live resté non joué (droits) : `verifier.py --live` et les captures restent à la charge du poste de Ced.

## 3. Régressions et modifications non demandées

- Aucune régression B-13. La seule modification du fichier scellé `Navigation.php` est l'ajout du hook (B13-03) ; `abonnementUrl()` préexistait.
- Le diff depuis l'état relu contient aussi des fichiers **B-14/B-15** (`Accueil.php`, `catalogue.php`, `single-imagine_numero.php`, `b14-*`, tests `AccueilB14*`). Ce sont des lots voisins en cours, hors périmètre B-13 : ce ne sont pas des régressions B-13, et `foreign_packets: []` + `qualifier` PASS confirment qu'ils ne périment pas les preuves B-13.
- Nouvelles données permanentes : neuf images synthétiques assignées aux articles de démonstration — assumé et documenté. Fixtures/menus/relations temporaires annulés en transaction. Aucun compte, prix, droit, article réel, envoi ni déploiement.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les huit instructions sont appliquées et prouvées ; tests hors-ligne au vert ; aucun problème de fond restant, aucune régression. Rappel doctrine §6 : ce verdict n'est pas un GO. Restent à la main de Ced, non bloquants pour la clôture code : la validation visuelle (libellé « Connexion » connecté, forme du menu étendu sur maquette) et le rejeu `--live` sur staging.
