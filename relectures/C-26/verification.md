# Vérification C-26 — 2e tour (final)

Vérificateur indépendant. Lot de test d'étanchéité (cible fictive `imagine-test-demo`). Le lot a été corrigé par Hermès après la fusion `corrections/C-26.md`. Base de comparaison : état relu ≈ commit `633521b3` (27/11 00:53, dernier avant les relectures de 01:43/01:50) → `HEAD` (`a7b3e247`). `git diff` lu sur les six fichiers du lot plus les fichiers C23 partagés. Ce n'est pas une relecture complète : je contrôle l'application des dix instructions, les tests et les régressions.

Rappel doctrine : ce verdict n'est pas un GO (§6). Il ne vaut que pour la clôture d'un lot de code.

## 1. Application des instructions de `corrections/C-26.md`

| # | Instruction | État | Fichier:ligne |
|---|---|---|---|
| 1 | **(Bloquant C26-05)** `denied_markers` : inventaire complet des témoins | **Appliquée** | voir détail |
| 2 | **(C26-01)** Archive `/evenements/` inventoriée + mutée | **Appliquée** | voir détail |
| 3 | **(C26-02)** Attendu B06 indépendant de `autorise()` | **Appliquée** | voir détail |
| 4 | **(C26-03)** Vérificateur C23 : recalcul sur toutes les lignes | **Appliquée** | voir détail |
| 5 | **(C26-04)** Vérificateur privacy : attente déduite du public | **Appliquée** | voir détail |
| 6 | **(C26-06)** Restaurations indépendantes + reçu sur exception | **Appliquée** | voir détail |
| 7 | **(Mineur)** `__import__('re')` → `re.findall` | **Appliquée** | — |
| 8 | **(Mineur)** défaut `/my-account/` | **Appliquée** | `c26.py:52` |
| 9 | **(Mineur)** témoins datés → marqueurs `C26_*` | **Appliquée** | `c26-fixture.php:357,383-384` |
| 10 | **(Traçabilité)** rejeu Python 3.11 **par les relecteurs** | **Partiellement** | voir §2 |

**Instruction 1 (bloquant).** L'oracle `denied_markers` (`c26.py:178-194`) ne repose plus sur le regex étroit `CONTENU_FICTIF_RESERVE_*`. Il délègue chaque corps réservé à `c23.reserved_witnesses` (`c23.py:318-322`), qui couvre `CONTENU_FICTIF_RESERVE_*` **et** les phrases témoins C08 (deux variantes), C10, C12. Les témoins coopérateur `C23_COOP_TEMOIN_[0-9]+` sont traités à part, avec application séparée des droits numéro (abonné / acheteur-autre-numéro) et de l'espace coopérateur. Un corps réservé inventorié sans témoin reconnu lève désormais (`c26.py:192`, `B06 contenu sans témoin reconnu` ; `c23.py:320`). La mutation « cooperative » injecte dans une vraie sortie un témoin C08 **et** un témoin B06 et exige que chacun fasse rougir (`c26-preparer.py:218-230`, `families = {... 'C08', 'B06'}`, `assert ... all(families.values())`). Test négatif couvrant C08/C10/C12 + `C23_COOP_TEMOIN_*` et la séparation des droits : `c26-tests.py:432`. — Le bloquant est levé.

**Instruction 2.** `routes()` ajoute `agenda-archive` → `/evenements/` (`c26.py:42`). `assess()` a un genre `agenda-archive` qui contrôle la structure du rendu (`c26.py:105-111`). La mutation `archive` passe par `mutate_source` (`c26-preparer.py:186-199`) : vrai `GET`, pas une réponse falsifiée.

**Instruction 3.** `cooperator_expected` (`c26.py:154-166`) calcule l'attendu à partir du code documenté `P-COOP` et des rôles livrés bruts — jamais depuis `autorise()`, la liste native observée ou un statut modifié (seule occurrence de « autorise » : le commentaire `c26.py:157`). `validate_cooperator` (`c26.py:168`) confronte la décision native à cet attendu. L'inventaire expose désormais `cooperator_roles` et `cooperator_actors` (code/rôles/statut) pour nourrir cet oracle (`c23-inventaire.php:87-90`). La mutation `autorisation-b06` altère le vrai code d'autorisation **avant** inventaire, réglages inchangés (`c26-preparer.py:135-156`). Test : `c26-tests.py:466`.

**Instruction 4.** `c23_checks` (`c26-verifier.py:54-88`) exige l'ensemble exact des contrôles C23 (identité-REST, inverses article/pdf/C08/achat-C14, faux-bing), impose leur unicité (`all(n==1 ...)`) et **recalcule** fuites et échecs sur toutes les lignes du reçu. Falsifications ajoutées : `c23-extras-supprimes`, `c23-identite-dupliquee`, `c23-inverse-vide`, `c23-echec-cache` (`c26-paquet-tests.py`). Test : `c26-tests.py:499`.

