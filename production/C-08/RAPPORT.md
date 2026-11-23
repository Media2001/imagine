# C-08 — Corrections appliquées, preuves actuelles

**Fait :** bloquant recherche fermé côté SQL sans mot de passe natif ; corrections C08-01/02/03, mémoïsation et repli Woo vérifiés.
**Prêt à relire :** C08 sur le seul `imagine-test-demo`, suivant les arbitrages du 23 novembre 2026, section C08 17 h 10.
**À valider :** visuel provisoire des blocs par Ced, aucune nouvelle règle financière ou de droits choisie.
**Bloqué :** aucun blocage résiduel sur les critères C08 exercés.
**Suite :** retour au parent ; aucun verrou, rapport global, Git, docs/corrections ni code d'un autre lot modifié.

## Résultats de la recette canonique exécutée

| Suite | Réussis | Échecs |
|---|---:|---:|
| PHP WordPress historique C08, avec les canaris de panne dans le même processus | 30 | 0 |
| PHP corrections : recherche, booléens natifs/REST, mémoïsation, invalidations, instant | 28 | 0 |
| Banc isolé mappage des droits et appel réel du moteur C06 | 19 | 0 |
| Processus sans Woo + repli du corps sans adaptateur | 7 | 0 |
| Unitaires Python locaux : découverte actuelle 31 + 2 corrections B01 | 33 | 0 |
| Écritures REST **HTTP** false / true / clé retirée / false rétabli, anonymes et nettoyage | 23 | 0 |
| Pannes de plans et numéro, page/REST/flux/oEmbed/recherche, restauration relue | 41 | 0 |
| Idempotence réelle du seed C08 | 4 | 0 |
| HTTP : page/REST/RSS/Atom/RDF/recherche/partage/aperçu/robots/cache | 299 | 0 |
| Non-régression B00 / URL / HTML B01 / bibliothèques closes | 120 | 0 |
| Conservation inter-lots, absence de canari/secret et readback final | 17 | 0 |
| **Total de contrôles et cas de cette recette** | **621** | **0** |

Reçu faisant foi : `verification-finale.json`, statut `VERIFIED`. Les assertions d'une réponse ne sont pas des parcours indépendants. **56 réponses HTTP** sont inventoriées par la suite d'étanchéité principale, en plus des réponses des suites REST écriture et pannes. Aucun test ignoré. Les **13 fichiers PHP déployés** ont été parsés et leurs octets relus après tous les rejeux ; **22 sources** liées par SHA-256. Les **71 fichiers PHP** des bibliothèques `src` correspondent au dépôt.

Commande réelle : environnement neuf hors dépôt `C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-c08-venv`, installation `pip --no-index --find-links production/B-01/validation -r production/B-01/validation/requirements.lock`, puis `python wp/tests/demo/c08-final.py`. Les six wheels B01 ont été réutilisés sans modification. `local-tests.json` inventorie les paquets et empreintes ; aucun second packaging HTML.

## Correction par correction

- **Recherche bloquante :** le test RED a effectivement retrouvé l'article anonyme par sa phrase de corps, avec `post_password` déjà vide après B00. `posts_search` masque maintenant le corps des articles non complets avant appariement ; `posts_orderby` applique la même garde au classement. L'anonyme trouve encore le titre et l'extrait publics, jamais l'article par sa phrase cachée. L'actif et la grâce le trouvent par cette phrase ; le sans-droit non. Recettes HTML, REST posts et REST search, phrase et mots, exclusion et termes contenant apostrophe/identifiant SQL. La réflexion du terme saisi dans l'en-tête HTML n'est pas traitée comme une fuite : les IDs/cartes font oracle.
- **Booléen :** présence de clé vérifiée séparément. `false` natif stocké vide ouvre l'article paru valide ; `true` réserve ; clé absente/valeur invalide ferme. Les chaînes historiques 0/1 restent compatibles. Écritures via `rest_do_request` **et via HTTP réellement authentifié**, refus anonyme, readback de stockage et lecture publique à chaque transition.
- **JSON-LD :** `NewsArticle`, propriétés du paywall conservées, jamais `articleBody` ni phrase du corps dans le partage.
- **Mémoïsation :** `(site, post, utilisateur)` en mémoire PHP de la requête uniquement. Un instant UTC commun à la seconde pour toutes les couches. Les tests comptent l'absence de relecture au second appel et gardent le même instant après attente/invalidation. Mutations natives de métadonnées/options et changements de filtres de lecture invalident les anciens résultats. Les canaris historiques de configuration/exception/date/statut continuent à s'exécuter dans un même processus et passent ; pas de fail-open pour rendre la suite verte.
- **Droits :** banc avec doublures locales au namespace de l'adaptateur, sans altérer les profils natifs ; états suspendu, expiré, virement non validé, on-hold sans fenêtre, paused sans abonnement, administration/rédaction, propriétaire incohérent. Le moteur C06 reste réel. Les doublures hors hooks invalident explicitement leur mémoire de banc ; elles ne sont pas présentées comme la preuve de l'invalidation native, assurée par les autres tests.
- **Woo absent :** `function_exists('wc_get_page_permalink')` avec repli connexion. Test dans un processus `--skip-plugins --skip-themes`, aucune désactivation persistante. Après retrait B00 des mots de passe, le repli du corps du thème sans adaptateur avait aussi été ouvert : test RED, puis fermeture par extrait public ou phrase neutre au seul point de sortie autorisé.
- **Anciens oracles :** les recettes B00/B01 corrigées avaient déjà retiré les cardinalités globales et autorisations par mot de passe. Aucune réédition de leurs sources. La régression C08 compare le snapshot original avec la seule migration autorisée des drapeaux `protected` des articles ; tous les autres IDs/textes/médias/métadonnées restent comparés. Pas de remplacement d'un oracle de sécurité par un simple nombre.

