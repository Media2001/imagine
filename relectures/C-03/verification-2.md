# Vérification C-03 — contrôle des modifications post-vérification (Claude, vérificateur)

Objet : Hermès a modifié C-03 **après** `relectures/C-03/verification.md` (commit `68c3a56`, 21/11 10 h 33). Objet du contrôle : quelle consigne justifiait ces changements, sont-ils appliqués, les tests passent-ils, y a-t-il une régression.
Méthode : `git diff 68c3a56..HEAD` sur `wp/plugins/imagine-pilotage/{config,src/Robots,tests/Robots}` et `production/C-03/` ; lecture du code et des tests ; contrôle des reçus par SHA-256. Pas de nouvelle relecture complète.
Consigne justificative : **`docs/arbitrages-2026-11-21.md`, section C-03** (réponses de Ced aux questions ouvertes de la fusion). Les traces de production confirment la filiation (`notes.md`, `PRET`, dossier `tests-21nov/premier-pret-avant-arbitrages/`).
Je ne suis pas Hermès, je n'ai pas modifié le code.

Changements depuis la vérification, en une ligne : `config/robots.php` et `Configuration.php` (délai DNS 200 → 1000 ms), `Verificateur.php` (+7 lignes : les pannes/doutes ne sont plus mis en cache), `CacheDefensifTest.php` (+3 cas défensifs), `CacheTest.php` / `ConfigurationTest.php` / `VerificateurTest.php` (ajustements), et les reçus `tests-21nov/`.

---

## 1. Arbitrages concernés, un par un

### Arbitrage C-03 — Q1, durées 3 600 / 60 / 200 ms → **Appliqué**
Trois points, tous tenus :

- **Délai de résolution porté à 1 000 ms.** `config/robots.php:25` (`delaiDnsMs: 1000`) et valeur par défaut `Configuration.php:12` (`int $delaiDnsMs = 1000`). Avant : `200`. Le budget est unique pour PTR + directe (`Verificateur::reste()`, l. 119-126), donc 1 000 ms couvre bien « toute la séquence » comme l'écrit l'arbitrage.
- **Cache positif 3 600 s, inchangé ; cache négatif 60 s uniquement pour un refus établi.** `Verificateur.php:63-69` : si la décision n'est pas vérifiée **et** que son motif n'est pas dans `[DomaineRefuse, AdresseDifferente, PlageAbsente]`, retour immédiat **sans écriture de cache**. Les trois motifs cachés correspondent mot pour mot à l'arbitrage (« nom hors domaine, résolution directe qui ne redonne pas l'adresse, adresse hors plages »).
- **Délai dépassé ou panne non mis en cache ; la requête suivante retente.** Même bloc l. 63-69 : `DelaiDepasse`, `DnsImpossible` et aussi `PlagesExpirees` tombent hors de la liste blanche → pas de cache, re-résolution au prochain appel. Cohérent avec `notes.md` (« plages expirées ou autre doute sont refusés sans écriture de cache »).
- **Les trois valeurs restent dans la configuration.** `config/robots.php:25-27`, inchangé pour `ttlPositif`/`ttlNegatif`.

### Arbitrage C-03 — Q2, clé de cache (identité + empreinte config) → **Appliqué** (déjà au 1er tour)
`Verificateur.php:45` : `hash('sha256', serialize(['c03-v2', $this->configuration, $robot->identifiant, $ip]))`. C'était la correction C03-01 du premier tour (constatée dans `verification.md`). L'arbitrage la valide (« Oui, une fois C03-01 corrigé »). Rien de neuf depuis, conforme.

### Arbitrage C-03 — Q3, liste Googlebot + Bingbot seulement → **Appliqué**
`config/robots.php:22-23` inchangé (google/bing). Verrouillé en test : `ConfigurationTest.php:106-107` assère désormais la liste exacte `['google','bing']` **et** les jetons exacts `[['Googlebot'],['bingbot']]`. Aucun agent supplémentaire.

