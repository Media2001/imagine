# Relecture B-00 — site de démonstration (Claude, relecteur indépendant)

Date : 2026-11-23. Lot : B-00. Brief : `briefs/B-00-site-de-demonstration.md`.
Périmètre relu : `production/B-00/`, `wp/outils/demo/`, `wp/plugins/imagine-site/`, `wp/tests/demo/`, bibliothèques appelées (`wp/plugins/imagine-pilotage/src/Acces`, `.../Robots`).

Je n'ai pas ouvert `relectures/B-00/codex.md`. Pas de fusion à ce stade.

> Avertissement de méthode : le plugin partagé `imagine-site` a été enrichi par C-08 (classe `Paywall`) **après** la production de B-00. B-00 ne se relit donc plus en isolation : l'état actuel du dépôt ne correspond plus à l'état décrit par les preuves B-00. Plusieurs constats ci-dessous viennent de cette dérive.

---

## 1. Conformité

- **Script unique, cible fixe.** `wp/outils/demo/construire.py` existe, ne vise que `imagine-test-demo` (`construire.py:64`, `validate_target` `construire.py:68`, garde de route `request_api` `construire.py:17`). Conforme au brief (« un seul script », « le site s'appelle `imagine-test-demo` et rien d'autre »).
- **Pile cible.** WP 7.0.9, WooCommerce 11.2.2, Subscriptions 9.4.1, Memberships 1.30.3 installés/activés, bibliothèques closes copiées en lecture seule, plugin `imagine-site` activé (`construire.py:204-229`). Conforme ; les versions premium viennent des en-têtes réels des ZIP (`b00_remote.py:32-50`), non de la doc publique.
- **Thème.** Le brief demande : thème `imagine` « dès que B-01 existe ; d'ici là, un thème par défaut ». `construire.py:244` active `imagine` si `wp/themes/imagine/style.css` existe, sinon garde le thème par défaut. **Le code est conforme.** Mais `wp/themes/imagine/style.css` **existe désormais** → une reconstruction active le thème `imagine`, ce que `A-VOIR.md` contredit (voir point 2, Important nº2).
- **Aucune connexion extérieure (site).** Garde MU posée avant extensions et seed (`construire.py:180`, `imagine-demo-offline.php` : `pre_wp_mail`→false, `pre_http_request`→`WP_Error`, passerelles vidées, tracking off). Conforme. Les téléchargements du constructeur (Woo depuis `downloads.wordpress.org`, `construire.py:210`) et Novamira sont distingués du fonctionnement hors-ligne du site (révision du 23/11 13 h 45 citée) — interprétation correcte et signalée.
- **Contenu fictif, modèle provisoire sans ACF.** Types `imagine_numero/_evenement/_partenaire`, taxonomie `imagine_thematique`, métas `imagine_numero_id`/`imagine_reserve` déclarés en code (`imagine-site.php:36-67`). En-tête du fichier signale le caractère provisoire (`imagine-site.php:1-10`, README). Conforme au brief (« type de contenu et champ déclarés en code », « Dis-le en tête du fichier »).
- **Livrables.** `notes.md` (5 lignes), `A-VOIR.md` (6 adresses + une phrase), preuves JSON + `http/`, `PRET` présents. Conforme sur la forme.
- **Interprétation signalée.** Dates du calendrier inventées (15 du mois, clôture −10 j) faute de jours précis dans « Données communes » : signalée `verification.md:10`. Acceptable.

## 2. Exactitude métier

