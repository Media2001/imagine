# Relecture C-10 — L'écran de réglages (relecteur Claude indépendant)

Date : 2026-11-23. Lot : `briefs/C-10-ecran-de-reglages.md`.
Production relue : `wp/plugins/imagine-pilotage/` (façade `src/Administration/Reglages.php`, bootstrap `imagine-reglages.php`) et `production/C-10/`.
Codex non lu (consigne). Fusion non faite (consigne).

## 0. Ce que j'ai pu exécuter

- La suite PHPUnit du lot (`docker compose run --rm -w /app/imagine-pilotage php composer test`) **n'a pas pu être relancée ici** : le binaire `docker` est absent du PATH de l'environnement de relecture et l'appel reste non approuvé en session non interactive. Je le signale au titre du rôle de vérificateur.
- Peu importe ce blocage : la suite PHPUnit **ne couvre pas** C-10 (voir §3). `phpunit.xml` déclare six suites (Numeros, Robots, Entreprise, Acces, Envoi, Echeancier) ; aucune `Administration`, et `tests/Administration/` n'existe pas.
- Les preuves du runner (`local-tests.json`, `verification-finale.json`) montrent 4 tests Python de périmètre au vert, 13 contrôles runtime, 79 contrôles HTTP, 30 contrôles de non-régression C08. Ces tests tournent contre le site de démonstration `192.168.129.32:8085` ; je ne les rejoue pas (accès à un site, hors de mes droits). Je m'appuie donc sur une lecture manuelle du code et le déroulé à la main des cas du cahier des charges.

## 1. Conformité

**Conforme sur l'essentiel.** Un menu natif `Imagine › Réglages`, trois sections (Accès, Paiement en quatre fois, Liste d'envoi), huit réglages, un seul formulaire Settings API vers `options.php`. Réutilisation des trois adaptateurs existants sans toucher aux moteurs ni aux bibliothèques closes (`src/Administration/Reglages.php:7-10`, `:36-39`). Les défauts correspondent aux arbitrages du 22/11 (`docs/arbitrages-2026-11-22.md`) : accès fermé, PDF robot en extrait, PDF antérieur fermé, marge vide, rejet « restent dues », tarif figé, premier SEPA avec marge.

Points conformes à souligner :
- Refus strict des clés et choix inconnus **avant** délégation à l'adaptateur Accès (`Reglages.php:68-84`). C'est ce wrapper qui garantit l'exigence du brief « une valeur inconnue ne devient pas silencieusement un défaut » : seul, `Acces\Reglages::depuisOptions()` recoercit en défaut silencieusement (`src/Acces/Reglages.php:16-26`). Bonne interprétation, à conserver.
- Domaines indépendants : chaque option a son propre `sanitize_callback` ; un domaine invalide conserve sa valeur, les autres domaines valides passent (`Reglages.php:53-65`, `:99-104`). Conforme au brief.
- Réservé aux administrateurs : groupe sous `manage_options` via `option_page_capability_imagine_reglages` (`Reglages.php:23`) et re-vérification de capacité à l'affichage (`:189-191`). L'écran ne rebranche pas les anciens menus C05/C06/C07.

**Interprétations non bloquantes, à acter :**

1. **Effet « sur le site » (brief, Livrables).** Le brief demande, pour **un** réglage, la manipulation qui montre « son effet sur le site », avec pour exemple l'accès → recharger un article. Le lot démontre à la place le réglage **Liste d'envoi** via un aperçu CSV produit par le vrai exporteur C07 (`Reglages.php:229-232`, `apercuCsv()` `:254-261`). C'est un vrai moteur, pas une imitation : acceptable comme preuve d'effet sur le consommateur C07. Mais c'est un aperçu **dans la page d'admin**, pas un effet en front, et les notes reconnaissent que les réglages Accès/Paiement **n'ont aucun consommateur branché** (C08 ignore encore l'option C06 — `production/C-10/notes.md:45`). Donc hors Liste d'envoi, aucun réglage ne change le comportement du site. C'est défendable sous « les bibliothèques closes ne changent pas », mais s'écarte de l'exemple du brief. → voir arbitrage en fin de rapport.

2. **« À confirmer par Imagine » affiché sur les huit réglages, sans condition** (`Reglages.php:223`). Le brief dit « quand la règle est encore ouverte ». Vérification faite dans `docs/decisions.md` et `docs/arbitrages-2026-11-22.md` : les huit règles sont effectivement encore ouvertes chez Imagine (grille tarifaire, SEPA, rejet, tarif, découverte, colonnes provisoires). La mention est donc légitime partout aujourd'hui. Mineur : la mention est codée en dur dans la boucle d'affichage, pas pilotée par un état « ouverte/tranchée » ; le jour où Imagine tranche un réglage, il faudra éditer le code pour retirer la mention.

