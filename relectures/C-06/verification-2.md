# Vérification C-06 — tour complémentaire après la reprise du 22/11

Date : 22/11/2026. Vérificateur : Claude Code (NUC).
Objet : contrôler que la reprise d'Hermès du 22/11 applique les arbitrages
`docs/arbitrages-2026-11-22.md` (section C-06), rejouer les tests si possible,
repérer toute régression, trancher le verdict. **Ce n'est pas une relecture
complète** : seuls les écarts depuis la vérification du 21/11
(`relectures/C-06/verification.md`) sont examinés.

Consigne qui déclenche la reprise : A-FAIRE (22/11, 17 h) renvoie C-06 à sa
« vérification complémentaire » ; la doctrine révisée le 22/11 (« une règle
ouverte devient un réglage ») et l'arbitrage `arbitrages-2026-11-22.md` §C-06
justifient les modifications. La reprise est décrite dans
`production/C-06/notes-22nov.md`.

Méthode : `git diff 77159fa..0ab13f1` sur `wp/` et `production/C-06`
(`77159fa` = fin de la remise corrective du 21/11 ; `0ab13f1` = dernier état).
Concordance SHA-256 entre l'arbre de travail et le sceau du 22/11
(`production/C-06/replays/reglages-22nov/final.json` et `artifact-verification.json`).

---

## 1. Application des arbitrages du 22/11 (section C-06)

Principe directeur : **une règle ouverte devient un réglage, défaut prudent
(fermé en cas de doute), chaque position testée** (doctrine §4, arbitrage §C-06).
Les trois réglages sont isolés dans un seul objet `Acces\Reglages` (final
readonly, trois booléens à `false`, `wp/plugins/imagine-pilotage/src/Acces/Reglages.php:9-13`),
passé en sixième argument de `Moteur::decider`.

### Arbitrage 1 — Contenu à sortie future → réglage, défaut « Fermé pour tous », autre « Ouvert à l'équipe » → **Appliqué**

- La sortie future n'est plus un `entree_invalide` : la condition
  `$contenu['sortie'] > $instant` est sortie de la validation (`Moteur.php:50`,
  ligne supprimée) et traitée dans un bloc dédié `Moteur.php:67-73`.
- Défaut prudent « fermé pour tous » : `Reglages.php:11` `contenuFuturEquipe = false`
  → `Decision(false, ContenuFuturFermeParReglage, Abonnement)` (`Moteur.php:71`).
  Le bloc est **avant** l'ouverture du contenu libre et avant le robot : équipe
  **et** robots compris, conforme à l'arbitrage.
- Position « ouvert à l'équipe » : seuls les droits `equipe` identifiés ouvrent
  (`Moteur.php:68-70`, motif `ContenuFuturEquipeParReglage`).
- Adaptateur : champ `contenu_futur` (`AdministrationReglages.php:113-119`), libellé
  par défaut « Fermé pour tous, équipe et robots compris (défaut) ».
- Tests deux positions : `ReglagesTest::testSortieFutureDeuxPositionsNeBeneficientQuaEquipeValide`
  (`tests/Acces/ReglagesTest.php:36-72`) ; priorité + borne à la seconde :
  `testSortieFuturePrioritaireDansLesHuitCombinaisonsEtBorneAUneSeconde:155-188`.

### Arbitrage 2 — PDF robot vérifié → réglage, défaut « Extrait », autre « Complet » → **Appliqué**

- Robot vérifié : accès complet uniquement si article, ou si PDF **et** position
  complète (`Moteur.php:76`, `$contenu['type'] !== 'pdf' || $reglages->pdfRobotComplet`).
  Sinon le robot passe en extrait (`Moteur.php:85-88`, motif `PdfRobotExtraitParReglage`).
- Défaut prudent : `Reglages.php:10` `pdfRobotComplet = false` → PDF robot en extrait,
  article robot toujours complet.
- Adaptateur : champ `pdf_robot` (`AdministrationReglages.php:120-126`).
- Tests deux positions : `ReglagesTest::testPdfRobotDeuxPositionsEtFauxRobotNeRecoitPasDeDroit:15-34`
  et `testPdfRobotEstExtraitParDefautSansFermerLesArticles:190-214` (google/bing,
  DNS et plage).

### Arbitrage 3 — PDF antérieur au début d'abonnement → réglage, défaut « Fermé », autre « Ouvert » → **Appliqué**

- `Moteur::abonnement` : PDF antérieur fermé sur ce seul droit, sauf si position
  ouverte (`Moteur.php:118-124`, `&& !$reglages->pdfAnterieurAbonnement`).
- Défaut prudent : `Reglages.php:12` `pdfAnterieurAbonnement = false`.
- Adaptateur : champ `pdf_anterieur_abonnement` (`AdministrationReglages.php:127-133`).
- Tests deux positions, trois familles d'abonnement, cinq états, quatre bornes de
  date : `ReglagesTest::testPdfAnterieurDeuxPositionsRespectentDatesEtEtatsDesTroisAbonnements:74-108`.

### Arbitrage 4 — Motif provisoire `PdfAnterieurAArbitrer` remplacé par un motif définitif nommant le réglage → **Appliqué**

