# Relecture Claude — C-14 (L'achat d'un numéro ouvre ce numéro)

Relecteur indépendant. Brief `briefs/C-14-achat-au-numero.md`, cahier des charges §3.7 et §3.9. Je n'ai pas lu `codex.md` ; pas de fusion à ce stade. Un verdict de relecture n'est jamais un GO.

## 1. Conformité

- **Produit → numéro.** `AchatsNumeros::champ()` ajoute un champ « Numéro à l'unité » sur le produit **simple** uniquement (`wp/plugins/imagine-site/AchatsNumeros.php:90-104`, `wrapper_class` `show_if_simple`). Provisoire, un seul numéro. Conforme au brief et à §3.9.
- **Commande payée → droit sur le seul numéro.** `AchatNumero::droit()` exige `etat ∈ {processing, completed}`, `payee === true`, une date `acquis` valide, `remboursement === false`, `numero > 0` et `instantane === numero` (`AchatNumero.php:14-27`). Le droit `{type:'achat', numero, acquis_le}` est perpétuel : le moteur n'y pose aucune fin (`imagine-pilotage/src/Acces/Moteur.php:151-159`). Articles **et** PDF : `achat()` ne distingue pas le type. Conforme à §3.9 « articles et PDF de ce numéro, sans limite de durée ».
- **Autre numéro fermé.** `achat()` renvoie `AutreNumero` si `numero` ne concorde pas (`Moteur.php:153`). Conforme à « l'achat n'ouvre pas les numéros antérieurs ».
- **États non payés / remboursement.** Non payés exclus par le double verrou statut + `is_paid()`. Remboursement détecté par un objet `shop_order_refund` sur la commande (`AchatsNumeros.php:71-72`) ; un remboursement, même partiel, ferme la commande. Conforme au brief.
- **Lecture par l'adaptateur C-08, moteur C-06 inchangé.** `Paywall::rights()` appelle `AchatsNumeros::droits()` et passe le contrat au moteur (`Paywall.php:161`). Le moteur n'est pas modifié ; le droit `achat` y préexistait (`Moteur.php:91,151,178-182`). Conforme.
- **Profil V-NUM dans le script C-09.** « V-NUM » n'existe pas au catalogue ; la production le mappe sur `P-NUMERO` via un alias explicite (`wp/outils/demo/c09-profils.json:27`, `order_only`, `motif:numero_achete`) et un raccord `c14-profil.php` branché depuis `c09-seed.php:232-234`. Interprétation **signalée** (RAPPORT.md, A-VOIR.md). Acceptable : le brief est servi, le compte/login existant est conservé.
- **Achat invité.** Le brief demande de dire ce que le cahier prévoit. §3.7 : l'achat papier peut se faire sans compte, la création de compte **est proposée après l'achat** et ouvre le numérique, « règle à confirmer par Imagine (chapitre 7) ». La production l'énonce et **ferme par défaut** (pas de rapprochement par email, parcours de revendication non livré) — A-VOIR.md et RAPPORT.md. Exigence du brief respectée. Voir question « Pour Imagine ».

Aucune invention non signalée repérée. Les interprétations (V-NUM→P-NUMERO, invité fermé, remboursement partiel) sont écrites dans les rapports de production.

## 2. Exactitude métier (deux cas déroulés à la main)

- **Cas « acheteur de T1 regarde un article de T1 »** (A-VOIR §2). Commande processing, `is_paid()`=vrai, `date_paid` présente, ligne figée `instantane`=#11, produit mappé #11, pas de remboursement. `AchatNumero::droit` → `{achat, '11', acquis_le}`. Moteur : contenu réservé, `numero` concorde, `instant ≥ acquis_le` → `NumeroAchete`, bloc `Aucun`. **Accès complet.** Attendu = §3.9. ✔
- **Cas « le même acheteur regarde T2 »** (A-VOIR §4). Pour T2, `achat.numero`('11') ≠ contenu('18') → `AutreNumero` (priorité 24) > `SansDroit` (0) → décision fermée, bloc `Abonnement`. **Extrait + bloc abonnement, PDF refusé.** Attendu = « l'achat n'ouvre pas les autres numéros ». ✔
- **Cas limite « remboursement partiel ».** Commande restée `processing`, un `shop_order_refund` créé → `refunded`=vrai (`AchatsNumeros.php:71`) → `remboursement !== false` → `droit()` renvoie `null`. Tous les droits de **cette** commande tombent ; une autre commande valide du même numéro reste indépendante (boucle par commande). Cohérent avec l'application littérale annoncée. ✔ (voir « Pour Imagine »)
- **Cas limite « réaffectation du produit ».** Si l'admin change le champ numéro du produit, `numero()` renvoie le nouveau numéro mais `instantane` garde l'ancien → `instantane !== numero` → `null`. L'achat passé **n'est pas déplacé** et **est fermé**. Voir « Décisions techniques ».
- **Cas limite « acquis au seuil ».** `instant < acquis_le` → `AchatPasCommence` ; égalité → ouvert (`Moteur.php:156`, testé `DroitsTest.php:21-22`). ✔

## 3. Tests

- **Rejeu de la suite PHP, commande autorisée** (conteneur jetable, sans réseau, dépôt en lecture seule) :

  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

  **REJEU : 927 tests, 33680 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS**
  (imagine-connecteur 37, imagine-non-regression 115, imagine-pilotage 775.)

