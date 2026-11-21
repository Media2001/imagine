# Vérification C-03 — 2e et dernier tour (Claude, vérificateur)

Objet : contrôle des corrections d'Hermès après `corrections/C-03.md`, lot « Vérification des robots d'indexation ».
Méthode : `git diff` depuis la version relue (baseline `5c45799`, 20/11) sur `wp/plugins/imagine-pilotage/` et `wp/tests/robots-runner/` ; lecture du code corrigé ; contrôle des preuves de tests ; **pas** de nouvelle relecture complète.
Je ne suis pas Hermès, je n'ai pas modifié le code.

---

## 1. Instructions de `corrections/C-03.md`, une par une

### Instruction 1 — Corriger la clé de cache (C03-01, **bloquant**) → **Appliquée**
- `src/Robots/Verificateur.php:45`. Avant : `hash('sha256', 'c03-v1' . serialize($this->configuration) . $robot->identifiant . $ip)` (concaténation sans séparateur). Après : `hash('sha256', serialize(['c03-v2', $this->configuration, $robot->identifiant, $ip]))`.
- Le tuple `(version, configuration, identifiant, IP)` est encodé par `serialize` d'un tableau : chaque composant est préfixé de son type et de sa longueur, l'ambiguïté `'robot'+'192.0.2.1'` ≡ `'robot19'+'2.0.2.1'` disparaît. Version passée à `c03-v2` → anciennes entrées invalidées. Conforme à la consigne (délimiteur non ambigu + bump de version).
- **Test ajouté** : `tests/Robots/CacheDefensifTest.php:20` `testTupleV2DistinctEtIdentiteDuCandidat`. Robots `robot`/`robot19`, IP `192.0.2.1`/`2.0.2.1`, cache partagé : le 2e couple fait **sa propre** résolution (4 appels DNS = 2+2), est refusé (`adresse_differente`, `robot` = null), et les deux clés v2 distinctes sont bien présentes (`assertCount(2, cache->entrees)` + vérification explicite des deux clés, l. 40-43). Le retour `robot` du candidat présenté est contrôlé (l. 33, 44). Sous l'ancienne clé ce test échouerait (le 2e couple lirait le positif du 1er) : il garde réellement l'invariant. Conforme à la consigne.

### Instruction 2 — Fermer C03-02 par un test (défensif) → **Appliquée** (avec normalisation UTC en plus)
- **Test ajouté** : `tests/Robots/CacheDefensifTest.php:48` `testExpirationAbsolueAuxTransitions`, `DataProvider` aux deux transitions `Europe/Brussels` (printemps `2026-03-29`, automne `2026-10-25`, l. 76-79). Instant initial donné en UTC, converti en `Europe/Brussels`. Prouve `expiration − création = exactement 3600 s` puis `60 s`, et que le refus/renouvellement tombe **pile** à l'échéance (3599 ouvert / 3600 expiré ; 3659 / 3660). C'est exactement la preuve demandée.
- **Normalisation UTC** : `Verificateur.php:64`, `$maintenant->setTimezone(new \DateTimeZone('UTC'))->modify(...)`. La fusion concluait que `modify('+N seconds')` est déjà absolu et que le correctif était *probablement inutile* (« sinon le test sert de preuve »). Hermès a appliqué le correctif UTC **en plus** du test. C'est une ceinture-et-bretelles : inoffensif (la comparaison porte sur des instants, le `setTimezone` ne déplace pas l'instant), et dans l'esprit de l'instruction. Voir §3, remarque non bloquante.

### Instruction 3 — Rendre le contrôle d'artefacts rejouable (C03-03, mineur) → **Appliquée**
- `wp/tests/robots-runner/check_artifacts.py:1-10` délègue désormais à `wp/tests/corrections-21nov/verify.py` scopé sur `C-03`, puis `SystemExit(0)` ; l'ancienne implémentation couplée à l'inventaire complet du plugin est conservée dessous, non exécutée (et copiée en `production/C-03/tests-21nov/check-artifacts-historique.py`).
- `corrections-21nov/verify.py:16-22` limite le manifeste à `src/Robots` + `tests/Robots` + fichiers partagés (`README.md`, `phpunit.xml`, `composer.json`, `composer.lock`, `config/robots.php`). Les ajouts légitimes de C-02 (`src/Entreprise`, `tests/Entreprise`) ne font plus casser l'assertion. L'instantané historique est conservé à part. Conforme.

### Instruction 4 — Corriger l'en-tête du README (mineur) → **Appliquée**
- `wp/plugins/imagine-pilotage/README.md:1` : « # Imagine — pilotage (lot C-01) » → « # Imagine — pilotage (C-01 à C-04 : bibliothèques métier et composition du connecteur) ». Conforme.