- `Motif.php` : `PdfAnterieurAArbitrer` supprimé, remplacé par
  `PdfAnterieurFermeParReglage = 'pdf_anterieur_ferme_par_reglage'` (`Motif.php:25`) ;
  ajout de `ContenuFuturFermeParReglage`, `ContenuFuturEquipeParReglage`,
  `PdfRobotExtraitParReglage` (`Motif.php:11-14`). `priorite()` mis à jour
  (`Moteur.php:208-209`, refus au même rang 26, n'élargit aucun accès).
- `AbonnementTest` : assertion mise à jour vers `pdf_anterieur_ferme_par_reglage`
  (`tests/Acces/AbonnementTest.php:104`) ; garde anti-retour dans `verify.py:66`
  (`'PdfAnterieurAArbitrer' not in code`).

### Effet sur les questions laissées ouvertes au 21/11 → **traitées**

Les trois interprétations que la vérification du 21/11 renvoyait à Ced (§5,
« Rappels pour la validation ») — sortie future fermée pour tous, robot+PDF,
PDF ancien — ne sont plus des questions pendantes : elles deviennent les trois
réglages ci-dessus, conformément au principe du 22/11. La valeur par défaut
conserve exactement le comportement du 21/11, donc aucune régression de sens.

### Réglage obligatoire avec défaut prudent → conforme doctrine §4

- Sixième argument `null`/omis = trois défauts prudents (`Moteur.php:33`,
  `$reglages ??= new Reglages()`). Tout autre type ferme l'entrée
  (`Moteur.php:39`, `!$reglages instanceof Reglages`), testé dans
  `ReglagesTest::testValidationPrecedeMemeLesTroisReglagesOuverts:127-153`.
- Toute l'entrée reste validée **avant** le moindre accès favorable (inchangé).

---

## 2. Résultat des tests

**Je n'ai pas pu rejouer PHPUnit dans cet environnement** : docker, php et python
sont refusés par le bac à sable de cette session (plusieurs tentatives bloquées),
même situation qu'aux deux tours précédents. La vérification repose donc sur la
concordance d'empreintes avec le sceau du 22/11, **pas** sur un rejeu indépendant.

Concordance SHA-256 — arbre de travail actuel vs `final.json` du paquet
`replays/reglages-22nov/` — **identique** sur les fichiers C-06 modifiés/ajoutés
que j'ai recalculés :

| Fichier | État |
|---|---|
| `src/Acces/Moteur.php` | ✓ `a8167e1d…` |
| `src/Acces/Motif.php` | ✓ `e121c29d…` |
| `src/Acces/Reglages.php` (ajout) | ✓ `3e106616…` |
| `src/Acces/AdministrationReglages.php` (ajout) | ✓ `14753c28…` |
| `tests/Acces/ReglagesTest.php` (ajout) | ✓ `1e1a2920…` |
| `tests/Acces/AdministrationReglagesTest.php` (ajout) | ✓ `eb9cf48f…` |
| `tests/Acces/OptionsReglagesTest.php` (ajout) | ✓ `4af63dbd…` |
| `tests/Acces/WordPressFictif.php` (ajout) | ✓ `0ade1d8e…` |
| `tests/Acces/AbonnementTest.php` | ✓ `a6f432c9…` |
| `tests/Acces/FermetureTest.php` | ✓ `c61931ec…` |

Le sceau correspond donc exactement au code présent.

Résultat scellé (`final.json`, `final.xml`, `artifact-verification.json`) :

- **247 tests / 30 368 assertions**, dont **Acces 63 / 10 388** ; Numeros 42,
  Robots 101, Entreprise 41 (63+42+101+41 = 247, cohérent).
- 0 échec, 0 erreur, 0 ignoré ; `exit_code = 0`. PSR-12 `0`, syntaxe `0`,
  `composer validate --strict` `0`.
- PHP 8.2.36, PHPUnit 11.5.58, conteneur jetable, réseau détaché, absence du
  conteneur vérifiée après coup.
- Tranches TDD rouge-puis-vert présentes et scellées (`red-robot-default`,
  `red-robot-setting`, `red-robot-value`, `red-future`, `red-old-pdf`,
  `red-coexistence`, `red-options`, `red-admin`, puis les `green-*`).
- Rejeu indépendant scellé `replays/rejeu-reglages-22nov/final.*` : même 247 / 30 368.
- Garde de couverture `check-standard-suite.py` : commande bornée acceptée **et**
  `Acces >= 63` exigé ; `verify.py` exige la présence de `ReglagesTest`,
  `OptionsReglagesTest`, `AdministrationReglagesTest` dans le JUnit.

Limite assumée : résultat vérifié par concordance d'empreintes, non par un rejeu
frais de ma part. Un dernier rejeu en environnement autorisé reste souhaitable.

---

## 3. Régressions ou modifications non demandées

**Dans le périmètre C-06 — aucune régression.**

- `Moteur.php` : seules les branches des trois réglages sont ajoutées. La
  validation avant tout accès est préservée ; le départage « le plus favorable
  l'emporte » est préservé et testé (`ReglagesTest::testRobotFermeNeRetirePasUnAchatOuUnDroitEquipeOuAbonnementValide:110-125`).
  Les réglages PDF agissent comme des limites, **pas comme un veto** retirant un
  autre droit favorable. Aucune autre règle métier modifiée.
- `FermetureTest.php:168-180` : un sous-cas a été retiré (contenu futur + achat,
  qui renvoyait `entree_invalide`). C'est la conséquence directe de l'arbitrage 1
  (la sortie future n'est plus `entree_invalide` mais `contenu_futur_*`) ; le
  comportement « fermé » est désormais couvert, plus largement, par `ReglagesTest`.
  Pas une perte de couverture.
- `AbonnementTest.php` : renommage + valeur de motif mise à jour. Légitime.

**Hors périmètre C-06 — présent dans le même diff, non évalué ici.**

- Le diff `77159fa..0ab13f1` contient aussi des fichiers **C-05 (`src/Echeancier/`)**
  et **C-07 (`src/Envoi/`, `tests/Envoi/`)**. Ils relèvent de la vérification de
  ces lots, pas de C-06.
- `phpunit.xml` racine : une suite `Envoi` a été ajoutée (`phpunit.xml:8`). C'est
  une modification **du lot C-07**, pas de C-06. La ligne `Acces` (correction du
  21/11) est conservée.

**Point d'attention — composition de la preuve C-06.**

Le paquet C-06 du 22/11 est joué via `composer test -- --configuration
tests/Acces/phpunit.xml`, c'est-à-dire par la configuration propre à Acces
(sur-ensemble Acces + trois suites closes), et **non** par le `composer test`
racine standard. Justification d'Hermès (notes §« Composition bornée volontaire »,
run.py:58-61) : le XML racine inclut désormais `Envoi`, lot non clos, qu'il serait
incorrect de certifier dans la preuve C-06 ; Echeancier et Envoi sont exclus de
l'inventaire (`run.py`, `verify.py:46-47`). L'intention de la correction du 21/11
(Acces présent dans le XML racine) est préservée : un `composer test` standard
exécute toujours Acces. Ce choix est cohérent avec la doctrine (ne pas certifier
un lot non clos) ; je le signale sans le considérer comme une régression C-06.

**Point à corriger avant clôture — README du plugin périmé (doctrine §5).**

`wp/plugins/imagine-pilotage/README.md` (section C-06, lignes ~241-245) décrit
encore les trois comportements comme des **« questions non tranchées »** codées en
dur (« une sortie future est refusée pour tous ; un robot vérifié ouvre aussi un
PDF déjà paru ; le PDF ancien reste refusé au seul titre de l'abonnement »). Il ne
documente ni les trois réglages, ni le sixième argument, ni `AdministrationReglages`.
Hermès l'a volontairement laissé de côté : le README est un fichier partagé
**interdit au worker**, sa mise à jour revient au parent (notes-22nov,
« README partagé à actualiser par le parent »). C'est une tâche de clôture, pas un
problème de fond du code.

**Seam WordPress.** `AdministrationReglages.php` est une couche fine Settings API
(capacité `manage_options`, i18n, échappement, pas de gestionnaire POST maison —
nonce/CSRF/persistance délégués à `options.php`, normalisation déléguée à `Reglages`
pur). Exemptée à juste titre du garde « PHP pur » (`verify.py:60-65`), conforme
doctrine §4. Testée par doubles (`WordPressFictif`), pas par intégration WordPress
réelle ; branchement du bootstrap laissé au parent. Aucun secret, compte ou donnée
réelle. Aucun site démarré.

---

## 4. Verdict

**Prêt pour la clôture.**

Les quatre points de l'arbitrage `docs/arbitrages-2026-11-22.md` §C-06 sont
**tous appliqués** et testés dans les deux positions, avec défauts prudents
conformes à la doctrine §4 ; le motif provisoire a disparu du code métier ; les
preuves scellées (247 / 30 368, Acces 63) concordent au bit près avec le code
actuel ; aucune régression ni modification non demandée **dans le périmètre C-06**.
Les trois questions que le tour du 21/11 renvoyait à Ced sont désormais des
réglages : **aucune question métier ouverte ne subsiste dans le lot**, donc rien
qui justifie un retour à Ced sur le fond.

Tâches de clôture restant **au parent/Claude** (un verdict n'est jamais un GO) :

1. Actualiser `wp/plugins/imagine-pilotage/README.md` (section C-06) : documenter
   les trois réglages, le sixième argument et `AdministrationReglages` ; retirer la
   formulation « questions non tranchées » devenue fausse (doctrine §5).
2. Coordonner le branchement du bootstrap partagé (`brancher()` / `lire()`), non
   réalisé par le worker.
3. Rejeu indépendant de la suite complète en environnement autorisé : la preuve
   reste vérifiée par concordance d'empreintes, pas par un rejeu de ma part
   (docker/php/python refusés dans cette session).

Les lots C-05 (Echeancier) et C-07 (Envoi) présents dans le même diff ont leur
propre vérification et ne sont pas couverts ici.
