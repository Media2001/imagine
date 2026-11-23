# C-08 — rapport de livraison

**Fait** : adaptateur réel C-06/C-03, raccord minimal au corps d'article, blocs neutres, gardes serveur et cache privé déployés sur le seul `imagine-test-demo`.
**Prêt à relire** : C-08, périmètre du brief; parcours dans `A-VOIR.md`.
**À valider par Ced** : présentation provisoire des blocs; aucune règle financière ni durée de grâce réelle décidée ici.
**Bloqué** : aucun blocage sur les critères C-08 vérifiés.
**Suite** : retour au parent; aucun autre lot, verrou ou rapport global touché.

## Résultat réel

- Article principal : http://192.168.129.32:8085/c08-article-reserve-article/ (ID 81). Second article sans extrait : ID 82.
- Phrase témoin au milieu du corps, absente des sorties anonymes contrôlées; présente dans page et REST authentifiés de l'abonné actif et de la grâce. Anonyme, actif, grâce, faux Googlebot/Bingbot et connecté sans droit vérifiés.
- REST rendu/brut et collections/champs/contexte embarqué; RSS2/RSS/Atom/RDF; extrait automatique; partage; oEmbed et page embed; recherche; aperçu et variantes de page; révisions/contexte édition refusés. XML-RPC désactivé. Aucun corps complet caché par CSS ou JavaScript.
- Exceptions/configuration invalide et numéro absent : extrait. Deux pannes de données ont été réellement provoquées puis restaurées, avec readback exact et retour de la page complète abonnée.
- Cache : privé/no-store/no-cache, sans validateur partagé; anonyme après lecture abonnée, même URL, sans cache-buster. Les objets expurgés sont des clones, pas des écritures dans le cache objet commun.

## Décomptes vérifiés

| Suite | Réussis | Échecs |
|---|---:|---:|
| Runtime PHP WordPress | 30 | 0 |
| HTTP / étanchéité (35 réponses) | 229 | 0 |
| Pannes HTTP réelles et restauration | 29 | 0 |
| Non-régression / intégrité B-00 / HTML B-01 | 120 | 0 |
| Cas unitaires locaux (8 B-00/B-01, 5 C-08) | 13 | 0 |
| Rejeu du seed / absence de doublon | 4 | 0 |
| **Total de contrôles et cas** | **425** | **0** |

`verification-finale.json` agrège les reçus réels, relit les empreintes exactes des **9 fichiers PHP déployés**, inventorie les **16 fichiers source** du lot et vérifie l'absence des mots de passe privés dans les livrables. Les **70 fichiers PHP** des deux bibliothèques closes correspondent exactement au dépôt; aucune modification de celles-ci. Les **41 objets tagués B-00** gardent leur snapshot exact (IDs, contenus, URL et médias).

Fixtures C-08 persistantes, idempotentes : **3 comptes fictifs @example.org, 1 plan Memberships, 2 adhésions, 2 abonnements Subscriptions manuels sans passerelle et 2 articles**. Comptes/données B-00 non remplacés. Identifiants : `C:\Users\Ced\.imagine-demo\c08-identifiants.json`, hors dépôt.

## Fichiers

- `wp/plugins/imagine-site/Paywall.php` (nouveau), `imagine-site.php`, `README.md`.
- `wp/themes/imagine/functions.php` (point de sortie), `parts/paywall-{connexion,abonnement,regularisation,decouverte_epuisee}.php` (nouveaux).
- `wp/outils/demo/c08.py`, `c08-seed.php` (nouveaux; transport B-00 réutilisé sans modification).
- `wp/tests/demo/c08-runtime.php`, `c08-verifier.py`, `c08-faults.py`, `c08-regression.py`, `c08-idempotence.py`, `test_c08_scope.py` (nouveaux).
- `production/C-08/` : références officielles vérifiées, traces RED, reçus finaux, sources anonymes HTTP, `A-VOIR.md`, présent rapport et `PRET`.

## Limites et écarts explicités

- **PDF non sécurisé, hors lot.** Ni découverte complète, ni achat d'un numéro, ni certification du mode lecture, ni cycle réel des impayés ne sont revendiqués. Les blocs sont des textes provisoires.
- Le DNS externe est volontairement indisponible dans cette démo hors ligne. Le vrai vérificateur Robots est appelé; les faux robots ne passent pas. Aucun vrai robot Internet n'est déclaré validé.
- La grâce repose sur une fenêtre explicite de l'objet Subscriptions; `on-hold` seul est fermé. Sa large fenêtre de fixture n'est pas une durée métier choisie. Les états offerts/groupés sont lisibles via les plans Memberships désignés, sans revendiquer un tunnel d'attribution ni Teams.
- Tous les articles natifs doivent avoir leurs métadonnées d'accès; une absence n'est pas une ouverture. Extrait public explicite, plafonné à 320 caractères par défaut, ou texte neutre; pas de découpe automatique du corps réservé.
- Les 2 articles supplémentaires étendent le sommaire T1. Les recettes historiques B-00/B-01 « exactement quatre articles » / « mot de passe => complet » sont devenues obsolètes pour ce site augmenté. Elles n'ont pas été modifiées ni présentées comme vertes. Leur remplacement C-08 vérifie le snapshot original exact et le comportement désormais requis. `construire.py`, son option `--theme-only` et ses chemins sont inchangés; utiliser le rejeu ciblé C-08, pas l'ancienne recette complète pour qualifier ce paywall.
- Incidents corrigés pendant l'exécution : premier passage natif `pending -> on-hold` refusé (transition via active); mot de passe d'un compte rejoué mal haché avec `wp_insert_user` (passage à `wp_update_user` et validation native); méthode REST d'en-tête inexistante (API `set_headers`); message de grâce inadapté à un refus; cas métadonnées entièrement absentes désormais fermé. Deux attentes de tests ont été corrigées après inspection : absence native des articles protégés dans la recherche, et témoin initial identique dans deux fixtures (témoins maintenant distincts).

Aucun Git, aucune voie 1, aucun autre site, aucune licence commerciale, aucune passerelle réelle ni email sortant. Aucun fichier de file/verrou/rapport global n'a été changé.
