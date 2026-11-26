# Vérification B-06 — 2e et dernier tour (après fusion `corrections/B-06.md`)

Vérificateur indépendant. Base : `git diff c0e07237..HEAD` sur `wp/` et `production/B-06`
(`c0e07237` = synchro 18:33, juste avant l'écriture de `relectures/B-06/claude.md` à 18:35),
relecture du code corrigé (`Cooperateurs.php`, `CooperateursRegles.php`, `b06-space.php`,
`b06-settings.php`, `b06-runtime.php`, `CooperateursReglesTest.php`), et contrôle des reçus
livrés. **Pas de relecture complète refaite** : seuls les cinq points de la fusion et les
régressions éventuelles.

---

## 1. Chaque instruction de `corrections/B-06.md`

### Instruction 1 — C1 : deux règles de rôle deviennent des réglages — **Appliquée**
- `CooperateursRegles.php:10` et `:17` : `administration()` et `lecture()` prennent désormais
  `array $autorises = ['administrator']` ; le rôle en dur a disparu
  (`array_intersect($roles, $autorises)`).
- `Cooperateurs.php:13-14` : deux options distinctes `ROLES_ATTRIBUT`
  (`imagine_cooperateurs_roles_attribut`) et `ROLES_LECTURE`
  (`imagine_cooperateurs_roles_lecture`).
- `Cooperateurs.php:96-104` (`reglages()`) : enregistrées dans le groupe existant
  `Reglages::GROUPE` (`imagine_reglages`), défaut `['administrator']`, `show_in_rest=false`.
- `Cooperateurs.php:131` (`champsReglages()`) : deux fieldsets séparés (poser/retirer vs lire),
  champs cochables Administrateur / Éditeur / Gestionnaire de boutique.
- **Défaut prudent conservé : Administrateur seul** (`A-VOIR.md`, readback
  `verification-fusion-finale-V2.json` → `roles_attribut=["administrator"]`,
  `roles_lecture=["administrator"]`).
- **`manage_options` seul ne vaut pas le rôle** : `nettoyerRoles()` (`Cooperateurs.php:118-120`)
  exige `current_user_can('manage_options')` **et** `administrator` dans les rôles, sinon
  conserve l'ancienne valeur (`add_settings_error`).
- Modifications contrôlées + journalisées (`journalReglages()` l.145-172, restauration si le
  journal échoue).
- `administration()` (l.184) et `autorise()` (l.189-195) et la défense
  `protegerObjets` (l.385-390) branchés sur les réglages.
- **Chaque configuration testée** : `b06-settings.php` déroule les 8×8 configurations
  (`config_{write}_{read}_...`), vérifie persistance, `administration()`/`autorise()`,
  capacité native `read_post`, valeurs invalides rejetées, capacité ≠ rôle
  (`_capacite_ne_permet_pas_configuration`), et **l'absence d'effet de bord sur le droit
  d'article** (`_article_inchange` par rôle, `_article_ferme` pour P-COOP) — exactement le
  point exigé par l'instruction.

### Instruction 2 — S1 : distinguer journal vide et lecture SQL impossible — **Appliquée**
- `Cooperateurs.php:272-274` (`audits()`) : après le `SELECT`, test
  `$wpdb->last_error !== '' || !is_array($rows)` → `throw new \RuntimeException` au lieu de `[]`.
- **Export** (`exporter()` l.421, l.429-434) : signature `array|\WP_Error` ; `audits()` en échec
  est capté et renvoie un `WP_Error` — plus de `done=true` silencieux omettant l'historique
  (WordPress gère `is_wp_error` au niveau du dispatch des exporters privacy).
- **Effacement** (`effacer()` l.492-496) : le `catch` pose `items_retained=true` **et**
  `done=false` + message de reprise. Avant, seul `items_retained` était posé.
- **Principe prudent respecté** : dans le doute, incomplet, jamais complet.
- **Test ajouté** : `b06-runtime.php` injecte une panne du `SELECT` via `add_filter('query', ...)`
  avec événement présent et vérifie `sql_export_jamais_complet`,
  `sql_effacement_incomplet_retient`, `sql_evenement_non_perdu`, puis la reprise complète
  (`sql_export_reprise_complete`) ; un second scénario fait échouer le `SELECT` de relecture
  finale après 50 événements sur 51 (`sql_relecture_finale_incomplete`,
  `sql_relecture_evenement_restant`, `sql_effacement_reprise_complete`).

### Instruction 3 — Couvrir B-06 par une preuve rejouable hors recette live — **Appliquée**
- Nouveau `wp/plugins/imagine-site/tests/CooperateursReglesTest.php`, dans le dossier `tests`
  **découvert par le `phpunit.xml` existant** (`<directory suffix="Test.php">tests</directory>`)
  → entre dans la suite T01 rejouée par `rejouer.ps1`, sans WordPress ni base ni HTTP.
- Couvre `administration()` et `lecture()` : défaut, capacité ≠ rôle, 8×8 configurations
  indépendantes des deux droits, non connecté, `source`/`date_utc` bien/mal formée,
  `cooperateur=false`, type invalide.
- Reçu : `PRET` et `fusion-livraison-rules-V2.json` indiquent « 3 tests, 981 assertions ».

### Instruction 4 — Affichage cohérent du statut — **Appliquée**
- `fiche()` `Cooperateurs.php:209` : condition passée à
  `is_array($state) && ($state['cooperateur'] ?? null) === true`.
- `compte()` `Cooperateurs.php:514` : même condition sur `$s`.
- Un décochage (`cooperateur=false`) n'affiche plus « Source : administration — <date> ».
- **Test** : `b06-runtime.php` (`compte_retrait_sans_source_date`,
  `fiche_retrait_sans_source_date`) avec mutation `display` qui doit rougir.

### Instruction 5 — Test rejouable de la collection REST — **Appliquée**
- `b06-space.php:43` : mutation `collection` ajoutée (retire `requete`/`protegerObjets`).
- `b06-space.php:67-77` : contrôle `/wp/v2/pages` pour un non-coopérateur :
  page publique témoin présente (`_collection_publique_presente`) et page réservée + enfant
  exclus (`_collection_exclut_espace`), avec la mutation
  `fusion-livraison-mutation-collection-V2` dont l'échec requis est
  `anonyme_collection_exclut_espace` (reçu présent).
- Conforme au défaut « masquer le texte ET exclure la page » : rien changé au code
  (`requete()` protégeait déjà), seule la preuve manquait.

---

## 2. Résultat des tests

- **Rejeu indépendant non réalisé par le vérificateur.** `rejouer.ps1` (suite T01 autorisée)
  s'appuie sur Docker/WSL ; son lancement est bloqué en session non-interactive par la
  demande d'approbation du sous-processus (`docker`/`wsl`). Je ne peux pas l'accorder ici.
  **C'est la même limite structurelle qu'au 1er tour** : le relecteur ne peut pas jouer la
  recette HTTP live, déjà consignée dans la fusion (§1).
- **Vérifications faites à la place :**
  - Empreintes SHA-256 des fichiers B-06 sur disque **identiques** au manifeste livré
    `FICHIERS-fusion-V2.json` (`Cooperateurs.php` = 432d7e80…, `CooperateursRegles.php`
    = 7783568a…, `CooperateursReglesTest.php` = 3ef7185e…). Les reçus décrivent donc bien le
    code présent.
  - Reçus livrés : `fusion-livraison-V2.json` → **916 contrôles B06 verts, 0 échec, 13
    mutations détectées** ; `verification-fusion-finale-V2.json` → `result=VERIFIED`,
    régression **1126 tests / 35 550 assertions**, 311 contrôles d'outils, P-COOP conservé,
    réglages par défaut Administrateur relus.
  - Lecture du diff et du code corrigé : les 13 mutations couvrent chacun des points des
    instructions 2, 4, 5 (collection, display, SQL export/effacement) ; les 8×8 configurations
    de l'instruction 1 sont dans `b06-settings.php`.
- **Conclusion tests** : reçus cohérents, verts, et correspondant au code sur disque ; mais
  **non rejoués indépendamment par le vérificateur** (limite d'environnement, pas un échec).

---

## 3. Régressions ou modifications non demandées

- **Aucune régression constatée dans le périmètre B-06.** Le diff des fichiers B-06
  (`Cooperateurs.php`, `CooperateursRegles.php`, les tests, `README-B06.md`) correspond
  strictement aux cinq instructions. Les signatures publiques restent compatibles
  (`exporter()` élargi en `array|\WP_Error`, paramètre `$autorises` optionnel à défaut
  `['administrator']` → comportement antérieur préservé si non réglé).
- **Hors périmètre B-06, dans le même diff** (à signaler, non bloquant) :
  `wp/plugins/imagine-site/imagine-site.php` enregistre désormais des classes
  `Personnalisation*` (`PersonnalisationRegles`, `Personnalisation`, `PersonnalisationReglages`,
  `PersonnalisationConfidentialite`), et de nombreux fichiers `c23-*`/`c24-*` changent. Ces
  éléments **ne font pas partie de `corrections/B-06.md`** : ils relèvent d'autres lots
  (C-23, C-24/Personnalisation) embarqués par les commits de synchronisation. Ils n'altèrent
  pas B-06 (ajouts après `Cooperateurs::register()`), mais Ced doit savoir que le commit de
  livraison B-06 n'est pas isolé — le travail d'autres lots y est mêlé.
- **Point visuel inchangé, comme prévu** : la date reste affichée en UTC brut dans un `<time>`
  sans `datetime`. C'était explicitement laissé « À arbitrer par Ced (visuel) » dans la fusion ;
  ce n'est pas une régression.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions de la fusion sont **appliquées** et accompagnées de leurs tests ; aucun
problème de fond ne subsiste ; aucune régression B-06. Les seuls éléments ouverts sont déjà
routés : la présentation de la date (visuel, défaut UTC conservé) et les deux questions métier
pour Imagine (défauts Administrateur appliqués et testés) — ni l'un ni l'autre ne bloque la
clôture du code.

**Deux réserves portées à Ced, non bloquantes :**
1. Le vérificateur n'a **pas pu rejouer** la suite T01 lui-même (Docker/WSL sous approbation en
   session non-interactive). La preuve de vert repose sur les reçus livrés, dont les empreintes
   correspondent au code sur disque. Un `rejouer.ps1` lancé par Ced lèverait cette réserve.
2. Le commit de livraison **mêle d'autres lots** (C-23, C-24/Personnalisation) ; la validation
   de B-06 ne vaut que pour les fichiers B-06 ci-dessus.

**Rappel doctrine : ce verdict n'est pas un GO.** Il ne vaut que pour la clôture du code B-06 ;
il n'autorise ni mise en ligne ni bascule.
