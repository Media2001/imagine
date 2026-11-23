# Relecture C-08 — le paywall branché sur l'article (relecteur Claude)

Date : 2026-11-23. Brief : `briefs/C-08-paywall-sur-article.md`. Cahier : §3.9, §4.4 ; recette R-25 à R-31 (`docs/recette/cas.md`).
Périmètre lu : `wp/plugins/imagine-site/`, `wp/themes/imagine/` (point de sortie + gabarits), `wp/outils/demo/c08*.php|py`, `wp/tests/demo/c08-*`, `production/C-08/`. Bibliothèques closes C-06/C-03 lues mais non jugées (lot clos).
Je n'ai pas ouvert `relectures/C-08/codex.md`. Pas de fusion à ce stade.

## 1. Conformité

- **Les quatre attendus du brief sont présents.**
  1. Adaptateur : `Paywall::decision()` (`Paywall.php:24`) rassemble réservation, numéro, date de sortie, visiteur + droits (Memberships/Subscriptions, `rights()` `Paywall.php:69`), robot (`robot()` `:136`) et instant, puis appelle `Acces\Moteur::decider` (`:41`).
  2. Point de sortie du corps : `imagine_article_body()` (`functions.php:34`) sert `the_content()` si `complet`, sinon l'extrait puis le gabarit du bloc (`paywall-{connexion,abonnement,regularisation,decouverte_epuisee}.php`).
  3. Étanchéité serveur : page (`content` + `sanitizePosts`), REST (`rest` `:195`), flux (`the_content_feed`, `get_the_excerpt`), extrait auto, partage (`share` `:224`, sans `articleBody`), oEmbed, embed ; XML-RPC coupé. Fermé par défaut : le `catch` renvoie `complet=false` (`:50`).
  4. Cache : en-têtes privés `no-store` posés (`cacheHeaders` `:211`), sans extension de cache.
- **Livrables présents** : `A-VOIR.md`, `PRET`, tests, blocs neutres à texte provisoire. Chemin des identifiants hors dépôt cité, jamais les mots de passe.
- **Interprétations signalées par Hermès** (acceptables, conformes à la doctrine « fermé par défaut ») : tout `post` natif est gouverné, l'absence de métadonnées n'ouvre pas (`README.md:30`, `imagine-site.php` + `Paywall::managed`) ; la grâce exige une fenêtre explicite sur l'objet Subscriptions, `on-hold` seul reste fermé (`Paywall.php:114`).
- **Point d'interprétation à noter** : pour l'anonyme, le moteur renvoie le bloc `connexion` (`Moteur.php:83`), là où R-26 dit « bloc d'abonnement ». Non bloquant : `paywall-connexion.php:8` propose à la fois « Se connecter » et « S'abonner ». La distinction anonyme/identifié-sans-droit vient de C-06 (clos).
- **Rien en trop** : PDF, découverte complète, achat d'un numéro, mode lecture, tunnel bien laissés hors périmètre et explicités.

## 2. Exactitude métier (cas déroulés à la main)

Déroulé sur le code (adaptateur + `Moteur::evaluer`) pour les situations exigées par la « Preuve » du brief :

- **R-25 / A-CARTE abonné actif** : Membership active + Subscription active, dates 2026→2030, instant 2026-11-23 dedans → `abonnement()` renvoie `AbonnementActif`, `complet=true`, bloc `Aucun`. Thème : `the_content()`, pas de bloc. Témoin présent. Conforme.
- **R-26 / V-ANON** : `identifie=false`, `droits=[]`, robot non vérifié, `reserve=true` → `Decision(false, Anonyme, Connexion)`. Extrait + bloc connexion ; témoin absent de toutes les sorties contrôlées. Conforme (réserve : recherche interne, voir §4).
- **Abonné en grâce** : Subscription `on-hold` + Membership `paused` + fenêtre `_imagine_acces_grace_*` ouverte → `etat=grace` (`:119`), `DelaiGrace`, `complet=true`, bloc `Regularisation`. Bandeau de grâce affiché (`paywall-regularisation.php:7`, message conditionné à `complet`). Conforme.
- **Compte sans droit** : `identifie=true`, aucune adhésion reconnue → `SansDroit`, bloc `Abonnement`. Extrait + bloc abonnement. Conforme.
- **Faux robot** : UA Googlebot + IP usurpée en en-tête → DNS désactivé → robot non vérifié → traité comme anonyme → extrait. Conforme.
- **Panne de l'adaptateur / métadonnées invalides / numéro absent** : `catch` → `complet=false`, bloc `abonnement` (`:50`) ; `faults.json` le confirme sur page/REST/flux/oEmbed. Fermé par défaut respecté.

