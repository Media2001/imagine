# Vérification — A-24 (2e et dernier tour)

Vérificateur : Claude. Date : 2026-11-26. Objet : contrôler l'application de
`corrections/A-24.md` par Hermès, relancer les tests, relever régressions et
modifications non demandées, donner un verdict. Pas de relecture complète refaite.

**Base de comparaison.** Les corrections ont été écrites au commit `d6169775`
(20:08, juste après les deux relectures, code non modifié entre-temps). Diff pris de
`d6169775` à HEAD sur `wp/outils/bascule/a24/`, `wp/tests/a24/` et `production/A-24/`.
Deux phases Hermès : un « réveil correctif » (≈21:38, `corrections-reveil.md`) qui
diffère la matrice native au parent, puis une « qualification finale déléguée »
(22:56, `FINALISATION.md`) qui rejoue réellement la matrice native et régénère le
paquet. Ce point explique une incohérence documentaire (§3).

---

## 1. Application des sept instructions

**1 — Corriger P1 (comparaison casse/espaces insensible). Appliquée.**
`wp/outils/bascule/a24/Analysis.php:15-25` : nouvelle méthode `sameAddressValue()` qui
supprime tout caractère d'espacement Unicode (`[\p{Z}\s]+`) puis compare en casse
simple Unicode via PCRE `/iu` (sans mbstring/intl). Utilisée uniquement à la
comparaison `Analysis.php:42-45`. La complétude (`trim`), `shipping_empty`, le pays et
le regroupement restent sur la valeur brute (vérifié : la ligne `$empty` et le test
`comparison_does_not_normalise_raw_completeness_or_country` le prouvent). Normalisation
en mémoire, aucune écriture, aucun nettoyage d'adresse. Conforme.

**2 — Corriger l'oracle, pur ET natif. Appliquée.**
Pur : `wp/tests/a24/unit.php:44-80` remplace `literal_case_and_space_comparison` par
`case_and_space_only_rows_are_not_different` (=0) plus huit cas nommés — casse seule,
espace seul, espace Unicode → 0 divergence ; rue/CP réellement autres, accent,
ponctuation, « 0 » → 1 divergence. Chaque cas contrôle `overall` ET le compte par pays,
et vérifie la non-mutation de l'entrée (`$case === $snapshot`). Natif :
`wp/tests/a24/standard.php:34-57` ajoute `native_comparison_{case_only_ignored,
space_only_ignored, actual_postcode_difference_counted}` sur les valeurs relues des
getters natifs, classique et HPOS, en prouvant que la fixture diffère réellement avant
comparaison. Noms rendus obligatoires par `inside.py:56-60` et `verify.py:57-59,93,117`.
Conforme.

**3 — Compléter le banc (différence réelle de contenu). Appliquée.**
`wp/tests/a24/seed.php:55-57` : l'abonnement i3 porte le code postal `1001` alors que le
compte garde `1000`. La métrique `different_from_account` reste donc exercée en positif
après correction (=1). Conforme.

**4 — Régénérer le paquet unique de preuves. Appliquée.**
Le paquet `production/A-24/preuves/final/` a été régénéré par un rejeu natif réel
(`matrix.json` : suite `A24-final-replay`, `native_exit=0`, `python_exit=0` dans les deux
encodages, `sources_stable=true`, `dependencies_stable=true`). `expedition.json`
(classique et HPOS, utf8 et cp1252) passe `different_from_account` de 2 à **1** (overall
et groupe BE), avec un nouvel `audit_sha256`. Ajout des reçus `classic-standard.json` /
`hpos-standard.json` portant les trois `native_comparison_*` à PASS ; `result.json`
passe à 212 contrôles natifs (206 + 6). Preuves non forgées : `verify.py` recalcule les
empreintes sources/dépendances et exige les nouveaux contrôles. Conforme.

**5 — Réaligner le SHA (M1). Appliquée.**
L'empreinte figée `ce62d8…db9` est **absente** de tout `production/A-24/` (grep : aucun
match). `RAPPORT.md` renvoie désormais aux `dependencies.json` scellés, qui portent
`c913c79206b6e7b54b8ecb42284952bf5a82d2d9075639f98eddf5479efade97` (utf8 et cp1252,
vérifié). Conforme.

