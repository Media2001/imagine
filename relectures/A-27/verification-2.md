# Vérification A-27 — tour de resceau (troisième passage)

Vérificateur : Claude. Date : 2026-11-27. Base de la vérification précédente : `relectures/A-27/verification.md` (HEAD `2ac3cd66`, 05:53). État vérifié : arbre courant (HEAD `4896fd84`).

Méthode : `git diff 2ac3cd66..HEAD` sur `wp/outils/bascule/a27`, `wp/tests/a27` et `production/A-27` ; relance de la commande autorisée `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` (qui joue aussi les vérificateurs de paquet sans argument). Je ne refais pas la relecture de fond : le code d'A-27 n'a pas changé depuis la dernière vérification.

**Ce qui a été modifié par Hermès depuis `verification.md`.** Un **resceau** (`production/A-27/RESCEAU-20261127.md`, 08:01) : matrice native réellement rejouée, nouveau `PRET`, `parent-gates.json`, `manifest.json` et `preuves/final/` régénérés. **Aucune ligne de code source touchée.** Cause : les corrections de T-03 (06:46) ont changé le lanceur de rejeu (`wp/tests/t01/`) que le paquet A-27 gèle ; son vérificateur était repassé rouge, le `PRET` retiré. Le resceau le relève.

---

## 1. Consignes / arbitrages concernés

- **`A-FAIRE.md:23-24` — « 0. Le resceau, une seule fois, sur l'import et le lanceur gelés : A-26, A-27, A-30, A-31. Des matrices réelles, jamais un changement d'empreinte. … code inchangé. Paquet refait, `PRET`. Ils se closent sur une ligne `PAQUETS` verte lue par un relecteur, sans nouveau tour de fond. » : Appliqué.**
  - *Code inchangé* : `git diff 2ac3cd66..HEAD -- wp/outils/bascule/a27 wp/tests/a27` est **vide** ; aucune empreinte de source a27 modifiée dans `production/A-27/manifest.json`.
  - *Matrice réelle, pas un changement d'empreinte* : `production/A-27/refresh-parent.json:3-21` journalise la commande native réelle (`a27-matrix.py --include-native --parent-serialized`, 07:54→08:00, `exit_code: 0`). Les preuves natives portent de nouveaux horodatages et de nouvelles liaisons SHA-256, mais les **comptes de paiement sont stables** : `…/native/classic-five/paiements.md` est identique octet pour octet, seule la clé `audit_sha256` suit la ré-exécution (ligne 79).
  - *Paquet refait et `PRET`* : `production/A-27/PRET:1` redaté `08:14:18` (« matrices natives réelles rejouées ; 11 paquets verts »). `parent-gates.json:47-48` → `exit_code: 0`, `commands: 19`, `fresh_native_replay: true`.
  - *Ligne `PAQUETS` verte lue par un relecteur* : voir §2 — relancée par moi, A-27 dans la liste des 11 paquets vérifiés, 0 échec.

- **`docs/arbitrages-2026-11-27.md:143-148` (passage de 7 h, « A-26 et A-27 — vérifiés “prêt”, pas clos : leur paquet est redevenu rouge ») — « Rien à corriger au fond. Ils se closent sur leur paquet refait une fois, et sur une ligne `PAQUETS` verte lue par un relecteur ; pas de nouveau tour de fond. » : Appliqué.**
  - Resceau porté sur le lanceur gelé, `PRET` redéposé, paquet A-27 revérifié vert par le rejeu indépendant. Aucun tour de fond refait, conformément à la consigne.

- **`A-FAIRE.md:19` + `docs/arbitrages-2026-11-27.md:148` — lanceur de rejeu (`wp/tests/t01/`, `wp/tests/rejouer.ps1`) gelé : Appliqué (hors périmètre A-27, constaté sans écart).** Le resceau n'a touché ni le lanceur ni l'import ; `RESCEAU-20261127.md:3` l'affirme et le rejeu s'exécute sur le lanceur inchangé.

- **`docs/arbitrages-2026-11-27.md:52` — « “Dans les six mois” : la borne reste au jour de l'audit du sixième mois » : Appliqué, inchangé.** `production/A-27/notes.md:3` et le code (non modifié) le confirment ; c'est un réglage rangé pour Imagine, pas un blocage.

## 2. Résultat des tests

Commande autorisée relancée (conteneur jetable, `network=none`, `rootfs=ro`, `wp` monté en lecture seule, nettoyage vérifié). Trois dernières lignes :

