# Vérification C-05 — second et dernier tour

Vérificateur : Claude Code (NUC). Date : 22/11/2026.
Objet : contrôler l'application des instructions de `corrections/C-05.md` après correction par Hermès, relancer les tests, signaler régressions.
Base comparée : diff `f2f8e21` (commit de la fusion, code relu) → `HEAD` sur `wp/` et `production/C-05`. Pas de nouvelle relecture complète.

---

## 1. Instructions de `corrections/C-05.md`

### Instruction 1 — (Important, C05-01) Chronologie à la jonction des blocs
**Appliquée.**
- `src/Echeancier/Planificateur.php:34-37` : avant la boucle, si `$annee->precedente !== null`, le bloc précédent est planifié récursivement et `$precedente` est initialisé à sa 4ᵉ date (`$blocPrecedent[3]->date`). Le contrôle `DATES_NON_CROISSANTES` (`Planificateur.php:42-44`) compare donc bien la 1ʳᵉ échéance reconduite à la dernière du bloc précédent.
- Aucune commune déplacée, aucune borne anniversaire rétablie : seule une comparaison stricte a été ajoutée.
- Test de refus explicite ajouté : `tests/Echeancier/PlanificateurTest.php:302` (`testCloturesEgalesJonctionRang4Rang1RefuseesExplicitement`), avec fixture dédiée `c05CalendrierJonctionEgale()` (`tests/Echeancier/Fixture.php:49-59`) : clôture de `REG-2028-04` alignée sur `REG-2028-01` → même instant 03/01/2028 → `DATES_NON_CROISSANTES` attendu.
- Cas valide du 09/04 conservé : `PlanificateurTest.php:317` (`test09AvrilGardeCommunesEtCinqDatesAvecChronologieInterBlocs`) vérifie 5 dates en fenêtre et chronologie inter-blocs ; e2e `commande 2027-04-09` → `first_window_payment_dates: 5`, 0 échec. Balayage 365 jours (`PlanificateurTest.php:356`) : exactement 28 fenêtres à 5 dates, aucun faux refus.

### Instruction 2 — (Important, I1) Tests exécutables par la commande standard
**Appliquée.**
- `phpunit.xml:9` : testsuite `Echeancier` déclarée (`<directory>tests/Echeancier</directory>`).
- Cas portés en vraies classes PHPUnit : `tests/Echeancier/PlanificateurTest.php` et `tests/Echeancier/ReglagesAdministrationTest.php` ; données communes isolées dans `tests/Echeancier/Fixture.php`.
- Banc maison supprimé : `tests/Echeancier/run.php` retiré (−356 lignes dans le diff).
- Le nouveau test C05-01 entre dans cette suite (voir instruction 1).

### Instruction 3 — (Mineur, M1) Paramètre `finEngagement`
**Appliquée.**
- `src/Echeancier/Planificateur.php:22` : signature désormais `planifier(Annee $annee, ?int $margeJours = null)` ; `finEngagement` et la garde `≤ début` retirés, `use DateTimeImmutable` supprimé. Plus de `TypeError` latent face à `finNumerique()` nullable, ni de formulation « compatibilité positionnelle ».
- Couvert par `PlanificateurTest.php:110` (`testApiSansFinEngagementEtProjectionAnneeNonActivee`) : vérifie la signature par réflexion et la projection d'une `Annee` non activée (`finNumerique() === null`).

### Instruction 4 — (Mineur, M2) Refus admin par `wp_die()`
**Appliquée.**
- `src/Echeancier/ReglagesAdministration.php:68` : `throw \LogicException` remplacé par `wp_die(__('Gestion WooCommerce requise.', 'imagine-pilotage'))`.
- Contrat testé : `tests/Echeancier/ReglagesAdministrationTest.php:12` + double `wp_die` (`tests/Echeancier/FonctionsWordPressFictives.php:21`). Confirmé aussi en e2e réel : check `admin_anonymous_wp_die_translated` → pass (classique et HPOS).

### Instruction 5 — (Mineur, M3 + C05-02) Deux citations à compléter
**Appliquée.**
- `production/C-05/sources/review-fusion-22nov-1458.json` : source [5] (M3) porte les citations littérales « Customer signs up: April 6 » / « First renewal date: May 1 (not July 1) », `status 200`, `page_sha256`, `literal_quotes_verified: true` ; source [4] (C05-02) porte le hook `woocommerce_subscription_payment_complete` et l'avertissement sur les renouvellements anticipés, mêmes garanties.
- `production/C-05/proposition.md:47` reformulé en conséquence (hook nommé, avertissement rattaché à sa section, renvoi à la collecte). M3 et C05-02 traités comme deux lacunes distinctes.