**6 — Lever I2 (rejeu Python sous Windows). Appliquée.**
Traité comme environnemental et documenté : `README.md` ajoute « Prérequis des fixtures
Python sous Windows » (scratch hors dépôt, `TMPDIR/TMP/TEMP` dirigés, droits
création/lecture/renommage/suppression). Le rejeu natif a passé **15 tests Python au
vert dans chaque encodage** (`matrix.json`, `python_tests=15`, `run.py` `native_exit=0` :
Docker disponible ici, contrairement à l'environnement de Codex). Les six `WinError 5`
ne sont pas reproduits sous ce prérequis. Conforme.

**7 — Phrase de portée (M3). Appliquée.**
`README.md` (paragraphe « Portée »), `RAPPORT.md` et `FINALISATION.md` indiquent que,
pour A-24, `rejouer.ps1` ne rejoue que l'unité PHP pure ; le natif (206/212 contrôles),
le confinement et le Python ne sont attestés que par la matrice scellée. Conforme.

## 2. Résultat des tests

- **Rejeu autorisé (sans argument), relancé par moi :**
  `REJEU : 1149 tests, 36036 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS` ;
  `OUTILS : 18 outils, 417 contrôles, 0 échecs ; hors rejeu : aucun`. Ligne A-24 :
  `a24 ; 27 controls ; 0 failures ; exit=0` (était 17 avant correction → les 10 nouveaux
  contrôles de comparaison sont bien exécutés et verts). Isolement confirmé
  (`network=none ; rootfs=ro ; mount=…/wp:ro ; cap-drop=ALL ; no-new-privileges`).
- **Matrice native scellée** (`result.json`, `*-standard.json`, les deux encodages) :
  `native_comparison_case_only_ignored`, `native_comparison_space_only_ignored`,
  `native_comparison_actual_postcode_difference_counted` à **PASS** en classique et HPOS.
- **Réserve de méthode :** `verify.py --require-shared` n'a **pas** pu être relancé
  indépendamment dans cette session (non-interactive : approbation requise impossible à
  accorder, Python hors liste). Je m'appuie donc, pour le natif/Python, sur le rejeu
  autorisé au vert et sur la matrice scellée régénérée. Codex avait obtenu `verify.py
  --require-shared` = code 0 au tour précédent.

## 3. Régressions et modifications non demandées

- **Aucune régression métier.** Les attentes dépendantes du compteur ont suivi la
  correction : `extended.py` attend maintenant `different_from_account=1` (overall et BE),
  `matrix.py` exige `python_tests>=15`, `test_verify.py` ajoute un test des reçus de
  comparaison. Cohérent, pas de régression.
- **Nettoyages de style non demandés (cosmétiques, sans effet) :** découpe de lignes
  PSR-12 dans `guards.php`, `neutralise.php`, `standard.php`, `seed.php` ; dans
  `unit.php`, le helper global `a24_check()` est devenu une fermeture `$check`. Signalés
  par Hermès (`notes.md`, « wrapper isolé, fermeture locale du helper »). Pas un défaut ;
  tests au vert.
- **Incohérence documentaire à réconcilier (point principal).** `RAPPORT.md` (en-tête de
  livraison, écrit à 21:38, phase « réveil correctif ») et le paragraphe « Portée » du
  `README.md` décrivent encore l'état *intermédiaire* : « matrice native à rejouer par le
  parent », « aucune matrice native ni reseal lancés par l'enfant », ancien paquet « ne
  prouve plus les sources corrigées », pas de PRET. Or la « qualification finale » de
  22:56 (`FINALISATION.md`, en-tête de `notes.md`, `PRET` redéposé à 22:56:55, paquet
  `preuves/final/` régénéré) a **bien** rejoué la matrice native au vert. Un lecteur du
  seul `RAPPORT.md` conclurait à tort que la preuve native reste en attente. C'est une
  contradiction de narration, pas un défaut de code, de métier ni de preuve : les chiffres
  et les reçus, eux, sont corrects et à jour.
- Hors périmètre A-24 : un fichier parasite `prefix}u0024s` traîne à la racine du dépôt
  (non suivi). Sans rapport avec ce lot ; simplement signalé.

## 4. Verdict

**Prêt pour la validation de Ced — sous réserve documentaire.**

Les sept instructions de `corrections/A-24.md` sont **appliquées** et prouvées de façon
indépendante : rejeu autorisé au vert (A-24 = 27 contrôles, 0 échec), matrice native
régénérée avec les contrôles de comparaison PASS (classique + HPOS, utf8 + cp1252), P1
corrigé en mémoire sans toucher aux données brutes, oracles pur et natif repris, banc
complété d'une vraie divergence, `different_from_account` ramené à 1, SHA réaligné,
portée et prérequis Windows documentés. **Aucun problème de fond ne subsiste** (code,
métier, étanchéité, preuves). Aucune question ouverte pour Ced ni Imagine.

La seule réserve est documentaire : `RAPPORT.md` et le paragraphe « Portée » du
`README.md` n'ont pas été rafraîchis après la finalisation de 22:56 et contredisent
l'état réel (matrice native rejouée, paquet régénéré, PRET déposé). À corriger avant
clôture pour ne pas induire la validation en erreur — simple mise à jour de rapport, pas
une reprise du code. Ce verdict de vérification n'est pas un GO ; la clôture reste à Ced.
