# Relecture B-08 — « Soutenir » et « Notre coopérative » (Claude, relecteur indépendant)

Date : 27 novembre 2026. Brief : `briefs/B-08-soutenir-et-notre-cooperative.md`. Cahier des charges : §3.1, §3.12.
Code relu : `wp/plugins/imagine-site/{CooperativeRegles,Cooperative,Soutenir,SujetRegles,Sujet,SujetConfidentialite}.php`, tests associés, seed `wp/outils/demo/b08-seed.php`, raccord `wp/themes/imagine/header.php`.

> Je n'ai pas ouvert `relectures/B-08/codex.md`. Pas de fusion à ce stade (demande explicite).

## Rejeu de la suite PHP

Commande autorisée, sans argument, exécutée depuis la racine (conteneur jetable, sans réseau, dépôt en lecture seule) :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

```
REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Ligne outils : `OUTILS : 20 outils, 521 contrôles, 0 échecs ; hors rejeu : aucun`.
Bloc `imagine-site` : `OK (178 tests, 2305 assertions)`, 0 échec. Isolation confirmée par le script (`network=none ; rootfs=ro ; mount=…/wp:ro ; cap-drop=ALL`).

## 1. Conformité

- **Les deux entrées existent et pointent juste.** `b08-seed.php:44-53` crée les huit entrées du menu dans l'ordre exact du §3.1 (`Nos numéros · Thématiques · Nos newsletters · Nos événements · Notre coopérative · Soutenir · S'abonner · Connexion`). « Proposer un sujet » n'y figure pas. Conforme.
- **Sous-pages aux intitulés exacts.** `CooperativeRegles.php:10-18` liste les sept intitulés littéraux du §3.12, dans l'ordre ; `b08-seed.php:79-83` les crée en enfants natifs de « Notre coopérative ». Conforme.
- **Lien vers l'espace coopérateurs de B-06.** `Cooperative.php:57-60` vise `get_page_by_path('espace-cooperateurs')`, slug effectivement créé par `wp/outils/demo/b06-seed.php:9`. Le lien ne donne aucun droit ; la protection B-06 reste indépendante. Conforme.
- **« Soutenir », quatre entrées dans l'ordre.** `Soutenir.php:36-50` : abonnement → bénévolat → prise de parts, avec don inséré entre abonnement et bénévolat quand il est ouvert ; ordre vérifié par `SoutenirAdapterTest.php:40-43`. L'abonnement renvoie à l'emplacement B-01 `home_url('/#imagine-abonnement')`, pas un tunnel neuf. Conforme.
- **Don éteint par défaut.** `Soutenir.php:14-17,43-46` : option absente = don fermé ; la section don n'est rendue que si le réglage est ouvert, et sans paiement. Conforme.
- **Prise de parts.** `Soutenir.php:48-49` : lien `rel="sponsored"` quand l'URL est renseignée, simple texte sinon ; URL vide par défaut. Conforme.
- **« Proposer un sujet » hors mise en avant.** Absent du menu ; lien discret depuis la page racine « Notre coopérative » seulement (`Cooperative.php:62-64`). Champs : nom, email, sujet, case de consentement **non cochée** (`Sujet.php:116-119`). Conforme.
- **Rien de CoopHub, pas de paiement.** Aucune `iframe`, aucun compteur, aucun appel : `SoutenirAdapterTest.php:32` le vérifie. Le don ouvert n'est qu'un emplacement. Conforme.
- **Pages non ajoutées à C-23.** Elles sont publiques ; la matrice reste inchangée (NOTE.md). Conforme.
- **Interprétations signalées.** NOTE.md déclare les choix prudents (consentement facultatif = la seule case demandée ; abonnement = emplacement B-01 ; apostrophes typographiques laissées à WordPress). Acceptable.

## 2. Exactitude métier (cas déroulés à la main)

