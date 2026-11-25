# Vérification B-02 (2ᵉ et dernier tour) — « Mon compte »

Vérificateur : Claude, sur le NUC. Je contrôle l'application de `corrections/B-02.md` après le travail d'Hermès, je relance ce que je peux, je signale les écarts. Ce n'est pas une relecture complète et ce verdict n'est pas un GO (§6 doctrine).

**Base comparée.** Version relue = état au commit `8dd5fc3` (25/11 20:38, horodatage de `relectures/B-02/claude.md`). Version corrigée = `HEAD` (`56bc091`). `git diff 8dd5fc3 HEAD` sur `wp/` et lecture de `production/B-02/`.

**Identité de la version testée.** Les dix fichiers listés dans `production/B-02/corrections-verification.json` ont leur SHA256 recalculé sur le disque : **tous identiques** à l'empreinte testée par Hermès. La version que je vérifie est exactement celle sur laquelle portent les logs ci-dessous — pas une version postérieure non testée.

---

## 1. Application des instructions de corrections/B-02.md

| # | Instruction | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | Garde Memberships (`function_exists`), absent ⇒ « Suspendu » | **Appliquée** | `MonCompte.php:34` (`$available = function_exists(...)`), appel gardé `:36` ; `MonCompteRegles.php:188` (available=false ⇒ Suspendu) ; test `MonCompteAdapterTest.php:25` (fatale impossible ⇒ « Suspendu »). |
| 2 | Quatre lignes toujours présentes, avant et indépendamment du calendrier | **Appliquée** | `MonCompteRegles.php:27-32` (4 positions dès `month`/intervalle 3, sans moteur) ; moteur optionnel `:70` ; `MonCompte.php:98` projette d'abord sans moteur ; test `MonCompteAdapterTest.php:39` (calendrier null/invalide/vide × début valide/invalide ⇒ 4 lignes, premier null). |
| 3 | Rattacher les règlements de renouvellement, contrôle propriétaire, sans double-compte | **Appliquée** | `MonCompteRegles.php:92-171` (`reglements` : propriétaire `:101`, dédup par id `:122`, contradiction/ambiguïté signalées) ; test `MonCompteReglesTest.php:50` (2 payées + 2 à venir, montants/ids propres, commande étrangère ignorée avec avertissement, `failed` ⇒ « Échouée »). |
| 4 | Projeter les numéros du bloc courant via `Moteur::renouveler()` ; cas 171-174 → 175-178 | **Appliquée** | `MonCompteRegles.php:73-78` (`ouvrir` puis `renouveler` sur chaque début) ; bloc indisponible nommé `:63-67` au lieu du premier bloc ; test `MonCompteReglesTest.php:71` (171/174 → 175/178, renouvellement manquant ⇒ premier null + message). |
| 5 | « Virement » réservé au circuit `bacs` ; sinon attente non spécifique | **Appliquée** | `MonCompteRegles.php:183-186` (pending : bacs ⇒ virement, sinon « Paiement en attente de validation ») et `:191` (on-hold) ; test `MonCompteReglesTest.php:114` (stripe/vide/bacs) ; `b02-state.php:7` attendu A-VIR passé à « Paiement en attente de validation ». Droits d'accès non touchés. |
| 6 | Isoler le cœur en PHP pur + `*Test.php` dans T01 + reconstruire `b02-runtime.php:53` + conserver l'isolation | **Appliquée** | `MonCompteRegles.php` (classe pure, reçoit données + heure, sans dépendance WP) ; `MonCompteReglesTest.php` ajouté ; `b02-runtime.php:53-65` attendu reconstruit (2 Payée / 2 À venir, ids/montants propres, rejeu sans double-compte) ; bornes exactes grâce ±1 s et fin à l'instant exact dans `MonCompteReglesTest.php:125-130`. Tests d'isolation conservés. |
| 7 | Hook redondant : supprimer ou justifier + corriger rapport l.36 et commentaire | **Appliquée** | Hook `woocommerce_after_subscription_object_save` retiré de `MonCompte.php` (commentaire `:20` « appartient à EnvoiNatif, sans doublon B02 ») ; `b02-state.php:23` renommé `aucun_hook_postal_redondant_MonCompte` ; test `MonCompteAdapterTest.php:83` ; rapport corrigé `production/B-02/rapport.md:22` (« limité au formulaire client » déclaré faux et retiré). |
| 8 | Réserves du runner calculées depuis les contrôles réels, profil A-SEPA4 | **Appliquée** | `b02.py:21-47` (`acceptance_blockers`/`observations` dérivés d'un relevé A-CARTE/A-SEPA4/A-SUSP/A-VIR) ; plus d'alias `a-4x-j45` ; test `test_b02_runner.py:10`. Anciens reçus laissés historiques (nouveaux sous `corrections-20261125/`). |
| 9 | Signaler les interprétations (`cancelled` ⇒ Expiré, on-hold+adhésion en attente) | **Appliquée** | `production/B-02/rapport.md:19` (« Décisions prises à défaut ») et `sources.md:6` (bacs = circuit distinct). |
| 10 | Tracer les écarts dans `docs/ecarts.md` (hors périmètre worker) | **Appliquée** | `docs/ecarts.md:42-43` (renvoi §3.10 erroné ; `a-4x-j45` ⇒ A-SEPA4). Reporté par le parent, comme prévu. |

Les deux réglages « Pour Imagine » (libellé on-hold, marge C-05) et les points « À arbitrer par Ced » restent ouverts **par conception** : ce sont les mêmes que dans la fusion, pas des instructions non faites.

## 2. Résultat des tests

- **Runner B02 (Python, hors ligne), rejoué par moi** : `python -m unittest test_b02_runner` ⇒ **2 tests OK**. Reproduit localement.
- **PHPUnit B02 (9 tests, 73 assertions)** : **OK** d'après `corrections-unit-final.log` (PHPUnit 11.5.58, PHP 8.2.33). Les 9 = 5 `MonCompteReglesTest` + 4 `MonCompteAdapterTest`.
- **T01 canonique (suite complète)** : **1023 tests / 34094 assertions, 0 échec / 0 erreur / 0 ignoré** (`corrections-t01-final.log`, `corrections-verification.json`). Paquet imagine-site : 59 tests / 346 assertions, les 9 B02 compris.
- **Natif + HTTP + préservation (138 contrôles)** : **0 échec**, rejeu strict **exit 2** à cause des cinq réserves d'acceptation (`corrections-verification.json`).

**Limite honnête d'exécution.** Dans mon périmètre, je n'ai **pas** pu relancer moi-même PHPUnit/T01 (`php` bloqué par les permissions de cet environnement) ni les recettes HTTP (pas de réseau vers le staging — conforme à la doctrine : le relecteur ne rejoue pas les recettes HTTP). Je m'appuie donc sur les logs d'Hermès **pour ces trois suites**, après avoir vérifié par SHA256 que les fichiers testés sont bien ceux du dépôt. Le seul test que j'ai exécuté indépendamment (runner) passe.

## 3. Régressions et modifications non demandées

- **Aucune régression dans le périmètre B-02.** Le diff des fichiers déclarés (`MonCompte.php`, `MonCompteRegles.php`, `parts/mon-compte.php`, les deux tests, `b02*.py/php`) correspond point par point aux instructions. Le gabarit n'ajoute que l'affichage `data-imagine-bloc-indisponible` et `data-imagine-rattachement` (`mon-compte.php:31-32`), cohérent avec les instructions 3 et 4.
- **`EnvoiRelations::renouvellements`** (dépendance nouvelle de `MonCompte.php:77`) existe et pré-date la correction (commit du 25/11 14:58) : pas de dépendance cassée introduite.
- **Changements `wp/` hors B-02.** Le diff depuis la version relue inclut aussi `Echeances*.php`, `b04-*`, `c15-*`. Ils **n'appartiennent pas** au lot déclaré B-02 (absents de `corrections-verification.json` et du rapport B-02) : ce sont les voies parallèles (A-11/12/13, C-16/17/18). Ils ne touchent aucun fichier B-02. Hors de ma vérification.
- **`strict exit 2` inchangé** : les cinq réserves (marge C-05, historique/compteur C-01, documents, A-VIR sans `bacs` natif, édition positive d'adresse non rejouée) sont les réserves métier/réel déjà portées par la fusion (§5 « Pour Imagine », §6 « À arbitrer par Ced »), pas un défaut technique neuf.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les dix instructions de `corrections/B-02.md` sont appliquées, localisées et couvertes par des tests ; le cœur métier est isolé en PHP pur et testable hors WordPress (lève le point de fond de la fusion). Aucune régression dans le périmètre B-02, aucune modification non demandée dans ses fichiers. Les suites déclarées sont au vert (T01 1023/0, PHPUnit 9/9, 138 contrôles natifs/HTTP sans échec) ; le seul test que j'ai pu rejouer moi-même (runner) passe. Il ne reste **aucun problème de fond technique** : ce qui subsiste relève de la validation visuelle sur maquettes, de la recette HTTP contre le staging et des réglages métier (marge C-05, libellé on-hold) — tous explicitement du ressort de Ced / Imagine selon la fusion et le §6 de la doctrine.
