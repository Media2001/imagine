# Vérification A-27 — second et dernier tour

Vérificateur : Claude. Date : 2026-11-27. Base relue : commit `8256b49b` (fusion `corrections/A-27.md`, 00:58). État vérifié : arbre de travail courant (HEAD = `2ac3cd66`, aucune modification non commitée sur les chemins A-27).

Méthode : `git log`/`git diff 8256b49b..HEAD` sur `wp/outils/bascule/a27`, `wp/tests/a27`, `wp/outils/staging` et `production/A-27` ; relance des deux vérificateurs de scellé et de la matrice Python. Je ne refais pas la relecture complète.

**Point de méthode préalable.** Hermès a corrigé en **deux passes**. La première (`production/A-27/corrections-1h30.md`, ~1 h 30) ne touche que le code et dit explicitement « aucun PRET créé, aucun sceau modifié, vérificateurs volontairement rouges, R1 reste au parent ». Une **seconde passe** (parent, 05:03) a requalifié et resellé : `parent-gates.json` daté `2026-11-27-05h03-qualification-A21-A27`, nouveau `PRET`, `preuves/final/` et `manifest.json` régénérés. **`corrections-1h30.md` est donc périmé** : il décrit l'état intermédiaire, pas l'état final. C'est l'état courant (reselé) qui fait foi, et c'est lui que j'ai vérifié.

---

## 1. Instructions de `corrections/A-27.md`, une à une

### R1 — Requalifier et resceller (bloquant) : **Appliquée.**
- Requalification parent présente : `production/A-27/parent-gates.json` → répertoire `2026-11-27-05h03-qualification-A21-A27`, `commands: 19`, `exit_code: 0`. Paquet, scellé et `PRET` régénérés (`production/A-27/PRET`, 2026-11-27T05:03:18 : « nouvelle matrice et gates réelles, sceau courant vert »).
- **Les deux vérificateurs repassent verts sur l'arbre courant** (ce qui était rouge au moment de la fusion) :
  - `production/A-27/verify.py` → `exit_code: 0` ; `package_and_inventory: PASS`, `frozen_sources: PASS`, `native_packet: PASS`, `parent_gates: 19`.
  - `wp/tests/a27/verify.py --evidence production/A-27/preuves/final` → `exit_code: 0` ; en particulier `exact_current_dependencies: PASS`, `exact_current_sources: PASS`, `utf8:executed_dependencies` et `cp1252:executed_dependencies: PASS` — exactement les contrôles que Codex avait vus rouges (R1).
- Les dépendances `wp/outils/staging` (dérive post-scellé qui avait cassé R1) sont désormais couvertes par le paquet reselé : l'empreinte vivante correspond. R1 est levé **mécaniquement et vérifié**, pas seulement actualisé.

### R2 — Vide ≠ illisible à la frontière de l'adaptateur : **Appliquée.** `Inventory.php:25-62`, usage ligne 124.
- Nouvelle méthode privée `paymentReference()` : un observateur non transformant (priorité `PHP_INT_MAX`) lit le schéma pendant la **même** évaluation de `woocommerce_subscription_payment_meta` que A-19, sans rejouer le filtre ; champ déclaré non scalaire / nul / non interprétable + verdict A-19 `absent` → renvoie `unknown` (jamais `absent`). Observateur retiré dans un `finally`. A-19 n'est pas modifié (conforme à l'interdit §3).
- Côté `Analysis` : `unknown` fait `present = true` (ligne 126) → l'abonnement est compté `automatic`/`illisible`, pas exclu. La règle « illisible, jamais absent » tient.
- Test ajouté demandé présent et vert : cas natif `correction-opaque` en **classique et HPOS** (`ppcp-gateway`, schéma opaque, cinq abonnements, aucun jeton → cinq `automatic illisible` + cinq `subscriptions_link_unknown`). Contrôles `*:correction_exact_counts_opaque`, `*:correction_projection_opaque`, `adapter_boundary_required` : PASS. Témoin rouge `red-r2.json_targeted_red` : PASS (la correction retirée rougit bien).

### R3 — Contradiction avant le repli de type : **Appliquée.** `Analysis.php:109-111`.
- Garde ajoutée **avant** le repli par passerelle : `if ($ids && (count($matches) !== 1 || !in_array($matches[0]['id'], $ids, true)))` → `illisible` + `link = unknown`, sans choix d'instrument. Couvre lien B / référence A et lien explicite sans correspondance.
- Le repli `mandat_sepa` / `accord_paypal` reste réservé à la **référence seule sans lien** (`$ids` vide), ligne 117-119 — conforme à la consigne.
- Tests distincts présents et verts : cas natifs `correction-conflict`, `correction-reference-only`, `correction-unique` en classique et HPOS ; contrôles `r3_required_distinct_cases` et `*:correction_*` : PASS. Témoin rouge `red-r3.json_targeted_red` : PASS.

