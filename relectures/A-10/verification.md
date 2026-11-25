# Vérification A-10 (2e et dernier tour) — inventaire des codes de réduction

Vérificateur : Claude. Date : 26 novembre 2026. Tour final après la fusion `corrections/A-10.md`.

Méthode : `git log`/`git diff 373229f..HEAD` (commit de la fusion) sur `wp/outils/bascule/a10`, `wp/tests/a10` et `production/A-10` ; relecture ciblée des seuls fichiers modifiés ; rejeu indépendant du vérificateur sur le paquet scellé courant. Pas de relecture complète refaite. Paquet `PRET` : **5e795d00f9d6**.

---

## 1. Instructions de `corrections/A-10.md` — état d'application

| # | Instruction | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | R1 — surfacer les codes portés sans fiche, « fiche introuvable », garder les décomptes, réglages à `null`, aucun identifiant d'abonné | **Appliquée** | `wp/outils/bascule/a10/Inventory.php:153-176` : `UNION ALL` des fiches `shop_coupon` et des noms distincts de lignes coupon portées par abonnements retenus/commandes de la fenêtre, filtrées par `NOT EXISTS` sur la fiche ; branche `ID===null` → `record_status='fiche introuvable'`, 23 réglages à `null` (`array_fill_keys`), `subscriptions` + `orders_12_months` conservés, aucun ID d'abonné projeté. |
| 2 | R1 (test) — cas coupon supprimé et renommé, encore portés, dans les deux magasins | **Appliquée** | `wp/tests/a10/seed.php:118-134` : `a10-deleted-old` (`delete(true)`), `a10-renamed-old`→`a10-renamed-new`, + `a10-order-only-old`. Vérifié `wp/tests/a10/inside.py:84-88` et `verifier.py:49-52` (`ORPHAN_UNKNOWN_FIELDS`, `ORPHAN_COUNTS`, `orphan_visible`). Les deux magasins (boucle `run_storage`). |
| 3 | R2 — oracle converti en UTC ; passage `Europe/Brussels` hiver+été ; branche legacy `expiry_date` + `zone()` fractionnaire + `A10_TIMEZONE_INVALID` | **Appliquée** | `seed.php:4` (`timezone_string=Europe/Brussels`), closure `$utc` qui clone et convertit (`seed.php:189-196`, `210-212`) ; `a10-season-winter/summer` + `a10-legacy-winter/summer` (expiry_date legacy) ; `inside.py:22-28` variantes `offset_fractional`/`offset_negative`/`offset_zero`/`timezone_invalid`/`timezone_invalid_fraction` avec dates UTC attendues et refus. |
| 4 | R3 — fixer l'horloge du banc ; égalité et ±1 s des deux côtés, commandes **et** expiration, deux magasins ; garder l'unité 29 février | **Appliquée** | `inside.py:56-58` : `SET GLOBAL init_connect='SET timestamp=…'` figé au 2026-11-25 12:00:00 UTC. Bornes commandes ±1 s sur les deux arêtes `seed.php:139-155`, bornes expiration ±1 s `seed.php:157-166` ; contrôlées `inside.py:91-96` + `verifier.py:54-58`. 29 février conservé (`unit.php` `calendar_window_clamped`, `verifier.py:72`). |
| 5 | Tester le refus `A10_DUPLICATE_COUPON_META` et `A10_META_INVALID` | **Appliquée** | `inside.py:25-26` variantes `duplicate_meta`/`invalid_meta` (exit 1, stderr = code d'erreur, base inchangée) ; `unit.php:23-31` `invalid_structured_meta_*` sur `Projection::ids`. |
| 6 | Harmoniser le montant vide : défaut proposé `null` + compléter la note | **Appliquée** (défaut `null` retenu) | Code inchangé : `amount` vide → `null` (`Inventory.php:183`, `Projection::decimal('')`), distinct de `minimum/maximum` vides → `0` (`:195`). Note étendue `Inventory.php:218` « montants vides ou invalides null » et `README.md`. Tests `unit.php:23` `empty_amount_unknown`, `inside.py:97` + oracle `seed.php:208` (coupon winter amount vide → `null`). |
| 7 | Refaire les preuves classique/HPOS + rejeu natif dans l'environnement autorisé, une fois R1 corrigé | **Appliquée** | Paquet régénéré `5e795d00f9d6` ; `production/A-10/rejeu-corrections.json` et `verification-finale.json` : `verifier.py` code 0, **204 assertions** (10 unit + 187 natives classique/HPOS + 7 runner), octets A-02 préservés, nettoyage vérifié. |

Les deux **décisions techniques** du rapport Claude sont tranchées conformément au défaut : montant vide → `null` documenté (#6) ; refus strict sur métadonnée dupliquée conservé **et** désormais prouvé (#5). Les deux questions **Pour Imagine** (commandes annulées/remboursées comptées ; 4ᵉ état `pending_cancel`) restent des réglages à défaut prudent appliqué — elles ne bloquent pas (doctrine §4).

---

## 2. Résultat des tests

- **Rejeu indépendant du vérificateur** sur le paquet `PRET` courant : `python wp/tests/a10/verifier.py production/A-10/preuves/5e795d00f9d6` → **code 0**, `unit_assertions: 10`, `native_assertions: 187`, `runner_assertions: 7` (**204**), `a02_original_bytes_preserved: true`, `cleanup_verified: true`. Reproduit à l'identique le reçu d'Hermès (`verification-finale.json`).
- **Portée de ce rejeu.** `verifier.py` revalide de bout en bout les **preuves scellées** (empreintes avant/après, oracle = getters Woo, bornes, variantes, confidentialité, rejeu idempotent) contre le `verifier.py` **mis à jour par la correction**. C'est la revérification propre de l'acceptation A-10.
- **Limite assumée (inchangée depuis le 1er tour).** Le **runner Docker natif** qui *génère* les preuves (staging + extensions commerciales) a été exécuté par Hermès, pas par moi : il est hors de mes droits (§3) et de l'environnement autorisé. Je m'appuie sur la revalidation indépendante des preuves scellées, non sur une régénération indépendante.
- **Non-régression des 4 plugins (`rejouer.ps1`).** Non relancée dans cet environnement (le validateur de commandes bloque le sous-processus Docker-dans-WSL). Sans objet pour ces corrections : le `git diff` ne touche **aucun** des quatre plugins PHPUnit ; le périmètre modifié est entièrement `wp/outils/bascule/a10` + `wp/tests/a10`. Le 1er tour avait enregistré ce suite au vert (1030 tests).

---

## 3. Régressions ou modifications non demandées

- **Aucune** dans le périmètre A-10. Le diff `373229f..HEAD` sur les fichiers A-10 correspond exactement aux sept instructions : `Inventory.php` (+25), `README.md`, `seed.php` (+101), `inside.py` (+56), `unit.php` (+9), `verifier.py` (+24), et les preuves régénérées sous `production/A-10/preuves/…`. Rien d'étranger aux corrections.
- Le compte d'inventaire attendu passe de 10 à **27 noms par magasin** (24 fiches + 3 orphelins) : changement **demandé** (R1 + jeux de bord), reflété partout (`verifier.py:49`, `inside.py:89`).
- Les listes `expired`/`never_used` gagnent `a10-boundary-expiry-before` et `a10-renamed-new` : conséquence attendue des nouvelles fixtures, et bien classées (l'orphelin sans fiche n'est **jamais** classé — `Inventory.php:200` n'opère que dans la branche fiche présente). Confidentialité reverifiée : `subscriptions` = compteurs par état, aucun identifiant d'abonné pour les orphelins.
- La fenêtre de diff contient aussi des fichiers d'**autres lots** (A-11, A-12, A-13, B-04, C-16, plugin imagine-site), produits en parallèle dans les commits de synchro. Ils sont **hors périmètre A-10**, ne touchent aucun fichier A-10, et ne relèvent pas de cette vérification.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les sept instructions de `corrections/A-10.md` sont appliquées et localisées ; les deux décisions techniques sont tranchées au défaut et prouvées ; aucun problème de fond ne subsiste. Le rejeu indépendant du vérificateur sur le paquet scellé courant est au vert (204 assertions, code 0). Aucune régression ni modification non demandée dans le périmètre A-10. Aucune question ouverte **visuelle ou touchant au réel** : les deux questions métier restent des réglages à défaut prudent (Imagine), sans effet bloquant.

Ce verdict n'est pas un GO au sens du §3 de la doctrine : il clôt le second tour de vérification de ce lot de code et ne vaut aucune autorisation d'accès au réel ni de migration.
