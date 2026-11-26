# Relecture A-25 — Ce que le site garde sur ses visiteurs (Claude, indépendant)

**En tête, comme demandé par le brief :** l'import inchangé peut laisser passer **en clair les messages de formulaires** (tables de messages non vidées par la neutralisation). C'est une information pour l'import, pas une correction à faire dans ce lot. Démontré par le banc `wp/tests/a25/neutralise.php` sur les deux magasins.

Date : 2026-11-26. Je n'ai pas ouvert `codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée, sans argument)

Commande exacte lancée :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, réseau coupé, dépôt monté en lecture seule (`mount=/mnt/c/.../wp:/repo/wp:ro ; network=none ; cap-drop=ALL ; no-new-privileges`). Dernière ligne :

```
REJEU : 1126 tests, 35550 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Outil A-25 dans la matrice : `T01 TOOL : a25 ; 15 controls ; 0 failures ; exit=0`. Les 16 outils et 311 contrôles passent, hors rejeu aucun.

> Remarque : `rejouer.ps1` rejoue le côté PHP. La suite Python de bout en bout (`matrix.py`, `verify.py`, 21 tests cp1252/UTF-8) est la preuve d'Hermès, exécutée hors de cette commande ; je ne l'ai pas rejouée, l'instruction de relecture limitant l'exécution à `rejouer.ps1` sans argument.

## 1. Conformité

- **Périmètre respecté.** Le lot ne supprime rien, n'anonymise rien, ne fixe aucune durée. Sortie en lecture seule, nombres par année et état/extension uniquement. Conforme §4.4 et au brief.
- **Lecture seule confinée et gardien A-22.** `confine.py` réutilise `stream_guard.py` (A-22), `a12/confine.py`, `a11/Runtime.php`/`ReadOnlyDb.php` sans les modifier (absents de `git status` → inchangés ; `Inventory.php` boote via `PublicAddresses\Runtime`, transaction READ ONLY, SELECT only, Landlock). Aucune duplication d'implémentation. Conforme à la doctrine « standard d'abord » et au brief (« par le gardien des sorties d'A-22 »).
- **Commentaires** (`Inventory.php:44-54`) : tous types sauf `order_note`, objets natifs `WP_Comment`, date GMT, présence email/IP/rattachement comptées séparément de leur valeur. Conforme.
- **Commandes sans compte** (`Inventory.php:56-68`) : SQL énumère les IDs `shop_order` (classique `posts`, HPOS `wc_orders`), sémantique par getters natifs `WC_Order`, `get_customer_id('edit') === 0`, année UTC. Magasin autoritaire via `OrderUtil`, pas de double compte. Conforme ; interprétation « sans compte ≠ navigateur non connecté à l'achat » signalée dans le README et dans SOURCES.
- **Liste fermée de formulaires** (`Inventory.php:10, 82-106`) : une seule extension, **Fluent Forms** (`fluentform_submissions`, `created_at`), choix justifié par schéma éditeur documenté. Table hors liste → `autre`, nom jamais publié. Liste vide = résultat explicite. Conforme au brief (liste écrite dans le code, « dis laquelle et pourquoi », « autre » sans nom, absence = résultat).
- **Fuite nulle de données** : états natifs d'une liste fermée (`Analysis::STATES`), noms d'extensions d'une liste fermée, aucun texte/adresse/IP/identifiant. `report.py::projection` valide strictement le schéma avant publication (deux fichiers exactement). Codes de refus fermés (`refusals.json` + liste figée de drop-ins), aucun chemin/nom tiré du site ; toute exception hors liste devient `A25_CONFINEMENT_FAILED`. `display_errors=0`, `log_errors=0`, stderr exigé vide. Conforme à la règle de la voie 1.
- **Neutralisation** (`Analysis.php:43-47`) : `email`/`ip` → `inconnu après neutralisation` (jamais zéro) dès la marque d'import ; `forms` → `inconnu` prudemment. `all`/`account`/`guests` restent lisibles. Conforme au brief (« là où il fausse un nombre, inconnu après neutralisation, jamais zéro »).
- **Garde d'audit** : `Command.php:41-57` et `confine.py:51-54` lient la photo A-02, vérifient l'emplacement de l'audit sous le parent, et refusent si `storage` du relevé ≠ `order_storage` de la photo. Bon garde-fou.

## 2. Exactitude métier — déroulé à la main

Banc de preuve (`wp/tests/a25/seed.php`), confronté au code et à `unit.php` :

- **3 commentaires / 2 années** : 2023 (état `1`, email+IP, sans compte), 2024 (état `0`, sans adresse, avec compte), 2024 (état `spam`, email+IP, sans compte).
  - `all` = 2023:1 + 2024:2 → 3 commentaires. Chaque cellule < 5 → `autres: 3`. ✓
  - `email` présent = commentaires 1 et 3 → **2**. ✓ (brief : email 2)
  - `ip` présent = commentaires 1 et 3 → **2**. ✓ (brief : IP 2)
  - `account` (`user_id > 0`) = commentaire 2 → **1**. ✓ (brief : lié 1)
- **Commandes sans compte** : 2023 + 2024, client 0 → **2**, fondues en `autres: 2`. ✓
- **Formulaires** : Fluent Forms 2 entrées (2023, 2024, dont une au texte canari), table inconnue 2 entrées → pool total **4** en `autres` ; `listed_extensions: ['Fluent Forms']`, `other_tables: 1`. ✓
- **Repli < 5 « comme A-20 »** : vérifié contre `wp/outils/bascule/a20/Analysis.php:93,109` — même seuil `< 5` fondu dans un seau « autres », par métrique. Cohérent. ✓ Les étiquettes année/état des petites cellules ne sortent pas.
- **Cas limites couverts par `unit.php`** : variante native à cinq (année/état visibles), état natif inconnu replié en `autre` sans texte libre (canari absent de `json_encode`), `forms` vide = `autres: 0` **seulement sans marque d'import**, frontière année (date GMT), date indisponible → année 0.
- **Neutralisation (banc `neutralise.php`)** : email fictif passe 2 → 3, IP passe 2 → 0 ; l'outil répond donc `inconnu après neutralisation` pour email et IP, et par prudence pour `forms`. `all`/`account`/`guests` inchangés. ✓

Résultats conformes au cahier des charges et au brief sur tous les cas déroulés.

## 3. Tests

- Suite PHP au vert (REJEU ci-dessus, a25 = 15 contrôles, 0 échec).
- `unit.php` vérifie la **règle** (comptes exacts, repli, inconnu-jamais-zéro, canari absent, états fermés), pas seulement le cas nominal : cinq-visible, état inconnu replié, vide-sans-marque. `report.py::projection` est testé par mutations (`verification-mutations.json` : canal omis, dépendance altérée, texte ajouté, reçu mixte → refusés).
- Couverture classique + HPOS annoncée et visible dans la matrice.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : fixtures `@example.org`, noms `A25_*_CANARY` manifestement inventés, MariaDB fictive.
- SQL en SELECT, transaction READ ONLY, Landlock, mail/HTTP/cron refusés, Action Scheduler court-circuité avant bootstrap (`Inventory.php:29-34`).
- Étanchéité : le texte des commentaires/messages (`comment_content`, `response`, `message`) n'est jamais sélectionné ni projeté ; seuls présence et comptes sortent. Projection stricte + états fermés garantissent structurellement l'absence de canari dans les sorties.
- Sorties privées `0700`/`0600`, jamais réécrites, refus si le dossier existe ou est un lien.

## 5. Doctrine

- « Standard d'abord » respecté : objets natifs WP/Woo, pas de réimplémentation ; `OrderUtil` pour le magasin autoritaire.
- Conventions §5 : `declare(strict_types=1)`, espace de noms `Imagine\VisitorRetention`, PSR-12 (0 erreur annoncé et vérifié par la matrice), README présent.

## 6. Études (sources)

- SOURCES.md cite les pages officielles (WP_Comment, WC_Order, Fluent Forms database) et signale honnêtement la page CRUD WooCommerce absente, non employée comme preuve.

## Verdict

**Conforme** — ce verdict n'est pas un GO (doctrine §6).

Points classés :

- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur 1** (`Inventory.php:112`, `report.py:40`) : `clear_messages_after_import` est une constante `true`, imposée aussi par la projection. L'outil ne mesure pas ce drapeau sur la copie inspectée (il ne rejoue pas l'import) : c'est un avertissement éditorial permanent, validé une fois par le banc. Correction proposée : le documenter comme avertissement fixe (déjà fait dans le README/rapport) pour que Ced ne le lise pas comme une mesure propre à la copie ; pas de changement de code requis.
- **Mineur 2** (SOURCES.md) : la grille §6 demande, pour chaque affirmation sur une extension, l'adresse **et la phrase exacte** de la doc. SOURCES donne les adresses mais pas la citation littérale du schéma Fluent Forms. Correction proposée : ajouter la phrase citée de `developers.fluentforms.com/database/` justifiant `fluentform_submissions`/`created_at`.
- **Mineur 3** (interprétation à garder visible) : « commande sans compte » = `customer_id == 0`, et non l'état authentifié du navigateur au moment de l'achat ; années en UTC pour commentaires (date GMT stockée) et commandes (`getTimestamp` → `gmdate`). Déjà signalé par Hermès dans le README et SOURCES ; rien à corriger, je le confirme comme interprétation assumée et tracée.

### Décisions techniques, défaut proposé

- Drapeau `clear_messages_after_import` (Mineur 1) : **défaut proposé** — garder la constante `true` comme avertissement permanent, l'étiqueter explicitement « avertissement éditorial, non mesuré sur la copie » dans la sortie. Hermès applique ; j'arbitre après coup à la fusion.

### Pour Imagine

- Aucune règle métier à trancher dans ce lot (durée de conservation et nettoyage sont explicitement hors périmètre : question Imagine / plan A-05, déjà renvoyée).

### À arbitrer par Ced (visuel / réel)

- Aucune question visuelle ni touchant au réel. Le lot ne touche ni au site, ni à une base réelle, ni à un compte.

**En attente de `codex.md` pour la fusion** : `relectures/A-25/codex.md` existe mais n'a pas été ouvert, conformément à la consigne. Fusion non faite.
