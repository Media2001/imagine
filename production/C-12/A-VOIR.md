# C-12 — À voir sur la démonstration fictive

Cible unique : `http://192.168.129.32:8085` (`imagine-test-demo`). Aucun accès au site réel.

## Démonstration en quelques minutes

1. Se connecter en **e-admin** à `http://192.168.129.32:8085/wp-login.php`. Les mots de passe existants restent dans `C:/Users/Ced/.imagine-demo/identifiants.json`, section `c09_accounts` ; ils ne sont pas recopiés ici.
2. Ouvrir `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages`, section **Accès**. Les cinq paramètres et le sixième champ **Relecture après quota** portent **« À confirmer par Imagine »**. Défauts : **Fermée**, **2 articles**, **7 jours**, **aucun numéro**, relecture **Se refermer**. Activer **Première lecture admissible d’un compte vérifié**, garder **Nombre d’articles / 2**, saisir **39,25,18**, relecture **Se refermer**, enregistrer. Le journal C10 montre administrateur et avant/après.
3. En **v-dec**, ouvrir d’abord `http://192.168.129.32:8085/c12-decouverte-non-designe/` : **extrait seulement**, sans ouverture de découverte. Il appartient au **même numéro 39** que le suivant : le numéro seul n’accorde aucun accès.
4. Ouvrir `http://192.168.129.32:8085/c12-decouverte-un/` : complet, **1/2**. Recharger : **1/2**. Revenir au **non-désigné** : extrait, aucun crédit consommé. Une nouvelle session ne recrédite rien.
5. Ouvrir `http://192.168.129.32:8085/c12-decouverte-deux/` (**numéro 25**) : complet, **2/2**. Puis `http://192.168.129.32:8085/c12-decouverte-trois/` (**numéro 18**) : extrait et **« Votre accès découverte est épuisé »**. Trois numéros existants distincts, **un seul témoin désigné par numéro** ; l’autre témoin du 39 reste réservé.
6. **Relecture après quota, question ouverte** : recharger le premier → bloc épuisé avec **Se refermer**. En e-admin choisir **Rester lisible pour les articles déjà ouverts** ; en v-dec recharger premier et deuxième → complets, toujours **2/2**. Troisième et non-désigné restent fermés. Remettre **Se refermer** → relecture fermée. Ce sont **deux politiques réglables du raccord**, pas une contrainte C06 ni un arbitrage acquis d’Imagine. Le mode lisible transmet au moteur le rang de l’article déjà ouvert, sans retirer/ajouter de crédit au stockage.
7. En **v-dec-fin**, le troisième est épuisé. En anonyme : extrait et connexion. Vider les cookies rend anonyme, pas des crédits.
8. Remettre **Ouverture : Fermée**, **Périmètre : vide**, **Relecture : Se refermer**. Autres réglages C10 inchangés. Ces défauts prudents sont laissés après les tests. Le parcours consomme réellement v-dec : pas de reset silencieux ; le script des profils permet un reset explicite de ce seul personnage fictif si une nouvelle démonstration est souhaitée.

Le mode **Durée** garde sa fin UTC exclue quelle que soit la relecture. Chaque ouverture fige durée/nombre/périmètre initial : les augmenter ne recrédite pas le compte. Le périmètre courant peut retirer, pas élargir l’initial. **La relecture est un réglage courant séparé**, applicable aux comptes épuisés, sans droit permanent ; désignation et périmètres initial/courant restent requis. Fermer suspend la découverte. Les quatre articles sont datés anciennement pour préserver les cartes récentes.

## Rejeu technique du parent

```bash
PYTHONDONTWRITEBYTECODE=1 python C:/Users/Ced/imagine/wp/outils/demo/c12.py --check-only
```

Cette commande commence par PHPUnit hors réseau (vrais **Paywall + Decouverte + moteur C06**, API WP/SQL doublées), relit les trois fichiers applicatifs installés, téléverse les recettes, exerce PHP natif, HTTP connecté/anonyme, POST `options.php` et concurrence, puis la non-régression C11 et les unitaires Python. Options, politique de relecture et état V-DEC sont restaurés exactement, même en échec. Les six wheels B01 sont lues sans installation. Pour le banc autonome ou l’installation ciblée :

```bash
PYTHONDONTWRITEBYTECODE=1 python C:/Users/Ced/imagine/wp/outils/demo/c12-unit.py
PYTHONDONTWRITEBYTECODE=1 python C:/Users/Ced/imagine/wp/outils/demo/c12.py
```

