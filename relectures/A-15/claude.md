# Relecture A-15 — Inventaire des emails que le site envoie

Relecteur : Claude, indépendant. Date : 26/11/2026.
Brief : `briefs/A-15-inventaire-des-emails.md`. Cahier des charges : §3.8.
Production relue : `wp/outils/bascule/a15/`, `wp/tests/a15/`, `wp/tests/a02-audit/README.md`, `production/A-15/`.

Ligne de rejeu (suite PHP, commande autorisée sans argument) :

> REJEU : 1088 tests, 34410 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

Image T01 : `sha256:0326cc20dbf5defb9ea86d972ad952edde52043843af5413128092c8dbe48b9a`. Conteneur jetable, réseau `none`, dépôt monté en lecture seule.

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus. Il ajoute un script en lecture seule qui projette le registre `WC()->mailer()->get_emails()` réellement chargé, et rien d'autre : aucune décision sur les emails à garder, aucun envoi.

- Une ligne par email avec identifiant, intitulé, extension déclarante, actif/non, destinataire par nature (client/administration), objet et contenu en oui/non, gabarit surchargé (nom de fichier) : `Inventory::shape()` et `collect()`, `wp/outils/bascule/a15/Inventory.php:49-58` et `:197-206`. Conforme au brief.
- Extensions d'envoi présentes/actives avec nom et version, sans réglage : `transports()`, `Inventory.php:105-160`. Le champ `runtime_mail_hook` est une observation (callback mail effectivement chargé), pas un réglage de fournisseur.
- Résumé lisible : `summary.active_by_extension` et `overridden_template_files`, `Inventory.php:215`.
- Aucune adresse, clé, objet ou corps ne sort : seuls des drapeaux et le nom du gabarit. `safeLabel()` masque un intitulé contenant adresse/URL/balise, `Inventory.php:10-14`.
- Réemploi d'A-12 (lanceur confiné, `confine.py:18-26`) et d'A-11 (chemin READ ONLY, `Runtime::boot`, `Inventory.php:164`), comme le brief l'exige (« comme A-12 l'a fait pour les contenus »).
- Limite des services extérieurs dite en une phrase dans le mode d'emploi : `a15/README.md:17` et `a02-audit/README.md:68`.

Interprétations signalées par Hermès (notes.md) et jugées prudentes : registre `WC_Emails` natif uniquement, pas d'historique d'envoi inventé ; pas de rendu de gabarit ; éditeur bloc expérimental **refusé** (`A15_BLOCK_EDITOR_UNSUPPORTED`) au lieu d'un faux « non personnalisé ». Aucune interprétation non signalée relevée.

## 2. Exactitude métier — déroulé à la main

Deux stockages (classic et HPOS), banc A-02 fictif. Cas du brief (section « Preuve ») déroulés sur `production/A-15/preuves/final/` :

| Cas attendu | Résultat du code | Verdict |
|---|---|---|
| Un email désactivé | `customer_on_hold_order` : `enabled=false` | OK |
| Un gabarit surchargé | `customer_on_hold_order` : `template_overrides=[…/a02-child/woocommerce/emails/customer-on-hold-order.php]`, résumé `overridden_template_files=1` | OK |
| Destinataire interne personnalisé avec adresse canari | `new_order` : `recipient_customised=true`, `recipient_nature=administration`, **sans adresse** | OK |
| Objet personnalisé (canari) | `new_order`/`customer_on_hold_order` : `subject_customised=true`, **sans le texte** | OK |
| Contenu de plan Memberships personnalisé | `WC_Memberships_User_Membership_Activated_Email` : `content_customised=true` (via `get_email_content` par plan, `Inventory.php:190-196`) | OK |
| Transports actif/inactif avec versions | `A15 SMTP fictif 1.2.3` (actif) et `A15 SMTP inactif fictif 4.5.6` (inactif) ; formateur MIME `WC_Email::handle_multipart` non confondu avec un transport (`Inventory.php:122-127`) | OK |
| Comptes exacts | 43 emails ; actifs : woocommerce 12, memberships 1, subscriptions 16 (29 au total) | OK |

Contre-épreuve indépendante : l'oracle naïf `wp/tests/a15/oracle.php`, écrit autrement (attribution par chemin de plugin, comptage direct), donne **les mêmes 43 emails et 29 actifs** sur classic et HPOS. Les deux chemins concordent.

Cas limites couverts par `wp/tests/a15/unit.php` et vérifiés dans `unit.json` (8/8 PASS) : objet/heading vides pris pour un repli, pas une personnalisation (`explicit_default_not_custom`) ; réglages absents = non personnalisé (`absent_settings_not_custom`) ; intitulé contenant une adresse masqué (`address_in_title_masked`) ; éditeur bloc refusé (`block_editor_not_misreported_as_unmodified`) ; valeurs privées absentes de la sortie (`private_values_absent`).

## 3. Tests

