# Relecture C-15 — Écran des échéances (Claude, relecteur indépendant)

Brief : `briefs/C-15-ecran-des-echeances.md`. Cahier : §3.13 (`docs/cahier-des-charges-v3.1.txt`, l.916-932).
Production relue : `wp/plugins/imagine-site/EcheancesRegles.php`, `EcheancesNatives.php`, `EcheancesAdmin.php` ; `wp/outils/demo/c09-seed.php` ; tests `wp/tests/demo/c15-*` ; `production/C-15/`.
Codex non lu. Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée, sans argument)

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, sans réseau, dépôt en lecture seule. Dernière ligne :

```
REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Image : `T01 IMAGE : sha256:16a9940acfa193138620b6c083f64552a80c53afd3ab9fa97e1894faea298e6d`.
Bibliothèques couvertes : imagine-connecteur (5), imagine-non-regression (6), imagine-pilotage (27), imagine-site (3 fichiers `*Test.php` : Achat, Envoi, Pdf).

## 1. Conformité

- **Cinq vues, un seul menu.** `EcheancesAdmin::menu` ajoute `Imagine → Échéances` au parent existant et déduplique l'entrée parente préexistante C10/C13 (l.44-55). Les cinq clés de vue sont présentes : `echeances`, `attente`, `virements`, `mandats`, `echecs` (l.183-185). Conforme.
- **Lecture de l'état natif, pas de registre parallèle.** `EcheancesNatives` ne lit que `wc_get_orders` / `wcs_get_subscriptions` et les méta natives ; aucun stockage de paiement. Conforme (brief « L'écran lit l'état natif »).
- **Action unique d'écriture.** Seul `recevoir()` écrit, via `WC_Order::payment_complete()` natif (EcheancesAdmin.php:132) + note datée UTC avec nom/login/ID de l'opérateur (l.136-138). Confirmation obligatoire (case à cocher, l.114), nonce lié à la commande (l.108), capacité dédiée (l.103). Pas de masse, pas de remboursement. Conforme.
- **Aucune règle nouvelle.** Aucun délai « virement en retard » : `attente`/`echecs` sans limite d'ancienneté ; les droits d'accès restent C06/C10. Explicitement signalé (A-VOIR.md l.33, RAPPORT.md l.11). Conforme au brief (« si l'écran a besoin d'une règle… c'est un réglage C10 ; tu le signales » — ici aucune règle nécessaire, c'est dit).
- **Aucun IBAN.** Référence = `A-PAPIER` fictif en démo, sinon méta `imagine_mandat_reference` (EcheancesNatives.php:93) ; le test CSV rejette explicitement un champ `iban` (c15-unit.php:53-55). Conforme.
- **Export aux précautions de la liste d'envoi.** Droit + nonce lié à la période (EcheancesAdmin.php:162), `php://output` (aucun fichier déposé), en-têtes `private, no-store` + `nosniff` + `attachment` (l.168-172), neutralisation des formules (EcheancesRegles.php:33-36). Conforme.
- **Aucun email / appel sortant.** Garde `pre_wp_mail`/`pre_http_request`/`woocommerce_defer_transactional_emails` posée le temps de la requête (EcheancesAdmin.php:125-129, retirée en `finally`). Conforme au brief.

**Interprétations faites — signalées, à confirmer :**

- a) **Vue `attente` restreinte aux commandes liées à une souscription du même propriétaire** (EcheancesNatives.php:74-78). Une commande à l'unité (numéro, don) réglée par virement et en attente n'apparaît donc pas. Signalée dans A-VOIR.md l.19. Le cahier dit « paiements en attente » sans restriction ; à confirmer côté métier.
- b) **Colonne `Devise` ajoutée au CSV** (EcheancesRegles.php:30) : l'export a 5 colonnes alors que le cahier en liste 4 (abonné, montant, référence, échéance ; §3.13 l.929-930). Ajout utile (montant sans devise ambigu) mais c'est un « plus » non demandé.
- c) **Vue `echeances` inclut les souscriptions `pending` et `on-hold`** (EcheancesRegles.php:69), pas seulement `active`/`pending-cancel`. Une souscription jamais activée peut remonter. Interprétation extensive, non signalée explicitement.

## 2. Exactitude métier — cas déroulés à la main

Référence `now = 2026-11-25 12:00:00 UTC`. Jeux de `c15-unit.php`.

