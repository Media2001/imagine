# Vérification C-01 (2ᵉ et dernier tour) — après corrections d'Hermès

Vérificateur : Claude. Date : 21/11/2026. Base de comparaison : état du 20/11 au soir (`40464e7`) → `HEAD`.
Périmètre du diff relu : `wp/plugins/imagine-pilotage/src/Numeros/`, `tests/Numeros/`, `production/C-01/`.
Je **ne refais pas** la relecture complète : je vérifie uniquement l'application des instructions de `corrections/C-01.md`, le résultat des tests, et l'absence de régression.

**Point clé de contexte.** Les trois questions « À arbitrer par Ced » de la fusion ont été **tranchées par écrit** : `docs/arbitrages-2026-11-21.md` (validé en bloc le 21/11 à 10 h 20, repris dans `docs/decisions.md`). Les choix d'Hermès sont donc jugés **contre ces décisions**, pas contre les options ouvertes de la fusion :
- Suspension → accès numérique **coupé** (comportement conservé).
- 29 février → fin au **28 février** de l'année suivante.
- Clôtures inversées → **refus à la construction**, message nommant les numéros.

---

## 1. Application des instructions de `corrections/C-01.md`

### Instruction 1 — C01-02 (séquence ne saute jamais un régulier) — **Appliquée**
- Contrôle ajouté **à la construction** : `wp/plugins/imagine-pilotage/src/Numeros/Calendrier.php:54-65` rejette (`InvalidArgumentException`) un calendrier dont un régulier de sortie postérieure a une clôture antérieure, avec un message nommant les deux numéros.
- Couvre aussi `Calendrier::modifier` : la méthode reconstruit l'objet via `new self(...)` (`Calendrier.php:37-38`), donc la modification inversée bute sur le même contrôle.
- Tests : `tests/Numeros/CorrectionsTest.php:23-31` (refus à la construction) et `:33-55` (modification inversée refusée **et** séquence/`dernier`/`echeances` inchangés : `171,172,173,174`).
- Conforme à l'arbitrage Ced #3 (« refusé à la construction, message qui nomme les numéros »). La séquence `Moteur::numeros` ne peut donc plus sauter un intermédiaire, l'entrée anormale étant barrée en amont.