### Arbitrage C-03 — Q4, répartiteurs de confiance / IP normalisée → **Appliqué** (hors code, en note)
Ce n'est pas une correction de code (dixit l'arbitrage). Conservé dans `production/C-03/notes.md` (prérequis hébergeur : inventaire des proxies, verrouillage de l'origine, une seule IP normalisée). Le moteur n'utilise toujours aucun en-tête. Conforme à la consigne.

### Instruction 5 (mineurs conditionnels du 1er tour) → **Non appliqué, conforme**
Liste non élargie ⇒ anticipation du jeton (`Verificateur.php:26`) et empreinte config pré-calculée toujours non modifiées. L'arbitrage ne les rouvre pas. Pas un écart.

---

## 2. Résultat des tests

- **Je n'ai pas pu rejouer la suite.** Toute exécution de binaire (php / docker / composer) exige ici une approbation interactive indisponible — mêmes droits que les deux relecteurs. Je ne conclus donc pas sur une exécution indépendante.
- **Correspondance preuve ↔ code (forte).** SHA-256 des fichiers actuels comparés aux reçus `production/C-03/tests-21nov/{final.json, artifact-verification.json}` : `config/robots.php` = `c42a9988…`, `Configuration.php` = `ceb6150f…`, `Verificateur.php` = `95398874…`, `CacheDefensifTest.php` = `fbaa9027…`, `CacheTest.php` = `e036b124…`, `ConfigurationTest.php` = `524b273c…`, `VerificateurTest.php` = `278d8d5f…` → **tous identiques aux reçus**. Les reçus ont donc été produits contre exactement les octets du code livré, arbitrages compris.
- **Résultats livrés** (`final.xml`) : `tests="184" assertions="19980" errors="0" failures="0" skipped="0"`, PHP 8.2.36. `artifact-verification.json` : **PASS**, scope Robots, réseau détaché, DNS fictif. `configuration-arbitrages.json` : `php -l` et PSR-12 sur `config/` à 0. Total passé de 172 à **184** (+12 cas) ; aucun test retiré.
- **Les nouveaux tests prouvent réellement l'arbitrage.** `CacheDefensifTest.php` :
  - `testPannesSansCacheEtNouvelleRequeteRetente` (5 cas : panne inverse/directe, timeout explicite, budget total, budget inverse) : décision refusée, `cache->entrees === []`, **premier appel DNS budgété à 1000 ms**, puis re-résolution immédiate qui réussit (preuve de non-empoisonnement).
  - `testSeulsLesRefusEtablisSontCachesSoixanteSecondes` (domaine / adresse / plage) : une entrée, `expiration − création = 60 s` pile, pas de ré-appel à +59 s, ré-évaluation à +60 s.
  - `testBudgetMilleMsAccepteSousLimiteEtCachePositif3600` : latence 499 ms acceptée, budgets `[1000, 501]`, cache positif `3600 s`.

**Conclusion tests** : non rejoués par le vérificateur (droits), mais reçus PASS et prouvés produits contre le code actuel par SHA-256. À rejouer une dernière fois dans le banc autorisé avant mise en ligne.

---

## 3. Régressions ou modifications non demandées

- **Aucune régression.** La seule modification de comportement — ne plus cacher un échec transitoire (timeout, panne, plages expirées) — est exactement ce qu'ordonne l'arbitrage Q1. Elle réduit le risque SEO signalé au 1er tour (un Googlebot refusé sur lenteur passagère n'est plus bloqué 60 s). La logique de décision (jetons, FCrDNS, CIDR, fermeture par défaut, budget unique) est inchangée.
- **`PlagesExpirees` n'est plus caché négativement**, alors que l'arbitrage ne cite littéralement que trois motifs. Ce n'est pas un écart : c'est un « doute » au sens de l'arbitrage, explicitement rangé par `notes.md` parmi les cas non cachés. À signaler, pas à corriger.
- **`VerificateurTest.php:219`** : le moteur d'aide passe désormais `delaiDnsMs: 200` explicite, pour que les anciens tests de délai gardent leur sens malgré le passage de la prod à 1000 ms. Modification de test, pas de code de prod ; sans effet sur le comportement livré.
- **Interdits doctrine §3** : aucun secret, aucune donnée réelle, DNS fictif, réseau détaché. Respectés.

---

## 4. Verdict

**Prêt pour la clôture.**

L'arbitrage `docs/arbitrages-2026-11-21.md` (C-03) est appliqué dans ses trois volets de code (délai 1 000 ms, cache négatif restreint aux refus établis, pannes non cachées) et verrouillé par des tests ciblés qui échoueraient sous l'ancien comportement. Q2 et Q3 sont tenus ; Q4 reste en note hébergeur, comme prévu. Aucune régression, aucune modification non demandée. Les reçus de tests sont PASS et prouvés (SHA-256) produits contre le code actuel.

Réserve, qui n'est pas un défaut mais relève de Ced :
1. Exécution indépendante de la suite dans le banc autorisé, à faire avant toute mise en ligne (je n'ai pas les droits d'exécution ici).
2. Prérequis non-code encore ouverts et déjà tracés : confirmation du référenceur (liste des robots) et confirmation hébergeur (répartiteurs de confiance, IP unique normalisée) avant branchement R-27/R-28.

*Rappel : ce verdict n'est pas un GO. Il constate que l'arbitrage est appliqué sans régression ; la décision de brancher appartient à Ced, après exécution indépendante de la suite.*