- **Échéances 30 j** (cahier §3.13 « arrivent à échéance », brief vue 1). Lignes : id1 active prochaine=+29 j/fin=+30 j ; id2 pending-cancel fin=+90 j ; id3 expired ; id4 cancelled ; id5 active prochaine=+181 j ; id6 on-hold prochaine=now. Déroulé : id3/id4 hors statuts ⇒ exclus ; id5 au-delà de 30 j ⇒ exclu ; id2 à +90 j ⇒ exclu ; restent id6 (now) et id1 (+29 j), triés par (échéance, id) ⇒ **[6, 1]**. Code `EcheancesRegles::echeances` : identique. À 90 j, id2 entre (borne `<=` incluse) ⇒ [6,1,2] ; à 180 j, id5 à +181 j reste exclu (seuil strict `+180 j`) ⇒ [6,1,2]. Conforme et borne correcte.
- **Virements à valider** (brief vue 3, « A-VIR seulement »). Parmi les commandes non payées en `pending`/`on-hold`, seules celles de méthode `bacs` : sur le jeu, seul id10 ⇒ **[10]**. `pending` sans méthode (id17) et `stripe` (id11) exclus. `EcheancesRegles::paiements($rows,'virements')` : identique. Conforme.
- **Mandats** (brief vue 4). Filtre `active` + `imagine_papier` + référence non vide + prochaine ≤ seuil + (`fin==0` ou `fin>now` et `prochaine<fin`). Sur le jeu papier ⇒ **[1]** ; une ligne `bacs` ⇒ `[]` ; un mandat dont la date native est déjà passée (`prochaine=now-1`) reste listé (id20). Conforme à A-VOIR.md l.20/33.

**Cas limites vérifiés :**

