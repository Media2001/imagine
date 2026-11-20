# C-03 — vérification défensive de l’identité des robots

**Livraison à relire, sans GO ni branchement sur un site.** Référence :
`briefs/C-03-verification-robots.md`, cahier des charges §3.9 et §4.4.
Aucune règle d’abonnement ou de restitution de contenu n’est ajoutée.
R-27 est servi par la bibliothèque ; R-26/R-28 restent des recettes d’intégration
ultérieures. Aucun cas de `docs/recette/` n’a été automatisé ou modifié.

## Ce qui est livré

`wp/plugins/imagine-pilotage/src/Robots/` : objets métier immuables PHP 8.2,
interfaces `Dns`, `Cache`, `HorlogeMonotone`, moteur `Verificateur`, contrôle
CIDR `Plage`, motifs explicites et cache mémoire de démonstration.
`tests/Robots/` : DNS et temps exclusivement simulés, sans attente réelle.
`config/robots.php` : **proposition** Googlebot et Bingbot en méthode DNS,
pas une activation WordPress. Tous les paramètres sont hors du moteur.
Le cache mémoire est volontairement mutable : c’est un adaptateur, non un objet
métier. Il est limité à la vie de son instance ; ce n’est pas le backend de production.

API centrale :

```php
$decision = $verificateur->verifier($agentUtilisateur, $ipValidee, $dateObservation);
$decision->estVerifie(); // bool
$decision->robot;       // identifiant configuré si vérifié, null sinon
$decision->motif;       // enum Motif, avec une valeur textuelle stable
```

Le constructeur reçoit configuration, DNS, cache et horloge monotone. La date
murale est un `DateTimeImmutable` fourni par l’appelant ; les dates exposées par
les objets sont en `Europe/Brussels`. Aucun `now`, `time`, `hrtime`, en-tête HTTP,
variable serveur, fonction WordPress, client HTTP ou DNS natif dans le moteur.

## Décision et fermeture par défaut

1. Le jeton HTTP du robot doit correspondre à la configuration. L’UA est une
   **candidature**, jamais une preuve. `NotGooglebot`, `GooglebotFake` et
   `Googlebot-Image` ne deviennent pas `Googlebot`. Un UA inconnu ou annonçant
   plusieurs robots configurés est refusé avant tout DNS/cache.
2. L’argument IP doit être une seule adresse valide, sans port, zone IPv6 ou
   liste de proxy. IPv6 est comparé en binaire ; ses écritures équivalentes
   partagent la même clé. Une IPv6 IPv4-mappée ne devient pas implicitement IPv4.
3. En méthode **DNS** : PTR, nom DNS ASCII valide sous un suffixe autorisé
   précédé d’un point, puis A/AAAA qui contient exactement l’IP d’entrée.
   Le domaine nu n’est pas un hôte de robot. Majuscules et un point DNS terminal
   sont acceptés ; faux suffixe, joker, espace, URL et labels invalides ne le sont pas.
   Plusieurs PTR/adresses peuvent être examinés, toujours avec le même budget.
4. En méthode **Plages** : appartenance CIDR IPv4/IPv6, sans DNS. Les chaînes
   sont validées/compilées à la construction. L’appelant doit fournir une date
   d’expiration de l’instantané ; absente ou atteinte, la réponse reste négative.
   Aucun préfixe réel n’est embarqué. Les préfixes des tests sont fictifs.
5. Il n’existe **aucun repli automatique** entre les méthodes. Une exception,
   un délai dépassé ou un cache indisponible ne produit jamais un résultat positif.
   Une configuration incohérente est refusée par exception à la construction :
   l’intégrateur devra la traiter comme indisponible, jamais comme une permission.

Motifs négatifs : `agent_inconnu`, `agent_ambigu`, `ip_invalide`,
`domaine_refuse`, `adresse_differente`, `dns_impossible`, `delai_depasse`,
`plage_absente`, `plages_expirees`, `cache_indisponible`.
Les seuls motifs positifs sont `verifie_dns` et `verifie_plage`.

### Délai : garantie du cœur et limite volontaire

Budget proposé : **200 ms pour toute la séquence DNS**, pas 200 ms par appel.
Le temps restant est transmis au résolveur injecté et contrôlé après chaque
retour ; une réponse concordante mais arrivée à l’échéance est refusée.
`DelaiDnsDepasse` permet au résolveur de signaler lui-même son expiration.

