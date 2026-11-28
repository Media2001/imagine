# Relecture C-31 — Adresses email jetables refusées à l'inscription (Claude, relecteur indépendant)

Brief : `briefs/C-31-adresses-jetables-a-l-inscription.md`. Cahier des charges : §3.9 (« Les adresses email jetables sont refusées à l'inscription »).
Périmètre relu : `wp/plugins/imagine-site/DomainesRefuses.php`, `DomainesRefusesRegles.php`, `DomainesRefusesReglages.php`, `tests/DomainesRefusesC31Test.php`, `imagine-site.php` (208-213), `README.md` (18-28), `wp/tests/demo/c31-runtime.php`, `production/C-31/`.
Ce verdict n'est pas un GO (doctrine §6).

## Rejeu de la suite PHP (commande autorisée, sans argument)

Commande : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
Conteneur jetable, sans réseau, dépôt en lecture seule. Dernière ligne du rejeu retenu :

```
REJEU : 1229 tests, 36926 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
OUTILS : 23 outils, 852 contrôles, 0 échecs ; hors rejeu : aucun
PAQUETS : 13 vérifiés, 0 échecs ; hors rejeu : aucun
```

Les quatre bibliothèques passent : `OK` pour imagine-connecteur (37), imagine-non-regression (152), imagine-site (784), imagine-pilotage (256). Le test unitaire C-31 `DomainesRefusesC31Test` est dans imagine-site et il est vert.

Note infrastructure (sans rapport avec le code C-31) : les deux premiers lancements ont fini en `T01 ERREUR : Inspection du conteneur impossible.` → `REJEU … 1 erreurs — FAIL`, alors que les quatre suites PHPUnit affichaient déjà `OK`. L'échec se produit après l'exécution, dans `Get-T01Inspect` (`rejouer.ps1:40`, inspection Docker du conteneur arrêté). Le troisième lancement passe proprement. C'est un aléa du harness T-01 partagé (Docker/WSL), pas un échec de test ; je n'ai pas le droit d'y toucher. Je le signale pour que Ced sache que la commande peut rendre un FAIL trompeur par intermittence.

## 1. Conformité

Conforme au brief, ni moins ni plus.

- **Standard d'abord** (`README.md:20`, `DomainesRefuses.php:14-16`). Un seul validateur pur branché sur les frontières natives : `registration_errors` (WP `register_new_user`), `woocommerce_registration_errors` (Woo `wc_create_new_customer`), `woocommerce_save_account_details_errors` (changement d'email Mon compte). Jamais de filtre global `wp_insert_user`, donc administration et C-16 épargnées. C'est bien « un refus posé une seule fois pour tous » : `wc_create_new_customer` est la fabrique commune au formulaire Mon compte, au checkout classique (`WC_Checkout::process_customer`) et au checkout par blocs (Store API `process_customer`). Vérifié sur la source officielle (voir §2).
- **Liste en réglage, journalisée, un domaine par ligne** (`DomainesRefusesReglages.php:16-20, 51-60`). Écran « Réglages → Adresses à l'inscription ». Trois domaines fictifs en `example.org` sur la démo (A-VOIR). **Liste vide → rien n'est refusé** (`DomainesRefuses.php:21`, `DomainesRefusesRegles.php:27-31`).
- **Comparaison domaine exact, sans casse** (`DomainesRefusesRegles.php:16, 30`). Sous-domaine non hérité ; choix le plus simple, signalé (`README.md:24`, A-VOIR). Interprétation IDN/punycode signalée (saisie ASCII, pas de conversion).
- **Refus à l'inscription seulement** ; compte existant intact ; changement d'email Mon compte soumis à la même règle, seulement si l'adresse diffère de l'existante (`DomainesRefuses.php:40-47`).
- **Message neutre** qui ne dit pas « jetable » et propose une autre adresse (`DomainesRefuses.php:27`).
- **Aucune liste téléchargée, aucun service tiers, aucun appel sortant** ; adresse refusée rangée nulle part ; aucun style, aucun email (vérifié par lecture, confirmé A-VOIR). Les interprétations (sous-domaine, IDN, liste vide, validation atomique) sont toutes écrites dans le README et l'A-VOIR : aucune interprétation muette.

