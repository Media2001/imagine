# Relecture A-03 — non-régression de l'existant (Claude, indépendant)

Lot : A-03. Brief : `briefs/A-03-non-regression.md`. Doctrine + `doctrine/grille-relecture.md`.
Production relue : `wp/outils/bascule/non-regression`, `wp/outils/bascule/comparer`, `wp/outils/bascule/a03/{Policy,Report,Site}.php`, `wp/outils/bascule/non-regression.md`, tests `wp/tests/a03-non-regression/`, `production/A-03/`.
Je n'ai pas lu `codex.md`. Pas de fusion à ce stade.

## 0. Rejeu de la suite autorisée

Commande (exacte, sans argument) :
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :
`REJEU : 812 tests, 33434 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Conteneur jetable, réseau `none`, dépôt monté en lecture seule, nettoyage vérifié.

**Réserve de portée (important).** Ce banc (T01) ne découvre que les paquets PHPUnit sous `wp/plugins`, `wp/mu-plugins`, `wp/themes` (`wp/tests/t01/discovery.php:40`). Le code A-03 vit sous `wp/outils/bascule/` : il **n'est pas exécuté** par cette commande. Le PASS ci-dessus prouve `imagine-pilotage`, pas A-03. Les tests propres d'A-03 passent par `wp/tests/a03-non-regression/run.py` (Docker/WSL + ZIP de plugins sous licence sur le NUC), hors de la commande autorisée ; je ne les ai donc **pas rejoués moi-même**. Je m'appuie sur les artefacts livrés par Hermès (voir §3).

## 1. Conformité

Le brief est couvert, point par point.

- **Accès** : matrice `uid:post` via `wc_memberships_user_can`, échantillon = un représentant par combinaison d'états adhésion/abonnement, plus le visiteur anonyme (uid 0). `Site.php:226-239`. IDs restreints vérifiés réellement restreints (`A03_CONTENT_NOT_RESTRICTED`, `Site.php:232`). Conforme à « ce que Memberships répond … on compare la matrice ».
- **Abonnements** : nombre par état / moyen de paiement / périodicité (`subscription_counts`), dates de prochain paiement (`subscriptions[].next_payment_utc`), actions en attente par type et par jour (`actions`, `action_days`). `Site.php:178-193, 240-255`. Conforme.
- **Commandes** : totaux par mois (12 mois glissants finissant à `as_of_month`) × état × devise, nombre et montant en mineur. `Site.php:274-321`. Conforme ; montants séparés par devise, bon choix pour éviter d'additionner des devises différentes.
- **Pages clés** : les sept clés attendues imposées (`Site.php:325`), code HTTP (premier + final), marqueur présent, erreur PHP. Conforme.
- **Renouvellement de test** : opt-in `--renewal-test`, triple garde (demandé + staging vérifié + runtime sûr, `Policy.php:35-38`), écrit en transaction annulée, nettoie, désactivé par défaut (`renewal.enabled=false`). Conforme à « seule partie qui écrit ; désactivée par défaut ».
- **Aucune donnée personnelle** : le rapport ne contient qu'IDs numériques, états (slugs), nombres, dates. Valeurs jamais ré-émises par `comparer` (`Report.php:41`). Réutilise `Audit::identifier` qui masque secrets/chemins (`audit:859`). Vérifié : scan des JSON produits → aucune occurrence de canaris, `@example.org`, noms fictifs. Conforme.
- **`comparer`** : classe attendu / à regarder / anormal, codes de sortie 0/3/2 et 1 (refus). Conforme.

Interprétations signalées par Hermès et acceptables : échantillon = un représentant par combinaison d'états (couvre chaque état présent) ; `pending` autorisé par Memberships recopié tel quel (réponse native, pas une décision — voir §4).

Pas de dépassement de périmètre : lecture seule par défaut, aucun accès réel, aucun secret ajouté.

## 2. Exactitude métier (déroulé à la main)

**Cas 1 — deux photos identiques → aucune différence.** `Report::compare($a,$a)` : `$a === $b` coupe à la racine, `changes=[]`, `anormal=0` → `comparer` renvoie 0. `generated_at_utc` est de toute façon exclu (`Report.php:26`). Conforme à la preuve ; artefact `*-identical.json` : `"changes": []`.

**Cas 2 — altération provoquée → détectée anormale.** Oracle du test :
- `UPDATE … post_status='wcm-expired'` sur l'adhésion active → `memberships.13.status` passe active→expired ; racine `memberships` ∉ {versions, pages, renewal} ⇒ **anormal**. Cascade attendue sur `samples.*`, `access.2:10` (droit perdu) ⇒ anormal.
- `DELETE … actionscheduler_actions` sur l'action fixture (id 28) → `actions.28` (tableau→null) et `action_days.a03_fixture_action:2027-01-14` disparaissent ; racine `actions`/`action_days` ⇒ **anormal**.
`comparer` renvoie 2. Dérivé à la main, cohérent avec `classic-anomalies.json`/`hpos-anomalies.json` (`anormal: 12`, dont `access.*` et `actions.*`).

**Cas limite — mouvement de date / santé HTTP.** Déroulé du test `page_health_and_date_movement_are_anomalous` : `next_payment` 2027-01-01→2027-01-02 ⇒ anormal ; marqueur perdu ⇒ anormal ; HTTP sain 200→302 ⇒ **à regarder** (non remonté en anormal car 302 ∈ [200,400[). Conforme à « HTTP sain modifié = à regarder ».

**Cas limite — changement d'année / fenêtre de 12 mois.** `orders()` calcule `-11 months` depuis `as_of_month` (`Site.php:279-284`) ; la commande fixture de 2025-11 (hors fenêtre 2025-12…2026-11) est correctement exclue ; total count 3, montant 4244 mineur. Dérivé à la main = artefact `classic/non-regression.json`.

Classification `Report.php` revue ligne à ligne : versions→attendu ; pages/renewal→à regarder sauf dégradation (marqueur≠true, php_error≠false, statut hors [200,400[)→anormal ; tout le reste→anormal. Conforme au brief.

## 3. Tests

- **Rejeu autorisé** : vert (voir §0) mais hors périmètre A-03 (réserve de portée).
- **Artefacts A-03 livrés** (`production/A-03/preuve-finale/`) : `runner.json` exit 0 (isolation, lint, unit, classic+hpos, nettoyage, sources inchangées) ; `result.json` exit 0 = **45 contrôles** classique + HPOS tous `ok:true` ; `unit.json` = **4 tests purs** verts ; `lint.json` = **7 fichiers** OK. Je les ai relus, non régénérés.
- **Couverture des cas limites** : bonne. Les tests réels couvrent lecture seule DB+fichiers (empreinte avant/après), refus drop-in avant bootstrap, refus compte non-SELECT, refus staging non vérifié, refus runtime non sûr, rollback après panne provoquée, lignes métier restaurées, réseau `none`, aucun écouteur. Ce ne sont pas de simples répétitions du code : ils vérifient la règle (ex. `renewal_business_rows_restored` compare des empreintes de tables, `two_mutations_detected` passe par un oracle SQL indépendant du sujet).
- **Limite de ma vérification** : les tests A-03 n'étant pas dans le banc autorisé, mon indépendance d'exécution se limite à la lecture d'artefacts produits par Hermès. Voir point important n°1.

## 4. Sécurité et données

- **Aucun secret / aucune donnée réelle** committé : fixtures `@example.org`, noms manifestement inventés, canaris PII présents dans les fixtures mais absents des rapports. `style.py`/`inside.py` référencent des empreintes SHA-256 d'outils/plugins (pas des secrets) hors dépôt.
- **Lecture seule** : compte SQL contraint à USAGE/SELECT sans GRANT OPTION (`Site.php:58-66`), puis `START TRANSACTION READ ONLY` ; mode écriture isolé derrière `wpdb` qui neutralise COMMIT et annule tout (`Site.php:85-127`). Défense en profondeur correcte.
- **Requêtes** : littérales ou préparées (`$wpdb->prepare` pour le COUNT de nettoyage, `Site.php:480-486`) ; `Policy::dsn` filtre DB_NAME/DB_HOST contre l'injection (`Policy.php:11-25`).
- **Chemins** : sortie refusée si dans l'arbre du site ou déjà existante (`Site.php:514-518`) ; `json()` refuse liens symboliques et > 16 Mo.
- **Paywall** : hors objet de ce lot (outil de lecture, ne sert pas de contenu). L'outil enregistre la réponse native de Memberships, y compris `pending`→autorisé ici ; c'est une **observation** à reverser aux lots qui implémenteront le paywall, pas un défaut d'A-03.

## 5. Doctrine

- **Standard d'abord** : lectures via API WooCommerce/Subscriptions/Memberships, réemploi des classes `Audit` d'A-02 (identifiant, config, décodage). Pas de ré-implémentation du standard. `sources.md` cite les pages officielles (une URL de renouvellement en 404 remplacée, signalé).
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\…`, préfixe `imagine_` pour les artefacts WP créés par la sonde, PSR-12 confirmé par `style.json`. Conforme.
- **Rejouable / non-régression** : c'est l'objet même du lot ; rapports déterministes (tri systématique, timestamp exclu). Conforme.