Cas déroulés à la main (lecture du code, le site vivant m'étant interdit).

**Cas A — calendrier vs source.** `docs/recette/profils.md:57` (« Données communes ») demande « numéros trimestriels et un hors-série d'été, sur trois ans, avec sortie et clôture ». `b00_fixtures.py:7-17` produit 4 trimestriels + 1 HS par an × 3 ans = 15 entrées, clôture = sortie − 10 j, triées. **Conforme.** Vérifié par `b00-recette.php:26-33` (15 dates, 5 par an, clôture < sortie) et `test_b00_construction.py:66-69`.

**Cas B — article réservé, visiteur anonyme (règle paywall).** C'est ici que la dérive C-08 casse une promesse B-00.

- Le verrou natif B-00 (mot de passe d'article) était censé, « en attendant C-08 », laisser voir le corps complet avec le secret. C'est ce que teste encore `b00-verifier.py:105-110` (`article_complet_avec_secret_fictif` attend `CONTENU_FICTIF_RESERVE_DEMO-2026-T1_1` dans la réponse après `postpass`).
- Or `imagine-site.php:34` appelle `Paywall::register()`, qui force `post_password_required` à `!decision()['complet']` (`Paywall.php:257-260`) et vide le corps en amont (`sanitizePosts` `Paywall.php:172-186`, `content` `:188-193`).
- Pour un visiteur anonyme (le cookie de mot de passe n'est **pas** une connexion : `get_current_user_id()===0`, `Paywall.php:39-40`), `decision()` appelle `Moteur::decider(...)` qui, article réservé + anonyme + pas de robot vérifié, renvoie `complet=false` (`Moteur.php:75-83`). Le `catch` renvoie aussi `false` si les extensions de droits manquent (`Paywall.php:49-51`).
- **Conséquence : le mot de passe natif ne restitue plus jamais le corps.** `b00-verifier.py:110` échoue aujourd'hui → la preuve « 81 assertions, zéro échec » (`b00-verification-http-idempotence.json`, `verification.md:31`, `PRET:4`) n'est plus reproductible.

Côté sécurité c'est **plus sûr**, pas moins (le corps reste masqué). Le défaut est de conformité/preuve, pas de fuite. Détail en point important nº1.

**Cas limites vérifiés par lecture :** article ouvert (`imagine_reserve='0'`) → `Moteur.php:75` `ContenuOuvert` `complet=true` → corps visible (attendu par `b00-verifier.py:56`) ; numéro (`imagine_numero`) non « managed » (`Paywall.php:17-21`) → sommaire visible, ne contient aucun marqueur réservé. Cohérent. Idempotence : `upsert` dédoublonne par `imagine_demo_key` (`b00-seed.php:18-24`), dates figées, secrets persistés par `setdefault` (`construire.py:187-188`) → logins stables entre relances.

## 3. Tests

- **Lancés en local (mes droits) :** `python -m unittest discover -s wp/tests/demo -p "test_b00*.py"` → **4/4 OK** (cible fixe, chemin hors dépôt, `retry_busy` 3×300 s, API normale/reprise, fixtures/PNG/PDF déterministes). Bons tests de la mécanique du script.
- **Non rejoués (hors de mes droits) :** `b00-recette.php`, `b00-snapshot.php`, `b00-verifier.py` et `construire.py --preuve reconstruction` exigent l'outil de staging et le conteneur Docker vivants (accès site interdit par la doctrine §3). Je m'appuie sur la lecture + les preuves fournies.
- **Commande `composer test` du cadrage :** sans objet ici — `imagine-site` n'a pas de `composer.json`/`phpunit.xml`. Aucune suite composer pour ce lot.
- **Qualité :** `b00-recette.php` couvre bien la structure (types, 15 dates, 5 numéros, 20 articles, 10 médias, versions réelles, email/HTTP/paiement fermés) mais **ne teste pas l'étanchéité du paywall** ; ce test vit dans `b00-verifier.py` (HTTP, site requis). Il n'existe donc **aucun test d'étanchéité rejouable hors site**, alors que la doctrine §4 l'exige. De plus `b00-verifier.py:110` est un **test rouge latent** (voir cas B) : il affirme une règle désormais fausse.

## 4. Sécurité et données

- **Secrets hors dépôt.** `validate_credentials_path` refuse tout chemin dans le dépôt (`construire.py:73-77`, testé `test_b00_construction.py:25`). Écriture dans `~/.imagine-demo/identifiants.json`, `chmod 600`, seul le **chemin** est affiché (`construire.py:182-196`). Copie conteneur en 0700/0600 hors racine web (`b00_remote.py:56-62`). Conforme au brief (« aucun mot de passe dans le dépôt », « affiche son chemin »).
- **Données fictives.** Noms manifestement inventés, courriels `@example.org` (`b00-seed.php:85-88`), avertissement « DÉMONSTRATION ENTIÈREMENT FICTIVE » (`b00-seed.php:110`). Conforme §3.
- **Transport ciblé.** `b00_remote.py` restreint écritures (`:14-24`) et commandes WP (`:26-30`) au seul site `imagine-test-demo`. Bon cloisonnement. Réserve : les opérations passent par `docker exec` direct et contournent le verrou de l'outil → la reprise 409/423 ne couvre que la création (point mineur nº4).
- **Paywall côté serveur.** Gardes multiples (contenu, REST rendu + brut, extrait, flux, oEmbed, en-têtes no-store, XML-RPC désactivé, DNS robot indisponible hors-ligne) : `Paywall.php:195-278`. Plus robuste que le verrou natif B-00. Je n'ai pas pu vérifier l'absence de fuite en conditions réelles (site requis).
- **Échappement.** Sorties du seed et du calendrier échappées (`esc_html`/`esc_url`/`esc_attr`, `b00-seed.php:125-170`, `imagine-site.php:79-89`). Requête d'inventaire des doublons sur `meta_key` constant (`b00-snapshot.php:40`). RAS.

## 5. Doctrine

- **Standard d'abord :** `register_post_type`/`register_post_meta`/protection native/hooks `pre_wp_mail`/`pre_http_request`, sources primaires listées et répondant 200 (`sources-standard.json`, `verification.md:40-46`). Conforme §4.
- **Conventions §5 :** `declare(strict_types=1)`, namespace `Imagine\`, préfixe `imagine_` (options/métas), UI en français via `__()`, aucune modification d'extension tierce (hooks seulement), README présent. Conforme.
- **Réserve de périmètre :** `imagine-site` mêle désormais le modèle provisoire B-00 et le moteur de droits C-08 dans le même plugin. Acceptable (C-08 s'appuie sur B-00), mais cela empêche de rejouer/relire B-00 seul et c'est la cause racine des points importants ci-dessous. À reporter dans `docs/ecarts.md`.

## 6. Études

Sans objet (lot de code).

---

## Points classés

### Important nº1 — Le mot de passe d'article ne restitue plus le corps : docs et preuve B-00 périmées
- **Où :** `Paywall.php:257-260` + `imagine-site.php:34` (override `post_password_required`) vs `b00-verifier.py:110` (`article_complet_avec_secret_fictif`), `A-VOIR.md:14`, `verification.md:22`, `PRET:4`.
- **Problème :** Paywall C-08 (actif sur le site B-00) masque toujours le corps pour un anonyme muni du seul mot de passe natif (trace : `Moteur.php:81-83`). L'assertion `b00-verifier.py:110` échoue donc aujourd'hui ; la preuve « 81/0 » n'est pas reproductible. Pourtant `A-VOIR.md:14` (le fichier transmis à Ced) et `verification.md:22` affirment encore que le secret « restitue le corps complet ». Le README reconnaît le changement (`imagine-site/README.md:26`) mais les livrables B-00 n'ont pas été mis à jour.
- **Correction proposée :** corriger `A-VOIR.md`, `verification.md`, `notes.md` pour décrire le comportement réel (le mot de passe natif ne donne plus le corps ; C-08 gouverne l'accès) ; puis soit retirer/retester `b00-verifier.py:105-110`, soit régénérer la preuve HTTP contre le code actuel. Reporter l'écart dans `docs/ecarts.md`.

### Important nº2 — `A-VOIR.md` annonce Twenty Twenty-Five alors que le code active le thème `imagine`
- **Où :** `A-VOIR.md:3` (« Thème provisoire Twenty Twenty-Five ; B-01 n'existe pas encore ») vs `construire.py:244` + présence de `wp/themes/imagine/style.css`.
- **Problème :** le thème B-01 existe désormais ; une reconstruction active `imagine` (conforme au brief), mais la phrase transmise à Ced et les captures `http/*.html` (prises sous TT25) ne correspondent plus.
- **Correction :** mettre `A-VOIR.md` à jour (thème = `imagine`) et régénérer les captures HTTP, ou figer explicitement que les captures datent de l'état pré-B-01.

### Mineur nº3 — Dérive possible du numéro T1 selon l'état partagé
- **Où :** `imagine-site/README.md:50` (« le numéro T1 affiche aussi les deux fixtures C-08 ») vs `A-VOIR.md:8` (« trois articles réservés, un ouvert »).
- **Problème :** sur un site reconstruit après un seed C-08, T1 porte des articles en plus ; `A-VOIR.md` ne le dit pas.
- **Correction :** préciser que `A-VOIR.md` décrit l'état B-00 seul (sans seed C-08).

### Mineur nº4 — Reprise 409/423 limitée à la création
- **Où :** `construire.py:36` (seul le POST est enveloppé par `retry_busy`) ; `request_api:24-27` lève `StagingBusy` sur 409/423, mais les GET de `ensure_site` (`:32`, `:46`) et les `docker exec` ne sont pas couverts.
- **Problème :** un 409/423 sur un GET se propagerait non capturé ; les écritures via `docker exec` contournent le verrou de l'outil. Conforme à l'esprit (seule mutation via l'outil = la création), mais la règle du brief (« si l'outil refuse une opération ») n'est garantie que pour la création.
- **Correction :** confirmer que c'est voulu, ou envelopper aussi la relecture d'état.

### Points positifs
- Cloisonnement strict sur `imagine-test-demo` (route API, transport, cible).
- Secrets hors dépôt, chemin seul affiché, copie conteneur 0700/0600.
- Idempotence du seed solide (clé de fixture, dates figées, inventaire indépendant + détection de doublons `b00-snapshot.php:38-41`).
- Paywall serveur plus étanche que le verrou natif demandé.

---

## Verdict

**À corriger.**

- **Bloquant :** aucun (le site fonctionne et reste sûr ; pas de fuite de contenu réservé constatée par lecture).
- **Important :** nº1 (mot de passe natif → corps : livrables et preuve HTTP B-00 périmés et trompeurs pour Ced ; test `b00-verifier.py:110` rouge latent), nº2 (thème annoncé faux).
- **Mineur :** nº3 (dérive T1 selon état partagé), nº4 (reprise 409/423 limitée à la création).

Réserves de vérification : la recette PHP, le snapshot et la recette HTTP n'ont pas pu être rejoués (site de staging vivant, hors de mes droits) ; seuls les 4 tests unitaires locaux ont été exécutés (4/4 OK). Ce verdict n'est pas un GO.
