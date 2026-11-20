# Relecture C-01 — Moteur de la règle des numéros (Claude)

Relecteur indépendant. Date : 20/11/2026. Je n'ai pas lu `codex.md` ni fait la fusion (consigne de Ced).
Périmètre relu : `wp/plugins/imagine-pilotage/src/Numeros/`, `tests/Numeros/`, `production/C-01/`.
Hors périmètre, non relus : `src/Robots/*` et `DelaiDnsDepasse.php` (lot C-03, modifiés dans le même arbre git).

## Méthode et preuves

- J'ai **vérifié par empreinte SHA-256** que 7 fichiers clés sur disque (Moteur, Annee, Calendrier, Numero, fixture, les deux tests) correspondent **exactement** à `production/C-01/tests/final.json`. Les journaux de test d'Hermès portent donc bien sur le code relu.
- Je **n'ai pas pu rejouer les tests** dans cette session : `docker` (sous WSL) et `php` exigent une approbation indisponible en mode non interactif. Les logs d'Hermès annoncent **39 tests, 101 assertions, 0 échec** (PHP 8.2.36, PHPUnit 11.5.58), lint PSR-12 et `composer validate` au vert. À rejouer par Ced avant tout GO (voir point **T-1**).
- J'ai **déroulé à la main** les deux exemples du §3.5 et les cas limites, et comparé à la logique du code.

## 1. Conformité

Les 9 règles du brief sont présentes et correctement situées :

1. Calendrier (`Numero` id/type/sortie/cloture, `Calendrier`). 2. Premier numéro papier (`Moteur::premier`). 3. Dernier = 4 réguliers (`dernier`). 4. Hors-série un par an (`horsSerie`). 5. Accès numérique de date à date (`accesNumerique` + `Annee::finNumerique`). 6. Renouvellement (`renouveler` + `numeros` branche « précédente »). 7. Paiement en 4 fois à marge paramétrable (`echeances($annee, $margeJours)`). 8. Restants à une date (`restants`). 9. Ayants droit d'un numéro (`aDroit`).

