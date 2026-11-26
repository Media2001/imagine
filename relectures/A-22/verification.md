# Vérification A-22 (2ᵉ et dernier tour) — après correction par Hermès

Vérificateur : Claude. Date : 2026-11-26.
Base relue : `corrections/A-22.md` (fusion, verdict *À corriger*), `relectures/A-22/claude.md`, `relectures/A-22/codex.md`.
Périmètre du diff examiné : `git diff 56bcbb54..HEAD` (56bcbb54 = commit qui introduit `corrections/A-22.md`, 17 h 58) sur `wp/outils/bascule/`, `wp/tests/a22/`, `production/A-22/`.

Je n'ai **pas** refait de relecture complète. Je contrôle seulement l'application des six instructions de la fusion, je relance les tests à ma portée, et je signale régressions et écarts.

## 1. Application des instructions de `corrections/A-22.md`

### Instruction 1 — A12 : rétablir `A12_PATH_INVALID`. **Appliquée.**
`stream_guard.py:144` : `legacy_path` étendu à `{'A03':…,'A11':…,'A12':'A12_PATH_INVALID'}`. Les deux portes de refus de nom (`:149` échec de `resolve`, `:153` échec de `re.fullmatch`) lèvent désormais `legacy_path or tool+'_OUTPUT_UNSAFE'`, donc `A12_PATH_INVALID` pour A12 avant le lancement PHP. Tests ajoutés : `test_corrections.py::test_every_historical_invalid_final_name` (A12 → `A12_PATH_INVALID`) et `test_historical_invalid_names_at_real_python_entrypoints` (commande réelle du frontend A12, nom avec point → `A12_PATH_INVALID`, aucun fichier publié). Les deux passent.

### Instruction 2 — A14–A19 : conserver chaque code invalid-name + repli `A14_FAILED`. **Appliquée.**
Mêmes tests que ci-dessus : A14, A15, A16, A17, A18, A19 refusent un nom final invalide avec `TOOL_OUTPUT_UNSAFE` (code historique documenté), vérifié à la fois via `inventory(...)` et via les commandes réelles des frontends. Le repli générique fermé d'A14 est préservé : `a14/command.php:126` (`A14_FAILED`) et `a14/main.py:78` (`A14_CONFINEMENT_FAILED` → `A14_FAILED`). Aucun compteur ni format métier réécrit. Tests verts.

### Instruction 3 — empreintes A03 : corriger `a3`→`a03`, refuser une racine absente. **Appliquée.**
`matrix.py:26` : `'a'+str(x)` remplacé par `'a'+str(x).zfill(2)` → chemin `a03`. Ajout `if not p.exists():raise RuntimeError('A22_SOURCE_ROOT_MISSING')` : une racine attendue absente n'est plus énumérée en silence. `stream_reports.py` et `stream_contract.php` ajoutés à la liste des sources empreintées. Tests `test_a03_source_roots_are_present_and_required` (les trois sources `a03/Policy.php`, `Report.php`, `Site.php` présentes dans l'empreinte ; racine retirée → `A22_SOURCE_ROOT_MISSING`) et `test_a03_policy_mutation_changes_executed_source_snapshot` (mutation de `Policy.php` sur miroir jetable → empreinte changée). Verts.

### Instruction 4 — valider le contenu final des rapports non-JSON. **Appliquée** (au-delà du minimum demandé).
Nouveau module `stream_reports.py` : contrats de contenu propres par outil (A03/A11/A12/A14/A15/A16/A17/A18/A19) sur JSON **et** Markdown **et** CSV (schémas figés, types de compteurs, cohérence des projections/totaux, en-têtes CSV, préfixes Markdown exacts). `complete()` (`stream_guard.py:140`) appelle désormais `stream_reports.validate(tool,output)` : un dossier dont le contenu final n'est pas validé est refusé (défaut fermé). S'ajoute un **liage par empreinte** : `stream_contract.php` (auto_prepend, `stream_guard.py:170`) enregistre, avant tout code du site, un `register_shutdown_function` qui gèle les fichiers terminés ; le parent (`final_binding`, `stream_guard.py:119`) ne statue qu'après les deux EOF et la terminaison, sans réémettre le protocole interne. Tests : `test_final_reports_contract_rejects_silent_shutdown_contamination`, `test_json_numeric_slots_cannot_be_replaced_by_site_text`, `test_private_completion_binds_every_final_byte`, `test_private_binding_refuses_oversized_file_before_publication`. Verts.

### Instruction 5 — cinquième canari : contamination d'un fichier. **Appliquée.**
`channels.py` ajoute **deux** canaris fichiers silencieux (sans écriture sur les flux) : `shutdown_file` (ajout à un `.md`/`.csv`/`.json` existant) et `shutdown_json` (JSON valide contaminé). Chacun est exigé en refus **et** absence de publication du canari. `replay.py` ajoute le témoin `mutation_without_final_contract_leaks` : sans les contrôles finaux, le contenu contaminé ressort réellement dans la copie jetable — preuve que c'est bien le contrat qui ferme la porte. `verify.py` compte maintenant 29 contrôles additionnels par outil concerné (31 pour A12 avec les sondes noyau). La clause « absent de tous les fichiers produits » n'est donc plus satisfaite à vide. Couvert en code et en tests.

