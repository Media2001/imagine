# Relecture A-12 — L'inventaire des contenus à reprendre (Claude, relecteur indépendant)

Brief : `briefs/A-12-inventaire-des-contenus.md`. Cahier des charges : §4.3 (premier point) et §4.2.
Code : `wp/outils/bascule/a12/` (`Command.php`, `Inventory.php`, `Registry.php`, `AuditLibrary.php`, `confine.py`).
Tests : `wp/tests/a12/`. Production : `production/A-12/`.

Je n'ai pas ouvert `codex.md`. Pas de fusion à ce stade.

---

## Rejeu de la suite autorisée

Commande exécutée, sans argument, depuis la racine :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernière ligne obtenue :

```
REJEU : 1062 tests, 34271 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Conteneur jetable, sans réseau, dépôt monté en lecture seule, exit 0. Tout est vert.

**Mais ce rejeu ne teste pas A-12.** La suite T01 découvre quatre paquets PHPUnit (`imagine-connecteur`, `imagine-non-regression`, `imagine-pilotage`, `imagine-site`) ; aucune trace de `a12`/`ContentInventory` dans la sortie. Le collecteur A-12 est un outil CLI confiné (Landlock, conteneur Linux, MariaDB par socket), testé par son propre harnais Python `wp/tests/a12/run.py` → `inside.py`, qui exige en plus les extensions sous licence (`/home/ced/staging-wp/plugins/`). Je ne peux pas rejouer cette suite dédiée avec la commande autorisée.

**Ce que le rejeu prouve donc réellement : la non-régression des quatre bibliothèques existantes.** C'est utile (A-12 réutilise A-11 sans le modifier) mais orthogonal au lot. J'ai vérifié A-12 autrement : déroulé manuel du code contre la fixture `seed.php`, recoupé avec les preuves committées `production/A-12/preuves/final/`. Ces preuves sont les artefacts d'Hermès, donc pas une vérification indépendante ; mon déroulé manuel, lui, l'est, et il concorde (voir §2).

---

## 1. Conformité

Le lot fait ce que demande le brief, en lecture seule, sans décider d'aucun rattachement. Chaque exigence est couverte :

- **Types et taxonomies enregistrés, qui les déclare, comptes par état, première/dernière date** : `Inventory::collect()` + `Registry`. Déclarant attribué par la pile des appels `register_post_type`/`register_taxonomy` réellement exécutés (`Registry::record`/`origin`), catégorie cœur/thème/extension/MU, fichier relatif lisible. Hors API ou illisible → `unknown`, jamais inventé. Conforme §4.3/§4.2.
- **Par taxonomie : nombre de termes + vingt termes les plus utilisés (nom + nombre)** : `collect()`, `LIMIT 20`, tri `n DESC, nom binaire, id interne`. Noms de rubriques autorisés par le brief. Conforme.
- **Clés de métadonnées par type + nombre de contenus porteurs, jamais les valeurs** : `collect()`, `COUNT(DISTINCT m.post_id)`, toutes les clés, internes incluses. Conforme.
- **Pièces jointes : poids et nombre par type MIME, PDF, orphelines** : `attachments()`. Conforme.
- **Liens visibles contenu↔produit, comptés par clé reconnaissable, sans interprétation** : `productLinks()`. Conforme.
- **Classique et HPOS ; aucun écrit en base, aucune tâche, aucun envoi, aucun HTTP** : étanchéité prouvée (§4). Conforme.

**Interprétations signalées (bon point).** Trois choix de silence du cahier des charges sont écrits dans le rapport produit (`conventions`/`limitations`) et dans le README : dates limitées aux contenus actuellement `publish` ; orphelin = parent nul/inexistant (pas « inutilisé ») ; poids = originaux locaux hors miniatures. Aucune interprétation non signalée relevée.

**Léger dépassement, documenté.** Le brief demande les objets « enregistrés ». L'outil ajoute aussi les types/taxonomies seulement stockés mais non enregistrés, marqués `stored_only_unregistered` et exclus des totaux du registre. Pour un audit de migration c'est un plus justifié et clairement séparé. Non bloquant.

## 2. Exactitude métier — déroulé manuel

J'ai déroulé à la main deux cas de la fixture `seed.php` et comparé à la sortie committée `classic-contents/contenus.json`.

**Cas 1 — type `a12_article` (5 contenus, 4 états, champs dupliqués).**
Attendu par le code : publish 2, draft 1, private 1, trash 1 → `content_count` 5 ; dates des seuls publiés : min 2024-02-03T11:00:00Z (ids[0]), max 2025-02-03T11:00:00Z (ids[1]) ; clés `a12_field` sur 5 contenus, `_a12_product_id` sur 3, `_A12_product_id` sur 1 (casse distincte, `BINARY`), `_a12_product_ids` sur 1.
Sortie : identique sur tous ces points. **Concorde.**

**Cas 2 — liens produits (directs, inverses, casse, sérialisé).**
Déroulé attendu : `_a12_product_id` → 2 contenus liés (ids[0], ids[1]) ; le couple ids[2]→ids[0] (article→article, aucun produit) est **exclu** ; `_A12_product_id` → 1 ; `_a12_article_id` (porté par le produit, sens inverse) → 1 contenu éditorial ; `_a12_product_ids` (tableau sérialisé) → 0 lien, `non_scalar_rows` 1.
Sortie : exactement cela. **Concorde.** Bien vu : le lien article→article n'est pas compté comme lien produit, et le sérialisé n'est pas interprété.

**Cas limites vérifiés sur la sortie.**
- Pièces jointes : 2 PDF (51 o cumulés : 23 + 28), 1 PNG, 1 WebP ; `pdf_count` 2 ; `orphan_count` **2** (un PDF orphelin + le placeholder WebP natif Woo, parent nul). Cohérent avec l'oracle : quatre médias, deux parents nuls, un seul PDF orphelin. Honnête : aucun média supprimé pour « arrondir » le total.
- Taxonomie `a12_rubrique` : `term_count` 23 ; `content_count` 4 contenus distincts ; `top_terms` = 20 entrées ; Rubrique 01 → 3, Rubrique 02 → 2, puis 0. **Concorde.**
- Type/taxonomie dynamiques : `a12_dynamic` présent, `a12_empty` à 0, `a12_theme` attribué au thème. `registry-gap.json` vide dans les deux magasins (registre exhaustif). Appels non exécutés exclus.

L'oracle de `seed.php` est bâti avec les vraies API WordPress/Woo (`get_posts`, `get_objects_in_term`, `WC_VERSION`, `OrderUtil`), indépendamment du SQL de `Inventory.php`. Le banc compare donc deux voies distinctes : c'est un vrai contrôle de la règle, pas une répétition du code.

## 3. Tests

- **Suite autorisée (T01)** : rejouée, PASS (ligne REJEU ci-dessus). Ne couvre pas A-12 ; prouve la non-régression des quatre bibliothèques existantes.
- **Suite dédiée A-12** (non rejouable avec la commande autorisée) : reçus committés tous verts — `unit.json` 7/7, `result.json` 118/118, `runner.json` 7/7, `style.json` 6/6 (PHPCS PSR-12 exit 0), `verification.json` 41/41 → `NATIVE_VERIFIE`, exit 0. Classique **et** HPOS prouvés (`storage` correct dans les deux).
- **Couverture des cas limites** : états multiples, casse, sérialisé, orphelin, média absent, type vide, type dynamique, déclarants par origine, refus d'audit absent/invalide/mauvais stockage, sorties existantes/web/dépôt refusées. Large, pas seulement le cas nominal.
- **Les tests vérifient-ils la règle ?** Oui, oracle indépendant (§2).

Réserve de vérification : les reçus verts sont ceux d'Hermès. Mon apport indépendant est le déroulé manuel, qui concorde. Le seul rejeu que je puisse relancer (T01) ne rejoue pas A-12.

## 4. Sécurité et données

- **Lecture seule prouvée** : `classic-db-before.json` == `classic-db-after.json` et `hpos-*` idem (SHA-256 identiques). `readonly-probe` : serveur en READ ONLY, `UPDATE` direct refusé (1792), COMMIT/changement de transaction refusés, HTTP/mail/cron bloqués avant extensions, écritures fichier refusées par Landlock (ABI 7 observée). `native_guards` = tentatives bloquées, pas des envois.
- **SELECT uniquement** : `Inventory::select()` rejette tout SQL ne commençant pas par `SELECT ` ; requêtes paramétrées via `wpdb::prepare` ; clés méta passées en `?` lié.
- **Confidentialité** : aucun titre, texte, valeur de champ, auteur ni contact dans la sortie. `Audit::identifier()` masque tout nom hors `[A-Za-z0-9_./-]{1,160}` ou ressemblant à un secret. Noms de termes : seuls textes libres permis (rubriques), masqués si motif de secret/caractère de contrôle. Scan de la sortie committée : aucun canari privé (`*_PRIVATE_CANARY`), aucun nom de média. Les chemins d'upload ne sortent pas.
- **Pas de secret, pas de donnée réelle** : fixtures fictives, `@example`-style, aucun site/compte/API. Garde `A12_CONFINED`, confinement obligatoire, `wp-config.php` jamais exécuté, refus symlink/traversée/disposition non standard.
- **Paywall** : hors périmètre de ce lot (outil hors ligne, aucune réponse à un visiteur).

## 5. Doctrine

- **Standard d'abord** : registre pris sur les objets natifs `get_post_types()`/`get_taxonomies()` après `wp_loaded` (pas d'analyse statique) ; réutilise A-11 (`Runtime`, `ReadOnlyDb`) et le parseur A-02 **sans les modifier** (`protected_sources_unchanged` au vert). Le SQL direct est justifié : lecture avant/autour du bootstrap, sous connexion figée.
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\`, préfixe `imagine_`/`a12_`, `README.md` présent, PHPCS PSR-12 exit 0. Conforme.
- **Rejouable, idempotent** : sortie refusée si elle existe déjà ; aucun écrit en base.

## 6. Études

Sans objet (lot de code). Les sources officielles sont dans `sources-officielles.json`.

---

## Verdict : **Conforme**, sous réserve de vérification.

Le code fait ce que demande le brief, respecte la lecture seule et la confidentialité, et mon déroulé manuel concorde avec la sortie. Rien de bloquant. Rappel de doctrine : ce verdict n'est pas un GO.

**Points classés**

- **Important — vérification.** La commande autorisée (`rejouer.ps1`) ne rejoue pas A-12 : elle ne prouve que la non-régression des quatre bibliothèques existantes. La seule preuve automatisée propre à A-12 est la suite dédiée Docker/Landlock/MariaDB + extensions sous licence, non rejouable ici. La clôture du lot repose donc sur des reçus produits par Hermès, non indépendamment reproduits. À traiter en fusion : décider si un recoupement indépendant est exigé avant clôture.
- **Mineur — reconnaisseur de liens large.** Le motif de clés capte aussi des clés internes WooCommerce (ex. `_product_version`, vu dans la sortie avec 0 lien, `non_scalar_rows` 2). Conforme à « sans interprétation / une clé à zéro n'est pas une preuve » et auto-documenté, mais le README dit « clés contenant product… » alors que le motif exige en réalité `product/produit/article/numero/issue` comme jeton délimité (option `_id`/`_ids`) ; les pluriels suffixés en `s` (`related_products`) ne sont pas captés. Écart de formulation, pas de comportement.
- **Mineur — à confirmer.** Première/dernière date limitées aux contenus actuellement `publish` : un type entièrement en brouillon ressort `null`. Interprétation défendable et signalée. À confirmer que c'est bien la sémantique voulue pour un audit de migration (plutôt que l'amplitude de tous les contenus stockés).

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

1. **Reconnaisseur de liens** : *défaut* — garder le comportement actuel (conservateur, sans interprétation) et aligner le README sur le motif réel (jeton délimité, pas « contenant »). Rien à changer au code.
2. **Dates publish-seulement** : *défaut* — garder la sémantique actuelle, déjà documentée. Si Ced veut l'amplitude de tous les contenus stockés, ce serait une évolution, pas une correction.

## Pour Imagine

Aucune question métier ouverte dans ce lot : il décrit, il ne décide d'aucun rattachement.

---

*`relectures/A-12/codex.md` existe mais n'a pas été ouvert. Fusion non réalisée, conformément à la consigne.*
