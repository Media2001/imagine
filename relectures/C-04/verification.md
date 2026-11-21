# Vérification C-04 — 2e et dernier tour

Date : 21/11/2026. Vérificateur : Claude Code (NUC). Objet : contrôler que les corrections
demandées dans `corrections/C-04.md` ont bien été appliquées par Hermès après la fusion, sans
régression. Ce n'est **pas** une relecture complète.

Méthode : `git diff a6bb… ← a4f66f7..7f134fe` sur `wp/plugins/imagine-connecteur` et
`production/C-04` (a4f66f7 = dernier état du connecteur avant la fusion du 20/11 18:08 ;
7f134fe = état corrigé du 21/11). Lecture du code corrigé et du test de régression
`tests/CorrectionsTest.php`. Rejeu : voir § Tests.

> **Rappel de rôle : ce verdict n'est pas un GO.** Le GO appartient à Ced.

---

## 1. Suivi instruction par instruction (`corrections/C-04.md` §4)

### Instruction 1 — C04-02 (bloquant, voie CSV) : affectation des lots monotone par abonnement
**Appliquée.** `src/DailyCsvDestination.php:98-122` : `openBatch()` parcourt désormais le journal
`*.event.json`, et pour un événement portant un `subscriptionId`, force
`$day = max($day, $record['batch_day'])` sur chaque prédécesseur du même abonnement ; le repli
quand le `.csv` est déjà scellé part de `max(jour de l'événement, minuit civil courant)`.
L'appel se fait **sous le verrou** (`send()` enveloppé dans `locked()`, lignes 36-49 ; `flock LOCK_EX`,
lignes 204-226) et la mémorisation est **durable** (records persistés, non l'état mémoire).
Scellement et unicité conservés (`exportPreviousDay`, lignes 59-96, inchangés sur ce point).
Test : `tests/CorrectionsTest.php:64` `testRattrapageMonotoneDurableEtOrdreDansLeCsv` rejoue
exactement le scénario (création jour 18 retardée, `18.csv` scellé vide le 19, renouvellement jour 19),
puis relance après redémarrage ; il vérifie `batch_day` identique, ordre création→renouvellement
dans le CSV, unicité et ré-export idempotent (8 assertions, passe).

### Instruction 2 — C04-04 (à traiter comme bloquant avant adaptateur) : contenu détaché
**Appliquée.** `src/Event.php` : le contenu passe d'une propriété promue à une propriété assignée
(`public array $content;`, ligne 15) ; `__construct` appelle `self::snapshot($content)` **avant**
whitelist et validation (ligne 24), et `snapshot()` (lignes 51-64) recopie récursivement les
tableaux et rejette tout non-scalaire/non-tableau (profondeur max 2, cohérente avec
`content › lines › ligne › scalaire`). Les références survivantes sont donc détachées avant stockage.
Test : `tests/CorrectionsTest.php:105` `testInstantaneDetacheAvantValidationDepotEtJournal` passe des
tableaux par référence (`&$identity`, `&$amount`, `&$total`), mute après construction **et** après
dépôt, puis vérifie que le contenu ne bouge pas et qu'aucune donnée interdite (`INTERDIT-FICTIF`)
n'atteint le journal CSV (5 assertions, passe).

### Instruction 3 — C04-03 (important) : survie de l'alerte
**Appliquée.** La notification est désormais portée **par la révision de file** et rejouée
indépendamment de l'envoi comptable :
- `src/Entry.php:19` ajoute le champ `notifications`, plus `withNotification`, `acknowledge`,
  `copyNotifications` et `sameBusinessState` (lignes 41-79).
- `src/Worker.php` : `quarantine()` et le chemin « essais épuisés » attachent la notification à la
  transition CAS puis `flushNotifications()` (lignes 92-129) ; `replay()` rappelle
  `flushNotifications()` en entrée (ligne 36), donc une alerte en échec est retentée au run/replay
  suivant. `flushNotifications` avale l'exception de `notify` (`catch (Throwable) { continue; }`,
  lignes 118-125) et n'acquitte (`acknowledge` + CAS) qu'après succès.
- `src/InMemoryQueue.php:48` : `replace` autorise un CAS « notification seule » hors table de
  transitions via `sameBusinessState`.