### Instruction 6 — revalider le paquet natif (matrice + banc). **Non vérifiable par moi — déclarée appliquée par Hermès.**
Même limite que les deux relecteurs du 1ᵉʳ tour : la matrice et le banc natif A-22 demandent Docker/WSL et un interpréteur Windows 3.14 ; hors de ma commande autorisée. Je ne les ai donc **pas** rejoués. Hermès déclare (`FINALISATION.md`, `notes.md`) un paquet neuf `preuves/final` issu de `a22-corrections-1753/matrix-final-02` (42 commandes code 0, 22 banques natives, sources stables). Le reçu `candidate-verification.json` est régénéré et cohérent avec le nouveau `verify.py` (comptes `A12:unit=15`, `A14:unit=8`, `A16:unit=23`, etc.), statut `CANDIDAT_GATE_PARENT`, `readiness_claimed:false`. **C'est un reçu producteur, pas une revalidation indépendante.** Cette instruction, par nature, reste à exécuter dans un environnement autorisant Docker/WSL — c'est exactement la réserve que la fusion posait (« ni Claude ni Codex n'a pu le valider »).

## 2. Résultat des tests

Lancés par moi, en local, `C:/…/python.exe 3.14.6` :

```
python -m unittest wp.tests.a22.test_corrections   → Ran 8 tests  OK
python -m unittest wp.tests.a22.test_guard
                   wp.tests.a22.test_contract       → Ran 17 tests OK
```

**25 tests Python A-22 verts**, dont les 8 tests de non-régression de la fusion (`test_corrections.py`) qui couvrent une à une les instructions 1 à 5.

Non rejoués par moi (hors commande autorisée / Docker-WSL requis), donc appuyés sur reçu seulement :
- la **matrice native A-22** (`matrix.py`) et le **vérificateur** (`verify.py`) — reçu `candidate-verification.json` (159 PASS par console, code 0) ;
- la **non-régression PHP** (`rejouer.ps1`, 1123+ tests). Le 1ᵉʳ tour l'avait rejouée verte avant correction ; les corrections ajoutent du Python et un fichier PHP autonome (`stream_contract.php`, chargé en auto_prepend, hors des lots testés). Le parent déclare un rejeu global vert (`FINALISATION.md` : 1 126 tests), non revérifié par moi.

## 3. Régressions ou modifications non demandées

- **`test_contract.py:136`** : l'attente passe de `assertTrue` à `assertFalse` (« un rapport ne se résume plus à ses noms de fichiers »). Ce n'est **pas** une régression : c'est la conséquence directe et assumée de l'instruction 4 (le contenu est désormais validé), accompagnée du commentaire idoine.
- **`stream_contract.php` ajouté à la commande PHP** (`auto_prepend_file`) : nouveau comportement, c'est le mécanisme de l'instruction 4/5, documenté.
- **Périmètre de l'ouvrier A-22 propre.** Les seules sources touchées par la correction sont dans `wp/outils/bascule/`, `wp/tests/a22/`, `production/A-22/`. Les autres fichiers du dépôt modifiés sur l'intervalle (`A-FAIRE*.md`, `briefs/…`, `corrections/B-06.md`, `files/rapports/…`, `docs/…`) relèvent de la voie 2 et du processus parent concurrents, pas de ce lot (confirmé par `FINALISATION.md`). Aucune fuite de périmètre imputable à A-22.
- Aucun secret, aucune donnée réelle introduite ; canaris et fixtures restent fictifs ; mutations confinées à des copies jetables / scratch.

## 4. Verdict

**Remonté à Ced — pour information, pas pour arbitrage : un point de fond reste ouvert, mais il n'est pas tranchable par moi.**

Les cinq instructions corrigeables en code (1 à 5) sont **appliquées et prouvées par des tests que j'ai relancés verts** (25/25). Les trois constats importants de la fusion (P1 code A12, P2 empreintes A03, P3 contenu des rapports) sont traités à la racine, chacun avec son test de non-régression.

Reste l'**instruction 6** : la revalidation indépendante du paquet natif (matrice + banc, Docker/WSL, Windows 3.14) n'a été faite par **personne d'indépendant** — ni les deux relecteurs du 1ᵉʳ tour, ni moi, faute d'environnement autorisé. Hermès l'a rejouée de son côté (reçu `candidate-verification.json`, 159/159), mais la doctrine (« le reçu producteur ne vaut pas validation ») et la fusion elle-même exigent une exécution indépendante avant clôture.

Concrètement :
- **Côté code et tests à ma portée** : rien ne bloque, tout ce qui pouvait être vérifié l'a été et est vert → *prêt pour la validation de Ced* sur ce volet.
- **Côté preuve native** : il manque un rejeu indépendant de la matrice/banc A-22 dans un environnement Docker/WSL. Ce n'est pas un problème de code ; c'est une étape de validation à ordonnancer (sur le NUC de Ced, ou par une tâche habilitée). Tant qu'elle n'est pas faite, le lot ne peut pas être clos « par les preuves » au sens de la doctrine §6.

**Décision à Ced :** lancer (ou faire lancer) une fois la matrice et le banc natif A-22 corrigés dans un environnement Docker/WSL autorisé ; si ce rejeu est vert de façon indépendante, le lot est prêt à clore. Le code, lui, est conforme aux corrections demandées.

Rappel doctrine : ce verdict n'est pas un GO.
