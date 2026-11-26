# Relecture A-18 — Claude (indépendant)

Lot : A-18 « Ce que le site garde et ne devrait pas garder ».
Brief : `briefs/A-18-donnees-a-ne-pas-garder.md`. Cahier des charges : §4.4 (« Aucune donnée de paiement stockée sur le site »).
Production relue : `wp/outils/bascule/a18/`, `wp/tests/a18/`, `production/A-18/`.
Je n'ai pas ouvert `relectures/A-18/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP autorisée

Commande lancée depuis la racine, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

`REJEU : 1111 tests, 34499 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Conteneur T01 jetable, réseau `none`, dépôt monté en lecture seule, nettoyé en fin de course (`T01 CLEANUP : absence verifiee`). Exit 0.

**Portée réelle de ce rejeu.** `rejouer.ps1` joue les suites PHPUnit des quatre extensions (connecteur, non-régression, pilotage, site). Le code A-18 vit dans `wp/outils/bascule/a18/` : ce n'est pas une extension T01, donc **ses propres assertions ne sont pas exercées par cette commande**. Les preuves propres au lot (unit 10, natif 84, gardes runner 7, lanceur Python 3) proviennent du banc natif Docker (`wp/tests/a18/run.py` + `inside.py`), qui exige l'image de staging et des extensions sous licence. Je ne l'ai **pas** rejoué : il sort de la seule commande autorisée et §3 m'interdit staging et réseau. Je me suis donc appuyé sur le paquet livré (lecture) et sur un déroulé à la main.

## 1. Conformité

- **Base, formes par clé et portée** (`Inventory::database`, `Inventory::groups`) : métas comptes, commandes, abonnements du magasin faisant autorité (classique **ou** HPOS) et options ; comptage par forme (IBAN / carte / registre belge), groupé par portée + clé technique. La sortie ne rend que clé + nombres (`conservation.json` vu). Conforme au point 1 du brief.
- **Jetons à part** (`Inventory::collect`) : `woocommerce_payment_tokens` groupés par passerelle et type, sans valeur ni `last4`. Le README dit « ce sont des références, pas des numéros ». Conforme.
- **Fichiers** (`Inventory::media`) : sous-dossiers de premier niveau non-année ; nom sorti s'il est dans la liste fermée (`exports, logs, backups, wc-logs, woocommerce_uploads, ai1wm-backups, wpallimport, gravity_forms, wpcf7_uploads, formidable, wpforms`), sinon fusionné sous `autre` ; extensions sur liste fermée sinon `autre` ; poids total ; aucun nom de fichier, aucun chemin profond. Taille lue par `getSize()` (stat), aucun fichier ouvert — confirmé par la garde inotify du banc. Conforme.
- **Marque de neutralisation** : présence de `imagine_staging_disabled_plugins` → `database.status = "inconnu après neutralisation"`, groupes `null` (jamais un zéro rassurant, leçon A-17). Conforme à l'alinéa du brief.
- **Règle de la voie 1 (aucun chemin/nom tiré du site en sortie, erreurs comprises)** : clés hors syntaxe masquées en `autre` (`Inventory::technical`) ; refus réduits à une liste **littérale** fermée de codes (`inventorier-conservation`), une exception d'extension contenant un canari est ramenée à `A18_INVENTORY_FAILED`. Conforme.

**Interprétation signalée par Hermès et que je retiens** : le brief demande « un oui ou non : un fichier de règles du serveur en interdit-il la lecture ». Le code **ne rend pas** ce oui/non. Il rend `server_rule_file_present` (présence d'un `.htaccess`/`web.config`) et `reading_denied = null` (inconnu). C'est un écart déclaré, voir §2 et le point important ci-dessous. Aucune autre interprétation n'a été faite en silence.

## 2. Exactitude métier (déroulé à la main)

Déroulé contre le code puis vérifié sur `production/A-18/preuves/final/classic-retention/conservation.json`.

- **IBAN.** `BE68539007547034` (exemple belge canonique) : structure `3!n7!n2!n`, modulo 97 = 1 → compté. `BE69539007547034` : clé fausse → **non compté**. `BE68ABCD07547034` : BBAN non numérique → rejeté par la structure. Conforme.
- **Commande à deux IBAN** (`_a18_bank` = valide + invalide) : la sortie donne `order:_a18_bank iban=1`. **L'invalide n'est pas compté** — exigence centrale de la preuve, vérifiée.
- **Carte.** `4242 4242 4242 4242` : 16 chiffres, Luhn OK → compté (`account:_a18_card card=1`). `4242424242424243` : Luhn faux → rejeté. `0000000000000000` : suite d'un seul chiffre exclue (sinon somme de Luhn = 0 passerait). `42424242` : trop court (<13) → rejeté. Conforme.
- **Registre belge.** `85.07.30-033.28` et `00.01.01-001.05` : clé 97 sur les 9 premiers, ou sur ces 9 préfixés de `2` (deux siècles) → comptés. `85073003329` : clé fausse → rejeté. Forme et clé seulement, pas de date civile (documenté). Conforme.
- **Option sérialisée** `a18_bank_setting` (IBAN valide + canari) : `option:a18_bank_setting iban=1`, le canari n'apparaît pas. Octets lus, aucun objet désérialisé. `a18_invalid_setting` (IBAN invalide) **absent** des groupes. Conforme.
- **Médias.** `exports` : `a.csv`(3)+`b.csv`(4)+`c.log`(5) = 12 octets, `csv:2, log:1`. `autre` : un dossier vide + un dossier inconnu (1 `.txt` de 4 octets) → `directories:2, txt:1, bytes:4` (le dossier vide fusionne dans `autre`). `2026` exclu (année). `woocommerce_uploads` : `html:1, regles:1`, `server_rule_file_present:true` (présence `.htaccess`). Tous conformes à la sortie livrée.

Cas limites couverts par le banc et relus : variante neutralisée (inconnu, pas zéro), variante règle (présence vraie mais `reading_denied` reste `null`, fichiers inchangés), rejeu identique (`replay_identical`), empreintes de toutes les tables et fichiers inchangées avant/après (y compris Action Scheduler).

## 3. Tests

- **Suite PHP autorisée** : verte (ligne REJEU ci-dessus), mais **hors périmètre A-18** (voir plus haut). Elle prouve seulement l'absence de régression ailleurs dans le dépôt.
- **Paquet de preuves livré** (`production/A-18/verification.json`, lu, non rejoué par moi) : `exit_code 0`, 33 contrôles PASS, comptes `unit 10 / result 84 / runner 7` en cp1252 **et** utf8. Un seul paquet (`preuves/final`), exigence « un seul paquet » respectée.
- **Qualité des tests** (lecture de `unit.php`, `inside.py`, `test_launcher.py`) : ils vérifient la règle, pas le code. Cas adverses solides — invalide non compté, canari absent de toute sortie, refus symlink fichier **et** dossier (code seul), six drop-ins fermés, PHP non confiné refusé, inotify = aucun `IN_OPEN`/`IN_ACCESS`, lanceur refusant un argument inconnu `--inconnu=été-漢` sans amorcer PHP. Couverture bien au-delà du cas nominal.
- **Réserve** : ces assertions ne sont vertes que dans le paquet fourni par Hermès ; je n'ai pas pu les régénérer indépendamment faute de Docker/staging autorisés. Vérification seconde (Codex ou Ced) utile sur ce point.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle** : fixtures `@example.org`, noms `A18_..._CANARY` manifestement inventés, carte de test `4242…`. Conforme §3 doctrine.
- **Lecture seule** : SQL `SELECT` paginé par clé (`WHERE id>%d … LIMIT 500`), `$wpdb->prepare` avec `%d`, noms de tables issus de `$wpdb->prefix`. Jamais de désérialisation d'objet. Confinement : `A18_CONFINED=1` exigé, `mail`/`exec` doivent être absents, sinon `A18_CONFINEMENT_REQUIRED`.
- **Sortie** : neuve, sœur du rapport A-02, hors site et dépôt (`disjointOutput`), refus si existe ou lien ; répertoire `0700`, fichiers `0600`, écriture en `x` (exclusif). Racine uploads bornée sous le site (`A18_UPLOAD_ROOT_UNSAFE`).
- **Aucune fuite de chemin/nom** : codes de refus sur liste littérale fermée ; noms de drop-ins issus de la liste fermée du Runtime A-11, pas découverts sur le site ; canari d'extension écrasé en `A18_INVENTORY_FAILED`. Testé.
- Pas de problématique paywall ici (outil d'audit hors ligne). N/A.

## 5. Doctrine

- **Standard d'abord** : README cite la doc officielle WooCommerce Payment Token API et explique pourquoi le sur-mesure est nécessaire (pas d'inventaire transversal de formes côté standard). `production/A-18/sources-officielles.json` porte provenance et empreinte des structures IBAN (python-stdnum, registre SWIFT v101, 89 pays). Conforme §4.
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\…`, PSR-12 (contrôle de style vert dans le paquet), textes FR, `README.md` présent pour l'outil. Codes d'erreur préfixés `A18_`. Conforme.
- **Rejouable / idempotent** : transformation nulle (lecture seule), rejeu identique prouvé. Conforme.