### Instruction 4 — M-1 / M-2 (à la main d'Hermès) : **Appliquée.**
- M-1 : `cards` conserve `later`/`illisible` sans fusionner les deux comptes du brief (`corrections-1h30.md` §Mineurs). Choix tracé.
- M-2 : note README sur l'id de passerelle SEPA conservée ; aucun id réel supposé.

### Instruction 5 — Écart à tracer dans `docs/ecarts.md` : **Appliquée.**
- `docs/ecarts.md:100` : « A-27 · aucun nombre utile sur une copie neutralisée… le compte réel demanderait une lecture de la source par Ced, hors agents ». L'écart est inscrit (par la main habilitée, hors droits du relecteur).

## 2. Résultat des tests (relancés localement)

- `production/A-27/verify.py` : `exit_code: 0`, tout PASS.
- `wp/tests/a27/verify.py --evidence production/A-27/preuves/final` : `exit_code: 0`, ~190 contrôles tous PASS (dépendances/sources courantes, matrice de commandes, immutabilité DB/fichiers classique+HPOS, canari absent, PSR-12, témoins rouges R2/R3, cas de correction natifs).
- Matrice Python indépendante (`wp/tests/a27/matrix.py`, hors scellé) : **41 tests verts en UTF-8 et 41 en cp1252**, `exit_code: 0`, `readiness_claimed: false`, `sources_stable: true`.

**Limite de ce tour (identique au premier).** Je n'exécute pas les matrices natives PHP/Docker (pas de PHP hôte, Docker/WSL réservés à A-28). Les preuves natives sont **liées au paquet par SHA-256 et revérifiées**, mais leur exécution reste celle du parent ; je confirme l'intégrité et la cohérence du paquet, pas une ré-exécution native indépendante. Ce n'est pas un défaut constaté — c'est le périmètre du relecteur.

## 3. Régressions ou modifications non demandées

- **Code A-27 propre** : modifications limitées à `Analysis.php` (les 3 lignes R3), `Inventory.php` (la méthode R2), `README.md` (documentation), plus des tests ajoutés/ajustés. Aucun débordement de périmètre, aucune régression dans la logique de comptage. Le diff `Analysis.php` est exactement la garde R3, rien d'autre.
- **Refonte de `wp/outils/staging`** (`engine.php` +971, `lib.php` −858, nouveaux `guard.php`, `store.php`, `form-decision-refused.php`) : **hors A-27**, issue du travail d'import A-28. Elle n'est pas une régression A-27 ; elle est la dérive de dépendance qui avait cassé R1, désormais absorbée par le reselé (dépendances vertes). À signaler comme contexte, pas comme défaut A-27.
- **`corrections-1h30.md` périmé** : il décrit la 1re passe (« vérificateurs volontairement rouges, aucun PRET ») alors que la 2e passe a reselé et mis `PRET`. Incohérence documentaire, sans effet sur le code. À ne pas lire comme l'état final ; une main habilitée pourrait l'annoter.

## 4. Points ouverts rappelés (ne relèvent pas du code A-27, mais conditionnent la clôture — doctrine §6)

Ce ne sont pas des problèmes de fond restants sur les corrections ; ce sont les arbitrages déjà posés par la fusion, qui restent à la main de Ced :
- **Porte A-22.** `parent-gates.json` : `A22_independent_review_closed: false` ; `PRET` dit « prêt à relire seulement, A22 non clos, aucun GO réel ». La clôture dépend de la fermeture de la relecture A-22.
- **Requalification à refaire une fois** après l'arrivée de la vérification d'A-28 (`docs/ecarts.md:99,112`) : le scellé courant gèle l'empreinte de l'import ; une dernière requalification A-21→A-27 est attendue.
- **Deux questions métier / réel pour Ced** (fusion §5), inchangées : borne du seuil « six mois » (défaut appliqué : borne au jour d'audit) ; procédé de comptage à la source sur copie non neutralisée sous GO écrit (défaut : rien de réel sans GO).

## 5. Verdict

**Prêt pour la validation de Ced.**

Les trois corrections bloquante/importantes (R1, R2, R3) sont appliquées, ciblées et **vérifiées vertes sur l'arbre courant** par les deux vérificateurs de scellé et par la suite Python relancée. Les mineurs et l'écart sont traités. Aucune régression dans le code A-27 ; aucune modification non demandée dans son périmètre propre.

Il ne reste **aucun problème de fond** sur les corrections demandées. Les points du §4 (porte A-22, requalification post-A-28, deux questions pour Ced) sont des conditions de clôture connues et déjà remontées, pas des défauts du code corrigé. Ce verdict n'est pas un GO : la clôture reste subordonnée à la fermeture d'A-22, à l'exécution native parent après A-28 et aux arbitrages de Ced ci-dessus.
