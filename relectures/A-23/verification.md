# Vérification A-23 — second et dernier tour

Lot : A-23. Base : `corrections/A-23.md` (fusion), code corrigé par Hermès après
la fusion. État relu = commit `ab843bc2` (synchro 19:23, juste avant la fusion
19:42-19:48). Diff lu sur `wp/outils/bascule/a23/`, `wp/tests/a23/` et
`production/A-23/`. Ce n'est pas une relecture complète : je contrôle que les
instructions de la fusion sont appliquées, sans régression.

---

## 1. Instructions de `corrections/A-23.md` (§4)

**Instruction 1 — Corriger P1 (exclusion alignée sur la règle inclusive A-17).**
**Appliquée.** `wp/outils/bascule/a23/Inventory.php:64-77` construit
`$managementRoles` à partir des **définitions** de rôles
(`wp_roles()->roles`, test `\Imagine\AccountSecurity\Inventory::management($definition['capabilities'])`,
ligne 67) plus les trois rôles fixes (ligne 65). L'exclusion devient l'union :
`Inventory.php:82-83`, `array_intersect($user->roles, $managementRoles)` **ou**
`management($user->allcaps)`. La boucle sur les rôles précède la boucle sur les
comptes (ligne 66 avant 79). C'est bien le schéma d'A-17
(`a17/Inventory.php:62-84` : appartenance à un rôle par définition), complété par
la détection par capacités directes. Une surcharge négative masquant une capacité
de rôle ne fait plus basculer le titulaire en lecteur.

**Instruction 2 — Reprendre le garde-fou d'identifiant de rôle d'A-17.**
**Appliquée.** `Inventory.php:68-72` : un identifiant de rôle non conforme au
motif qui porte une capacité de gestion lève `A23_ROLE_IDENTIFIER_UNSAFE`
(ligne 70) ; sinon il est ignoré (ligne 72). Calque exact d'A-17
(`a17/Inventory.php:63-67`, `A17_ROLE_IDENTIFIER_UNSAFE`). Le code de refus est
déclaré dans la liste close `wp/outils/bascule/a23/refusals.json` (ajout d'une
ligne).

**Instruction 3 — Compléter le banc (classique ET HPOS) + assertions natives.**
**Appliquée.** `wp/tests/a23/seed.php:81-124` ajoute six titulaires d'un rôle de
gestion-par-définition (`a23_operator`) avec surcharge `add_cap('edit_users', false)`
(ligne 96) : cinq comptes « négative override » et un compte multirôle
`customer` + `a23_operator` (lignes 87, 93-94). Le seed vérifie lui-même le
masquage (lignes 100-108) et échoue (`A23_SEED_FAILED`) sinon. Trois masqués et
le multirôle reçoivent un abonnement vivant, deux masqués restent sans commerce
(lignes 109-119), pour éprouver les deux totaux publiés. Le seed étant partagé, il
est rejoué sur les deux magasins ; les reçus natifs livrés portent les cas des
deux côtés (voir §2). Assertions natives présentes et vertes :
`role_negative_override_excluded`, `role_multi_management_excluded`,
`management_without_commerce_excluded`, `no_false_published_family`,
`private_values_absent` (classic **et** hpos). Le vérificateur les exige
(`verify.py` : `mandatory_role_boundary_cases`, `role-definitions_all_pass`).
*Observation (ne bloque pas) :* le cas multirôle porte aussi la surcharge négative
— c'est un scénario combiné, plus fort que le minimum demandé ; l'exclusion y est
prouvée par la définition de rôle, la demande (b) est donc satisfaite.

**Instruction 4 — Ne rien changer d'autre (i-1 et t-1 au défaut, périmètre
collisions et détection de neutralisation intacts).** **Appliquée.**
`Analysis.php`, `Command.php`, `report.py`, `confine.py` sont **inchangés** depuis
l'état relu (diff vide). Le périmètre des collisions (i-1) et la détection de
neutralisation par présence d'option (t-1, `Inventory.php:36-37`) ne sont pas
touchés dans le code ; t-1 est seulement **documenté** comme dépendance au README,
conformément au défaut proposé au §5 de la fusion.

## 2. Résultat des tests