Chaque règle renvoie au cahier des charges (§3.5 pour l'essentiel, §3.4/§3.6 cités). Les 4 interprétations imposées par le brief sont isolées derrière une méthode unique et listées dans `notes.md` « À arbitrer par Ced ». Bon.

- **C-1 — important (interprétation non signalée).** `Moteur::accesNumerique` (`Moteur.php:20`) couple l'accès numérique à `Annee::estActive`, donc **le coupe pendant une suspension**. Le périmètre cité du brief est §3.5/§3.4/§3.6 ; la coupure pour impayé relève de §3.8, hors périmètre, et `notes.md` ne range pas cette interprétation dans ses arbitrages. Le brief (point 5) dit seulement « ouvert dès le paiement ou l'acceptation du mandat », « de date à date ». Correction proposée : soit documenter cette coupure dans `notes.md` comme arbitrage, soit découpler l'accès numérique de la suspension. → **À arbitrer par Ced** (question en fin de rapport).

- **C-2 — mineur.** `PRET` est déposé. La doctrine (§4) dit qu'un lot sans tests exécutés n'est pas `PRET`. Ici les tests ont été exécutés par Hermès et les preuves sont vérifiables par empreinte : `PRET` est défendable. `notes.md` précise bien que `PRET` = « prêt à relire », pas un GO. Rien à corriger ; je le note pour mémoire.

## 2. Exactitude métier (déroulé manuel)

**Exemple 1 du §3.5 — commande 8 octobre 2026, après la sortie du n° 170.**
Calendrier fictif : n° 170 sortie 2026-10-05 / clôture 2026-09-20 ; n° 171 clôture 2026-12-20 ; HS-2027 clôture 2027-06-25.
- `premier` = 171 (170 clôturé le 09-20 < 10-08). ✔
- `numeros` = 171, 172, 173, 174 ; `dernier` = 174. ✔
- `horsSerie` = HS-2027 (HS-2026 clôturé, HS-2027 ouvert à la date de début). ✔
Conforme au cahier (« 171, 172, 173, 174 et le hors-série de l'été 2027 »).

**Exemple 2 — renouvellement octobre 2027.**
- `numeros(suite)` = 175, 176, 177, 178 ; `horsSerie(suite)` = HS-2028. ✔
Conforme (« 175 à 178 et le hors-série de l'été 2028 »).

**Cas limites vérifiés, tous cohérents :**
- Clôture incluse : commande le 2026-09-20 (jour de clôture) → premier 171 ; la veille → 170 ; le lendemain → 171. ✔ (interprétation « clôture incluse », conforme à `notes.md`).
- Entre clôture et sortie (2026-09-25) → 171. ✔
- Passage d'année (2026-12-20 → 172 ; 2027-01-01 → 172). ✔
- Fuseau : 2026-09-19T22:00:00Z = minuit Bruxelles → bascule à 171. ✔
- Calendrier partiel (un seul numéro connu) → `premier`=171, `dernier`=null, `nonResolus`=3, aucun identifiant inventé. ✔ (« ne jamais inventer un numéro »).
- **Suspension/réactivation** : un numéro clôturé pendant la suspension n'est **pas** rattrapé (`aDroit('172')` faux après réactivation tardive), tandis qu'un envoi déjà acquis avant la suspension est conservé. ✔ C'est exactement le cas limite du brief. La distinction projection (`numeros`) / droit d'envoi (`aDroit`, qui relit l'historique à la clôture) est propre et bien documentée.

Aucune divergence trouvée entre le code et le cahier des charges sur les cas déroulés.

- **M-1 — mineur (lisibilité).** Fixture `tests/Numeros/fixtures/calendrier.php:22` : `modify('first day of previous month')` est aussitôt écrasé par `setDate(...)`. Le résultat est correct, l'étape est inutile. Simplification possible, non bloquant.

## 3. Tests

- **T-1 — important (à rejouer).** Tests non exécutés par moi dans cette session (voir « Méthode »). Les preuves d'Hermès sont vérifiables et l'empreinte du code concorde, mais la doctrine demande de les rejouer : à faire par Ced dans un conteneur jetable (`docker compose run --rm -w /app/imagine-pilotage php composer test`) avant toute suite.
- **Positif.** Couverture des cas limites réelle, pas seulement le nominal : bornes de clôture, UTC/Bruxelles, passage à l'heure d'été (marge en jours civils et non en secondes), passage d'année, calendrier vide/partiel, renouvellement sans ancrage, suspension/réactivation, invariants de dates/identifiants, refus explicite du 29 février.
- **Positif.** Les tests vérifient la **règle** (valeurs attendues : identifiants, dates d'échéance), ils ne répètent pas le code. Les cycles RED/GREEN sont conservés comme traces.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Fixture manifestement fictive (numérotation réelle mais dates inventées ; aucun abonné, aucun email). Conforme.
- Lot de logique PHP pure : pas de sortie HTML, pas de SQL, pas de REST, pas de hook WordPress → les sujets échappement / nonce / requête préparée / étanchéité paywall **ne s'appliquent pas ici**. Ils resteront à vérifier au branchement (lots « Abonnement et échéances », « Paywall »).
- Isolement des tests : réseau coupé avant PHPUnit, aucun montage ni port, image synthétique. Conforme aux interdits de la doctrine.

## 5. Doctrine

- **Standard d'abord** : le brief impose explicitement un moteur PHP pur isolé *avant* branchement WooCommerce (doctrine §4, « logique métier hors de WordPress »). Pas de réimplémentation d'une fonctionnalité d'extension tierce. Conforme.
- **Conventions §5** : PHP 8.2, `declare(strict_types=1)` partout, namespace `Imagine\Pilotage\Numeros`, PSR-12 (lint vert), objets `readonly`, `DateTimeImmutable` en `Europe/Brussels`, aucune lecture d'horloge dans le moteur (date toujours passée en argument). `README.md` présent et complet. Conforme.
- **Horodatage** : marge de prélèvement paramétrable (`margeJours`), obligatoire et strictement positive ; aucune valeur par défaut décidée (7 et 3 ne sont que des valeurs de test). Conforme au brief (« marge paramétrable, fixée avec l'administration »).

## 6. Études

Sans objet (lot de code).

## Écart à tracer

Aucun écart au cahier des charges constaté. Les cas d'acceptance R-02, R-16, R-20, R-32, R-34 ne sont **pas** automatisés dans ce lot — ce que le brief demande (« ne les automatise pas encore »). `notes.md` le dit clairement.

---

## Verdict : **Conforme** — à corriger sur deux points, puis à faire valider.

Ce verdict **n'est pas un GO**.

**Points classés :**

- **Important**
  - **T-1** : rejouer les tests du lot (non rejoués par le relecteur ; preuves vérifiées par empreinte seulement).
  - **C-1** : l'accès numérique est coupé pendant la suspension (§3.8, hors périmètre cité) sans être rangé dans les arbitrages de `notes.md` → documenter ou découpler.
- **Mineur**
  - **C-2** : `PRET` déposé — défendable (tests exécutés, empreintes concordantes) ; noté pour mémoire.
  - **M-1** : simplification de la fixture (ligne 22).

## À arbitrer par Ced (question fermée)

1. **Accès numérique pendant une suspension pour impayé** : doit-il être **coupé** dès la suspension (comportement actuel du moteur), ou **rester ouvert** « de date à date » jusqu'à l'anniversaire malgré la suspension ? (Oui = coupé / Non = maintenu.)