- Dates égales à la borne : `prochaine == now` est inclus dans `echeances` (`>= $now`), `echeance == now+days*86400` inclus (`<=`). Cohérent.
- `payé` / `date_payée` : `paiements` exclut toute commande payée ou datée payée (EcheancesRegles.php:49) ⇒ pas de double validation ; une 2ᵉ validation d'A-VIR est refusée côté action car `virement()` relève la commande désormais payée et lève (EcheancesNatives.php:48-49 ⇒ 409). Conforme au brief (« une seconde validation est refusée »).
- Formules tableur : `=`, `+`, `-`, `@`, y compris précédés d'espaces/contrôles, préfixés `'` (EcheancesRegles.php:35) ; `fputcsv(..., '')` désactive l'échappement antislash au profit du guillemet RFC 4180. Correct.
- **Cas limite non couvert (mineur)** : un mandat papier réel dont `imagine_mandat_reference` est vide est silencieusement exclu de la liste et de l'export (EcheancesRegles.php:17 `reference !== ''`). Il faudrait au moins le voir signalé « référence manquante » plutôt que disparaître.

## 3. Tests

- **La suite autorisée passe** (ligne REJEU ci-dessus), mais **elle n'exerce aucune règle C-15**. `imagine-site` n'expose que 3 `*Test.php` (Achat, Envoi, Pdf) ; `EcheancesRegles` n'a pas de test PHPUnit dans le paquet. Les tests C-15 vivent dans `wp/tests/demo/` (`c15-unit.php` pur, `c15-runtime.php`, `c15-http.py`, `c15-action.py`) et sont lancés par un harnais Python séparé — la plupart exigent le site de démonstration vivant (`http://192.168.129.32:8085`) et le réseau. Le README le reconnaît (README.md l.165 : « les tests C15 autonomes… ne sont pas annoncés comme découverts par T01 »).
- **Conséquence** : un relecteur qui rejoue la seule commande sandbox autorisée obtient « vert » sans toucher une ligne de C-15. Les règles pures (`EcheancesRegles`) sont testables sans WordPress ni base — elles **devraient** être un `*Test.php` du paquet `imagine-site`, donc dans le rejeu réseau-less (doctrine §4 « Rejouable », « Les tests d'abord »). Point **important**.
- **Qualité des tests purs** (`c15-unit.php`) : bonne. Ils vérifient la règle (tri, bornes, neutralisation de formules, absence d'IBAN) et non une répétition du code ; j'ai redéroulé leurs attendus à la main (§2) sans écart.
- **Tests HTTP** (`c15-http.py`) : bonne couverture sécurité déclarée — paywall (page refusée E-REDAC/A-CARTE), export refusé sans droit, nonce absent/invalide/tableau, anonyme, `GET`→405, nonce lié à la période, `no-store`, sans IBAN, formules neutralisées. **Je n'ai pas pu les rejouer** : ils exigent un site vivant et le réseau, hors de la commande autorisée. Je m'appuie donc sur `production/C-15/*.json` et le RAPPORT pour leur résultat, sans l'avoir reproduit indépendamment.

## 4. Sécurité et données

- **Droits** : `autorise()` = `manage_options` ou `imagine_gerer_echeances` (EcheancesAdmin.php:20-23). Cette capacité est une capacité **C09 existante**, accordée au rôle « Référent abonnements » dans `c09-seed.php:88`, pas un nouveau droit global — conforme au brief (« celui de la liste d'envoi ou un voisin »). `recevoir()` et `exporter()` appellent `verifier()` avant toute lecture/écriture. Les handlers `admin_post_nopriv_*` retombent proprement sur un 403 via `verifier()`.
- **Nonces** : vérifiés pour l'action (`RECU:id`) et l'export (`EXPORT:days`) ; `wp_verify_nonce` ne remplace pas le contrôle de capacité (ordre correct). Confirmation en deux temps, chaque POST portant un nonce.
- **Échappement** : `esc_html`/`esc_attr`/`esc_url` systématiques dans `page()` ; aucune sortie non échappée repérée.
- **Export** : pas de fichier sur le disque public, en-têtes de cache privés, type forcé, pas de sniff.
- **Données** : jeux fictifs, noms inventés ; aucune donnée réelle ni secret dans le dépôt. La reconnaissance « fictive » A-VIR/A-PAPIER est verrouillée par cinq conditions cumulées (environnement `local`, option `imagine_demo_site`, `home_url` exact, méta `imagine_demo_fictif`, propriété dans `imagine_c09_fixture`) — EcheancesNatives.php:14-24 — et ne rend aucun autre profil payable. Hors démo, méthode vide = inconnue. Correct.
- **Paywall / étanchéité** : la page admin est protégée par capacité ; pas de fuite de texte réservé dans ce lot (écran back-office). Rien à signaler.

## 5. Doctrine

- **Standard d'abord** : paiement via `WC_Order::payment_complete()` natif, lecture via API Woo/WCS, pas de requête SQL maison ni de table parallèle. Conforme.
- **Logique métier hors WordPress** : `EcheancesRegles` est du PHP pur sans dépendance WP, `EcheancesNatives` est la couche fine de branchement. Bonne séparation (doctrine §4).
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\`, préfixe `imagine_` (caps, options), UI française via `__()`, aucune modification d'extension tierce (hooks/filtres uniquement). `README.md` documente le lot (l.151, 160-165). Conforme.
- **Réserve** : seule entorse à « Rejouable / Tests d'abord » = le point §3 (pas de test C-15 dans le rejeu sandbox).

## Verdict

**À corriger.** Le lot est fidèle au brief et au §3.13, bien séparé, sûr. Aucun point bloquant. Un point important (couverture de test non rejouable) et des mineurs.

- **Bloquant** : aucun.
- **Important**
  1. Les règles pures C-15 (`EcheancesRegles`) ne sont pas couvertes par la commande de rejeu autorisée (réseau-less). Ajouter un `tests/EcheancesReglesTest.php` au paquet `imagine-site` reprenant les cas de `c15-unit.php`, pour qu'un rejeu sandbox exerce C-15. Les tests HTTP peuvent rester hors sandbox, mais le pur doit entrer dans T01.
- **Mineur**
  2. CSV : colonne `Devise` au-delà des 4 champs du cahier (EcheancesRegles.php:30). Écart « en plus » à assumer ou retirer.
  3. `attente` restreinte aux commandes liées à une souscription (EcheancesNatives.php:74-78) : périmètre plus étroit que « paiements en attente » du cahier.
  4. `echeances` inclut `pending`/`on-hold` (EcheancesRegles.php:69) : inclusion extensive non signalée.
  5. Mandat papier réel sans `imagine_mandat_reference` : exclusion silencieuse de la liste/export (EcheancesRegles.php:17) au lieu d'un signalement.

**Ce verdict n'est pas un GO** : validation visuelle de Ced et seconde relecture (Codex) + fusion restent dues ; aucune preuve de transaction réelle.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

- **Point 1 (test rejouable)** — défaut : ajouter `imagine-site/tests/EcheancesReglesTest.php` (portage direct de `c15-unit.php`) sans toucher au harnais HTTP. À appliquer sans attendre.
- **Point 2 (colonne Devise)** — défaut prudent : **conserver** `Montant`+`Devise` (un montant sans devise est ambigu), mais le mentionner comme écart assumé au §3.13 dans le RAPPORT. Arbitrage a posteriori.
- **Point 4 (statuts `echeances`)** — défaut : conserver `pending`/`on-hold` mais l'énoncer dans A-VOIR comme choix explicite.
- **Point 5 (référence manquante)** — défaut : lister quand même la souscription papier avec une mention « référence manquante » en clair, plutôt que l'omettre.

## Pour Imagine (réglage / question métier)

- **Point 3** — « Paiements en attente » doit-il inclure les commandes **à l'unité** (numéro, don, pack) réglées par virement et non encore reçues, ou se limiter aux paiements liés à un abonnement ? Défaut prudent proposé : se limiter aux paiements liés à une souscription (comportement actuel, cohérent avec la démo), jusqu'à réponse.

## Pour Ced (visuel / réel)

- Rien à trancher sur le réel dans ce lot (démo entièrement fictive, hors ligne, aucun GO réclamé). La validation **visuelle** de l'écran `Imagine → Échéances` et de ses cinq vues reste à faire sur captures, selon le système de design.
