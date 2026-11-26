# Vérification C-18 — Les extractions (2e et dernier tour)

Date : 26 novembre 2026. Vérificateur : Claude (2e tour).
Base : `corrections/C-18.md`, diff `b8a5d207..HEAD` sur `wp/` et `production/C-18`, reçus `production/C-18/corrections-V2/`.
Portée : contrôle de l'application des corrections, pas une relecture complète (celle-ci est dans `relectures/C-18/claude.md` et `codex.md`).

## 1. Application des trois instructions de corrections/C-18.md

### Instruction 1 — C18-02 (important) : découpler le filtrage d'état de la traduction. **Appliquée.**

- Nouvelle méthode `MonCompte::etatCle()` (`MonCompte.php:38`) : même projection B02 que `MonCompteRegles::etat()`, **avant** `__()`. `MonCompte::etat()` (`MonCompte.php:32-34`) ne fait plus que l'envelopper dans `__()`. La clé stable est donc exposée proprement.
- `ExtractionsNatives::lire()` porte désormais la **clé stable** pour le filtrage : `'etat' => MonCompte::etatCle($sub)` (`ExtractionsNatives.php:40`), au lieu du libellé traduit.
- `extractions/etat.php` : les options du filtre restent les chaînes stables (`'Actif'`, `'En délai de grâce'`, `'Suspendu'`, `'Expiré'`), désormais documentées comme clés non traduites (`etat.php:10-14`) ; la sélection compare `$row['etat'] === $f['etat']` (`etat.php:15`), clé stable contre clé stable.
- Traduction repoussée en **bordure d'affichage** : nouvelle `ExtractionsAdmin::affichage()` (`ExtractionsAdmin.php:105`) traduit la seule colonne `etat` ; l'aperçu et le CSV passent par elle (`ExtractionsAdmin.php:101`). `lire()` garde un contrat stable pour C19.
- **Test de raccord ajouté** : `testTranslatedDisplayDoesNotChangeNativeSelectionOrC19Totals` (`tests/ExtractionsNativesTest.php:23`). Un vrai filtre gettext `Actif → Active` est injecté ; les mêmes identifiants restent sélectionnés, la ligne garde la clé stable `Actif`, l'affichage rend `Active`, et le total C19 (`TableauBordRegles::calculer('actifs', …)`) reste à 1. Droits et règle d'état inchangés.

Le défaut technique visé par la fusion (sélection indépendante de la langue) est atteint.

### Instruction 2 — C18-03 (mineur) : éprouver la pagination native. **Appliquée.**

- Faux lecteur natif ajouté (`tests/fixtures/c18-faux-natif.php`) : `wcs_get_subscriptions()` sert les pages depuis `$GLOBALS['c18_pages']`, enregistre chaque requête et lève après 4 appels (anti-boucle).
- `testNativePaginationReachesSecondPageAndStops` (`tests/ExtractionsNativesTest.php:47`) avec jeu de données 100 puis 101 abonnements : la deuxième page est bien franchie (appels pages 1 et 2, `subscriptions_per_page = 100`), l'unique correspondance au filtre (ID 101) est en **deuxième page**, et la boucle s'arrête sur une page incomplète. Le test exerce `lire()` (boucle + rupture), pas un simple filtrage de tableau.
- Bonus : `testNativeBoundaryOverlapDoesNotDuplicateSubscription` (`:68`) couvre un chevauchement d'ID entre pages. Le correctif associé — `lire()` indexe désormais `$rows` par identifiant d'abonnement (`ExtractionsNatives.php:44`), puis `ExtractionsRegles::selectionner()` ré-indexe par `array_values` (`ExtractionsRegles.php:82`) — dédoublonne par abonnement, jamais par titulaire.

### Instruction 3 — C18-01 (mineur) : actualiser `A-VOIR.md`. **Appliquée.**

- Nouvelle **mise à jour datée du 26 novembre 2026** en tête (`production/C-18/A-VOIR.md:3-15`), renvoyant au reçu successeur `verification-successeur-20261126T012310784456-V2.json` et au `corrections-V2/final.json` : C09 natif **382/382**, code 0.
- La réserve historique est **conservée mais requalifiée** : titre « Résultat historique… » (`:28`), et section « Limites conservées » réécrite (`:84`) qui pose explicitement le 381/382 comme **état historique daté avant restauration**, « plus courant », et non comme limite présente. L'action 8793 pending (abonnement 101) est documentée comme préservée.

## 2. Résultat des tests

