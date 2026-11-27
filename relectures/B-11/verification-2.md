# Vérification B-11 — 3e tour (passage au contrat 16h30, vérificateur)

Date : 2026-11-27. Portée : modifications d'Hermès **après** la vérification précédente (`relectures/B-11/verification.md`, commit `adb9f630`, 15h33). Méthode : `git diff adb9f630..HEAD` sur `wp/` et `production/B-11/`, relance du rejeu PHP autorisé, lecture du vérificateur de réception hors-ligne et des reçus. **Pas de relecture complète refaite.** Ce verdict n'est pas un GO.

Rappel du 2e tour : verdict « Remonte à Ced » pour deux raisons de fond — (1) la réception renouvelée était de nouveau périmée par une ligne d'amorçage d'un lot voisin (B-12 dans `imagine-site.php`) ; (2) la persistance dans l'éditeur réel n'était plus prouvée par automate, renvoyée à Ced. L'arbitrage `docs/arbitrages-2026-11-27.md` (passage de 16h) tranche les deux : contrat d'amorçage partagé, et saisie éditeur « reste à Ced », décision de 13h ratifiée.

## 1. Consignes / arbitrages concernés, un par un

Source des consignes : `docs/arbitrages-2026-11-27.md` passage de 16h (§ « B-11 — vérifié "remonte à Ced" : rien pour Ced, une règle »), repris dans `A-FAIRE-2.md:17,23,36` (consigne 0).

1. **Contrat d'amorçage partagé : contrôler l'empreinte de ses propres fichiers + la présence du bloc d'enregistrement propre (exact, unique), jamais l'empreinte entière du fichier d'amorçage ; idem README borné à sa section.** **Appliqué.**
   - Bibliothèque neuve `wp/tests/demo/lot_reception_contract.py` : `registration()` (`:33-41`) exige le bloc propre B-11 présent **exactement une fois** et refuse une seconde inscription modifiée ; `section()` (`:44-51`) borne la section README au titre de niveau 2 suivant ; `sources()` (`:54-65`) ne couvre que les fichiers propres (exclut `imagine-site.php`) ; `integrity()` (`:88-94`) vérifie `contract_version`, sources propres, `bootstrap_contract`, `readme_section`.
   - `wp/tests/demo/b11-verifier1330.py:28-29` : remplace `manifest['sources']==b11.sources()` par `contract.integrity('B11',...)` + `contract.sources('B11')` ; `:59` : `contract.tested_sources(...)` ; `:74` (`--live`) : `contract.live_registration(...)`.
   - `production/B-11/reception-contrat-V2.json` : `contract_version:1` (`:99`), `bootstrap_contract` bloc propre `occurrences:1` (`:101-105`), `readme_section` (`:106`), sources propres (`:7-40`).
   - Preuve directe : le bloc B-11 est présent **1 fois** dans `imagine-site.php:168-172` (`grep -c` = 1), et le vérificateur de réception hors-ligne passe (voir §2).

2. **Aucun code fonctionnel de B-11 ne change (« Rien à réécrire dans le code du lot »).** **Appliqué.**
   - `git diff adb9f630..HEAD` **vide** sur `Medias.php`, `MediasRegles.php`, `AudioNumero.php`, `imagine-site.php`, `b11-recette.py`, `b11-observer.php`, `b11-editor-audit.php`, `b11-verifier.py`.
   - Les empreintes fonctionnelles du reçu (`reception-contrat-V2.json:22-24`) sont celles des fichiers courants ; `contract.tested_sources` (`lot_reception_contract.py:82-84`) exige que les trois fichiers fonctionnels soient couverts et byte-identiques aux preuves historiques.

3. **Réception neuve qui rejoue sur l'arbre courant (la raison de fond n° 1 du 2e tour).** **Appliqué.** La ligne B-12 ajoutée dans `imagine-site.php` ne périme plus la réception : le contrôle porte sur le bloc propre, pas sur l'empreinte entière. Vérificateur hors-ligne **PASS** (§2), là où le 2e tour était **rouge** sur `sources_finales`.

4. **PRET redéposé.** **Appliqué.** `production/B-11/PRET` pointe `reception-contrat-V2.json`, `NOTE-contrat-V2.md`, `A-VOIR-contrat-V2.md`, `UI_save_verified=false`, mention « Contrat16h30 ». Ancien PRET archivé en `PRET-avant-contrat-V2`.

5. **La saisie dans l'éditeur réel reste à Ced (décision de 13h ratifiée à 16h — raison de fond n° 2 du 2e tour, tranchée).** **Appliqué.** Politique 13h30 conservée : `UI_save_verified=false`, 16 options effectives, témoin backend 8/8 (`reception-contrat-V2.json` sortie du vérificateur §2 ; `NOTE-contrat-V2.md:3`). Les trois lignes de parcours restent pour Ced dans `A-VOIR-contrat-V2.md:3-5`. Ce n'est plus un problème de fond : c'est la validation visuelle de Ced, de son ressort (doctrine §6).

