# A-24 — adresses d’expédition, comptes seulement

## Standard installé — dix lignes

1. Un abonnement `WC_Subscription` hérite des accesseurs d’adresse de `WC_Order` ; aucune adresse n’est déduite du produit.
2. Classique : le CPT `shop_subscription` utilise `posts` et les métadonnées `_shipping_*` / `_billing_*` dans `postmeta`.
3. HPOS : `wc_orders` porte l’abonnement ; `wc_order_addresses`, discriminé par `address_type=shipping` ou `billing`, porte les adresses.
4. L’outil lit exclusivement le magasin faisant autorité via `wcs_get_subscriptions()` et les getters natifs en contexte `edit`.
5. Le compte client garde sa propre livraison `shipping_*` en `usermeta`, lue par `WC_Customer`, jamais recopiée vers l’abonnement.
6. `WC_Countries::get_address_fields($country, 'shipping_')` fournit les obligations natives ; les locales de pays, options de visibilité et filtres natifs sont respectés.
7. Par défaut BE/FR : prénom, nom, pays, rue, ville et code postal requis ; US ajoute l’État ; AE n’exige ni code postal ni État (banc épinglé).
8. Société, complément et téléphone dépendent aussi des options natives ; leur liste n’est pas une règle postale inventée par A-24.
9. Pays vide : Woo applique son pays de base ; pays inconnu : ses champs par défaut ; l’outil compte en plus pays absent et pays inconnu séparément.
10. La documentation officielle décrit ces API et les filtres ; le banc photographie leurs obligations et empreintes dans `*-standard.json` sur la pile réellement exécutée.

Références officielles consultées le 26 novembre 2026 :
- `https://woocommerce.com/document/subscriptions/develop/functions/` — Subscription Function & Property Reference (héritage WC_Order).
- `https://developer.woocommerce.com/docs/features/high-performance-order-storage/` — magasins autoritaire/de secours et quatre tables HPOS.
- `https://developer.woocommerce.com/docs/customizing-checkout-fields-using-actions-and-filters/` — `get_address_fields`, locales, `required` et filtres. Cette page vise surtout le checkout classique ; A-24 n’est pas un validateur de checkout en blocs.

## Parcours opérateur

Uniquement sur copie anonymisée et vérifiée, Linux isolé, aucun réseau non-loopback, PHP 8.2+, Python 3 et noyau Landlock. **Aucun accord pour lire la source réelle.** Le compte SQL de la copie doit avoir SELECT seulement. Le lanceur ajoute une transaction READ ONLY, une façade SQL, le confinement fichiers A-12, puis le gardien A-22 inchangé. Ce dernier attend la terminaison et les deux EOF ; JSON/Markdown sont contrôlés intégralement avant publication atomique. `error_log` vise `/dev/null` avec le seul droit d’écriture correspondant ; les écritures ailleurs restent bloquées.

Depuis la racine du dépôt, après l’audit A-02, remplacer seulement les trois chemins ; ne pas ajouter d’argument :

```sh
python3 wp/outils/bascule/a24/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/expedition-date
```

Le dossier `/hors-web` existe, est privé, hors web et disjoint du dépôt et du site dans les deux sens ; `expedition-date` n’existe pas. L’audit se trouve dans un sous-dossier voisin. Sortie nominale : `A24_OK expedition.json expedition.md`. PHP brut est refusé. Un refus ne sort qu’un code fermé ; pour un drop-in, le seul détail possible est un nom technique de la liste fermée. Rien de libre ni d’issu du site n’est conservé sur un refus.

## Lecture des comptes

