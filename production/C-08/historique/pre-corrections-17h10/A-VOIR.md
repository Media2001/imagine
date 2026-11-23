# C-08 — à voir sur la démonstration

**Site unique : imagine-test-demo. Aucun contenu, abonné ou paiement réel.**

## Article à ouvrir

http://192.168.129.32:8085/c08-article-reserve-article/

1. **Anonyme** : ouvrir une fenêtre privée. On voit l'extrait public C08, puis « Se connecter » / « S’abonner ». Aucun formulaire de mot de passe de l'article n'est nécessaire. Le texte complet n'est pas dans le code reçu.
2. **Abonné actif** : se connecter sur http://192.168.129.32:8085/wp-login.php avec le compte fictif `imagine-c08-actif`, puis rouvrir l'article. On voit le début, la suite et la fin; aucun bloc d'abonnement.
3. **Délai de grâce** : dans une autre session, se connecter avec `imagine-c08-grace`. Même article complet, avec le bandeau de régularisation. C'est un abonnement Subscriptions natif `on-hold` lié à une adhésion Memberships `paused`, muni d'une fenêtre de grâce fictive explicite.
4. **Faux robot** : le test `python wp/tests/demo/c08-verifier.py` demande la même URL avec les agents Googlebot et bingbot. Ils restent en extrait, y compris avec une fausse IP Google dans les en-têtes de proxy. Changer seulement son User-Agent ne donne aucun accès.
5. **Compte sans droit** : `imagine-c08-sans-droit` montre l'extrait avec le bloc d'abonnement, pas le bandeau de grâce.

**Mots de passe et URL conservés uniquement hors dépôt :**
`C:\Users\Ced\.imagine-demo\c08-identifiants.json`, section `accounts`, entrées `actif`, `grace`, `sans-droit`. Ne pas copier ces valeurs dans un rapport. Les autres identifiants B-00 restent dans leur fichier d'origine.

La phrase témoin, placée au milieu du corps enregistré, est :
> Les lucioles violettes de C08 gardent le secret du village fictif.

Elle doit être présente dans la page d'un abonné actif/en grâce, absente des réponses anonymes. Le second article, sans extrait éditorial, possède un témoin différent pour éviter un faux positif dans les flux :
http://192.168.129.32:8085/c08-article-reserve-automatique/
En anonyme, il affiche la phrase neutre « Cet article est réservé aux abonnés. », jamais une découpe du corps.

## Sorties à consulter en anonyme

- REST : http://192.168.129.32:8085/wp-json/wp/v2/posts/81
- Flux : http://192.168.129.32:8085/?feed=rss2
- Recherche : http://192.168.129.32:8085/?s=C08
- Embarqué : http://192.168.129.32:8085/c08-article-reserve-article/embed/

REST, flux et partage ne contiennent pas le témoin. La recherche native peut exclure entièrement un article qui conserve son mot de passe B-00 : c'est un refus, pas une ouverture. Les métadonnées de partage décrivent le seul extrait public. Le JSON-LD nomme la zone payante sans `articleBody`.

Dans l'onglet réseau du navigateur, la page abonné et les réponses anonymes portent `Cache-Control: no-cache, no-store, private, must-revalidate, max-age=0`; aucun ETag/Last-Modified réutilisable. Les tests redemandent exactement la même URL en anonyme après chaque lecture authentifiée, sans cache-buster.

## Rejouer

À la racine `C:\Users\Ced\imagine` :

```powershell
python wp/outils/demo/c08.py --seed
python wp/tests/demo/c08-idempotence.py
python wp/tests/demo/c08-faults.py
python wp/tests/demo/c08-verifier.py
python wp/tests/demo/c08-regression.py
python -m unittest discover -s wp/tests/demo -p "test_*.py" -v
```

L'installation refuse un autre site, un site arrêté et un environnement non local. Elle ne crée ni n'arrête de site et ne reconstruit pas B-00. Les pannes réelles de configuration et de numéro sont restaurées dans un `finally`, avec relecture exacte et contrôle positif abonné après restauration.

## Limites à ne pas confondre avec le résultat

- **Le PDF n'est pas fermé par C-08.** Les PDF factices B-00 restent publics. Aucun test ne revendique leur protection.
- Pas de DNS externe : le vrai robot Internet n'est pas validé dans cette démonstration hors ligne; les faux robots sont refusés. Le vérificateur C-03 est réellement appelé, pas remplacé par un test d'User-Agent.
- Pas de découverte complète/décompte, tunnel d'achat d'un numéro, cycle réel d'impayés ou certification du mode lecture.
- Pas de cache d'hébergement/CDN testé; politique privée conservatrice sur toutes les réponses dynamiques du squelette, aucun plugin de cache ajouté.
- Les 2 articles C-08 supplémentaires apparaissent dans le sommaire T1; aucun texte/ID/média B-00 n'a été changé. Les anciennes recettes qui exigeaient exactement quatre articles par numéro ou une ouverture par mot de passe sont historiques et ne doivent pas être présentées comme la recette C-08.

Les preuves actuelles sont dans `installation.json`, `idempotence.json`, `faults.json`, `http.json`, `regression.json`, `local-tests.json`, `verification-finale.json`. Les fichiers `red-*` sont des traces historiques d'échecs corrigés, pas le statut final.
