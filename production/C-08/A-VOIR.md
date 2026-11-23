# C-08 — À voir après corrections du 23 novembre 2026

Site unique **imagine-test-demo**, entièrement fictif : http://192.168.129.32:8085/ . Thème neutre, aucun design final revendiqué.

## Parcours court

1. Ouvrir une fenêtre privée : http://192.168.129.32:8085/c08-article-reserve-article/ (article **81**, sans mot de passe natif).
2. Vérifier l'extrait « Extrait public C08 », le bloc de connexion et l'absence du corps intégral dans la source.
3. Chercher la phrase **Les lucioles violettes de C08 gardent le secret du village fictif.**, en la mettant entre guillemets dans le formulaire de recherche. **Aucun article 81 dans les résultats anonymes.** La phrase saisie peut être réaffichée dans le formulaire/titre : ce n'est pas un fragment de résultat.
4. Chercher **"Extrait public C08"** ou **"Article réservé fictif article"** : l'article réservé est retrouvable par ses données publiques. La correction n'a donc pas retiré arbitrairement tous les articles réservés de la recherche.
5. Se connecter sur http://192.168.129.32:8085/wp-login.php avec le compte C08 `actif`, puis revenir à l'article : le corps et la phrase témoin sont présents. La même recherche sur la phrase trouve désormais l'article 81.
6. Avec le compte `grace`, corps complet et bandeau régularisation ; avec `sans-droit`, extrait et bloc abonnement. Revenir à la même URL en anonyme : jamais de corps complet recyclé.

Les identifiants sont **hors dépôt**, dans `C:\Users\Ced\.imagine-demo\c08-identifiants.json`, section `accounts`, clés `actif`, `grace`, `sans-droit`. Ne pas copier les mots de passe ici. Les identifiants B00/C09 enrichis restent dans `C:\Users\Ced\.imagine-demo\identifiants.json` et ont été préservés.

## Autres sorties

- Sans extrait éditorial : http://192.168.129.32:8085/c08-article-reserve-automatique/ (**82**), message neutre, jamais de découpe du corps.
- REST article : http://192.168.129.32:8085/wp-json/wp/v2/posts/81 ; collections, champs, contexte embed et route alternative vérifiés.
- RSS2 : http://192.168.129.32:8085/?feed=rss2 ; RSS, Atom et RDF également éprouvés.
- Source de l'article : descriptions de partage publiques et JSON-LD **NewsArticle**, sans `articleBody`.
- Accueil : le dernier numéro reste distinct ; la section des cinq derniers articles conserve **82, 81, 45, 44, 43**. Tous les articles canaris de test ont été supprimés.

## Preuves actuelles et rejeu

`verification-finale.json` : **621 contrôles/cas réussis, zéro échec**, dont **299 contrôles HTTP sur 56 réponses**, **23 contrôles d'écriture REST HTTP**, **41 contrôles de pannes/restauration**, et lecture exacte des **13 fichiers PHP déployés**. Le rapport détaille les autres suites ; ce total n'est pas 621 parcours indépendants.

Rejeu complet, dans l'environnement hors dépôt préparé avec les **six wheels figés B01** :

```powershell
C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-c08-venv/Scripts/python.exe wp/tests/demo/c08-final.py
```

Préparation hors ligne documentée dans `wp/plugins/imagine-site/README.md`. Les anciens rapports et PRET sont archivés sous `historique/pre-corrections-17h10/`, pas présentés comme l'état actuel. Les fichiers `red-*` sont les traces des défauts et corrections, pas des échecs résiduels.

## Limites à ne pas confondre avec un GO

- Cache privé/no-store encore large, provisoirement, y compris sur des pages ouvertes ; aucun cache d'hébergement validé.
- Les réglages de `Acces\Reglages` affichables en C10 ne sont **pas raccordés** au moteur par C08 : ses valeurs par défaut restent utilisées.
- Aucun vrai robot Internet vérifié hors ligne ; faux Googlebot/Bingbot refusés. PDF, achat/découverte complets, tunnel, performance exhaustive et validation visuelle restent hors lot.
- Le plugin doit rester actif pour protéger toutes les API. Son absence est testée pour le **repli du corps du thème**, pas présentée comme une protection de toutes les API après désactivation complète du plugin.
- Ne jamais afficher directement `get_post($id)->post_content` : source volontairement intacte en cache objet ; utiliser les points de sortie sécurisés.

`PRET` signifie prêt pour la relecture technique du lot, pas déploiement en production ni validation graphique de Ced.
