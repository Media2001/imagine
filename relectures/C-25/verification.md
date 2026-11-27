# Vérification C-25 — second et dernier tour

Vérificateur indépendant. Objet : contrôler que les corrections de `corrections/C-25.md` (fusion du 27/11 00 h 02) ont bien été appliquées par Hermès, relancer les tests, repérer toute régression. Pas de relecture complète refaite.

Base de comparaison : état de la fusion `afb074a8` (27/11 00 h 03) → `HEAD` (`b7129778`). Correctif source d'Hermès : `88facc8d` (00 h 38).

## 1. Instructions de `corrections/C-25.md`, une par une

### §4 — Instructions pour Hermès

1. **R1 — Journaliser les réglages C-25 → Appliquée.**
   - `RetractationReglages.php:15-16` : raccords additifs `added_option` / `updated_option` (priorité 25), ciblant la seule option `Retractation::OPTION`.
   - `RetractationReglages.php:48-74` : `journal()` écrit un événement avant/après (auteur, date UTC) dans le journal partagé ; **si l'écriture échoue, restauration de la préimage exacte** (ou suppression si absente au départ) puis `wp_die` si la restauration échoue à son tour (`:67`).
   - `RetractationReglages.php:78-79` : garde dans `nettoyer()` empêchant le sanitizer de renormaliser la préimage pendant la restauration.
   - Testé par le vrai chemin (`options.php`) : `testReglagesJournalAjoutModificationEtRollbackPreimage` (`RetractationAdapterTest.php`), recette avec création, modification et deux pannes SQL d'INSERT du journal.
   - Nuance : les événements sont stockés dans des options dédiées `imagine_reglages_journal_<uuid>` plutôt qu'injectés dans la bibliothèque close C-10 ; la recette vérifie que l'écran C-10 les affiche. Vérifié par reçu, non re-dérivé (pas de relecture complète).

2. **R2 — Corriger l'échappement du motif → Appliquée.**
   - `Retractation.php:115` : écriture via `add_comment_meta($note, self::META, wp_slash($record), true)`.
   - `Retractation.php:116` : comparaison de relecture conservée **contre l'original** `$record`, pas la valeur slashée. Un motif à antislash est donc enregistré, relu à l'identique et accepté.
   - Bouchons corrigés **d'abord**, comme demandé : `RetractationWPStubs.php` — `add_comment_meta` applique désormais `wp_unslash`, et `wp_unslash`/`wp_slash` sont réalistes (stripslashes/addslashes, récursifs).
   - Test de bout en bout jusqu'à l'export C-21 : `testAntislashWordPressReluEtExporteSansPerte`.

3. **R3 — Compléter `README.md` (section C-25) → Appliquée.**
   - `wp/plugins/imagine-site/README.md:371-395` : section « C-25 — rétractation, demande seule ». Décrit les deux étapes, l'accusé, la note privée, le journal de demande, les deux réglages (`jours` 1–365 défaut 14 ; `origine` paiement/manuelle), les commandes de test (distinction hors-ligne / recettes `imagine-test-demo`), les bornes et limites.

4. **Documenter le blocage `delete_user` → Appliquée.**
   - `README.md:377` : refus prudent de la suppression (`wp_die`) en cas de panne SQL persistante, pour ne pas laisser de trace orpheline, avec marche à suivre (réparer puis réessayer).
   - Code inchangé et conforme (`RetractationConfidentialite.php:28`) : aucun comportement de suppression ajouté.

### §4bis — Décision technique (défaut proposé)

- **Injection des réglages dans l'écran C-10 → défaut appliqué.** Injection par bufferisation conservée, **aucun hook neuf dans C-10** ; le hook de rendu dédié est renvoyé à un prochain passage. Documenté `README.md:375` et dans `CORRECTIONS-002-V2.md`. Conforme au défaut proposé.

### §5 — À arbitrer (métier / visuel / juridique)

