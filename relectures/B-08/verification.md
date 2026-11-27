# Vérification B-08 — second et dernier tour

Date : 27 novembre 2026. Vérificateur indépendant, après fusion `corrections/B-08.md` et corrections d'Hermès.

Base de comparaison : état relu `a717952d` (dernière synchro avant les corrections, 04:08) → `HEAD`. Les corrections B-08 ont toutes atterri à partir de la synchro de 05:08. Diff ciblé sur `wp/plugins/imagine-site/`, `wp/outils/demo/b08-seed.php` et les tests. Pas de nouvelle relecture complète.

---

## 1. Instructions de `corrections/B-08.md` (§4)

### 1 — Antislash (B08-01). **Appliquée.**
`Sujet.php:58` : `meta_input => wp_slash($meta)` au lieu de `$meta`. Les valeurs sont slashées à la frontière `wp_insert_post()`, comme l'exige la convention WordPress ; `update_metadata` les déséchappe une fois, le stocké redevient la valeur normalisée. La boucle de vérification `Sujet.php:62-63` compare toujours contre `$meta` **normalisé** (non slashé) — cohérent. Un sujet contenant `\` est désormais accepté et relu à l'identique.

### 2 — Test qui masquait B08-01. **Appliquée.**
- Stub fidèle : `SujetWPStubs.php:58` — `wp_insert_post` applique `wp_unslash($row['meta_input'])` comme le vrai `update_metadata` ; ajout de `wp_slash` et de `add_meta_box` (lignes 46-47) pour rendre le détail admin testable.
- Cas passant par `$_POST` : `SujetAdapterTest.php:52` (`testAntislashDuPostAuDetailAdminEtExport`). `$_POST` slashé, sujet `C:\dossier\fichier` + antislash final + apostrophe. Vérifie le **succès** (`enregistrée`), puis la **conservation exacte** en métadonnée, dans le **détail admin** (meta box rendue) et dans l'**export** `SujetConfidentialite::exporter`, avec `mail=0 / http=0`.

### 3 — Reprise du seed de menu (B08-02). **Appliquée.**
`b08-seed.php` : le témoin d'appartenance est inscrit **au moment de la création**, plus en dernier.
- Menu : hook `wp_create_nav_menu` → `$rememberMenu` écrit `imagine_b08_menu` dès la création du terme (`b08-seed.php:40-53`).
- Items : hook `wp_add_nav_menu_item` → `$rememberItem` marque la méta et l'option dès l'insertion (`b08-seed.php:104-122`).
- Un item interrompu avant rattachement est récupéré au rejeu (`b08-seed.php:87-101`), et le refus d'un menu/item **étranger** est conservé (`Collision menu B08` ligne 38, `Item étranger` lignes 83/93/99/106).
- Couvert par les tests seed `wp/tests/demo/b08-seed-reprise.php`, `b08-seed-collisions.php`, `b08-seed-cibles.php` et les mutants seed (voir §2).

### 4 — README (§5 doctrine). **Appliquée.**
`wp/plugins/imagine-site/README.md` : nouvelle section **B-08** (deux réglages, type privé `imagine_sujet`, `wp_slash`, callbacks export/effacement, commande de rejeu, renvoi `production/B-08/{NOTE.md,A-VOIR.md}`). Les sections **B-06** et **B-07**, qui manquaient aussi, sont comblées au passage, comme suggéré.

### 5 — Durcir les cibles d'URL. **Appliquée.**
`b08-seed.php:57-65` : helpers `$pageUrl` (page publiée seulement) et `$archiveUrl` (archive existante seulement), appliqués à `kiosque`, `newsletters`, `agenda` et `compte` (`b08-seed.php:67-74`). Une cible absente donne une URL vide, jamais un repli silencieux. `wc_get_page_permalink('myaccount')` est remplacé par `wc_get_page_id` + `$pageUrl`, gardé par `function_exists`.

### 6 — Schéma `https` seul (décision technique). **Appliquée.**
`Soutenir.php:22` : `parse_url($url, PHP_URL_SCHEME) === 'https'` au lieu de `in_array(..., ['https','http'])`. Test `SoutenirAdapterTest.php:50` (`testPartsRefuseHttpEnLectureEtEcriture`) : un `http://…` est refusé en écriture (`nettoyer`), ignoré en lecture (`configuration`), et absent du rendu.

