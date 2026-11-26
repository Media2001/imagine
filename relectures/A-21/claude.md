# Relecture A-21 — Les portes du site vers l'extérieur (Claude, relecteur indépendant)

Brief : `briefs/A-21-portes-vers-l-exterieur.md`. Cahier des charges cité : §4.4, §2.5.
Sources relues : `wp/outils/bascule/a21/` (Analysis.php, Inventory.php, Command.php, inventorier-portes, confine.py, README.md) et `wp/tests/a21/`.
Dépendances relues pour la sécurité : `wp/outils/bascule/a11/Runtime.php`.
`relectures/A-21/codex.md` **non ouvert**. Fusion **non faite** (voir fin).

## Rejeu de la suite PHP

Commande autorisée, sans argument :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernière ligne :

```
REJEU : 1123 tests, 34569 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

L'outil A-21 y figure : `T01 TOOL : a21 ; 15 controls ; 0 failures ; exit=0` (les 15 assertions pures de `unit.php`). Conteneur jetable, réseau `none`, dépôt monté en lecture seule, nettoyage relu.

> Je n'ai pas rejoué la matrice Windows native (`run.py`/`matrix.py`, Docker) ni `style.py` : hors commande autorisée. Je m'appuie sur le rejeu ci-dessus, la lecture des sources et le déroulé manuel. Le candidat reporte PSR-12 strict 0/0 ; non revérifié par moi.

## 1. Conformité

Le lot fait ce que demande le brief, en lecture seule, sans rien révoquer ni appeler.

- **Clés d'interface** : comptes par droit (`read`, `write`, `read_write`), plus `unknown` prudent pour une valeur corrompue (`Analysis.php:84-88`). Correspond à l'énumération native Woo « lecture / écriture / les deux ».
- **Jamais / > 12 mois** : `never_used` et `unused_twelve_months` comptés **disjoints** (`Analysis.php:89-98`). Le brief dit « aucun accès depuis douze mois **ou** jamais » — lu ici comme deux nombres plutôt qu'un seul. Interprétation **signalée** dans `production/A-21/notes.md` et `README.md`. Plus informatif, la somme redonne le chiffre du brief → conforme.
- **Webhooks** : comptes par état (`active/paused/disabled` + `unknown`) et par sujet, destinations des **seuls actifs** en `same_domain` / `external_domain` / `unknown`, **sans jamais nommer le domaine** (`Analysis.php:52-72`). Conforme à « sans nommer ce domaine ».
- **Sujets non standard** regroupés sous `unknown` (`Analysis.php:61`) : interprétation signalée, imposée par la règle voie 1 (un identifiant de sujet libre peut porter une identité).
- **Magasin d'extensions** : oui/non sur `woocommerce_helper_data.auth.access_token` (`Analysis.php:28`).
- **Neutralisation → « inconnu »** : si la marque `imagine_staging_disabled_plugins` existe, les trois rubriques répondent `inconnu après neutralisation`, données `null`, jamais zéro (`Inventory.php:19`, `Analysis.php:18-24`). Même logique que A-17.
- **Standard d'abord** : dix lignes dans `a21/README.md` (clés → `woocommerce_api_keys`, webhooks → `wc_webhooks`, helper → `woocommerce_helper_data`), avec références officielles datées.
- **Deux lignes dans le mode d'emploi de l'audit** : `wp/tests/a02-audit/README.md:79-80`, identiques à `production/A-21/readme-ajout.txt`, ajout unique vérifié par contrat (`verify.py:readme_contract`), pas par empreinte de tout le fichier.

Rien « en moins ». Rien « en trop » de bloquant : le banc ajoute un webhook interne et un désactivé au-delà du minimum du brief, ce qui renforce la couverture sans élargir le livrable.

## 2. Exactitude métier — déroulé à la main

**Cas A — ancienneté d'une clé, seuil strict à l'anniversaire.** Banc natif : clés `read`/`last_access=null` et `read_write`/`2024-01-01 00:00:00`, fuseau `Europe/Paris`, horloge = instant courant (≈ 2026-11-26). À la main : `year-1=2025`, `month=11`, `day=min(26, 30)=26` → seuil `2025-11-26`. `null` → `never_used`. `2024-01-01 < seuil` → `unused_twelve_months`. Résultat attendu `{read:1, write:0, read_write:1, unknown:0, never_used:1, unused_twelve_months:1}`. Le code et le test `keys_exact` donnent exactement cela. **OK.**

**Cas limite — égalité au seuil.** `unit.php` : `2025-11-25 23:59:59` → ancien ; `2025-11-26 00:00:00` (= seuil) → **non** ancien. Conforme à « une date égale au seuil n'est pas depuis plus de douze mois ». **OK.**

**Cas limite — 29 février.** Horloge `2024-02-29`, accès `2023-02-28`. À la main : `day=min(29, 28)=28` → seuil `2023-02-28` = accès → non ancien (`leap_anniversary_clamped_not_march`). **OK.**

**Cas B — destination d'un webhook actif.** Site `https://shop.example.org`. Actif vers `http://SHOP.EXAMPLE.ORG.:8080/inside` : hôte en minuscules, point final retiré, schéma/port ignorés → `shop.example.org` = site → `same_domain`. Actif vers `outside.example.org` → `external_domain`. Actif vers `bad/CANARY` (pas de schéma) → `unknown`. Le domaine n'apparaît dans aucune sortie. **OK** (`active_destinations_domain_not_origin`).

