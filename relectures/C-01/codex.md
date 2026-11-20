# Relecture indépendante Codex — C-01

Date : 20 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, brief C-01, cahier des charges §3.4 à §3.8 et §3.13, décisions et cas R-02, R-16, R-20, R-32, R-34. Périmètre examiné : moteur `Numeros`, tests, fixture, configuration et documentation de la bibliothèque, lanceur et preuves de `production/C-01/`. Le rapport Claude n'a pas été consulté. Aucun fichier autre que ce rapport n'a été modifié.

## 1. Conformité

Les livrables demandés sont présents. Le moteur est indépendant de WordPress et de WooCommerce ; calendrier, projections papier, renouvellement, activation numérique, suspension, échéances et restants ont une API dédiée. Les quatre interprétations imposées par le brief sont isolées et déclarées dans les notes. Les choix complémentaires concernant la réception théorique, les échéances dépassées et la suspension sont également signalés ; aucun prélèvement n'est exécuté.

**C01-01 — Mineur — Traçabilité des règles incomplète.**

- **Fichier et ligne :** `wp/plugins/imagine-pilotage/src/Numeros/Moteur.php:15`.
- **Problème :** les méthodes métier ne renvoient pas aux paragraphes qu'elles appliquent. Les descriptions de l'API et les notes ne fournissent pas non plus de correspondance règle → paragraphe → test. Cela complique notamment la distinction entre droits contractuels, état à la clôture et interprétations provisoires.
- **Correction proposée :** ajouter des références précises aux méthodes ou une table de correspondance : papier et renouvellement (§3.5), échéances (§3.4–3.6), restants (§3.7), suspension (§3.8), droits figés (§3.13). Identifier séparément les interprétations du brief.

## 2. Exactitude métier

### Deux déroulés manuels du cahier des charges

1. **Commande et activation le 8 octobre 2026.** Dans la fixture, le n° 170 est sorti le 5 octobre après clôture le 20 septembre. Le premier régulier ouvert est le 171, clôturé le 20 décembre 2026 ; les quatre sélectionnés sont 171, 172, 173 et 174. Le premier hors-série encore ouvert est HS-2027. Une activation le 8 octobre ouvre le numérique immédiatement, avec fin exclusive le 8 octobre 2027 à la même heure. Le code concorde avec l'exemple du §3.5 et les assertions existantes.
2. **Renouvellement le 8 octobre 2027.** Le dernier numéro précédent est 174 ; la branche de renouvellement prend les quatre suivants : 175, 176, 177 et 178. HS-2027 est fermé ; HS-2028 est retenu. Le résultat concorde avec le second exemple du §3.5 et le test de renouvellement.

Les bornes ordinaires sont cohérentes : commande le 19 septembre 2026 → 170 ; le 20 ou le 21 septembre → 171 ; le 20 décembre → 172. Un calendrier limité au 171 conserve trois réguliers non résolus ; son renouvellement reste non résolu jusqu'à connaissance du quatrième précédent. Une suspension du 10 janvier au 1er avril 2027 exclut le 172, clôturé le 20 mars, sans effacer le droit historique au 171. Ces conclusions proviennent de la lecture du code, sans exécution PHP indépendante.

**C01-02 — Important — Des clôtures dans un ordre différent des sorties produisent quatre numéros non consécutifs.**

- **Fichier et ligne :** `wp/plugins/imagine-pilotage/src/Numeros/Moteur.php:98`.
- **Problème :** le filtre retire tous les réguliers déjà clôturés avant de prendre les quatre premiers. Or le calendrier n'impose pas que les clôtures suivent l'ordre des sorties, et sa méthode de modification permet de créer cette situation. Exemple à partir de la fixture : le 1er décembre 2026, avancer la clôture du 172 au 15 décembre 2026, sans changer sa sortie du 5 avril 2027. Cette modification est acceptée : les clôtures ancienne et nouvelle sont futures, le type et le rang de sortie restent identiques. Une commande le 16 décembre obtient alors **171, 173, 174, 175**, avec `nonResolus() === 0`. Le 172 est silencieusement sauté, contrairement aux quatre réguliers consécutifs exigés par le brief ; le dernier numéro et les échéances se décalent aussi.
- **Correction proposée :** sélectionner la séquence contractuelle à partir du premier régulier ouvert, sans supprimer silencieusement un numéro intermédiaire. Définir et contrôler la cohérence des clôtures lors de la construction et de la modification du calendrier ; si une séquence ne peut pas être servie, la signaler explicitement au lieu de substituer un cinquième numéro. Ajouter un test de cette modification suivie d'une commande entre les deux clôtures, portant sur la séquence, le dernier numéro et les échéances.

**C01-03 — Important — Une activation le 29 février empêche tout accès numérique actif, dès le paiement.**