## 2. Exactitude métier (déroulé à la main)

Cas déroulés à la main sur le code :

- **Marge SEPA vide (défaut).** `marge_jours = null` rendu en champ vide (`Reglages.php:37`, `:219`). `Echeancier\Reglages::premierSepaPayeLe()` lève `MARGE_OBLIGATOIRE` tant que la marge n'est pas renseignée (`src/Echeancier/Reglages.php:75-77`). Conforme à l'arbitrage « le moteur refuse de planifier, aucun défaut inventé ». ✓
- **Colonne dupliquée (`ville` deux fois).** `FormatExport` rejette doublon et colonne inconnue (`src/Envoi/FormatExport.php:16-22`) ; `AdministrationFormatExport::nettoyer()` rattrape l'exception, pose un message clair et renvoie la liste précédente (`src/Envoi/AdministrationFormatExport.php:97-115`). Conforme (cas du A-VOIR point 6). ✓
- **Accès, clé surnuméraire ou valeur hors liste.** `clesExactes()` + `in_array(..., true)` refusent, `refuser()` conserve l'ancienne valeur et pose le message (`Reglages.php:68-104`). ✓
- **Réenregistrement identique.** `journaliser()` sort si `before === after` (`:116`) ; `update_option` WordPress ne déclenche pas non plus `updated_option` sur une non-modification. Pas de faux événement au journal. ✓ (cas A-VOIR point 5).

**Cas limite non couvert — à vérifier (important).** Première sauvegarde du domaine **Paiement** avec une valeur de type invalide (clés exactes mais, p. ex., `marge_jours = "abc"`). Chemin : `nettoyerPaiement()` délègue à `Paiement::sanitiser()` qui, sur exception, renvoie `get_option(self::OPTION, [])` (`src/Echeancier/ReglagesAdministration.php:46-57`). Si l'option n'a **jamais** été enregistrée, cela renvoie `[]`, qui est alors persisté comme valeur du domaine. Conséquence : `page()` lit le Paiement par `get_option()` **brut** (`Reglages.php:193`), pas par `->lire()`, et afficherait des sélecteurs vides au lieu des défauts prudents. Les consommateurs restent saufs (ils passent par `depuisOption([])` qui recompose les défauts), donc l'impact est un affichage, pas une ouverture de droit. À dérouler côté HTTP : le runner affirme avoir testé la conservation « après réglage non standard » (donc après une valeur déjà posée), pas forcément la toute première sauvegarde invalide.

## 3. Tests

**Point bloquant.** La nouvelle logique de la façade C-10 (`Administration\Reglages` : `clesExactes()`, `nettoyerAcces()`, `nettoyerPaiement()`, `refuser()`, `journaliser()`, `ajouterAuJournal()`, `journal()`, `apercuCsv()`) **n'a aucun test PHPUnit**. `tests/Administration/` n'existe pas ; `phpunit.xml` ne déclare pas la suite ; aucun test du dépôt ne référence `Imagine\Pilotage\Administration\Reglages`. Les quatre fichiers qui contiennent « Administration » testent les **adaptateurs** C-05/06/07, pas la façade.

- Or le brief liste comme livrable n°1 : « Le code et ses tests (droits, nonce, valeurs invalides, journal) ». Ces quatre comportements ne sont vérifiés que par les tests Python HTTP contre le site de démo — hors de `composer test`, non rejouables en relecture, et dépendants d'un site vivant.
- Doctrine §4 : « Les tests d'abord… La logique métier hors de WordPress… testables sans base ni WordPress. » La validation stricte (`clesExactes`, `refuser`) et la dé-duplication du journal sont du PHP pur testable avec le `WordPressFictif` déjà présent (`tests/Acces/WordPressFictif.php`), comme les adaptateurs le font déjà.
- Doctrine §6 : la clôture d'un lot de code par Claude repose sur « tests au vert ». La suite `composer test` ne teste rien de C-10.

Correction proposée : ajouter `tests/Administration/ReglagesTest.php` (et la suite dans `phpunit.xml`) couvrant au minimum : clés exactes acceptées/refusées pour Accès et Paiement ; valeur hors liste refusée avec conservation de l'ancienne ; journal écrit une fois par option modifiée après persistance, rien sur refus ni sur no-op ; `apercuCsv()` reflète le format relu. Les tests de droits/nonce HTTP peuvent rester en recette de démonstration, mais ne remplacent pas la couverture unitaire de la logique.

Le RED initial (`red-runtime.json`) est un RED d'écran (« ecran_present=false ») : il prouve l'ordre test→implémentation sur la présence de l'écran, pas sur les règles de validation.

