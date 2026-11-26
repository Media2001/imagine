# Relecture C-16 — Claude (indépendant)

**Lot** : C-16 — Commande pour le compte d'un client ; encodage sans email ; vente sans identité.
**Brief** : `briefs/C-16-commande-pour-un-client.md`. **Cahier des charges** : §3.13, §2.3.
**Date** : 2026-11-26. **Je n'ai pas ouvert `codex.md`. Pas de fusion à ce stade.**

## Rejeu de la suite PHP autorisée

Commande, sans argument, depuis la racine :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, réseau `none`, dépôt monté en lecture seule, nettoyage vérifié. Dernière ligne :

```
REJEU : 1062 tests, 34271 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Image : `sha256:7f75bd127fe6…`. Isolation confirmée (`network=none ; rootfs=ro ; mount=…/wp:/repo/wp:ro ; cap-drop=ALL`).

**Portée de ce que mon rejeu prouve.** T01 est vert et inclut les 6 tests `CommandeReglesTest` (validation pure). Il **ne couvre pas** les comportements de bout en bout : anti-doublon, création de compte sans email, exclusion d'envoi, idempotence, vente directe, refus de droit. Ceux-ci ne sont exercés que par `c16-http.py` et les lectures natives, **sur le site de démo**, que je ne peux ni n'ai le droit de rejouer (accès site/base/identifiants interdits au relecteur). Je m'appuie donc, pour ces cas, sur la lecture du code et sur les preuves déposées par Hermès, pas sur une exécution de ma part.

## 1. Conformité

Conforme au brief, à la lecture du code.

- **Trois écrans** : `CommandeAdmin::page()` route `étape` 1/2/3 (client → commande → confirmation). `natif.md` chiffre le parcours natif (liste + souscription + commande = 3 écrans existant) et ne construit que la saisie. Conforme §3.13 « trois écrans au plus ».
- **Un seul menu** : `add_submenu_page('imagine', …)` (`CommandeAdmin.php:46`). Conforme.
- **Commande native en attente** : `wc_create_order(status pending, created_via imagine-c16)`, souscription `wcs_create_subscription(status pending)` avec `set_requires_manual_renewal(true)` (`CommandeNative.php:131,142`). Aucun `payment_complete()`, aucune adhésion, aucun accès. Conforme « crée la commande native, en attente de paiement ».
- **Sans email** : case dédiée → adresse technique `@sans-email.imagine.invalid`, meta `imagine_sans_email=1` (`CommandeNative.php:100-105`). Marqueur unique réutilisé (`SansEmail::META`), lu par `ExtractionsNatives.php:34` (email vidé). Conforme « ne crée pas un second marqueur ».
- **Un compte par adresse** : l'email connu est résolu dès l'écran 1 (`CommandeAdmin.php:117-119`) et revérifié à la création (`CommandeNative::creerClient` → `clientExistant`). Pas de doublon ; nom/adresse de l'existant non modifiés (`CommandeNative.php:96`). Conforme.
- **Vente sans identité** : compte générique `imagine-vente-directe`, un clic (`CommandeAdmin.php:221-225`). Adresse facultative en mode direct (`CommandeRegles::commande($data, true)`). Conforme §3.13.
- **Droit dédié + jeton** : accès = `manage_options` OU (`imagine_gerer_echeances` ET `imagine_creer_compte_client`) (`CommandeAdmin.php:20`). Nonce lié à action+token (`CommandeAdmin.php:77,111`). Conforme « droit dédié (C-15 ou un voisin), jeton ».
- **Paiement hors ligne** : seulement `bacs` (virement) et `imagine_papier` (mandat papier), descripteurs, jamais `process_payment()` (`CommandeNative.php:176`). Conforme.
- **Don / pack / offert / groupé** : une seule ligne de texte « emplacements seulement » (`CommandeAdmin.php:197`). Aucun parcours inventé. Conforme « laisse des emplacements nommés ».
- **Interprétations signalées** (doctrine §1) : brouillon serveur à 1 h, aucune création avant confirmation, revalidation du catalogue, verrou par brouillon+email — toutes écrites dans `natif.md`. Correct.

## 2. Exactitude métier — cas déroulés à la main

Déroulé contre le code (je ne peux exécuter le parcours sur site).

**Cas A — abonnement par virement, compte existant.** Écran 1 `mode=existant,id` → brouillon étape 2. Écran 2 produit abonnement + adresse + `bacs` → empreinte catalogue figée, étape 3. Écran 3 `confirmer=oui` → `creer()` : ordre `pending` + souscription `pending` (renouvellement manuel), méthode `bacs`. La vue « virements à valider » retient `état ∈ {pending, on-hold}` ET `méthode=bacs` (`EcheancesRegles.php:75-76`) : la souscription-virement y apparaît. **Conforme** à la preuve attendue.

**Cas B — compte créé « sans email ».** Écran 1 `mode=nouveau, sans_email=1` → `CommandeRegles::client` force `email=''`, `sans_email=true` (ignore un email tapé par erreur — testé). `clientExistant` rend `null` (email vide) : création **différée** à la confirmation. À la confirmation : compte `@sans-email.imagine.invalid`, `imagine_sans_email=1`. Envois : `SansEmail::filtrer` refuse tout message dont un destinataire TO/CC/BCC est `.invalid` ou marqué (`SansEmail.php:23-33`) ; `ExtractionsNatives` vide l'email. Accès : aucune adhésion créée ; décision C-06 attendue `complet=false, motif=sans_droit, bloc=abonnement` (`acces-sansmail.json`). **Conforme** : n'apparaît dans aucun envoi, accès fermé tant que rien n'est payé.

**Cas C — adresse déjà connue.** Écran 1 `mode=nouveau, email=connu` : `clientExistant` trouve le compte → bascule `mode=existant,id` (`CommandeAdmin.php:117-119`). Pas de second compte, nom/adresse inchangés. **Conforme**.

**Cas D — compte sans le droit.** `autorise()` faux → POST : `refus()` (403) ; GET : `wp_die(403)` (`CommandeAdmin.php:33,174`). **Conforme** « reçoit un refus ».

**Cas limites vérifiés dans le code** : double-envoi / retour navigateur → même ID (`draft['resultat']` réutilisé, `CommandeAdmin.php:155`) ; interruption après marquage `commence` → 409 et relecture native imposée, jamais de double création aveugle ; catalogue modifié entre écran 2 et 3 → empreinte divergente → 409 ; concurrence sur même email → verrou MySQL `GET_LOCK` puis `get_user_by('email')` sous verrou. Cohérent.

## 3. Tests

- **Suite autorisée verte** (voir REJEU) : 1062/34271, 0 échec. Inclut les 6 `CommandeReglesTest`.
- **Qualité des tests purs** : `CommandeReglesTest` vérifie bien la règle et pas seulement le code (email ignoré en sans-email, normalisation, rejet tableau/email invalide, adresse obligatoire sauf direct, refus passerelle en ligne, refus adresse incomplète). Correct.
- **Lacune de couverture offline (important)** : aucun test unitaire ne couvre `CommandeNative` (création ordre/souscription, anti-doublon, verrou), ni `SansEmail::filtrer`, ni le reset. Ces comportements — dont l'exclusion d'envoi, qui est une obligation §3.13 et touche au paywall — ne sont prouvés que par `c16-http.py` sur le site. `SansEmail::filtrer` est quasi-pur (seuls `get_user_by`/`get_user_meta` à simuler) : il mériterait un test unitaire rejouable hors site, comme la règle « paywall côté serveur » de la doctrine le réclame par un test d'étanchéité.

## 4. Sécurité et données

- **Secrets / données réelles** : aucun dans le lot. Noms fictifs, adresses `@example.org` / `.invalid`. Conforme.
- **Droits** : capacité dédiée vérifiée avant menu, avant POST, et dans `page()`. `woocommerce_prevent_admin_access` relâché uniquement sur cette page, le contrôle de capacité restant en place. Correct.
- **Nonces** : `wp_nonce_field` / `wp_verify_nonce` liés à `action:token` ; brouillon lié au référent (`qui === get_current_user_id()`), jeton hors URL. Correct.
- **Échappement** : `esc_html` / `esc_attr` / `esc_url` sur toutes les sorties. `strip_tags` + rejet des octets de contrôle à l'entrée (`CommandeRegles::texte`). Correct.
- **Requêtes préparées** : `$wpdb->prepare` pour `GET_LOCK`/`RELEASE_LOCK` et le `LIKE` des transients du reset. Correct.
- **Aucun email / appel externe** : `CommandeNative::garde()` exige que le coupe-circuit `pre_wp_mail` renvoie `false`, que `pre_http_request` renvoie un `WP_Error`, et qu'aucune passerelle ne soit disponible, sinon il jette. Défense en profondeur correcte ; le lot refuse de s'exécuter hors démo locale fictive.
- **Paywall** : C-16 n'expose aucun contenu réservé ; il crée des objets `pending` sans accorder d'accès. Pas de fuite introduite.

## 5. Doctrine

- **Standard d'abord** : `natif.md` compare au parcours WooCommerce/Subscriptions (10 lignes, sources officielles citées) et ne code que la saisie manquante. Conforme §4.
- **Logique hors WordPress** : `CommandeRegles` est de la validation pure, testée sans base. Conforme.
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\Site`, préfixe `imagine_`, textes passés par `__()`, aucune extension tierce modifiée (hooks seulement), `README.md` du plugin documente C-16 (ce qu'il fait, réglages/capacités, comment lancer les tests). Conforme.
- **Rejouable / non-régression** : reset C-16 (`c16-reset.php`) ciblé, prévol complet, refus d'objet payé/modifié/étranger, idempotent. Conforme.

## Verdict

**Conforme** à la relecture (code + rejeu T01 vert), avec deux points importants et des points mineurs ci-dessous. **Ce verdict n'est pas un GO** (doctrine §6) : il ne vaut que pour la relecture de code, et plusieurs preuves de bout en bout n'ont pu être rejouées par moi (site interdit).

**Bloquant** — aucun.

**Important**
1. **Réserve C-09 non vérifiable par moi** (381/382 ; action A-PAPIER #8103 annulée le 25/11 20:38:22 UTC). C'est un état du site de démo : accès interdit au relecteur, je ne peux pas confirmer le diagnostic d'Hermès (annulation antérieure au déploiement C-16, inchangée avant/après le parcours). Je m'appuie sur ses journaux (`gates-c09-*`). Hermès l'a classé hors C-16 et signalé — correct — mais **le gate reste rouge** et `--strict-global` renvoie toujours 2. À lever avant toute clôture C-09 ou globale ; `PRET` ne vaut que « C-16 prêt à relire techniquement ».
2. **Couverture offline mince des comportements critiques.** Hors site, seul `CommandeReglesTest` tourne. Anti-doublon, compte sans email, exclusion d'envoi (`SansEmail::filtrer`), idempotence : prouvés uniquement par la recette HTTP sur site. Proposer au minimum un test unitaire de `SansEmail::filtrer` (quasi-pur) — c'est l'étanchéité d'envoi exigée par §3.13 et par la doctrine (« un test d'étanchéité le vérifie »).

**Mineur**
1. `c09-seed.php` a dérivé du sceau C-16 : `final.json` enregistre `55aeb3d1…`, l'arbre porte `7b7ad355…`. L'écart vient d'un ajout **postérieur** C-17 (`\Imagine\Demo\C17\profils(true);`, commit 60936c7, 00:58 > PRET 00:48), pas de C-16. Les 6 fichiers C-16 sont, eux, identiques au sceau (hashs relus). La mention « payload relu identique » ne vaut donc que pour le code C-16, pas pour le seed partagé.
2. `PRET`/`A-VOIR` annoncent T01 à **1040/34229** ; mon rejeu donne **1062/34271** (tests C-17/C-18 ajoutés depuis). Chiffre périmé, pas un défaut ; la suite reste verte, 0 échec.
3. C-16 pose `imagine_sans_email` sur A-SANSMAIL via le seed C-09. Réalisation défendable de l'intention du brief (« le marquage que lisent déjà C-09 et la liste d'envoi ») et signalée dans `natif.md`. Mais le brief supposait le marqueur **déjà** présent ; il ne l'était pas. Couplage C-16 → fixture C-09 à garder en tête ; la non-régression est couverte par T01 vert.
4. Exclusion des commandes à l'unité de « virements à valider » : affirmée dans `A-VOIR.md`, mais elle dépend de la logique C-15 que je n'ai pas entièrement tracée. L'**inclusion** de la souscription-par-virement, elle, est confirmée (`EcheancesRegles.php:75-76`).

## Décisions techniques, défaut proposé

- **Test d'étanchéité `SansEmail::filtrer` manquant hors site.** Défaut proposé : Hermès ajoute un test unitaire PHP (stubs `get_user_by`/`get_user_meta`) couvrant un destinataire `.invalid`, un destinataire marqué mêlé à un destinataire normal, et un CC/BCC marqué — sans attendre d'arbitrage. Claude arbitre après coup.
- **Chiffre T01 dans `PRET`/`A-VOIR` périmé.** Défaut proposé : rafraîchir le décompte (1062/34271) ou renvoyer vers le log de rejeu plutôt qu'un chiffre figé.

## Pour Imagine

Rien à trancher côté métier dans ce lot : le brief exclut don/pack/offert/groupé et interdit toute règle nouvelle ; Hermès n'en a introduit aucune. Les seuls réglages de défaut prudent (accès fermé tant que non payé, aucun envoi) suivent la doctrine.

*(Aucune question visuelle ou touchant au réel à adresser à Ced dans cette relecture, hormis la réserve C-09 déjà portée par Hermès, qui relève d'un état de démo et non d'un choix.)*
