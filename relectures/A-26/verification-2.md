# Vérification A-26 — resceau (tour complémentaire)

Lot : A-26. Objet : le resceau du 27/11 (consigne 0 de `A-FAIRE.md`), fait **après** la vérification « prêt » de `relectures/A-26/verification.md` (`PRET` du 05:03:18, retiré à 6 h 46 quand les corrections de T-03 ont changé le lanceur).
Méthode : `git diff` de l'état relu (`11685b06`, synchro 05:08, juste après le `PRET` 05:03) jusqu'à `HEAD`, sur `wp/outils/bascule/a26`, `wp/tests/a26`, `production/A-26`, l'import gelé (`wp/outils/staging`) et le lanceur gelé (`wp/tests/t01`, `rejouer.ps1`) ; relance de la suite autorisée. Pas de relecture de fond refaite.

## 1. Consignes et arbitrages concernés

### C0 — Resceau une seule fois, matrices réelles, jamais un changement d'empreinte, code inchangé (`A-FAIRE.md:23-24`) : **Appliquée**
- **Matrice réellement rejouée**, pas un échange d'empreinte : `production/A-26/refresh-parent.json:1-21` (nouveau) trace `FULL_REAL_NATIVE_MATRIX_REPLAY`, commande `wp/tests/a26/matrix.py`, début 07:42:40 / fin 07:46:24, `exit_code 0`.
- Preuves ré-exécutées, pas recopiées : conteneur neuf (`runner.json` : `imagine-a26-tiers-1b4ea1…` → `…9eb1a4cce896`, `at` 03:51 → 06:42), dossier de travail neuf (`windows-matrix.json` : scratch `requal2127-t03-20261127` → `a30-reader-resceau-0743`), tous les `log_sha256` et `audit_sha256` changés.
- **Code du lot inchangé** : `git diff 11685b06 HEAD -- wp/outils/bascule/a26 wp/tests/a26` = **vide**. Le resceau ne touche que `production/A-26/`.
- **Ligne PAQUETS verte lue par le vérificateur** (condition de clôture de la consigne) : voir §2.

### C0bis — Import et lanceur gelés ; une correction ne restructure pas un fichier commun (`A-FAIRE.md:17-21`, `arbitrages-2026-11-27.md:148`) : **Appliquée**
- Import gelé **intact** : `git diff 11685b06 HEAD -- wp/outils/staging` = vide. Le sceau de dépendances ne bouge pas (`production/A-26/preuves/final/dependencies.json` inchangé, les 7 empreintes de staging tiennent).
- Lanceur : `wp/tests/t01` a bien changé, mais ce sont **les corrections de T-03** (commits 06:53–07:03, avant le resceau), pas A-26. A-26 n'a touché ni `t01`, ni `rejouer.ps1`. Il a resellé **sur** ce lanceur gelé.

### A26 7 h — paquet refait une fois, `PRET` renouvelé, sans nouveau tour de fond (`arbitrages-2026-11-27.md:143-147`) : **Appliquée**
- `PRET` renouvelé : `production/A-26/PRET` passe de `05:03:18` à `2026-11-27T08:14:17` (« matrices natives réelles rejouées ; 11 paquets verts ; simulation seulement aucun GO réel »). Postérieur au resceau.
- Aucune correction de fond : les trois instructions de `corrections/A-26.md` (B1/I1/M1) restaient levées au tour précédent ; rien n'y a été rouvert.

### T-03 — A-20 entre dans le rejeu, `rejeu.json` par lot, un seul paquet de preuves (`arbitrages-2026-11-27.md:155`, `A-FAIRE.md:27,55`) : **Appliquée**
- `production/A-26/rejeu.json` élagué : il ne pointe plus vers les journaux de la qualification 05:03 (hors paquet), seulement vers les logs de `preuves/final/`. Ancien paquet sorti du dépôt (`refresh-parent.json` → `historical_outside_repository`).
- La ligne PAQUETS (§2) liste 11 lots, **A-20 compris**.

## 2. Résultat des tests (suite autorisée, relancée par le vérificateur)

Commande, telle quelle : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` (conteneur jetable, réseau coupé, dépôt monté en lecture seule). Dernière ligne :

`REJEU : 1167 tests, 36333 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Lignes complémentaires :
- `PAQUETS : 11 vérifiés, 0 échecs ; hors rejeu : aucun` — A-20, A-21, A-22, A-23, A-24, A-25, **A-26**, A-27, A-28, A-30, A-31.
- `OUTILS : 22 outils, 584 contrôles, 0 échecs ; hors rejeu : aucun`. Contrôle d'outils A-26 : `a26 ; 30 controls ; 0 failures ; exit=0`.

Lecture : le vérificateur de paquet d'A-26 **passe au vert, lu indépendamment** — le sceau refait colle au lanceur et à l'import gelés dans leur état courant. C'est la ligne PAQUETS verte exigée par la consigne 0 pour la clôture.

## 3. Régressions ou modifications non demandées

- **Aucune régression dans le périmètre A-26.** Code du lot inchangé, import et sceau de dépendances intacts, tout le vert tient.
- Écart de comptage attendu, non un défaut : la ligne REJEU (1167 / 36333) dépasse celle écrite dans `RESCEAU-20261127.md:10` (1166 / 36318) parce que l'arbre a avancé depuis le resceau (travaux A-32 de l'autre voie). Règle déjà tranchée : un compte global qui bouge parce qu'une autre voie livre n'est pas un défaut du lot (`A-FAIRE.md:28`). PASS et PAQUETS inchangés.
- Hors périmètre A-26, non imputable au resceau : l'arbre de travail porte des fichiers A-32 non suivis (`wp/outils/bascule/tournee/`, `wp/tests/a32/`) et un fichier parasite `prefix}u0024s` à la racine — à signaler à qui tient A-32, sans rapport avec ce lot.

## 4. Verdict : **Prêt pour la clôture**

Le resceau est une matrice réelle, pas un changement d'empreinte ; le code du lot n'a pas bougé depuis la vérification « prêt » ; l'import et le lanceur gelés sont intacts ; le `PRET` est renouvelé ; et la ligne `PAQUETS` est verte, A-26 compris, **lue indépendamment** par le vérificateur. C'est exactement la condition posée par la consigne 0 et l'arbitrage de 7 h.

La question ouverte de `verification.md` §4 (resceller maintenant ou attendre la stabilité de l'import) n'a plus lieu d'être : Ced l'a tranchée (`arbitrages-2026-11-27.md:30` — une seule requalification sur l'import final), l'import **et** le lanceur sont désormais gelés. Aucun problème de fond restant.

**Rappel : cette vérification n'est pas un GO réel.** Elle atteste que le paquet refait est valide et vert sur les dépendances gelées ; la clôture reste l'acte de Ced.
