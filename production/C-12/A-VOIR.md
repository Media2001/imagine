# C-12 — À voir sur la démonstration fictive

Cible unique : `http://192.168.129.32:8085` (`imagine-test-demo`). Aucun accès au site réel.

## Démonstration en quelques minutes

1. Se connecter en **e-admin** à `http://192.168.129.32:8085/wp-login.php`. Les mots de passe existants restent dans `C:/Users/Ced/.imagine-demo/identifiants.json`, section `c09_accounts` ; ils ne sont pas recopiés ici.
2. Ouvrir `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages`, section **Accès**. Les cinq champs Découverte portent **« À confirmer par Imagine »**. Le défaut est **fermé**, forme **nombre d’articles**, **2 articles**, **7 jours**, **aucun numéro**. Choisir **Première lecture admissible d’un compte vérifié**, garder **Nombre d’articles / 2**, saisir **39** dans le périmètre, puis enregistrer. Le journal C10 montre le compte administrateur et les valeurs avant/après.
3. Dans une autre session, se connecter en **v-dec**, sans visiter d’autre article réservé du numéro 39 entre les étapes. Ouvrir `http://192.168.129.32:8085/c12-decouverte-un/` : texte complet, compteur **1/2**. Recharger ce même article : toujours **1/2**. Une autre session du même compte n’ajoute aucun crédit.
4. Ouvrir `http://192.168.129.32:8085/c12-decouverte-deux/` : texte complet, **2/2**. Puis `http://192.168.129.32:8085/c12-decouverte-trois/` : seulement l’extrait et **« Votre accès découverte est épuisé »**. Une relecture après épuisement est également fermée, conformément au moteur C06 ; le compteur n’est jamais décrémenté pour prolonger le droit.
5. Se connecter en **v-dec-fin**, puis ouvrir le troisième article : même bloc d’épuisement. En fenêtre anonyme : extrait et connexion. Vider les cookies rend anonyme, pas des crédits.
6. Revenir en e-admin et remettre **Ouverture : Fermée**, **Périmètre : vide**. Les autres réglages C10 ne changent pas. Le lot laisse lui-même ces valeurs prudentes après ses tests.

Le mode **Durée** utilise la durée, pas le nombre ; fin UTC exclue. Chaque ouverture fige ses paramètres. Modifier la durée/le nombre ne recrédite jamais un compte déjà ouvert ; le périmètre courant peut retirer un numéro mais n’élargit pas le périmètre initial. Fermer suspend tous les accès découverte. Les trois articles C12 sont datés anciennement pour préserver les cartes récentes de la démo.

## Rejeu technique du parent

```bash
python C:/Users/Ced/imagine/wp/outils/demo/c12.py --check-only
```

Cette commande relit le code installé, téléverse les recettes ciblées, exerce le vrai HTTP connecté/anonyme et les POST natifs `options.php`, puis la non-régression C11 et les unitaires locaux. Elle restaure exactement les options et l’état V-DEC trouvés à l’entrée, même en cas d’échec. Elle ne remet donc pas à zéro une démonstration déjà consommée. Pour installer les seuls fichiers/fixtures C12, sans constructeur global ni reset des autres profils :

```bash
python C:/Users/Ced/imagine/wp/outils/demo/c12.py
```

Résultats : `C:/Users/Ced/imagine/production/C-12/resultats.json`. Le script C09 intègre maintenant les deux profils découverte ; son complément ciblé est `wp/outils/demo/c12-profils.php`. Aucun fichier de `production/C-09` ou `production/C-11` n’est écrit par le runner C12.

## Périmètre démontré et limites

- Compte avec prénom, nom et email valide. **Email confirmé par drapeau fictif** `imagine_email_confirme=1` posé pour ces deux profils : ni email envoyé, ni vrai parcours de vérification revendiqué. Le refus des emails jetables est à brancher dans le futur parcours d’inscription.
- Une seule ouverture **par compte**. Recréer un compte avec une autre adresse, prouver l’unicité par personne ou résister à une suppression administrative des données : hors périmètre.
- REST authentifié avec nonce de la vraie session, flux, recherche, aperçu, oEmbed/embed, HEAD/POST, préchargement et robots reconnaissables ne démarrent ni ne consomment la découverte ; pas de corps réservé sur ces sorties au titre de la découverte. Les droits abonnés natifs restent indépendants.
- Les robots Google/Bing locaux sont des **faux robots non vérifiés** ; le contrat robot vérifié est éprouvé séparément en PHP, sans prétendre avoir fait du DNS Internet. Un robot avec cookies valides et UA humain n’est pas distinguable d’un lecteur.
- Découverte **articles seulement**, jamais PDF. Le stockage privé C11, le PDF abonné exact et les refus anonymes/REST ont été rejoués sans reconstruction.
- Réglages C10 étendus depuis `imagine-site` par hooks et enveloppement du rendu existant, faute de hook interne. Aucun fichier de la bibliothèque close n’est modifié. La table/titre de la section Accès est une dépendance de ce petit raccord, contrôlée par HTTP.
- Déclencheur, durée, nombre et périmètre : **à confirmer par Imagine**. Aucun GO réel, paiement, achat, installation NUC, email sortant ou validation visuelle n’est déduit de PRET.

## Documentation officielle consultée

- WordPress Settings API : `https://developer.wordpress.org/plugins/settings/settings-api/` — persistance native, capacité et nonce de `options.php`.
- WordPress `add_option()` : `https://developer.wordpress.org/reference/functions/add_option/` — son code comporte un UPSERT ; le compteur utilise INSERT IGNORE et un compare-and-swap binaire pour ne jamais écraser une ouverture concurrente.
- WordPress `template_redirect` : `https://developer.wordpress.org/reference/hooks/template_redirect/` — connaissance de la requête finale avant le rendu ; consommation après les redirections canoniques, sans changer le template.
- WooCommerce Memberships, restrictions : `https://woocommerce.com/document/woocommerce-memberships-restrict-content/` — réutilisation des adhésions/restrictions natives existantes ; le stockage nouveau se limite à l’ouverture et au compteur que ces règles ne raccordent pas.