**Je n'ai pas pu ré-exécuter la suite moi-même.** Dans cette session non interactive, Docker, WSL et l'exécution de scripts/binaires (`rejouer.ps1`, `docker`, `wsl`, `php`) sont refusés (« approbation requise ») — même limite que Codex au 1er tour, qui avait été bloqué par WSL.

Contrôle de substitution effectué — **empreinte SHA-256 des fichiers sur disque confrontée au reçu `corrections-V2/final.json`** :

| Fichier | SHA-256 disque = reçu |
|---|---|
| `ExtractionsNatives.php` | ✅ `97e84ee2…` |
| `MonCompte.php` | ✅ `8ebf22bb…` |
| `extractions/etat.php` | ✅ `8d4b2768…` |
| `ExtractionsAdmin.php` | ✅ `daf3ed85…` |
| `tests/ExtractionsNativesTest.php` | ✅ `7f34299f…` |
| `tests/fixtures/c18-faux-natif.php` | ✅ `5c3454ec…` |
| `production/C-18/A-VOIR.md` | ✅ `884d1feb…` (reçu `readback-documentaire.json`) |

Le code en place est donc **octet pour octet** celui qu'Hermès a testé. Les reçus montrent une démarche **rouge→vert** sur deux images de conteneur distinctes :

- **Rouge** (image `34d7b325…`, ancien code + nouveaux tests) : `corrections-red-raccord.json` fait échouer le test de raccord (sélection vide sous traduction) ; `corrections-red-native.json` fait échouer les tests de pagination/chevauchement. Les tests prouvent donc bien le défaut.
- **Vert** (image `5405161e…`, code corrigé) : `corrections-green-etat.json` et `corrections-green-native.json` → **22 tests / 55 assertions, exit 0**.
- `unit-c18.json` : **22 / 55**. `unit-root.json` : **120 / 614**. `final.json` → suite **canonique : 1084 tests / 34362 assertions, 0 échec, 0 erreur, 0 ignoré, pass**. Aussi : 62 contrôles natifs/gettext/seam, 95 contrôles HTTP, neuf CSV rouverts, C09 natif 382/382.

Lecture : **tests au vert attestés par les reçus d'Hermès, corroborés par l'identité SHA-256 du code relu**, mais **non ré-exécutés indépendamment par moi** dans cette session. À ne pas traiter comme une double exécution.

## 3. Régressions ou modifications non demandées

- **Dans le périmètre C-18 : aucune.** Les seuls fichiers de code touchés sont ceux qu'exigent les instructions (`ExtractionsNatives`, `MonCompte`, `extractions/etat`, `ExtractionsAdmin`) plus les deux fichiers de test. `MonCompte::etatCle()` et `ExtractionsAdmin::affichage()` ne sont pas des ajouts gratuits : ce sont les mécanismes mêmes du découplage demandé.
- **Contrat C19 préservé.** En exécution FR sans traduction chargée, `etatCle()` rend la même valeur que l'ancien `etat()` (`'Actif'`, …) : aucun changement de comportement courant. Sous traduction, la nouvelle voie **corrige** le résultat au lieu de le fausser. `final.json` liste les sources C19 (TableauBord*, indicateurs) avec leurs empreintes sous `C19_read_only_sources_unchanged`, et le test de raccord vérifie le total C19.
- **Hors périmètre C-18.** Le diff `b8a5d207..HEAD` contient aussi des changements d'autres lots (C-17, C-19, C-20, bascule a16/a17). Ils ne relèvent pas de cette vérification et ne sont pas examinés ici.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les trois instructions de la fusion sont appliquées, proprement et au bon endroit ; les tests sont au vert selon des reçus rouge→vert dont j'ai vérifié qu'ils décrivent exactement le code en place ; aucune régression dans le périmètre C-18. **Aucun problème de fond ne subsiste** qui justifierait un « Remonte à Ced ».

Deux réserves demeurent — ce sont des portes de clôture, pas des défauts :
1. **Validation visuelle** de l'écran `Imagine → Extractions` : attendue de Ced (question visuelle déjà ouverte dans la fusion ; `visual_approval: false` dans les reçus). La clôture du lot y reste suspendue.
2. **Preuves de niveau site** (refus 403, ouverture des fichiers, téléchargements HTTP, journal in situ) toujours portées par le seul Hermès : aucun relecteur ni vérificateur ne les a reproduites par exécution indépendante.

Rappel doctrine : ce verdict n'est pas un GO ; il vaut pour la clôture d'un lot de code, sous réserve de la validation visuelle de Ced.
