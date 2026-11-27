# Relecture C-28 — Packs thématiques d'anciens numéros (Claude, indépendant)

Relecteur : Claude. Brief : `briefs/C-28-packs-thematiques.md`. Cahier : §3.3, §3.1.
Production lue : `wp/plugins/imagine-site/{PacksRegles.php, PacksThematiques.php}`, raccord `AchatsNumeros.php`, `AchatNumero.php`, `Paywall.php`, `MonCompte.php`, `single-product.php`, README (§C-28), `production/C-28/{A-VOIR.md, NOTE.md}`.
`codex.md` non ouvert. Pas de fusion à ce stade.

## 0. Vérification exécutée

- Suite PHP rejouée, commande autorisée sans argument : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` (conteneur jetable, réseau coupé, dépôt en lecture seule).
- Dernière ligne du rejeu :

  `REJEU : 1189 tests, 36512 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

- Ce que je **n'ai pas** pu rejouer : la recette navigateur et les bancs natifs de démo (`c28-recette.py`, `c28.py runtime/regressions`, `c28-verifier.py --live`). Ils mutent un site vivant et sortent du réseau ; la doctrine me l'interdit. Les cas de bout en bout ci-dessous sont donc déroulés **à la main sur le code**, pas rejoués.

## 1. Conformité

- **Standard d'abord présent.** `README` lignes 526-532 : cinq lignes, produit groupé natif (non achetable, prix des enfants) et Product Bundles (extension payante, non activée), choix = produit simple + liste + prix global. Deux URL de documentation officielle citées. Conforme à la demande du brief.
- **Pack = produit rattaché à une liste éditoriale.** `PacksThematiques::champ()` (l.78-96) et `enregistrer()` (l.98-123) : sélection multiple dans les données générales du produit simple, IDs stricts/dédoublonnés/publiés (`PacksRegles::numeros`), refus sans écraser l'ancienne liste. Conforme.
- **Page de pack.** `single-product.php` l.22-41 : titre, pour chaque numéro couverture/titre/date (métadonnées publiques B04), bouton/panier natifs, prix étiqueté « Prix fictif : ». Pas de corps d'article ni PDF embarqué. Conforme au brief et au squelette B01.
- **Même décision d'accès, aucune règle nouvelle.** C'est le cœur du lot et il est correct : `AchatsNumeros::droits()` l.139 applique le filtre `imagine_achat_instantanes` qui, pour une ligne de pack, remplace l'instantané unique par la liste figée (`PacksThematiques::instantanes` l.69-76), puis chaque numéro repasse **inchangé** par `AchatNumero::droit()` (l.142-155). Aucune table de droits, aucun type de droit, aucun accès anonyme ajoutés. Conforme à « par la même décision d'accès ».
- **Mon compte.** Rien n'a été ajouté dans `MonCompte.php` et c'est volontairement correct : `donnees()` l.119-125 liste les numéros dont `Paywall::decisionPdf()['complet']` est vrai, et cette décision consulte `AchatsNumeros::droits()` (via `Paywall::rights()` l.190). Les numéros d'un pack apparaissent donc dans la même rubrique que les achats à l'unité, sans code dédié. Conforme.
- **Remboursement = réglage C-14 tel quel.** Aucun réglage parallèle (`AchatsNumeros::reglages` inchangé). La ligne de pack suit la portée `imagine_achat_remboursement`. Conforme.
- **Interprétation signalée à confirmer (mineur).** Le cahier §3.3 l.393 dit « vendus comme **produits groupés** ». L'implémentation retient un **produit simple**, pas `WC_Product_Grouped`. Le choix est argumenté dans le README (le groupé natif n'a pas de prix global et n'est pas achetable). Interprétation la plus proche du texte, correctement signalée (doctrine §1). À confirmer par Imagine : « un pack = un produit simple à prix unique, et non le produit groupé natif — d'accord ? » Défaut proposé : conserver le produit simple (déjà implémenté).
- **Règle de composition passée bien appliquée, sans réglage.** `docs/decisions.md` l.93 tranche C-28 : « les numéros que le pack contenait au moment du paiement, ni plus ni moins ; pas de réglage ». `NOTE.md` et le code appliquent exactement cela (gel au paiement, pas de réglage nouveau). Conforme — aucune question à poser à Ced sur ce point.

