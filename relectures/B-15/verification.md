# Vérification B-15 — second et dernier tour

Vérificateur : Claude. Date : 2026-11-28.
Base : `corrections/B-15.md` (fusion du 27/11), relecture d'origine `relectures/B-15/claude.md`.
Méthode : `git diff` de l'état relu (commit des corrections `63a11841`) jusqu'à `HEAD`, sur `wp/` et `production/B-15/`, plus lecture du code. Pas de relecture complète refaite.

> Périmètre du diff : côté B-15, seuls trois fichiers de test changent (`PiedPageB15Fixture.php` nouveau, `PiedPageB15Test.php`, `b15-runtime.php`) ; `PiedPage.php` est **inchangé**. Le reste des changements `wp/` (B-16, C-30, C-31) relève d'autres lots menés en parallèle, hors de cette vérification (voir §3).

## 1. Instructions de `corrections/B-15.md`, une par une

### Instruction 1 — Prouver la réutilisation du cache, pas le déterminisme ; résister au mutant ; compléter le test PHPUnit tautologique
**Appliquée** (même au-delà du minimum demandé).

- `wp/tests/demo/b15-runtime.php:19-28` : compteur de construction branché sur `post_thumbnail_html` (`$builds`). Assertions renforcées — `numero_cache_construit` exige `$builds === 1`, `numero_cache_reutilise` exige encore `$builds === 1`, et un nouveau cas `numero_cache_reconstruit_apres_invalidation` exige `$builds === 2` après `invalider()`. C'est l'option (b) de la fusion (compter les passages de construction).
- `wp/plugins/imagine-site/tests/PiedPageB15Test.php:17-45` : nouveau test `testVraiRenduEtCachePuisMutationDuRetourAnticipe` (`#[RunInSeparateProcess]`, `#[PreserveGlobalState(false)]`) qui :
  - exécute un **vrai** `PiedPage::rendre()` et vérifie l'ordre des cinq zones lu dans la sortie réelle (`data-b15-zone`) et la présence du titre — comble le test tautologique `testOrdreDesCinqZonesEstUtiliseParLeRendu` ;
  - modifie `Accueil::$title` **sans** invalider, vérifie que `numero()` renvoie encore le HTML en cache et que `$builds` reste à 1 — c'est l'option (a) de la fusion ;
  - invalide, vérifie le nouveau HTML et `$builds === 2` ;
  - reconstruit un **mutant** (`PiedPageB15Mutant`) en supprimant `return $cached;` par `str_replace` + `eval`, et vérifie qu'une construction a alors lieu malgré un cache présent — la preuve devient donc fausse si le retour anticipé disparaît (résistance au mutant explicitement demandée).
- `wp/plugins/imagine-site/tests/PiedPageB15Fixture.php` (nouveau) : stubs WordPress en espace de noms `Imagine\Site` + `Accueil::$builds` ; fournit tout ce qu'appellent `rendre()` et `numero()`. Isolement process correct pour éviter les redéclarations.