### Instruction 5 — Mineurs sans urgence, conditionnels à l'élargissement de la liste → **Non appliqués (conforme à la consigne)**
- Anticipation du jeton d'agent `Verificateur.php:26` : toujours `(?=[/\s;)]|$)`, ni `,` ni `(`. Non modifié.
- Empreinte de configuration `serialize(...)` recalculée à chaque appel (`Verificateur.php:45`) : non pré-calculée.
- La consigne les qualifiait explicitement de « sans urgence, à faire **si** la liste de robots s'élargit ». La liste reste Google/Bing : ne pas les appliquer est conforme. Sans effet sur les UA réels (`jeton/version`). Pas un écart.

---

## 2. Résultat des tests

- **Je n'ai pas pu rejouer la suite moi-même** dans cette session : toute exécution de binaire (php / composer / docker) est refusée (mêmes droits que les deux relecteurs). Je ne conclus donc pas sur une exécution indépendante.
- **Contrôle de correspondance preuve ↔ code (fort).** J'ai calculé le SHA-256 des fichiers corrigés et je l'ai comparé au `source_sha256` des reçus livrés `production/C-03/tests-21nov/artifact-verification.json` :
  - `src/Robots/Verificateur.php` = `634305f0…ffef5a4` → **identique** au reçu.
  - `tests/Robots/CacheDefensifTest.php` = `9d0d6b50…213752` → **identique** au reçu.
  Les reçus ont donc été produits contre **exactement** les octets du code corrigé actuel (y compris le changement UTC qui n'est encore qu'en copie de travail).
- **Résultats livrés** (`production/C-03/tests-21nov/`) : `final.log` → `OK (172 tests, 19891 assertions)`, PHP 8.2.36, PHPUnit 11.5.58 ; `verify.py` ré-assertionne `final.xml` (aucun `failure`/`error`/`skipped`), exit/PSR-12/syntaxe/composer-validate à 0, réseau détaché, pas de montages ni de ports, conteneur vérifié → `artifact-verification.json` : **PASS**, scope Robots. Les décomptes concordent entre `final.log`, `final.xml` et `artifact-verification.json`. Le total 172 englobe désormais C-01 (Numeros), C-02 (Entreprise) et C-03 (Robots) ; aucun test n'a été retiré, la suite Robots a gagné les deux nouveaux cas défensifs.

**Conclusion tests** : non rejoués par le vérificateur (droits), mais les reçus livrés sont PASS et prouvés produits contre le code corrigé par empreinte SHA-256. À rejouer une dernière fois dans le banc autorisé avant mise en ligne, comme l'exige la fusion.

---

## 3. Régressions ou modifications non demandées

- **Aucune régression.** Les changements depuis la version relue se limitent à : clé de cache (instr 1), normalisation UTC (instr 2), nouveaux tests `CacheDefensifTest` (instr 1+2), `check_artifacts.py` scopé + bancs `corrections-21nov/` (instr 3), en-tête README (instr 4), plus les reçus `tests-21nov/`. La logique de décision (jetons, DNS inverse/directe, FCrDNS, CIDR, budget de délai, fermeture par défaut) est **inchangée**.
- **Une modification au-delà de la lettre, non bloquante** : la normalisation UTC (`Verificateur.php:64`) dépasse ce que la fusion jugeait nécessaire (elle concluait le correctif probablement inutile, le test suffisant). Elle est inoffensive — `creation` reste en `Europe/Brussels`, `expiration` en UTC, la comparaison l. 51 porte sur des instants absolus — et va dans le sens « le doute ferme ». À signaler, pas à corriger.
- **Interdits doctrine §3** : aucun secret, aucune donnée réelle, DNS fictif injecté, réseau détaché. Respectés.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Le bloquant C03-01 est corrigé et verrouillé par un test qui échouerait sous l'ancienne clé. Le désaccord C03-02 est clos par les tests aux deux transitions (plus une normalisation UTC défensive, inoffensive). Les mineurs demandés (C03-03, README) sont faits ; les mineurs conditionnels (instr 5) sont à juste titre laissés. Aucune régression, aucun problème de fond restant. Les reçus de tests sont PASS et prouvés (SHA-256) produits contre le code corrigé.

Réserves à porter à Ced, qui ne sont **pas** des défauts mais relèvent de sa décision (déjà listées en fusion §5) :
1. Une exécution indépendante de la suite dans le banc autorisé reste à faire avant toute mise en ligne (je n'ai pas les droits d'exécution ici).
2. Les questions d'arbitrage ouvertes restent entières : durées **3 600 / 60 / 200 ms** (`config/robots.php`, inchangé — risque SEO du budget DNS court + cache négatif), principe d'une clé de cache par identité+config (plus strict que « par IP »), périmètre Googlebot/Bingbot seuls, et confirmation hébergeur (répartiteurs de confiance, IP unique normalisée) avant recette R-27/R-28.

*Rappel : ce verdict n'est pas un GO. Il constate que les corrections demandées sont appliquées et sans régression ; la décision de brancher appartient à Ced, après exécution indépendante de la suite.*