## 2. Exactitude métier — cas déroulés à la main

Déroulé sur le code (lignes citées), en suivant un acheteur `V` sur un pack `[11,18,25]`.

1. **Avant paiement, rien n'est ouvert.** Commande en attente → statut ni `processing` ni `completed` → non interrogée par `droits()` (l.102). Même si elle l'était, `LIGNE` (`_imagine_pack_paye`) n'est écrit qu'au paiement (`payer()` l.47-48), donc `instantanes()` renvoie `[]` et aucun droit. ✔
2. **Après paiement, trois numéros ouverts pour le seul acheteur.** `payer()` fige `numeros`=`[11,18,25]` relus **sur le produit** (l.58, pas l'objet panier). `droits()` étend la ligne en trois instantanés ; `AchatNumero::droit()` exige `client` == propriétaire (l.21). Anonyme : `rights=[]`. ✔
3. **Quatrième numéro ajouté au pack après coup → ne s'ouvre pas.** `instantanes()` lit l'instantané figé `LIGNE`, jamais le produit vivant. Ajouter `32` à `imagine_pack_numeros` ne modifie pas `[11,18,25]`. ✔ C'est le point sensible du lot et il est correct.
4. **Numéro retiré du pack après coup → reste ouvert.** Même mécanisme : l'instantané figé garde `11`. `droit()` ne referme que si le numéro lui-même est dépublié (comportement C-14 identique à un achat seul). ✔
5. **Remboursement.** Mode `commande` : tout remboursement ferme toute la commande. Mode `ligne` : rembourser la ligne pack (`_refunded_item_id` = id de la ligne) ferme ses numéros ; un partiel non ventilé n'en ferme aucun ; un remboursement complet ferme dans les deux modes. Logique entièrement portée par C-14 (`AchatNumero::remboursement` l.13-16, `droits()` l.122-149), rien de propre au pack. ✔
6. **Liste devenue vide figée (cas limite).** Si à l'instant du paiement un numéro inclus est dépublié, `numeros()` renvoie `[]`, `payer()` fige `numeros`=`[]`, et aucun rétro-octroi n'est possible si le pack est réparé ensuite. Comportement prudent et cohérent. ✔
7. **Numéro déjà possédé.** Aucune remise, le pack se vend quand même (aucune logique de remise). Conforme au brief ; le doublon de droit est inoffensif.

Conclusion métier : les six règles du brief et les cas de preuve sont satisfaits **dans le code lu**. L'immutabilité repose sur « geler au paiement + ne relire que l'instantané », ce qui est le bon motif.

## 3. Tests

- **Suite scellée au vert** (voir §0) : `REJEU … PASS`. Image reconstruite sortie 0.
- **Couverture — point important.** La seule couverture C-28 dans la suite rejouable est `tests/PacksC28Test.php` : **2 tests sur `PacksRegles` uniquement** (règles pures). La couche WooCommerce `PacksThematiques` — c'est-à-dire **le gel au paiement, la garde d'écriture unique, le marquage candidat et le filtre d'expansion** — n'a **aucun test dans la suite scellée** (`phpunit.xml` ne découvre que `tests/*Test.php`, et `c28-horslive.php` ne fait que relancer le filtre `PacksC28`). Ces comportements ne sont prouvés que par la recette de démo (`c28-recette.py`, `runtime`), qui n'est pas rejouable hors-ligne et que je n'ai pas pu exécuter. Une régression dans `PacksThematiques::payer()` (par ex. relire le produit vivant au lieu de l'instantané) **ne serait pas attrapée** par `rejouer.ps1`.
  - Correction proposée : ajouter à la suite scellée une couverture de la couche de branchement, sur le modèle des bancs natifs à rollback déjà utilisés ailleurs (ou des doubles légers pour `candidat`/`payer`/`instantanes`), afin que le gel et la non-reprise soient garantis par le rejeu, pas seulement par la démo.
- Les tests pures existants vérifient bien la règle (ordre strict, dédoublonnage, enveloppe payée rejetant des données malformées) et ne répètent pas le code. Bon.

## 4. Sécurité et données

- **Étanchéité paywall.** `single-product.php` n'émet aucun corps réservé : titres, vignettes, date de sortie, prix ; liens vers les permaliens des numéros. Aucune voie de fuite ajoutée ; `Paywall` inchangé. Déroulé manuel cohérent avec les 32 témoins C26 revendiqués dans `NOTE.md` (non rejoués par moi). ✔
- **Échappement.** `champ()` : `esc_html__`, `esc_attr`, `selected(...,false)`. `single-product.php` : `esc_url`, `esc_html`, `esc_attr`, `wp_kses_post` sur le prix. Rien de brut. ✔
- **Droits/nonce.** `enregistrer()` l.100-104 : s'appuie sur le nonce natif Woo (`woocommerce_admin_process_product_object`) + `current_user_can('edit_post')` + garde `imagine_pack_present`. Même motif que C-14. Lecture `$_POST` via `wp_unslash` puis validation stricte `PacksRegles::numeros`. ✔
- **Données fictives.** `A-VOIR.md` déclare le site, le produit 3592, le prix 3.28 € et les numéros comme fictifs ; aucune commande payée ni droit C09 laissés. Aucun secret dans le dépôt. ✔

## 5. Doctrine

- **Standard d'abord** respecté (§1 ci-dessus) ; aucune extension commerciale activée.
- **Logique pure hors WordPress** : `PacksRegles` (pur, testé) + couche fine `PacksThematiques`. Conforme à la doctrine §4 — sous la réserve de couverture du §3.
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\Site`, préfixe `imagine_`/`_imagine_` sur métadonnées et produit, textes passés par les fonctions de traduction. ✔ Aucune modification d'extension tierce (hooks/filtres uniquement).
- **Mineur (robustesse).** Métas `imagine_pack_numeros` (pack) et `imagine_achat_numero_id` (C-14) sont exclusives quand les deux champs sont soumis ensemble (le champ pack délète le mapping C-14, l.119). Par une sauvegarde programmatique ne soumettant qu'un seul champ, un produit pourrait porter les deux métas. Risque faible (le panneau natif soumet toujours les deux via le champ caché `imagine_pack_present`). Correction proposée : lors de l'enregistrement C-14, délier aussi le pack si un numéro unique valide est posé, par symétrie.
- **Mineur.** `single-product.php` décide pack/non-pack par `meta_exists(PRODUIT)` (l.11) mais l'affichage par `numeros()` qui renvoie `[]` si **un** numéro inclus est dépublié → le pack entier devient non achetable (« Pack indisponible »). Défaut sûr, mais à confirmer côté Imagine : faut-il vendre le reste du pack si un numéro est dépublié ? Défaut proposé : rester strict (ne pas vendre un pack incomplet).

## Verdict

**À corriger.** Un verdict de relecture n'est jamais un GO.

- **Bloquant** : aucun.
- **Important** :
  1. §3 — la couche WooCommerce du pack (gel au paiement, non-reprise, filtre d'expansion) n'est couverte par **aucun test de la suite scellée rejouable** ; sa preuve repose uniquement sur la recette de démo non rejouable hors-ligne. Ajouter une couverture rejouable.
- **Mineur** :
  1. §1 — interprétation « produits groupés » (§3.3) rendue par un produit simple : signalée, défendable, à confirmer par Imagine (défaut : conserver le produit simple).
  2. §5 — asymétrie possible des métas pack / C-14 lors d'une sauvegarde programmatique partielle.
  3. §5 — un pack dont un numéro inclus est dépublié devient entièrement non achetable ; confirmer le comportement attendu.

Aucune question ne touche au réel ni au visuel au point de bloquer : la seule attente visuelle est l'habillage du squelette, déjà rangée par `NOTE.md` pour Ced.

### Décisions techniques, défaut proposé
- Couverture de la couche de branchement dans la suite scellée (important 1). Défaut : l'ajouter sur le modèle des bancs natifs à rollback existants ; Hermès applique, Claude arbitre après coup.
- Déliement symétrique pack ↔ C-14 (mineur 2). Défaut : délier le pack quand un numéro unique valide est enregistré.

### Pour Imagine
- « Produits groupés » du §3.3 = produit simple à prix unique (déjà implémenté) : à entériner.
- Pack contenant un numéro dépublié : rester non achetable (défaut) ou vendre les numéros restants ?
