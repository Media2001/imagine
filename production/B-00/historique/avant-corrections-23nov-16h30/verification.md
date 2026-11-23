# B-00 — vérification et limites

## Livré

`imagine-test-demo` a été créé par la voie normale de l’outil, puis construit et rejoué sans destruction. URL : **http://192.168.129.32:8085** ; registre relu : **`running`**. Aucune intervention sur les autres sites, la voie 1, les verrous, les rapports globaux ou Git.

- WordPress **7.0.9**, PHP **8.3**, WooCommerce **11.2.2**, Subscriptions **9.4.1**, Memberships **1.30.3**, plugin `imagine-site` actif. Les classes et fonctions des deux extensions premium sont réellement chargées, pas seulement inscrites dans une liste.
- Les ZIP déposés par Ced imposent notamment WP 7.0 et WooCommerce 11.1 pour Subscriptions. WooCommerce 11.2.2 a été choisi dans sa plage testée déclarée 11.2 ; le dernier WooCommerce public observé était 11.3.1, volontairement non choisi. Aucune dépendance n’a été abaissée ni aucun contrôle de version contourné. Les en-têtes, minima internes Memberships et SHA-256 des ZIP sont dans `b00-reconstruction.json` ; les métadonnées officielles sont dans `versions-sources.json`.
- Quatre numéros trimestriels fictifs et un hors-série d’été 2026 ; chacun possède trois articles réservés, un ouvert, une couverture PNG générée (aplat et numéro) et un PDF factice généré. Trois thématiques, deux événements, deux partenaires, accueil et calendrier. Aucun média web, archive Imagine ou contenu réel.
- Calendrier déterministe **2026–2028** : sorties le 15 janvier, avril, juillet et octobre, hors-série le 15 août, clôture dix jours avant. **J’ai compris que ces dates devaient être des fixtures, non des dates métier validées**, car « Données communes » demande trois ans mais ne donne pas de jours précis.
- Les bibliothèques closes `imagine-pilotage` et `imagine-connecteur` n’ont pas de fichier plugin WordPress et ne peuvent donc pas être « activées ». Leurs `src/` sont copiés sans modification et leurs classes sont chargées par `imagine-site`, vérifiées en PHP. Rien n’a été écrit dans ces bibliothèques.
- Le modèle et l’association `imagine_numero_id` sont déclarés en code, sans ACF. Le thème `imagine` de B-01 n’existe pas encore : Twenty Twenty-Five reste actif, conformément au brief.

## Sécurité du démonstrateur

La création normale autorisée installe Novamira/licence/MCP sans contournement ; c’est l’exception écrite de la révision du 23 novembre à 13 h 45. Immédiatement après cette création, la garde MU est posée **avant les extensions Woo et le seed** : `pre_wp_mail` renvoie `false`, `pre_http_request` renvoie `imagine_demo_offline`, toutes les passerelles disponibles sont filtrées à vide et le suivi Woo est désactivé. Le site est non indexable. Aucun compte WooCommerce.com, aucune activation de licence commerciale, aucune connexion Stripe/PayPal/Brevo/Odoo/CoopHub.

Cette garde vise les API email/HTTP de WordPress ; elle n’est pas présentée comme un pare-feu Docker ou une preuve d’isolation réseau du conteneur. Les téléchargements explicites des logiciels publics par le constructeur et le provisionnement standard de Novamira sont distingués du fonctionnement hors ligne du site. Aucun transport de paiement ni commande/abonnement réel n’a été créé.

Les secrets de test sont générés hors dépôt : `C:\Users\Ced\.imagine-demo\identifiants.json`. Leur copie de travail côté conteneur est dans `/var/www/.imagine-demo/seed-secret.json`, hors racine web, dossier 0700 et fichier 0600. Ils ne sont jamais affichés ni placés dans les preuves. Les comptes utilisent `@example.org`. Aucun cookie ou nonce d’administration authentifiée n’est sauvegardé.

Pour ne pas rendre les textes réservés publics en attendant C-08, **j’ai utilisé provisoirement la protection par mot de passe native WordPress**, avec extrait public et corps complet conservé dans `post_content`. Les réponses anonymes page/REST/flux/recherche/oEmbed ne livrent pas le marqueur du texte réservé ; un accès avec le secret fictif hors dépôt restitue le corps complet. **Cela ne remplace pas C-08, ne branche pas le moteur de droits et ne valide aucun accès abonné.**