## Conservation et fichiers

Conservation exacte de la projection originale **C09 : 27 comptes, 13 commandes, 12 abonnements, 14 adhésions**, avec IDs/dates/états/droits ; les décisions des 27 profils restent identiques, y compris **A-VIR**, non réarbitré ici. Bibliothèques et bootstrap C10 actifs, réglages et journal identiques. `NumeroPublication.php` et `imagine-site.php` sont identiques aux empreintes B01 corrigées. Les autres sources B01 sont inchangées hors les deux raccords C08 explicitement permis. Les fichiers privés enrichis B00 et C08 sont inchangés en octets pendant la recette finale.

C08 garde **2 articles (81/82), 3 comptes, 1 plan, 2 adhésions, 2 abonnements manuels sans passerelle**. Le rejeu conserve IDs, corps, numéros, dates métier, états et grâce dans son état comparé. Les projections intégrales C08 utilisateurs/abonnements ne sont pas promises byte-identiques après connexions et seed : leurs empreintes changent et sont déclarées dans le reçu ; cela n'est pas masqué par un nouveau baseline. Tous les articles temporaires sont supprimés. Accueil final : **82,81,45,44,43**, dans sa section d'articles ; le dernier numéro est une carte distincte.

Sources modifiées :
- `wp/plugins/imagine-site/Paywall.php`, `README.md` ; aucun changement de `NumeroPublication.php` ni du bootstrap B01.
- `wp/themes/imagine/functions.php` : seul repli du point de sortie du corps ; `parts/paywall-regularisation.php` : garde Woo.
- `wp/outils/demo/c08-seed.php` : mot de passe natif vide et pas de rehash inutile d'un secret correct.
- `wp/tests/demo/c08-verifier.py`, `c08-faults.py`, `c08-regression.py`.

Sources nouvelles : `c08-corrections-runtime.php`, `c08-rights.php`, `c08-no-woo.php`, `c08-rest-write.py`, `c08-final.py` sous `wp/tests/demo/`. Le transport B00 est réutilisé, pas modifié. Preuves actuelles, traces RED et références officielles sous `production/C-08/` ; anciennes preuves sous `historique/pre-corrections-17h10/`.

## Limites et reports pour le parent / Claude

- Interdiction documentée de `echo get_post($id)->post_content` : le cache objet conserve volontairement la source. Les sorties futures doivent utiliser l'adaptateur et les hooks ; pas de recherche publique avec `suppress_filters=true` ni SQL brut hors garde.
- En-têtes `private/no-store` et `DONOTCACHEPAGE` encore **provisoirement larges**, même sur pages ouvertes ; stratégie de cache distinguant anonyme/connecté et cache d'hébergement à traiter dans son lot. L'inventaire SQL des IDs de cette petite démo n'est pas une preuve de performance sur une volumétrie de production.
- Les réglages `Acces\Reglages` de C10 ne sont **pas raccordés** par C08 ; moteur sur valeurs par défaut. Ne pas prétendre les réglages futur/PDF/découverte actifs. Seuls plans/extrait sont lus par l'adaptateur.
- Vrai robot Internet R27 non démontré hors ligne, DNS volontairement indisponible. PDF, découverte/achat complets, tunnel, mode lecture spécifique, performances/WCAG exhaustives et design final hors lot.
- Le plugin doit rester actif pour ses gardes REST/recherche/flux. La fermeture du corps du thème **sans adaptateur** n'est pas une certification de toutes les API après désactivation totale du plugin.
- Les défauts de développement détectés et corrigés incluaient l'instant avec microsecondes rejeté par le moteur clos (retour au contrat à la seconde), et un sélecteur d'oracle comptant initialement aussi la carte numéro comme article (recentré sur la section article, sans modifier les IDs attendus). Traces RED conservées ; recette complète rejouée après la dernière correction.

Aucun écart restant de recherche à reporter comme non corrigé. À reporter dans les documents globaux par leur propriétaire : cache provisoire, raccord des réglages moteur, robot Internet non prouvé et limites ci-dessus. `docs/`, `corrections/`, file, verrou et rapports globaux n'ont pas été écrits. **PRET n'est pas un GO production.**
