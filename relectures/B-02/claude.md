# Relecture B-02 — « Mon compte » (squelette) — Claude

Relecteur indépendant. Je signale, je cite, je propose ; je ne réécris pas le code.
Je n'ai pas lu `relectures/B-02/codex.md`. Pas de fusion à ce stade.

Périmètre lu : brief `briefs/B-02-mon-compte.md`, cahier §3.7/§3.8/§3.9/§3.10, `wp/plugins/imagine-site/{MonCompte.php,EnvoiNatif.php,imagine-site.php}`, `wp/themes/imagine/parts/mon-compte.php`, dossier `production/B-02/`.

## Rejeu de la suite PHP

Commande jouée, sans argument :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

(conteneur jetable, sans réseau, dépôt en lecture seule). Dernière ligne :

```
REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Portée réelle de ce rejeu (bannières `T01 COVERAGE`) : `imagine-connecteur` (5), `imagine-non-regression` (6), `imagine-pilotage` (27), `imagine-site` (3 : `AchatNumeroTest`, `EnvoiReglesTest`, `PdfNumeroTest`). **Aucun test de ce lot (`MonCompte`, gabarit) n'est dans cette suite rejouable.** Voir §3.

Non rejoué par moi : les « 144/144 » du rapport (75 PHP natives + 54 HTTP + gardes). Ce sont des recettes HTTP contre le staging vivant (`wp/tests/demo/b02-*`, `wp/outils/demo/b02.py`), avec cookies et objets HPOS réels. Elles exigent un accès au site, interdit à mon rôle (droits §Exécution ; conteneur `--network none`). Je reprends les chiffres d'Hermès **comme déclarés, non vérifiés par moi**.

## 1. Conformité

- Les cinq rubriques du brief sont présentes (`mon-compte.php` l.12-14, 17-65) : Mon abonnement, Mes échéances, Mes numéros, Mes coordonnées, Mes factures et justificatifs. Navigation interne et réutilisation du My Account natif. Conforme sur la forme.
- Données non branchables rendues en emplacement nommé, pas en donnée inventée (ex. l.26 numéros restants, l.44 date d'échéance, l.63 factures vides). Conforme à la doctrine §3/§4 (« pas de donnée inventée »).
- **Écart brief / cahier, à tracer.** Le brief renvoie à « §3.10 », qui est en réalité « Newsletters et segmentation ». Le contenu « Mon compte » vit en §3.7 (Compte client), §3.8 (impayés, délai de grâce) et §3.9 (droits d'accès). Hermès l'a vu (`sources.md` l.12, `rapport.md` l.34). De même l'étiquette `a-4x-j45` du brief est une erreur, renommée `A-SEPA4`. Ces deux écarts doivent aller dans `docs/ecarts.md` avec la date (doctrine §7) — je ne peux pas y écrire à ce stade, je le signale.
- Interprétations faites et **non signalées** dans le rapport (grille 1.3) : (a) `on-hold` + adhésion `pending/delayed` ⇒ « Virement en attente de validation » (`MonCompte.php` l.61-63) ; (b) `cancelled` ⇒ « Expiré » (l.48), ce qui fond « résilié » dans « expiré ». Les deux sont défendables mais auraient dû être écrites (« j'ai compris X »).

## 2. Exactitude métier (déroulé à la main)

Logique d'état : `MonCompte::etat()` (l.44-72). Déroulé sur les profils de `A-VOIR.md` :

- **a-carte** (actif, pas de fin) : l.48 faux → l.51 `active` → **« Actif »**. Conforme.
- **a-susp** (on-hold, grâce finie à J-1) : l.57 `on-hold` → pas d'adhésion en attente → fenêtre de grâce `from<=now<until` fausse (fin passée) → l.71 **« Suspendu »**. Conforme à §3.8 (« au terme du délai, l'accès est suspendu »).
- **a-grace** (on-hold, grâce active jusqu'à J-1) : même chemin, fenêtre vraie → l.68 **« En délai de grâce »**. Conforme.
- **virement** (status `pending`) : l.54 → **« Virement en attente de validation »**. Conforme à §3.13 (« virements à valider »).

Cas limite échéances (§3.8, paiement en quatre fois) — `echeances()` (l.75-102) :

- Détection 4× = `billing_period === 'month'` et `billing_interval === 3` (l.136). Interprétation : un abonnement trimestriel = quatre positions sur l'année. Acceptable pour un squelette, lié à C-05.
- **Défaut réel** : seule la position 1 reçoit une commande (`wc_get_order($sub->get_parent_id())`, l.87) ; les positions 2-4 sont forcées à « État de paiement non raccordé » (l.91). Or les commandes de renouvellement **sont déjà récupérées** plus bas pour le bandeau d'échec (`get_related_orders(...,'renewal')`, l.142). Donc un règlement réel (ex. 2ᵉ échéance `processing`/payée d'`A-SEPA4`) s'affiche « non raccordé » alors qu'il **est** branchable. Cela contredit « ce qui n'est pas branchable apparaît comme emplacement nommé » : ici c'est branchable mais rendu comme un trou. Le rapport présente cela comme une limite de fixture (`A-VOIR` l.10) ; c'est en partie un choix de code.

## 3. Tests

- La suite rejouable passe (1012 tests), mais **ne couvre pas la logique propre de B-02** : `etat()`, `echeances()`, l'isolation par identité de session. Seules les recettes HTTP contre le staging l'exercent, et elles ne sont pas rejouables hors ligne ni par mon rôle.
- Contradiction avec la doctrine §4 : « la logique métier hors de WordPress… testable sans base ni WordPress », « un lot sans tests n'est pas PRET ». Le cœur de B-02 — surtout le mapping des états et le contrôle d'isolation — pouvait être isolé derrière une couche fine et couvert par PHPUnit avec un double de `WC_Subscription`. Ce n'est pas fait. **Important.**
- Conséquence : la preuve d'isolation (exigence centrale du brief) ne repose que sur des assertions HTTP que je ne peux rejouer. Je confirme par **lecture** que la conception est saine (identité = `get_current_user_id()` seul, l.107 ; re-contrôle `get_customer_id()===user` l.113 ; filtre d'édition d'adresse l.34-35 ; garde du gabarit l.5), mais je ne peux pas l'**exécuter** dans mon périmètre.

## 4. Sécurité et données

- Isolation : aucun identifiant de GET/POST n'entre dans le choix de l'identité (l.104-115). Re-contrôle du titulaire sur la commande d'échéance (l.88) et filtre d'édition d'adresse par propriétaire (l.34-35). En-têtes `private, no-store` sur les pages de compte (l.27-32). Conception correcte.
- Échappement : toutes les sorties du gabarit passent par `esc_html`/`esc_attr`/`esc_url`, et `wp_kses_post` pour `wc_price` et l'adresse formatée. Pas de formulaire ni de nonce maison : on réutilise les routes et nonces Woo/WCS. Rien à redire.
- **Robustesse / fatale possible — important.** `etat()` l.58 appelle `wc_memberships_get_user_memberships(...)` **sans `function_exists`**. Le runtime relevé par le rapport (l.11) liste WooCommerce et Subscriptions mais **pas Memberships**. Tout abonnement `on-hold` (a-susp, a-grace) traverse cette branche ; si Memberships est absent ou désactivé, c'est une erreur fatale sur la page de compte. À garder derrière `function_exists`.
- Données : aucun secret, aucun email réel, aucun cookie/nonce dans `production/B-02/` (vérifié). Les identifiants vivent hors dépôt (`A-VOIR` l.5). Conforme §3.

## 5. Doctrine

- Standard d'abord : réutilisation du My Account, des adresses et nonces natifs, documentation citée (`sources.md`). Bon.
- **Raccord postal redondant — mineur.** `EnvoiNatif::register()` (l.120-124) relève sur **chaque** sauvegarde de souscription (`woocommerce_after_subscription_object_save`), ajouté à 14:43. `MonCompte::register()` (l.21-26) accroche **la même action** avec une garde « formulaire client » ajoutée plus tôt (13:43/13:53). Le second est donc devenu **mort/redondant** : sa garde ne restreint plus rien. En conséquence, l'affirmation du rapport (l.36) « raccord limité au formulaire client » **n'est plus exacte** : on relève désormais à toute sauvegarde de souscription. La déduplication de `enregistrer()` évite le doublon de données, mais la garde trompeuse et le hook mort devraient être retirés (ou, si l'intention était bien de restreindre, c'est le hook d'`EnvoiNatif` qu'il faut revoir).
- Conventions §5 : `declare(strict_types=1)`, espace `Imagine\`, préfixe `imagine_` sur les options/métas, textes en français via i18n. Conforme.

## 6. Études

Sans objet (lot de code).

## Verdict

**À corriger.** Le squelette est conforme au brief et proprement isolé par conception ; la suite rejouable est au vert. Mais deux points importants (garde Memberships manquante, logique propre de B-02 non couverte par la suite rejouable) et un défaut d'exactitude (échéances 2-4 non raccordées alors que branchables) doivent être traités.

- **Bloquant** : aucun.
- **Important** :
  1. `MonCompte.php` l.58 — `wc_memberships_get_user_memberships` sans `function_exists` : fatale possible sur toute page de compte d'un abonné `on-hold` si Memberships est absent du runtime.
  2. Tests — le cœur de B-02 (`etat()`, `echeances()`, isolation) n'a aucun test dans la suite rejouable ; il n'est prouvé que par des recettes HTTP contre le staging, non rejouables hors ligne. Contredit doctrine §4.
  3. `MonCompte.php` l.85-100 vs l.142 — les commandes de renouvellement, déjà chargées, ne servent pas à raccorder les positions 2-4 ; une échéance réellement payée apparaît « non raccordé ».
- **Mineur** :
  4. Hook mort/redondant `MonCompte.php` l.21-26 face à `EnvoiNatif.php` l.120-124 ; le rapport l.36 décrit un périmètre de raccord qui n'est plus celui du code.
  5. Interprétations non signalées : `on-hold`+adhésion⇒« virement » (l.61-63), `cancelled`⇒« Expiré » (l.48).
  6. Bandeau de régularisation affiché pour « Suspendu/grâce » (gabarit l.33), plus large que « si une échéance a échoué » du brief ; le texte distingue, acceptable.

Ce verdict n'est pas un GO.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

1. **Garde Memberships.** Défaut : encadrer l'appel par `function_exists('wc_memberships_get_user_memberships')`, et renvoyer « Suspendu » quand la fonction est absente. Catégorie : technique.
2. **Couverture de test.** Défaut : extraire le mapping d'état et la détection 4× dans une unité PHP pure (couche fine sur `WC_Subscription`) et ajouter un `*Test.php` sous `imagine-site/tests`, pris par le rejeu T01. Catégorie : technique.
3. **Échéances 2-4.** Défaut prudent : ne rien inventer, mais raccorder l'état « Payée/Échouée » d'une position quand une commande de renouvellement non ambiguë lui correspond par date ; sinon rester « non raccordé ». Catégorie : technique.
4. **Hook redondant.** Défaut : supprimer le hook `MonCompte.php` l.21-26 et mettre le rapport à jour, ou documenter pourquoi `EnvoiNatif` relève sans garde. Catégorie : technique.

## Pour Imagine (réglages métier)

- **« Virement en attente » pour un `on-hold` avec adhésion en attente** : est-ce le libellé voulu, ou faut-il réserver « virement en attente » au seul statut `pending` ? Défaut prudent proposé : réserver « Virement en attente de validation » au statut `pending`, et laisser `on-hold` en « Suspendu / En délai de grâce ».

## À arbitrer par Ced (visuel / réel)

- Aucune question visuelle nouvelle de ma part : le besoin designer (`besoins-designer.md`) couvre les cinq rubriques, les cinq états et les emplacements non raccordés. La validation visuelle et la recette HTTP contre le staging restent de ton ressort (hors de mon périmètre d'exécution).
