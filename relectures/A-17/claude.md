# Relecture A-17 — Sécurité des comptes de l'administration (Claude, indépendant)

Lot : outil de diagnostic **lecture seule** des comptes d'administration, complément du script d'audit A-02, lancé par le confinement A-11/A-12.
Brief : `briefs/A-17-securite-des-comptes.md`. Cahier des charges : §4.4.
Code lu : `wp/outils/bascule/a17/` (Command.php, Inventory.php, inventorier-securite, confine.py, README.md) et `wp/tests/a17/`.
Preuves lues : `production/A-17/preuves/final/`.

> Je n'ai **pas** ouvert `relectures/A-17/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée, sans argument)

Commande exécutée : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

```
REJEU : 1093 tests, 34426 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Conteneur jetable, réseau coupé, dépôt monté en lecture seule, image T01 vérifiée. **Non-régression globale verte.**

**Réserve de transparence (pas un défaut).** Cette commande rejoue la suite PHPUnit T01 de tout le dépôt ; elle **ne sélectionne pas la suite A-17 dédiée** — le README du lot le dit lui-même (« `wp/tests/rejouer.ps1` ne sélectionne pas cette suite dédiée »). La preuve propre à A-17 (classic/HPOS natif, gardes, confidentialité) vient de son paquet natif livré `preuves/final/`, que j'ai **lu et contrôlé** (voir §3), mais que je n'ai **pas ré-exécuté** : `wp/tests/a17/run.py` exige Docker Linux + les extensions commerciales de staging, hors de la commande autorisée et de la doctrine §3. Je m'appuie donc, pour A-17, sur le déroulé manuel et sur les reçus livrés, pas sur une ré-exécution indépendante de sa suite.

## 1. Conformité

- Le lot fait ce que demande le brief, ni moins ni plus : inventaire agrégé en lecture seule, aucun compte créé/modifié/supprimé, aucune protection activée, aucune tentative de connexion. Conforme au cahier des charges §4.4 (double authentification administrateurs, limitation des tentatives) **en posture d'état des lieux**, pas d'activation.
- Sorties attendues toutes présentes : comptes par rôle de gestion (`roles[]`), agrégats (`application_password_accounts`, `two_factor_active`, `last_login`), protections sans réglage (`protections[]` : nom/version/active), oui/non de configuration (`public_registration`, `default_role`, `admin_file_editing`, `xmlrpc_authenticated_methods`, `application_passwords_available`).
- **Rattachement au cahier des charges** présent. Interprétations **signalées** dans le README (doctrine §1 respectée) : rôles de gestion par capacités natives ; 2FA/dernière connexion par adaptateur reconnu, sinon `inconnu` jamais zéro ; XML-RPC lu via le filtre `xmlrpc_enabled`, honnêtement présenté comme « pas un test HTTP » ; édition de fichiers lue sur le fichier **original** et non sur les valeurs forcées du confinement.
- Deux lignes ajoutées au mode d'emploi partagé A-02 : présentes (`wp/tests/a02-audit/README.md:71`), contrôlées isolément par `verify.py` (`own_two_readme_lines_only`). `production/A-17/PRET` présent.

## 2. Exactitude métier (déroulé à la main)

Banc : 2 administrateurs (dont le canari `A17_LOGIN_PRIVATE_CANARY`, porteur d'un mot de passe d'application et d'un 2FA fictif actif + l'admin d'installation A-02), 1 rôle sur mesure `a17_gestion` (capacité `manage_imagine`), 1 `editor`, 1 `shop_manager`. Horloge `--as-of=2026-11-26T12:00:00Z` → clôture `2025-11-26T12:00:00Z`.

**Cas 1 — comptes et mots de passe d'application.** Attendu : administrator=2, a17_gestion=1, editor=1, shop_manager=1 ; `unique_management_accounts=5` ; mots de passe d'application administrator=1. Sortie `classic-security/securite.json` et `hpos-security/securite.json` : **identiques à l'attendu**. Correct.

**Cas 2 — dernière connexion, borne des 12 mois.** Le canari a une connexion au 2025-01-01 (< clôture → `no_recent_record`), l'autre admin au 2026-11-01 (> clôture → récent, non compté), les trois autres rôles sans métadonnée (→ `unknown_accounts`). Sortie : administrator `{observe, no_recent_record:1, unknown_accounts:0}`, a17_gestion/editor/shop_manager `{observe, no_recent_record:0, unknown_accounts:1}`. **Correct.** Code `Inventory.php:98` `$last < $cutoff` (strict) : une connexion **exactement** à la clôture n'est pas « ancienne » — conforme au README.

**Cas limite — adaptateur 2FA inconnu.** Avec `A17_UNKNOWN_PROVIDER` la classe `Two_Factor_Core` disparaît → `two_factor_adapter: "inconnu"`, `two_factor_active: null` partout, **jamais zéro**. Testé (`*:unknown_2fa_not_zero`), vérifié dans `classic-unknown/` et `hpos-unknown/`. Correct.

**Cas limite — événement rejoué (idempotence/lecture seule).** Deuxième passage octet pour octet identique (`*:replay_identical`) ; empreintes de base et de fichiers identiques avant/après (`*:all_tables_scheduler_identical`, `*:files_identical`) ; sonde mu-plugin qui lève sur toute écriture/mail/HTTP/cron/login. Correct — la neutralité du diagnostic est **réellement éprouvée**, pas seulement affirmée.

**Configuration.** `public_registration:true`, `default_role:"subscriber"`, `admin_file_editing:true` (lu sur `DISALLOW_FILE_EDIT/MODS=false` du fichier original, pas sur les valeurs forcées en confinement → `*:actual_configuration_not_runtime_forced_values`), XML-RPC et mots de passe d'application `true`. Correct.

## 3. Tests

- Suite globale PHP : verte (voir ligne REJEU). Paquet natif A-17 livré : `result.json exit_code 0`, `unit.json`, `runner.json` tous verts ; PSR-12 strict `style.json` 0 erreur / 0 avertissement ; matrice Windows UTF-8 + cp1252 vertes. Contrôlés par lecture.
- Les tests vérifient bien la **règle** et pas seulement le code : comptes exacts, confidentialité (recherche d'un motif `CANARY|@|user_login|…` sur l'intégralité des sorties), gardes de chemin (`exists/site/repo/ancestor/root`), refus hors confinement, drop-in nommé sans exécution. Bon niveau d'exigence.
- **Vérification indépendante de la confidentialité** : j'ai cherché `CANARY`, `a17-fictif-`, `user_login`, `user_pass`, `@example` dans toutes les `securite.*` et les sorties d'audit du paquet → **0 occurrence**. Le canari est bien absent.

**Point important — un cas requis par le brief n'est pas testé.** Le brief exige : « combien n'ont aucune connexion… **si le site garde cette information (sinon « inconnu », jamais une estimation)** ». Ce chemin « aucun journal de connexion reconnu → `last_login_adapter:"inconnu"`, statut `inconnu`, `no_recent_record:null` » est **implémenté** (`Inventory.php:51,73-74,87,96-97`) mais **jamais exercé** : `inside.py` active toujours `wp-last-login/wp-last-login.php` (une seule occurrence), et le seul cas « inconnu » testé est celui du **2FA**, pas celui de la dernière connexion. Asymétrie : le 2FA inconnu est prouvé, la connexion inconnue ne l'est pas.
*Correction proposée* : ajouter un cas natif sans `wp-last-login` (ou journal non reconnu) et vérifier `last_login_adapter=="inconnu"`, statut `inconnu`, `no_recent_record is None`, `unknown_accounts == accounts`, pour classic **et** HPOS.

**Point mineur — borne exacte non couverte.** La grille (§2) demande explicitement les « dates égales à une date de clôture ». Le code est correct par lecture (`<` strict), mais aucun compte fixture n'a de connexion **exactement** à `2025-11-26T12:00:00Z` ; les deux dates seedées sont nettement avant/après. *Correction proposée* : seeder un compte pile à la borne et vérifier qu'il n'est pas compté `no_recent_record`.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle.** Jeux fictifs, `@example.org`, canaris. Rien de réel dans le dépôt ni dans les sorties.
- **Lecture seule réellement garantie** : bootstrap A-11 (`Runtime::boot`) refuse wp-config symlink, constantes inconnues (`A11_CONFIG_OVERRIDE_UNSUPPORTED`), drop-ins (`A11_DROPIN_UNSUPPORTED`) et liens symboliques ; confinement A-12 (réseau coupé, `disable_functions=mail,exec,…`, `A17_CONFINED=1` exigé). Invocation non confinée refusée (`A17_CONFINEMENT_REQUIRED`), prouvé par `*:unconfined_refused`.
- **Gardes de sortie** : chemin de sortie disjoint du site et du dépôt dans les deux sens, répertoire neuf, pas de symlink, 0700/0600 ; audit A-02 lié par schéma + `audit_sha256` + contrôle de cohérence du stockage (`A17_AUDIT_STORAGE_MISMATCH`).
- **Masquage défensif** des noms/versions d'extension suspects (`Inventory.php:20-24` : > 160 car., `@`, caractères de contrôle, préfixes `sk_/pk_/whsec_/xkeysib-`). Bonne précaution anti-fuite.
- Pas de paywall en jeu (outil de diagnostic, aucun contenu réservé servi). Requêtes : API natives WordPress, pas de SQL concaténé.

## 5. Doctrine

- **Standard d'abord** : s'appuie sur les API natives (`WP_Application_Passwords`, `Two_Factor_Core`, `wp_roles`, `get_option`, `wp_is_application_passwords_available`) ; aucun sur-mesure réinventant l'existant.
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\`, PSR-12 strict vert, textes en français, aucune modification d'extension tierce. Conforme.

## Décisions techniques, défaut proposé

- **Portée de `manage_` dans `management()`** (`Inventory.php:12`). Le motif capte **toute** capacité commençant par `manage_`, ce qui inclut des capacités de contenu (`manage_categories`, `manage_links`, `manage_nav_menus`) que porte un éditeur ou un rôle de contenu sur mesure — pas seulement l'administration. Un rôle sur mesure n'ayant que `manage_categories` serait compté comme rôle de gestion. Pour un **état des lieux de sécurité**, le défaut prudent est de **sur-signaler** (montrer à Ced plutôt que masquer), et l'interprétation est écrite dans le README. *Défaut proposé : garder la règle inclusive telle quelle ; Claude confirme après coup.* À confirmer seulement si l'on veut restreindre aux capacités réellement administratives.
- **`modify('-12 months')` sur un 29 février** : si `--as-of` tombe un 29 février d'année bissextile, le calcul calendaire PHP bascule au 1er mars. Marginal (`--as-of` par défaut = maintenant, et contrôlé par l'opérateur). *Défaut proposé : laisser tel quel ; documenter la convention.*

## Verdict

**À corriger** (le verdict n'est pas un GO).

- **Bloquant** : aucun.
- **Important** : cas requis par le brief non testé — chemin « dernière connexion = inconnu (aucun journal reconnu) ». Comportement correct par lecture, mais non prouvé. Ajouter le test natif (classic + HPOS) avant clôture.
- **Mineur** : (a) borne exacte des 12 mois non couverte par une fixture ; (b) portée large de `manage_` (décision technique, défaut inclusif proposé) ; (c) arithmétique calendaire au 29 février.

Le cœur du lot — lecture seule éprouvée, confidentialité éprouvée, comptes exacts classic/HPOS, confinement — est solide. Les corrections demandées sont **additives** (tests + une confirmation de décision) ; rien n'est à refaire.
