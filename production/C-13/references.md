# C13 — références officielles vérifiées (24/11/2026)

- WordPress `add_submenu_page` : https://developer.wordpress.org/reference/functions/add_submenu_page/ — capacité du menu ET contrôle du callback ; admin native suffisante.
- WordPress `check_admin_referer` : https://developer.wordpress.org/reference/functions/check_admin_referer/ — nonce vérifie l'intention, ne remplace jamais la capacité.
- WordPress `admin_post_{$action}` : https://developer.wordpress.org/reference/hooks/admin_post_action/ — contrôleur authentifié, réponse CSV à la demande ; aucun fichier export public.
- WooCommerce CRUD : https://developer.woocommerce.com/docs/best-practices/data-management/crud-objects/ — lecture par objets natifs, compatible stockage HPOS, aucune requête SQL sur les commandes.
- Subscriptions : https://woocommerce.com/document/subscriptions/develop/functions/ — dates `get_date(..., 'gmt')`, statuts et getters natifs.

Standard réutilisé : menu/formulaire/tableaux WordPress, capacités natives, nonce, contrôleur admin-post, CRUD Subscriptions/Memberships. Sur-mesure limité au raccord C01/C07, aux observations postales datées et à l'audit. CSV et protection tableur viennent exclusivement de C07/C04 ; format lu dans C10. Aucun changement des bibliothèques closes.

Traçabilité de méthode : les cinq URL officielles ont été relues en HTTP 200. La consultation distante a été tardive sur le premier tracer calendrier/capacités ; ce point de procédure n'est pas présenté comme conforme à « docs avant code ».

Constats préalables : le rôle dédié existe réellement et e-abo le possède ; aucun élargissement requis. C09 contient des états présents, sans historique postal daté de clôture, aucun paiement, ni attribution persistée des quatre numéros. Ne pas reconstituer un historique passé à partir des états présents ; si un abonnement existait avant une clôture mais n'a aucun relevé antérieur, l'export est fermé. Offerts/groupés restent absents du natif C09 : ne pas inventer de bénéficiaires.

## Corrections du 25 novembre — contrats primaires inspectés avant raccord

- Source native installée Subscriptions : `includes/gifting/class-wcs-gifting.php`, méthodes `is_gifted_subscription`, `get_recipient_user`, `set_recipient_user` ; relation `_recipient_user`, signal de cadeau non résolu `_recipient_user_email_address`. Pas de rapprochement automatique par email ; expédition du cadeau sur son adresse de livraison native.
- Source native `WC_Subscription::get_related_orders('all', 'renewal')`, relations HPOS via CRUD. `get_billing_interval()` revient ici comme chaîne ; comparaison normalisée explicitement. Les sauvegardes réelles utilisent `woocommerce_after_subscription_object_save` (B02 le constatait déjà) ; son raccord spécifique préexistant est conservé.
- Memberships : objets/plans natifs `wc_memberships_get_user_membership`, `wc_memberships_get_membership_plan`, produits du plan et lien `_subscription_id`. Le modèle collectif livré est explicitement configurable/fermé par défaut ; aucune extension Teams n’est installée ni prétendue testée.
- Règles closes lues sans écriture : C01 `Calendrier::modifier`, `Moteur::ouvrir/renouveler/numeros/nonResolus` ; C07 `Abonnement`, `Situation`, `ListeEnvoi::etablir`. Le nouveau code pur leur délègue les blocs et l’éligibilité ; il conserve seulement les règles d’adaptation historique C13.
- Découverte T01 inspectée en lecture seule : `Get-T01Packages`, `verifyCoverage` et `executer.php`. Configuration racine acceptée : bootstrap Composer, couverture complète de `tests/`, manifests et lock préparés. Le nouveau paquet l’utilise tel quel, sans toucher aux fichiers fermés. Les dépendances reprennent les versions verrouillées publiques existantes ; hash de contenu du nouveau manifeste recalculé selon l’algorithme primaire Composer, sans changer les versions.

Les sources de B02/C14/fermées sont relues conformes au dépôt avant/après le rejeu natif. Résultats et limites actuels : `RAPPORT.md`, `resultats.json`, `resultats-purs.json`. Les constats C09 restent des limites de données d’acceptation, plus une absence du raccord cadeau/groupe/renouvellement.
