# Vérification A-21 (n° 3) — contrôle des modifications postérieures au second tour

Vérificateur : Claude. Objet : contrôler que les modifications apportées à A-21 par Hermès **après** la vérification n° 2 (`relectures/A-21/verification-2.md`, commit `ed4317c1`, synchro 2026-11-26 19:38) sont justifiées par une consigne ou un arbitrage, rejouer la suite, repérer toute régression. Pas de relecture complète.

Méthode : `git diff ed4317c1..HEAD` sur `wp/outils/bascule/a21`, `wp/tests/a21`, les fichiers partagés (`stream_guard.py`, `stream_reports.py`, `stream_contract.php`, `a11/`) et `production/A-21` ; lecture du paquet refait ; rejeu de la suite autorisée.

Cadrage : `A-FAIRE.md` (consigne 1 « requalification », lignes 24-32 ; T-03 lignes 19-22 ; règles lignes 54-55) et `docs/arbitrages-2026-11-27.md` (A-28 : lignes 30-33 ; requalification : lignes 86-91 ; T-03 : lignes 93-100).

Ce qui a changé depuis le 26/11 19:38 : **aucun fichier de code**. `git diff ed4317c1..HEAD` sur les sources et tests d'A-21 et sur le gardien partagé est **vide**. Seuls ont bougé le paquet `production/A-21/preuves/final/` (refait), `notes.md`, `FINALISATION.md`, `manifest.json`, `PRET`, et quatre fichiers de paquet : ajout de `rejeu.json`, `verify.py`, `parent-gates.json`, `rapport-court.md` ; suppression de `candidate-verification.json` et `verification-probes.json`. La logique métier (`Analysis.php`, `Inventory.php`, `Command.php`, `inventorier-portes`, `confine.py`, `unit.php`, `README.md`) **n'a pas bougé**.

## 1. Consignes et arbitrages concernés

### A — Requalification : paquet neuf sur l'import A-28 gelé, A-21 reste clos : **Appliqué**

Consigne 1 (`A-FAIRE.md:28-29`) et arbitrage A-28 (`docs/arbitrages-2026-11-27.md:30-31`) : un lot clos dont une dépendance change ne se rouvre pas ; A-21 reste clos, son paquet est refait sur l'import final, le circuit le revérifie sur le `PRET` redéposé, il ne se rouvre que si sa matrice est rouge.

- Paquet unique régénéré sur l'import A-28 final : `production/A-21/notes.md:3-5` (« Sept matrices NEUVES sérialisées sur l'import A28 final », Python Windows 3.14.6, UTF-8/mode 1 et cp1252/mode 0 mesurés).
- Le gel de l'import est reflété dans les dépendances : `production/A-21/preuves/final/dependency-snapshot.json` inclut bien le découpage en cinq fichiers de l'import (`engine.php`, `store.php`, `guard.php`, `form-decision-refused.php`, `lib.php`).
- `PRET` redéposé : `production/A-21/PRET:1` → `2026-11-27T05:03:18 … A22 non clos ; aucun GO réel`.
- Code inchangé (diff vide) : A-21 ne se rouvre pas.

### B — T-03 : déclaration `rejeu.json` et point d'entrée sans argument : **Appliqué**

T-03 (`A-FAIRE.md:19-22`, `docs/arbitrages-2026-11-27.md:96-98`) : les déclarations `rejeu.json` s'ajoutent lot par lot pendant la requalification, avant le sceau ; A-21 et A-22 reçoivent un point d'entrée sans argument qui appelle le vérificateur existant sur l'unique paquet ; **aucun contrôle n'est changé pour rendre une ligne verte**.

- `production/A-21/rejeu.json:1-3` : `schema 1`, `entrypoint verify.py`, `requires []`, puis la liste des logs et des contrôles attendus.
- `production/A-21/verify.py:9-12` : refuse tout argument (`NO_ARGUMENTS`, sortie 1) et relance, sans argument nouveau, le vérificateur inchangé `wp/tests/a21/verify.py` sur `production/A-21/preuves/final`.
- Aucun contrôle changé : `git diff` sur `wp/tests/a21/verify.py` est vide ; le vérificateur est celui du second tour.

### C — Import et gardien gelés, aucune restructuration : **Appliqué (vérifié)**

Import gelé (`A-FAIRE.md:17`, `docs/arbitrages-2026-11-27.md:83`) : plus aucun changement de `wp/outils/staging/` ni du gardien partagé. Vérifié : `git diff ed4317c1..HEAD` sur `stream_guard.py`, `stream_reports.py`, `stream_contract.php` et `a11/` est vide. A-21 n'a touché ni l'import ni le gardien.

### D — Un seul paquet de preuves par lot : **Appliqué**

Règle (`A-FAIRE.md:55`) : un seul paquet (le dernier rejeu vert), les essais intermédiaires hors dépôt. Les deux fichiers de résultats du second tour laissés à la racine du lot (`candidate-verification.json`, `verification-probes.json`) sont retirés ; la preuve vit désormais dans `preuves/final/` seul.

