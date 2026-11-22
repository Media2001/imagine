# Relecture C-05 — Paiement en quatre fois (Claude, relecteur indépendant)

Date : 22/11/2026. Relecteur : Claude Code (NUC). Brief : `briefs/C-05-echeancier-quatre-fois.md`.
Base lue : brief, cahier §3.4/§3.5, `docs/decisions.md`, `docs/arbitrages-2026-11-22.md`, cas R-02/R-16/R-17 (`docs/recette/cas.md`), code `wp/plugins/imagine-pilotage/src/Echeancier/` et `src/Numeros/`, banc `wp/tests/echeancier-runner/`, production `production/C-05/`.
`codex.md` existe mais **n'a pas été ouvert** (consigne). **Pas de fusion à ce stade** (consigne).

---

## 1. Conformité

- **Livrables demandés : tous présents.**
  - Échéancier PHP pur : `Planificateur` + `Versement`, s'appuyant sur `Numeros\Moteur` (C-01), sans rien recalculer. ✓
  - Note de conception `production/C-05/proposition.md` : compare deux voies (A cadence courte pilotée / B annuel + trois appels), chacune sur les cinq dimensions demandées (compte abonné, paiement échoué, reconduction, comptage d'engagement, Odoo), recommande A. ✓
  - Preuve sur vrai Subscriptions (banc jetable, renouvellement manuel, hors ligne) sur quatre dates de commande (≥ trois demandées). ✓
  - « Ce que tu ne décides pas » : marge, rejet/engagement, variation tarifaire — posés en réglages et questions. ✓

- **Écart brief ↔ décision (à signaler, pas un défaut du lot).** Le brief exige « toujours exactement quatre paiements par année d'engagement… jamais cinq ». Le lot applique l'**Option A** : quatre échéances **par bloc de quatre numéros**, donc une fenêtre de date à date peut contenir **cinq** dates. Cette réinterprétation n'est pas une invention : elle est tranchée par Ced le 22/11 (`decisions.md` ligne 30 ; `arbitrages-2026-11-22.md` §C-05), qui corrige expressément la formulation du 21/11 reprise par le brief. Doctrine §1 : la décision l'emporte sur le texte du brief. Hermès a suivi la décision **et** l'a signalé clairement (`proposition.md` §1, `reprise.md`). → Conforme. À reporter dans `docs/ecarts.md` : le brief C-05 est resté rédigé sur l'ancienne règle.

- **Interprétations signalées.** Le paramètre `finEngagement` est conservé « pour compatibilité positionnelle » et ne borne plus les paiements : signalé en clair (`Planificateur` l.19-23, README, proposition §3). Voir point mineur M1.

## 2. Exactitude métier (déroulé à la main)

Calendrier de test : clôtures les 10 jan/avr/juil/oct, sorties le 20, marge 7 → dates communes le 3.

- **R-02 — commande 2027-02-20 12:00 (milieu de trimestre).** C-01 attribue REG-2027-04/07/10 et REG-2028-01. Plan obtenu :
  - rang 1 (initial) REG-2027-04 à la commande, 2027-02-20 12:00 ;
  - rang 2 REG-2027-07 le 2027-07-03 ; rang 3 REG-2027-10 le 2027-10-03 ; rang 4 REG-2028-01 le 2028-01-03.
  Quatre échéances, une par numéro ; chaque échéance postérieure tombe 7 jours avant la clôture du numéro qu'elle paie. **Conforme** à la règle du brief et à R-02. ✓
- **R-16 — reconduction.** Bloc suivant = quatre numéros qui suivent le dernier (REG-2028-04/07/10, REG-2029-01), toutes dates communes (aucun second « initial »). **Conforme** à R-16 (« commencent au numéro qui suit son dernier numéro »). ✓
- **Bornes de clôture (veille/jour/lendemain : 2027-04-09/10/11).** `Moteur::numeros()` fait avancer le bloc dès que le numéro est clôturé ; l'initial est toujours le premier numéro encore ouvert, et sa date de commande précède toujours l'échéance 2. Dates strictement croissantes. ✓
- **Contre-exemple A-00 (cinq dates).** Commande 2027-04-09 : fenêtre [09/04/2027, 09/04/2028) contient cinq dates (09/04, 03/07, 03/10, 03/01, puis 03/04/2028 = première commune reconduite avant l'anniversaire). Chaque bloc garde quatre créances. 28 des 365 commandes quotidiennes sont dans ce cas. C'est exactement le cas que le brief demande de traiter ; sous Option A il est **accepté**, conformément à l'arbitrage. ✓
- **R-17 — avis avant prélèvement.** Non exercé (prototype non branché, aucun email). Les données nécessaires (date, numéro, rang, montant via `montantsRestants`) sont bien produites. Acceptable pour un lot de proposition ; à implémenter au branchement.

Cas limites couverts par les tests : calendrier incomplet → refus `CALENDRIER_INCOMPLET` ; clôtures égales → refus `DATES_NON_CROISSANTES` ; fin contractuelle ≤ début → refus ; DST et 29 février repris de C-01. ✓

## 3. Tests

- **Les tests n'ont pas été relancés par moi en local.** Raison : pas de PHP ni de Docker dans le PATH ; le runner officiel (`wp/tests/echeancier-runner/run.py`) passe par `wsl.exe -d Ubuntu -- docker` (approbation refusée en session) et **écrit dans `production/C-05/preuves/`** (surface interdite en écriture pour moi). Je le dis, comme le prévoit la grille.
- **À défaut, j'ai contrôlé les reçus livrés.** `reprise-final-unit.json` porte un manifeste sha256 des sources exercées ; j'ai recalculé les empreintes des 16 fichiers (`src/Echeancier`, `src/Numeros`, `tests/Echeancier/run.php`, banc) → **0 divergence, 0 manquant**. Les reçus **correspondent donc exactement au code relu** : 380 tests / 2 289 assertions / **0 échec**, `exit_code` 0, syntaxe 0 ; e2e `exit_code` 0.
- **Qualité des tests : bonne.** Dates attendues vérifiées contre des oracles indépendants (chaînes en dur pour R-02 ; `sprintf('2027-07-%02d', 10-marge)` pour la marge ; fenêtre recomptée à la main dans le test 365 jours). L'e2e assère réellement, sur vrai Subscriptions, que `next_payment` natif et l'action Action Scheduler tombent à la date C-01, l'idempotence (positionner deux fois → une seule action), et les gardes (initial non planifiable en renouvellement, abonnement automatique refusé, passerelle non vide refusée, non-fixture refusée). Couverture des cas limites réelle, pas seulement le nominal.
- **Important (I1) — les tests C-05 sont invisibles pour la commande du brief.** `tests/Echeancier/run.php` est un banc maison autonome, **pas** une classe PHPUnit, et **n'est pas** listé dans `phpunit.xml` (qui ne déclare que Numeros/Robots/Entreprise/Acces/Envoi). Conséquence : `docker compose run --rm -w /app/imagine-pilotage php composer test` (qui lance `phpunit`) **n'exécute aucun test C-05** et ressort au vert. Tous les lots voisins du même plugin utilisent PHPUnit. Voir « À corriger » ci-dessous.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Fixtures `@example.org`, noms manifestement inventés. ✓
- `ReglagesAdministration` : capacité `manage_woocommerce`, nonce via `settings_fields`, sorties échappées (`esc_html`/`esc_attr`/`esc_html__`), `show_in_rest => false`, filtre `option_page_capability_imagine_c05` correct, saisie invalide → ancienne option conservée, option corrompue → échec fermé à la lecture. ✓
- `RaccordManuel` : triple garde (drapeau manuel explicite + passerelle vide + méta `imagine_c05_fixture`). ✓
- **Non branché sur le site.** Le plugin n'a aucun fichier d'amorçage PHP ; `grep` → **zéro référence** aux classes Echeancier hors de leur dossier. Le seam `enregistrer()` est documentaire, activé seulement dans la fixture. ✓ Conforme à la doctrine (aucun GO réel, rien d'activé).
- Paywall : sans objet ici (aucun texte réservé dans ce lot).

## 5. Doctrine

- Logique métier hors WordPress (PHP pur, testable sans base). ✓ PHP 8.2, `strict_types`, namespace `Imagine\`, préfixe `imagine_`, libellés traduisibles. ✓
- Standard d'abord : la proposition examine bien le natif (périodes Woo, alignement de facturation qui ignore l'intervalle > 1 unité) avant de justifier le sur-mesure. ✓
- Une règle ouverte devient un réglage, défaut prudent (marge obligatoire sans défaut → moteur bloqué ; rejet « restent dues » ; tarif « figé par bloc »), chaque valeur testée. ✓ Conforme à l'arbitrage du 22/11.

## 6. Études

Huit sources officielles, HTTP 200, empreinte et extrait datés (`sources/review-2026-11-22.json`). Citations pertinentes et vérifiables par adresse. **Doute mineur (M3)** : l'extrait stocké pour la source [5] (alignement de facturation) est tronqué et ne montre pas littéralement l'exemple « 6 avril → 1er mai » cité dans la proposition ; l'URL reste joignable, donc acceptable.

---

## Points classés

**Important**

- **I1 — Tests C-05 hors de `composer test`/PHPUnit.** `tests/Echeancier/run.php` n'est pas une classe PHPUnit et n'est pas déclaré dans `wp/plugins/imagine-pilotage/phpunit.xml`. La commande de test du brief (`composer test` → `phpunit`) ne couvre donc rien du lot et ressort au vert à tort — risque de fausse confiance en CI, alors que les lots voisins sont tous en PHPUnit. *Correction proposée* : porter les cas unitaires en `tests/Echeancier/*Test.php` et ajouter la testsuite au `phpunit.xml`, en gardant le banc e2e (vrai Subscriptions) à part dans son runner dédié.

**Mineur**

- **M1 — `Planificateur::planifier($annee, DateTimeImmutable $finEngagement, …)`.** Le 2ᵉ paramètre est désormais vestigial (« compatibilité positionnelle ») : il ne sert qu'à une garde `≤ début` et ne borne plus les paiements. Pour du code neuf sans appelant externe, garder un paramètre trompeur est évitable. De plus il est typé non-nullable alors que la source prévue `Annee::finNumerique()` renvoie `?DateTimeImmutable` → `TypeError` latent si une année non activée est passée (cf. seam §6 de la proposition). *Correction proposée* : retirer le paramètre, ou le rendre nullable/validé et abandonner la formulation « compatibilité ».
- **M2 — `ReglagesAdministration::afficher()` lève `\LogicException`** sur capacité absente, au lieu de `wp_die()` (convention WordPress pour un refus d'accès). Une exception non rattrapée donne une page d'erreur fatale. *Correction proposée* : `wp_die()` avec message traduit.
- **M3 — Source [5] : extrait stocké tronqué** (voir §6). *Correction proposée* : capturer la phrase complète de l'exemple cité.

**À arbitrer par Ced (questions fermées)**

- Q1 — Pour l'abonnement en **quatre fois par domiciliation (SEPA, R-02)**, le premier numéro est payé à la commande, sans la marge appliquée aux échéances suivantes. Si la commande tombe juste avant la clôture du premier numéro, le prélèvement initial SEPA peut ne pas être confirmé avant cette clôture. **Faut-il appliquer aussi une marge de confirmation au premier numéro SEPA** (sinon risque d'envoi avant confirmation) ? (Frontière C-01/C-05/tunnel.)
- Q2 — Après un rejet en cours d'année, le défaut retenu est « les échéances restantes restent dues » ; les décisions 8 et 12 (sort de l'engagement et délai de grâce) restent ouvertes chez Imagine. **Confirmer le défaut prudent en attendant leur réponse ?**

---

## Verdict

**À corriger.**

- Fond métier **conforme** à la décision du 22/11, correctement signalé ; preuve sur vrai Subscriptions solide ; reçus au vert et liés au code relu par empreinte.
- Un point **important** (I1) à traiter avant clôture : rendre les tests C-05 exécutables par la commande standard. Trois points **mineurs** et deux questions pour Ced.

Ce verdict n'est pas un GO. Fusion avec `codex.md` non faite (consigne) : `codex.md` est présent mais je m'arrête à l'écriture de ce rapport.