```
PAQUETS : 11 vérifiés, 0 échecs ; hors rejeu : aucun
OUTILS : 22 outils, 584 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1167 tests, 36333 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

- **`PAQUETS : 11 vérifiés, 0 échecs`** : A-27 figure dans la liste vérifiée (`T01_RESULT … "lots":[…,"A-27",…],"failures":[]`). C'est la ligne verte que la consigne 0 exige pour la clôture, obtenue indépendamment. Le paquet, rouge après T-03, est redevenu vert par le resceau.
- **`a27 ; 61 contrôles ; 0 échecs`** (banque PHP pure dans le conteneur).
- Écart de comptes avec `RESCEAU-20261127.md:10` (1166 → 1167 tests) : un test de plus, dû au mouvement global des suites ; `A-FAIRE.md:28` dit qu'un compte global qui bouge n'est pas un défaut du lot. `PAQUETS` et `OUTILS` sont identiques à la note d'Hermès.

**Limite inchangée.** Le rejeu autorisé joue les suites PHPUnit, la banque `a27` et les vérificateurs de paquet ; il ne ré-exécute pas la matrice native classique/HPOS (portes parent, hors de mes droits). Je confirme l'intégrité et la cohérence du paquet reselé, pas une ré-exécution native indépendante. C'est le périmètre du relecteur, pas un défaut.

## 3. Régressions ou modifications non demandées

- **Aucune régression de code.** Les sources d'A-27 (`Analysis.php`, `Inventory.php`, `README.md`, tests) sont inchangées depuis la vérification précédente : les corrections R1/R2/R3 déjà vérifiées tiennent telles quelles.
- **Comptes métier stables.** Les `paiements.*` natifs gardent leurs valeurs ; seules changent les liaisons SHA-256 et les horodatages liés à la ré-exécution. Pas de dérive des nombres présentés à la décision.
- **Variance environnementale dans l'audit, sans effet.** Dans les `audit.md` natifs, `wp_postmeta.bytes` et `total_bytes` bougent (ex. `classic-five-audit`, 311296 → 278528) et les `next_epoch` des crons sont recalculés : conséquence d'un nouveau conteneur, `rows` inchangés (1662). C'est le contexte d'audit, pas une sortie d'A-27. Sans incidence.
- **`parent-gates.json` allégé.** Le drapeau `A22_independent_review_closed: false` a disparu (remplacé par `fresh_native_replay: true`) : cohérent avec A-22 désormais clos (`docs/arbitrages-2026-11-27.md:137`), pas une régression. Les artefacts de qualification (`native-counts.json`, `phase-commands.json`…) retirés de la liste des gates relèvent du nouveau répertoire de resceau ; `commands: 19`, `exit_code: 0`.
- **`rejeu.json` nettoyé.** Les chemins de journaux éphémères (`files/rapports/…-qualification-A21-A27/…`) ont été retirés de `logs`, ne restent que les preuves du paquet (`production/A-27/preuves/final/…`). Self-contenance cohérente avec « un seul paquet de preuves par lot » ; le vérificateur de paquet passe au vert, donc le `rejeu.json` est cohérent avec le scellé. Non demandé explicitement, sans conséquence.
- **`corrections-1h30.md` toujours périmé** (déjà signalé au tour précédent) : décrit la 1re passe (« vérificateurs volontairement rouges, aucun PRET »). Incohérence documentaire sans effet sur le code ; une main habilitée pourrait l'annoter.

## 4. Verdict

**Prêt pour la clôture.**

Le resceau est exactement ce que la consigne 0 (`A-FAIRE.md:23-24`) et l'arbitrage de 7 h (`docs/arbitrages-2026-11-27.md:143-148`) demandaient : matrice native réellement rejouée, code inchangé, aucune empreinte de source modifiée, `PRET` redéposé, et **ligne `PAQUETS` verte obtenue par le rejeu indépendant du relecteur** (11 paquets, 0 échec, A-27 compris). Aucune régression, aucune modification de fond non demandée dans le périmètre A-27.

Il ne reste aucun problème de fond à remonter à Ced. Ce verdict n'est pas un GO sur le réel : les deux questions déjà rangées (seuil « six mois » pour Imagine ; comptage à la source sous GO écrit pour Ced) restent des conditions de réglage/réel connues, pas des défauts du lot. La clôture d'A-27 sur une ligne `PAQUETS` verte est acquise ; l'ultime requalification parent après la preuve finale de T-03 reste la seule étape de circuit attendue, hors droits du relecteur.
