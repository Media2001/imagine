# Vérification A-20 (2e et dernier tour)

Vérificateur : Claude. Date : 2026-11-26. Base « version relue » : commit `67f5ed6d` (écriture de `corrections/A-20.md`, 12:53). Comparaison jusqu'à HEAD (`4d4efd77`). Diff lu sur `wp/outils/bascule/a20/`, `wp/outils/bascule/stream_guard.py`, `wp/tests/a20/`, `production/A-20/`. Tests relancés en local. Aucun fichier modifié.

Rappel de cadre : ce verdict clôt la vérification d'un lot de code ; **ce n'est pas un GO** au sens du §3 de la doctrine.

## 1. Instructions de `corrections/A-20.md`

### Instruction 1 — Fermer les flux du processus PHP (B1) — **Appliquée**

- Plus aucun `os.execvp` qui hérite de stdout/stderr bruts. Un superviseur **extérieur** au processus WordPress est interposé : `wp/outils/bascule/stream_guard.py:22-63` (`supervise`) lance PHP via `subprocess.Popen`, draine les deux tuyaux dans des tampons mémoire bornés (64 KiO), les **jette** et ne retransmet jamais les octets bruts de l'enfant.
- `confine.py:58-59` charge ce gardien ; `confine.py:68-69` l'appelle ; le succès final émis à l'opérateur est un **littéral fixe** `print('A20_OK tarifs.json tarifs.md')` (`confine.py:79`), non dérivé du site.
- Liste fermée de messages : `closed_refusal` (`confine.py:34-41`) n'accepte en stderr que les codes du `frozenset REFUSALS` (+ messages dropin A-11 exacts) et retombe sinon sur `A20_PROCESS_OUTPUT_INVALID`. Le gestionnaire final (`confine.py:82-85`) mappe toute autre erreur sur `A20_CONFINEMENT_FAILED`.
- La publication est faite par le processus parent, depuis un répertoire jetable 0700, **après** validation (`confine.py:61-78`). README mis à jour en conséquence (`wp/outils/bascule/a20/README.md:24`).

### Instruction 2 — Tout arrêt anticipé = échec, même code 0 — **Appliquée**

- `confine.py:72-74` : refus fermé si `returncode!=0` **ou** stdout différent du littéral de succès exact **ou** stderr non vide.
- Au-delà du code retour : `validator.validate(staged_out, audit)` (`confine.py:75-77`, `report.py`) exige les deux rapports complets et conformes avant publication ; un exit 0 sans rapports complets lève `A20_REPORT_INVALID`.
- Couvert par tests : cas `silent_exit` (`exit(0)`) → `A20_PROCESS_OUTPUT_INVALID` ; `forged_success` (faux `A20_OK` sans rapport) → `A20_REPORT_INVALID` (`wp/tests/a20/inside.py`).

### Instruction 3 — Étendre le banc (3 canaris) — **Appliquée et dépassée**

- `wp/tests/a20/inside.py:101-128` ajoute une table de 15 cas adverses jouée en classique **et** HPOS, dont les trois exigés :
  - (a) `direct_stdout` = `fwrite(STDOUT, …)` direct → `A20_PROCESS_OUTPUT_INVALID` ;
  - (b) `direct_stderr` = `fwrite(STDERR, …)` direct → `A20_PROCESS_OUTPUT_INVALID` ;
  - (c) `echo_exit` = `echo CANARI ; exit(0)` → `A20_PROCESS_OUTPUT_INVALID`.
- Douze cas supplémentaires : `die(...)`, `exit(0)` muet, sorties et JSON falsifiés via `register_shutdown_function`, fichier/clé en trop, octet UTF-8 invalide, rapport partiel.
- Chaque cas vérifie **en plus** qu'aucun octet `CANARY` ne subsiste dans les artefacts conservés et qu'aucun répertoire jetable `.a20-*` ne fuit (`inside.py:127`). `verify.py:28` rend ces 30 contrôles (`closed_process:*` / `closed_artifacts:*`) obligatoires dans le paquet.

### Instruction 4 — Rejouer la matrice native et sceller le paquet — **Appliquée (scellé vérifié localement ; rejeu natif indépendant non reproductible sur ce poste)**