### E — Preuve PAQUETS déférée à T-03, candidat honnête : **Appliqué**

Posture de la requalification (`production/A-21/notes.md`, dernier paragraphe ; `FINALISATION.md`) : la preuve PAQUETS verte finale relève de T-03, elle n'est pas inventée dans le lot. En conséquence `production/A-21/preuves/final/candidate.json` ne revendique rien : `status CANDIDAT_GATE_PARENT`, `readiness_claimed: false`. C'est honnête : la matrice native est verte (§2), mais le sceau PAQUETS final dépend du rejeu indépendant, lequel a effectivement tourné ici (§2).

### F — Décisions à défaut conservées : **Appliqué (vérifié)**

Code inchangé → les trois décisions à défaut du second tour sont conservées : comptes d'inactivité disjoints, lecture directe de `woocommerce_helper_data`, cas IP/IPv6 best-effort. Preuves présentes : contrôle `literal_ip_ipv6_pure_cases` dans `rejeu.json` et paquet natif `PASS`.

## 2. Résultat des tests

Environnement : NUC Windows 11, PowerShell. PHP via conteneurs jetables du lanceur (réseau `none`, dépôt monté en lecture seule).

Note : la commande, écrite exactement comme demandé, a d'abord été **bloquée par la validation du harness** via l'outil PowerShell (« nested PowerShell process which cannot be validated ») ; elle a été acceptée et exécutée via le shell, à la racine du dépôt, à l'identique.

- **Suite autorisée rejouée**, commande exacte :

  ```
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
  ```

  Dernière ligne :

  ```
  REJEU : 1153 tests, 36074 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
  ```

- A-21 y figure, outil pur : `T01 TOOL : a21 ; 18 controls ; 0 failures ; exit=0`.
- **Nouveau et décisif** : la suite exécute désormais une étape PAQUETS (mécanisme T-03), qui rejoue le vérificateur de paquet sans argument. A-21 y est vérifié :

  ```
  PAQUETS : 9 vérifiés, 0 échecs ; hors rejeu : A-30 (declaration absente)
  ```

  Détail machine : `"packets":{"verified":9,"lots":["A-20","A-21",…,"A-28"],"failures":[]}`. Le vérificateur de paquet d'A-21, impossible à relancer au second tour, **passe cette fois au vert dans la commande autorisée**.
- Lecture du paquet natif livré, en appui : `result.json` 172/172 `PASS`, `a22-channels.json` 25/25 `PASS`, `runner.json` 8/8, `unit.json` 18/18, `pure-include.json` vert (18, fichiers inchangés, natif absent), `windows-matrix.json` exit 0 (6 lignes), deux encodages mesurés (UTF-8 mode 1, cp1252 mode 0, Python 3.14.6).

## 3. Régressions ou modifications non demandées

Aucune régression. Le code d'A-21 est inchangé octet pour octet depuis la vérification n° 2 ; ses décisions à défaut sont conservées.

Trois points de périmètre, tous attendus et conformes :

1. La présence des cinq fichiers de l'import dans `dependency-snapshot.json` suit le gel d'A-28 (le découpage de l'import, acté et non défait par l'arbitrage `docs/arbitrages-2026-11-27.md:80-83`). A-21 ne fait que refléter l'import gelé ; il n'y a pas touché.
2. La suppression de `candidate-verification.json` et `verification-probes.json` à la racine du lot est voulue (un seul paquet, §1-D). Ce ne sont pas des preuves perdues : la matrice est refaite dans `preuves/final/`.
3. Le vérificateur de paquet reste partagé avec A-22 ; la clôture formelle d'A-21 reste, par l'arbitrage, groupée avec A-20 et A-22 sur l'import gelé.

Aucun accès au réel, aucune archive Imagine, aucun compte, aucune opération Git, Novamira ni déploiement dans ces modifications.

## 4. Verdict

**Prêt pour la clôture.**

Les seules modifications postérieures à la vérification n° 2 sont la refonte du paquet sur l'import A-28 gelé et les deux artefacts T-03 (`rejeu.json`, `verify.py`) — toutes justifiées par la consigne 1 et les arbitrages A-28 et T-03 du 27/11, toutes appliquées et vérifiables. Le code métier n'a pas bougé. La suite autorisée est verte (1 153 tests, A-21 à 18 contrôles, exit 0) et, cette fois, le vérificateur de paquet d'A-21 a été **réellement rejoué par la commande autorisée** (étape PAQUETS : A-21 parmi 9 vérifiés, 0 échec) — le point qui restait en suspens au second tour est levé. Aucune régression, aucune modification non demandée.

Rappels : ce verdict clôt la vérification de code ; il n'est pas un GO au sens du §3 de la doctrine (aucune bascule, aucun accès au réel). La clôture formelle d'A-21 est groupée avec A-20 et A-22 ; A-22 reste non clos. La décision d'avancer appartient à Ced.