- **Suite PHP rejouée** (commande autorisée, sans argument) : PASS, ligne reportée en tête. Elle prouve la **non-régression générale** du dépôt.
- **Réserve de couverture (important, non bloquant)** : cette suite (T01/PHPUnit) **n'exécute pas** les tests propres à A-15. Le banc natif A-15 (`unit.php`, `inside.py`, gardes du runner) tourne uniquement via `python wp/tests/a15/run.py`, qui exige Docker **et** les extensions commerciales sous licence (`/home/ced/staging-wp/plugins/`). Je ne pouvais pas le rejouer avec la seule commande autorisée. J'ai donc vérifié A-15 **en lisant le paquet livré**, pas en le ré-exécutant : `result.json` = 76 checks PASS, `exit_code=0`, `no_real_site=true` ; `unit.json` = 8 PASS. À reporter à Ced : la preuve A-15 repose ici sur l'artefact commité, pas sur un rejeu indépendant de ma part.
- Les tests vérifient la règle, pas le code : canaris seedés distincts (`A15_SUBJECT_PRIVATE_CANARY`, `a15-recipient-canary@example.org`, `A15_PLAN_BODY_PRIVATE_CANARY`) et contrôle de leur **absence** dans toute la sortie.
- Cas limites présents : désactivation, surcharge de thème enfant, destinataire interne, personnalisation de plan, transport actif/inactif, rejeu identique, refus transactionnel même avec root.

## 4. Sécurité et données

- **Aucune fuite.** Recherche sur tout le paquet (`CANARY`, `a15-secret`, `a15-recipient`, `@example.org`, textes privés) : les seules occurrences sont des **noms de checks**, jamais une valeur. Les canaris seedés sont absents de `emails.json`, `emails.md` et de l'ensemble des preuves.
- **Aucun envoi.** `seed.php` pose `pre_wp_mail => __return_false` et le banc place un transport canari qui échoue s'il est atteint ; `result.json` : `…cli_and_actual_mail_sql_file_http_cron_guards` PASS (exit 0, stderr vide). `inventorier-emails` n'appelle jamais `trigger`/`get_content`/rendu.
- **Lecture seule prouvée.** Empreintes base identiques avant/après (classic `911bc088…`, HPOS `28da5a35…`), fichiers identiques, et transaction READ ONLY tenue **même avec le compte root** (`transaction_blocks_even_privileged_root` PASS). Moteurs non-InnoDB refusés (`Inventory.php:170-172`).
- **Échappements et gardes.** Identifiants/slugs/gabarits filtrés par expressions régulières strictes avant usage (`Inventory.php:46`, `:68`, `:85`, `:95`) ; sortie disjointe du site et du dépôt, jamais écrasée, droits 0700/0600 (`Command.php:28-81`). Confinement obligatoire (`A15_CONFINED`, `mail`/`exec` désactivés) sinon refus, `Command.php:52-54`.
- **Aucun secret, aucune donnée réelle** dans les livrables ni les tests ; `no_real_site=true`, `real_go=false`.

## 5. Doctrine

- **Standard d'abord** : le lot ne refait rien que WooCommerce fasse déjà ; il se contente de lire le registre natif et `wc_locate_template`. Conforme.
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\`, PHP 8.2, PSR-12 (`result.json` : `a15_lint:*` et `style/` PASS). Préfixe et README présents. Conforme.
- **Rejouable / idempotent** : sortie refusée si elle existe déjà ; rejeu classic/HPOS donnant un résultat identique (`replay_identical` PASS). Conforme.
- **Un seul paquet de preuves** (brief) : `production/A-15/preuves/final`, essais hors dépôt (notes.md). Conforme.

## Décisions techniques, défaut proposé

1. **Transport déclaré par un thème.** `transports()` n'énumère que plugins et mu-plugins ; un thème qui enregistrerait un hook mail (`phpmailer_init`/`pre_wp_mail`/`wp_mail`) serait repéré comme propriétaire (`owner()` renvoie `theme:…`) mais **jamais listé** comme transport. Le brief dit « extensions d'envoi », donc cas marginal. *Défaut proposé : conserver le comportement actuel (thèmes non listés comme transports).* Hermès applique, Claude arbitre après coup.

## Pour Imagine

Aucune question métier n'est ouverte par ce lot : outil de diagnostic en lecture seule, qui ne décide d'aucun email. Rien à trancher côté Imagine.

## Verdict

**Conforme.**

- Bloquant : aucun.
- Important : la preuve A-15 n'a pas pu être **ré-exécutée** avec la seule commande autorisée (elle exige Docker + extensions sous licence) ; elle est vérifiée par lecture du paquet commité. À confirmer par un rejeu de `wp/tests/a15/run.py` côté Ced si l'on veut une preuve indépendante.
- Mineur : transport déclaré par un thème non listé (ci-dessus).

Ce verdict n'est pas un GO (§3/§6 de la doctrine). `codex.md` n'a pas été ouvert ; aucune fusion n'est faite à ce stade.