6. **Pas de resceau ni de PRET voisin, pas de réception complémentaire des voisins ; lots code clos non rouverts.** **Appliqué.** Le contrat ne lit aucun PRET/état voisin (`reception-contrat-V2.json:138` ; `lot_reception_contract.py` n'ouvre aucun reçu voisin) ; `NOTE-contrat-V2.md:7` : le complément voisins historique « n'est ni réexécuté ni un critère vivant ». C27/C28 (clos) non rouverts ; A-31/A-32 hors périmètre (`reception-contrat-V2.json:97`).

7. **Catch Paywall trop large, reporté au gel du code.** **Respecté (hors périmètre).** Non repris ici, conforme à l'arbitrage (`reception-contrat-V2.json:97`).

## 2. Résultat des tests

- **Rejeu PHP autorisé** (`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`, conteneur jetable, réseau `none`, dépôt en lecture seule). Lancé via l'outil Bash car l'outil PowerShell refuse un processus imbriqué. Dernière ligne :
  > REJEU : 1204 tests, 36667 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

  `OUTILS : 22 outils, 720 contrôles, 0 échecs`. Le compte (1204/36667) concorde avec celui annoncé par la note (`NOTE-contrat-V2.md:11`). `MediasB11Test` est dans le vert. Les paquets A-31 (`A31_PARTIAL_EVIDENCE`) et A-32 (`A32_PACKAGE_DRIFT`) restent rouges sur la ligne `PAQUETS` : connus, hors périmètre, non réparés — n'inversent pas le verdict `REJEU … PASS`.
- **Vérificateur de réception B-11 hors-ligne** (`python -B wp/tests/demo/b11-verifier.py`, test du lot, sans réseau) : **PASS**.
  > {"B11":"PASS","receipt":"reception-contrat-V2.json","mode":"offline","checks":32,"success":true,"UI_save_verified":false,"effective_options":16,"backend_witness_checks":8,"contract":"owned-files + unique exact own block + bounded own README"}

  C'est le contrôle qui était **rouge** au 2e tour (`sources_finales`) : il passe désormais, le contrat ayant remplacé l'empreinte entière de l'amorçage. Confirme en preuve directe les consignes 1 et 3.
- **Recette runtime/navigateur** (`b11-recette.py`, Playwright + staging) : **non rejouable par le vérificateur** (lecture seule, hors réseau, pas d'accès au staging). Preuves prises dans les reçus `politique1330-*`, sur parole — inchangées depuis le 2e tour.

## 3. Régression / modification non demandée

- **Raison de fond n° 1 du 2e tour : levée.** La récurrence « un lot voisin périme la réception par une ligne d'amorçage » est structurellement résolue par le contrat. Ce n'est plus une régression.
- **Code fonctionnel B-11 : aucune régression.** Diff vide sur les trois fichiers ; empreintes égales au reçu. Le bloc d'amorçage reste présent une seule fois malgré l'ajout de C-29/B-12.
- **Modification non demandée, bénigne et assumée :** la bibliothèque `lot_reception_contract.py` est **partagée** avec C-29 (ainsi que `b11-c29-contract.py` et `b11-c29-contract-tests.py`). C'est de l'outillage de réception uniquement (aucun PHP fonctionnel, amorçage ou donnée écrits — déclaré en tête du fichier `:1-4`), dans les dossiers de la voie 2. Factorisation cohérente avec la règle 16h30 appliquée à plusieurs lots ; pas un écart de périmètre B-11. À signaler sans réserve bloquante.
- **README partagé :** la section B-11 reçoit un paragraphe borné (contrat 16h30, `README.md:522`) à l'intérieur de sa section ; C-29 ouvre sa propre section. Pas de débordement sur C-28.

## 4. Verdict

**Prêt pour la clôture** (volet code et preuve).

Les deux raisons de fond qui avaient fait « Remonte à Ced » au 2e tour sont traitées, chacune par l'arbitrage de 16h que je retrouve appliqué :
1. **Réception qui rejoue :** passage au contrat, vérificateur hors-ligne **PASS**, rejeu PHP **PASS** (1204 tests). La ligne d'amorçage d'un lot voisin n'invalide plus le scellé B-11.
2. **Saisie éditeur :** décision de 13h « reste à Ced » ratifiée à 16h ; ce n'est pas un problème de fond mais la validation visuelle de Ced (doctrine §6), avec les trois lignes d'`A-VOIR-contrat-V2.md`.

Aucun problème de fond restant, aucune réécriture de code B-11. Il reste la **validation visuelle de Ced** et le **parcours de saisie dans l'éditeur** (A-VOIR) — étapes normales du ressort de Ced pour un lot visuel, non bloquantes pour la clôture du code. Ce verdict n'est pas un GO au sens du §3.