**Instruction 5.** `privacy_checks` (`c26-verifier.py:35-50`) dérive `owner` du public `inverse-proprietaire` et impose `positive is owner` ; l'attente de témoin vient de `owner or red`, plus du champ `positive` du reçu. Falsifications `privacy-inverse-vide-redesigne` et `privacy-tiers-positive`. Test : `c26-tests.py:488`.

**Instruction 6.** `restoration` tente chaque remise en état isolément (`attempt`, `c26-preparer.py:46-66`) : cleanup, b06, usermeta sont indépendants. `finish_restoration` (`c26-preparer.py:69`) écrit le reçu `-restauration.json` et le bilan même sur exception (try/except par bloc), appelé dans le `finally` de `run`. Le refus d'écraser une dérive concurrente est conservé (`mutate_source`, `c26-preparer.py:138-142`) ; une dérive sur l'étape b06 laisse `ok=False` et fait échouer l'assertion finale `all(x['ok'] ...)` — la dérive bloque toujours. `restored()` du vérificateur exige `restoration_steps` complet et tous `ok` (`c26-verifier.py:93-95`). Tests : `c26-tests.py:514` et `:528`.

**Instructions 7-9 (mineurs).** Plus aucun `__import__` dans `c26.py` ; plus de `mon-compte` (défaut `/my-account/`) ; plus de date `2001-01-01` dans `c26-fixture.php` (marqueurs `C26_PERSONNALISATION_FICTIF` / `C26_ACCUSE_FICTIF`). Vérifié par recherche. Test : `c26-tests.py:541`.

## 2. Résultat des tests

Reçus scellés du run Hermès (`production/C-26/`) :

- **Suite offline** (`tests.json`, `tests-utf8.log`, `tests-cp1252.log`) : `Ran 52 tests` + `OK` dans les deux encodages (utf-8 et cp1252), `exit 0`, **Python 3.11.15**, `TMPDIR_present=false`, `network_blocked=true`.
- **Vérificateur** (`verification-finale.json`) : 77 contrôles, **0 échec**, dont les nouveaux (`*_b06_oracle`, `*_witness_oracle`, `*_privacy_semantics`, `*_c23_cases/total/leaks/failures/witnesses`, `mutation_C08_et_B06`, `mutation_source_archive`, `mutation_archive`, `mutation_source_autorisation-b06`, `mutation_autorisation_b06`).
- **Qualification / falsifications** (`qualification-finale.json`) : 20 cas de falsification, **tous rejetés** (`all_rejected=true`), y compris les onze contre-exemples ajoutés par les corrections.

> **Réserve de traçabilité (instruction 10) — non levée par le relecteur.** Je n'ai **pas** pu rejouer la suite Python moi-même : le harnais refuse l'exécution d'un interprète Python dans cette session (même blocage qu'au 1er tour). La preuve « au vert » repose donc sur les **reçus scellés** produits par Hermès sur le NUC, pas sur un rejeu indépendant du vérificateur. J'ai en contrepartie lu le code du vérificateur et des falsifications : les contrôles sont réels (attente dérivée du public, recalcul sur toutes les lignes, sceau externe des sources) et ne se laissent pas blanchir trivialement. L'instruction 10 reste donc à honorer par un rejeu que Ced, seul à disposer de l'environnement d'exécution, peut lancer lors de sa validation.

## 3. Régressions et modifications non demandées

- **`c23.py`** : extraction de `reserved_witnesses` (régex **identique**, même levée). Refactor nécessaire à l'instruction 1 ; comportement C23 préservé — le reçu C23 interne reste 0 fuite / 0 échec.
- **`c23-inventaire.php`** : ajout de `cooperator_roles` et `cooperator_actors` **sans retirer** l'existant. Support direct de l'instruction 3.
- Aucune autre régression détectée dans le diff des fichiers du lot.
- Point sans impact : le fixture **inline** d'un test de routage (`c26-tests.py:29`) garde `2001-01-01T01:26:24Z` comme marqueur de personnalisation. C'est une donnée d'entrée de test, pas un témoin scellé ni la fixture de production ; sans effet sur l'étanchéité et hors périmètre de l'instruction 9.
- Hors périmètre : le même intervalle de commits contient du travail B-08 / B-09 non lié à C-26 ; non examiné ici.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les dix instructions sont appliquées (instructions 1 à 9 confirmées par lecture du diff ; le bloquant C26-05 est levé). Aucune régression ni modification non demandée. Les reçus scellés sont verts : 52 tests sous Python 3.11.15 dans les deux encodages, 77 contrôles du vérificateur sans échec, 20 falsifications toutes rejetées.

**Une seule réserve, non bloquante côté code :** l'instruction 10 demandait un rejeu Python **par les relecteurs eux-mêmes** ; le harnais me l'a refusé comme au 1er tour. La preuve de test reste adossée aux reçus, pas à un rejeu indépendant du vérificateur. Je recommande à Ced de relancer `c26-tests.py` sous Python 3.11 lors de sa validation — geste qu'il effectue de toute façon comme dernière barrière. Ce n'est pas un problème de fond dans le code, donc pas un « Remonte à Ced ».
