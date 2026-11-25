# Relecture A-08 — La répétition de la bascule (relecteur Claude, indépendant)

Date : 2026-11-25. Brief : `briefs/A-08-repetition-de-la-bascule.md`.
Production relue : `wp/outils/bascule/repeter`, `wp/outils/bascule/a08/sequence.py`,
`wp/outils/bascule/repetition.md`, `wp/outils/bascule/comparer`, `wp/tests/a08/`,
`production/A-08/` (manifeste, notes, preuves `2bbcefb53170`, vérifications).
`relectures/A-08/codex.md` **non ouvert** (consigne). Fusion **non faite** (consigne).

## Rejeu de la suite autorisée

Commande, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, hors réseau, dépôt monté en lecture seule. Dernière ligne :

```
REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Blibliothèques PHP couvertes : imagine-connecteur (37), imagine-non-regression (6 fichiers),
imagine-pilotage (27), imagine-site (3). **Limite de ce rejeu** : il ne joue **que** le PHP
(PHPUnit). L'orchestration A-08 (`a08/sequence.py`) et l'intégration réelle (`wp/tests/a08/inside.py`)
sont du Python et tournent dans un **autre** conteneur, via `python -B wp/tests/a08/run.py` — hors
de la commande autorisée, et non rejoué ici (Docker + image A08 + extensions sous licence requis).
Ces tests-là, je les ai vérifiés **par lecture du code et des preuves livrées**, pas par ré-exécution.
Voir point I.1.

## 1. Conformité

Les cinq attendus du brief sont présents.

- **Séquence (1).** `repeter` enchaîne audit → photo « avant » → mise à jour (A-04) →
  nettoyage (A-05) → photo « après » → comparaison (`a08/sequence.py:110`). Ordre exact figé
  et testé (`test_sequence.py:25`).
- **Aucune logique ajoutée (2).** Le wrapper n'appelle que les outils natifs avec leurs
  arguments (`commands()`, `a08/sequence.py:176`) ; les attestations GO sont seulement
  transmises, jamais fabriquées (`--go=` ajouté tel quel, `sequence.py:180`). Deux rendez-vous
  opérateur (`--mutations-ready`, `--reception-ready`) encadrent les écritures et la réception :
  aucun garde-fou A03/A04/A05 n'est retiré ni contourné.
- **Arrêt au premier refus/anomalie (3).** `sequence.py:157` fixe `status = ARRÊT : <étape>
  (code X)`, écrit `look_at`, et renvoie le code natif (1 refus, 2 anomalie). Reprise à la
  première étape non réussie ; les cas non reprenables (`A05_UNINSTALL_AMBIGUOUS`, lecture
  coupée) sont décrits dans `repetition.md`.
- **Un seul rapport (4).** `report()` réécrit un unique `rapport.md` : chaque étape, sa durée,
  son résultat, ses preuves, puis la comparaison attendu/anormal. Aucune valeur de base
  (vérifié : voir §4).
- **Marche à suivre (5).** `repetition.md` donne l'ordre, les commandes exactes, les préparations,
  les arrêts normaux (75) et anormaux, et marque les endroits à GO écrit.

Choix de périmètre signalé (doctrine §1) : commande **à côté** du lanceur plutôt que modification
de `lancer` — justifié dans `notes.md` (le lanceur accepté ne prend ni argument ni état) ; le
docstring de `repeter` confirme « the accepted numbered launcher is untouched ». Interprétation
« idempotence métier, pas immobilité technique absolue » signalée franchement dans `notes.md` et
le rapport de livraison. **Conforme sur ce point** : l'écart est déclaré, pas masqué.

## 2. Exactitude métier — déroulé à la main

Lot d'orchestration : pas de nouvelle règle métier. J'ai déroulé à la main les quatre cas de
preuve du brief, à partir des preuves brutes du paquet retenu `preuves/2bbcefb53170` (classique ;
HPOS identique) :

- **Chaîne complète, seuls les changements attendus.** `comparaison-1-stdout.log` : 4 changements,
  tous `class: attendu` (versions.wordpress, versions.woocommerce, actions.32, action_days),
  `anormal: 0`, reçu `exit: 3`. Accepté car `code ∈ {0,3}` et aucun anormal (`sequence.py:153`). ✔
- **Échec au milieu → arrêt.** `classic-refused-checkpoint.json` : `done = [audit, avant]`,
  dernière tentative `mise-a-jour`, 3 tentatives seulement, `status: ARRÊT`. `mise-a-jour-1-stderr.log`
  = `A04_MAINTENANCE` (vrai refus natif), appel `exit: 1`. Ni nettoyage ni « après » lancés. ✔
- **Reprise.** `classic-resumed-call.json` : `exit: 75` ; l'état passe à
  `[audit, avant, mise-a-jour, nettoyage]` sans rejouer la photo « avant » (scellée). ✔
- **Second passage → rien ne change.** `comparaison-2` : code 0, liste vide ;
  `second_native_business_invariants` borne les écritures techniques à `.maintenance` et au
  transient WCS, tout le reste identique. ✔

Cas limites couverts par les tests que j'ai lus : entrée modifiée entre deux appels
(`A08_IDENTITY_CHANGED`), preuve scellée altérée (`A08_EVIDENCE_CHANGED`), symlink enfant refusé
sans appel natif, état demandé dans le site refusé, anomalie code 2 jamais requalifiée, log PHP
sale avant mutations, exécutable natif manquant, `--new-pass` refusé si incomplet, verrou de site.

**Durées mesurées** (cumulées, deux passages + refus, attentes opérateur/sauvegardes exclues) :
mise à jour ~82,8 s (classique) / ~82,3 s (HPOS) domine ; tout le reste 2–3 s ; comparaison < 0,1 s.
Fenêtre d'un passage : ~84,3 s (classique) / ~85,6 s (HPOS). Le rapport de livraison le précise ;
`notes.md` rappelle que ces petits sites fictifs ne dimensionnent pas le vrai site. Cf. point II.3.

## 3. Tests

- Suite PHP autorisée : **au vert** (REJEU ci-dessus), inchangée par A-08.
- Tests A-08 (non rejoués ici, lus) : 14 unitaires d'orchestration (doubles de `runner`, jamais
  de preuve native) + intégration réelle classique/HPOS sur le banc A04/A05 (`inside.py`,
  49 contrôles natifs), tous rapportés réussis dans `runner.json`/`result.json` du paquet retenu.
- Les tests vérifient la **règle** et pas seulement le code : `inside.py` relance les vrais outils,
  provoque un vrai `A04_MAINTENANCE`, compare des empreintes base+fichiers avant/après, et interdit
  toute fuite de jeton fictif dans le rapport (`single_report_six_rows_private`).

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Le rapport exclut les valeurs de base : canari
  `BASE_VALUE_CANARY` absent du rapport (`test_sequence.py:78`), et `inside.py` interdit
  `@example.org`, `Fiction`, `a08_orphan_setting` dans `rapport.md`.
- Isolation du banc A-08 vérifiée : réseau absent, pas de montage/port, capacités retirées,
  propriété contrôlée avant suppression par nom exact (`run.py`, `inspect-*`/`runner.json`).
- Extensions sous licence lues depuis le NUC hors dépôt (`/home/ced/staging-wp/...`), conforme §3.
- GO réels : aucun demandé ni implicite ; `PRET` porte `not_a_real_go: true`. Les deux GO A-04 et
  A-05 restent distincts et simplement transmis.

## 5. Doctrine

- « Standard d'abord » respecté : A-08 n'ajoute aucune logique, il orchestre des outils existants.
- Rejouable / non-régression : la séquence est un script versionné, reprenable, idempotent au sens
  métier ; photos « avant »/« après » + comparaison intégrées.
- Conventions §5 : l'orchestrateur est en Python, comme A-04/A-05 ; le code métier PHP n'est pas
  touché. `comparer` est en PHP strict. Rien à redire.
- Transparence §7 : `notes.md` trace les limites (départ WP 7.0, pas de montée 6.9.1→7.0, fixtures
  HTTP en rollback, `__pycache__` A-05 orphelin laissé intact). Candide et correct.

## Verdict

**Conforme.** Aucun point **bloquant**, aucun point **important** au sens d'un défaut de code.
Les livrables font ce que le brief demande, les quatre preuves se déroulent, la suite PHP autorisée
est au vert. Les réserves ci-dessous sont des **mineurs** et une **limite de ma vérification**.
Ce verdict **n'est pas un GO** (doctrine §6).

### Limite de ma vérification (à lever avant clôture)

- **I.1 — L'orchestration A-08 n'est pas couverte par le rejeu autorisé.** `rejouer.ps1` ne joue que
  le PHP. Les tests qui prouvent `sequence.py` et la chaîne réelle (`wp/tests/a08/`) tournent via
  `python -B wp/tests/a08/run.py`, que je n'ai pas lancé. Je les ai validés par lecture + preuves
  livrées, non par ré-exécution. *Défaut proposé (technique)* : le second tour « prêt pour la
  validation » doit confirmer que ce rejeu Docker A-08 fait partie de la porte verte, sinon la
  logique propre du lot n'est jamais re-jouée par un relecteur.

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

- **II.2 — Le rapport final écrase la comparaison du premier passage.** `sequence.py:152` remplace
  `checkpoint['comparison']` à chaque passage ; après un second passage complet, `rapport.md`
  affiche « attendus : 0, anormaux : 0 » (passage 2) et **perd** les 4 changements attendus du
  passage 1. La preuve brute `comparaison-1-stdout.log` les garde ; le rapport lu par Ced, non.
  Sans incidence le jour réel (un seul passage). *Défaut proposé* : conserver dans `rapport.md` la
  comparaison de chaque passage, ou indiquer à quel passage se rapporte la ligne affichée.
- **II.3 — Durées du rapport cumulées sur tentatives et passages.** `report()` (`sequence.py:38-42`)
  somme toutes les tentatives : « mise-a-jour 82,857 » agrège un refus + deux mises à jour réelles
  sur deux passages. La fenêtre d'un seul passage (~84 s) n'apparaît que dans le rapport de
  livraison, pas dans le `rapport.md` que Ced regarde pendant la bascule. *Défaut proposé* :
  préciser dans le rapport que les durées sont cumulées, ou isoler la durée du premier passage.
- **II.4 — Empreinte d'identité trop large.** `sequence.py:76-77` hache **tous** les fichiers sous
  `wp/outils/bascule` (`base.rglob('*')`), y compris des outils sans rapport (a09, a10,
  `inventorier-codes`…). Toucher n'importe lequel pendant une répétition en cours bloque la reprise
  par `A08_IDENTITY_CHANGED`. Fail-closed, donc prudent, mais surprenant le jour réel. *Défaut
  proposé* : restreindre l'identité aux outils réellement invoqués (audit, non-regression,
  mettre-a-jour, nettoyer, comparer + support a03/a04/a05), ou documenter la contrainte dans
  `repetition.md`.
- **II.5 — Refus non propre hors Linux.** `import fcntl` (`sequence.py:65`) est dans le `try`, mais
  le `except` final ne capte pas `ImportError` (`sequence.py:170`). Lancer `repeter` directement sur
  un hôte non-Linux produit une trace au lieu d'un code d'arrêt stable. Prévu pour tourner en
  Docker Linux (`repetition.md:63`), donc risque faible. *Défaut proposé* : capter `ImportError`
  et rendre un refus stable, ou documenter « Linux/Docker uniquement ».

### Pour Ced (usage, touche au réel)

- **III.6 — Lisibilité de la marche à suivre sous pression.** `repetition.md` est exacte et
  complète mais très dense (sigles MU, 503, codes 75/1/2/3, « garde staging »…) pour une page que
  tu liras le jour J, sous tension. Question fermée : **la garde-t-on telle quelle (exacte mais
  dense), ou ajoute-t-on une ligne en clair par bloc ?** *Défaut proposé* : garder le contenu exact
  et ajouter une phrase d'intro simple par bloc (sans changer les commandes).

## Suite

`codex.md` existe mais n'a pas été ouvert, conformément à la consigne. La fusion
(`corrections/A-08.md`) **n'est pas faite** : elle attend ton feu vert, après lecture de ce rapport.