Exécutés en local dans cette session :
- `wp/tests/a23/test_role_corrections.py` : **5 tests, OK** (contrats de source :
  définitions avant capacités, refus fermé, seed, vérificateur, banc en processus
  séparé).
- `wp/tests/a23/test_verify.py` : **9 tests, OK**.
- `wp/tests/a23/verify.py` sur le paquet livré `production/A-23/preuves/` :
  **exit 0**, tous les contrôles `PASS`, dont `utf8/cp1252 : role-definitions_all_pass`,
  `mandatory_role_boundary_cases`, `neutralised_strict_projection`,
  `five_commands_all_pass`, `two_line_delta`, `exact_final_inventory_and_hashes`.

Contrôle des reçus natifs livrés (`role-definitions.json`, utf8) : **exit_code 0**,
28 contrôles `PASS` classic + hpos, dont `role_negative_override_excluded`,
`role_multi_management_excluded`, `management_without_commerce_excluded`,
`no_false_published_family`, `private_values_absent`,
`false_capability_keeps_reader`, `unsafe_management_role_closed:0..3`.

Totaux métier sur le reçu natif (`classic-accounts/comptes.json`) : **readers 32**,
phpass 10, wordpress_bcrypt 20, `autres` 2 ; **live_readers 20** ; **without_commerce
autres 3**. Identiques à l'exactitude validée en fusion : les six comptes de gestion
masqués sont bien exclus, aucune famille bcrypt n'apparaît à tort.

**Limite d'exécution (à consigner, comme au premier tour).** Je n'ai pas pu
ré-exécuter de façon indépendante la matrice Docker/native (`matrix.py`, `run.py`)
ni `role-probe.php` en PHP natif : l'environnement bloque l'appel `php` et le
runtime conteneur, exactement le mur rencontré par les deux relecteurs. Les reçus
natifs proviennent donc du paquet livré par Hermès ; je les ai revalidés par
`verify.py` (vert) et par les tests de contrat de source (verts), sans re-production
native indépendante. Un verdict n'est pas un GO (doctrine §6).

## 3. Régressions ou modifications non demandées

- Aucune régression de logique : les fichiers de calcul (`Analysis.php`,
  `report.py`) et de confinement (`confine.py`, `Command.php`) sont inchangés ;
  les totaux publiés sont préservés.
- Modifications non strictement demandées, toutes documentaires et bénignes, à
  signaler :
  - `README.md` : réécriture de la définition « Lecteur » (section Définitions et
    limites) — **cohérente** avec le correctif P1, souhaitable.
  - `README.md` : correction de citation `[S1]` → `[S2]` (ligne 1) et ajout d'un
    paragraphe sur le « More Information » historique de S3 — hors périmètre de la
    fusion, sans effet sur le code.
  - `README.md` : paragraphe documentant les filtres `pre_as_*` (comportement déjà
    présent et relu, non introduit par la correction) et la dépendance t-1.
  - `README.md` : la commande d'exemple passe de `python` à
    `C:/Python314/python.exe` (chemin absolu propre à la machine). Détail de doc
    uniquement ; à surveiller s'il doit rester portable.
- Rappel : l'étanchéité (`A23_ROLE_HASH_PRIVATE_CANARY`,
  `A23_ROLE_NAME_PRIVATE_CANARY` dans le seed) est contrôlée par
  `private_values_absent` → aucune valeur privée en sortie.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les quatre instructions de la fusion sont appliquées, le P1 est corrigé en suivant
la règle A-17 annoncée, les cas de régression sont au banc (classique et HPOS) et
verts, les totaux publiés sont inchangés, aucune régression dans le code de calcul.
Aucun problème de fond restant ne justifie un « Remonte à Ced ».

Reste pour Ced, hors périmètre de cette vérification : (a) la question métier
ouverte **i-1** (une collision d'email/login d'un lecteur avec un compte
d'administration compte-t-elle ? défaut proposé : oui) — elle touche au réel et
revient à Ced ; (b) la décision de clôture et de reprise ; (c) la matrice native
n'a été rejouée en vert indépendamment par aucun des relecteurs ni par cette
vérification — seul `verify.py` valide le paquet livré.