## 2. Exactitude métier (déroulé à la main)

Cas du cahier des charges / brief, déroulés sur le code :

1. **Domaine listé, chaque point d'entrée → refusé, aucun compte.** `register_new_user` et `wc_create_new_customer` appliquent leur filtre *avant* `wp_insert_user` ; la `WP_Error` empêche l'insertion ; `process_customer` relance la `WP_Error` en exception et bloque le checkout. Correct.
2. **Autre domaine → passe.** `refuse()` renvoie `false`, aucune erreur ajoutée. Correct.
3. **Casse différente → refusé.** `refuse()` abaisse la casse du domaine de l'email (`DomainesRefusesRegles.php:30`) et `liste()` abaisse celle des domaines stockés (`:16`). Correct. Test unitaire `testDomainesExactsSansCasseNiHeritage`.
4. **Liste vide → tout passe.** `in_array(x, [], true) === false`. Correct.
5. **Compte existant sur domaine ajouté ensuite → intact.** Les filtres ne tournent qu'à l'inscription / au changement ; aucun balayage des comptes. Correct.
6. **Rien de l'adresse refusée en base ni au journal.** L'email refusé n'est jamais inséré ni journalisé ; le journal ne trace que la valeur du réglage (liste de domaines), déclenché par la sauvegarde admin (`DomainesRefusesReglages.php:32-49`), jamais par une adresse de lecteur. Correct.
7. **Mutation témoin « aucun compte créé ».** Retrait du filtre Woo → un compte est réellement créé → le contrôle d'absence échoue (`c31-runtime.php:52-56`). Le canari est vivant.
8. **Sous-domaine `sub.jetable-fictif.example.org`** non refusé par héritage (`testDomainesExactsSansCasseNiHeritage`, ligne 17). Conforme au choix annoncé.

Vérification « standard d'abord » contre la source officielle WooCommerce (trunk), car la preuve `standard-V2.json` documente les *hooks* mais pas l'*ordre des arguments* :
- `wc_create_new_customer` : `apply_filters( 'woocommerce_registration_errors', $errors, $username, $email )` — le 3ᵉ argument est bien **l'email**, pas le mot de passe. La signature `inscription(WP_Error, string $username, string $email)` est donc juste. (Point sensible : si le 3ᵉ argument avait été le mot de passe, toute la voie Woo aurait laissé passer les jetables en silence. Ce n'est pas le cas.)
- Store API (checkout par blocs) `process_customer` appelle `wc_create_new_customer(...)` (route Store API, ~l.1095) → même filtre. La voie blocs est donc couverte par le même hook.

Aucun écart métier constaté.

## 3. Tests

- Les tests passent : rejeu `PASS` ci-dessus.
- **Couverture rejouable partielle.** La suite hors-ligne (`DomainesRefusesC31Test`) ne couvre que `DomainesRefusesRegles` (fonctions pures : `liste`, `refuse`). Le câblage WordPress/WooCommerce — `DomainesRefuses::inscription` (garde admin/AJAX, `:36`), `::compte` (`:40-47`), et le journal/restauration de `DomainesRefusesReglages` — n'est éprouvé *que* par `c31-runtime.php`, qui exige un WP+Woo+base vivant et **n'est pas rejoué** par `rejouer.ps1`. Conséquence : la justesse de l'ordre des arguments (que j'ai dû vérifier à la main contre la source Woo) et la logique de garde reposent sur un test non rejouable. Contraire à l'esprit « rejouable » de la doctrine (§4). Le dépôt a déjà le patron `ContactWPStubs.php` pour stuber `WP_Error`/`get_userdata` : `inscription()` et `compte()` sont stubables hors-ligne.
- Les tests unitaires vérifient la règle (comparaison exacte, casse, héritage, entrées invalides `testConfigurationInvalideNonReparee`), pas seulement le code.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : domaines fictifs en `example.org`, emails de test en `example.org`. Conforme.
- Écran de réglages : capacité `manage_options` (`DomainesRefusesReglages.php:17, 53`), nonce via `settings_fields` (`:55`), sorties échappées `esc_html__` / `esc_textarea` (`:54-57`), `show_in_rest => false` (`:14`). Correct.
- Aucune requête SQL sur mesure dans le code du lot (le `$wpdb->prepare` + `esc_like` est dans le test, pas en production).
- Pas de paywall concerné par ce lot.

