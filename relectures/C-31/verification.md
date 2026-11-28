# Vérification C-31 (2ᵉ et dernier tour) — Adresses email jetables refusées à l'inscription

Vérificateur : Claude. Date : 28 novembre 2026. Base relue : la version d'avant corrections (commit `356b0b22`, 01:23). Fusion appliquée : `corrections/C-31.md`. Ce verdict n'est pas un GO (doctrine §6).

Méthode : `git diff 356b0b22 HEAD` sur `wp/` et les fichiers C-31, relecture des nouveaux tests, rejeu de la suite hors-ligne. Pas de relecture complète refaite.

---

## 1. Suivi des instructions de `corrections/C-31.md`

### Instruction 1 — test rejouable hors-ligne du câblage (I-1 + I1) : **Appliquée**
- Nouveaux fichiers `wp/plugins/imagine-site/tests/DomainesRefusesC31AdapterTest.php` et `DomainesRefusesC31WPStubs.php` (patron `ContactWPStubs`, monde jetable, `WP_Error`/`get_userdata`/`WP_REST_Request` stubés).
- `testRaccordArgumentsEtAbsenceDeFiltreGlobal` fige l'**ordre des arguments** : un mot de passe « listé » passé en 2ᵉ argument ne refuse pas, l'email en 3ᵉ refuse (`AdapterTest:30-32`) ; absence de `wp_insert_user`/`user_register` vérifiée (`:35-36`).
- `testInscriptionGardeAdminMaisPasAjaxPublic` : matrice garde admin/cap/AJAX, domaine libre, liste vide (`:39-53`).
- `testCompteInchangeAccepteEtChangementRefuseSansEcriture` : inchangé accepté, changé refusé, autorisé, email en base inchangé (`:55-67`).
- Objectif de l'instruction (prouver hors-ligne l'ordre des arguments et la garde sans dépendre du live) : atteint.

### Instruction 2 — preuve « Mon compte » réelle (I1) : **Appliquée**
- L'assertion vacante `do_action('woocommerce_save_account_details_errors', …)` est **retirée** de `c31-runtime.php` (diff : lignes supprimées autour de l'ancien `:37-38`).
- Remplacée par de vrais POST du formulaire natif dans `wp/outils/demo/c31-compte.py` (trois scénarios, `c31-compte.py:48-82`) : refus → `refuse_email_non_ecrit` (adresse relue inchangée) + `refuse_temoin_sauvegarde_bloquee` ; changement autorisé → `autorise_email_relu` + `autorise_billing_email_relu` ; adresse inchangée sur domaine ajouté après création → témoin sauvegardé. Compte de recette supprimé, réglages restaurés.

### Instruction 3 — preuve d'absence réelle (I2) : **Appliquée**
- Commande réelle : `WC()->checkout()->process_checkout()` avec vrai `$_POST`/nonce, et non plus `process_customer` par réflexion (`c31-runtime.php`, section checkout). Store API réelle via `rest_do_request` sur `/wc/store/v1/checkout`.
- Balayage élargi à **toutes les colonnes textuelles de toutes les tables** du préfixe (`SHOW TABLES`/`SHOW COLUMNS`), présence vérifiée pour `woocommerce_sessions`, `wc_orders`, `wc_order_addresses`, `wc_orders_meta`, `wc_customer_lookup`, etc. (`stockage_present_*`). Rejeu : 47 tables / 187 colonnes.
- **Témoin positif de détection** : adresse volontairement déposée dans options, usermeta, session et commande HPOS, puis `mutation_stockage_detectee_*` exige que le scan la trouve (`c31-runtime.php`). Le canari « filtre Woo retiré → compte créé » est conservé.
- Persistance avant refus effectivement reproduite (`billing_email` en session) puis corrigée en avançant la garde (voir §3).
- Contrôles ajoutés : `checkout_aucune_commande` / `store_aucune_commande` (compte de commandes inchangé).

### Instruction 4 — style PSR-12 (M1 + M-3) : **Appliquée**
- Blocs conditionnels sur une ligne réécrits dans `DomainesRefusesRegles.php` (`liste`) et `DomainesRefuses.php` (`inscription:38-40`, `compte`).
- Plusieurs-instructions-par-ligne séparées dans `c31-runtime.php`.
- PHPCS ciblé : exit 0, zéro erreur (`corrections-style-final-V2.log` vide).

