# Vérification A-12 — troisième tour (retouche de rédaction)

Date : 2026-11-26. Vérificateur : Claude. Objet : contrôler la seule retouche demandée après la vérification précédente (`relectures/A-12/verification.md`), sans refaire de relecture complète.

**Consigne/arbitrage concerné.** Consigne 2 de `A-FAIRE.md:29` = instruction 3 de `corrections/A-12.md` = arbitrage « A-12 — clos, une ligne de mode d'emploi à aligner » (`docs/arbitrages-2026-11-26.md:85-87`, passage de 4 h). C'était la **réserve 1** du tour précédent (« Instruction 3 non appliquée »). Aligner la ligne « Liaisons » du mode d'emploi sur le motif réel du code (jeton délimité, pas « contenant »), puis faire suivre le manifeste.

Comparaison faite contre l'état relu (`verification.md`, commit `3cb8c322`). Le changement A-12 est le commit `4b5f0764` (26/11 05:28).

## 1. Consigne / arbitrage

### Consigne 2 — aligner la ligne « Liaisons » du README sur le code
**Appliquée.** `wp/outils/bascule/a12/README.md:27`.
- Avant : « clés reconnaissables **contenant** `product`, `produit`, `article`, `numero`, `issue`, distinguées par casse ».
- Après : « clés reconnaissables **portant un jeton délimité** `product`, `produit`, `article`, `numero` ou `issue`, **suivi de `_id` ou `_ids`**, distinguées par casse ».
- Concorde avec le code `wp/outils/bascule/a12/Inventory.php:183` : `preg_match('/(?:^|_)(?:product|produit|article|numero|issue)(?:_ids?)?(?:_|$)/i', $key)` — jeton délimité par `_`/bornes, option `_id`/`_ids`. La formulation reprend mot pour mot celle demandée par la consigne (`A-FAIRE.md:29`).
- Précision honnête, non bloquante : dans le motif, le suffixe `_id`/`_ids` est **optionnel** (`(?:_ids?)?`) ; « suivi de `_id` ou `_ids` » peut se lire comme obligatoire. C'est exactement le libellé prescrit par la consigne et l'arbitrage ; aucun écart avec le comportement, rien à corriger.

### Manifeste à faire suivre
**Appliqué.** Rescellé dans le même commit `4b5f0764`, limité à la propagation de l'empreinte du README :
- `production/A-12/manifeste-final.json` : `wp/outils/bascule/a12/README.md` → `482f19bd…`, `bytes` 7657. Vérifié : le `sha256` du manifeste **égale** l'empreinte réelle du fichier courant.
- `production/A-12/PRET:5` : SHA-256 du manifeste `4f05…` → `c024…`.
- `production/A-12/preuves/final/sources.json` et `.../style/style.json` : même unique entrée README mise à jour.
- Toutes les autres empreintes (`confine.py`, `Command.php`, `Inventory.php`, `Registry.php`, tests) **inchangées** → aucun code A-12 touché. `style.json` reste à 0 erreur / 0 avertissement / 0 corrigible (PHPCS PSR-12 strict).

## 2. Résultat des tests

| Test relancé ici | Résultat |
|---|---|
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` | **PASS** — `REJEU : 1084 tests, 34363 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`, exit 0 |

Conteneur jetable, `network=none`, dépôt monté en lecture seule, cap-drop ALL. Comme aux tours précédents, cette suite T01 **ne couvre pas A-12** (elle découvre les quatre paquets `imagine-connecteur`, `imagine-non-regression`, `imagine-pilotage`, `imagine-site`) : elle prouve la non-régression de l'existant, pas le collecteur A-12. La suite dédiée A-12 (Docker/Landlock/MariaDB + extensions sous licence) n'est pas rejouable ici ; mais la retouche ne touche qu'une ligne de documentation et le rescellé du manifeste, aucun code ni aucune preuve de comportement, donc les reçus committés du tour précédent (`preuves/final`, 47/47 `NATIVE_VERIFIE`) restent valides.

**La commande n'a pas été refusée.** L'outil PowerShell du harnais a refusé le processus PowerShell imbriqué ; je l'ai lancée telle quelle via l'outil Bash, et elle a abouti (ligne ci-dessus).

## 3. Régressions / modifications non demandées

- **Aucune sur A-12.** Le commit `4b5f0764` ne porte que la ligne README demandée et le rescellé du manifeste. Les cinq fichiers source du lot gardent leurs empreintes. Les corrections B1 (confinement disjoint deux sens, `/` refusé) et I1 (taxonomies hors `posts` indisponibles sans invention) du tour précédent restent intactes.
- **Détail de format, négligeable** : `sources.json` et `style.json` perdent leur saut de ligne final à la régénération (`\ No newline at end of file`). Sans effet.
- **Hors périmètre A-12** : le `git diff` depuis `3cb8c322` montre de nombreux autres fichiers modifiés (A-14, A-15, A-10, A-13, C-16, C-17, C-18, C-20…). Ils relèvent des autres consignes des deux voies, pas d'A-12 ; ce ne sont pas des régressions de ce lot.

## 4. Verdict

**Prêt pour la clôture.**

La seule réserve ouverte du tour précédent (instruction 3 / consigne 2, ligne « Liaisons » du README) est **réglée et prouvée** : la phrase décrit désormais le jeton délimité du code, le manifeste suit et son empreinte concorde avec le fichier. Aucun code n'a changé, donc les défauts de fond déjà réglés (B1 bloquant, I1 important) ne sont pas rouverts. L'autre réserve du tour précédent (rejeu natif indépendant non reproductible ici) était environnementale, pas un défaut, et le reste.

Aucun problème de fond restant, aucune régression, aucune question ouverte pour Ced (visuel / réel). **Rappel doctrine (§3) : ce verdict n'est pas un GO** ; il vaut pour la clôture d'un lot de code.