## 6. Études

Sans objet (lot avec code). `sources.md` néanmoins fourni et sourcé.

## Points

**Important**
1. **Portée du banc autorisé.** Les tests de logique *pure* d'A-03 (`Report::compare`, `Policy::dsn/verified/renewalAllowed`) n'ont besoin ni de WordPress ni de base : les porter en paquet PHPUnit découvrable par T01 les mettrait sous la suite rejouée à chaque `rejouer.ps1`, au lieu de dépendre du seul banc Docker/WSL hors-ligne. Aujourd'hui, la commande autorisée ne protège pas le cœur d'A-03 contre une régression future. `wp/tests/a03-non-regression/unit.php` vs `wp/tests/t01/discovery.php:40`.

**Mineurs**
2. **Bruit de diff sur les listes triées.** `sample_states` est une liste triée ; la perte d'un état réindexe toute la liste → 6 entrées `sample_states.membership.N` pour une seule mutation logique (anomalies observées = 12 pour 2 mutations). La détection reste correcte, mais un dictionnaire indexé par état serait plus lisible. `Report.php:19-23`.
3. **`php_error` dépend de l'affichage.** La détection scanne le corps HTML (`Site.php:374`). Avec `display_errors` off (production réelle), seules les erreurs affichées sont vues ; un fatal silencieux n'est attrapé que via le statut 500. Documenté (`non-regression.md:10`, `notes.md:8`) — à confirmer acceptable.
4. **`comparer` n'émet que chemin + classe.** Choix anti-PII correct, mais lire `actions.28 anormal` sans valeur avant/après oblige à rouvrir les deux rapports. Compromis assumé ; à garder en tête. `Report.php:41-43`.
5. **Traçabilité lot.** `non-regression.md:2` parle du « MU de sécurité A-01 » alors que le brief rattache A-03 à A-02 et que le MU vit sous `wp/outils/staging/`. Étiquette de lot imprécise, cosmétique.

**À arbitrer par Ced (questions fermées)**
- Le suivi *exhaustif* des actions planifiées (toute action en attente, tout changement → anormal) est conforme au brief (« rien ne doit disparaître ni changer de date »). Mais autour d'une vraie mise à jour, les actions induites par l'update (`woocommerce_run_update_callback`, `action_scheduler/migration_hook`) et les tâches d'entretien replanifiées seront classées **anormal**, pas « à regarder ». Acceptes-tu ce bruit attendu post-update, ou faut-il une liste de hooks « attendus après mise à jour » ? (oui / non)
- Acceptes-tu la limite `php_error` ci-dessus (point 4), ou veux-tu un contrôle complémentaire (ex. lecture d'un journal d'erreurs sur staging) ? (oui / non)

## Verdict

**Conforme.** Aucun point **bloquant**. Un point **important** (couverture par le banc autorisé) et quatre **mineurs**. Le lot fait ce que demande le brief, prouvé sur site fictif classique et HPOS. Ce verdict n'est pas un GO et ne clôt pas le lot : fusion avec Codex requise, puis clôture par Claude selon la doctrine §6.
