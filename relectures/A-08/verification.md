# Vérification A-08 — second et dernier tour

Date : 25 novembre 2026. Vérificateur : Claude (lecture seule sur le code, exécution des
tests du lot). Base comparée : version relue (`c8f2679`, 21:43) → `HEAD` (22:23).
Je n'ai pas refait de relecture complète : j'ai contrôlé **ce qui a changé depuis la fusion**
(`git diff` sur `wp/outils/bascule` et `production/A-08`) et rejoué ce qui était exécutable.

Fichiers effectivement modifiés par Hermès depuis la version relue :
`wp/outils/bascule/a08/sequence.py`, `wp/outils/bascule/repetition.md`,
`wp/tests/a08/test_sequence.py`, `wp/tests/a08/inside.py`, plus les artefacts de production
(`production/A-08/` : manifeste, PRET, verifier.py, sceller.py, preuve scellée régénérée).

---

## 1. Les six instructions de `corrections/A-08.md`

### Instruction 1 — R4 + II.4 : sceller la bonne empreinte — **Appliquée**
- Le `base.rglob('*')` disparaît. Une **clôture de dépendances explicite** `DEPENDENCIES`
  est déclarée (`sequence.py:7-16`) et hachée en identité (`sequence.py:122`).
- Elle **inclut** le code hors arbre qui décide du verdict :
  `../../plugins/imagine-non-regression/src/Report.php`, `PhpLog.php`, `Policy.php`,
  `../staging/runtime-probe.php` + garde staging (`sequence.py:12-15`).
- Elle **exclut** a09, a10, `inventorier-codes` (vérifié : clôture de 23 entrées, aucune
  mention a09/a10/inventorier-codes).
- Test ajouté `test_dependency_closure_refuses_external_code_but_ignores_other_lots`
  (`test_sequence.py:204-224`) : modifier `src/Report.php` **refuse la reprise avant tout
  appel natif** (compteur d'appels inchangé, `A08_IDENTITY_CHANGED` au rapport) ; toucher
  a09/a10/inventorier-codes ne bloque pas. Reproduit côté natif par
  `external_comparison_change_refused_before_native` (`inside.py:128-135`, aucun `a04` créé).

### Instruction 2 — R1 : un refus produit toujours un rapport cohérent — **Appliquée**
- L'`except` nu est remplacé par un gestionnaire qui, verrou tenu et état accessible,
  **écrit `report()`** (`sequence.py:199-222`, verrous conservés via `ExitStack`
  `sequence.py:83,99`). Si l'état est inaccessible ou le verrou non acquis, il **signale
  explicitement sur stderr** `A08_REPORT_NOT_UPDATED : … ne décrit pas cette tentative`
  (`sequence.py:220-221`).
- Tests : `test_missing_input_after_success_replaces_stale_report` (entrée disparue après
  succès → `ARRÊT`, plus de `Statut : TERMINÉ`), `test_concurrent_refusal_leaves_report_and_warns_stderr`
  (exécution concurrente : rapport **non écrasé** + avertissement stderr),
  `test_unreadable_checkpoint_reports_without_erasing_failure`, `test_incomplete_new_pass_refreshes_report`
  (`test_sequence.py:226-258`). Natif : `missing_input_current_stop_report`,
  `incomplete_new_pass_current_stop_report` (`inside.py`).

### Instruction 3 — R2 : documenter l'issue après anomalie (code 2) — **Appliquée**
- `repetition.md:53-57` ajoute un bloc **« Code 2 : »** : la reprise ne refait pas la
  réception ; conserver état et preuves d'échec ; **restaurer la sauvegarde de départ
  vérifiée (base ET fichiers)** ; recommencer les six étapes dans un **nouvel état** ; ne
  supprimer ni checkpoints ni verrous. Conforme mot pour mot à l'instruction (doctrine :
  restaurer puis nouvel état).

### Instruction 4 — II.5 : capter `ImportError` (défaut technique) — **Appliquée**
- L'`except` capte désormais `ImportError` → code d'arrêt stable `A08_LINUX_REQUIRED`
  (`sequence.py:199-201`), sans trace. Test `test_missing_fcntl_stable_no_traceback`
  (`test_sequence.py:260-271`). Preuve réelle Windows : `production/A-08/windows-importerror.json`
  (exit 1, `no_state_created: true`, stderr = `A08_LINUX_REQUIRED` + `A08_REPORT_NOT_UPDATED`,
  pas de `Traceback`) — rejouée et confirmée.

