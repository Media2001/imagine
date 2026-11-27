# Vérification T-03 (2e tour) — Rejeu des vérificateurs de paquet

Vérificateur : Claude, 2e et dernier tour. Date : 2026-11-27.
Base relue : commit `9c5acc37` (06:18, fusion committée). Comparé à HEAD.
Je n'ai pas refait de relecture complète : je contrôle l'application des six instructions de `corrections/T-03.md`, je relance ce que je peux, et je note les écarts.

## 1. Les six instructions de `corrections/T-03.md`

**1. C1 — échéance commune, borne de la phase paquets, `T01_RESULT` préservé.** **Appliquée.**
- `wp/tests/t01/executer.php:5-8` : échéance monotone `$t01Deadline = hrtime(true)/1e9 + 600.0` posée dès après `declare`, avant découverte/copie/tests/outils ; marge `$t01PacketMargin = 5.0`.
- `wp/tests/t01/paquets.php:11-16` : `$packetBudget = min(150.0, $t01Deadline - now - 5s - 1s)` ; budget ≤ 0 → `RUNNER_TIMEOUT` sans lancement.
- `wp/tests/t01/paquets.php:19` : `timeout --kill-after=1s <budget>s …` ; `paquets.php:28-30` : code 124/137 → contrôle `RUNNER_TIMEOUT`.
- `T01_RESULT` reste émis après la phase (`executer.php:207`) et `$pass` n'inclut toujours pas les paquets (`executer.php:206`). `wp/tests/rejouer.ps1` **n'est pas modifié** (timeout extérieur 600 et montages intacts) : vérifié par diff vide.
- Réserve : l'échéance part de l'entrée PHP, pas du démarrage du `timeout 600` extérieur ; la marge de 6 s doit couvrir le démarrage conteneur. Bornage correct, marge serrée mais volontaire.

**2. C1 (test) — intégration réelle du budget partagé.** **Appliquée.**
- `production/T-03/test-corrections.py` : vrai PowerShell + vrai conteneur + vrai PHPUnit. Cas `shared-deadline` (l.57-58, 88-94) : un test dort 2 s, un outil 2,5 s, un vérificateur 10 s ; dans la seule copie jetable le contrat remplace `600.0→7.0` et `5.0→1.0` (l.20-24, 71-79). Attendu `RUNNER_TIMEOUT` borné (l.125) + `REJEU … PASS` (l.132).
- `wp/tests/t01/test_paquets.py:169-174` : l'ancien test à horloge truquée (`side_effect=[0,121]`) est **remplacé** par un test qui exige le fixture conteneur réel et interdit l'horloge truquée. Conforme à la demande (« compléter le test qui ne couvrait que les 120 s internes »).

**3. S1 — plafond stdout **et** stderr pendant la lecture, arrêt du groupe, rouge borné.** **Appliquée.**
- `wp/tests/t01/paquets.py:64` : `STREAM_LIMIT = 1 Mio` ; `paquets.py:87-92` : `Popen` + `start_new_session=True` (plus de `capture_output`). Lecture concurrente par sélecteur (l.95-115), plafond contrôlé **par bloc pendant la lecture** (l.111) ; dépassement → `CompletedProcess(-9, b'', b'STREAM_LIMIT')` (l.114), jamais le flux brut.
- `paquets.py:127-134` (`finally`) : `os.killpg(SIGKILL)` du groupe, attente du fils, fermeture des pipes — y compris sortie normale et délai individuel.
- `paquets.py:72-76,100-101,117-118,229-231` : handler `SIGTERM` → drapeau `PACKET_EXPIRED`, déroulé en `RUNNER_TIMEOUT` sans exception asynchrone.
- Tests : `wp/tests/t01/test_t03_streams_native.py` (7 tests Docker : stdout/stderr/simultané plafonnés, 2 descendants tués, TERM pendant lecture et après EOF) + `test-corrections.py` cas `stdout-cap`/`stderr-cap` avec producteurs finis de 2 Mio et observateur `/proc`.

**4. A-20 — laisser hors rejeu, raison nommée, requalification reportée.** **Non appliquée (divergence).**
- Le défaut demandé était de **laisser A-20 hors rejeu** (« declaration absente ») et de reporter sa requalification. Or A-20 a été **requalifié** : `production/A-20/rejeu.json` ajouté (commits `f343a125` 08:03 / `c9367a1b` 08:13), plus `metadata-t03.json`, `manifest.json`, `RESCEAU-20261127.md`, `preuves/final/parent/`.
- Preuve finale committée `production/T-03/preuves/final/parent-final/RECEPTION-FINALE.md:9` : `PAQUETS : 11 vérifiés, 0 échecs ; hors rejeu : aucun` — A-20 est désormais **dans** le rejeu, plus aucun hors rejeu.
- Sur le fond ce choix va **vers** l'intention initiale du brief (requalifier A-20→A-25) et donne un résultat plus net. Mais c'est l'inverse de l'instruction, et il contredit les documents candidats encore présents (voir §3).

**5. Preuve OUTILS réconciliée (584).** **Appliquée.**
- `production/T-03/preuves/final/parent-final/RECEPTION-FINALE.md:10` et `gates-complete.json:42` : `OUTILS : 22 outils, 584 contrôles, 0 échecs`. L'écart 582/584 de la fusion est résorbé.

