# Vérification T-02 — tour complémentaire (après retouche d'Hermès)

Vérificateur : Claude. Objet : contrôler ce qu'Hermès a modifié sur T-02 **après** la vérification précédente (`relectures/T-02/verification.md`, « Prêt pour la validation de Ced »).

**Fenêtre exacte.** `verification.md` est committée à 18:48 (`4ca65e46`). Depuis, la seule modification de T-02 est le commit de 19:23 (`ab843bc2`). `git diff 4ca65e46 HEAD -- wp/tests/t01 wp/tests/rejouer.ps1 production/T-02` ne retourne que **trois fichiers** : `FINALISATION.md` (+8), `PRET` (±1), `manifest.json` (±6). **Aucun code touché.** `notes.md` inchangée.

Nature de la retouche : le parent a **rejoué ses portes communes à 19:21** (préparation d'image + rejeu global UTF-8/cp1252), puis a aligné les artefacts de preuve de T-02 sur ce dernier gate. Le décompte passe de 14 outils / 279 contrôles à **16 outils / 311 contrôles**, parce que la découverte automatique inchangée a capté les lots voisins A-23/A-24/A-25.

---

## 1. Consignes et arbitrages concernés

### a) Portes communes rejouées après gel des sources — **Appliquée**
- Consigne `A-FAIRE.md:17-21` (point 0 : « rejoue la préparation de l'image et le rejeu global dans les deux encodages… dépose les `PRET` sur les mêmes sources ») et arbitrage `docs/arbitrages-2026-11-26.md:358` (A-22, instruction 6 : « les portes du parent rejouées après le gel des sources… rejeu global dans les deux encodages »).
- Preuve : `files/rapports/2026-11-26-19h21-verification/parent.json` — `exit_code: 0`, `preparation`/`utf8`/`cp1252` à PASS, `global_results` **1 126 tests, 35 550 assertions, 16 outils, 311 contrôles, 0 échec** dans les deux encodages. Commandes enregistrées : `wp/tests/preparer-image.ps1` puis `wp/tests/rejouer.ps1` ×2.
- Date et heure du gel : **2026-11-26 19:21:25** (`PRET:1`, `FINALISATION.md:1`).

### b) Rafraîchir les pointeurs de paquet sur le gate final — **Appliquée**
- `FINALISATION.md:1-9` : nouveau bloc « Finalisation parent du 2026-11-26T19:21:25 », « Prêt à relire, non clos », comptes 16/311, « sans modification de notre part ». Le bloc 17:06 est conservé en dessous (historique).
- `PRET:1` → pointe désormais sur `files/rapports/2026-11-26-19h21-verification`.
- `manifest.json` : empreinte de `FINALISATION.md` recalculée (`375ab4a1…`) et champs `parent_preparation` / `parent_global_T01` repointés sur le dossier 19h21.
- Contrôle de cohérence fait ici : `Get-FileHash` de `FINALISATION.md` = `375AB4A1…` = empreinte du manifeste. **Concorde.**

### c) T-02 clos, trois corrections déjà vérifiées — **Confirmée, inchangée**
- Arbitrage `docs/arbitrages-2026-11-26.md:341-344` (« T-02 — clos ») : reçu mixte refusé, empreintes internes recalculées, décompte du dernier rejeu, harnais laissé dans l'espace global.
- Ces trois corrections (R1/R2/M1) et le défaut tenu (R3) étaient déjà « Appliquées » dans `verification.md §1`. Le commit 19:23 **n'y touche pas** : le code (`tools.php`, `tools-contract.php`, `test-t02-package.py`, `verifier.py`, `rejouer.ps1`) est identique à l'état scellé. Le verificateur propre T-02 rend le même `321dffdf…` qu'au premier tour (`parent.json`, fichiers `T-02-utf8/cp1252.json`).

---

## 2. Résultat des tests

J'ai **relancé moi-même** la suite, avec la commande exacte demandée (Docker disponible dans ma session) :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernière ligne :

```
REJEU : 1126 tests, 35550 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Ligne précédente : `OUTILS : 16 outils, 311 contrôles, 0 échecs ; hors rejeu : aucun`. Détail capté : a23 = 34, a24 = 17, a25 = 15, etc. Isolation inchangée (`network=none ; rootfs=ro ; mount … :/repo/wp:ro ; cap-drop=ALL ; no-new-privileges`), balayage des orphelins et `T01 CLEANUP : absence verifiee de imagine-t01-e059d3f8…` : aucun conteneur ne reste.

Mon rejeu reproduit **à l'identique** le gate parent de 19:21 (1 126 / 35 550 / 16 / 311, PASS). Levée de la réserve de forme de `verification.md` : cette fois les suites ont bien été ré-exécutées, pas seulement contrôlées par empreinte.

---

## 3. Régression ou modification non demandée

- **Aucune.** Les seuls fichiers modifiés depuis la vérification sont trois artefacts de preuve (`FINALISATION.md`, `PRET`, `manifest.json`) ; aucun fichier de code ni `rejouer.ps1`.
- **Décompte 14/279 → 16/311 : non imputable à T-02.** Il vient des lots voisins A-23/A-24/A-25 arrivés dans l'arbre commun et captés par la découverte automatique, inchangée (`tools.php` découvre, ne compte pas en dur). `FINALISATION.md:3` le dit : « changements concurrents de la voie 2, sans modification de notre part ». C'est exactement le mécanisme déjà décrit dans `verification.md §3`.
- Détails cosmétiques du commit (barres obliques dans `PRET`/`manifest.json`, pointeur vers un dossier au lieu d'un `.json`) : alignements de forme, pas des régressions.
- `manifest.json` reste restreint au lot (43 fichiers), aucun lot clos tiers régénéré.

---

## 4. Verdict

**Prêt pour la clôture.**

La retouche post-vérification se limite à rejouer les portes communes du parent (gel des sources 2026-11-26 19:21:25) et à rafraîchir les pointeurs de preuve de T-02 sur ce gate final, conformément à la consigne 0 d'`A-FAIRE.md` et à l'arbitrage de 16 h. Aucune ligne de code modifiée depuis l'état déjà vérifié. Rejeu global **vert, 16 outils / 311 contrôles, UTF-8 et cp1252**, ré-exécuté par moi-même et concordant avec le gate parent ; empreinte de `FINALISATION.md` cohérente avec le manifeste. Aucune régression, aucune modification non demandée, aucun problème de fond restant, aucune question ouverte pour Ced dans ce lot d'outillage.

Rappel doctrine : ce verdict ne vaut que pour la clôture d'un lot de code, jamais pour un accès au réel, un compte ou un déploiement.
