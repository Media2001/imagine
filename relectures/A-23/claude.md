# Relecture A-23 — Comptes des abonnés (Claude, relecteur indépendant)

Lot : A-23. Brief : `briefs/A-23-comptes-des-abonnes.md`. Cahier des charges : §4.3.
Production relue : `wp/outils/bascule/a23/`, `wp/tests/a23/`, `production/A-23/`.
`relectures/A-23/codex.md` **non ouvert**. Fusion **non faite** (demandée plus tard).

Rejeu PHP autorisé, sans argument, depuis la racine :
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
(conteneur jetable, réseau `none`, rootfs en lecture seule, dépôt monté `ro`).

> REJEU : 1126 tests, 35550 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

Ligne jumelle des outils purs :
> OUTILS : 16 outils, 311 contrôles, 0 échecs ; hors rejeu : aucun

Outil A-23 dans ce rejeu : `a23 ; 34 controls ; 0 failures ; exit=0`.
Note : la commande autorisée ne rejoue que la **suite PHP**. La matrice Python
(`wp/tests/a23/matrix.py`, `verify.py`) est hors de cette commande ; je ne l'ai pas
lancée (droits : « les tests du lot, en local » via la commande donnée). Les reçus
Python figurent dans `production/A-23/preuves/final/` et `FINALISATION.md`.

---

## 1. Conformité

- Les cinq familles de nombres demandées par le brief sont toutes produites, pour
  les comptes hors administration :
  - familles d'empreinte par préfixe seul → `Analysis::analyse` clé `families`
    (`wp/outils/bascule/a23/Analysis.php:40`, liste fermée + `autre` + `vide`) ;
  - email vide / mal formé / partagé casse ignorée → clé `emails`
    (`Analysis.php:42`, `Analysis.php:47-49`) ;
  - login = email / collision de casse → clé `logins` (`Analysis.php:43`, `:50-51`) ;
  - abonnés vivants, « les mêmes nombres, à part » → `live_readers`
    (`Analysis.php:58`) ;
  - sans aucune commande ni abonnement → `without_commerce` (`Analysis.php:59-62`).
- Lecture seule, par le lanceur confiné (A-12) et le gardien des sorties (A-22) :
  `confine.py:39` (`stream_guard.py::supervise`), `confine.py:40` (clôture A-12).
  Aucun gardien recopié dans le lot (conforme au brief ; cf. README §Parcours).
- Dix lignes de standard WordPress dans le mode d'emploi : `README.md:5-14`, avec
  trois sources officielles datées (`README.md:18-20`) et le code installé cité.
- Deux lignes pour le mode d'emploi de l'audit : `production/A-23/readme-ajout.txt`.
- k-anonymat « moins de cinq fondu dans autres, comme A-20 » : `Analysis::pool`
  (`Analysis.php:65-76`) ; validé en sortie par `report.py` (`pool_valid`, `:20-36`).
- Sortie strictement fermée : que des nombres et des libellés d'une liste close
  (`report.py:8-13`, `projection` `:39-63`). Aucune empreinte, aucun fragment,
  aucun identifiant, aucune adresse, aucun nom.
- Régime « inconnu après neutralisation », jamais zéro, sur les six blocs
  `families`/`emails`/`logins` × (lecteurs, vivants) : `Analysis.php:54-56`,
  déclenché par la marque d'import `imagine_staging_disabled_plugins`
  (`Inventory.php:36-37`). L'import est lu, **pas modifié**.
- `production/A-23/PRET` = « prêt à relire, non clos » : cohérent, Hermès ne
  revendique pas la clôture (notes.md §« Porte parent toujours en attente »).

**Interprétations signalées (documentées par Hermès, à confirmer en métier)**

- i-1 — Périmètre de comparaison des collisions. Les doublons d'email et de login
  d'un lecteur sont cherchés contre **tous** les comptes, administration comprise
  (`Analysis.php:30-36`, README `:75-76`, notes.md §Décisions). Un lecteur peut
  donc être compté « partagé » parce qu'il partage son adresse avec un compte
  d'administration, pas forcément avec un autre lecteur. Choix défendable pour la
  reprise (une collision avec un admin est un vrai obstacle) et testé
  (`unit.php:67-71`). **Défaut proposé : garder (comparer contre tous les comptes).**

## 2. Exactitude métier — cas déroulés à la main

Banc fictif `wp/tests/a23/seed.php` : 32 comptes `customer` (i=0..31) + 4 comptes
de gestion (editor, shop_manager, rôle `a23_operator` avec `edit_users`, subscriber
portant une capacité `manage_*`). Sortie comparée :
`production/A-23/preuves/final/cp1252/native/classic-accounts/comptes.json`.

