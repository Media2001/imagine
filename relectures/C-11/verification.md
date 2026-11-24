# Vérification C-11 — second et dernier tour

Vérificateur : Claude. Date : 24 novembre 2026.
Base : `corrections/C-11.md` (fusion, verdict « À corriger »).
Version relue → version corrigée : `git diff a9e980e..HEAD` sur `wp/` et `production/C-11/`
(a9e980e = commit où la fusion a été écrite ; HEAD = 471e84f).

Périmètre : je ne refais pas la relecture. Je vérifie que chaque instruction est appliquée,
je relance les tests reproductibles, je note les écarts.

---

## 1. Instructions de `corrections/C-11.md`

### Instruction 1 — Bloquant C11-01 (convergence du seed) : **Appliquée**

- La branche PDF du seed passe désormais les deux chemins publics exacts à `protect()` :
  `wp/outils/demo/b00-seed.php:85-87`.
- La migration fait pareil, l'`unlink` manuel a disparu :
  `wp/outils/demo/c11-migrate.php:21-23`.
- Nettoyage mutualisé en une seule routine `PdfNumero::removePublicCopies()`
  (`wp/plugins/imagine-site/PdfNumero.php:47-67`), appelée par `protect()`
  (`PdfNumero.php:140`). Elle supprime **et relit l'absence** ; une copie inattendue
  (répertoire, lien, hors racine, non supprimable) lève et ne vaut jamais réussite.
- Test de convergence réel ajouté : `wp/tests/demo/c11-seed-runtime.php:16-82` recrée
  un départ **public** sur le seul témoin T4 (deux copies, référence privée retirée),
  rejoue le seed deux fois, vérifie la suppression des copies et la stabilité des
  identifiants/octets privés (idempotence), puis restaure l'état privé.
- Résultat : `production/C-11/runtime.json` → `c11-seed-runtime` 7/7 à `true`
  (`depart_sans_reference_privee`, `passage_1/2_copies_supprimees`,
  `passage_1/2_ids_octets_prives_stables`, `restauration_privee_relue`).

### Instruction 2 — Important C11-02 (chemins portables) : **Appliquée**