### Instruction 2 — C01-03 (ouverture numérique immédiate le 29 février) — **Appliquée**
- `wp/plugins/imagine-pilotage/src/Numeros/Annee.php:57-58` : `finNumerique()` **ne lève plus** d'exception pour une ouverture le 29/02 ; elle renvoie le 28/02 de l'année suivante (heure d'ouverture conservée, borne exclusive).
- `Moteur::accesNumerique` inchangé (`Moteur.php`, empreinte identique au reçu) : il n'échoue plus puisque `finNumerique` ne jette plus. L'ouverture immédiate fonctionne.
- Tests : `tests/Numeros/CorrectionsTest.php:57-73`, déroulés **via `accesNumerique()`** pour les deux motifs d'activation : la veille (faux), à l'instant du paiement (vrai), le lendemain (vrai), pendant une suspension (faux), et aux bornes de fin au 28/02 (vrai à 14:29:59, faux à 14:30:00).
- Conforme à l'arbitrage #2. La fusion disait « sans trancher la fin » ; ici la fin est tranchée au 28/02, mais **parce que Ced l'a arbitré** entre-temps — ce n'est donc pas une initiative d'Hermès.

### Instruction 3 — C-1 (documenter la coupure numérique en suspension, sans toucher au code) — **Appliquée**
- `production/C-01/notes.md`, point « Suspension » : la coupure `accesNumerique → estActive` est désormais écrite, avec renvoi à l'arbitrage Ced C-01/1.
- Aucun changement de code sur ce point (correct : l'arbitrage confirme le comportement actuel).

### Instruction 4 — C01-01 (traçabilité règle → §CDC → test) — **Appliquée** (variante « table »)
- `production/C-01/notes.md` : section « Corrections et traçabilité — 21 novembre 2026 » avec une table **Règle → source → test** couvrant les 9 règles.
- La fusion laissait le choix entre annotation par méthode **ou** table d'ensemble ; Hermès a retenu la table. Exigence satisfaite. (La référence au §CDC n'est pas posée en commentaire sur chaque méthode du code — ce n'était pas obligatoire.)

### Instruction 5 — M-1 (nettoyage fixture) — **Appliquée**
- `tests/Numeros/fixtures/calendrier.php:22` : le `modify('first day of previous month')` mort avant `setDate(...)` est supprimé ; résultat des dates inchangé.

### Instruction 6 — T-1 (rejeu ciblé + vérifier l'absence de la suite Robots dans la preuve) — **Appliquée côté production**
- Rejeu enregistré : `production/C-01/tests-21nov/` (voir §2).
- Preuve ciblée `numeros.xml` : ne contient **que** les suites `Numeros` (CorrectionsTest, InvariantsTest, MoteurTest). **Aucune suite `Robots`** dans la preuve C-01. Le point T-1 de la fusion est levé.
- Réserve : je n'ai **pas pu rejouer moi-même** (php/docker refusés en session non interactive, comme au 1er tour). Le **rejeu indépendant par Ced** reste requis avant toute suite — ce n'est pas un GO automatique.

---

## 2. Résultat des tests

- Source vérifiée par empreinte : les 7 fichiers clés sur disque (`Annee`, `Calendrier`, `Moteur`, `CorrectionsTest`, `InvariantsTest`, fixture, `phpunit.xml`) ont un **SHA-256 identique** au reçu `production/C-01/tests-21nov/artifact-verification.json`. La preuve porte donc bien sur le code actuel.
- Suite ciblée **Numeros** (`numeros.json` / `numeros.xml`) : **42 tests, 121 assertions, 0 échec, 0 erreur, 0 ignoré**. `exit_code` 0 ; PSR-12, syntaxe et `composer validate` à 0. PHP 8.2.36. Réseau coupé, aucun montage/port.
- Suite **complète** du plugin (`final.json` / `artifact-verification.json`) : **175 tests, 19 911 assertions**, `exit_code` 0 — garde-fou de non-régression inter-lots au vert.
- Évolution cohérente depuis la relecture : 39 → 42 tests Numeros = +3 tests de `CorrectionsTest`.
- **Non rejoué indépendamment par le vérificateur** : preuve de production vérifiée par empreinte uniquement.

## 3. Régressions ou modifications non demandées

- **Aucune régression constatée.** Le diff `40464e7 → HEAD` se limite au périmètre des corrections : `Annee.php`, `Calendrier.php`, fixture, `InvariantsTest.php`, `CorrectionsTest.php` (nouveau), `notes.md`, `PRET`, reçus `tests-21nov/`.
- La réécriture de `InvariantsTest.php:120-126` (`testAnniversaireDu29Fevrier…`) qui attendait une `LogicException` est **nécessaire** : elle suit le nouveau comportement arbitré (28/02). Pas un test supprimé en douce.
- **Aucune modification non demandée** : pas de changement de code hors instructions, aucune valeur métier nouvelle, aucun automatisme financier ajouté. Les valeurs de marge (7/3) restent des valeurs de test.
- `Moteur.php` **inchangé** (empreinte identique) : la correction C01-03 est portée par `Annee::finNumerique`, pas par un contournement dans le moteur.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les deux défauts importants de la fusion (C01-02, C01-03) sont corrigés et **alignés sur les arbitrages écrits de Ced**. C-1 est documenté, la traçabilité (C01-01) et le nettoyage (M-1) sont faits, le rejeu (T-1) est ciblé et la preuve C-01 est exempte de la suite Robots. Aucune régression, aucune modification hors périmètre.

**Ce n'est pas un GO.** Il reste deux gestes qui relèvent de Ced, pas d'un problème de fond :
1. **Rejouer les tests indépendamment** dans un conteneur jetable (`composer test -- --testsuite Numeros`) — le vérificateur n'a pu valider que par empreinte.
2. Prononcer la **validation** du lot (le verdict de vérification n'en est pas une).

Aucun problème de fond restant n'est remonté.
