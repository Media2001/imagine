# Vérification A-33 — Le poids des archives (2e et dernier tour)

Date : 2026-11-28. Vérificateur : Claude. Base : `corrections/A-33.md` (fusion du 28/11, 3 h 48).
Diff relu : `git diff bd5113ea..HEAD` (version relue → correction `6616351d`) sur `wp/outils/bascule/a33/`, `wp/tests/a33/` et `production/A-33/`.
Ce n'est pas une relecture complète : je contrôle l'application des cinq instructions, les tests, et les écarts.

## 1. Instructions de `corrections/A-33.md`, une par une

### Instruction 1 — I2, ne pas écraser l'appartenance aux dix — **Appliquée**
- `wp/outils/bascule/a33/Inventory.php:101` : `$keep = (bool) array_intersect(...)` est devenu `$keep = $keep || (bool) array_intersect(array_map('intval', $links), $recentIds);`. C'est exactement la correction proposée. Un numéro reconnu sélectionné (`:88`) reste conservé.
- Banc : `wp/tests/a33/inside.py:192-198` ajoute un mapping `article_type === 'a16_numero'` (type partagé) en `post_type` et le contrôle `shared_type_selected_issue_stays_kept` vérifie que le numéro sélectionné n'apparaît pas dans `published_outside` et que `recent_media` reste cohérent.
- A-16 n'est ni modifié ni durci (aucun fichier `a16/` dans le diff).