1. **Install neuve, don fermé** — `imagine_soutenir` absente → `configuration()` renvoie `don=false, parts_url=''` → `rendre()` affiche abonnement, bénévolat, prise de parts **en texte**, pas de section don. Conforme au §3.12 (« configuré, activé en 2027 »).
2. **Don ouvert** — `['don'=>true]` → section « don ponctuel ou récurrent » + « sans paiement », aucune action financière. Conforme.
3. **Parts renseignée** — `parts_url='https://example.org/parts'` → `<a … rel="sponsored">`. Vidée → texte seul. Conforme (règle B-05 sur les liens sortants, voir §5).
4. **Proposition, adresse d'un compte vs adresse inconnue** — `Sujet::traiter()` renvoie le **même** message dans les deux cas et ne consulte aucun compte (`SujetAdapterTest.php:32-34`). Le formulaire ne révèle pas l'existence d'un compte. Conforme.
5. **Cas limite — nonce invalide / champ non-chaîne / email mal formé** — refus propre, aucun enregistrement (`Sujet.php:71-78`, `SujetAdapterTest.php:42-45`). Conforme.
6. **Cas limite — export paginé 101 propositions** — trois pages (50/50/1), `done` au bon moment, adresse tierce jamais incluse (`SujetConfidentialite.php:28-37`, test 64-80). Conforme.
7. **Cas limite — effacement par tranches + erreur de lecture** — effacement sur la première tranche à chaque appel (collection qui rétrécit), erreur `wpdb`/suppression → `done=false`, retenté (`SujetConfidentialite.php:39-59`). Conforme : jamais de succès annoncé à tort.
8. **Donnée personnelle rangée et déclarée** — proposition en `wp_posts` (`imagine_sujet`, statut `private`) + `wp_postmeta` (`imagine_sujet_*`), déclarée à l'export **et** à l'effacement natifs de C-21, par adresse (`SujetConfidentialite.php:12-20`). L'adresse d'un compte est donc couverte par le flux C-21. Conforme.

## 3. Tests

- **Au vert**, rejeu ci-dessus. Six tests B-08 ; les mutations (12 sources, NOTE.md) ne sont pas dans le rejeu PHPUnit mais dans l'orchestration démo.
- **Cas limites couverts**, pas seulement le nominal : pagination 101, trois tranches d'effacement, échecs d'écriture/lecture/suppression, nonce et capacités, consentement décoché, transports à zéro.
- **Les tests vérifient la règle, pas le code** : ordre des sections par position (`SoutenirAdapterTest.php:40-43`), absence d'énumération (même message), compteurs `mail=0/http=0` (`SujetAdapterTest.php:41`), statut `private` et `show_in_rest=false` relus. Bonne qualité.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle** : adresses de test en `@example.org`, URL fictive `example.org/parts`.
- **Droits, nonce, échappement, requête préparée** : nonce `imagine_sujet` vérifié (`Sujet.php:75`) ; méta-boîte et détails réservés à `manage_options` (`Sujet.php:23`, `39-41`) ; sorties passées par `esc_html/esc_url/esc_attr` ; lecture par `$wpdb->prepare` (`Sujet.php:102`).
- **Étanchéité** : le type `imagine_sujet` est `public=false`, `publicly_queryable=false`, `exclude_from_search=true`, `show_in_rest=false` (`Sujet.php:35-37`) ; les méta portant nom/email/texte ne sont pas enregistrées pour REST. Le texte personnel ne sort ni par page, ni REST, ni recherche, ni flux.
- **`create_posts => do_not_allow`** : aucune proposition créable via l'UI ; seule la voie formulaire (`wp_insert_post` direct) écrit. Bien vu.
- **Pas de fuite d'existence de compte** : message uniforme, aucune recherche d'utilisateur.

## 5. Doctrine

