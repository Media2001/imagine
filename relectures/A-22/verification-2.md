# Vérification A-22 (3ᵉ tour) — après le paquet refait et le raccord T-03

Vérificateur : Claude. Date : 2026-11-27.
Base : `relectures/A-22/verification.md` (2ᵉ tour, verdict « remonté à Ced : un seul point de fond ouvert »).
Diff examiné : `git diff 3c7c8681..HEAD` (3c7c8681 = commit de la vérification précédente, 26/11 19 h 43) sur `wp/` et `production/A-22`.
Consignes lues : `A-FAIRE.md` (consigne 1, requalification ; point 0, T-03), `docs/arbitrages-2026-11-27.md` (passages de 1 h et 4 h : blocs « A-22 », « A-28 », « T-03 »), `doctrine/doctrine.md`.

Je n'ai **pas** refait de relecture complète. Je contrôle l'application des consignes qui justifiaient les changements d'Hermès depuis le 2ᵉ tour, je relance les tests à ma portée, et je signale les écarts.

## Ce qui a changé depuis le 2ᵉ tour

Le **code** d'A-22 n'a pas bougé : `wp/tests/a22/` (gardien, tests, matrice, vérificateur) et le gardien commun (`wp/outils/bascule/stream_guard.py`, `stream_reports.py`, `channels.py`, `stream_contract.php`, `stream_bridge.php`) ont un `git diff` **vide** sur l'intervalle. Les changements d'A-22 sont uniquement le **paquet de preuves refait** et le **raccord T-03** (`git diff --stat` sur `production/A-22`). Les évolutions de `wp/outils/bascule/a23…a31` et `wp/tests/a23…a31` relèvent d'autres lots (voie 1), pas d'A-22.

## 1. Consignes et arbitrages concernés

### C1 — Paquet périmé par A-28, à refaire sur l'import gelé. **Appliquée.**
`A-FAIRE.md:30` (« A-22 : paquet refait ») et `docs/arbitrages-2026-11-27.md:62`. Paquet unique `production/A-22/preuves/final/`, sept matrices neuves sérialisées sur l'import A-28 final (`production/A-22/FINALISATION.md:1-5`), Python Windows 3.14.6, UTF-8 et cp1252 mesurés. Gardien et import déclarés intacts (`FINALISATION.md:3,185`), ce que le diff confirme.

### C2 — Un seul paquet de preuves ; les essais intermédiaires sortent du dépôt. **Appliquée.**
`A-FAIRE.md:55`. Les reçus producteurs du 2ᵉ tour sont supprimés : `candidate-verification.json` (−733), `execution-summary.json`, `runner-absence.json`, `verification-probes.json` retirés ; `manifest.json` régénéré. Il ne reste que `preuves/final` + `FINALISATION.md`. La réserve « reçu producteur, pas revalidation » du 2ᵉ tour (`verification.md:27,58`) n'a plus d'objet : plus aucun reçu producteur n'est présenté comme preuve.

### C3 — T-03, point d'entrée sans argument appelant le vérificateur existant, sans changer de contrôle. **Appliquée.**
`A-FAIRE.md:22` et `docs/arbitrages-2026-11-27.md:98`. Nouveau fichier `production/A-22/verify.py:1-12` : il refuse tout argument (`verify.py:8-10`, code `NO_ARGUMENTS`) et relance le vérificateur existant **inchangé** `wp/tests/a22/verify.py` sur l'unique paquet `production/A-22/preuves/final` (`verify.py:11`). Aucun contrôle du vérificateur n'est modifié (diff de `wp/tests/a22/` vide).

### C4 — Déclaration `rejeu.json` ajoutée lot par lot, avant le sceau. **Appliquée.**
`A-FAIRE.md:20` et `docs/arbitrages-2026-11-27.md:96`. `production/A-22/rejeu.json` ajouté (+289), `entrypoint:"verify.py"`, `requires:[]`, liste des logs du paquet. C'est la déclaration qui permet au rejeu de T-03 de jouer le vérificateur d'A-22 (voir §2).

### C5 — Ne pas toucher au gardien commun sans l'annoncer ; import gelé. **Appliquée.**
`A-FAIRE.md:42`, `docs/arbitrages-2026-11-27.md:83`. `git diff` vide sur les cinq fichiers du gardien commun et aucune empreinte de l'import touchée par A-22. `FINALISATION.md:3` l'annonce explicitement (« Gardien commun INCHANGÉ »).