## Exécutions et preuves

- Création normale : `b00-creation-normale.txt`, registre `created_at=2026-11-23T13:03:15+00:00`. La fonction `ensure_site()` du script a créé le site alors absent ; les premières exécutions complètes ont ensuite repris ce même site. Pas de fausse réponse HTTP 201 fabriquée : la sortie réelle de la création est conservée, mais son paquet HTTP brut initial n’avait pas été archivé.
- Première construction complète, mises à jour et installations réelles : `b00-construction.json` (copie aussi dans `tests/b00-premiere-construction.json`).
- Relances complètes du constructeur : `b00-reconstruction.json`. Comparaison exacte du snapshot initial et final : mêmes IDs, slugs, URL, empreintes des textes et fichiers, métadonnées et compte de test. **41 objets WordPress tagués**, plus trois termes et un utilisateur fictif dans le manifeste de **45 entrées** ; inventaire indépendant égal au manifeste, zéro doublon. `tests/b00-snapshot-initial.json` conserve la référence avant relance.
- Tests Python : **4 réussis** ; refus d’autre slug et de secrets dans le dépôt, création normale/reprise par l’API, concurrence avec trois attentes de 300 secondes, fixtures/assets déterministes. Les attentes de concurrence sont testées sans immobiliser réellement l’outil ; aucun refus de concurrence n’a eu lieu pendant cette exécution.
- Recette réelle dans WordPress : **81 contrôles réussis**, zéro échec, stderr vide. Types, calendriers, articles, couvertures/PDF, bibliothèques, versions et blocages email/HTTP/paiement.
- HTTP et idempotence : **81 assertions réussies**, zéro échec. Les six URL de `A-VOIR.md` sont toutes observées : accueil/numéro/réservé/ouvert/calendrier HTTP **200** ; `/wp-admin/` HTTP **302** vers la connexion, formulaire et session administrateur fictif HTTP **200**. Les autres objets et les dix fichiers médias ont également été visités. `b00-verification-http-idempotence.json`, réponses publiques dans `http/`.
- Syntaxe PHP : **5 fichiers B-00 sans erreur** ; comparaison des secrets générés aux artefacts du périmètre : aucune occurrence. `tests/b00-syntaxe-secrets.json`.

La preuve RED des quatre types encore absents avant implémentation est `tests/b00-red-runtime.json`. Pendant la mise au point, `eval-file` a refusé `strict_types` (corrigé par inclusion réelle via `wp eval`), et le dossier privé des secrets était initialement non inscriptible (création ciblée du dossier et droits corrigés). Ces incidents ont été retestés, ils ne constituent plus des blocages.

## Standard utilisé et sources primaires

Le code s’appuie sur les mécanismes WordPress existants, plutôt que d’inventer un système de contenu ou de diffusion :

- `register_post_type()` : https://developer.wordpress.org/reference/functions/register_post_type/
- `register_post_meta()` : https://developer.wordpress.org/reference/functions/register_post_meta/
- protection native : https://developer.wordpress.org/reference/functions/post_password_required/
- court-circuit email : https://developer.wordpress.org/reference/hooks/pre_wp_mail/
- court-circuit HTTP : https://developer.wordpress.org/reference/hooks/pre_http_request/
- Subscriptions : https://woocommerce.com/document/subscriptions/
- Memberships : https://woocommerce.com/document/woocommerce-memberships/

Les pages primaires ont répondu HTTP 200, consignées dans `sources-standard.json`. Les versions imposées par les ZIP locaux sont fondées sur **leurs propres en-têtes et constantes**, non extrapolées de la documentation publique. Aucun achat ou compte commercial nécessaire.

## Reste à valider

Aucun blocage technique B-00 restant. `PRET` signifie prêt à relire ; la clôture et les validations de Ced restent celles de la doctrine. Les gabarits B-01, le paywall C-08 et les trente profils C-09 **ne sont ni réalisés ni revendiqués par B-00**. Les constats de blocage du brief ancien sont conservés sous `historique/` et remplacés par le diagnostic actuel.
