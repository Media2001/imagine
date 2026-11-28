# C-33 — comptes non publics en anonyme

Trois adresses à ouvrir en navigation privée :

1. http://192.168.129.32:8085/?author=2 — page introuvable, **404 sans redirection** et sans adresse publique d’auteur. Les archives par nom sont aussi fermées.
2. http://192.168.129.32:8085/wp-json/wp/v2/users — erreur REST **404**, aucune liste de comptes ; même règle pour un numéro, la casse et l’alias rest_route.
3. http://192.168.129.32:8085/?feed=rss2&withoutcomments=1 — flux d’articles : signature B16 si renseignée, sinon nom du site, jamais le nom du compte de saisie. Atom et oEmbed reçoivent le même traitement, adresse de compte supprimée.

Le sitemap est désactivé au repos (`blog_public=0`). La recette l’a réellement activé pour un témoin puis a restauré l’option exacte : index XML non vide, sans section utilisateurs. L’ancienne adresse directe du fournisseur absent rend ici une page HTML 200 sans compte, pas un sitemap utilisateurs (comportement natif documenté, aucune règle de serveur). Six autres types vus : post, page, product, imagine_numero, imagine_evenement, imagine_partenaire. Aucun type de message de visiteur/contact ni pièce privée dans cet index ; rien d’autre n’a été corrigé.

Preuves courantes : `native-final-V2.json` (14 contrôles), `browser-final-V2.json` (53 contrôles, 19 réponses brutes HTTP sans cookies/jetons, capture Edge). Compte témoin ayant publié vérifié avant les contrôles d’absence. **Six mutations sur cinq voies** : archive numérique (redirection native dévoilant le compte), REST, index du sitemap, détail utilisateurs du sitemap, flux et oEmbed. Chaque voie revient réellement au comportement natif lorsqu’on retire son filtre en mémoire de requête ; le même contrôleur refuse la réponse. Administrateur et éditeur listent le témoin dans le sélecteur REST natif et lisent l’article en contexte d’édition. Aucun privilège étendu ni interface d’édition remplacée.

```bash
python -B production/C-33/verifier.py --live
python -B wp/outils/demo/c33.py native nouvelle-native-V2
python -B wp/outils/demo/c33-browser.py nouveau-browser-V2
```

Compte, article, métadonnées, sessions du seul compte témoin, options et sonde retirés/restaurés et relus. Snapshot privé durable avant mutations. Le premier banc a conservé un FAIL de comparaison stricte : seulement la version du cache natif Woo `product_query` avait été régénérée par suppression de l’article ; aucun état métier ne différait. Cette ancienne version n’est pas présentée comme retrouvée. Le banc capture et restaure désormais aussi cette ligne. Autres échecs historiques : attente 404 indue pour le fournisseur sitemap absent (le cœur retombe en HTML 200), et flux `?p=ID` natif de **commentaires**, remplacé par `withoutcomments=1` pour exercer le vrai flux d’articles. Aucun échec réécrit.

Périmètre : anonymes seulement ; rien changé pour les connectés. Pas de 2FA, limitation de tentatives, hébergement, nom public de compte choisi par un humain, ni réécriture globale des identifiants d’auteur présents sur les objets REST posts. Aucun code clos/B16/C26 modifié, aucun nouveau contenu de visiteur collecté ; pas de donnée ni de site réel.
