# Relecture A-10 — inventaire des codes de réduction (Claude, relecteur indépendant)

Lot : A-10, voie 1, chantier A. Cahier des charges §4.3.
Périmètre relu : `wp/outils/bascule/a10/` (Command, Inventory, Projection, README), `wp/outils/bascule/inventorier-codes`, `wp/tests/a10/` (seed, unit, inside, run, verifier, readonly-probe), les deux lignes ajoutées à `wp/tests/a02-audit/README.md`, la bibliothèque A-02 réutilisée (`wp/outils/bascule/audit`), et les preuves scellées `production/A-10/preuves/eaeb5368fbca/`.

Je n'ai pas ouvert `relectures/A-10/codex.md`. Je ne fais pas la fusion.

---

## 1. Conformité

Le lot fait ce que demande le brief, sans reclassement ni suppression (brief : « ce lot ne produit que l'inventaire »). Chaque champ demandé est présent et rattaché au texte.

- **Champs demandés présents.** `Inventory.php:167-183` : type, montant + unité (`amount`/`amount_unit`), dates UTC (`date_created/modified/expires`), limites (`usage_limit`, `usage_limit_per_user`, `item_limit`), usages (`usage_count`), restrictions produits/catégories incluses et exclues par identifiant, `allowed_email_count`, récurrence (`recurring_on_renewals`). Conforme au brief §« Ce qu'on veut ».
- **Abonnés rattachés.** `Inventory.php:158-163` : porteurs comptés par état `active / on_hold / pending / pending_cancel`, distincts (COUNT DISTINCT). Le brief demande « actifs, suspendus ou en attente » (trois états). Hermès ajoute un 4ᵉ état `pending_cancel`, séparé et déclaré (`README.md:17`, limitation `Inventory.php:201`). C'est un ajout mesuré pour ne pas perdre de porteurs, pas une invention de règle — acceptable mais à confirmer côté métier (voir questions).
- **Commandes 12 mois.** `Inventory.php:164` : fenêtre `[cutoff, now]` inclusive sur la date de création UTC. Conforme au brief.
- **Expirés / jamais utilisés à part.** `Inventory.php:185-190`, listes de noms séparées, recoupement autorisé. Conforme au brief (« à part ») et au cahier.
- **Confidentialité.** Aucun nom/email/identifiant client projeté : `metadata()` (`Inventory.php:88-107`) liste blanche de clés, commentaire explicite « Never read _used_by, descriptions, authors, customers ». Les emails sont **comptés** (`Projection::emailCount`), jamais listés. Les noms de codes sont la seule exception, expressément autorisée par le brief.
- **Hors racine web, hors dépôt.** `Command.php:34-47` refuse toute sortie dans le site ou le dépôt, les sorties existantes, les liens symboliques, et exige un audit A-02 frère valide. Conforme au brief (« s'écrit hors de la racine web… ne rejoint jamais le dépôt »).
- **Classique et HPOS.** `Inventory.php:139-145`, magasin faisant autorité choisi sur l'option `woocommerce_custom_orders_table_enabled`. Vérifié dans les deux magasins (preuves classic + hpos). Conforme.
- **Aucun écrit, aucune tâche, aucun envoi.** Transaction `REPEATABLE READ` + `READ ONLY` (`Inventory.php:41-43`), garde `A10_NON_SELECT_FORBIDDEN` (`Inventory.php:65`), pas de bootstrap Woo (lecture directe du stockage). Conforme au brief et à la doctrine §4 (logique métier hors WordPress).
- **Livrables.** Script + tests + deux lignes exactes ajoutées en fin de `wp/tests/a02-audit/README.md` (vérifié : les deux lignes sont bien présentes, `readme-ajout.txt` = 2 lignes) + `production/A-10/PRET`. Complet.

**Interprétations signalées par Hermès (doctrine §1 respectée).** Les limitations (`Inventory.php:197-205`, README) déclarent : empreinte de récurrence = réglage standard et non remise future ; `payment_limit` inclut le paiement initial ; commandes = tous statuts sauf corbeille/auto-draft (donc pas des ventes nettes) ; « jamais utilisé » = compteur Woo à zéro. Ces choix sont les plus proches du texte et sont écrits — conforme.

---

## 2. Exactitude métier (déroulé à la main)

J'ai déroulé les cas du cahier/brief à la main et comparé aux preuves scellées (`classic-codes/codes.json`), identiques en HPOS.

**Cas 1 — code récurrent porté par un abonnement actif (cas phare du brief).**
`a10-recurring-fee`, type `recurring_fee`, `_wcs_number_payments=3`.
- Récurrence : `Projection::recurring('recurring_fee')` → `true`. Preuve : `recurring_on_renewals: true`. ✔
- Limite de paiements : `payment_limit_including_initial: 3`. ✔
- Porteurs : la fixture fournit active/on-hold/pending-cancel, plus un abonnement `pending` neuf ; les abonnements `cancelled` et `expired` neufs sont **exclus** des quatre états comptés. Attendu `{active:1, on_hold:1, pending:1, pending_cancel:1}`. Preuve identique. ✔
- Commandes 12 mois : 4 commandes récentes (`-1j`, `-2j`, `-3j`, `-4j`, tous statuts sauf corbeille) + 1 renouvellement réel (`-1h`) = **5**. Exclues : `-2 ans` (hors fenêtre), `+2 j` (futur, > now), corbeille. Les lignes coupon dupliquées ne doublent pas le compte (COUNT DISTINCT). Preuve : `orders_12_months: 5`. ✔
- Casse : le renouvellement et certaines commandes portent `A10-RECURRING-FEE` en majuscules ; `BINARY LOWER(...)=BINARY LOWER(?)` les rattache. ✔

**Cas 2 — code expiré ET jamais utilisé (cas limite dates + recoupement).**
`a10-expired-never-used`, expire `2000-01-01`, `usage_count=0`.
- Expiré : `expiry < now` (comparaison de chaînes ISO-8601 UTC, ordre lexical = ordre chronologique). → listé dans `expired`. ✔
- Jamais utilisé : `usage_count === 0` → listé dans `never_used`. ✔
- Présent dans les **deux** listes (recoupement autorisé) ET dans l'inventaire complet. Preuve : `expired` et `never_used` le contiennent tous deux. ✔

**Cas limite — changement d'année / année bissextile pour la fenêtre.**
`Projection::cutoff` : `cutoff(2024-02-29)` → `2023-02-28` (jour borné via `format('t')`). Couvert par l'unité `calendar_window_clamped`. Sur le run réel : `now = 2026-11-25` → fenêtre `from_utc = 2025-11-25T20:45:22Z`. ✔

**Cas limite — type inconnu / tiers.** `Projection::recurring` renvoie `null` pour tout type hors des sept standards (unité `recurrence_standard_types`), et `amount_unit = 'unknown'`. Aucune récurrence inventée. ✔

Conclusion : les comptes du rapport sont exacts sur le banc fictif ; ils correspondent à mon déroulé manuel et à l'oracle des getters Woo natifs.

---

## 3. Tests

**Suite PHP rejouée avec la commande autorisée, sans argument :**
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
Conteneur jetable, hors réseau, dépôt en lecture seule. Dernière ligne :

```
REJEU : 1030 tests, 34124 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

- **Portée exacte de ce rejeu.** `rejouer.ps1` exécute les suites PHPUnit des **quatre plugins** (`imagine-connecteur`, `imagine-non-regression`, `imagine-pilotage`, `imagine-site`) : 1030 tests, 34124 assertions, vertes. Il prouve la **non-régression** de l'existant. Il **n'exécute pas** l'acceptation propre d'A-10 : le module `wp/outils/bascule/a10/` n'est pas un plugin PHPUnit ; ses tests (`unit.php`, `inside.py`) tournent via `wp/tests/a10/run.py` dans un conteneur Docker avec les extensions commerciales de staging (`/home/ced/staging-wp/plugins`). Je n'ai **pas** rejoué ce runner natif : il est hors de la commande autorisée, exige Docker + plugins commerciaux hors dépôt, et toucherait au staging. J'ai donc vérifié l'acceptation A-10 par (a) la lecture des preuves scellées, (b) le déroulé manuel §2, (c) la relecture du code — pas par une ré-exécution indépendante.
- **Reçu Hermès.** `production/A-10/verification-finale.json` : `verifier.py` code 0, **110 assertions** (6 unitaires + 97 natives + 7 runner), empreinte base identique avant/après dans les deux magasins, octets A-02 préservés. Je reprends ce reçu sans l'avoir rejoué moi-même.
- **Qualité des tests lus.** Les natifs vérifient la **règle** (oracle = getters Woo réels, renouvellement réel `wcs_create_renewal_order`, empreinte logique de toutes les tables, piège de bootstrap, blocage d'un UPDATE root par la transaction). Ce ne sont pas de simples répétitions du code. Les cas limites couverts : expiré/jamais/recoupé, doublons de lignes coupon, commandes ancienne/future/corbeille, mauvais audit, mauvais magasin, sortie interdite, lien symbolique, config dynamique.
- **Lacunes de couverture (mineures).**
  1. `Projection::expiry` — la branche **legacy** `expiry_date` au format `Y-m-d` interprété dans le fuseau du site (`Projection.php:83-88`) et la méthode `zone()` (`Inventory.php:109-124`, fuseaux, `gmt_offset` fractionnaire, `A10_TIMEZONE_INVALID`) ne sont exercées par aucun test : la fixture n'écrit que des timestamps numériques. Proposition : ajouter un coupon fixture à `expiry_date` legacy en fuseau non-UTC, ou un test unitaire de `expiry()`/`zone()`.
  2. `A10_DUPLICATE_COUPON_META` (`Inventory.php:100`) et `A10_META_INVALID` (unserialize) ne sont pas exercés ; le refus strict est codé mais non prouvé sur banc.

---

## 4. Sécurité et données

- **Lecture seule réellement contrainte.** `SET SESSION TRANSACTION READ ONLY` + transaction ouverte (`Inventory.php:41-43`), `MULTI_STATEMENTS=false`, `EMULATE_PREPARES=false`, garde `select()` sur `SELECT ` préfixe. La sonde `readonly-probe.php` prouve qu'un UPDATE échoue même avec l'utilisateur `root` (errno 1792). Solide, conforme à la doctrine §4.
- **Aucune donnée réelle, aucun secret.** Fixtures `@example.org` et canaris `PRIVATE_CANARY` ; le test `privacy` vérifie l'absence de `@`, `customer_id`, `billing_`, etc. dans les deux sorties. Rapports réels interdits de dépôt (garde `A10_OUTPUT_UNSAFE`).
- **Requêtes préparées / injection.** Le nom de code est un paramètre lié ; les noms de tables passent par `table()` (liste blanche + backticks, préfixe validé) ; les noms de colonnes viennent d'un ternaire fixe HPOS/classique, pas d'entrée utilisateur. Pas de concaténation d'entrée.
- **Sorties échappées.** `codes.md` encode le JSON avec `JSON_HEX_TAG|HEX_AMP|HEX_APOS|HEX_QUOT` (`Command.php:58`) ; `Audit::identifier` masque types/statuts hors motif et filtre les motifs de clés (`sk_`, `whsec_`, hex 40). Modes 0700/0600 posés et prouvés.
- **Config.** `wp-config.php` refusé si lien symbolique, non canonique, trop gros (`Inventory.php:18`) ; parseur littéral A-02 réutilisé sans modification (une config dynamique lève `A02_CONFIG_NON_LITERAL`, testé).
- **Paywall** : sans objet (lot d'outil, pas de contenu réservé).

Aucun problème de sécurité relevé.

---

## 5. Doctrine

- **Standard d'abord.** Les quatre sources officielles WooCommerce/Subscriptions sont tracées par SHA-256 (`sources-officielles.json`) et justifient qu'aucun moteur de règles sur-mesure n'est écrit — seule la projection en lecture l'est. Conforme §4.1.
- **Logique hors WordPress.** Règles en PHP pur testable (`Projection`), couche fine `Inventory` sur PDO, pas de bootstrap Woo. Conforme.
- **Conventions §5.** `declare(strict_types=1)`, espace de noms `Imagine\CouponInventory`, PHP 8.2 (`match`/propriétés typées), aucun code tiers modifié, README présent. Préfixe `imagine_` sans objet (pas d'option/hook WordPress créé). Conforme.
- **Rejouable / idempotent.** Deux passages (`classic-codes` vs `classic-repeat`) produisent des `codes` identiques (`repeat_exact_business_fields`). Empreinte base identique avant/après. Conforme.
- **Pas de Git, pas de staging, pas de réel.** Le runner crée/détruit son propre conteneur étiqueté, sans réseau ni montage ; aucun accès réel. Conforme §3.

---

## Verdict

**Conforme** — sous réserves de vérification ci-dessous. Ce verdict n'est pas un GO (doctrine §6).

Points classés :

- **Bloquant** : aucun.
- **Important** :
  - *(Vérification, pas défaut de code)* L'acceptation propre d'A-10 (110 assertions natives) n'a **pas** été ré-exécutée de façon indépendante : la commande autorisée `rejouer.ps1` couvre la non-régression des 4 plugins (1030 tests, PASS), pas le runner Docker d'A-10. Mon assurance sur A-10 repose sur les preuves scellées + déroulé manuel + relecture. À signaler à Ced avant toute clôture.
- **Mineur** :
  - Lacune de couverture : branche legacy `expiry_date` + `zone()` non testées (§3, point 1).
  - Lacune de couverture : refus `A10_DUPLICATE_COUPON_META` / `A10_META_INVALID` non exercés (§3, point 2).
  - Incohérence mineure de projection : `amount` vide → `null` alors que `minimum/maximum_amount` vides → `"0"` (`Inventory.php:169` vs `180`). Sans impact sur le banc (tous les coupons ont un montant) ; à harmoniser ou documenter.

---

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

1. **Coupon sans montant (`coupon_amount` vide).** `amount` renverrait `null`. Défaut proposé : conserver `null` (= inconnu), cohérent avec « montants invalides null », mais aligner la note de limitation pour couvrir aussi le cas « vide ». Arbitrage Claude en fusion.
2. **Refus strict sur métadonnée dupliquée.** Sur une vraie base, une clé coupon dupliquée (plugin tiers) ferait échouer tout l'inventaire. Défaut proposé : garder le refus strict (sécurité d'exactitude) tant que l'audit réel reste interdit sans GO ; ajouter un test prouvant le refus. Arbitrage Claude.

---

## Pour Imagine (règle métier → réglage)

1. **Que compte « nombre de commandes des douze derniers mois » ?** Le code compte toutes les commandes portant le code sauf corbeille/auto-draft (donc annulées et remboursées incluses). Question fermée : *faut-il compter aussi les commandes annulées et remboursées comme « utilisations » du code dans l'inventaire ?* Défaut prudent proposé : **oui** (vue la plus large, déjà déclarée comme « pas des ventes nettes »). À confirmer par Imagine ; devient un réglage si réponse différente.
2. **4ᵉ état de porteur `pending_cancel`.** Le brief demande actifs / suspendus / en attente ; Hermès ajoute `pending_cancel` séparé. Question fermée : *garder `pending_cancel` comme colonne distincte, ou le replier dans « en attente » ?* Défaut prudent proposé : **garder distinct** (ne perd aucun porteur, information strictement additionnelle).

---

*Étape suivante : `relectures/A-10/codex.md` existe mais n'a pas été ouvert. La fusion (`corrections/A-10.md`) n'est pas faite, conformément à la consigne.*
