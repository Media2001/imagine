# Vérification C-27 — 2e et dernier tour (Claude, vérificateur)

Date : 2026-11-27. Entrée : `corrections/C-27.md` (verdict de fusion **À corriger**) appliqué par Hermès.
Méthode : `git diff` entre la version relue (`9566f365`, synchro 07:58, état lu par les deux relecteurs) et HEAD, sur `wp/` et `production/C-27` ; relance des tests hors réseau. Pas de relecture complète refaite.
Ce verdict **n'est pas un GO** (doctrine §6).

## 1. Instructions de `corrections/C-27.md` : état d'application

### Instructions pour Hermès (numérotées)

**1. I1 — `Acquisition.php:123` (absence vs échec de lecture avant initialisation de la source) → Appliquée.**
Nouvelle méthode `Acquisition::sourceFiable()` (`Acquisition.php:154-169`) : vide le cache `user_meta`, remet `$wpdb->last_error`, lit la source par SQL direct sur `{$wpdb->usermeta}`, et renvoie `[]` **uniquement** pour une absence SQL prouvée, `WP_Error` dès que `last_error` est non vide ou le résultat non-tableau. Dans `repondre()` (`Acquisition.php:128-138`) : la source est lue via `sourceFiable()` ; `is_wp_error` → `throw` → `ROLLBACK` (ligne 144), donc la déclaration ajoutée en transaction est annulée ; l'écriture n'a lieu que si `$source === []` ; la relecture de contrôle utilise `self::sourceFiable($actor) !== [$record]`. Le `=== ''` a disparu. Conforme à l'instruction (distinction explicite, lecture fraîche fiable, annulation en cas d'échec).

**2. I2 — `AcquisitionConfidentialite.php:161` (effacement : symétrie du cache, vérification réelle de la suppression) → Appliquée.**
`AcquisitionConfidentialite.php:152-178` : la source est lue via `Acquisition::sourceFiable($owner)`, qui invalide lui-même le cache `user_meta` (symétrie avec `repondre()`) et distingue erreur/absence (`is_wp_error` → `throw`). La suppression est confirmée avant `COMMIT` (`Acquisition::sourceFiable($owner) !== []` → `throw`). La relecture finale ajoute `$remainingSource = Acquisition::sourceFiable($owner)` et `done` exige `$remainingSource === []` en plus de `$remaining`/`$remainingSeen` vides (ligne 178). La meta `SOURCE` est donc bien vérifiée, pas seulement les options. Conforme.

**3. M1 — `Acquisition.php:111` (refuser une proposition `VUE` effacée) → Appliquée.**
`repondre()` lit désormais le tombstone `VUE` sous le même verrou : `wp_cache_delete(self::VUE . $id, 'options')` (ligne 108), puis `$seen = get_option(self::VUE . $id, null)` (113) et refus si `($seen['etat'] ?? '') === 'effacee'` (114). Le README est corrigé : la promesse « laisse seulement commande/état effacé **pour interdire un redépôt** » est retirée ; la nouvelle phrase explicite que « le POST refuse le tombstone **REPONSE ou VUE**, y compris une proposition seulement vue et effacée sans réponse » (`README.md`, section C-27). Conforme sur le code et sur le README.

**4. Tests (couvrent I1, I2, M1) → Appliquée.**
`tests/AcquisitionAdapterTest.php:64-129` ajoute 5 tests ; les stubs (`tests/AcquisitionWPStubs.php`) modélisent un vrai cache `user_meta` empoisonnable (ensemble vide mis en cache sur échec de lecture) et un `delete_user_meta` qui peut échouer :
- (a) `testPremiereLectureSourceEnEchecAnnuleLaDeclarationSansEcraser` → I1 : première lecture SOURCE en échec, source antérieure intacte, déclaration non validée.
- (b) `testEffacementPremiereLectureSourceEnEchec…`, `…CacheVideEmpoisonneEtSuppressionEnEchec…`, `…RelectureFinaleSourceEnEchec…` → I2 : `done=false` / `items_retained=true` tant que la source subsiste, puis reprise.
- (c) `testPropositionVueSeuleEffaceeRefuseUnAncienFormulaire` → M1 : POST d'un ancien formulaire sur proposition sans réponse effacée → `WP_Error`, aucun état modifié.
Le vérificateur compte `unit_tests: 12` (contre 7 relus) / `unit_assertions: 80`.