### Instruction 5 — rejeu après corrections : **Appliquée**
- Suite PHP rejouée verte (voir §2). Recettes live native/navigateur/compte/commande rejouées par Hermès (`corrections-*-final-V2.json`).

---

## 2. Résultat des tests

Rejeu hors-ligne relancé par moi (commande autorisée, conteneur jetable, réseau coupé, dépôt en lecture seule) :

```
REJEU : 1243 tests, 37036 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
OUTILS : 23 outils, 852 contrôles, 0 échecs ; hors rejeu : aucun
PAQUETS : 13 vérifiés, 0 échecs ; hors rejeu : aucun
```

- Hausse attendue depuis la version relue (1229 → 1243 tests, 36926 → 37036 assertions) : nouvel adaptateur C-31 et lots parallèles.
- Run ciblé C-31 : `OK (9 tests, 64 assertions)` — les deux fichiers de test C-31 tournent (`corrections-cible-final-V2.log`).
- Paquet `imagine-site` complet : `OK (267 tests, 3267 assertions)`.
- **L'aléa T-01 signalé au 1ᵉʳ tour** (inspection Docker du conteneur arrêté rendant un `FAIL` trompeur) **ne s'est pas reproduit** : rejeu propre du premier coup.

Preuves live d'Hermès (hors suite rejouable, nécessitent WP+Woo+base) : native 46, inscriptions 16, Mon compte 29, commande Store API 13 — toutes PASS.

---

## 3. Régressions / modifications non demandées

- **Deux nouveaux points d'entrée ajoutés** dans `DomainesRefuses.php` : `commande` sur `woocommerce_checkout_posted_data` (priorité 1) et `commandeBlocs` sur `rest_request_before_callbacks` (priorité 1). C'est une modification de comportement au-delà d'un simple correctif de style, **mais elle est demandée** par l'instruction 3 (« si une persistance apparaît avant le refus, placer le contrôle avant cette écriture »). La persistance de `billing_email` en session avant le refus a été réellement reproduite, puis la garde avancée. Gardée correctement : n'agit que hors connexion et quand un compte est créé ; invités sans création et comptes existants non concernés. Couverte hors-ligne par `testCommande*` et `testStoreApi*` de l'adaptateur. Conforme au brief (« création pendant une commande » est un point d'entrée à refuser). **Pas une régression.**
- **Aucune régression constatée** : suite complète verte, paquet de non-régression inclus. Message public et méthode `valider` inchangés. Aucun filtre global de création de comptes ajouté (administration et C-16 toujours épargnées).
- **Hors périmètre C-31** : le `git diff` sur `wp/` depuis la base contient aussi des fichiers C-30, C-32, C-33, A-32 et l'ajout au bootstrap `imagine-site.php` (C-32/C-33). Ce sont des lots parallèles, pas des modifications de C-31. Non évalués ici.
- **Finalisation** : contrairement à l'état décrit dans `FINALISATION-V2.md` (« PRET absent »), `production/C-31/PRET` et `reception-corrections-V2.json` existent (créés à 04:57, après le rapport) : la passe de scellé a bien été exécutée par le parent. Cohérent.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions de `corrections/C-31.md` sont appliquées. Le point important I-1/I1 (câblage sans test rejouable) est levé : le câblage — ordre des arguments, garde admin/AJAX, condition de changement d'email, nouveaux points d'entrée commande et Store API — est désormais prouvé hors-ligne par `DomainesRefusesC31AdapterTest`. I2 est levé : balayage de toutes les tables textuelles avec témoin positif, parcours commande et Store API réels. Le style PSR-12 est corrigé. Le rejeu hors-ligne est vert, relancé et confirmé par moi. Aucun problème de fond restant.

Reste **uniquement la validation visuelle de Ced**, déjà prévue et non bloquante côté code :
- écran « Réglages → Adresses à l'inscription » (rendu conforme au système de design, défaut proposé : conforme) ;
- ton du message public de refus (ne dit pas « jetable », propose une autre adresse ; défaut proposé : conserver).

Rappel doctrine §6 : ce « prêt » ne vaut que pour la clôture du lot de code ; il n'est pas un GO de mise en ligne.