- Nouveau paquet unique `production/A-20/preuves/final` ; les anciens paquets (`parent-independent/`, `matrix.json`, `verification.json`…) ont été supprimés et re-scellés.
- `python wp/tests/a20/verify.py production/A-20/preuves/final` → **111 contrôles PASS, exit 0, 0 FAIL**.
- Le scellé est **lié aux sources corrigées courantes** : `exact_current_owned_sources` (sources.json == empreintes actuelles de `wp/tests/a20` + `wp/outils/bascule/a20`) PASS, et `all_executed_dependencies_unchanged` (snapshot == `run.py:DEPENDENCIES`, y compris `stream_guard.py`) PASS dans les deux consoles. Les reçus ne sont donc pas périmés : ils portent bien le code d'après-correction.
- Par console : 34 tests Python, 158 contrôles natifs, 23 assertions PHP pures, 9 contrôles runner, 21 contrôles canaux/mutations, PHPCS 0/0.
- **Limite d'environnement (inchangée depuis le 1er tour).** Je n'ai pas pu ré-exécuter **indépendamment** la matrice native confinée (Landlock/conteneur Linux) sur ce poste Windows : elle exige l'environnement de staging. Je me suis donc appuyé, comme au 1er tour, sur le vérificateur local + l'intégrité du scellé lié aux sources. Le rejeu natif complet reste à confirmer par le parent/Ced avant clôture définitive (cf. Q3 de la fusion).

### Instruction 5 — Défauts techniques Q1 et Q2 — **Appliquée (défaut « oui », inchangé)**

- `Analysis.php` non modifié depuis la relecture (diff vide). Les deux défauts sont conservés :
  - Q1 `without_product_line` gardé (`Analysis.php:51`, documenté `:140`) ; présent au contrat (`report.py` count_keys).
  - Q2 « annuel » = `1 year` ∪ `12 month` (`Analysis.php:78-79`, documenté `:123`) ; même règle appliquée côté validateur (`report.py`, test `non_annual`).

## 2. Résultat des tests

- `python -m unittest discover -s wp/tests/a20 -p 'test_*.py'` → **Ran 34 tests, OK**.
- `python wp/tests/a20/verify.py production/A-20/preuves/final` → **111 PASS, 0 FAIL, exit 0**.
- `verification-probes.json` (6 contrôles anti-recyclage/anti-altération) : tous PASS, exit 0.
- Non rejoué en local : la matrice native confinée (conteneur Linux), hors de portée de ce poste — voir Instruction 4.

## 3. Régressions ou modifications non demandées

- Aucune régression détectée dans le périmètre A-20. Les empreintes lecture-seule (tables/fichiers avant/après, y compris sous `root`) restent vertes dans le paquet.
- **Modifications non littéralement listées mais justifiées par les instructions :**
  - Création d'un gardien **partagé** `wp/outils/bascule/stream_guard.py` (extrait du candidat A-21) : sert directement l'instruction 1 (« superviseur hors du processus »). Ajouté aux dépendances (`run.py:DEPENDENCIES`).
  - `matrix.py` route désormais le runner natif via `wp/tests/a22/run.py --lot=A20` au lieu de `a20/run.py` : consolidation du runner commun, cohérente avec le thème « gardien commun A22 » de `FINALISATION.md`.
  - Nouveaux fichiers `report.py` + `report-contract.json` (contrat de rapport fermé) : support des instructions 1 et 2.
- **Point d'attention hors périmètre A-20 :** le gardien `stream_guard.py` est maintenant partagé par A-03/A-11/A-20/A-21/A-22. Son introduction doit être vérifiée dans les relectures de ces autres lots ; elle n'entre pas dans cette vérification A-20.

## 4. Verdict

**Prêt pour la validation de Ced.**

Le bloquant B1 est corrigé sur les deux voies de fuite signalées (écriture directe sur flux ; arrêt anticipé/`exit`), avec un superviseur hors-processus à liste fermée et un contrat de rapport. Le banc couvre les trois canaris exigés et douze de plus, y compris l'absence de fuite dans les artefacts conservés. Tests Python et vérificateur locaux au vert (34 tests ; 111 contrôles), scellé lié aux sources corrigées courantes. Q1/Q2 conformes aux défauts. Aucun problème de fond restant, aucune question visuelle ou touchant au réel.

**Réserve à lever par le parent/Ced avant clôture définitive (non bloquante pour la validation) :** le rejeu de la matrice native confinée n'a pu être reproduit **indépendamment** sur ce poste (limite d'environnement déjà actée au 1er tour) ; il doit être confirmé dans l'environnement de staging. Et, comme tout verdict de relecture, celui-ci n'est pas un GO réel (import, staging, déploiement : §3 de la doctrine).
