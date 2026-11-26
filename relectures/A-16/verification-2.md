# Vérification A-16 — troisième tour (après retouche d'Hermès)

Vérificateur indépendant. Objet : la **retouche** demandée après la vérification précédente (`relectures/A-16/verification.md`, qui remontait un seul point à Ced).
Base de la consigne : `A-FAIRE.md` consigne 2 ; `docs/arbitrages-2026-11-26.md` (passage de 10 h, « A-16 — le refus nomme le champ, jamais sa valeur ») ; brief ligne 31.
Méthode : `git diff` de la version vérifiée (commit `43c906c2`, 08 h 33) à HEAD sur `wp/` et `production/A-16`, puis rejeu de la suite PHP. La retouche a été livrée vers 11 h 08–11 h 18. Pas de relecture complète refaite.

## 1. Consignes / arbitrages concernés

**Arbitrage 10 h + A-FAIRE.md consigne 2 — le refus `A16_MAPPING_KEY_ABSENT` nomme le champ (liste fermée), jamais la valeur. APPLIQUÉ.**
- La levée du refus porte désormais un `field` constant, plus la valeur de l'opérateur : `Inventory.php:101` (`['field' => 'numero_type']`), `:106`, `:110` (`'thematique'`), `:117`+`:128` (`'pdf_cle'`, `'date_cle'`, `'liaison.cle'`). L'ancien `['key' => $valeur]` a disparu partout.
- Le nom n'est réémis sur stderr qu'au point de sortie de l'outil, filtré par une **liste fermée écrite dans le code** : `inventorier-numeros:42` → `['numero_type', 'thematique', 'pdf_cle', 'liaison.cle']`, puis `:44` `json_encode(['field' => …])`. Exactement les quatre noms de l'arbitrage. Le point commun A-11 (`Runtime::refusalMessage`) reste inchangé (diff vide) : il ne rend que le code ; c'est l'outil qui rajoute le champ whitelisté.
- La valeur de l'opérateur ne transite plus dans `details` : aucune fuite possible.
- Mode d'emploi aligné : `README.md:17` (« `A16_MAPPING_KEY_ABSENT` ajoute seulement `{"field":"numero_type"}`, …, jamais la valeur fournie »).
- **Un test par champ** (consigne) : `inside.py` boucle sur les quatre champs, injecte la valeur-canari `A16_MAPPING_PRIVATE_CANARY`, et exige `stderr == A16_MAPPING_KEY_ABSENT {"field":"<champ>"}` **et** `CANARY` absent de la sortie. Liste obligatoire mise à jour : `verify.py:25` (`absent_mapping_field:*`, l'ancien `absent_mapping_key_code_only` retiré). Preuve livrée : les 8 cas (4 champs × classic/HPOS) sont PASS avec le bon stderr et sans canari.

*Précision (pas un écart) :* la liste fermée tient quatre champs. `article_type` et `date_cle` sont aussi des champs de la correspondance et peuvent lever `A16_MAPPING_KEY_ABSENT` ; comme ils ne sont pas dans la liste, ils sortent en **code seul**. C'est conforme à la lettre de l'arbitrage (qui énumère ces quatre noms), pas au-delà. À connaître : si l'opérateur se trompe sur `article_type` ou `date_cle`, il reçoit le code sans le champ.

**Règle nouvelle « parcours du mode d'emploi » (A-FAIRE.md ligne 26) — APPLIQUÉ.**
Un test lance la commande documentée (`README.md:6`, `python3 …confine.py …`) avec **les seuls arguments de sa ligne** et exige exit 0 + rapport conforme : `inside.py` → `readme_command_only_documented_arguments`. PASS classic/HPOS.

**Règle du chemin de refus pour un lien symbolique (arbitrage A-17, applicable à A-16) — APPLIQUÉ.**
Test ajouté `symlink_canary_never_output` : un lien nommé `A16_IDENTITY_PRIVATE_CANARY` donne `stderr == A11_SYMLINK_UNSUPPORTED` sans jamais recopier le nom. PASS classic/HPOS.

## 2. Résultat des tests

- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` → dernière ligne :
  `REJEU : 1123 tests, 34569 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`
  (dont `T01 TOOL : a16 ; 23 controls ; 0 failures` — les unités PHP pures sont bien rejouées en local).
- Paquet natif livré `production/A-16/preuves/final/result.json` : 0 FAIL, `exit_code 0` ; les 8 `absent_mapping_field:*`, les 2 `symlink_canary_never_output`, les 2 `readme_command_only_documented_arguments` sont PASS, stderr vérifié ci-dessus.
- `production/A-16/verification.json` : `PARENT_GATES_PASSED`, `exit_code 0`. Marqueur `production/A-16/PRET` redéposé (12 h 14, « non clos »).
- Non rejoués ici (droits §3, pas de Docker avec extensions sous licence) : la matrice native classic/HPOS (`inside.py`) et la suite complète du runner. Je constate leur verdict dans le paquet livré, lié au code par empreintes — même limite qu'aux deux tours précédents.

## 3. Régression / modification non demandée

Aucune régression fonctionnelle. Le refactor de `Inventory.php` (boucle sur des noms de champ au lieu des valeurs) conserve les conditions de refus ; seul le contenu du détail change (constante au lieu de valeur). Deux changements non strictement demandés, tous deux bénins et traçables :
- `verify.py` gagne un mode `--candidate` et un contrôle `candidate_parent_build_explicitly_pending` ; le mode final conserve `preparer_image_executed`. C'est de l'outillage d'empaquetage (étape candidat → parent), sans effet sur l'outil A-16.
- La version de Python reportée passe de 3.14.7 à **3.14.6** et un contrôle `platform=='win32'` est ajouté (`verify.py`, `README.md:19`). C'est un alignement sur l'environnement réel (`C:/Python314`), pas une régression.

L'ancien contrôle `absent_mapping_key_code_only`, qui attestait le comportement fautif (« code seul »), est retiré : c'est précisément ce que la retouche corrige.

## 4. Verdict

**Prêt pour la clôture.**

Le seul point que la vérification précédente remontait à Ced — le refus qui ne nommait plus la clé absente — est résolu exactement comme Ced l'a arbitré à 10 h : le refus nomme le **champ** de la correspondance (liste fermée de quatre noms écrits dans le code), jamais la valeur de l'opérateur, avec un test par champ et le canari absent. La règle « parcours du mode d'emploi » et le chemin de refus du lien symbolique sont également couverts par un test. Tous les tests accessibles sont verts (rejeu 1123/34569, paquet natif exit 0). Aucune régression ni réserve de fond restante.

---
*Rappel doctrine : ce verdict de vérification n'est pas un GO (§6). Il ne vaut que pour la clôture du lot de code.*
