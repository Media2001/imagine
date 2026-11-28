# Relecture C-30 — Page d'offre de bienvenue et code suivi

Relecteur : Claude, indépendant. Lot : C-30. Brief : `briefs/C-30-offre-de-bienvenue-et-code-suivi.md`.
Cahier des charges : §3.7, §3.14, §4.2. Production : `production/C-30/`, code dans `wp/plugins/imagine-site/CodesSuivis*.php`.

Ce verdict n'est pas un GO (doctrine §6). La fusion n'est pas faite : `codex.md` existe mais n'a pas été ouvert.

## Rejeu de la suite PHP

Commande autorisée, sans argument, conteneur jetable sans réseau, dépôt en lecture seule :
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

> REJEU : 1219 tests, 36748 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

Le test scellé propre au lot a bien tourné : `CodesSuivisC30Test` (2 tests, 9 assertions, 0 échec). Isolation confirmée dans la sortie (`network=none`, `rootfs=ro`, montage `:ro`, `cap-drop=ALL`).

## 1. Conformité

Le lot fait ce que demande le brief, sans ajouter d'avantage financier. Points vérifiés :

- **« Le standard d'abord », cinq lignes** : `README.md:17-21` décrivent l'attribution native (Sourcebuster `sbjs_*`, `OrderAttributionController`, session d'attribution 30 min, métadonnées d'origine) et pourquoi elle n'est pas réutilisée pour un code imprimé. Conforme.
- **Page « Bienvenue » publique** avec lien « S'abonner » : shortcode `imagine_bienvenue` → `Navigation::abonnementUrl()`, texte laissé vide (`CodesSuivis.php:18-19`). Sans code ou code inconnu, la page rend sans erreur (`template_redirect`, `CodesSuivis.php:20-28`). Conforme.
- **Liste de codes = réglage journalisé** : `CodesSuivisAdmin.php`, Settings API + capacité `manage_options` + journal C10 (`added_option`/`updated_option`). Liste vide valide (aucun code retenu). Conforme.
- **Code retenu seulement s'il est dans la liste** : `CodesSuivisRegles::retenir()` vérifie `isset($liste[$code])`. Une valeur inconnue n'est ni rangée, ni affichée, ni journalisée telle quelle (ni dans la page, ni dans la session, ni dans l'admin). Conforme.
- **Suivi par la session Woo, rangé une fois sur la commande payée** : session `WC()->session` (`retenir`), candidat au checkout, scellé à l'état payé sous verrou SQL, immuable (`CodesSuivis.php:52-105`). Ce qui est posé dans le navigateur et sa durée sont déclarés et **vérifiables** (voir §2).
- **Nombres par code à côté de C-27, sans identité** : `CodesSuivisAdmin::nombres()`. Conforme.
- **Export / effacement C-21** : `CodesSuivisConfidentialite` (candidat + conversion). Conforme.
- **Règles** : aucun prix ni coupon touché (le code ne passe jamais par le total) ; source C-27 du compte inchangée (`Acquisition::SOURCE` non écrite) ; aucun traceur ni appel sortant ; commande C-16 (`created_via=imagine-c16`) sans code ; rien vers Odoo ni newsletter. Conforme.

**Interprétations signalées par Hermès** (A-VOIR.md, README.md:25) : périmètre limité au checkout classique ; candidat provisoire pour paiement asynchrone. Elles sont écrites, donc recevables au sens de la doctrine §1 — voir le point important ci-dessous.

## 2. Exactitude métier (déroulé à la main)

Cas 1 — **code de la liste → la commande le porte.** `?code=fictif-affiche` validé par `retenir`, posé en session ; au checkout `candidat()` revalide contre la liste et pose `_imagine_code_suivi_candidat` ; au paiement `payer()` transfère vers `_imagine_code_suivi`, pose le sceau, supprime le candidat, relit pour confirmer. Résultat attendu, cohérent avec le code.

Cas 2 — **code inconnu / sans code → rien.** `retenir('NON_LISTE_INTERDIT')` renvoie `null`, la session n'est pas touchée ; sans session valide, `candidat()` sort. La commande ne porte ni candidat ni méta. Conforme (brief + preuve `commande_inconnue_aucune_meta`).

Cas 3 — **code changé en cours de session : lequel gagne ?** Le **dernier code connu** gagne : `retenir` écrase la session à chaque code valide ; un inconnu n'écrase pas. Prouvé (`dernier_valide_gagne`, `inconnu_ne_remplace_pas`). Conforme au brief.

Cas limites examinés :
- **Immuabilité après paiement** : le sceau `_imagine_code_suivi_scelle` bloque tout second transfert, même si la liste ou la session change ensuite (`payee`/`paye_immuable`). Correct.
- **Bornes de période** : `compter()` compare en UTC avec `>= $du` et `<= $au`, bornes incluses ; date de paiement prise de `get_date_paid()->getTimestamp()` puis `gmdate` → bien en UTC. Une date de clôture égale compte. Dates impossibles refusées (`2026-02-30` → `WP_Error`, parse strict `!Y-m-d`).
- **Évènement rejoué** : `payer()` est idempotent (verrou `GET_LOCK` par commande + sceau). Rejouer le paiement ne recrée rien.
- **Durée du cookie** : vérifiée contre l'empreinte de la version installée dans `production/C-30/standard2-V2.json` : `is_user_logged_in() ? WEEK_IN_SECONDS : 2 * DAY_IN_SECONDS`. La claim « 2 jours invité / 7 jours connecté » du README est **exacte** et sourcée. Pas de nouveau cookie propre au lot ; seul le cookie natif `wp_woocommerce_session_*` (HTTPOnly) est posé.

Aucun écart métier constaté.

## 3. Tests

Ce qui tourne dans le conteneur scellé et rejouable : uniquement `CodesSuivisC30Test` — la validation pure (`CodesSuivisRegles::liste/retenir`) et une mutation témoin (contrôle « code inconnu non rangé »). Elle passe.

**Point important — couverture scellée partielle.** Toute la logique branchée sur WooCommerce — session (`retenir`), candidat, scellé/verrou/immuabilité (`payer`), comptage (`compter`), export et effacement — n'a **aucun test déterministe rejouable**. Elle n'est exercée que par les scripts vivants (`wp/tests/demo/c30-runtime.php`, lancés par `production/C-30/verifier.py --live`), qui exigent un site démarré et ne font pas partie de la suite scellée. C'est une asymétrie avec le standard du projet : les lots voisins ont un test d'adaptateur scellé qui couvre ces chemins (ex. `tests/CodesSuivisRegles`… vs `AcquisitionAdapterTest` pour C-27, qui couvre export/effacement/comptage sur bouchons Woo). Doctrine §4 « les tests d'abord » et grille §3. À mes yeux : **important**, pas bloquant (les preuves vivantes existent, le brief demande une preuve « proportionnée »).

Qualité d'un test (mineur) : `prix_identique` (`c30-runtime.php:49`) pose les deux totaux à `12.34` à la main ; l'égalité est quasi tautologique. Le contrôle utile est `get_coupon_codes() === []`. À renforcer en comparant un total réellement calculé par Woo avec/sans code.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle** : codes `fictif-*`, e-mails fixtures. Conforme.
- **Entrées** : `$_GET['code']` validé contre la liste fermée avant tout rangement ; jamais réfléchi dans la page. `du`/`au` sortis en `esc_attr`, validés en `compter` (parse strict). Codes/libellés affichés en `esc_html`/`esc_textarea`.
- **Droits / nonce** : `reglages()` → `manage_options` + nonce Settings API ; `nombres()` → `TableauBordAdmin::autorise()`, lecture seule en GET (pas d'état modifié). `candidat`/`payer` sont des hooks serveur.
- **Requêtes préparées** : `GET_LOCK`/`RELEASE_LOCK` via `$wpdb->prepare`. Comptages de journal via SQL constant sans entrée externe.
- **Paywall** : hors périmètre (aucun texte réservé). Aucune voie de fuite du code brut vers un visiteur.

RAS de sécurité.

## 5. Doctrine

- **Standard d'abord** : pas de réimplémentation ; attribution native documentée et volontairement non réutilisée ; session = `WC_Session_Handler` natif, pas de cookie maison. Conforme.
- **Logique métier hors WordPress** : `CodesSuivisRegles` est pur et testé ; `CodesSuivis` est la couche Woo. Conforme à l'intention, sous réserve du §3 (la couche Woo reste non testée en scellé).
- **Conventions §5** : `declare(strict_types=1)`, espace `Imagine\Site`, préfixe `imagine_`/`_imagine_`, textes traduits. Conforme. README à jour avec la section du lot.
- **Efficacité (mineur)** : `compter()` charge toutes les commandes `processing/completed` et filtre les dates en PHP, sans borne `date_paid` dans la requête → coût en O(toutes les commandes payées). Acceptable à l'échelle d'Imagine ; à surveiller.

## 6. Études

Sans objet (lot avec code). La seule affirmation d'étude (attribution native) cite la documentation officielle WooCommerce (`README.md:498`, order-attribution-tracking).

## Verdict

**À corriger** — rien de bloquant ; le code est conforme au brief et la suite scellée passe, mais la preuve déterministe est incomplète.

- **Important**
  1. La logique Woo (candidat / scellé / verrou / immuabilité / comptage / export / effacement) n'a aucun test scellé rejouable ; elle ne tient que par les scripts vivants `c30-runtime.php` + `verifier.py --live`. Ajouter un test d'adaptateur scellé sur bouchons Woo, à l'image de `AcquisitionAdapterTest`.
  2. Périmètre limité au checkout classique (`created_via=checkout`). Un panier passé par le checkout Blocks / Store API (`store-api`) ne reçoit jamais de code, candidat comme scellé. Déclaré par Hermès, mais à trancher (voir décisions techniques).

- **Mineur**
  3. `compter()` : filtrage des dates en PHP plutôt que par `date_paid` en requête — efficacité.
  4. Test `prix_identique` quasi tautologique (totaux fixés à la main) ; renforcer par un total calculé par Woo.
  5. `compter`/l'affichage comptent par code stocké via `instantane()` (validation structurelle), pas par appartenance à la liste **actuelle** : un code retiré de la liste réapparaît dans les nombres pour les commandes passées. Interprétation raisonnable (attribution historique) mais non écrite — à documenter.
  6. La page « bienvenue » n'existe que par le seed de démonstration (`wp/outils/demo/c30-seed.py`), pas par un script de bascule. Conforme à « démo uniquement », mais le chemin de création en production reste à préciser (contenu Imagine).

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

- **Checkout Blocks / Store API** (point important 2). *Défaut prudent proposé* : garder le périmètre checkout classique **et** raccorder aussi `candidat`/`payer` au chemin Store API (`woocommerce_store_api_checkout_order_processed`, ou accepter `created_via` ∈ {`checkout`,`store-api`}), pour que l'attribution ne dépende pas du type de tunnel retenu côté thème. À défaut d'extension, écrire un test qui prouve qu'un code n'est jamais perdu sur le tunnel réellement utilisé par le site.
- **Test scellé de la couche Woo** (point important 1). *Défaut proposé* : ajouter `CodesSuivisAdapterTest` (bouchons Woo) couvrant session/candidat/scellé/immuabilité/comptage/export/effacement, pour que le rejeu prouve la règle sans site vivant.

### Pour Imagine

Aucune question métier ouverte dans ce lot : l'offre de bienvenue n'offre rien ici (décision d'Imagine, lot séparé), et la liste de codes est déjà un réglage par défaut vide. Rien à arbitrer côté métier.

### À arbitrer par Ced (visuel / réel)

Aucun point visuel ni touchant au réel à ce stade (démo uniquement, aucun avantage financier, aucun appel sortant). Le rendu de la page « Bienvenue » viendra du texte d'Imagine.