### C6 — Le point de fond du 2ᵉ tour : rejeu indépendant du vérificateur de paquet. **Désormais exécutable et exécuté — vert.**
`docs/arbitrages-2026-11-27.md:63` (« A-22 se clora sur ce rejeu indépendant ») : T-03 fait jouer les vérificateurs de paquet sans argument par la commande de rejeu autorisée, dans le conteneur isolé. C'était l'unique réserve du 2ᵉ tour (`verification.md:54,58,62`). Je l'ai lancée moi-même (voir §2) : le vérificateur de paquet d'A-22 passe au vert, de façon indépendante.

## 2. Résultat des tests

Commande lancée telle quelle, sans argument :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, dépôt monté en lecture seule, sans réseau. Dernières lignes :

```
PAQUETS : 9 vérifiés, 0 échecs ; hors rejeu : A-30 (declaration absente)
OUTILS : 22 outils, 582 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1153 tests, 36075 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Le bloc machine confirme le périmètre des paquets vérifiés :
`"packets":{"verified":9,"lots":["A-20","A-21","A-22","A-23","A-24","A-25","A-26","A-27","A-28"],"failures":[],"excluded":[{"lot":"A-30","reason":"declaration absente"}]}`.

**A-22 figure dans les paquets vérifiés, 0 échec.** C'est le premier tour où le vérificateur de paquet d'A-22 est rejoué par quelqu'un d'indépendant (moi), via la commande autorisée, et au vert. Non-régression PHP : verte (1153 tests). A-30 « hors rejeu : déclaration absente » est le comportement attendu de T-03 (`A-FAIRE.md:21`), pas un échec.

Limite inchangée : la **matrice native Docker/Windows 3.14** (`wp/tests/a22/matrix.py`) demande toujours Docker/WSL hors de ma commande ; je ne l'ai pas réexécutée. Mais l'arbitrage a fixé la clôture d'A-22 sur le **rejeu indépendant du vérificateur de paquet** (`arbitrages-2026-11-27.md:63`), pas sur une réexécution de la matrice — et ce rejeu est fait et vert.

## 3. Régressions ou modifications non demandées

- **Aucune régression de code A-22.** Code et tests inchangés depuis le 2ᵉ tour (diff vide).
- `wp/tests/rejouer.ps1` a évolué (+14) pour exécuter l'étape PAQUETS : c'est le mécanisme de T-03 (lot distinct), pas un fichier d'A-22 ; il est l'outil qui rend le rejeu indépendant possible, pas une retouche d'A-22. À tracer côté T-03, pas ici.
- Pas de fuite de périmètre : les changements `a23…a31` sont d'autres lots de la file voie 1, pas A-22.
- Aucun secret, aucune donnée réelle ; paquet refait sur bancs fictifs et import neutralisé.

## 4. Verdict

**Prêt pour la clôture** (du code et du paquet ; ce verdict n'est pas un GO au sens de la doctrine §3).

Raisons :
- Les six consignes/arbitrages qui justifiaient les changements d'Hermès sont **appliquées** (C1 à C6), chacune située.
- Le code d'A-22 est inchangé depuis la relecture « Conforme » et les cinq corrections déjà prouvées au 2ᵉ tour.
- L'**unique point de fond** laissé ouvert au 2ᵉ tour — le rejeu indépendant du vérificateur de paquet — est désormais **exécuté par moi, au vert**, A-22 compris (`PAQUETS : 9 vérifiés, 0 échecs`), par la commande autorisée dans le conteneur isolé, exactement le mécanisme que l'arbitrage avait désigné pour la clôture.
- Tests verts (1153), aucune régression, aucune modification non demandée dans A-22.

Réserve de dépendance, pour information : la clôture d'A-22 s'appuie sur le raccord T-03 (`rejeu.json` + `production/A-22/verify.py` + l'étape PAQUETS de `rejouer.ps1`), lot encore en réception. Le mécanisme a produit un résultat indépendant et vert pour A-22 ; sa propre clôture suit sa file. Rien de tout cela ne bloque A-22 au fond.

Rappel doctrine : ce verdict n'est pas un GO.