**Ce cœur synchrone ne peut pas interrompre un adaptateur qui ne rend jamais
la main.** Le futur adaptateur devra garantir un délai dur/annulation pour PTR,
A et AAAA. Il n’est pas livré ici afin de ne faire aucun appel réseau réel.
Un simple `gethostbyaddr()` ou `dns_get_record()` suivi d’un chronomètre ne
suffit pas : leurs signatures documentées n’offrent pas ce paramètre [P1, P2].
La garantie testée est celle du moteur avec un résolveur simulé conforme ;
aucune latence d’un serveur DNS réel n’a été mesurée.

## Cache et réglages proposés, pas validés

| Paramètre | Proposition | Rôle |
|---|---:|---|
| `ttlPositif` | 3 600 s | Durée maximale d’une identité vérifiée |
| `ttlNegatif` | 60 s | Refaire plus vite une tentative refusée, y compris un timeout |
| `delaiDnsMs` | 200 ms | Budget total PTR + A/AAAA |

Les durées doivent être strictement positives et le négatif plus court que le
positif. Pas d’expiration glissante : une lecture ne prolonge rien. L’expiration
est exclusive et un résultat provenant du futur n’est pas utilisé.
Un positif CIDR n’est jamais conservé au-delà de la validité des plages.

« Par IP » signifie ici **IP canonique + identité candidate + empreinte de la
configuration complète + version de politique**. Une clé contenant seulement
l’IP permettrait de transférer une vérification Google à Bing ou à un navigateur.
UA inconnu/ambigu et IP invalide ne nécessitent pas de cache : leur refus local
est immédiat et ne doit pas empoisonner une vérification ultérieure.
L’interface reçoit une entrée immuable avec création/expiration ; le moteur
vérifie les dates. Le backend doit être de confiance, inaccessible aux visiteurs,
avec sa propre politique d’éviction/limitation de mémoire. Aucune IP n’est écrite
dans un journal par la bibliothèque ; le hash de clé n’est pas une anonymisation.

## Sources officielles et configuration initiale

Le registre `sources-officielles.json` donne les URLs consultées le **20/11/2026**,
une courte citation et le constat associé. Les fichiers de plages n’ont pas été
récupérés ; leurs sources sont les liens donnés par ces pages.

- **Googlebot** : `googlebot.com`, incluant ses sous-domaines tels que
  `geo.googlebot.com`. La documentation distingue les robots communs des
  robots spéciaux et extractions à la demande [G1, G2]. On n’élargit donc pas
  cette proposition à tout `google.com` ou `googleusercontent.com`.
  Documentation : https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests
  et https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers .
  Source CIDR liée : https://developers.google.com/static/crawling/ipranges/common-crawlers.json .
  Ne pas utiliser la liste générale de toutes les adresses Google.
- **Bingbot** : `search.msn.com`, inverse puis directe concordante [B1].
  Documentation : https://www.bing.com/webmasters/help/how-to-verify-bingbot-3905dc26 .
  Source CIDR liée : https://www.bing.com/toolbox/bingbot.json . L’exploitant demande
  de rafraîchir la liste chaque jour ; aucune ancienne liste figée n’est activée.

Pour employer les plages, un futur composant extérieur au moteur devra récupérer
uniquement la source officielle, contrôler le format et la provenance, remplacer
atomiquement un instantané complet et fournir son expiration. Une récupération
échouée ne renouvelle pas la validité de l’ancien instantané. L’expiration locale
et la cadence Google restent à fixer lors de cette intégration ; ce lot ne
prétend ni actualiser les listes ni démontrer leur fraîcheur.

### Le standard d’abord

L’étude A-00 a été consultée, sans modifier sa conclusion ni ses preuves.
La page officielle Memberships décrit les restrictions par adhésion et les
extraits pour visiteurs/moteurs [W1] :
https://woocommerce.com/document/woocommerce-memberships-settings/ .
Elle ne démontre pas une API qui vérifie l’identité Google/Bing par FCrDNS/CIDR.
C-03 se borne à cette lacune identifiée et demandée par le brief : il ne refait
ni les adhésions natives, ni le rendu, ni un générateur de schéma SEO.

### Robots à proposer au référenceur, non activés