### Instruction 5 — Limite de rejeu : Docker A-08 dans la porte verte + régénérer la preuve — **Appliquée (côté production) ; Partiellement de mon côté**
- La preuve scellée a été **régénérée** : nouvelle empreinte `production/A-08/preuves/0bfc90415810`
  (l'ancienne `2bbcefb53170` n'est plus référencée). Le manifeste pointe cette preuve.
- Cette preuve **contient le rejeu Docker A-08** : `unit.log` se termine par `OK`,
  `Ran 21 tests` = `counts.a08_unit`, intégration `result.json` exit 0 (59 checks tous `ok`),
  régressions a02/a03/a04/a05 vertes (`runner.json` exit 0, 11 checks).
  L'identité scellée des deux parcours (`classic`, `hpos`) vaut la **clôture vivante**
  (`identity.tools == DEPENDENCIES` recalculé).
- **Limite de mon côté (identique aux deux relecteurs)** : je n'ai **pas** pu ré-exécuter
  moi-même le banc Docker A-08 (`wp/tests/a08/run.py`) ni la suite PHP (`wp/tests/rejouer.ps1`) :
  Docker/WSL + extensions sous licence hors d'atteinte, et `run.py` écrit sous `production/`
  (hors de mes droits d'écriture). J'ai donc **re-lu et re-contrôlé** la preuve scellée octet
  par octet via la logique de `production/A-08/verifier.py` (lecture seule) — tout l'invariant
  A-08 ressort vert. La re-exécution Docker indépendante par un relecteur reste le seul point
  non rejoué.

### Instruction 6 — R3 / II.2 / II.3 : un seul rapport, passages identifiés, durées attribuées — **Appliquée**
- `report()` réécrit (`sequence.py:46-67`) : sections **« ## Passage N »**, comparaison
  **par passage** (`comparisons` clé par numéro, `sequence.py:181`), durées marquées
  **« cumulées dans ce passage »** (`sequence.py:51`), chaque essai porte `pass`
  (`sequence.py:155`). Un seul `rapport.md` (contrôle `glob('rapport*.md') == 1`).
- Test `test_pass_reports_retain_first_comparison_and_attributed_durations`
  (`test_sequence.py:273-284`) : après un second passage, `Passage 1`/`Passage 2`,
  `attendus : 4` **et** `attendus : 0` coexistent (le premier passage n'est plus écrasé).

### III.6 (pour Ced) — question de style sur `repetition.md` — **Correctement déférée, non tranchée**
- `production/A-08/PRET` porte `ced_question_deferred: "III.6 : … aucune décision réelle prise"`.
  Hermès n'a pas tranché une question qui touche au réel : conforme au CLAUDE.md et à la
  doctrine §6. **Elle reste à arbitrer par Ced.**

---

## 2. Résultat des tests

- **`production/A-08/verifier.py` (lecture seule, mes droits)** : exécuté. **S'arrête en
  échec** à la première boucle sur une catégorie `protected` — `AssertionError('protected',
  'wp/outils/bascule/tester-redirections.md')`. Cause isolée : **dérive de fichiers du lot
  voisin A-09** (voir §3), **pas** un défaut A-08.
- **Re-contrôle lecture seule ciblé A-08** (même logique que `verifier.py`, en neutralisant
  le bruit A-09) : **tout vert**. Détail vérifié :
  - Dérive manifeste **hors A-09 = 0** dans les cinq catégories ; catégories propres A-08
    `evidence` (176), `history` (782), `delivery` (18) : **zéro dérive**.
  - Clôture scellée = 23 entrées, exclut a09/a10/inventorier-codes, inclut `Report.php` et
    `runtime-probe.php` hors arbre.
  - Preuve `0bfc90415810` : `runner.json` exit 0 (11/11), `result.json` exit 0 (59/59),
    `unit.log` → `OK`, `Ran 21`, les six nouveaux tests présents, identité des deux parcours
    = clôture vivante, passages `[1]*7 + [2]*6`, comparaisons par passage présentes.
  - `repetition.md` documente « Code 2 », preuve ImportError Windows stable.
  - `PRET.manifest_sha256` = sha vivant de `manifeste.json` → manifeste **intact**
    (non altéré par le commit A-09).
- **Banc Docker A-08 (`run.py`) et suite PHP (`rejouer.ps1`)** : **non rejoués** par moi
  (Docker/WSL + licences indisponibles ; exécution de script bloquée par le harnais ;
  `run.py` écrit sous `production/`, hors droits). Preuve scellée re-lue à la place.

**Bilan tests : tout ce qui est propre à A-08 est au vert. Seule la ré-exécution Docker
indépendante manque, comme au premier tour.**

---

## 3. Régression ou modification non demandée

- **Aucune régression dans le code A-08.** Les changements de `sequence.py` au-delà des six
  instructions (refonte du verrouillage par `ExitStack`, re-vérifications de symlink,
  `resolve(strict=True)` déplacé après prise du verrou, passage du schéma `v1`→`v2`) sont
  **au service de l'instruction 2** (le verrou doit tenir jusqu'au gestionnaire de refus pour
  écrire le rapport) et sont couverts par les tests de limites et la preuve scellée. Le schéma
  `v2` refuse les anciens états `v1` (`A08_IDENTITY_CHANGED`), choix **documenté**
  (`repetition.md:60`). Outils natifs intacts, aucun garde-fou A03/A04/A05 retiré.
- **Point à remonter (hors instructions, pas un défaut de logique A-08) — `verifier.py` est
  rouge sur l'arbre courant.** Le manifeste A-08 a été scellé à 22:02 avec
  `protected_and_history_drift: []` (`controle-perimetre-corrections.json`). Le lot **A-09** a
  ensuite avancé (commit `7a75199`, 22:13 : son `PRET`, son manifeste, son
  `tester-redirections.md`, `a09/check.py`, `test_http.py`…). Comme les catégories larges
  `protected` (8 fichiers) et `sources` (2 fichiers) du manifeste A-08 **photographient aussi
  des fichiers A-09**, `verifier.py` échoue désormais contre l'arbre courant. **Les dix
  fichiers en dérive sont tous A-09** ; aucun fichier A-08 n'a bougé. Hermès avait d'ailleurs
  noté les voies concurrentes (`global_scope_receipt`), mais la photo A-08 déborde sur le
  périmètre d'A-09. **Conséquence concrète : si Ced lance `verifier.py` en l'état, il s'arrête
  sur la dérive A-09.** Remède : re-sceller le manifeste A-08 après stabilisation d'A-09, ou
  restreindre les catégories `protected`/`sources` au seul périmètre A-08. C'est une hygiène
  d'empaquetage inter-lots, pas une correction de logique à refaire.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les six instructions de `corrections/A-08.md` sont **appliquées** (instruction 5 appliquée
côté production, partiellement de mon côté faute de Docker indépendant) ; les tests propres à
A-08 sont **au vert** et re-contrôlés octet par octet ; **aucune régression** dans le code du
lot. La correction centrale (R4 : sceller le code qui décide du verdict, hors arbre) est bien
en place et testée avant tout appel natif.

Deux choses accompagnent cette validation, à l'attention de Ced — **aucune n'est un défaut de
logique A-08, aucune n'invalide les corrections** :

1. **III.6** (style des intros de `repetition.md`) reste **à arbitrer par Ced** : le lot porte
   une question qui touche au réel, il n'est donc pas clôturable par les seules preuves
   (doctrine §6). Défaut proposé dans la fusion : garder le contenu exact, ajouter une ligne
   simple par bloc.
2. **Re-sceller / restreindre le manifeste A-08** pour que `verifier.py` repasse au vert sur
   l'arbre courant (dérive due au lot A-09, §3), et — idéalement — faire rejouer le banc
   Docker A-08 dans un environnement qui le permet, pour lever la dernière limite de
   re-exécution indépendante (instruction 5).

*Rappel doctrine : ce verdict n'est pas un GO. Aucun retrait ni aucune bascule réelle n'est
décidé ici ; préalables A03/A04/A05 et GO écrit de Ced restent requis avant toute opération
sur le vrai site.*
