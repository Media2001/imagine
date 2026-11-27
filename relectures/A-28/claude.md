# Relecture A-28 — Les messages de formulaires ne survivent pas à l'import

Relecteur : Claude, indépendant. Brief : `briefs/A-28-messages-de-formulaires-et-import.md`.
Cahier des charges : §4.4. Doctrine : §3. Je n'ai pas lu `codex.md`. Pas de fusion à ce stade.

Rappel : ce verdict n'est jamais un GO (doctrine §6).

## Rejeu de la suite PHP

Commande autorisée, sans argument :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, réseau coupé, dépôt monté en lecture seule (`network=none ; rootfs=ro ; mount=…/wp:ro`). Dernière ligne :

```
REJEU : 1151 tests, 36062 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Outil du lot : `T01 TOOL : a28 ; 62 controls ; 0 failures ; exit=0`. Les suites d'A-01 et voisines (a20–a29) ressortent vertes dans le même rejeu.

**Limite de vérification.** Je n'ai lancé que la commande autorisée. Je n'ai **pas** rejoué la matrice native Windows (`wp/tests/a28/matrix.py`), ni `production/A-28/verify.py` : ils écrivent sous `production/` (lecture seule pour moi) et sortent du périmètre d'exécution donné. La preuve du vrai parcours d'import avec canaris (`preuves/final/native/**`, `before/native.json`) est donc contrôlée **par lecture** des journaux et des JSON gelés, pas par ré-exécution. Les deux contextes natifs (`utf8`, `cp1252`) y sont `PASS`, exit 0 ; la preuve d'avant correction est `baseline:true`. Je le signale au lieu de l'affirmer comme rejoué.

## 1. Conformité

Le lot fait ce que le brief demande, sans plus.

- **Standard d'abord.** `production/A-28/standard.md` : liste fermée en dix points, six tables Fluent Forms et deux types Flamingo, chaque forme adossée à une citation de doc/source officielle (Flamingo `class-inbound-message.php`, `class-contact.php` sur le dépôt de l'éditeur ; Fluent Forms `developers.fluentforms.com/database/`). CF7 seul « which doesn't store submitted messages » : la page `contactform7.com` bloquée par WAF est honnêtement écartée comme non-preuve. `wpcf7_contact_form` (définition de formulaire, pas un message) est explicitement **conservé**. Conforme à la doctrine §4 « standard d'abord ».
- **Liste = politique, pas heuristique.** `wp/outils/staging/form-policy.json` énumère les six suffixes et deux types ; aucun motif générique « form »/« message ». Confirmé par le test `exact_suffix_only` (`x_fiction_fluentform_submissions` n'est pas touché).
- **Une seule source partagée.** La même `form-policy.json` est lue côté PHP (`lib.php:55`) et côté Python (`staging-court/table_policy.py:25`), et transportée dans le vrai payload d'import (`test_policy.py::test_dependency_in_actual_transfer`). Pas de liste parallèle cachée.
- **Trois lignes au mode d'emploi** de l'import : `wp/outils/staging-court/README.md:188-190` (ce qui est vidé, ce qui est refusé, le compteur + types inconnus). `production/A-28/PRET` présent.
- **Pas de sur-périmètre.** Aucune commande de Ced modifiée, aucune nouvelle extension, aucune lecture de l'archive d'Imagine. Comparé byte à byte dans le différentiel hors-formulaires.

Interprétations signalées (conformes à la doctrine §1) : inclusion de `fluentform_logs` (purge entière), `fluentform_draft_submissions` et `ff_scheduled_actions` « par prudence » — justifiée dans `standard.md`, défendable car ces tables peuvent porter du texte de visiteur.

## 2. Exactitude métier — cas déroulés à la main

J'ai déroulé le code (`wp/outils/staging/lib.php`, `staging-court/table_policy.py`) sur les formes du brief.

**Cas A — canari dans une table dédiée de la liste, import par défaut.**
Constructeur : suffixe ∈ `formTables` → exclu des tables inconnues (`lib.php:65-66`), aucune décision requise. `transform()` : `in_array($kind, $this->formTables)` → `replace($table, $row, null)` pour chaque ligne (`lib.php:384-388`). Table vidée sans décision. → canari supprimé. Conforme. (tests `legacy_forced_empty_*`, Python `test_closed_tables_always_empty`.)

**Cas B — canari dans un type de contenu de la liste (`flamingo_inbound`/`flamingo_contact`), import par défaut.**
`formPostIds()` (`lib.php:352-370`) prend les posts de ces types, puis, par point fixe, leurs révisions transitives. `transform()` supprime ces posts et leurs `postmeta` (`lib.php:384-388`). → message, révisions et métadonnées supprimés. Conforme. (test `known_posts_revisions_deleted_*` : posts `[4,5]` restants = magazine + définition CF7 ; `known_postmeta_deleted_*` : seul `post_id 4` reste ; nested revision ID 3→2→1 bien supprimée.)

**Cas C — canari dans une table dédiée INCONNUE, import par défaut puis `garder`.**
Hors liste → traitée par la politique A-01 existante. Par défaut (`table_policy_version=1` / `Policy.resolve`) : famille « vider » → table vidée, canari supprimé. Avec `garder` : décision acceptée (ce n'est pas une table de la liste), table conservée, canari **reste** — c'est le comportement A-01 voulu et la preuve attendue du brief. Conforme. (`nonform.php` : `x_fiction_messages` gardé ; `before/native.json` atteste le canari résiduel sous `garder`.)

**Cas D — `garder`/`anonymiser` sur une table de la liste.**
`lib.php:85-88` : `isset($inventory[$table]) && $kind ∈ formTables && $decision !== ['action'=>'vider']` → `throw FormDecisionRefused($kind)`. `Command::diagnostic` (`command.php:16-19`) rend `{stage: native_neutraliser, code: FORM_MESSAGES_DECISION_REFUSED, table: <suffixe>}`, exit 78 (`command.php:112`) — comme les refus d'A-01. Point important : `command.php:108` **n'ajoute pas** la coordonnée PDO (dernière table visitée) pour ce refus → aucune valeur, aucun chemin de données. Côté Python : `table_policy.py:35-38` lève `FORM_MESSAGES_DECISION_REFUSED` détail `{table: <suffixe>}`, étape `sql_preflight`. Étape + code + table de la liste ; **aucune valeur** (test `test_refusal_receipt_exact_and_no_values` : l'entrée `A28_PRIVATE_Jerome` n'apparaît jamais ; test PHP `no_message_output_*`). Conforme au brief (« étape, code, table ; aucune valeur »).

**Cas E — vérification d'une copie où un message reste.**
`verifier()` relit à neuf (`new self`, `lib.php:645`), compte `formResidues = count(formPostIds) + Σ lignes des tables de la liste` (`lib.php:663,668-669`). `>0` → `FORM_MESSAGES_REMAIN` dans `issues`, `ok=false` (`lib.php:763-764`), et la sonde n'est **pas** lancée (`lib.php:780-781` ajoute `SONDE_NON_EXECUTEE_DONNEES_REFUSEES`). Donc refus **sans amorcer WordPress**. Le rapport expose `form_message_residues` = un nombre ; jamais le texte. Conforme (tests `residue_numeric_*`, `residue_no_bootstrap_*` : `calls===0`).

**Cas F — mutation témoin (contrôle retiré) et résidu créé pendant le bootstrap.**
Après la sonde et sans défaut, `verifier(null)` est rejoué et un résidu introduit pendant le chargement est repris (`lib.php:804-810`) → test `residue_introduced_during_bootstrap_refused`. Les témoins de mutation (blocage spécifique retiré dans la copie du conteneur) sont décrits dans `red-green.json` ; je les vérifie par lecture, pas par ré-exécution (voir limite ci-dessus).

**Cas G — type de contenu INCONNU (`fiction_magazine`).**
Non supprimé ; `verifier()` émet l'avertissement `TYPES_CONTENU_INCONNUS_CONSERVES` et le liste dans `unknown_post_types` (`lib.php:773-775,816`). Aucune décision prise — conforme à la consigne « ne décide rien… les contenus du magazine en font peut-être partie ». (test `unknown_type_remains_warning_*` : `form_message_residues===0`, `ok===true`.)

Tous les cas concordent code ↔ brief.

## 3. Tests

- Rejeu global vert (voir plus haut), outil `a28` : 62 contrôles, 0 échec.
- Les tests vérifient la **règle**, pas le code : canari fictif (`A28_FICTIVE_UNIT`) tracé jusqu'à son absence ; différentiel deux-process entre ancien et nouvel import prouvant que seul le compteur `form_message_residues` (à zéro) s'ajoute, tables/rapport/diagnostics historiques identiques (`nonform.php/.py`).
- Cas limites couverts : révisions imbriquées, suffixe exact vs quasi-homonyme, table en VUE (`read_only_residue_never_verified`), résidu pendant bootstrap, décision numérique non-form qui garde le code A-01 (`non_form_numeric_decision_keeps_A01_code` → `DECISION_INVALIDE`).
- Preuve d'avant correction (`before/native.json`, `baseline:true`) : atteste le **défaut**, pas sa correction ; 108 contrôles verts sur l'ancien import. Bonne discipline de non-régression (doctrine §4).

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : archives fabriquées, noms manifestement fictifs, adresses `@example.org` (doctrine §3).
- Aucune valeur rendue aux refus : le code de refus formulaire n'expose que le suffixe de table de la liste fermée, validé contre la politique du dépôt, jamais du texte de site (`lib.php:23`, `command.php:106-112`). Les journaux d'erreur bruts sont coupés (`command.php:42-43`).
- Le compteur de vérification ne sort qu'un entier.
- `§4.4` (paywall/sécurité) n'est pas directement touché par ce lot ; rien n'y est régressé (les suites paywall voisines restent vertes au rejeu).

## 5. Doctrine

- Conventions §5 : `declare(strict_types=1)`, espace de noms `Imagine\Staging`, préfixe `imagine_` pour l'option globale, codes constants (jamais du texte d'interface issu de données). Conforme.
- Standard d'abord : le sur-mesure se limite à ce que WordPress/les extensions ne font pas ; la liste fermée cite ses sources. Conforme §4.
- Idempotence de l'import vérifiée (test `idempotent_*`). Rejouable sur copie fraîche (doctrine §4).

## Points

Aucun **bloquant**, aucun **important**.

**Mineurs / limites** (ne bloquent pas la clôture) :

1. **(mineur)** `lib.php:28` — le constructeur de `FormDecisionRefused` fait une lecture de fichier (`file_get_contents(form-policy.json)`) à l'intérieur d'un constructeur d'exception, sans garde d'E/S. Déterministe ici (le fichier a déjà été lu par `Engine`), mais une exception d'E/S à cet instant masquerait le refus d'origine. Proposition : passer la liste déjà chargée au lieu de relire le fichier. À arbitrer après coup (décision technique).

2. **(mineur)** `lib.php:85` — le refus `garder`/`anonymiser` sur table de la liste exige `isset($inventory[$table])`. Pour une décision posée sur une table de la liste **absente** de l'archive, le refus retombe en `DECISION_INVALIDE` (code A-01 générique) au lieu de `FORM_MESSAGES_DECISION_REFUSED`. Sans risque de donnée (rien à conserver), mais le code de refus diffère. Proposition : refuser tôt toute décision dont le suffixe ∈ liste, présente ou non. Décision technique, défaut proposé : laisser tel quel (le refus a lieu).

3. **(limite, pas un défaut)** Le compteur de résidus porte sur les tables de la liste et les posts de types de la liste. Un `postmeta` **orphelin** portant un message Flamingo (post parent inexistant dans l'archive) ne serait ni supprimé ni compté comme résidu formulaire — il resterait « autre ». Hors périmètre de la liste fermée (cohérent avec le brief), mais à garder en tête pour la qualification des types inconnus.

## Décisions techniques, défaut proposé

- Points 1 et 2 ci-dessus. Défaut : conserver le comportement actuel ; Hermès peut appliquer les simplifications sans attendre, j'arbitre après.

## À arbitrer par Ced (touche au réel)

**Faut-il que l'import supprime aussi les types de contenu hors liste fermée ? oui / non.**
Aujourd'hui A-28 ne décide rien : un type inconnu (`fiction_magazine` dans le banc) est conservé et seulement signalé (`TYPES_CONTENU_INCONNUS_CONSERVES`). Le risque de trancher « supprimer » est la perte de contenus du magazine rangés sous un type inattendu. **Défaut prudent proposé : non — conserver + signaler** (comportement actuel). Ne pas transformer ce `PRET` en GO sur le réel : aucune anonymisation universelle des messages (pièces jointes, taxonomies libres, autres extensions) n'est prouvée.

## Verdict

**Conforme.** Le lot répond au brief, ni moins ni plus : liste fermée sourcée, tables et types de la liste vidés par la politique sans décision, `garder`/`anonymiser` refusés avec étape/code/table et sans valeur, vérification qui compte les résidus et refuse sans amorcer WordPress, type inconnu laissé ouvert avec question posée. Rejeu PHP vert. Points restants mineurs ou purement techniques.

Rappel doctrine §6 : ce « Conforme » **n'est pas un GO**. Clôture du lot de code soumise à la seconde relecture (Codex), à la fusion, et au second tour « prêt pour la validation ». `codex.md` non lu ; fusion non faite.