| Robot | Méthode officiellement publiée | Documentation |
|---|---|---|
| Applebot | Domaine `applebot.apple.com`, correspondance d’IP, ou CIDR | https://support.apple.com/en-us/119829 [A1] |
| DuckDuckBot | Liste d’IP publiée | https://duckduckgo.com/duckduckgo-help-pages/results/duckduckbot [D1] |
| YandexBot | Inverse, suffixes `yandex.ru`, `yandex.net`, `yandex.com`, directe concordante | https://yandex.com/support/webmaster/en/robot-workings/check-yandex-robots [Y1] |

Cette liste n’est pas exhaustive et ne constitue pas une autorisation. Les
agents Google Image/Video/Inspection/Other ne sont pas ajoutés implicitement.
Les règles d’indexation et d’usage IA restent distinctes et hors de ce lot.

## Adresse du visiteur derrière un répartiteur

Le moteur ne lit **jamais** `X-Forwarded-For`, `Forwarded` ou `REMOTE_ADDR`.
Une chaîne fournie par Internet peut être forgée. Elle ne devient digne de
confiance que si la connexion qui l’apporte vient d’un répartiteur explicitement
approuvé et que celui-ci supprime/remplace les valeurs clientes non fiables.
Prendre aveuglément la première IP de `X-Forwarded-For` est interdit.

Avec l’hébergeur, avant tout branchement :

1. Inventorier les IP/CIDR exacts des proxies/CDN autorisés et toute la chaîne.
2. Verrouiller l’accès direct à l’origine quand l’architecture le permet ; une
   requête directe non approuvée ne doit pas imposer son en-tête IP.
3. Faire normaliser l’IP à la couche serveur, en ne remontant que la chaîne de
   proxies connus. Nginx documente `set_real_ip_from`, `real_ip_header` et
   `real_ip_recursive` [N1] : https://nginx.org/en/docs/http/ngx_http_realip_module.html .
   Ce sont des pistes de réglage, pas une configuration appliquée à un hébergeur inconnu.
4. Fournir à C-03 **une seule IP normalisée**, traiter les ambiguïtés par refus,
   puis recetter en environnement autorisé le proxy connu, l’origine directe,
   les chaînes multiples et les en-têtes forgés. Ne pas tester ces voies ici.

Le test unitaire fournit des en-têtes fictifs contradictoires : seule l’IP
passée en argument est utilisée. Ce n’est pas une validation réseau de l’hébergement.

## Deux cas déroulés et portée des preuves

- UA `Googlebot/2.1`, IP fictive `192.0.2.1`, PTR
  `crawl-fictif.googlebot.com`, A `192.0.2.1` : **vérifié, google, verifie_dns**.
- Même UA/IP/PTR, mais A `192.0.2.2` : **non vérifié, robot null,
  adresse_differente**. Le PTR seul n’ouvre donc pas l’accès.

Ces chemins, faux suffixes, IPv6, CIDR, pannes, délais, caches, configuration
initiale et absence de lecture d’en-têtes sont exercés par PHPUnit.
Le bilan réel et les empreintes sont dans `tests/rapport.md`, `tests/final.*`
et `tests/artifact-verification.json`. C-01 est rejoué dans `composer test` ;
C-04 est rejoué dans un sous-dossier isolé du runner C-03, sans modifier ses sources.
Le lanceur ne touche ni aux preuves ni aux runners C-01/C-04.

## À arbitrer par Ced avant l’intégration

1. Confirmer les propositions **3 600 s / 60 s / 200 ms** ? (`config/robots.php`)
2. Faire valider par le référenceur **Googlebot et Bingbot seulement**, sans
   agents Google spécialisés ni autres robots à ce stade ?
3. Valider la méthode DNS proposée avant d’implémenter son adaptateur à délai dur,
   ou choisir explicitement des instantanés CIDR avec leur politique de fraîcheur ?
4. Faire confirmer par l’hébergeur les répartiteurs de confiance et la restitution
   de l’IP avant tout branchement ?

**Rien n’est déployé.** Les adaptateurs réseau/cache persistant, l’extraction IP,
le paywall, les caches de pages et l’étanchéité HTML/REST/flux/oEmbed/recherche/PDF
restent dans leurs lots ultérieurs. `PRET` veut uniquement dire « prêt à relire ».
