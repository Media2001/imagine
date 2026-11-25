# Vérification A-05 — second et dernier tour

Date : 25 novembre 2026. Vérificateur : Claude (indépendant, pas Hermès). Base : `corrections/A-05.md` (verdict fusion « À corriger »), corrigé par Hermès après la fusion.

Méthode : `git diff c77f6a7..HEAD` (fusion → maintenant) sur `wp/outils/bascule/a05/clean.py`, `wp/outils/bascule/nettoyer.md`, `wp/tests/a05/`, et relecture des preuves scellées dans `production/A-05/`. Ce n'est pas une relecture complète : je contrôle uniquement l'application des 5 instructions, les tests, les régressions.

---

## 1. Application des instructions de `corrections/A-05.md`

### Instruction 1 — P1 : fermer la garde de dossier partagé → **Appliquée**
- `wp/outils/bascule/a05/clean.py:155-158`. La garde ne teste plus le seul voisin `garder` ; elle liste **tous** les voisins du dossier (`neighbours=[n for n in inv['plugins'] if n!=name and n.startswith(base+'/')]`) et refuse `A05_SHARED_PLUGIN_DIRECTORY` dès qu'il en existe un, quelle que soit son action (`garder` **ou** `desactiver`). Le code d'erreur nomme le voisin fautif.
- Variante « plusieurs `retirer` » : traitée par le défaut prudent recommandé — refus même dans ce cas (commentaire `:155-156`), donc aucune suppression de fichiers avant désactivations/désinstallations explicites.
- Tests ajoutés (`wp/tests/a05/test_clean.py:110-131`) : voisin `desactiver` actif **et** inactif, dans les deux ordres du plan ; plusieurs `retirer` partageant un dossier. Les quatre passent en local ; vérifient aussi que les fichiers du dossier sont intacts après refus.

### Instruction 2 — P2 : aligner la lecture d'en-tête → **Appliquée**
- `clean.py:126`. La regex `Requires Plugins:` passe de `^\s*(?:\*)?\s*` à `^[ \t/*#@]*` — exactement la classe de préfixes WordPress (`get_file_data`) recommandée en idéal. La regex `Plugin Name:` (`clean.py:123`) est alignée sur la même classe. L'asymétrie entre les deux lectures est supprimée ; aucune extension n'est chargée.
- Tests ajoutés (`test_clean.py:132-146`) : en-tête `// `, `# `, `@ `, `/* `, `* ` et sans préfixe, au **retrait** comme à la **désactivation** de la dépendance → `A05_DEPENDENCY:base/main.php`. Passent en local. Côté natif, un test recoupe la lecture avec `get_plugin_data` de WordPress (`inside.py:correction_native_header_*`).

### Instruction 3 — P3 : rendre la garde uploads symétrique → **Appliquée**
- `clean.py:168`. Ajout de la clause `row['path'].startswith(kept['path']+'/')` : un `garder` sur un ancêtre refuse désormais la suppression de son descendant, en plus du sens déjà présent (descendant gardé bloquant le parent). Code `A05_UPLOAD_KEEP_CONFLICT:<cible>`.
- Tests ajoutés (`test_clean.py:147-156`) : ancêtre `garder` + descendant `supprimer`, dans les deux ordres des règles ; vérifie qu'un fichier témoin du descendant survit. Passent en local.