**5. Rejeu / documentation `A-VOIR.md` → Appliquée.**
`production/C-27/A-VOIR.md` documente les lanceurs non rejoués en première relecture (recettes mutantes Python des deux côtés, PHPUnit côté Codex) et que la livraison corrective les a réellement exécutés. Nouvelle recette `wp/outils/demo/c27-corrections.py` et contre-exemples `wp/tests/demo/c27-verifier-tests.py` ajoutés.

### Décision technique (Hermès applique, Claude arbitre après coup)

**Forme de `imagine_source_acquisition` (tableau structuré) → Appliquée.** Documentée dans le README C-27 : « `imagine_source_acquisition` garde le **tableau structuré complet** (`commande`, `compte`, `date`, `choix`, `libelle`), jamais un simple libellé ». Défaut proposé par la fusion respecté.

### À arbitrer par Ced (visuel)

**Emplacement de la section C10 → non tranché, normal.** C'est une question visuelle laissée à Ced (défaut conservé : sous « Enregistrer »). Rien à corriger côté code ; elle reste ouverte pour la validation de Ced.

## 2. Résultat des tests (hors réseau, sans site)

- **Vérificateur parent** `python -B production/C-27/verifier.py` → **C27 PASS** : 628 gates, **1 195 tests globaux / 36 573 assertions** (0 échec), **12 tests unitaires C-27 / 80 assertions**, 11 mutants de source, 5 témoins mutants réels, 56 contrôles natifs, 720 contrôles d'outils. 2 échecs de paquets étrangers = **A-31/A-32** (hors périmètre, signalés et non masqués).
- **Contre-exemples** `python -B wp/tests/demo/c27-verifier-tests.py` → **14/14 OK**, dont `test_I1_mutant_must_really_overwrite`, `test_I2_mutant_must_really_retain_source`, `test_M1_mutant_must_really_accept_old_POST`, `test_final_source_read_failure_must_not_claim_done` : les mutants reproduisent réellement les bugs, les preuves ne sont pas de simples drapeaux.
- **PHPUnit via `rejouer.ps1`** : non rejoué indépendamment ici (le conteneur Docker / processus imbriqué exige une approbation en session non-interactive). Je m'appuie sur le vérificateur parent, qui est le lanceur hors-réseau désigné et qui revalide le rejeu global (1 195 tests) ainsi que les 12 tests unitaires C-27.

## 3. Régressions ou modifications non demandées

- **Dans le périmètre C-27 : aucune régression.** Les seules modifications des fichiers C-27 depuis la version relue sont exactement les corrections I1/I2/M1, leurs tests, la section C-27 du README et la recette de contrôle. Une seule ligne ajoutée non explicitement demandée : `$result['items_removed'] = false;` dans le bloc de rollback de `effacer()` (`AcquisitionConfidentialite.php:186`) — cohérent (sur rollback, rien n'a été retiré), bénin, pas une régression.
- **Hors périmètre C-27 :** le `git diff` depuis `9566f365` fait apparaître beaucoup d'autres lots (B-07, B-09, B-10, B-11, C-28, A-31, A-32) progressés en parallèle dans la même synchro. Ils ne font pas partie de C-27 et ne sont pas des régressions de ce lot ; A-31/A-32 restent rouges au rejeu global, déjà signalés en tête d'`A-VOIR.md` et sans incidence sur C-27.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les deux points importants (I1, I2) et le point mineur (M1) de la fusion sont corrigés de façon cohérente et vérifiée ; les tests couvrant les trois chemins d'échec sont ajoutés et verts ; le vérificateur parent passe ; aucune régression dans le périmètre C-27. Le seul élément restant est la **validation visuelle de Ced** (emplacement de la section C10, squelette sans CSS) — c'est précisément ce que la doctrine §6 réserve à Ced, pas un problème de fond.

Ce verdict n'est pas un GO : il ne vaut ni mise en ligne ni autorisation de déploiement, et la validation visuelle de Ced reste requise pour clore.