- Comparaison de frontière canonique centralisée : `PdfNumero::withinDirectory()`
  (`PdfNumero.php:35-44`) — normalise les séparateurs (`\` → `/`), applique la casse
  selon l'OS, frontière explicite (`=== $directory` ou préfixe `$directory . '/'`).
- Utilisée pour **refuser** un stockage privé sous la racine publique
  (`directory()`, `PdfNumero.php:77`) et pour qualifier/**retirer** une source publique
  (`protect()`, `PdfNumero.php:137-140`). L'ancien `str_starts_with(... $public . '/')`
  à fail-open Windows est supprimé des deux endroits.
- Tests : `tests/PdfNumeroTest.php:27-47` déroule enfant / égal / frère / casse distincte,
  en Unix **et** Windows (volume `D:` inclus) ; verts.

### Instruction 3 — Important (couverture PHPUnit du contrôleur) : **Partiellement**

- Les tests existent et couvrent le vrai contrôleur : `tests/PdfNumeroTest.php`
  (36 tests — `serve` 404/405/GET/HEAD/302, `path`, `directory`, `block`, frontière
  canonique), via `phpunit.c11.xml` et le banc hors-ligne `wp/outils/demo/c11-unit.py`.
  L'objectif de fond — l'étanchéité du contrôleur n'est plus prouvée uniquement par
  `c11.py` contre la démo — est **atteint** : ces tests tournent dans un conteneur isolé,
  réseau coupé, sans toucher la démo.
- **Mais la lettre de l'instruction n'est pas tenue** : ces tests **n'entrent pas dans
  `rejouer.ps1`**. Hermès le déclare explicitement (README `imagine-site/README.md`,
  A-VOIR, PRET) : l'image T01 n'a pas de cache Composer `imagine-site`, donc les 812 tests
  de `rejouer.ps1` ne comprennent pas C-11 ; le repli est un runner dédié `c11-unit.py`,
  invoqué aussi par `c11.py`. Écart assumé et tracé, pas caché. Point à faire valider
  par Ced (cf. §4).

### Instruction 4 — Mineur (lien PDF) : **Appliquée**

- `wp/themes/imagine/single-imagine_numero.php:26` : le lien « Ouvrir le PDF… » ne
  s'affiche que si `Paywall::decisionPdf(get_post())['complet']` est vrai. Plus de lien
  de téléchargement sous un bloc « connectez-vous ». `decisionPdf()` est fermé par défaut
  sur exception (`Paywall.php:118-120`), donc l'appel direct dans le thème est sûr.

### Instruction 5 — Mineur (instant unique) : **Appliquée**

- `Paywall::decisionPdf()` réutilise l'instant de requête partagé :
  `Paywall.php:108` (`self::$requestInstant ??= …`), même mécanisme qu'`article`
  (`Paywall.php:52`), propriété `Paywall.php:18`. `runtime.json` →
  `instant_article_PDF_unique: true`.

---

## 2. Résultat des tests

- **PHPUnit C-11 — relancé par moi** : `python wp/outils/demo/c11-unit.py` →
  `OK (36 tests, 200 assertions)`, conteneur isolé (réseau `none`, rootfs read-only)
  supprimé et absence relue. **Reproduit indépendamment, vert.**
- **Recettes démo `c11.py`** (migration, seed-runtime, runtime, HTTP, défauts) :
  **non rejouées par moi** — elles exigent un accès au staging/base, interdit aux droits
  de relecture. Même limite commune qu'au premier tour (cf. `corrections/C-11.md` §1).
  Je m'appuie sur les preuves rapportées par Hermès :
  - `runtime.json` : `c11-seed-runtime` 7/7, `c11-runtime` 25/25, `local_unit` 33/33,
    `shared_C12_C13_preserved: true`, `phpunit` 36/200 — tous `true`.
  - `faults.json` : 8/8 à `true` (corrompu/absent/traversée fermés sans octets).
  - `http.json` : 94 contrôles booléens, **0 faux** (vérifié en scannant le fichier).
  - `PRET` : PHPUnit 36/200, seed 7/7, natif 25/25, HTTP 94/94, défauts 8/8,
    Python 33/33, T01 812/33434.

---

## 3. Régressions / modifications non demandées

- **Aucune régression C-11 détectée.** Les cinq fichiers C-11 corrigés sont propres au
  commit (pas de diff de travail en attente) et les corrections sont intactes.
- **Travail hors périmètre C-11 présent dans le même arbre** (lots C-12 / C-13) :
  `EnvoiNatif.php`, `ListeEnvoiAdmin.php` et leur enregistrement
  (`imagine-site.php:49-50`), plus `c12-seed.php`, `c13.py`, `c13-fixture.php`,
  `tests-c12/`. Ce n'est pas demandé par `corrections/C-11.md`, mais **cela ne dégrade
  pas C-11** : `c11.py` a été resserré pour ne plus réécrire les fichiers partagés
  (liste `FILES` réduite, `imagine-site.php` passé en lecture seule `SHARED`) et vérifie
  activement la préservation de l'état C-12/C-13 (`shared_C12_C13_preserved: true`).
  À signaler seulement : la clôture de C-11 ne vaut pas clôture de C-12/C-13.
- Détail mineur sans impact : le thème appelle `block()` puis `decisionPdf()`
  (`single-imagine_numero.php:25-26`), soit deux calculs de décision ; l'instant partagé
  les rend cohérents. Pas une régression.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les deux défauts qui motivaient le « À corriger » sont réellement réparés et couverts par
des tests verts que j'ai reproduits (PHPUnit C-11, 36/200) :
le bloquant C11-01 (convergence du seed depuis un départ public, idempotence) et
l'important C11-02 (frontière de chemin canonique, fin du fail-open Windows). Les deux
mineurs sont faits. Aucun **problème de fond** ne subsiste.

Deux points d'attention, non bloquants, déjà déclarés par Hermès — à acter par Ced :

1. **Instruction 3 partielle** : les tests PHPUnit du contrôleur n'entrent pas dans
   `rejouer.ps1` (limite d'image T01, cache Composer absent). Repli assumé via
   `c11-unit.py`. Question fermée : ce runner dédié est-il accepté, ou faut-il intégrer
   C-11 à `rejouer.ps1` ? **Accepté / À intégrer.**
2. **Preuve HTTP non reproduite** par le vérificateur (droits de relecture) : `c11.py`,
   `http.json`/`runtime.json`/`faults.json` sont rapportés, pas rejoués ici. Même limite
   qu'au premier tour. À rejouer par Ced sur le staging s'il veut la preuve de première
   main.

Restent ouvertes les trois questions « À arbitrer par Ced » de `corrections/C-11.md` §5
(politique robot/extrait, achat à l'unité, cible d'hébergement Windows/Linux). Elles
relèvent du métier, pas de la correction.

Rappel : un verdict de vérification n'est pas un GO.