## Points classés

**Important (arbitrage technique — défaut proposé, à trancher par Claude en fusion)**

1. `wp/outils/bascule/a18/Inventory.php:102` et `:160` — le oui/non demandé par le brief (« un fichier de règles du serveur en interdit-il la lecture ») n'est **pas** rendu. Le brief est contradictoire sur ce point : il interdit d'ouvrir tout fichier et de faire la moindre requête, tout en exigeant la preuve d'une interdiction effective — indémontrable par les seules métadonnées de fichiers. Défaut prudent retenu par Hermès : `server_rule_file_present` (présence du nom technique) + `reading_denied = null` (inconnu), documenté dans le README et au banc. **Je valide ce défaut** : toute autre option (lire le `.htaccess`, tester en HTTP) violerait la règle de non-ouverture et le §3. À acter en écart (`docs/ecarts.md`, contradiction interne au brief §A-18 vs §4.4). Non bloquant.

**Mineur**

2. `wp/outils/bascule/a18/Forms.php:15` et `:64` — `iban-structures.json` est relu par `file_get_contents` à **chaque** appel de `scan()` et de `iban()`, soit une lecture disque par ligne de métadonnée (et par candidat IBAN). Correct mais coûteux sur de grandes tables. Proposition : charger la table une fois (constante statique mémoïsée).
3. `wp/outils/bascule/a18/Inventory.php:134` — le discriminant de neutralisation est la seule présence de l'option `imagine_staging_disabled_plugins`. C'est un proxy de « les formes ont été vidées par l'import ». Il privilégie l'« inconnu » (prudent). Risque résiduel : une copie vérifiée **non** neutralisée mais portant par ailleurs ce marqueur rendrait « inconnu » à tort ; inversement une copie anonymisée sans ce marqueur rendrait un zéro trompeur. À confirmer : ce marqueur est posé exactement quand les formes de paiement sont neutralisées.
4. `wp/outils/bascule/a18/Forms.php:75-79` — une même valeur qui passe à la fois Luhn (carte) et la clé registre belge est comptée dans les deux colonnes. Conforme au brief (comptage par forme, indépendant), mais peut gonfler les totaux sur des nombres ambigus de 11 chiffres. À mentionner dans le mode d'emploi, sans correction.

## Verdict

**Conforme**, sous réserve des points ci-dessus.

- Aucun **bloquant**.
- Un **important** : l'écart assumé sur le oui/non des règles serveur (défaut prudent validé, à acter en écart).
- Quatre **mineurs** (dont les n°2 à 4 ci-dessus ; le point sur la portée réelle du rejeu autorisé est le quatrième).

Ce verdict **n'est pas un GO** (§6 doctrine). Deux réserves de vérification restent ouvertes : (a) le banc natif A-18 (10/84/7/3) n'a pas été rejoué par moi — à confirmer par une seconde relecture ; (b) le rejeu autorisé (`rejouer.ps1`) ne couvre pas la logique A-18 elle-même. Fusion non faite, en attente de l'étape prévue.