### Instruction 2 — I1, inclure les PDF référencés par `pdf_cle` dans `recent_media` — **Appliquée**
- `Inventory.php:67-78` : pour chaque numéro sélectionné, lecture de `pdf_cle` dans `postmeta` (post) ou `termmeta` (terme), selon `numero_source`, comme A-16. Les ID de PDF sont collectés dans `$pdfs`.
- `Inventory.php:142-144` : une pièce est comptée `recent_media` si `isset($pdfs[$id]) || isset($recent[$parent])`. Dédoublonnage par ID de pièce (chaque pièce vue une fois, garde `$seen` `:133-136`).
- `orphan_media` reste séparé et identifiable (`:139-141`, bloc distinct) ; un PDF orphelin figure dans les deux compteurs, non additifs — défaut technique proposé, appliqué tel quel.
- README documente le choix (`wp/outils/bascule/a33/README.md`, paragraphe « Les pièces des numéros conservés… »), conforme à la décision par défaut (pas l'acception stricte `post_parent`).
- Banc : contrôles `pdf_post_orphan_and_shared_deduplicated` (`inside.py:179`), `pdf_taxonomy_and_multilink_deduplicated` (`:191`), variante taxonomie `recent_media == weight(5, 4, 1, 70)` (`:190`). Le cas taxonomie (terme, PDF jamais parenté) est bien exercé.

### Instruction 3 — compléter le semis sur les quatre angles morts — **Appliquée**
`wp/tests/a33/seed.php` (et le miroir `inside.py`) :
- (a) Année inconnue avec pièce : `seed.php:43-45` crée un `post` publié à `post_date_gmt = '0000-00-00 00:00:00'` portant la pièce `[$unknown, 37]` (`:52-53`). Contrôle `unknown_year_attachment_json` (`inside.py:180`).
- (b) Article lié à deux numéros (un ancien, un des dix) : `seed.php:57` `wp_set_object_terms($articles[0], [$terms[0], $terms[11]], 'a16_issue')`, avec PDF partagé ; contrôle de non-double-comptage dans `pdf_taxonomy_and_multilink_deduplicated`.
- (c) Égalité de dates à la frontière : `seed.php:22-23` `(2010 + ($i === 1 ? 2 : $i))` force `issues[1]` et `issues[2]` à `2012` ; contrôle `tie_boundary_a16_id_order` (`inside.py:181`), départage par ID hérité d'A-16.
- (d) Cas I1/I2 : couverts par les contrôles cités aux instructions 1 et 2.
- Les `_a16_pdf_id` ne sont plus tous à `'0'` : `seed.php:54-56` fixe de vrais ID de pièce pour `issues[9]`, `[10]`, `[11]` (post et terme).

### Instruction 4 — renouveler les preuves — **Appliquée**
- `production/A-33/` a été renouvelé (diff ~416 Ko : preuves re-scellées, `manifest.json`, `RAPPORT.md`).
- Le vérificateur scellé `production/A-33/verify.py` passe : `{"lot": "A-33", "exit_code": 0, "checks": [{"check": "A33_PACKAGE_PASS", "status": "PASS"}]}`. Il contrôle les empreintes de toutes les traces livrées (python-tests, natives, style, portails) : la chaîne de preuves est complète et verte, et couvre les nouveaux contrôles.
- `PRET` existe (`production/A-33/PRET`).
- Réserve d'honnêteté : je n'ai **pas** pu relancer moi-même le harnais sanctionné `rejouer.ps1` dans cette session (Docker bloqué par le bac à sable). Ma vérification indépendante s'appuie sur (1) le vérificateur scellé ci-dessus et (2) les suites Python exécutables sur l'hôte (§2). Le rejeu Docker complet reste attesté par les traces livrées, pas par une exécution fraîche de ma part.

### Instruction 5 — dater ou corriger la documentation périmée — **Appliquée**
- `production/A-33/BLOCAGE.md:15` : « État initial du 27 novembre 2026 uniquement … Cet état n'est pas le statut courant ; consulter le marqueur et le lecteur sans argument. » Le présent litigieux a disparu.
- `production/A-33/BLOCAGE.md:33` : « Attendus historiques du premier candidat, le 27 novembre 2026 (périmés depuis la réception du 28 novembre à 2 h 25) … ». Le titre « Attendus actuels » a été supprimé au profit d'« Attendus historiques ».
- `RAPPORT.md` aligné (fusion appliquée, réception post-PRET PASS). L'historique de fond n'a pas été réécrit.

## 2. Résultat des tests

Exécutés par moi, sur l'hôte, depuis la racine :
- `python -B production/A-33/verify.py` → **PASS** (`A33_PACKAGE_PASS`, exit 0).
- `python -B production/A-32/verify.py` → **PASS** (`A32_PACKAGE_PASS`, exit 0). L'invalidation `A32_PARTIAL_EVIDENCE` qui bloquait le premier candidat est levée : A-32 a bien été requalifié sur les sources incluant A-33.
- `python -B production/A-31/verify.py` → **PASS** (`A31_PACKAGE_PASS`, exit 0).
- `wp/tests/a33/test_delivery.py` → **11 tests OK** (dont `test_missing_pure_controls_refused`, nouveau seuil 852 contrôles).
- `wp/tests/a33/test_report.py` → **19 tests OK**, dont `test_actual_file_channel_tampering` qui déclenchait une `PermissionError` chez Codex au 1er tour : plus d'échec environnemental ici.

Non exécutés par moi : les contrôles natifs confinés (`inside.py`, inotify/libc Linux), les unités PHP pures (`unit.php`) et le portail général — ils tournent dans `rejouer.ps1` (Docker), indisponible dans cette session. Ils sont attestés verts par les traces scellées validées par `verify.py` (1 243 tests / 37 036 assertions, 23 outils, 852 contrôles d'après `RAPPORT.md`).

## 3. Régressions et modifications non demandées

Aucune régression détectée : logique `orphan`/`kept`/`byYear`/`other` équivalente hors des ajouts I1/I2 ; le dernier `elseif ($parent !== 0 && $attachment['parent_exists'] !== null)` (`:147`) reproduit l'ancien `else` sans changer le classement des pièces déjà couvertes par le bloc orphelins. A-16, l'import, le gardien et le lanceur ne sont pas touchés.

Modifications présentes dans le diff **au-delà** des cinq instructions, à signaler :
- **`wp/tests/a33/run.py` — liste `DEPS` resserrée** : les globs larges (`a11`, `a12`, `a16` entiers, `staging`, `staging-court`, `t01`, `a02-audit` entier) sont remplacés par une liste close de fichiers réellement copiés par le banc. Change la photographie des sources du banc. Non demandé par `corrections/A-33.md` ; cohérent avec le chantier parallèle de clôture T-03 (« lecteur borné aux fichiers du lot »). Tests verts, pas de régression observée.
- **Machinerie « paquet bloqué » : `seal.py` + `probe.py` (`--blocked`), `gates.py`, `delivery.py` (`gates_recorded`)** : ajout d'un mode préservant un paquet à portail réellement rouge (`A33_GATES_INVALID`) sans jamais accorder PRET, et conservation des deux reçus de portail même si le premier est rouge. Non demandé par la fusion. Le paquet **final livré n'est pas en mode bloqué** (verify = `A33_PACKAGE_PASS`, PRET présent) : cette infrastructure a servi l'état transitoire, pas la livraison. Tests verts.

Ces deux points ne contredisent aucun nombre produit ni aucune instruction ; ils élargissent le périmètre touché. À arbitrer après coup par Claude (décision technique), sans blocage.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions de `corrections/A-33.md` sont appliquées, vérifiées sur le code et le banc. Les vérificateurs scellés des trois paquets passent, les suites Python exécutables sur l'hôte passent, et le défaut d'environnement de Codex (PermissionError) ne se reproduit pas. Aucun problème de fond restant, aucune question visuelle ou touchant au réel. Seules réserves consignées : (1) le rejeu Docker complet n'a pas été relancé par moi dans cette session et repose sur les traces scellées ; (2) deux élargissements de périmètre non demandés (`DEPS` resserré, machinerie « bloqué ») à arbitrer techniquement après coup.

Un verdict n'est pas un GO.