Cohérence des deux couches : `sanitizePosts` et `imagine_article_body` prennent la même `decision()`, donc le corps servi et le corps expurgé s'accordent. Pas d'incohérence trouvée sur les cas nominaux.

## 3. Tests

- **Je n'ai pas pu exécuter les tests.** `docker compose … composer test` demande une approbation non accordable en session non interactive (plusieurs tentatives refusées). La suite C-08 (`c08-verifier.py`, `c08-faults.py`, `c08-regression.py`, `c08-idempotence.py`) vise le site de démonstration `imagine-test-demo`, dont l'accès dépasse les droits du relecteur (lecture seule, exécution locale uniquement). Je me suis donc appuyé sur les reçus déposés et le déroulé à la main.
- **Reçus relus (tous à zéro échec)** : `http.json` 229/0, `faults.json` 29/0, `regression.json` 120/0, `local-tests.json` 13/0, `idempotence.json` 4/0, `verification-finale.json`. Les `red-*.json` sont des traces d'échecs corrigés, pas le statut final.
- **Lacune de couverture — recherche interne (importante, liée au §4)** : la recherche n'est testée qu'avec le terme public « C08 » (`c08-verifier.py:107`), jamais avec la phrase témoin. Le reçu `http/recherche.html` montre « Aucun contenu » : l'étanchéité tient au mot de passe natif (voir §4), pas à une sortie testée du corps réservé.
- **Lacune de couverture — mappage de l'adaptateur (mineure à importante)** : `rights()` traduit beaucoup d'états Memberships/Subscriptions (`suspendu`, `expire`, `virement_non_valide`, `on-hold` sans fenêtre, `paused` sans abonnement, rôle `author`). Seuls `actif`, `grace`, `sans-droit` sont éprouvés de bout en bout. Le minimum du brief (anonyme, actif, grâce, faux robot) est atteint ; mais ce « raccord fin » porte une vraie logique sans test isolé. Proposition : un test unitaire du mappage `rights()` (doublures WP/WC) ou des profils A-SUSP/A-EXPIRE en plus.
- **Robot vérifié non éprouvé** : le chemin positif (robot vérifié → texte complet + balisage payant, `Moteur.php:78`) n'est pas démontrable hors ligne (DNS coupé). Honnêtement déclaré (`A-VOIR.md:54`), mais R-27 n'est donc couvert qu'à moitié.
- Les tests vérifient bien la règle (présence/absence du témoin, blocs, en-têtes), pas seulement le code.

## 4. Sécurité et données