### Instruction 6 — (Suivi) Reporter l'écart « jamais cinq » dans `docs/ecarts.md`
**Non appliquée — mais hors périmètre d'Hermès.**
- `docs/ecarts.md` ne contient aucune entrée sur le brief C-05 resté rédigé « jamais cinq », corrigé par l'arbitrage Option A du 22/11 (vérifié : seules les entrées 20/11 C-04 et 22/11 C-07 existent).
- C'est un item de suivi à la charge de **Claude (fuseur / clôture)**, pas d'Hermès : la doctrine §7 confie le report dans `docs/ecarts.md` à Claude, et `docs/` est hors de la surface d'écriture d'Hermès. Hermès le note explicitement (`production/C-05/corrections-22nov-1458.md:7`).
- Reste donc à faire au moment de la clôture du lot. Ce n'est pas un défaut de code.

---

## 2. Résultat des tests

**Non rejoués localement par le vérificateur**, pour les mêmes raisons que les deux relecteurs (PHP/Docker absents du PATH, runner via `wsl.exe` refusé en session, écriture dans `production/C-05/` interdite au relecteur). Un rejeu dans l'environnement de test autorisé reste nécessaire avant clôture.

Reçus archivés par Hermès (paquet `production/C-05/replays/fusion-22nov-1458/`), cohérents avec le code relu :
- PHPUnit `final.xml` : **746 tests / 33 077 assertions / 0 erreur / 0 échec / 0 skipped**. Suite **Echeancier : 384 tests / 2 307 assertions / 0 échec**. `final.json` : `composer test` exit 0, PSR-12 exit 0, syntaxe exit 0, `composer validate` exit 0.
- e2e réel (`final-e2e-result.json`) : Subscriptions 9.4.1, WooCommerce 11.1.1, WordPress 7.0.9, PHP 8.2.36 ; classique + HPOS. Les quatre exécutions : `failed: 0`, `error: null`, **aucun `pass: false`**. Checks clés présents et au vert : `equal_block_boundary_refused_before_orders`, `admin_anonymous_wp_die_translated`, `four_positions_cycle_1/2`, `option_a_anniversary_window` (4 ou 5 selon la commande).

Portée des reçus (rappel) : prototype à preuves synthétiques, pas de débit bancaire, pas d'emails, pas d'Odoo, réseau détaché.

---

## 3. Régressions et modifications non demandées

- **Aucune régression décelée** sur C-05. Les corrections se limitent aux fichiers visés (`Planificateur.php`, `ReglagesAdministration.php`, `phpunit.xml`, `tests/Echeancier/*`, proposition, sources, paquet de preuves). Les suites voisines (Numeros, Robots, Entreprise, Acces, Envoi) restent au vert dans le même `final.xml`.
- **Modifications hors périmètre C-05 présentes dans la fenêtre de diff** : `src/Envoi/AdministrationFormatExport.php` (nouveau), `src/Envoi/ExportCsv.php`, `tests/Envoi/*`, `wp/tests/envoi-runner/`. Elles appartiennent au **lot Envoi**, pas aux corrections C-05 ; elles ne touchent aucun fichier C-05 et n'ont aucun effet sur l'échéancier. Captées ici uniquement parce que le diff `f2f8e21→HEAD` couvre plusieurs synchros. À vérifier dans le cadre de leur propre lot, pas de C-05.
- Point d'attention mineur, non bloquant : la vérification inter-blocs replanifie récursivement toute la chaîne des années précédentes à chaque appel (`Planificateur.php:34-37`). Correct et sans faux refus (balayage 365 jours + e2e verts) ; simple coût théorique, acceptable pour un moteur pur appelé par bloc.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq corrections de code (C05-01, I1, M1, M2, M3+C05-02) sont appliquées et couvertes par des tests ; preuves archivées au vert, cohérentes avec le code relu. Aucun problème de fond restant, aucune régression sur C-05.

Deux réserves à porter à l'attention de Ced, non bloquantes pour un prototype :
1. **Item 6 encore à faire** : tracer dans `docs/ecarts.md` le brief C-05 « jamais cinq » corrigé par l'arbitrage du 22/11 — tâche du fuseur/clôture (Claude), pas d'Hermès.
2. **Rejeu indépendant** dans l'environnement de test autorisé non encore réalisé, et questions Q1 (marge SEPA du premier numéro) / Q2 (défaut après rejet) toujours ouvertes pour Ced / Imagine.

Rappel : ce verdict n'est pas un GO ; il ne vaut que pour la clôture du lot de code et appartient à Ced.