### Instruction 4 — refaire les preuves → **Appliquée**
- Nouvelle preuve scellée `production/A-05/preuves/8d814c18912a` (l'ancienne `3f1d3e3ce8f2` est conservée et marquée `previous_evidence_unchanged: true` dans `scellement.json`).
- `verification-finale.json` : `exit_code 0`, 21 tests unitaires (contre 16), 149 contrôles d'intégration (contre 93), 7 contrôles runner, 0 échec. `native_correction_refusals` : 22 côté classic, 22 côté hpos — les plans de conflit P1/P2/P3 sont bien exercés nativement.
- Cycle TDD tracé et scellé pour chaque correction : P1/P2/P3/M1 ont chacun une preuve `red` (exit 1) puis `green` (exit 0) distincte. C'est plus que demandé : la preuve de l'échec préalable est fournie.

### Instruction 5 — M1 : journaliser les noms planifiés absents → **Appliquée**
- Nouvelle fonction `absent_resources()` (`clean.py:172-184`), branchée sur la sortie à blanc sous la clé `information` (`clean.py:232`). Chaque entrée : `{kind, name, status:"nommé, absent"}`, pour les cinq familles (plugin, table, option, cron, upload), préfixes sans correspondance compris. La docstring et le code garantissent qu'aucune opération, checkpoint ni écriture n'en découle.
- Tests ajoutés (`test_clean.py:157-172`) + cas natif `correction_M1_information_only` / `correction_M1_real_noop` (`inside.py`) : confirment que ces lignes sont informatives, que le passage réel reste `A05_NOOP`, et que l'empreinte avant/après est identique. Passent en local.

**Bilan : 5 / 5 instructions appliquées.** Aucune partielle, aucune non appliquée.

---

## 2. Résultat des tests

- **Suite unitaire pure-Python, relancée par moi en local** (`wp/tests/a05/test_clean.py`) : 21 tests, **19 OK, 2 erreurs d'environnement, 0 échec de logique**.
  - Les deux erreurs sont dues au poste Windows, pas au code : `test_example_is_only_a_keep_form` lit un chemin Docker en dur (`/subject/plan-imagine.exemple.json`), et `test_upload_escape_and_symlink_are_refused` échoue sur `os.symlink` (WinError 1314, privilège Windows requis). Ces deux tests sont conçus pour tourner dans le conteneur Linux ; ils ne sont pas touchés par la correction.
  - **Les 5 tests ajoutés par la correction passent tous** en local : `test_shared_directory_deactivate_neighbour_refuses_in_both_orders`, `test_shared_directory_multiple_removals_refuse_instead_of_early_rmtree`, `test_comment_dependency_headers_block_removal_and_deactivation`, `test_upload_kept_ancestor_blocks_descendant_deletion_in_both_orders`, `test_absent_plan_names_are_information_only_for_every_resource_kind`.
- **Suite native Docker** (`wp/tests/a05/run.py` → `inside.py`) : je ne peux pas la rejouer ici (pas de Docker sur ce poste Windows ; même limite que les deux relecteurs au premier tour, écriture `production/` interdite au relecteur). Je m'appuie sur la preuve scellée régénérée par Hermès : `8d814c18912a`, `exit_code 0`, lint/unit/integration/isolation/cleanup tous `ok`, 149 contrôles, duration ~198 s. Les empreintes avant/après sont identiques et `verification-finale.json` confirme `source_drift: []`, `historical_evidence_files_unchanged: 307`.
- **Non-régression A-03** : la comparaison native rend `native_exit 0, changes:[], anormal:0` côté classic et hpos — identique au premier tour. A-03 n'est pas requalifié.

Les trois trous de garde identifiés par la fusion (voisin `desactiver`, en-tête `//`/`#`, ancêtre gardé) sont désormais couverts par des tests qui échouaient avant la correction (preuves `red`) et passent après (preuves `green`).

---

## 3. Régressions ou modifications non demandées

- **`own_changed_files`** (déclaré dans `verification-finale.json` et confirmé par `git diff`) : `clean.py`, `nettoyer.md`, `wp/tests/a05/inside.py`, `wp/tests/a05/test_clean.py`. Rien hors de ce périmètre.
- **`nettoyer.md`** modifié (`:12`, `:34`, section mode à blanc) : non explicitement demandé par les instructions, mais c'est un **alignement de la documentation** sur les gardes corrigées (uploads symétrique, voisin partagé nommé quel que soit son état, champ `information`). Conforme à la doctrine §5 (chaque outil sur mesure documente ses règles) et au sens déjà tranché par la fusion. **Pas une régression, pas de la dérive métier.**
- **`clean.py`** : le `git diff` ne touche que les quatre zones ciblées (regex en-têtes, garde dossier partagé, garde uploads, fonction `absent_resources` + sa ligne de sortie). Aucune modification du chemin nominal, des préalables A-04, du SQL, ni de la logique de reprise.
- **Dérive concurrente hors périmètre** : `wp/plugins/imagine-site/imagine-site.php` et `wp/tests/demo/b03-final.py` ont changé dans le dépôt, mais Hermès les a explicitement **non touchés** au titre d'A-05 (`concurrent_out_of_scope_drift_not_touched`). Ils relèvent d'autres lots (B-03, etc.) ; hors de cette vérification.
- Le périmètre de sûreté reste inchangé : `plan-imagine.exemple.json` est toujours tout `garder` / `uninstall:false`, donc aucun des trois défauts ne pouvait de toute façon se déclencher sur le formulaire livré — la correction ferme les gardes **avant** qu'un plan de retrait soit un jour exécuté, comme l'imposait la fusion.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions de `corrections/A-05.md` sont appliquées, au bon endroit, avec les tests réclamés et un cycle TDD red→green scellé pour chacune. La preuve a été régénérée (`8d814c18912a`, exit 0, 149 contrôles) sans toucher l'ancienne. Aucune régression, aucune modification hors périmètre ; la seule édition non listée explicitement (`nettoyer.md`) est un alignement de documentation légitime. Aucun problème de fond ne subsiste, aucune question technique ni métier n'est laissée ouverte.

Rappels doctrine, hors périmètre de cette vérification : aucun retrait réel n'est décidé ; le plan rempli, les préalables et un GO A-05 écrit nommant la tâche restent requis avant toute opération sur le vrai site (§3). Ce verdict de vérification n'est pas un GO au sens du §3 ; il ne vaut que pour la clôture du lot de code A-05, qui revient à Ced.
