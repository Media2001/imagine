# Vérification A-23 — second tour (après requalification)

Lot : A-23. Base relue au tour 1 = commit `13c4d43e` (vérification déposée
26/11 23:33). Modifications d'Hermès depuis : requalification du 27/11 05:03
(nouveau paquet natif sur l'import A-28 gelé). Consigne : `A-FAIRE.md` §1
(« A-23 : code inchangé, clôture sur le paquet refait après A-28 »). Arbitrage :
`docs/arbitrages-2026-11-27.md` §« A-23, A-24, A-25 » (l. 35-41) et l. 91
(« rien de changé au fond ; toujours clôture sur le paquet refait »). T-03,
consigne 0 : `rejeu.json` ajouté lot par lot avant le sceau. Ce n'est pas une
relecture complète : je contrôle que la consigne de requalification est appliquée,
sans régression.

---

## 1. Consignes et arbitrages concernés

**Code métier inchangé (consigne §1 ; arbitrage l. 91).** **Appliqué.**
`git diff 13c4d43e HEAD -- wp/outils/bascule/a23/ wp/tests/a23/` = **vide**. Ni
`Inventory.php`, ni `Analysis.php`, ni `README.md`, ni `refusals.json`, ni le banc
n'ont bougé depuis la vérification n° 1. Les quatre corrections de la fusion déjà
vérifiées (règle inclusive A-17, garde-fou `A23_ROLE_IDENTIFIER_UNSAFE`, banc
classique+HPOS, périmètre intact) restent en l'état.

**Alignement sur la règle d'A-17, six comptes de gestion masqués exclus, classique
et HPOS (arbitrage l. 37).** **Appliqué** (inchangé). Les reçus natifs
`preuves/final/{utf8,cp1252}/native/role-definitions.json` sont présents des deux
côtés (`classic:role_negative_override_excluded`, `…:role_multi_management_excluded`,
etc.). Totaux préservés : `readers.accounts` = **32**
(`…/classic-accounts/comptes.json:8`).

**Chemin absolu de Python conservé dans la commande du mode d'emploi (arbitrage
l. 41).** **Appliqué.** `README.md` inchangé ; la commande d'exemple reste en
`C:/Python314/python.exe` (chemin du poste de contrôle, exigé par la règle du
parcours du mode d'emploi). Ce n'est donc plus une « modification non demandée »
mais un choix tranché.

**Paquet unique, essais intermédiaires hors dépôt (`A-FAIRE.md` l. 55).**
**Appliqué.** `production/A-23/candidate-verification.json` (663 lignes) **supprimé** ;
un seul `preuves/final/`. Nouveaux reçus de la matrice : `rejeu.json`,
`native/result.json`, `native/role-definitions.json`, `parent-gates.json`,
`verify.py` étendu.

**Déclaration `rejeu.json` avant le sceau (T-03, consigne 0).** **Appliqué.**
`production/A-23/rejeu.json` présent, `"entrypoint": "verify.py"`, liste close des
logs et des 77 contrôles du lot.

**Ne pas revendiquer les portes du parent (`parent_gates_not_claimed`).**
**Appliqué.** `PRET` : « A22 non clos ; aucun GO réel ». `notes.md` : « la preuve
PAQUETS verte finale relève de T03, jamais inventée ici ».

## 2. Résultat des tests

Commande exacte lancée :
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
(non refusée). Dernière ligne :

> REJEU : 1153 tests, 36075 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

Lignes jumelles : `OUTILS : 22 outils, 582 contrôles, 0 échecs` ;
`PAQUETS : 9 vérifiés, 0 échecs` (dont **A-23**). Outil A-23 dans ce rejeu :
`a23 ; 34 controls ; 0 failures ; exit=0`. Le `T01_RESULT` final porte
`"pass":true` et liste A-23 dans `packets.lots`.

*Honnêteté d'exécution :* la toute première invocation a vu sa sortie tronquée par
le tampon d'affichage (fin de ligne non atteinte). La relance intégrale ci-dessus
donne la ligne PASS complète ; ce n'était pas un échec de test.

La matrice native Python (`verify.py`, `matrix.py`) n'est pas rejouée par cette
commande, qui ne couvre que la suite PHP ; les reçus natifs sont ceux livrés par
Hermès (import A-28 gelé), non reproduits indépendamment ici — comme au tour 1.

## 3. Régressions ou modifications non demandées

- **Aucune régression de logique** : code strictement inchangé.
- Totaux métier **identiques** à la vérification n° 1, classique et HPOS :
  `readers` 32 (phpass 10, wordpress_bcrypt 20, autres 2), `live_readers` 20,
  `without_commerce` autres 3 (`…/classic-accounts/comptes.json`,
  `…/hpos-accounts/comptes.json`). Seuls les `audit_sha256` changent, recalculés
  sur l'import A-28 gelé : c'est l'effet attendu d'un paquet refait, pas une dérive
  métier.
- Nettoyage conforme : suppression de l'artefact intermédiaire
  `candidate-verification.json`. Aucune modification hors du périmètre A-23.

## 4. Verdict

**Prêt pour la clôture.**

Le code est inchangé depuis la vérification « prêt » du premier tour ; la consigne
de requalification et l'arbitrage du 27/11 sont appliqués (paquet refait sur
l'import A-28 gelé, `rejeu.json` déposé, un seul paquet) ; les totaux publiés sont
préservés classique et HPOS ; la suite PHP est au vert et A-23 figure dans les neuf
paquets vérifiés. Aucun problème de fond nouveau ne justifie un « Remonte à Ced ».

Rappels hors périmètre de cette vérification (déjà classés, non bloquants) : la
question métier **i-1** (collision d'un lecteur avec un compte d'administration ;
défaut proposé : garder) reste pour Imagine ; **A-22** demeure non clos ; la ligne
PAQUETS verte et le rejeu natif indépendant relèvent de T-03. Un verdict de
vérification n'est pas un GO réel (doctrine §6).