- **Standard d'abord, respecté** : pages et menu natifs, API Settings, outils de confidentialité natifs, type de contenu natif ; le sur-mesure se limite à la « proposition locale privée ». Les cinq lignes du brief sont dans NOTE.md.
- **Règle B-05 sur les liens sortants** : B-05 pose `rel="sponsored"` sur les liens sortants (brief B-05 ; `wp/themes/imagine/functions.php:182`). `Soutenir.php:49` pose la même déclaration. Comme le raccord `the_content` de B-08 s'exécute en priorité 30 et le filtre partenaire en priorité 20, le lien de parts n'est pas repris par le filtre : la déclaration manuelle est donc nécessaire et correcte. Conforme.
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\Site`, préfixe `imagine_` (options `imagine_soutenir`, `imagine_b08_*`, méta `imagine_sujet_*`), textes français via `__()`. Conforme.
- **Idempotence (comme B-06)** : `b08-seed.php:13-33,55-71` relit les témoins `imagine_b08_page` / `imagine_b08_menu_item`, réutilise l'existant et **refuse toute collision** (page ou item étranger) ; cible verrouillée à `imagine-test-demo`. Conforme.

## 6. Études

Sans objet (lot avec code).

## Verdict

**Conforme** — sous réserve des points mineurs ci-dessous. Rappel de doctrine : ce verdict n'est **pas** un GO ; la validation visuelle de Ced et la seconde relecture restent dues.

Aucun point **bloquant**. Aucun point **important**.

### Points mineurs

1. **`wp/plugins/imagine-site/README.md`** — le README ne documente pas B-08 (ni ses deux réglages `imagine_soutenir[don]` / `[parts_url]`, ni le type `imagine_sujet` et ses rappels export/effacement). B-06 et B-07 y manquent aussi : écart qui s'accumule au regard du §5 de la doctrine (« chaque extension sur mesure a un README : ce qu'elle fait, ses réglages, comment lancer ses tests »). *Correction proposée* : ajouter une section B-08 au README (réglages, stockage de la proposition, rejeu des tests).
2. **`wp/outils/demo/b08-seed.php:47`** — l'entrée de menu « Nos newsletters » vaut `get_permalink(get_page_by_path('nos-newsletters'))` ; si cette page est absente (les newsletters ne figurent pas dans les dépendances déclarées du lot : B-00, B-01, B-05, B-06), `get_permalink(null)` renvoie `false` et l'item reçoit une URL vide. *Correction proposée* : garder l'entrée seulement si la page existe, sinon un repli explicite (fragment d'accueil), comme pour les autres entrées custom.
3. **`wp/plugins/imagine-site/Soutenir.php:21-23`** — `url()` accepte `http` autant que `https` pour l'adresse de prise de parts. Pour un lien sortant vers CoopHub, n'autoriser que `https` serait plus prudent (la règle B-05 ne tranche pas le schéma, d'où le rang mineur). *Correction proposée* : restreindre à `https`, ou le signaler comme choix assumé.
4. **`wp/plugins/imagine-site/Sujet.php:57`** — toutes les propositions portent le même titre neutre « Proposition de sujet » ; dans la liste d'administration elles ne se distinguent que par la date. Pur confort de tri, sans incidence métier ni fuite. *Correction proposée* (optionnelle) : colonne date/sujet tronqué non sensible.

### Décisions techniques, défaut proposé

- **Schéma du lien de parts** (point 3) : *défaut prudent* — restreindre à `https`. Hermès peut l'appliquer sans attendre ; j'arbitre après coup.

### Pour Imagine

- Aucune question métier ouverte : le brief et le §3.12 tranchent tout (don fermé jusqu'en 2027, intégration CoopHub par lien à défaut d'accès). Rien à arbitrer par Ced au titre du métier dans ce lot.

### Réserve de vérification

Je n'ai pas rejoué la recette HTTP « live » (pas d'accès site, interdit par mes droits) : je m'appuie sur le rejeu PHP ci-dessus et sur le déroulé manuel. Les reçus HTTP/mutations d'Hermès existent dans `production/B-08/` mais ne sont pas des preuves que j'ai pu reproduire moi-même.