**Cas C — dates invalides / futures.** `2026-02-30` (débordement → `03-02`, format ≠) et `2027-01-01` (> horloge) → `last_access_unknown` (2) ; `0000-00-00 00:00:00` → `never_used`. **OK.**

**Cas D — copie neutralisée.** Le vrai outil de neutralisation (`wp/outils/staging/lib.php`, **non modifié**) tourne sur un clone fictif : clés vidées, 4 webhooks désactivés, destinations/secrets vidés, jeton magasin effacé, marque posée. L'outil répond alors `inconnu après neutralisation` partout, jamais zéro, et la lecture laisse le clone inchangé (`neutralised_unknown_not_zero`, `neutralised_database_unchanged`). **OK.** Conforme au brief (« inconnu après neutralisation, jamais zéro, comme A-17 »).

Idempotence : empreintes de toutes les tables (ordonnanceur compris) et des fichiers identiques avant/après ; rejeu à instant figé bit-à-bit identique (`frozen_replay_identical`, `all_tables_scheduler_identical`).

## 3. Tests

- Suite PHP pure rejouée **au vert** (15 assertions a21, voir ci-dessus).
- Les attendus sont des valeurs écrites à la main, indépendantes de l'implémentation ; le banc natif utilise un **oracle SQL distinct** (`seed.php`) — un test vérifie la règle, il ne répète pas le code.
- Cas limites couverts : égalité au seuil, 29 février, fuseau du site, dates invalides/futures, zéro historique, sujet standard `product.published` préservé, destination `unknown`.
- Étanchéité « voie 1 » testée : scan anti-canari sur **toutes** les sorties et tous les artefacts, refus fermés (symlink, dropins, surcharge de config, horloge invalide, exception tirée du site → `A21_INVENTORY_FAILED`), sondes réelles de refus SQL/fichier/mail/HTTP/cron.
- `unit.php` reste pur et auto-découvrable par T-02 (dépend du seul `Analysis.php`).

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle** : fixtures manifestement fictives (`CANARY`, `@example.org`).
- **Aucune fuite de nom/chemin du site, sortie d'erreur comprise** : `Inventory.php` ne sélectionne que `permissions,last_access` / `status,topic,delivery_url` — jamais description, clé, secret, fragment, nonce, nom, compte (`Inventory.php:25-37`). Toute exception inconnue est rabattue sur un code fermé (`inventorier-portes:45`). `refusalMessage` (`a11/Runtime.php:21-31`) ne laisse sortir qu'un nom de dropin **issu d'une liste blanche de six noms WordPress standard**, jamais une chaîne tirée du site — conforme à l'autorisation du brief.
- **Lecture seule** : boot A-11 en transaction `READ ONLY`, HTTP/mail/cron sous garde, écriture refusée (prouvé par sonde). Sorties en `0700`/`0600`, création refusée si la cible existe ou est un lien.
- **Aucun appel sortant** tenté au nominal (`outbound_attempts` = 0/0/0).
- **Requêtes** : noms de tables via `$wpdb->prefix` (non issu d'une entrée externe) ; aucune valeur externe interpolée dans le SQL. Confinement exigé (`A21_CONFINEMENT_REQUIRED` hors conteneur).

## 5. Doctrine

- **Standard d'abord — point à signaler (mineur).** Pour le magasin d'extensions, l'outil **relit l'option** `woocommerce_helper_data` et teste `auth.access_token` (`Analysis.php:28`) au lieu d'appeler la méthode native `WC_Helper::is_site_connected()` que le `README.md` cite pourtant. Équivalent fonctionnel, défendable (lecture directe, aucun effet de bord possible), l'oracle du banc utilise bien la méthode native et l'outil la rejoint. À noter au titre du « standard d'abord ».
- Conventions §5 respectées : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_` (option seulement lue), textes d'interface en français, aucun code d'extension tierce modifié (hooks/SELECT), `README.md` présent.
- Rejouable, idempotent, logique métier en PHP pur hors WordPress (`Analysis.php` testable sans base) : conforme.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

1. **Deux comptes disjoints** (`never_used` / `unused_twelve_months`) plutôt qu'un compte agrégé. Défaut proposé : **garder** (plus informatif, somme = chiffre du brief).
2. **Lecture directe de l'option** pour le magasin d'extensions au lieu de `WC_Helper::is_site_connected()`. Défaut proposé : **garder** la lecture directe (évite tout effet de bord), ou, si l'on veut coller au standard, appeler la méthode native — sans incidence sur le résultat.
3. **URL à hôte littéral IP / IPv6** d'un webhook actif : non couverte par un test dédié ; classée best-effort par comparaison de chaîne, sans fuite. Défaut proposé : **garder**, ajouter un cas de test si une telle URL est plausible en production.

Aucune question **visuelle ou touchant au réel** pour Ced dans ce lot.

## Verdict

**Conforme.** (Un verdict de relecture n'est jamais un GO au sens du §3 de la doctrine.)

Points classés :
- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur** :
  1. Magasin d'extensions relu via l'option plutôt que `WC_Helper::is_site_connected()` (standard-first) — `Analysis.php:28`.
  2. Deux comptes d'inactivité disjoints vs formulation « ou » du brief — interprétation signalée, à confirmer en défaut.
  3. Pas de test pour un hôte IP/IPv6 de webhook actif.

## Suite

`relectures/A-21/codex.md` n'a pas été ouvert. **Je m'arrête après la relecture** : la fusion et `corrections/A-21.md` ne seront écrits que lorsque `codex.md` existera.