Les deux angles (runtime + PHPUnit) couvrent désormais construction / réutilisation / reconstruction ; le trou précis signalé par Codex (`b15-runtime.php:22` d'origine) est fermé.

### Instruction 2 — Invalidation trop large (`PiedPage.php:16`) — défaut : garder tel quel
**Appliquée (défaut conservé, conforme à la consigne).** `PiedPage.php:16` est inchangé (diff vide sur le fichier) : les hooks `save_post_attachment`, `added_post_meta`, `updated_post_meta`, `deleted_post_meta`, `deleted_post` restent branchés. La fusion demandait explicitement de « garder tel quel » (correction sans risque), arbitrage ultérieur de Claude. Rien à corriger ici.

### Instruction 3 — Résolution d'URL hétérogène (`PiedPage.php:86,91`) — défaut : conserver
**Appliquée (défaut conservé, conforme à la consigne).** `PiedPage.php:86` (`/nos-newsletters/`) et `:91` (`/points-de-vente/`) restent des slugs en dur via `home_url`, non alignés sur `get_page_by_path`. La fusion demandait de « conserver » (conforme au brief, « un lien suffit »). Rien à corriger.

### Instruction 4 — Rafraîchir le comptage dans `A-VOIR.md` (viser 1209 / 36693)
**Appliquée en esprit, adaptée sur le chiffre.** `production/B-15/A-VOIR.md:27` ne porte plus l'ancien « 1208 / 36685 » : il affiche désormais « 1214 tests / 36717 assertions PASS », avec la justification que « 1209/36693 était celui du rejeu de relecture du 27/11 ; la file a gagné B16/C30 depuis ». Le réflexe demandé — retirer le chiffre périmé et donner un comptage frais explicable — est tenu. Réserve : le chiffre littéral de la consigne (1209/36693) n'est pas celui écrit, et je n'ai **pas** pu reproduire 1214/36717 moi-même (voir §2). Décalage de rédaction, pas un défaut de code.

## 2. Résultat des tests

**Je n'ai pas pu relancer la suite autorisée dans cette session.** `wp/tests/rejouer.ps1` exige Docker dans WSL Ubuntu (conteneur jetable `--network none`) ; l'environnement non-interactif bloque les processus imbriqués (`wsl.exe`, `docker`) et aucune approbation manuelle n'est possible ici. Tentatives faites, toutes refusées par le bac à sable. `php` seul n'est pas non plus exécutable pour jouer le PHPUnit en isolé.

Ce que j'ai pu vérifier sans exécuter :
- **Logique des nouveaux tests** : lue intégralement. Le test PHPUnit est cohérent et réellement résistant au mutant (le cache contient le HTML « B » au moment du mutant ; sans retour anticipé, `Accueil::numero()` est rappelé → `$builds` change → `assertNotSame` passe). Le runtime compte bien 1 / 1 / 2. Toutes les fonctions appelées sont fournies par la fixture.
- **`production/B-15/verifier.py`** (harnais de preuve) : resserré, pas affaibli — contrôles natifs 15 → **16**, tests PHPUnit B15 attendus 2 → **3**, reçus repointés sur `*-corrections-final-V2` et `reception-corrections-V2.json`, assertions de `pass` / zéro échec intactes.
- **Comptage rejeu** annoncé par Hermès dans `A-VOIR.md` : **1214 tests / 36717 assertions PASS**, OUTILS 23/852/0, 13 paquets/0 échec.

**Statut : rejeu vert reporté par les reçus d'Hermès, non reproduit indépendamment dans cette session.** À confirmer par un passage normal du harnais sur le NUC de Ced.

## 3. Régressions ou modifications non demandées

- **Aucune régression B-15 détectée** par le diff : `PiedPage.php` (code fonctionnel) n'a pas bougé ; seuls les tests et la preuve ont été renforcés dans le sens des corrections.
- `verifier.py` : modification attendue et cohérente avec l'instruction 1 (nouveaux reçus + comptes 16/3). Aucun assouplissement.
- **Hors périmètre B-15, à signaler** : le diff `63a11841..HEAD` sur `wp/` touche aussi de nombreux fichiers B-16, C-30, C-31 (`PageArticle.php`, `CodesSuivis*`, `DomainesRefuses*`, outils et tests associés, `README.md`). Ce sont d'autres lots avancés en parallèle, non évalués ici ; ils ne sont pas des régressions de B-15 mais cohabitent dans le même arbre.
- **Arbre de travail** : deux fichiers non committés au départ (`wp/outils/demo/c31-browser.py`, `wp/tests/demo/c31-observer.php`) relèvent de C-31, sans rapport avec B-15.

## 4. Verdict

**Prêt pour la validation de Ced.**

Motif : les quatre instructions de la fusion sont traitées correctement — instruction 1 pleinement appliquée (et au-delà : option a + option b + mutant), instructions 2 et 3 conservées conformément à leur défaut prudent, instruction 4 tenue dans son esprit (comptage périmé retiré, chiffre frais justifié). `PiedPage.php` est inchangé : aucune régression de code. Il ne reste **aucun problème de fond** ouvert par cette vérification.

Deux réserves honnêtes, qui ne sont pas des problèmes de fond mais que Ced doit connaître :
1. Le rejeu complet n'a **pas** pu être relancé par moi dans cette session (Docker/WSL hors d'atteinte en non-interactif) ; je m'appuie sur la lecture des tests, le resserrement de `verifier.py` et le rejeu vert reporté par Hermès (1214/36717 PASS). Un passage normal du harnais sur le NUC doit le confirmer avant clôture.
2. Le comptage inscrit dans `A-VOIR.md` (1214/36717) diffère du chiffre littéral demandé (1209/36693), écart expliqué par l'arrivée de B16/C30 dans la file.

Rappel doctrine : ce verdict n'est **pas** un GO. La validation visuelle de l'habillage du pied reste du ressort de Ced (doctrine §6).