- Vivants = `active`, `pending`, `on-hold`, `pending-cancel`, exactement comme A-20 ; un abonnement compte une fois, pas un client et pas un droit au prochain numéro.
- Les dix champs natifs examinés sont `shipping_first_name`, `shipping_last_name`, `shipping_company`, `shipping_country`, `shipping_address_1`, `shipping_address_2`, `shipping_city`, `shipping_state`, `shipping_postcode`, `shipping_phone`.
- Vide/manquant = chaîne vide après `trim` ; « facturation remplie » signifie au moins un des dix champs de facturation non vide, pas une attestation de complétude. Aucun repli facturation→livraison.
- `missing_required` compte, par champ fermé, son absence lorsqu’il est requis par Woo ; `missing_any` compte au moins une de ces absences. Aucune validation du format postal, de la rue ni de la distribution.
- `different_from_account` compare les dix champs uniquement en mémoire : suppression de tous les caractères d’espacement Unicode (`\p{Z}` et `\s`, en bord comme à l’intérieur), puis comparaison Unicode insensible à la casse simple de PCRE (`/iu`, sans mbstring/intl). Ainsi `Rue Exemple` et `rueexemple` sont égaux ; accents, ponctuation et vrais caractères différents restent significatifs. Pas de translittération ni de normalisation postale ; une entrée UTF-8 invalide/non comparable reste différente. Les valeurs d’origine, la complétude (`trim`), `shipping_empty`, pays et groupes ne changent pas. `account_unavailable` distingue les abonnements sans compte existant ; ils ne sont pas comptés comme différents ni comme égaux.
- Pays : code natif exact, sans correction de casse/espaces ; absent et non reconnu sont séparés. Les codes connus viennent de Woo mais la sortie est bornée par `country_codes.json` issu de Woo 11.1.1, Kosovo compris. Une extension qui ajoute un pays ou un champ non qualifié provoque un refus fermé, jamais la restitution de son nom.
- `overall` et `countries` portent les mêmes métriques. Chaque pays/groupe absent/inconnu de moins de cinq abonnements est fondu dans `autres pays` ; ce groupe peut dépasser cinq. Les groupes de taille suffisante affichent seulement le code ou `country_absent`/`country_unknown`, jamais une valeur inconnue.

## Après neutralisation

L’import A-01 n’est pas modifié. Son anonymiseur efface prénom/nom, société, rue/complément, ville, État, code postal et téléphone sur abonnement, facturation et compte ; il conserve les pays et les liens de compte. Sur sa marque `imagine_staging_disabled_plugins`, `shipping_empty`, `empty_with_billing`, `missing_any`, `different_from_account` et chaque champ manquant **sauf `shipping_country`** valent `inconnu après neutralisation`, globalement et par pays. Restent lisibles : nombre d’abonnements, pays absent/inconnu, répartition par pays, champ pays requis absent, comptes indisponibles. Les zéros des autres champs ne doivent pas être interprétés : ils ne sont pas publiés. Le diagnostic complet des adresses d’origine reste à Ced, hors des agents.

## Rejeu local et réception

### Prérequis des fixtures Python sous Windows

Utiliser un compte autorisé à créer, lire, renommer et supprimer des dossiers/fichiers dans un **scratch local hors dépôt**, sans règle antivirus/EDR interdisant ces opérations. Avant la suite, créer ce dossier et définir **TMPDIR, TMP et TEMP** vers lui (commandes exactes dans `production/A-24/COMMANDES.md`). Ne pas viser le Temp système ; ne pas ignorer une erreur de nettoyage ni désactiver une protection de poste. Les tests utilisent `TemporaryDirectory(dir=TMPDIR)` et gardent un nettoyage strict. Les six erreurs WinError 5 de la relecture n’ont pas été reproduites avec ce prérequis : les 14 tests initiaux passent sous UTF-8 et cp1252 sur Windows/Python 3.14.6, puis les 15 tests corrigés passent également. Cela qualifie ce poste et ce scratch, pas une installation Windows neuve ni la cause exacte du refus chez le relecteur.

**Portée :** pour A-24, `wp/tests/rejouer.ps1` ne rejoue que l’unité PHP pure (`unit.php`). Il ne rejoue ni l’adaptateur natif classique/HPOS, ni le confinement, ni les tests Python ; leurs preuves intégrées viennent de la matrice scellée. Le paquet historique `preuves/final/` atteste 206 contrôles natifs de l’ancien code, pas la correction courante ; une nouvelle matrice puis un reseal par le parent sont obligatoires avant réception. Le rejeu Python et PHP pur sans Docker effectué pour les corrections est documenté séparément dans `production/A-24/corrections-reveil.md`.

PHP pour la matrice native uniquement dans un conteneur jetable sans montage, réseau ni port. Image locale épinglée, licences locales fictives : pas de téléchargement ni de lancement du site de démonstration. Les commandes Windows exactes et la réception sont dans `production/A-24/COMMANDES.md` ; `wp/tests/a24/run.py --output=...` exige un dossier scratch neuf hors du dépôt. Le vérificateur accepte qu’un futur `production/A-24/PRET` soit ajouté par le parent : il ne l’épingle ni n’exige son absence. Le mode d’emploi commun appartient au parent ; les deux seules lignes à intégrer figurent dans `production/A-24/readme-ajout.txt` et seront contrôlées par contrat, sans empreinte du fichier partagé.