## 5. Doctrine

- **Standard d'abord** : respecté, hooks natifs, sources citées (`README.md:21`).
- **§5 conventions** : `declare(strict_types=1)`, `namespace Imagine\Site`, préfixe `imagine_` (option `imagine_domaines_refuses`, codes d'erreur `imagine_*`), textes FR via `__()`. PHP 8.2 (`str_contains`, `mixed`). Conforme.
- Aucune modification d'extension tierce : uniquement des hooks. Conforme.
- Section README présente (`README.md:18-28`).

## Verdict

**Conforme.** Le lot fait ce que demande le brief, le standard est respecté, le rejeu est vert, aucun écart métier.

Points classés :
- **Bloquant** : aucun.
- **Important** : (I-1) le câblage WP/Woo n'est pas couvert par un test *rejouable* ; sa justesse (ordre des arguments du filtre, garde admin/AJAX, condition de changement d'email) dépend du seul test live `c31-runtime.php`.
- **Mineur** :
  - (M-1) Validation atomique : une seule ligne invalide fait rejeter toute la liste et conserver l'ancienne (`DomainesRefusesReglages.php:26-29`, `DomainesRefusesRegles.php:12-21`). Défendable et documenté, mais peut surprendre à la saisie.
  - (M-2) Domaine IDN en Unicode rejeté par le validateur (ASCII/punycode seulement) ; documenté, sans action requise.
  - (M-3) Style : plusieurs instructions par ligne dans `c31-runtime.php` (lisibilité du test).

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

- **I-1 — ajouter un test unitaire rejouable du câblage.** Défaut proposé : écrire, avec le patron `ContactWPStubs`, un test hors-ligne de `DomainesRefuses::inscription` (cas garde admin/AJAX, domaine listé, domaine libre, liste vide) et de `::compte` (email inchangé accepté, email changé vers un domaine listé refusé). Objectif : prouver hors-ligne l'ordre des arguments et la logique de garde, sans dépendre du test live.
- **M-1 — validation atomique.** Défaut proposé : conserver le comportement (atomique + message d'erreur conservant l'ancienne liste), déjà documenté.

## Pour Imagine (réglage métier)

- **Origine de la liste de domaines.** Déjà parqué par le brief (« D'où elle viendra est une question rangée pour Imagine »). Défaut prudent en place : liste vide → rien n'est refusé, jusqu'à ce qu'Imagine fournisse la liste. Aucune action bloquante.

## Pour Ced (visuel / touchant au réel)

- **Écran « Réglages → Adresses à l'inscription »** : validation visuelle demandée par l'A-VOIR (rendu propre de l'écran). Défaut proposé : conforme au système de design existant, à confirmer d'un coup d'œil.
- **Message public de refus** : « Cette adresse ne peut pas être utilisée pour créer ou modifier votre compte. Merci d'utiliser une autre adresse email. » Conforme au brief (ne dit pas « jetable », propose une autre adresse). À valider sur le ton.

---

`relectures/C-31/codex.md` existe mais n'a pas été ouvert, conformément à la consigne. Fusion non faite (demandée plus tard).