**Cas 1 — familles d'empreinte (lecteurs).**
seed : `$P$…` pour i=0..9 (10), `$wp$2y$…` pour i=10..29 (20), canari sans préfixe
i=30 (→ `autre`), empreinte vide i=31 (→ `vide`). Attendu : groupes phpass 10,
wordpress_bcrypt 20 ; `autres` = 1+1 = 2 (le canari `autre` et le `vide`, <5, fondus,
donc le canari n'est jamais isolé). **Sortie : phpass 10, wordpress_bcrypt 20,
autres 2. Conforme.** L'ordre `$wp$2y$` avant `$2y$` est respecté (`Analysis.php:14-16`).

**Cas 2 — email partagé casse ignorée (lecteurs).**
seed : `shared-0..4@example.org` (i=10..14) et `SHARED-0..4@example.org` (i=15..19)
→ 10 comptes en collision ASCII. De plus l'administrateur `editor` reçoit
`a23-fictif-31@example.org` (`seed.php:78`), adresse déjà portée par le lecteur i=31 ;
le lecteur i=31 est donc compté partagé (collision contre tous les comptes).
Attendu : 10 + 1 = 11. **Sortie : email_shared_case_insensitive 11. Conforme**,
et illustre i-1.

**Cas 3 — abonnés vivants (sous-population).**
Vivant = abonnement `active|pending|on-hold|pending-cancel` (`Inventory.php:60-61`),
dédupliqué. seed : i=0..19 vivants (20), i=20..24 `expired`, i=25..26 `cancelled`,
le i=0 porte deux abonnements vivants (`seed.php:62-63`) et reste compté une fois.
Attendu : 20 comptes ; familles phpass 10 + wordpress_bcrypt 10 ; login_equals_email 5
(seuls i=10..14 parmi les vivants) ; login_case_collision 5 (i=0..4, comparés à
cASE0..4 non vivants → collision globale conservée). **Sortie : 20 / phpass 10 /
wordpress_bcrypt 10 / login_equals_email 5 / login_case_collision 5. Conforme.**

**Cas limite — exclusion administration + collision conservée.**
32 lecteurs exactement en sortie : les 4 comptes de gestion sont exclus, y compris
le subscriber à capacité `manage_*` et le rôle custom `a23_operator` (détection
inclusive A-17, `Inventory.php:68-69`). Si l'un n'avait pas été exclu, `readers`
vaudrait 33. **readers = 32. Conforme.**

**Cas limite — sans historique commercial.**
i=29,30,31 sans commande ni abonnement (`seed.php:39-59`). Attendu 3, fondu (<5).
**Sortie : without_commerce autres 3. Conforme.**

**Cas limite — neutralisation.**
`classic-neutralised/comptes.json` : les six blocs = « inconnu après neutralisation »,
tandis que readers 32 / live 20 / without_commerce 3 restent lisibles. **Conforme**
au brief (« jamais zéro »). Notes.md dit lesquels restent utiles : résultat présent.

**Rien n'est écrit / rejouable (vérifié sur les reçus) :**
- empreintes de tables identiques avant/après : `classic-db-before.json` ==
  `classic-db-after.json` ; idem variante neutralisée ; idem HPOS. (diff : identiques.)
- rejeu idempotent : `classic-accounts` == `classic-repeat`.
- racine en lecture seule : `classic-accounts` == `classic-root-readonly`.
- HPOS == classique (hors `audit_sha256`) : mêmes nombres sur les deux magasins.
- deux contextes complets : dossiers `utf8/` et `cp1252/` présents.

**Canaris :** recherche sur les 109 fichiers de `production/A-23/preuves/` des
jetons `*_PRIVATE_CANARY`, `@`, `example.org`, `shared-/SHARED-`, `a23-fictif`,
`Case/cASE` → **aucune occurrence**. Aucun fragment d'empreinte, identifiant,
adresse ou nom ne sort d'aucune voie.

## 3. Tests

- Suite PHP rejouée dans le conteneur autorisé : **PASS** (ligne REJEU ci-dessus).
- Les tests purs vérifient la **règle**, pas seulement le code :
  `wp/tests/a23/unit.php:33` (mappe `$wp$` sans `2y` → `autre`, `$H$` → `phpass_h`),
  `:35-37` (seuil k-anonymat, zéros fondus), `:49-52` (login=email exact, sans
  historique), `:70-72` (admin exclu mais collision conservée + aucune sortie
  privée), `:73-83` (neutralisation inconnue mais compte préservé), `:84`
  (population vide).
- Contrôle statique du standard contre le code WordPress installé :
  `wp/tests/a23/standard.php:16-36` (branche MD5 ≤32, branche `$wp`, HMAC SHA-384,
  branche phpass, `password_verify`, filtre bcrypt par défaut, reconnaissance
  `$P$`/`$H$`), empreintes de sources scellées, **sans essai de mot de passe**.
- Confinement/fuite côté lanceur : `wp/tests/a23/test_launcher.py` vérifie qu'un
  argument inconnu ne recopie pas sa valeur (`:26-28`), le refus en cp1252 réel
  (`:34-36`), le refus fermé quand le gardien A-22 manque (`:38-46`).
- Cas limites couverts : dates/statuts d'abonnement expiré et annulé exclus du
  vivant, double abonnement non doublé, email vide vs mal formé vs partagé,
  collision de casse vs répétition identique.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle ; jeux fictifs en `@example.org` et canaris
  manifestement inventés (`seed.php`). Conforme doctrine §3.
- Sortie fermée côté serveur : la publication n'a lieu qu'après code de fin, EOF
  des deux flux **et** validation stricte `report.py::complete_report`
  (`confine.py:69-73`). `report.py:20-36` borne `autres` (`<= 4·(labels restants)`)
  pour qu'un groupe ≥5 ne puisse se cacher dans `autres`.
- Requêtes : lecture seule, identifiants de tables entre accents graves et valeurs
  d'option en clause fixe (`Inventory.php:33-44,65`) ; échec dur si `last_error`
  (`Inventory.php:13-16`). Le magasin natif fait seul autorité ; aucun
  rapprochement par email (`Inventory.php:38`). Lien client malformé → refus, pas
  « aucun historique » (`Inventory.php:49-55`).
- Chemins : sortie disjointe du site et du dépôt dans les deux sens, base en
  `[A-Za-z0-9_-]`, refus de réécriture/lien symbolique, audit borné à 16 Mio et
  rattaché au bon parent (`Command.php:31-47`, miroir `confine.py:47-54`).
- Erreurs : jamais de chemin ni de nom tiré du site ; seuls des codes fermés
  (`refusals.json`) et, pour un fichier de remplacement, un nom technique d'une
  liste close (`confine.py:16-18`). `display_errors`/`log_errors` à 0, fonctions
  dangereuses désactivées, `A23_CONFINED` exigé (`inventorier-comptes:8-15`,
  `Command.php:21-23`, `confine.py:63-67`).
- Aucune empreinte essayée, aucune notification, aucun compte modifié (confirmé
  par db avant==après et par `pre_wp_mail` neutralisé dans le banc, `seed.php:5`).

## 5. Doctrine

- Standard d'abord : reconnaissance par préfixe seul, aucune réimplémentation de
  `wp_check_password` ; réutilise les coutures A-02/A-11/A-12/A-17/A-22
  (`inventorier-comptes:19-26`). Conforme §4.
- Conventions §5 : `declare(strict_types=1)`, espace de noms `Imagine\…`, préfixe
  `imagine_`/`A23_`, PSR-12 (notes.md : zéro erreur/avertissement), README présent.
- Préinitialisation des quatre filtres `pre_as_*` via le mécanisme natif
  `WP_Hook` (`Inventory.php:24-29`, README `:87-93`) : évite la recréation de
  tâches Action Scheduler sur copie neutralisée, sans toucher au Runtime ni aux
  autres lots ; le SQL READ ONLY reste la barrière de fond. Besoin transversal
  correctement **signalé au parent, non appliqué ailleurs** (notes.md §Besoin
  transversal). Bon réflexe de traçage d'écart.

**Décisions techniques, défaut proposé**

- t-1 — Détection de neutralisation par simple présence de l'option
  `imagine_staging_disabled_plugins` (`Inventory.php:36-37`). La marque pouvant
  être posée dès la neutralisation seule, le choix est volontairement conservateur
  (« inconnu » plutôt que fuite d'un zéro faux). Dépendance à documenter si l'outil
  d'import change cette marque. **Défaut proposé : garder le comportement prudent
  actuel.** Arbitrage Claude après coup.

## Verdict

**Conforme.** (Rappel doctrine : un verdict de relecture n'est jamais un GO.)

Points classés :
- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur** :
  - i-1 — périmètre de comparaison des collisions inclut l'administration
    (interprétation documentée et testée ; défaut proposé : garder).
  - t-1 — détection de neutralisation sur présence d'option (conservateur ;
    défaut proposé : garder ; dépendance à surveiller côté import).

Le lot fait ce que le brief demande, ni moins ni plus : il compte, il ne décide
rien de la reprise. Rejeu PHP au vert, cas du cahier des charges déroulés à la main
et confirmés, étanchéité des sorties vérifiée sur les 109 fichiers de preuve.

`codex.md` présent mais non lu. **Fusion non réalisée** (conformément à la consigne).