Clé de déduplication des alertes = couple `(clé événement, code)` (contrat écrit dans
`src/Alerts.php:9` et `src/QueueStorage.php:17-22`).
Test : `tests/CorrectionsTest.php:136` `testAlerteSurvitPanneEtRedemarrageSansNouvelEnvoi` (2 jeux :
quarantaine et épuisement) — `notify` échoue une fois, la notification persiste, redémarrage → envoi
réussi, notification purgée, **sans** nouvel appel à la destination (`destination->calls()` inchangé).

### Instruction 4 — C04-01 (important) : câbler C-02
**Appliquée.** `composer.json:10-13` ajoute l'autoload PSR-4
`Imagine\Pilotage\Entreprise\ → ../imagine-pilotage/src/Entreprise/`. `src/BillingComposition.php:12-18`
livre `withEntreprise()` qui compose `Validator::billing(..., fn => NumeroEntreprise::depuisSaisie($n)->estValide())`.
`examples/entreprise.php` fournit l'exemple exécutable. L'injection indépendante est **conservée**
(`Validator::billing` garde son callable facultatif ; la composition est explicite et externe au moteur).
`production/C-04/notes.md:58-61` est corrigé (« C-02 n'existait pas » remplacé par la composition réelle).
Test : `tests/CorrectionsTest.php:180` `testCompositionAvecVraiC02EtQuarantaine` — numéro fictif valide
accepté, numéro invalide → quarantaine `enterprise_number` (règle nommée vérifiée).

### Instruction 5 — Injection de formule CSV (important ou à contractualiser)
**Appliquée — option « préfixe apostrophe » retenue**, conforme à la décision Ced citée dans
`notes.md` et `PRET` (« neutralisation formule CSV dès ce lot »). `src/DailyCsvDestination.php:171-174` :
`array_map` préfixe d'une apostrophe toute cellule texte qui, après d'éventuels caractères de
contrôle ASCII (`\A[\x00-\x20]*`), commence par `= + - @`.
Test : `tests/CorrectionsTest.php:201` `testCsvNeutraliseFormulesMaisPasMontantsNumeriques` — les six
cas (`=`, `+`, `-`, `@`, `\t=`, texte simple) sont préfixés comme attendu et le montant entier négatif
`-1200` reste intact (non préfixé car non-chaîne).

### Instruction 6 — C04-05 (mineur) : traçabilité règle → paragraphe → test
**Appliquée.** `production/C-04/notes.md` contient désormais une table « Règle → source → tests »
(7 entrées) reliant chaque règle au §/point de brief et à son test, en distinguant exigences et
interprétations soumises à arbitrage.

### Instruction 7 — Couverture (mineur) : RetryPolicy
**Appliquée.** `tests/CorrectionsTest.php:274` `testRetryPlafondMemeTresGrandNumeroDessai` (plafond
`maximumSeconds`, y compris `PHP_INT_MAX`) et `:284` `testRetryRefuseParametresInvalides` (6 jeux :
`attempts<1`, `base<1`, `factor<2`, `max<base`, `delay(0)`, `delay(-1)`).

### Instruction 8 — Traçage (mineur) : `docs/ecarts.md`
**Appliquée dans son effet, mais pas par Hermès.** Les trois écarts attendus sont bien présents —
`docs/ecarts.md:14-16` : (a) R-39/40/41 dus au branchement ; (b) i18n des messages à ré-emballer ;
(c) `payment_reference` à confirmer avec Step. Hermès a déclaré l'écriture de `docs/ecarts.md` **hors
de son périmètre** (`notes.md`, § « Différés »), ce qui est cohérent avec la doctrine §6 (c'est à
Claude/fusionneur de reporter dans `ecarts.md`, pas au worker). Résultat : la trace existe, objectif
atteint. Rien à corriger côté Hermès.

### Instruction 9 — Rejouer la suite complète dans un environnement autorisé
**Appliquée.** Preuves fraîches `production/C-04/tests-21nov/` :
- `final.xml` : **37 tests, 224 assertions, 0 échec, 0 erreur, 0 ignoré**.
- `final.json` / `artifact-verification.json` : `status: PASS`, `exit_code 0`, PHPCS
  `psr12_exit_code 0`, `syntax_exit_code 0`, `composer_validate_exit_code 0`.
- Conteneur jetable, **réseau coupé** (`network_disconnected: true`), sans montage ni port
  (`no_mounts`, `no_ports`), source du conteneur vérifiée (`container_source_verified: true`).

---

## 2. Tests

Je n'ai **pas pu relancer PHPUnit moi-même** : `php`, `composer` et `docker` sont refusés par le bac
à sable (même limite que les deux relecteurs du 1er tour, et conforme à la doctrine §3 : exécution
seulement en environnement autorisé). Je me suis donc appuyé sur les reçus `tests-21nov/`, mais en les
**rattachant au code réellement relu** : j'ai recalculé localement les empreintes SHA-256 des sources
et des tests, et elles correspondent **octet pour octet** à `tests-21nov/final.json` et
`artifact-verification.json`. Vérifiées notamment :

| Fichier | SHA-256 (préfixe) | Concordance |
|---|---|---|
| `src/Event.php` | `93466597…` | ✓ |
| `src/Worker.php` | `3481fb50…` | ✓ |
| `src/DailyCsvDestination.php` | `b5816a7f…` | ✓ |
| `src/Entry.php` | `a68adde9…` | ✓ |
| `src/InMemoryQueue.php` | `a685be47…` | ✓ |
| `src/BillingComposition.php` | `6730d8cc…` | ✓ |
| `tests/CorrectionsTest.php` | `14c4c0d2…` | ✓ |
| `composer.json` | `3f20376e…` | ✓ |

**Conclusion tests :** le résultat PASS (37/224/0) s'applique bien aux sources corrigées ici présentes.
Les 15 tests de `CorrectionsTest` couvrent nommément chacune des instructions 1 à 7. La suite
historique (`EventTest`, `ExportTest`, `ValidationTest`, `WorkerTest`) passe toujours (pas de
régression de test). Réserve : je certifie la **concordance code↔preuves**, pas une exécution live de
mon fait.

---

## 3. Régressions et modifications non demandées

Aucune régression constatée. Points de forme relevés, tous justifiés par les corrections :

- **`InMemoryQueue::replace` assoupli** (`src/InMemoryQueue.php:48`) : un CAS « notification seule »
  est accepté hors table de transitions via `sameBusinessState`. Nécessaire à l'instruction 3 ; la
  table d'états reste appliquée pour tout vrai changement d'état (`EventTest::testTransitionTableExhaustive`,
  29 assertions, passe).
- **`Event` — profondeur de `snapshot` plafonnée à 2** : cohérente avec la whitelist existante ;
  `testPrivacyWhitelistRejectsUnknownFieldsAtEveryLevel` passe toujours.
- **`openBatch` relit tout le journal à chaque envoi d'un événement d'abonnement** (glob O(n) sous
  verrou, `DailyCsvDestination.php:102`). Correct et borné par le verrou ; simple **point d'attention
  de perf** à volume élevé, pas un défaut de correction.
- Aucune écriture hors périmètre worker : les changements portent sur `wp/plugins/imagine-connecteur`
  et `production/C-04` ; `docs/ecarts.md` relève du fusionneur (cf. instruction 8).

Rappel des réserves déjà actées dans la fusion et **non closes par ce lot** (normales, à la main de Ced) :
« exactement une fois » après accusé perdu reste une exigence à Step ; choix connecteur intégré / n8n ;
unicité transactionnelle distante ; arbitrages de `corrections/C-04.md` §5. Ce ne sont pas des défauts
de correction.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les deux points bloquants (C04-02 voie CSV ; C04-04 traité comme bloquant avant adaptateur) et les
points importants (C04-01, C04-03, injection de formule CSV) sont corrigés, testés, et les preuves de
test correspondent exactement au code relu. Les mineurs (C04-05, couverture RetryPolicy, traçage
`ecarts.md`) sont traités. Aucune régression. Il ne reste **aucun problème de fond** à remonter.

Deux réserves à garder en tête, qui ne justifient pas un retour à Hermès :
1. je n'ai pas pu exécuter la suite en direct (bac à sable) — la garantie repose sur la concordance
   SHA-256 code↔preuves, forte mais non équivalente à un rejeu de ma main ;
2. les arbitrages de `corrections/C-04.md` §5 et les écarts de `docs/ecarts.md` restent ouverts et
   relèvent de Ced / du lot de branchement.

Conformément au rôle : ce « Prêt pour la validation » **n'est pas un GO**. Il appartient à Ced de
prononcer la validation, après arbitrage des questions ouvertes.
