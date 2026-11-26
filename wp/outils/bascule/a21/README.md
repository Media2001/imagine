# A-21 — portes vers l'extérieur, lecture seule

## Le standard d'abord (dix lignes)

1. WooCommerce > Réglages > Avancé > REST API gère les clés liées à un utilisateur WordPress (documentation officielle « WooCommerce REST API »).
2. Les permissions natives sont `read`, `write` et `read_write` ; elles ne prouvent pas les droits effectifs du compte associé.
3. Le code installé `includes/class-wc-install.php` place ces déclarations dans la table préfixée `woocommerce_api_keys`, indépendamment du magasin de commandes.
4. Cette table contient aussi description, clé, secret, fragment et nonces : A-21 ne sélectionne aucun de ces champs, ni l'utilisateur.
5. `includes/class-wc-rest-authentication.php::update_last_access` enregistre `current_time('mysql')` : l'horodatage est local au site, pas UTC.
6. WooCommerce > Réglages > Avancé > Webhooks expose états, sujet et destination (documentation officielle « Webhooks »).
7. `includes/class-wc-install.php` et `includes/data-stores/class-wc-webhook-data-store.php` utilisent la table préfixée `wc_webhooks`, identique en classique et HPOS.
8. Les états natifs sont `active`, `paused`, `disabled` ; un sujet peut aussi être une action libre ou provenir d'une extension.
9. `WC_Helper_Options` regroupe les données du magasin dans `woocommerce_helper_data` ; `WC_Helper::is_site_connected()` teste seulement la présence de `auth.access_token`.
10. Cette déclaration locale n'est ni une vérification du compte distant ni une licence : A-21 ne charge aucune liste distante et n'appelle jamais la destination d'un webhook.

Références publiques officielles lues le 26 novembre 2026 : `https://woocommerce.com/document/woocommerce-rest-api/`, `https://woocommerce.com/document/webhooks/`, `https://woocommerce.com/document/managing-woocommerce-com-subscriptions/`. Code qualifié : WooCommerce 11.1.1 du banc synthétique compatible A-02 (WordPress 7.0.9), pas la production 6.9.1.

## Commande opérateur, après autorisation sur une copie vérifiée

Dans le conteneur Linux déconnecté disposant de PHP 8.2+, `pdo_mysql`, Python 3 et Landlock, depuis le répertoire de travail de l'opérateur ; remplacer seulement les chemins. Le parent `/hors-web` doit exister ; la sortie est neuve, sœur du dossier d'audit A-02, et son parent est disjoint du site et du dépôt dans les deux sens.

```text
python3 /chemin/du/depot/wp/outils/bascule/a21/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/portes-date
```

Le banc lance exactement cette ligne avec ses seuls trois arguments, après substitution des chemins fictifs. `--as-of=2026-11-26T00:00:00Z` est facultatif pour figer l'instant UTC ; sans lui, un seul instant UTC courant est capturé. Ne pas appeler le PHP brut : il refuse hors confinement.

## Résultat et limites

- `portes.json` et `portes.md`, comptes seulement ; répertoire 0700, fichiers 0600. Rien n'est corrigé, révoqué, désactivé ou décidé.
- Clés : total, droits, jamais utilisées, strictement avant l'anniversaire de douze mois, dates inconnues. Les deux comptes d'inactivité sont disjoints. NULL, vide et date zéro = jamais ; date invalide ou future = inconnue. Date locale interprétée avec le fuseau WordPress ; le 29 février se rabat au 28 février de l'année précédente. Une date égale au seuil n'est pas « depuis plus de douze mois ».
- Webhooks : comptes par état et par sujet standard fermé (`coupon`, `customer`, `order`, `product` et leurs événements natifs), destinations des seuls actifs. Sujets personnalisés/actions libres regroupés sous `unknown`, jamais recopiés : même un identifiant apparemment technique peut contenir une identité. Pas de description, ID d'objet ou compte, URL ni domaine dans les rapports.
- Domaine = nom d'hôte exact, casse et point DNS final neutralisés ; schéma/port/chemin ne comptent pas. Un sous-domaine distinct est extérieur. URL mal formée, relative ou contenant des identifiants = `unknown` ; pas de résolution DNS, de liste publique de suffixes ou d'appel HTTP. Cette comparaison n'est pas une appréciation de confiance.
- Magasin d'extensions : oui/non sur la déclaration locale native, sans vérification distante ; ne confond pas Jetpack/WordPress.com avec le magasin WooCommerce.
- L'import existant `wp/outils/staging/lib.php` vide `woocommerce_api_keys`, désactive `wc_webhooks`, vide destination/secret et efface les champs sensibles dont `access_token`. Avec sa marque existante `imagine_staging_disabled_plugins`, même vide, les trois rubriques répondent **inconnu après neutralisation**, données `null`, jamais zéro/non historique. L'import reste inchangé. Sans marque, l'outil compte seulement la copie courante et ne prétend pas reconstruire l'historique.
- Bootstrap A-11 partagé : SELECT et transaction READ ONLY avant les extensions, fonctions de processus/mail désactivées, HTTP et planifications bloqués ; Landlock ne permet d'écrire que sous le parent de sortie externe. Aucun réseau Docker, port ni volume dans le banc.
- Cache, pare-feu en fichiers de remplacement et liens symboliques sont refusés ; suivre `../a11/README.md` sur la copie vérifiée, jamais sur la source réelle. Les erreurs ne rendent que des codes fermés et les six noms techniques de remplacement autorisés, jamais un nom libre du site.
- Site simple et tables WooCommerce présentes exigés ; schémas anciens ou incohérents refusés, pas de migration automatique ni de découverte d'autres interfaces propres aux extensions.

## Rejeu synthétique

Sur Windows, aucun PHP hôte : `C:/Python314/python.exe -B wp/tests/a21/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a21-rejeu-nouveau`.
La sortie doit être neuve et hors dépôt. Runner A-21 dérivé du flux A-19 et réutilisant ses helpers A-02 inchangés ; uniquement image préexistante, conteneur jetable sans réseau, fixtures commerciales autorisées. `unit.php` est pur, retourne ses assertions lorsqu'inclus par T-02 et n'a besoin ni de banque native ni de nouvel adaptateur PHPUnit.
Vérification du candidat : `C:/Python314/python.exe -B wp/tests/a21/verify.py production/A-21/preuves/final`.
L'image globale et T-01 finaux restent à la session parente ; ce candidat ne dépose pas `PRET`.
