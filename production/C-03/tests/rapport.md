# C-03 — bilan des vérifications réellement exécutées

Passage final le **20 novembre 2026**, PHP **8.2.36**, PHPUnit **11.5.58**.
Le conteneur ne servait aucun site et son réseau était détaché pendant tous les tests.

| Suite / contrôle | Résultat réel | Preuves |
|---|---|---|
| C-03 / Robots | **89 tests, 199 assertions, tous réussis** | `final.xml`, suite `Robots` |
| Non-régression C-01 / Numeros | **39 tests, 101 assertions, tous réussis** | `final.xml`, suite `Numeros` |
| `composer test` pilotage, deux suites | **128 tests, 300 assertions**, code 0 | `final.log`, `final.json` |
| Non-régression C-04 | **22 tests, 161 assertions**, code 0 | `c04-regression.log`, `.xml`, `.json` |
| Ensemble des trois suites | **150 tests, 461 assertions**, aucun échec/erreur/ignoré | `artifact-verification.json` |
| PSR-12 src/tests, syntaxe PHP, Composer strict | codes 0, aucun avertissement final | `final-lint.log`, `final-composer-validate.log`, `final.json` |
| PSR-12 et syntaxe de la configuration | codes 0 | `configuration*.log`, `configuration.json` |
| PSR-12, syntaxe, Composer strict C-04 | codes 0 | `c04-regression*.log`, `.json` |
| Sources livrées = sources réellement testées | empreintes SHA-256 et inventaires concordants | `final.json`, `configuration.json`, vérificateur d’artefacts |
| C-01/C-04 protégés | **226 fichiers originaux inchangés** ; les deux fichiers partagés ont seulement les ajouts C-03 attendus | `protected-before.json`, vérificateur d’artefacts |
| Nettoyage | seul conteneur possédé C-03 supprimé, absence relue | `cleanup.json` |

## Ce qui a été exercé

- Agent inconnu sans DNS ; jetons trompeurs et agent annonçant plusieurs robots refusés.
- Configuration initiale Google/Bing chargée sans réseau, identités vérifiées par des réponses fictives.
- Bon UA avec IP quelconque ; PTR absent ; PTR admis mais A/AAAA différent ; domaine suffixé
  frauduleusement, domaine seulement contenu, domaine nu, labels/URL/espaces invalides.
- Point DNS final et casse normalisés, plusieurs PTR et plusieurs A/AAAA, IPv6 sous ses formes équivalentes.
- Pannes inverse/directe, exception de timeout, réponse inverse tardive, budget global non renouvelé
  pour la directe, budget configurable ; aucun `sleep` ni serveur DNS réel.
- CIDR IPv4/IPv6, premiers/derniers hôtes, bits partiels, préfixes /0, /32, /127 et /128,
  famille différente, IPv4-mappée, adresses et préfixes malformés.
- Plages sans DNS, instantané absent/expiré ; le positif en cache ne dépasse pas son expiration.
- Cache positif/négatif, échéance exacte, absence de prolongation à la lecture, timeout négatif,
  séparation par IP/robot/configuration, IPv6 canonique, recul de date, panne lecture/écriture.
- Configuration invalide refusée, objets décision cohérents, dates exposées en Europe/Brussels.
- En-têtes serveur fictifs contradictoires ignorés au profit de l’IP passée en argument.

Les deux déroulés métier (DNS concordant puis inverse falsifié) sont détaillés dans `../notes.md`.
R-27 n’est pas une recette HTTP effectuée sur un site : c’est ici une bibliothèque isolée.
R-26/R-28, le paywall et ses canaux restent entièrement hors de ce lot.

## Exécutions RED → GREEN et incidents conservés

Les reçus `red-agent`, `red-dns-contract`, `red-delais`, `red-cache`, `red-plages`,
`red-validation-full` et `red-fuseau` précèdent l’implémentation des comportements correspondants.
Les erreurs d’API encore absente du premier `red-dns` ont été remplacées comme preuve de
comportement par `red-dns-contract` (15 assertions en échec, sans erreur de chargement).
`green-dns` avait encore une erreur PSR-12 : ce n’est **pas** le passage final.
Ces problèmes ont été corrigés, puis toutes les suites ont réellement été rejouées.

La commande `red-validation` utilisant un filtre avec `|` a échoué avant PHPUnit
(code **127**, interprétation par le transport WSL). Son ancien XML recyclé par le banc
hérité a été **retiré** : seul le reçu/log d’incident est conservé, ce n’est pas une suite.
Le wrapper C-03 refuse désormais ces filtres et efface le précédent JUnit avant chaque
exécution. La commande correcte `red-validation-full` puis le passage final sont conservés.
Le banc partagé C-01 et ses preuves n’ont pas été modifiés.

L’extracteur documentaire automatique était indisponible et une URL Google initiale retournait
404 : lecture officielle récupérée dans le navigateur via la redirection de l’ancienne URL.
Le registre `../sources-officielles.json` distingue les pages consultées des fichiers de plages
simplement référencés. Aucun fichier de plages réelles n’a été testé ou intégré.

## Rejouer et contrôler

Commandes dans `wp/tests/robots-runner/README.md`. Après la fermeture, le contrôle
se rejoue localement, sans Docker ni réseau :

```sh
python wp/tests/robots-runner/check_artifacts.py
```

Il compare les fichiers finaux aux reçus des suites, vérifie les décomptes JUnit,
les inventaires protégés, le nettoyage et les scripts, puis produit
`artifact-verification.json` et `fichiers-livres.json` (liste exacte et empreintes).
Le README pilotage n’a reçu qu’un appendice C-03 ; `phpunit.xml`, qu’une suite Robots.
Le contrôle reconstruit les octets originaux de ces deux fichiers et les compare au départ.

Aucun Git, compte, donnée personnelle, installation hôte, exploitation, DNS de test réel,
WordPress, base, déploiement ou branchement paywall. Les consultations réseau sont limitées
à la documentation publique et à la préparation des outils Composer dans le conteneur autorisé.
La fermeture est vérifiée. Aucun blocage du lot pur restant ; l’adaptateur DNS à délai dur,
le backend cache persistant et la chaîne proxy attendent leur intégration autorisée.