### 7 — Colonne de liste admin (optionnelle). **Non appliquée.**
Aucun hook `manage_{post_type}_posts_columns` dans `Sujet.php`. Instruction marquée *optionnelle* (« à laisser si le temps manque ») : sans incidence métier ni fuite. Non bloquant.

---

## 2. Résultat des tests

> Le rejeu officiel PHPUnit tourne dans Docker/WSL (`wp/tests/rejouer.ps1`). Dans cette session non interactive, le lancement de PowerShell/Docker/WSL a été refusé par la couche d'autorisation. J'ai donc exécuté le vérificateur scellé sans réseau, qui recalcule le SHA-256 des sources sur disque et les compare à l'empreinte enregistrée au moment du run vert : **les sources actuellement sur disque sont bit-à-bit celles qui ont produit le run vert enregistré.**

`python -B production/B-08/verifier.py` → **PASS** (délègue à `verifier-corrections.py`, `scope = imagine-test-demo`) :

- **Suite globale** : 1153 tests / 36075 assertions, 0 échec / 0 erreur / 0 ignoré ; 582 contrôles outils, 0 échec, aucun outil exclu.
- **Suite B-08 locale** : 8 tests / 194 assertions, 0 échec (était 6 / 181 à la relecture → +2 tests, +13 assertions = les deux cas ajoutés, antislash et refus `http`).
- **Mutation** : 14 mutants PHP tués (dont les nouveaux `slash` et `https`) + 2 mutants seed (`item`, `cible`) ; chaque mutation fait tomber au moins un test. Preuves RED associées : `corrections-red-slash.log` et `corrections-red-https.log` montrent exactement 1 échec **avant** correctif (TDD).
- **Seed** : contrôles `reprise` (5), `cibles` (7), `collisions` (10), `http` (35) tous vrais ; `exact_restoration` et `business_preserved` vrais ; oracles RED `reprise_sans_doublon = false` et `compte_sans_url_si_cible_absente = false` avant correctif.
- **Nettoyage** : aucun sujet résiduel, `don = false`, `parts_url = ''`, observateur et seed retirés. 10 pages / 15 items natifs.
- Empreintes des sections README (B-06, B-07, B-08) conformes au manifeste.

Je n'ai pas pu relancer moi-même PHPUnit en conteneur ; la preuve ci-dessus est une vérification d'intégrité du paquet, pas une ré-exécution. C'est la seule limite de ce tour.

---

## 3. Régressions ou modifications non demandées

- **Aucune régression B-08.** Les seules sources de production B-08 modifiées sont `Sujet.php` (instr. 1), `Soutenir.php` (instr. 6), `b08-seed.php` (instr. 3, 5), `README.md` (instr. 4) ; côté tests `SujetWPStubs.php`, `SujetAdapterTest.php`, `SoutenirAdapterTest.php` (instr. 2) plus les tests seed. Tout correspond aux instructions, rien au-delà.
- **`imagine-site.php:143-150`** : ajout additif du chargement B-09 (Contact / AutresPages). N'altère pas l'enregistrement de `Soutenir`/`Sujet` (lignes 140-142 inchangées). Hors périmètre B-08, non régressif.
- Le reste du diff `wp/` depuis la base (A-30, A-31, B-09, C-23, C-26, Contact) relève de lots parallèles d'Hermès, sans contact avec B-08.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les sept instructions sont traitées (six appliquées et vérifiées au code et aux tests ; la septième, optionnelle, volontairement laissée). Aucun problème de fond restant, aucune régression, aucune question ouverte pour Ced dans ce lot.

Rappels de doctrine, non bloquants pour ce tour mais hors de ma portée :
- Je n'ai **pas** pu ré-exécuter PHPUnit en conteneur ni le rejeu HTTP « live » (pas d'accès site/base, et lancement Docker refusé ici). La preuve verte repose sur les logs enregistrés par Hermès, dont j'ai confirmé que les sources scellées égalent les sources sur disque.
- Un verdict de vérification **n'est pas un GO** : restent la validation visuelle du thème/menu par Ced et le rejeu HTTP sur `imagine-test-demo`.