- Non traité ici, et c'est correct : borne finale **incluse**, trace anti-doublon **dépersonnalisée conservée**, défaut **14 jours / paiement** laissés inchangés en attendant l'arbitrage d'Imagine ; validation visuelle et validation juridique restent dues à Ced. Ce sont des questions ouvertes préexistantes, pas des défauts de code.

## 2. Résultat des tests

Je n'ai **pas** pu réexécuter la suite moi-même dans cette session : `php` est refusé (politique de permission, session non interactive), aucun `phpunit` n'est embarqué, et le harnais de démo (`c25.py`) écrit ses reçus dans `production/C-25/`, interdit à mon rôle.

J'ai donc contrôlé autrement, et c'est concluant : **les 6 fichiers source et tests C-25 sont octet pour octet identiques (SHA-256 vérifiés sur disque) à ceux scellés dans le reçu de régression verte.**

| Fichier | SHA-256 disque = reçu |
|---|---|
| `Retractation.php` | ✔ `61ab8228…` |
| `RetractationReglages.php` | ✔ `5f3435da…` |
| `RetractationConfidentialite.php` | ✔ `00897450…` |
| `RetractationRegles.php` | ✔ `2bd47e95…` |
| `tests/RetractationAdapterTest.php` | ✔ `c0f3cde6…` |
| `tests/RetractationWPStubs.php` | ✔ `e6f014a0…` |

Reçus correspondants (code courant, scellés le 26/11 ~23 h 52-54) :

- `regression-corrections002-V2.json` : **1151 tests, 36062 assertions, 0 échec / 0 erreur / 0 ignoré** ; **20 outils, 521 contrôles, 0 échec**.
- `canonique-corrections002-V2.json` : **10 tests, 172 assertions**, 0 échec.
- `mutations-corrections002-V2.json` : **15/15 mutations détectées**, dont `antislash` (R2) et `journal-reglages` / `rollback-reglages` / `preimage-reglages` (R1), chacune exigée en échec par les deux nouveaux tests. Preuve que les correctifs R1/R2 sont réellement couverts.
- `recette-corrections002-V2.json` : **57 contrôles** (23 HTTP + 34 natifs), tous verts ; vrais POST `options.php`.
- `verification-corrections002-V2.json` : **PASS**, `pret_verified: true`, `exit: 0`.

Statut de test : **vert**, sur le code exact livré. Les angles morts des bouchons signalés dans la fusion (R1 et R2) sont désormais couverts.

## 3. Régressions ou modifications non demandées

- **Côté C-25 : aucune.** Les seuls changements de code C-25 depuis la fusion sont les quatre instructions ci-dessus plus le défaut technique convenu. Aucun fichier C-25 n'est modifié non commité (l'arbre de travail ne touche que des lots tiers).
- **Hors C-25 (pour information, hors périmètre de cette vérification).** L'intervalle `afb074a8..HEAD` contient aussi des changements d'autres lots (`wp/tests/a25`, `a28`, `a29`, `wp/tests/demo/c26-*`) et des modifications non commitées sous `wp/tests/a29/` ; travail parallèle d'autres agents, sans lien avec C-25. La régression globale (1151 tests) reste verte, donc aucune interaction négative constatée.
- `CORRECTIONS-002-V2.md` documente un incident de harnais (transport de l'inverse, portée `locals()`) **côté outils de reçus**, résolu, sans perte de préimage ni état métier altéré ; ne touche pas le code livrable C-25.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les quatre instructions (R1, R2, R3, doc `delete_user`) et le défaut technique sont appliqués, cités fichier + ligne, et couverts par des tests dont les mutations prouvent l'efficacité. La suite est verte sur le code exact livré. Aucun problème de fond restant côté code.

Rappel doctrine : ce verdict n'est pas un GO. Restent dues, hors de ce lot de code, la **validation visuelle** (parcours, écran C-10, liste admin) et la **validation juridique** (délai et dates légales, loi belge du 19/07/2026), ainsi que les deux réglages métier à trancher par Imagine (borne finale, trace anti-doublon) — toutes déjà consignées dans `production/C-25/A-VOIR.md`.