- **Fichier et ligne :** `wp/plugins/imagine-pilotage/src/Numeros/Moteur.php:22`.
- **Problème :** pour une année ouverte et activée le 29 février 2028 à 12 h, `accesNumerique()` appelé à ce même instant trouve l'année active, puis appelle `finNumerique()`, qui lève systématiquement une exception pour cette date d'ouverture. Le problème persiste le lendemain et pendant toute la période active. L'arbitrage sur le 28 février ou le 1er mars est bien déclaré dans les notes, mais l'incertitude sur la fin ne justifie pas de rendre impossible l'ouverture immédiate prescrite par le §3.5. Le test existant vérifie seulement que le calcul de fin lève une exception.
- **Correction proposée :** dissocier l'ouverture immédiate du calcul de l'anniversaire litigieux et prévoir une politique de fin explicite, soumise à Ced. Préserver le droit pendant la période incontestablement couverte, sans choisir ici entre les deux anniversaires. Ajouter des tests par l'API `accesNumerique()` à l'instant du paiement, le lendemain, pendant une suspension et aux bornes de fin après arbitrage.

Le rejeu d'une activation ou d'une suspension sur l'objet résultant est refusé par exception, sans ajout de transition. Ce comportement est testé et ne constitue pas une idempotence silencieuse ; son traitement relève du futur adaptateur. L'idempotence de la file Odoo n'appartient pas à ce lot.

## 3. Tests

**Tests non relancés pendant cette relecture.** Le prérequis d'accès au conteneur a été tenté par la commande suivante :

```text
wsl.exe -d Ubuntu -- docker image inspect imagine-staging-e2e-public:644662e9cc4f --format '{{.Id}}'
```

Résultat : code de sortie 1, accès refusé, `Wsl/Service/E_ACCESSDENIED`. PHPUnit n'a donc pas démarré. Aucun outil n'a été installé sur Windows et aucun site ou compte n'a été utilisé. Le lanceur n'a pas été exécuté directement : il réécrit notamment `composer.lock` et les preuves dans `production/C-01/tests/`, ce que la consigne de cette relecture interdit.

La preuve antérieure `production/C-01/tests/final.xml` annonce **39 tests, 101 assertions, zéro erreur, échec ou test ignoré** ; le reçu situe ce passage au 20 novembre 2026 à 14:28:39 UTC, sous PHP 8.2.36. C'est un résultat fourni par la production, pas un résultat obtenu par ce relecteur.

La comparaison SHA-256 en lecture seule confirme l'identité des sept fichiers du moteur, des deux fichiers de tests et de la fixture avec ce reçu. `composer.json`, `composer.lock`, le README et le lanceur correspondent également. **`phpunit.xml` diffère** : la configuration actuelle comprend aussi la suite `Robots`, absente du JUnit C-01 enregistré. La preuve historique étaye donc les sources C-01 examinées, sans certifier l'actuel `composer test` complet.

La couverture comporte les exemples exacts, les jours autour des clôtures, UTC/Bruxelles, décembre/janvier, calendrier incomplet, activation tardive, suspension/réactivation, modification future, marges variables et changement d'heure. Plusieurs assertions utilisent des résultats métier littéraux : elles ne se contentent pas de répéter l'algorithme. Les scénarios manquants et leurs résultats attendus sont précisés dans C01-02 et C01-03. Après correction, rejouer au minimum `composer test -- --testsuite Numeros` dans le conteneur autorisé, puis les contrôles prescrits du lot.

## 4. Sécurité et données

Aucun secret ni donnée réelle identifié dans les fichiers C-01 examinés. La fixture ne contient que des parutions fictives. Le moteur ne fait aucun accès réseau, aucune requête SQL et aucune sortie HTML ; il n'expose pas d'entrée WordPress. Droits administratifs, nonces, échappement, requêtes préparées et étanchéité du paywall ne sont donc pas évaluables dans cette bibliothèque pure. L'événement `Activation` n'est pas une preuve de paiement : cette frontière est explicitement documentée.

## 5. Doctrine

La séparation métier/WordPress, les types stricts, les objets `readonly`, les dates immuables et le fuseau Bruxelles sont respectés à la lecture. Aucun appel à l'horloge courante n'est présent dans le moteur. Les vérifications PSR-12 et syntaxiques sont annoncées réussies dans le reçu antérieur ; elles n'ont pas été réexécutées ici.

La commande d'un moteur autonome correspond au périmètre explicite de C-01. La couverture native des extensions est expressément renvoyée à A-00 dans `production/C-01/notes.md:78` ; ce lot seul ne démontre donc pas cette étude préalable. Aucune conclusion de redondance avec une extension n'est avancée dans cette relecture.

Le marqueur `PRET` se présente comme une invitation à relire, pas comme une validation. Son existence ne remplace ni les corrections ci-dessus ni les arbitrages ouverts. Il n'a pas été modifié.

## 6. Études (lots sans code)

Sans objet : C-01 est un lot de code. Aucune affirmation nouvelle sur les capacités d'une extension tierce n'est formulée ici.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun point classé dans cette catégorie.
- **Important : C01-02**, sélection non consécutive lorsque les clôtures changent d'ordre.
- **Important : C01-03**, exception empêchant l'accès numérique dès une activation le 29 février.
- **Mineur : C01-01**, références métier à compléter.

Limite de validation : exécution indépendante des tests empêchée par le refus d'accès WSL ; résultats antérieurs et correspondance des sources contrôlés en lecture seule.
