# Vérification A-28 — second et dernier tour

Vérificateur : Claude. Objet : contrôler que les corrections de `corrections/A-28.md` ont été appliquées par Hermès après la fusion. Base : `git diff` depuis le commit de relecture (`2596510a`, 27/11 01:43) sur `wp/` et `production/A-28/`, plus rejeu des tests. Ce n'est pas une relecture complète ; je ne reprends que les cinq instructions de la fusion, les tests, et les écarts.

Rappel doctrine §6 : ce verdict n'est pas un GO sur le réel.

## 1. Instructions de la fusion — état

### Instruction 1 (important, I1) — compter les `postmeta` résiduels d'un message connu dont le parent a été purgé, avec provenance fiable, refus `FORM_MESSAGES_REMAIN`, sans suppression générale des `postmeta`
**Appliquée.**
- Provenance fiable des identifiants : `wp/outils/staging/engine.php:111-119` lit `context['form_post_ids']`, valide que c'est une liste d'entiers positifs (sinon `CONTEXTE_REFUSE`) et amorce `knownFormPosts` ; snapshot conservé entre phases (`engine.php:20-21`, `:411-412`).
- Comptage des `postmeta` résiduels dans `verifier()` : `engine.php:794-796` (`$kind === 'postmeta' && isset($this->knownFormPosts[post_id]) → ++$formResidues`), agrégé `engine.php:757,763`, refus `engine.php:891-893` (`FORM_MESSAGES_REMAIN`).
- Pas d'extension à une purge générale : `transform()` ne supprime que les `postmeta` des posts connus (`engine.php:420-423`) ; un orphelin de type inconnu (`post_id 99`) est conservé — vérifié par le test `unknown_orphan_not_globally_purged` (`wp/tests/a28/unit.php:93`).

### Instruction 2 (important, I1 — preuve) — témoin de mutation où seule la purge des `postmeta` est omise, `verifier()` doit refuser
**Appliquée.**
- Unitaire PHP : `wp/tests/a28/unit.php:78-119` — `known_orphan_postmeta_counted` (parents 41/42 absents, meta orphelines conservées, provenance `[41,42]` → `ok=false`, `form_message_residues=2`, `FORM_MESSAGES_REMAIN`, bootstrap non lancé) et `in_memory_provenance_survives_parent_and_revision_loss` (parent + révision retirés en cours de route, résidu toujours compté).
- Contrat de témoin : `wp/tests/a28/test_verify.py:110-134` — `test_orphan_witness_semantics_not_just_outer_hash` sur `orphan_contract`, mutation `omit_only_postmeta_purge`, mutant `exit 0 / ok=true` opposé au refus `exit 1 / FORM_MESSAGES_REMAIN`.
- Matrice native : contrôles `ORPHAN_IMPORT / ORPHAN_MUTATION / ORPHAN_ORACLE / ORPHAN_PROVENANCE / ORPHAN_REFUSAL` et `NATIVE_MUTATION_WITNESS` déclarés dans `production/A-28/rejeu.json:96-112` ; reçus `RESULTATS.md:5-10` (« contrôle retiré 0 / contrôle rétabli 1 »).

