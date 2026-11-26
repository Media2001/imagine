# Vérification T-02 — second et dernier tour

Vérificateur : Claude. Objet : contrôler l'application de `corrections/T-02.md` par Hermès après fusion. Base de comparaison : état relu (commit de la fusion `2d47285c`, 2026-11-26 13:23) → état courant.

**Méthode d'exécution.** Les banques PHP et le rejeu global tournent dans le conteneur Docker via WSL ; dans cette session, l'exécution de `php`, `python` et `docker` est refusée par le bac à sable (approbation requise, indisponible en non-interactif) — même limite d'environnement que Codex (refus WSL). Je n'ai donc pas pu relancer les suites moi-même. J'ai contrôlé autrement, et de façon vérifiable : lecture du code de la garde, recalcul des empreintes SHA-256 des journaux finaux livrés face aux reçus (`Get-FileHash`), comparaison des sources courantes aux sources scellées, et lecture du rapport de portes du parent exécuté à 17:06. Ce croisement est concordant (détail ci-dessous).

---

## 1. Instructions de corrections/T-02.md

### 1 — (R1, important) Refuser les reçus mixtes `tests` + `checks` — **Appliquée**
- Garde ajoutée dans `wp/tests/t01/tools.php:124-128` : `if (!is_array($receipt) || (array_key_exists('tests',…) && array_key_exists('checks',…))) throw T02_UNIT_RECEIPT_INVALID;`. L'exception est captée en `tools.php:155-156` → `failures = max(1, …)` : échec fermé. La garde est placée **avant** la lecture de `tests`/`checks`, donc le `elseif` n'est plus atteignable sur un reçu mixte. Le cas `!is_array` couvre aussi le reçu scalaire (`"true"`).
- Contrat exact de la fusion présent dans `wp/tests/t01/tools-contract.php:115-121`, avec le reçu `{"tests":{"ancien":true},"checks":[{"check":"nouveau","status":"FAIL"}],"exit_code":0}` et l'attente `code === 1 && pass === false && tools.failures >= 1` (bilan final **FAIL**), totaux PHPUnit inchangés vérifiés.
- Variantes ajoutées (`tools-contract.php:151-155`) : ordre inversé, deux familles vertes, familles nulles, reçu scalaire. Suite de contrats portée de 18 à **24**.
- Surface de `rejouer.ps1` non élargie : empreinte `2e11e76c…` identique avant/après.
- Preuve de mutation témoin (`verification.json` racine, bloc `mutation`) : garde retirée → reçu mixte indûment PASS (`unguarded_mixed_exit: 0`), contrats rouges (`unguarded_contract_exit: 1`), puis restauration et PASS réel. TDD rouge-puis-vert réel.

### 2 — (R2, mineur) Resceller des reçus cohérents — **Appliquée**
- Les `commands.*.output_sha256` des reçus internes `preuves/final/{utf8,cp1252}/verification.json` sont recalculés sur les octets des journaux finaux. Recalcul de contrôle fait ici :
  - `utf8/rejeu.log` → `f3a96898…` = reçu `f3a96898…` ✔
  - `cp1252/rejeu.log` → `3e1406b8…` = reçu `3e1406b8…` ✔
  - `utf8/t02-contracts.log` → `80d72af4…` = reçu `80d72af4…` ✔
- La discordance signalée par la fusion (ex. `utf8/rejeu.log` 441655b5 vs reçu d0b5913b) est résorbée.
- Ajout de `production/T-02/verifier.py` (lecture seule) qui vérifie empreintes internes **et** manifeste externe ; `test-t02-package.py:50-57` refuse une empreinte interne périmée même après rescellement externe. Aucune preuve d'un lot clos tiers régénérée.

### 3 — (M1, mineur) Aligner le décompte — **Appliquée**
- `production/T-02/notes.md:12` passe à **14 banques / 279 contrôles** ; **11/204** et **13/242** sont explicitement étiquetés « photos dépassées ». Décompte issu du dernier rejeu, pas du miroir initial. Voir §3 sur l'origine du nouveau total.