- **Secrets / données réelles** : conformes. Comptes fictifs `@example.org`, mots de passe hors dépôt (`c08-seed.php:10`, `A-VOIR.md:15`), aucune passerelle, aucun envoi. Reçus sans cookie/nonce/mot de passe.
- **Échappement** : gabarits en `esc_html`/`esc_attr`/`esc_url` ; `share()` en `esc_attr` + `wp_json_encode` avec drapeaux `JSON_HEX_*` (`Paywall.php:238`). Écritures de métadonnées sous `auth_callback` (`imagine-site.php:61`).
- **Étanchéité du corps** : solide sur page, REST (rendu ET brut supprimés, `protected=true` `:201`), flux, extrait, oEmbed, embed, partage (pas d'`articleBody`), XML-RPC coupé ; `sanitizePosts` donne une défense en profondeur sans écrire dans le cache objet partagé.

**Points à corriger :**

- **[Important — possiblement bloquant] La recherche interne n'est pas fermée par C-08.** `Paywall.php` n'ajoute aucune garde de recherche (`pre_get_posts`/`posts_search`). Le corps réservé reste dans `post_content` en base (l'expurgation n'a lieu qu'au rendu). Aujourd'hui l'article réservé n'apparaît pas dans `/?s=…` seulement parce que la fixture garde un `post_password` natif (`c08-seed.php:89`), ce que `A-VOIR.md:32` reconnaît. Or le modèle C-08 déclare ce mot de passe comme simple repli, « jamais un droit de lecture » (`README.md:10`). Un article réservé géré par le seul `imagine_reserve=1`, sans mot de passe, serait apparié par la recherche SQL sur `post_content` et remonterait à l'anonyme (titre + extrait), révélant que le corps caché est indexé. Le §3.9 et la doctrine §4 exigent l'étanchéité de la recherche interne côté serveur. Proposition : fermer la recherche dans C-08 (exclure les `post` non `complet` du résultat ou retirer `post_content` de l'appariement pour un visiteur non autorisé), et tester `/?s=<témoin>` → zéro résultat révélateur, indépendamment du mot de passe.
- **[Important] `decision()` recalculée sans mémoïsation.** Elle est rappelée par `sanitizePosts` (une fois par post), `content`, `post_password_required`, `share`, chacun relançant les requêtes Memberships/Subscriptions et la vérification Robots (`Paywall.php:40`, `:83`, `:103`, `:160`). Sur une archive ou une page de recherche à N articles, coût en N×. Risque direct sur les seuils de réception du chapitre 5 (Lighthouse mobile, LCP). Proposition : mémoïser par `(ID de post, utilisateur)` pour la requête courante.
- **[Mineur] Portée du cache trop large.** `cacheHeaders` + `DONOTCACHEPAGE` sont posés sur **toutes** les réponses (`wp_headers` et `rest_post_dispatch` à `PHP_INT_MAX`, `:249`), y compris les pages ouvertes et l'accueil. Le §4.4 demande que le cache *distingue* connectés et anonymes, pas qu'il soit désactivé partout. Sûr pour la démo (fermé par défaut), mais à resserrer quand un cache réel arrivera (lot cache séparé). À tracer.
- **[Mineur] Déterminisme des deux couches.** Faute de mémoïsation, `sanitizePosts` et `imagine_article_body` recalculent l'instant indépendamment ; à la seconde d'une bascule d'échéance, les deux pourraient diverger (corps complet d'un côté, expurgé de l'autre). La mémoïsation ci-dessus lève aussi ce risque.
- **[Mineur] Contournement par `get_post()`.** L'expurgation passe par le filtre `the_posts` ; un futur code qui ferait `echo get_post($id)->post_content` la contournerait (cache objet intact, voulu). Le thème actuel est sûr. À documenter comme règle pour la suite.
- **[Mineur] Réglages du moteur non alimentés.** L'adaptateur ne lit pas d'option vers `Acces\Reglages` : le moteur tourne toujours avec les valeurs par défaut (`Moteur.php:34`). Sans effet dans ce lot (futur/PDF hors périmètre) ; à brancher avec l'écran C-10.

## 5. Doctrine

- **Standard d'abord** : respecté. Objets natifs Memberships/Subscriptions, pas de table de droits parallèle, hooks uniquement, bibliothèques closes ni modifiées ni activées. `references.md` cite les pages officielles (Memberships, Subscriptions, hooks WP, balisage payant Google).
- **Logique métier hors WordPress** : le moteur C-06 est pur et testé ; l'adaptateur est la couche fine attendue — mais sa logique de mappage reste sans test isolé (voir §3).
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_`, textes traduits, `README.md` présent. Conforme.
- **[Mineur] Non-régression.** Les recettes historiques B-00/B-01 (« exactement quatre articles », « mot de passe ⇒ complet ») deviennent fausses sur le site augmenté et ne sont ni mises à jour ni retirées. `c08-regression.py` les remplace proprement (snapshot B-00 exact `:19`, empreintes des bibliothèques, HTML B-01). Risque : une exécution naïve de l'ancienne suite afficherait du rouge et serait prise pour une régression. Proposition : marquer explicitement obsolètes (ou retirer) `b00-verifier.py`/`b01-verifier.py` sur ce qui ne vaut plus, pour garder un corpus vert.
- **[À tracer] Écart.** Le fait que l'étanchéité de la recherche repose sur le mot de passe natif (et non sur C-08) mérite une ligne dans `docs/ecarts.md` tant que le point 4 n'est pas corrigé.

## Verdict

**À corriger.**

- **Bloquant** : aucun au sens strict — les fixtures livrées ne fuient pas et le minimum du brief (4 situations) est prouvé.
- **Important** : (1) la recherche interne n'est pas fermée par C-08 et dépend du mot de passe natif (§4) — à trancher en fusion si on le tient pour bloquant au regard du §3.9 ; (2) `decision()` sans mémoïsation, risque sur les seuils de réception du chapitre 5.
- **Mineur** : portée du cache trop large ; déterminisme des deux couches ; contournement `get_post()` ; réglages du moteur non alimentés ; recettes B-00/B-01 obsolètes laissées rouges ; R-27 (robot vérifié) non démontré hors ligne (déclaré).

Ce verdict n'est pas un GO. Les tests n'ont pas été rejoués par le relecteur (voir §3) ; il s'appuie sur les reçus déposés et le déroulé à la main.
