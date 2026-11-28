# Vérification A-32 — second et dernier tour

Date : 2026-11-28. Vérificateur : Claude. Objet : contrôler que les corrections de `corrections/A-32.md` ont bien été appliquées par Hermès, relancer les tests, repérer toute régression ou modification non demandée, trancher un verdict.

Méthode : `git diff` entre la version relue (`12d18d97`, dernier état tournée avant corrections, 27/11 19 h 08) et HEAD sur `wp/outils/bascule/tournee/`, `wp/tests/a32/` et `production/A-32/` ; relance des tests Python ; lecture des preuves natives régénérées. Pas de relecture complète refaite.

## 1. Application de chaque instruction de `corrections/A-32.md`

### Instruction 1 — C02, compléter la liste de `classify()` — **Appliquée**
- `wp/outils/bascule/tournee/tournee.py:68-71` : `allowed_messages()` ajoute les codes de supervision dynamiques `A11/A12/A15/A16/A17/A18/A19` × `PROCESS_OUTPUT_INVALID` / `PROCESS_TIMEOUT` / `SUCCESS_INCOMPLETE`. Gardien et outils clos non modifiés.
- `classify()` (`tournee.py:81-84`) inchangé : ces messages sont classés « refusé » **avec code** ; rejet conservé des messages inconnus ou accompagnés de texte libre.
- Banc ajouté : `wp/tests/a32/test_tournee.py:162-174` (`test_dynamic_supervision_codes_are_closed_refusals`, vérifie aussi qu'un code + texte libre ou un code absent retombe en « en échec » sans fuite) et, côté natif réel, `wp/tests/a32/inside.py:125-160` — double A-15 avec `timeout=0.2 s` réel via A-22 et double A-19 à schéma incomplet réel.
- Preuves : `production/A-32/preuves/final/{utf8,cp1252}/native/result.json` → `*:supervision_codes_preserved` PASS (classic + HPOS). `…/classic-supervision.json` : `emitted_codes = {A15: A15_PROCESS_TIMEOUT, A19: A19_SUCCESS_INCOMPLETE}`, `exit_code 1`, bilan « refusé » portant le code.

### Instruction 2 — C04, neutraliser le contenu des chaînes PHP — **Appliquée**
- Nouveau fichier `wp/outils/bascule/tournee/php_config.py` : petit tokenizer fail-closed, chaînes consommées comme jetons atomiques de données (jamais rescannées comme du code), ne reconnaît qu'un `define` littéral unique, autonome, au niveau supérieur. Heredoc/nowdoc, backticks, balises mixtes, `namespace`, formes conditionnelles/opaques et chaînes/commentaires non terminés → refusés.
- `tournee.py:108-113` : l'ancienne regex (qui conservait le contenu des chaînes) est remplacée par `lexer.staging_declaration(config)`. A-05 et les outils clos non touchés.
- Banc : `test_tournee.py:89-121` (`test_php_strings_comments_and_opaque_declarations_fail_closed`) couvre 11 formes refusées — dont `define` dans une chaîne, dans un commentaire `/* */` `//` `#`, heredoc, conditionnel, appel de méthode, non terminé, double déclaration — et 3 formes valides. `inside.py:225-231` ajoute aux négatifs `environment_absent`, `define_in_string`, `define_in_comment`.
- Preuves : `*:tour_guard_zero_tools:define_in_string` et `…:environment_absent` PASS ; `…/classic-unverified-define_in_string-proof.json` présent, aucun outil lancé.

### Instruction 3 — C03 / A-16, ne pas figer les littéraux d'exemple — **Appliquée, avec réserve correctement signalée par Hermès**
- `wp/outils/bascule/tournee/outils.jsonl:5` (A-16) : `--limit=10` retiré. `outils.jsonl:8` (A-19) : `--as-of=2026-11-26T00:00:00Z` retiré.
- `tournee.py:27-39` : `documented_commands()` reconnaît ces deux omissions **uniquement** sur les README nommés et seulement si leur phrase de défaut documentée est présente ; aucune forme nouvelle n'est ajoutée à un outil clos. Défauts confirmés dans les README : `a19/README.md:24` (`--as-of` facultatif, instant UTC courant par défaut), `a16/README.md:15` (N=10 par défaut, de 1 à 100).
- Banc : `test_documented_optional_defaults_not_example_literals` ; `inside.py` cas horloge A-19 (`current`, `later`, `year_before`, `equality`, `year_after`) et `a16_omitted_limit_still_default_ten`.
- Preuves : `*:a19_clock:*` (5 cas × 2 stockages), `*:a19_later_replay_advances_utc`, `*:a19_equality_and_year_change`, `*:a16_omitted_limit_still_default_ten` → PASS.
- **Réserve (conduite correcte)** : `tournee/README.md:23` signale que l'affirmation du défaut proposé dans la fusion — « omettre `--limit` pour un inventaire **complet** » — contredit `a16/README.md:15`, qui fixe N=10 (1–100), jamais illimité. Omettre `--limit` redonne donc 10, pas un inventaire complet. Hermès a appliqué la lettre de l'instruction (retrait du littéral gelé) et refusé d'élargir l'outil clos, en traçant la contradiction (doctrine §1). Voir §4.

### Instruction 4 — C01, README commun — **Appliquée**
- `wp/outils/bascule/README.md:18` : la phrase obsolète (« A-23 à A-25 » ; « A-26/A-27/A-29/A-31 ne sont pas clos ») est remplacée par un renvoi à `tournee/outils.jsonl`, A-26/A-27 inclus, A-29/A-31 hors tournée. `tournee/README.md:40` aligné (renvoi explicite à l'instruction 4). Pas de restructuration du fichier par A-32.

### Instruction 5 — Traçabilité RAPPORT — **Appliquée**
- `production/A-32/RAPPORT.md` ajoute un point 5 : `verified_site()` applique l'arbitrage du 27/11 (lignes 220–224) — interdiction du brief levée pour la tournée seule, lecture du statut comme A-05, refus global d'un seul code avant tout outil ; précisé comme consigne, non interprétation libre.

## 2. Résultat des tests

- **Tests Python (rejouables ici, Windows, Python 3.14.6)** : `python -m unittest discover -s wp/tests/a32 -p 'test_*.py'` → **16 tests, OK** (9 `test_tournee` + 7 `test_delivery`), incluant les trois nouveaux cas de correction (`test_dynamic_supervision_codes_are_closed_refusals`, `test_php_strings_comments_and_opaque_declarations_fail_closed`, `test_documented_optional_defaults_not_example_literals`).
- **Banc natif complet (`matrix.py` / `run.py`)** : non rejouable sur le NUC — il exige un Linux déconnecté avec PHP CLI et les outils réels A-11…A-27 (doctrine §3 : aucun accès site/base, droits du relecteur en local seulement). Preuves régénérées par Hermès, lues et contrôlées : `production/A-32/preuves/final/utf8/native/result.json` et `.../cp1252/native/result.json` → **72 checks, 72 PASS, 0 échec, `exit_code 0`, `no_real_site`**, dans les deux consoles. Tous les checks propres aux corrections sont au vert (supervision, horloge A-19, limite A-16, define-dans-chaîne, environnement absent).

## 3. Régressions ou modifications non demandées

- **Aucune régression** : les checks nominaux et d'étanchéité restent verts (72/72) ; les tests Python nominaux passent.
- **Aucune modification non demandée dans le périmètre A-32** : les seules évolutions de `wp/outils/bascule/tournee/` et `wp/tests/a32/` correspondent exactement aux cinq instructions.
- **Fichier partagé — à signaler, hors A-32** : une section « A-33 — Le poids des archives » a été ajoutée ensuite à `wp/outils/bascule/README.md` par le lot A-33. Ce n'est pas une régression d'A-32 (la correction A-32 ne touche que la phrase de liste) mais, le fichier étant partagé, le fait est noté.

## 4. Points de fond restants (déjà routés vers Ced/parent par la fusion)

- **§5 de la fusion — PRET A-32 face au rejeu courant qui exclut A-31.** Non traité par les corrections, car explicitement « hors périmètre d'écriture d'Hermès-code et du relecteur ». Toujours pour Ced/parent : s'appuyer sur ce `PRET` suppose un rejeu général actuel montrant A-31 et A-32 tous deux dans `packets.lots`, aucun exclu, zéro échec, A-31 rescellé après sa retouche (cf. `FINALISATION.md:48`, `A-FAIRE.md:27-33`). État inchangé depuis la fusion ; aucune nouvelle preuve ne le lève.
- **A-16 — plafond résiduel à 10.** Le littéral gelé est retiré comme demandé, mais le souci de fond de la fusion (une tournée de migration tronquée à 10 numéros) **n'est pas levé** : A-16 étant un outil clos, son défaut documenté reste N=10 (1–100). Rendre A-16 illimité sortirait du gel des outils clos imposé par le brief. Si une migration doit dépasser 10 numéros, c'est une décision sur la capacité d'A-16 (lot/arbitrage séparé), pas un défaut d'A-32. Hermès l'a correctement signalé et n'a pas élargi l'outil.

Ces deux points sont des matières de réception ou de décision technique déjà identifiées par la fusion ; aucun n'est un défaut introduit par les corrections.

## 5. Verdict

Les cinq instructions de `corrections/A-32.md` sont **appliquées** et vérifiées au code, au banc et aux preuves ; les trois importants (C02, C04, C03/A-16) et le mineur (C01) sont traités ; la traçabilité est ajoutée. Les tests Python sont verts dans cet environnement ; les preuves natives régénérées sont 72/72 vertes dans les deux consoles. Aucune régression ni modification non demandée dans le périmètre A-32.

**Prêt pour la validation de Ced.**

Rappel, non bloquant pour le code : le §5 (PRET A-32 / rejeu excluant A-31) reste une décision de réception pour Ced/parent, et la capacité plafonnée d'A-16 à 10 est une question d'outil clos — aucun des deux n'est un défaut d'A-32.

Un verdict de vérification n'est pas un GO au sens du §3 de la doctrine.