### 4 — (R3) Ne pas namespacer les seules fonctions T-02 — **Appliquée (défaut tenu)**
- `tools.php` reste dans l'espace global, cohérent avec le harnais T-01 (`copyTree`, `discoverT01Tools`, `runT01Tools`…). Aucun namespacing partiel introduit. Conforme au défaut technique de la fusion.

---

## 2. Résultat des tests

Je n'ai pas pu relancer les suites dans cette session (exécution php/python/docker refusée par le bac à sable). Preuves contrôlées à la place :

- **Gate parent du 2026-11-26 17:06** (`files/rapports/2026-11-26-17h06-portes-parent.json`, exécuté après la correction) : `preparer-image.ps1` puis rejeu global `rejouer.ps1` en **UTF-8 et cp1252**, `exit_code: 0`, 11/11 contrôles PASS. `global_results` : **1 123 tests, 34 569 assertions ; 14 outils, 279 contrôles ; 0 échec, 0 erreur, 0 ignoré** dans les deux encodages. Vérificateur propre `production/T-02/verifier.py` relancé vert (stdout `321dffdf…`) deux fois.
- **Empreintes des journaux** recalculées ici concordent avec les reçus (voir R2).
- **Sources courantes = sources scellées par le parent** (contrôle `Get-FileHash`) :
  - `wp/tests/t01/tools.php` → `81c2de07…` ✔
  - `wp/tests/t01/tools-contract.php` → `eb4d550b…` ✔
  - `wp/tests/t01/test-t02-package.py` → `ea8ae93b…` ✔
  Rien n'a bougé entre le scellement parent et l'état courant.

Faisceau concordant : code de la garde correct, reçus cohérents, rejeu global vert attesté par le parent dans les deux encodages. Aucun indice contraire.

---

## 3. Régressions ou modifications non demandées

- **Aucune régression de code T-02.** Les seuls fichiers de code touchés depuis la version relue sont `tools.php` (+5 lignes), `tools-contract.php` (+13 lignes) et l'ajout de `test-t02-package.py` / `verifier.py` — tous ciblés par les corrections.
- **Décompte 13/242 → 14/279 : non imputable à T-02.** Il vient de lots voisins arrivés dans le dépôt commun (A-23 nouveau = 34 contrôles ; A-21 passé de 15 à 18) et correctement captés par la découverte automatique inchangée de T-02. Ce n'est pas une modification de T-02 : `tools.php` ne compte pas en dur, il découvre. `notes.md` le dit honnêtement (« A-23 découvert automatiquement sans modification de ses fichiers »). À signaler, pas un défaut.
- **Marqueur `PRET` déposé par le parent (17:06), pas par l'enfant.** Contenu : « prêt à relire, non clos ». Il ne revendique **pas** la clôture et pointe vers le gate parent. Cohérent avec la doctrine (un verdict n'est pas un GO ; la clôture passe par ce second tour). `notes.md`, écrit à 14:21 avant le gate, dit « aucun PRET » : léger décalage temporel entre la note de l'enfant et l'action du parent, sans contradiction de fond.
- Preuves candidates anciennes déplacées hors dépôt, paquet unique `preuves/final/` ; aucun lot clos tiers régénéré.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

R1, R2 et M1 sont appliquées et vérifiées ; R3 tient le défaut prévu. Rejeu global vert UTF-8 et cp1252 attesté par le gate parent, reçus internes cohérents (empreintes recalculées), sources courantes identiques aux sources scellées. Aucune régression, aucun problème de fond restant, aucune question ouverte pour Ced dans ce lot d'outillage.

Réserve de forme, non bloquante : je n'ai pas pu ré-exécuter les suites moi-même dans cette session (bac à sable). La vérification repose sur le contrôle cryptographique des preuves livrées et sur le rapport d'exécution indépendant du parent. Rappel doctrine : ce verdict ne vaut que pour la clôture d'un lot de code, jamais pour un accès au réel, un compte ou un déploiement.
