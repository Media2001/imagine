# Relecture A-04 — `mettre-a-jour` (Claude, indépendant)

Lot : A-04, le script de bascule. Brief : `briefs/A-04-mise-a-jour.md`.
Production relue : `wp/outils/bascule/{mettre-a-jour, mettre-a-jour.md, a04/*}`, `wp/tests/a04/*`, `production/A-04/*`.
Je n'ai pas ouvert `relectures/A-04/codex.md`. Je ne fais pas la fusion : c'est l'étape suivante.

## 0. Rejeu de la suite autorisée

Commande jouée, telle quelle, sans argument :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, réseau `none`, dépôt monté en lecture seule (`/repo/wp:ro`). Dernière ligne :

```
REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Important : cette suite est le banc PHP global **T01** (plugins `imagine-*`). Elle **ne joue pas** les tests propres à A-04, qui sont en Python et tournent dans Docker/WSL sous Linux (`wp/tests/a04/run.py`, `inside.py`). Depuis ce poste Windows en lecture seule et sans réseau, je ne peux pas rejouer moi-même cette suite Python. Pour A-04 je m'appuie donc sur : (1) le rejeu T01 ci-dessus, vert, qui atteste la non-régression des plugins dont dépend la réception A-03 ; (2) le paquet de preuves que j'ai **lu** (voir §3), pas reproduit.

## 1. Conformité

Le brief est couvert, point par point.

- Préalables et refus — `wp/outils/bascule/a04/update.py:235-271` : maintenance récente (`maintenance()` 207-211), marqueur staging vérifié (237-238), octets du MU de sécurité (239-241), drop-ins absents (242-244), sauvegarde présente/récente/intègre (`check_backup` 88-97), versions de départ exactes (265-270). Conforme au brief §1.
- Ordre justifié et hors-ligne — `update.py:16` (`ORDER`), `validate_plan:57-74` impose `core, woocommerce, woocommerce-subscriptions, woocommerce-memberships` puis le reste, archives locales à SHA-256 figé, aucune connexion compte (sorties réseau/mail coupées dans `bootstrap.php:18-23`). Conforme au brief §2 et à doctrine §4 (standard d'abord : API natives seulement).
- Migrations jusqu'au bout, fond compris — `runtime.php:34-94` draine la file `woocommerce-db-updates` par ID, liste fermée, puis `wooFinalize`. Boucle à point fixe ≤ 10 vagues côté Python (`update.py:301-312`) pour les suites natives créées tardivement (Variation Gallery). Arrêt à la première anomalie avec code et journal (`update.py:319-321`, `runtime.php:227-238`). Conforme au brief §3.
- Reprenable — état atomique lié au plan/site/`wp-config` (`update.py:180-181, 247-248`), étapes `verified` non rejouées (282), copie interrompue terminée avant re-bootstrap (279). Conforme au brief §4.
- Journal — `etat.json`, `journal.json`, `journal.txt`, `migrations.jsonl` (`update.py:249-254`, `runtime.php:16-32`) : étape, versions, durée, migrations. Conforme au brief §5.
- Ne supprime/nettoie rien, ne touche pas au thème — `overlay()` copie sans suppression (`update.py:154-171`), vérifié par `inside.py:198` (`themes_untouched_and_no_cleanup`). Conforme.
- Livrables — script, mode d'emploi (`mettre-a-jour.md`), tests, risques une page (`risques.md`), `production/A-04/PRET`, rapport (`rapport.md`). Tous présents.

Interprétations signalées (doctrine §1, « j'ai compris X ») — toutes assumées :

- La pile de départ complète du banc est **WordPress 7.0**, pas le 6.9.1 réel d'Imagine (`docs/decisions.md:24`). Le brief l'autorise s'il est dit clairement ce que ça empêche de prouver : c'est fait (`risques.md:3`, `rapport.md:14`, `COORDINATION.md:7`). Le cas 6.9.1 n'est joué que pour prouver le **refus natif** de Subscriptions 9.4.1 sous 6.9.1 (`inside.py:204-220`). Donc : migration historique premium et montée de base 6.9.1 → 7.0 sur la pile commerciale **non prouvées**, et c'est écrit.
- GO de production = attestation locale, pas une signature (`update.py:76-86`, `mettre-a-jour.md:73`). Assumé.

## 2. Exactitude métier (déroulés à la main)

J'ai déroulé quatre cas contre le code (le lot est de l'infrastructure, pas une règle de calcul ; les « cas » sont les scénarios de preuve du brief).

- **Reprise après arrêt.** `--stop-after=woocommerce` → `copying` fait, `migrating` non entamé, retour 75 (`update.py:289-297`). Au relancement : core `verified` sauté (282), woo repris avec contrôle `current in [before, after]` (269), migrations rejouées sous sémantique native. Vérifié bout à bout par `inside.py:104-146` (`controlled_interruption`, `previous_step_not_replayed`, `current_step_resumed`). Correct.
- **Callback falsifié.** Une action `woocommerce_run_update_callback` pointant `wp_delete_user` est refusée : `runtime.php:57-63` exige `wc_update_*` ou une méthode `Automattic\WooCommerce\*` dans la liste native. `inside.py:124-129` prouve le refus **et** que l'utilisateur ciblé n'est pas supprimé. Correct, et c'est un vrai test d'étanchéité, pas une répétition du code.
- **GO production.** Sans GO → `A04_PRODUCTION_GO_REQUIRED` ; GO expiré ou lié à un autre site/plan → `A04_PRODUCTION_GO_INVALID` (`update.py:76-86`, bornes 0 < expires−now ≤ 6 h). Déroulé confirmé par `test_go.py` et `inside.py:180-185`. Correct.
- **Sauvegarde hors délai.** `created_at` vieux de 21601 s → `A04_BACKUP_AGE` ; future → âge négatif → refus (`update.py:90-91`). `inside.py:86-88` et `test_safety.py:58-60` confirment. Correct.

Cas limites couverts : SHA-256 de paquet faux (`test_packages.py`), version de départ fausse / downgrade (`validate_plan:68`), drift d'une étape déjà `verified` (`update.py:270`), collision de casse et traversée d'archive (`test_safety.py:33-38`), lien symbolique de destination (45-51), `wp-config` changé entre deux reprises (`test_update.py:61-63`). Rien d'évident laissé de côté.

## 3. Tests

- Suite PHP globale rejouée par moi : **PASS** (ligne REJEU au §0).
- Suite Python A-04 : non rejouée par moi (contrainte poste, §0). Paquet de preuves **lu** : `production/A-04/preuves/9c204eb862d6/runner.json` → `exit_code 0`, 8 contrôles runner verts ; `result.json` → suite `A04-real-synthetic-classic-hpos`, `exit 0`, **70/70** contrôles, aucun échec. `verification-finale.json` concorde (32 tests Python, A-03 natif classique et HPOS code 3 + aller-retour code 0).
- Qualité des tests : réelle, pas du miroir de code. Exemples : remplacement atomique qui échoue et laisse la destination intacte (`test_update.py:43-51`), checkpoint corrompu non réinitialisé en silence (65-70), version lue depuis un fichier piégé qui lève une exception si exécuté (`test_safety.py:68-70`), SIGKILL avec enfant WP-CLI vivant qui garde le verrou hérité (`inside.py:90-102`).
- Couverture des cas limites : bonne (cf. §2). Les deux fixtures couvrent **classique et HPOS**, exigé par le brief.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Fixtures `@example.org`, GO `*SYNTHETIC-ONLY*` écrit dans le conteneur (`inside.py:182`), jamais dans le dépôt. Conforme doctrine §3.
- Extraction d'archive durcie : refus de `..`, chemins absolus, `\`, octets de contrôle, liens symboliques ; limites anti-zip-bomb (taille totale, par fichier, nombre d'entrées, refus du chiffrement) — `update.py:109-129`. `safe_path` revérifie avant chaque `os.replace` (167). Solide.
- Étanchéité runtime : mail, HTTP sortant, passerelles de paiement, runner asynchrone AS et cron coupés dans `bootstrap.php:18-37` ; `runtime.php:107-112` exige que la sonde `staging/runtime-probe.php` confirme ces coupures avant toute migration. Les clés de la sonde (`mail_blocked`, `http_blocked`, `subscriptions_staging`, `cron_disabled`, `as_async_disabled`, `as_runner_disabled`, `gateways_disabled`) correspondent exactement à celles vérifiées — cohérent.
- MU 503 persistant tant que l'opérateur ne l'enlève pas (`maintenance.php`), même après expiration du `.maintenance` natif. Le script ne lève jamais la maintenance ni ne bascule de DNS. Conforme à la prudence du brief.
- Requêtes SQL du runtime : lectures préparées sur `actionscheduler`/`options`, contrôle `last_error` (`runtime.php:166-221`). Pas d'écriture SQL brute hors API natives.

## 5. Doctrine

- Standard d'abord : aucune migration réécrite à la main ; `WC_Install`, `WC_Subscriptions_Upgrader`, cycle Memberships natifs (`runtime.php:117-162`). Toute migration inconnue, `failed` ou `in-progress`, ou toute tâche de fond non reconnue → **arrêt**, jamais de faux « terminé » (166-219). Conforme doctrine §4 et §4 idempotence.
- Logique hors WordPress : l'orchestration (plan, verrous, état, archives) est en Python pur, testable sans WP ; seule la couche migration touche WP via WP-CLI. Conforme à l'esprit du §4.
- Conventions §5 : PHP `declare(strict_types=1)`, espace `Imagine\`, préfixe `imagine_`/`IMAGINE_A04_`, textes FR. PSR-12 : 0 erreur, 1 avertissement résiduel (classe + point d'entrée dans `runtime.php`), assumé sans refonte. Pas de modification d'extension tierce : uniquement des filtres. Conforme.
- Rejouable / non-régression : réception par **verdict natif A-03 uniquement** (code 3 pour l'attendu, 0 pour l'identique), un code 2 n'est jamais requalifié (`COORDINATION.md:5`, `inside.py:168`). Conforme aux décisions du lot.

## Verdict

**Conforme**, sous réserve des limites explicitement documentées. Ce verdict n'est pas un GO (doctrine §3 et §6) : il ne vaut que pour la clôture d'un lot de code, sur fixtures fictives.

Points classés :

- **Bloquant** : aucun.
- **Important** : aucun. La seule chose à ne jamais oublier côté réel est déjà traitée comme risque n°1 : la pile commerciale complète 6.9.1 → 7.0 (et les migrations historiques premium) n'est **pas** prouvée ici ; elle devra l'être sur le staging Imagine avant tout réel.
- **Mineur** :
  1. `adapter: "bootstrap-only"` (5ᵉ étape et au-delà) **désactive de fait** le garde-fou de migration différée propre au composant : `runtime.php:169-174` met le préfixe à `(?!)` pour ces composants, donc le balayage des actions/batches/cron en attente ne matche plus rien pour eux. L'outil repose alors **entièrement** sur l'audit humain qui a déclaré le composant « sans migration différée ». C'est annoncé (`mettre-a-jour.md:46`), mais la garantie technique disparaît pour ces plugins.
  2. `journal.txt` est un en-tête suivi de lignes JSON (`update.py:252`). Le brief demande un « journal lisible ». C'est exploitable mais ce n'est pas une table humaine ; `journal.json` reste la source structurée.
  3. `validate_plan` interdit tout adaptateur qualifié au-delà des quatre premiers (`update.py:69`). Une extension à migration spécifique ne peut donc **pas** entrer dans un plan sans modifier le code — ce qui est sûr (elle serait sinon bloquée au runtime), mais le mode d'emploi laisse entendre qu'un adaptateur qualifié suffirait.

## Décisions techniques, défaut proposé

Questions techniques — Hermès applique le défaut sans attendre, j'arbitre après coup.

1. Garde-fou `bootstrap-only` (mineur 1) : faut-il, pour chaque composant `bootstrap-only`, **vérifier aussi** l'absence d'action/batch/cron en attente de façon générique (pas seulement par préfixe de nom), en plus de l'audit ? **Défaut proposé** : statu quo (audit humain + refus au moindre mécanisme reconnu), car élargir le balayage à tout préfixe risquerait de bloquer des tâches opérationnelles légitimes ; mais exiger qu'une trace d'audit nommant le composant accompagne chaque `bootstrap-only` dans le plan. Prudent.
2. Lisibilité du journal (mineur 2) : ajouter une ligne humaine par étape (« core 7.0 → 7.0.9, 12 s, 3 migrations ») dans `journal.txt` ? **Défaut proposé** : garder le format actuel ; `journal.json` suffit à la traçabilité. Changement cosmétique, non bloquant.

## Pour Imagine

Rien à trancher côté métier dans ce lot : A-04 est de l'outillage, sans règle métier ouverte.

## À arbitrer par Ced (visuel ou réel)

Rien. Aucune question visuelle. Rien ici n'autorise d'accès réel, de compte, d'achat ni de déploiement ; la branche production n'a été exercée que sur des fixtures fictives avec un GO synthétique. La preuve réelle reste à faire sur le staging Imagine vérifié, avec un GO écrit de Ced nommant la tâche (doctrine §3).

---

Fusion non faite : `relectures/A-04/codex.md` existe mais n'a pas été ouvert, conformément à la consigne. Étape suivante possible : croiser les deux rapports et écrire `corrections/A-04.md`.