## 4. Sécurité et données

- **Droits/nonce** : groupe sous `manage_options` (`Reglages.php:23`), page re-vérifie la capacité et `wp_die` 403 sinon (`:189-191`), nonce par la Settings API (`settings_fields` `:199`). Les preuves HTTP (refus rédacteur/gestionnaire WooCommerce/abonné/anonyme, nonce absent/faux/autre session → 403 sans écriture) sont cohérentes avec ce code. ✓
- **Échappement** : `esc_html`/`esc_attr`/`esc_textarea`/`selected()` partout, y compris le journal (`:243-247`, valeurs `wp_json_encode` puis `esc_html`). ✓
- **Requêtes préparées** : `journal()` utilise `$wpdb->prepare()` + `esc_like()` (`:131-135`). ✓
- **Paywall / données réelles** : l'écran n'expose aucun contenu réservé ; l'aperçu CSV n'apparaît que sur `local` + `imagine-test-demo` (`:229`) et utilise une ligne fictive (`:257-259`). `secret_scan` du runner à zéro. ✓
- **Pas de REST** : `show_in_rest => false` sur les trois options (`:57`). ✓

Rien de bloquant côté sécurité.

## 5. Doctrine

- **Standard d'abord** : Settings API native, composants d'admin natifs, aucun gestionnaire POST maison. Conforme au « sobre » du brief. ✓
- **Hooks seulement sur le tiers** : aucune modification des moteurs ; la façade n'appelle que lecture/validation des adaptateurs. ✓
- **Journal, une option par événement, non autoloadée** (`Reglages.php:121`, `:125`). Choix défendable contre la perte d'un append concurrent, mais la table `options` croît sans borne (pas de purge) et l'affichage est plafonné à 50 (`:133`). Mineur, assumé dans `notes.md:64` ; à confirmer qu'aucune purge n'est attendue.
- **Duplication de défaut (mineur)** : le défaut Paiement est recodé en dur dans `Reglages.php:37-38` alors que l'Accès et l'Envoi dérivent leur défaut de l'adaptateur (`:36`, `:39`). Risque de dérive si le défaut C-05 change. Proposer d'exposer un accesseur de défaut côté `ReglagesAdministration` et de le réutiliser.
- **Incohérence de lecture (mineur)** : `page()` lit Accès et Envoi via `->lire()` (robuste, try/catch → défauts) mais Paiement via `get_option()` brut (`:192-194`). Uniformiser sur `->lire()` corrigerait aussi le cas limite du §2.
- **Convention §5** : PHP 8.2, `declare(strict_types=1)`, namespace `Imagine\`, préfixe `imagine_`, textes passés par `__()`. ✓ README présent (`src/Administration/README.md`).

## Verdict

**À corriger.**

**Bloquant**
1. Absence de tests automatisés (`composer test`/PHPUnit) pour la façade `Administration\Reglages` : droits, nonce, valeurs invalides et journal ne sont couverts que par des tests HTTP hors suite et non rejouables. Contraire au livrable n°1 du brief et à la doctrine §4/§6. (§3)

**Important**
2. Cas limite Paiement : première sauvegarde avec valeur invalide → persistance d'un `[]` et affichage de sélecteurs vides, car `Paiement::sanitiser()` renvoie `get_option(..., [])` et `page()` lit le brut au lieu de `->lire()`. À dérouler et corriger. (§2, §5)
3. Effet « sur le site » : seul le réglage Liste d'envoi a un effet (aperçu admin via le vrai exporteur C07) ; Accès et Paiement n'ont aucun consommateur branché. Conforme à « bibliothèques closes inchangées », mais s'écarte de l'exemple du brief. (§1.1)

**Mineur**
4. Mention « À confirmer par Imagine » codée en dur sur les huit champs, non pilotée par un état ouverte/tranchée (`:223`). Aujourd'hui exacte.
5. Défaut Paiement dupliqué (`:37-38`) et lecture non uniforme dans `page()` (`:192-194`).
6. Journal sans purge, croissance non bornée de `options` ; affichage plafonné à 50 (assumé).

## À arbitrer par Ced (questions fermées)

- A. L'aperçu CSV admin produit par le vrai exporteur C07 suffit-il comme « effet d'un réglage sur le site », ou exiges-tu qu'au moins un réglage soit branché à un consommateur en front avant clôture de C-10  ? (oui/non)
- B. Acceptes-tu que le journal des modifications conserve tous les événements sans purge, l'écran n'en affichant que 50 ? (oui/non)

Verdict non valant pas GO : validation visuelle de l'écran par Ced toujours attendue (`PRET`/`notes.md`).