- **Qualité des tests.** `DroitsTest::testAchatNumeroEstPerpetuelMaisExactArticlesEtPdf` balaie type × numéro × date et vérifie le comportement, pas le code (`DroitsTest.php:17-38`). Le test combinatoire 2^11 (`:56-94`) valide la priorité et l'ordre. `c14-unit.php` couvre payée/completed, 8 statuts fermés, invité, réaffectation, contrat exact. Ce ne sont pas des tautologies.
- **Couverture des cas du brief.** payée, non payée, remboursée (total + partiel), autre numéro, PDF, nonce REST, réaffectation, instantané : présents dans `wp/tests/demo/c14-runtime.php` et `c14-http.py` (grep des libellés).
- **Limite d'exécution signalée.** Les suites natives WP (`c14.py`, 536) et HTTP (`c14-http.py`) exigent un staging en service (site + base). Mes droits (doctrine §3) interdisent tout accès à un site ou à une base : **je ne les ai pas rejouées**. Je reprends leurs chiffres des reçus (`COMMANDES.md`, `resultats.json`, `regressions.json`) **sans vérification indépendante**. Seul le rejeu PHP ci-dessus est de première main.

## 4. Sécurité et données

- **Droits/nonce.** `enregistrer()` vérifie `current_user_can('edit_post', …)` avant d'écrire la méta (`AchatsNumeros.php:109`) ; nonce/capacité Woo natifs en amont. `identifiant()` n'accepte qu'un entier positif strict (`:16-21`, `wp_unslash`). Pas d'injection.
- **Cohérence propriétaire.** `droits()` relit `customer_id` et lève si la commande ne lui appartient pas (`:60-63`). `numero()` exige `post_type=imagine_numero` et `post_status=publish` (`:33`). Défense explicite correcte.
- **PDF.** Contrôleur C-11 inchangé : chaque GET réévalue le droit, aucune URL physique (`PdfNumero.php:241`). L'achat n'ouvre pas un second circuit de téléchargement.
- **Étanchéité.** Le moteur reste la seule porte ; un non-autorisé reçoit l'extrait + bloc. Aucune voie nouvelle n'exfiltre le texte réservé.
- **Données.** Fixtures gardées : `guard()` impose `local` + site `imagine-test-demo` + `home_url` précis, bloque mail et HTTP sortant, exige zéro passerelle (`c14-profil.php:6-16`). Montant zéro, `set_date_paid` synthétique, aucune transaction (`:52-60`). Aucun secret, aucune donnée réelle. Mots de passe fictifs hors dépôt (A-VOIR).

## 5. Doctrine

- **Standard d'abord.** CRUD natif (`wc_get_orders`, items, refunds), champ produit via `woocommerce_wp_select`, pas de plan Memberships par numéro, pas de second circuit PDF. Sources officielles citées (A-VOIR §Standards). Conforme §4.
- **Logique métier hors WordPress.** `AchatNumero` est pur, testable sans WP ni base (`c14-unit.php`). `AchatsNumeros` est la couche fine Woo. Conforme.
- **Conventions §5.** `declare(strict_types=1)`, namespace `Imagine\`, préfixe `imagine_` (constantes méta), textes i18n français. Conforme.

## Verdict

**Conforme.** Le lot fait ce que demande le brief, cite §3.7/§3.9, signale ses interprétations, et le cœur de règle (pur + moteur) passe au rejeu autorisé. Verdict de relecture, pas un GO.

Points classés :

- **Bloquant :** aucun.
- **Important :** aucun de correctness. Un seul point de méthode : la vérification des suites natives/HTTP n'est pas de première main (voir §3). À confirmer au second tour par qui a accès au staging, ou à acter comme repris des reçus.
- **Mineur :**
  - `droits()` relance une requête remboursement par commande (N+1) ; sans incidence à l'échelle démo (`AchatsNumeros.php:71`).
  - Vérifier que le `README.md` du plugin décrit `AchatNumero`/`AchatsNumeros` et leurs réglages (convention §5) — non recontrôlé ici.

## Décisions techniques, défaut proposé (Hermès garde le défaut, Claude arbitre après)

1. **Réaffectation du produit révoque un achat passé.** La double concordance instantané + mapping courant ferme un achat déjà payé si l'admin change ou vide le champ numéro du produit (`AchatsNumeros.php:22`, `AchatNumero.php:22`). §3.9 dit « sans limite de durée ». *Défaut proposé : fermé* (prudent, modèle provisoire 1:1), comme implémenté. Arbitrage : un achat payé doit-il survivre à une réaffectation du produit ? Je penche pour conserver le défaut fermé tant que le modèle est provisoire.

## Pour Imagine (questions fermées, réglages)

1. **Remboursement partiel.** Un remboursement partiel d'une commande multi-lignes doit-il fermer le numéro acheté, ou seulement si la ligne de ce numéro est remboursée ? *Défaut appliqué : ferme tout achat de la commande* (prudent). Fermée : « On ferme sur tout remboursement, même partiel — oui / non ? »
2. **Achat invité et rattachement après achat (§3.7, à confirmer ch.7).** L'achat papier invité, suivi d'une création de compte, doit-il ouvrir l'accès numérique au numéro, avec rapprochement par email ? *Défaut appliqué : fermé, pas de rapprochement email, parcours de revendication non livré.* Fermée : « L'achat invité ouvre-t-il le numérique après création de compte — oui / non ? » À tracer dans `docs/ecarts.md` (règle §3.7 laissée ouverte par le cahier, dépend d'Imagine).

---
*Étapes suivantes : `relectures/C-14/codex.md` existe mais n'a pas été lu. Fusion non faite, conformément à la consigne.*