Résultats : `C:/Users/Ced/imagine/production/C-12/resultats.json`. Le script C09 intègre maintenant les deux profils découverte ; son complément ciblé est `wp/outils/demo/c12-profils.php`. Aucun fichier de `production/C-09` ou `production/C-11` n’est écrit par le runner C12.

Le seed conserve les IDs des trois témoins et rattache deux/trois aux numéros 25/18 ; il ajoute le seul témoin non désigné du 39. Migration bornée du personnage fictif **V-DEC-FIN** : son ancien périmètre de démo devient 39/25/18 **sans changer ses deux articles consommés** ; aucun compte lecteur ni crédit n’est élargi. Bootstrap C13 et PdfNumero C11 ne sont pas réinstallés.

**Limite du runner partagé :** `wp/tests/rejouer.ps1` ne sélectionne pas `phpunit.c12.xml` et n’a pas de cache Composer imagine-site : ses 812 tests ne couvrent pas ce raccord. Repli C11 réutilisé sans modifier runner/T01 : image existante `imagine-tests-t01:1`, PHPUnit 11.5.58, PHP 8.2.33, conteneur local éphémère `--network none`, dépôt en lecture seule, nettoyage/absence relus. Aucun téléchargement ni installation. La preuve SQL/HTTP native reste distincte des doublures locales.

## Périmètre démontré et limites

- Compte avec prénom, nom et email valide. **Email confirmé par drapeau fictif** `imagine_email_confirme=1` posé pour ces deux profils : ni email envoyé, ni vrai parcours de vérification revendiqué. Le refus des emails jetables est à brancher dans le futur parcours d’inscription.
- Une seule ouverture **par compte**. Recréer un compte avec une autre adresse, prouver l’unicité par personne ou résister à une suppression administrative des données : hors périmètre.
- REST authentifié avec nonce de la vraie session, flux, recherche, aperçu, oEmbed/embed, HEAD/POST, préchargement et robots reconnaissables ne démarrent ni ne consomment la découverte ; pas de corps réservé sur ces sorties au titre de la découverte. Les droits abonnés natifs restent indépendants.
- Les robots Google/Bing locaux sont des **faux robots non vérifiés** ; le contrat robot vérifié est éprouvé séparément en PHP, sans prétendre avoir fait du DNS Internet. Un robot avec cookies valides et UA humain n’est pas distinguable d’un lecteur.
- Découverte **articles seulement**, jamais PDF. Le stockage privé C11, le PDF abonné exact et les refus anonymes/REST ont été rejoués sans reconstruction.
- Réglages C10 étendus depuis `imagine-site` par hooks et enveloppement du rendu existant, faute de hook interne. Aucun fichier de la bibliothèque close n’est modifié. La table/titre de la section Accès est une dépendance de ce petit raccord, contrôlée par HTTP.
- Désignation native **imagine_decouverte**, booléenne, éditable via l’API WordPress par l’éditeur autorisé. Absente/fausse/invalide : pas de découverte. Les droits natifs prioritaires restent indépendants.
- **À confirmer par Imagine : relecture après quota — se refermer ou rester lisible ?** Doctrine §4 appliquée, deux valeurs testées, choix courant prudent **fermé**, sans inventer l’arbitrage. Déclencheur, durée, nombre et périmètre restent également à confirmer. Aucun GO réel, paiement, achat, installation NUC, email sortant ou validation visuelle n’est déduit de PRET. Aucun gate paiement C09/C13 n’est contourné.

## Documentation officielle consultée avant la correction applicative

- WordPress Settings API : `https://developer.wordpress.org/plugins/settings/settings-api/` — persistance native, capacité et nonce de `options.php`.
- WordPress `register_post_meta()` : `https://developer.wordpress.org/reference/functions/register_post_meta/` — clé éditoriale native, aucune table sur mesure.
- WordPress `get_post_meta()` : `https://developer.wordpress.org/reference/functions/get_post_meta/` — vrai stocké comme `1`, faux comme chaîne vide ; absence fermée via `metadata_exists`.
- WordPress `add_option()` : `https://developer.wordpress.org/reference/functions/add_option/` — son code comporte un UPSERT ; le compteur utilise INSERT IGNORE et un compare-and-swap binaire pour ne jamais écraser une ouverture concurrente.
- WordPress `template_redirect` : `https://developer.wordpress.org/reference/hooks/template_redirect/` — connaissance de la requête finale avant le rendu ; consommation après les redirections canoniques, sans changer le template.
- WooCommerce Memberships, restrictions : `https://woocommerce.com/document/woocommerce-memberships-restrict-content/` — réutilisation des adhésions/restrictions natives existantes ; le stockage nouveau se limite à l’ouverture et au compteur que ces règles ne raccordent pas.