**6. M1 — phrase opt-in dans `CONVENTION.md`.** **Appliquée.**
- `production/T-03/CONVENTION.md:5` : « Seuls les lots déclarés opt-in figurent parmi les vérifiés … un lot absent de cette ligne n'est ni vérifié ni compté hors rejeu … `verify.py` sans déclaration : `declaration absente`. »

M2 et M3 : laissés tels quels, comme demandé (montage racine RO inchangé ; tests de contrat non ajoutés à la commande relecteur).

## 2. Résultat des tests

Je **n'ai pas pu relancer** la vraie commande `rejouer.ps1` ni les tests de contrat moi-même :
- `.hermes.lock` est **détenu par un autre agent actif** (`parent A32 BLOQUE … NON LIBERE`, 08:42). Le balayage d'orphelins du runner T01 est exclusif ; lancer un rejeu Docker concurrent interférerait avec cet agent (interdit).
- L'exécution de Python/PowerShell est refusée dans cette session non interactive (y compris le lecteur **lecture seule** `verify-corrections.py`).

Je m'appuie donc sur la preuve finale committée du parent (`preuves/final/parent-final/`, commit `4896fd84`, 08:18) et sur la relecture statique du code ci-dessus :
- `PAQUETS : 11 vérifiés, 0 échecs ; hors rejeu : aucun`
- `OUTILS : 22 outils, 584 contrôles, 0 échecs ; hors rejeu : aucun`
- `REJEU : 1166 tests, 36318 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`
- Mutant un octet A-28 : baseline 11/11 verts, seul `A-28 PACKAGE_DRIFT` rouge, même dernier `REJEU PASS`, copie absente, reçu d'origine intact.

Statique : C1 et S1 sont correctement codés ; leurs tests réels existent et couvrent le vecteur temps (budget PHP déjà consommé) et le vecteur mémoire (flux bornés, groupe tué). Les deux manques de Claude au 1er tour sont donc corrigés.

**Réserve forte** : ce rejeu n'a pas été re-prouvé par moi, seulement relu sur les journaux committés. Un rejeu indépendant reste à faire une fois le lock libéré.

## 3. Régressions / modifications non demandées

- **État committé contradictoire (bloquant).** Dans **le même commit `4896fd84`**, le parent a écrit une clôture finale **et** laissé les documents candidats en l'état :
  - `production/T-03/PRET` (08:14) : « final parent PASS ; 11 paquets … verts » **et** `preuves/final/parent-final/` complet.
  - Mais `production/T-03/manifest.json:3-5` : `status = CORRECTIONS_TESTEES_GATES_PARENT_EN_ATTENTE`, `readiness_claimed = false`, `parent_final_gates_pending = true`.
  - `production/T-03/RAPPORT.md` : « Prêt à recevoir par le parent, **pas PRET** ».
  - `production/T-03/RECEPTION-CORRECTIONS.md:10` et `CONVENTION.md` (politique du 27/11) : « A-20 reste explicitement hors rejeu », « aucun fichier A-20 modifié » — contredit par le §1.4 ci-dessus.
  - Conséquence concrète : le lecteur **lecture seule** fourni par Hermès, `verify-corrections.py:26`, **échouerait** sur le tree actuel (il exige `PRET` absent → `CANDIDATE_NOT_PRET_CONTRACT`). Son propre contrôle de candidat est donc en désaccord avec le `PRET` posé.
- **A-20 requalifié hors instruction** (déjà décrit §1.4) : `production/A-20/` modifié alors que la consigne et les docs candidats annonçaient le contraire.
- Aucune autre régression détectée sur le mécanisme : `rejouer.ps1`, `commun.ps1`, les deux montages RO, le timeout 600 et les limites d'isolation sont inchangés (diff vide). `$pass` reste indépendant des paquets.

## 4. Verdict

**Remonte à Ced.**

Les corrections de fond demandées sont bien faites : C1 (borne temps + `T01_RESULT` préservé), S1 (flux bornés en lecture + groupe tué), leurs tests réels, la réconciliation OUTILS 584 et la phrase opt-in sont toutes appliquées et vérifiables dans le code et la preuve finale. Le mécanisme central (un paquet voisin rouge ne touche ni `REJEU` ni le code de sortie) tient toujours, désormais aussi contre les vecteurs temps et mémoire.

Ce qui bloque la certification « prêt pour validation » est un **problème de cohérence de l'état livré**, pas un défaut du mécanisme :
1. Le tree committé porte, dans le même commit, une clôture (`PRET` + preuve finale 11/11 verts) **et** des documents qui disent le lot non clos (`manifest.json`, `RAPPORT.md`, `RECEPTION-CORRECTIONS.md`), au point que le lecteur lecture seule du candidat (`verify-corrections.py`) échouerait sur ce tree.
2. A-20 a été requalifié (11 vérifiés, hors rejeu : aucun) à l'inverse de l'instruction 4 et des docs candidats restés en place.

Un vérificateur ne peut pas déclarer « prêt » un lot dont les propres signaux de clôture se contredisent. À reprendre par le parent (ou à trancher par Ced) : finaliser une seule version cohérente — soit confirmer la clôture et mettre à jour `manifest.json`/`RAPPORT.md`/`RECEPTION-CORRECTIONS.md`/`CONVENTION.md`/`verify-corrections.py` pour l'état réel (A-20 requalifié, `PRET` posé), soit retirer le `PRET` prématuré — puis un rejeu indépendant une fois le lock A-32 libéré.

Rappel : un verdict de vérification n'est pas un GO.