### Instruction 3 (mineur, M1) — `standard.md:11` : citation officielle exacte pour `fluentform_draft_submissions` et `ff_scheduled_actions`, ou marquer « doute »
**Appliquée** (option « doute » de l'instruction).
- `production/A-28/standard.md:11` remplacé par « **Doute explicite sur la justification documentaire** … aucune phrase officielle exacte … inclus par prudence … pas présentés comme des stockages officiellement cités ». Aucune citation ajoutée : Hermès a retenu la porte de secours prévue par la consigne, pas la citation. Liste inchangée (`form-policy.json` : six tables, deux types).

### Instruction 4 (mineur, décision technique) — ne plus relire `form-policy.json` dans le constructeur d'exception
**Appliquée.**
- `wp/outils/staging/form-decision-refused.php:12-18` : `__construct(string $table, array $tables)` reçoit la liste déjà chargée et la valide par `in_array` ; plus aucun `file_get_contents`. Appel : `engine.php:66` (`new FormDecisionRefused($kind, $this->formTables)`).

### Instruction 5 (mineur, décision technique) — refuser tôt toute décision dont le suffixe ∈ liste, présente ou non dans l'archive → `FORM_MESSAGES_DECISION_REFUSED`
**Appliquée.**
- `wp/outils/staging/engine.php:62-69` : la boucle de décisions teste `in_array($kind, $this->formTables)` **sans** exiger `isset($inventory[$table])` ; `garder`/`anonymiser` → `FormDecisionRefused`.
- Test dédié : `wp/tests/a28/unit.php:43-51` — `absent_closed_refusal_garder/anonymiser` (table de la liste absente de l'archive → code `FORM_MESSAGES_DECISION_REFUSED`, plus `DECISION_INVALIDE`).

Les cinq instructions sont **appliquées**. Aucune « partiellement », aucune « non appliquée ».

## 2. Tests

Commande autorisée, sans argument, en conteneur jetable (`network=none`, `rootfs=ro`, `wp` monté en lecture seule) :

```
REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
OUTILS : 21 outils, 553 contrôles, 0 échecs ; hors rejeu : aucun
PAQUETS : 1 vérifié (A-28), 0 échecs
T01 TOOL : a28 ; 82 controls ; 0 failures ; exit=0
```

Point important pour I1 : l'outil `a28` passe de 62 à **82 contrôles** ; les nouveaux témoins orphelins tournent **réellement en PHP** dans ce rejeu. La réserve de la fusion (« I1 n'est démontré que par analyse statique, n'a pas été exécuté en PHP ») est donc levée pour le chemin unitaire et le contrat de témoin.

**Limite de vérification** (inchangée depuis la relecture) : je n'ai lancé que la commande autorisée. La matrice native Windows (`matrix.py`) et `production/A-28/verify.py` écrivent sous `production/` (lecture seule pour moi) ; je les contrôle **par lecture** des reçus gelés (`RESULTATS.md`, `rejeu.json`, `preuves/final/native/**`), pas par ré-exécution. Les deux contextes natifs (`utf8`, `cp1252`) y sont `PASS`, et le transport de la provenance `form_post_ids` par le vrai import (contrôle `ORPHAN_IMPORT`) n'est attesté que par ces reçus, pas rejoué nativement par moi.

## 3. Régressions et modifications non demandées

- **Refonte de structure (non demandée littéralement, sans régression).** `wp/outils/staging/lib.php` (≈858 lignes) est éclaté en `engine.php`, `store.php`, `guard.php`, `form-decision-refused.php` ; `lib.php` n'est plus qu'un manifeste de `require`. Ce n'était pas dans les cinq instructions, mais c'est porté par la porte **PSR-12** ajoutée au lot (gate `psr12` dans `rejeu.json`, « chaque déclaration a son fichier distinct » `RESULTATS.md:12`, équivalence des jetons dans `preuves/final/format-equivalence.json`). `Guard` et l'interface `Store` sont des extractions propres (comportement inchangé) ; la logique `Engine` est identique hors corrections. Suite complète verte et différentiel hors-formulaires préservé (seul le compteur zéro s'ajoute). Acceptable, tracé ici pour Ced.
- **Attente de test ajustée.** `post_residue_*` passe de `3` à `6` résidus (`unit.php:135`) : conséquence directe du nouveau comptage des `postmeta` de posts connus, pas une régression.
- **Autres lots dans le diff.** Le diff depuis le commit relu touche aussi a26, a27, a29, a30, t01 : travail parallèle hors périmètre A-28, suite globale verte ; pas une régression d'A-28.
- **Fichier parasite.** Un fichier non suivi `prefix}u0024s` traîne à la racine (artefact de quoting shell) ; sans rapport avec A-28, à nettoyer hors lot.

Aucune commande de Ced modifiée, aucune nouvelle extension, aucune donnée ou archive réelle, aucun secret.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq corrections de la fusion sont appliquées et citées ; la suite autorisée rejoue au vert (1151 tests, 0 échec) et exécute désormais en PHP les témoins orphelins d'I1 ; aucune régression ni modification non demandée problématique. Il ne reste **aucun problème de fond** à remonter.

Ce qui relève encore de Ced n'est pas un défaut mais sa part de validation : la question « touche au réel » de la fusion — **l'import doit-il supprimer aussi les types de contenu hors liste fermée ? oui / non** — reste ouverte, avec le défaut prudent déjà implémenté (« non — conserver + signaler »). Conformément à la doctrine §6, ce « prêt » ne vaut que pour la clôture du lot de code et n'autorise aucun accès au réel.
