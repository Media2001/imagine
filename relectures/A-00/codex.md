# Relecture indépendante Codex — lot A-00

Date : 20 novembre 2026. Périmètre : brief A-00, production documentaire A-00, paragraphes cités du cahier des charges, décisions et preuves locales pertinentes dans `wp/`.

Relecture effectuée selon `relecteurs/AGENTS.md`, la doctrine et la grille. Aucun accès à un site, une base ou un compte ; aucune installation. Le rapport Claude n'a pas été consulté. Seul ce fichier est écrit.

## 1. Conformité

Les 19 besoins figurent dans la synthèse et dans des sections distinctes. Les références métier, modules et éditeurs, adaptations et questions fermées sont présents. La conservation des abonnements en ligne respecte la décision du 11 novembre. Les limites d'A-01 sont explicitement distinguées d'une recette de paiement ou de paywall.

**C1 — important — `production/A-00/couverture-extensions.md:371` — L'écart entre le brief et le cahier des charges sur carte → SEPA n'est pas identifié comme tel.**

La question « maintient-on le prélèvement SEPA obligatoire après une première carte ? » présuppose une obligation existante. Or le §3.6 réserve expressément le mandat pour les échéances suivantes à Bancontact (`docs/cahier-des-charges-v3.1.txt:539`, notamment « Bancontact ne sert qu'au premier paiement »). C'est le besoin 3 du brief qui étend cette formulation à la carte. Aucune décision lue ne tranche cette extension. Le conditionnel de la section 3 évite de décider le développement, mais n'explique pas à Ced l'origine de l'écart et présente la carte récurrente comme une concession à autoriser.

**Correction proposée :** signaler explicitement la divergence brief/§3.6, avec les deux formulations, puis demander si Ced souhaite ajouter l'exigence carte → SEPA. Conserver la qualification documentaire de chaque parcours sans attribuer cette extension au cahier des charges. C'est un arbitrage de périmètre financier, conformément aux §1 et §6 de la doctrine.

## 2. Exactitude métier

Deux cas du §3.5 ont été déroulés sur papier ; les résultats ci-dessous sont ceux du cahier des charges, pas ceux d'une extension exécutée :

| Cas | Résultat attendu | Comparaison avec l'étude |
|---|---|---|
| Commande le 8 octobre 2026, dans le cas fourni après le n°170 | Numérique immédiat incluant le n°170 après paiement/mandat ; papier 171 à 174 ; hors-série été 2027 ; numérique de date à date | La séparation engagement, créances, papier et numérique à la ligne 92 est cohérente. Le simple réglage trimestriel ne prouve ni cette attribution ni quatre seules charges. L'étude ne le prétend pas. |
| Reconduction en octobre 2027 du même abonnement | Papier 175 à 178 et hors-série été 2028 ; nouvelle année numérique ; nouvelle série de quatre fractions si ce mode est conservé | La ligne 88 distingue correctement expiration et reconduction. La règle de facturation à la jonction des années reste explicitement ouverte ; aucune recette de ce cycle n'est fournie. |

Le contre-exemple fictif de la ligne 90 est arithmétiquement correct : 20 février, 10 avril, 10 juillet, 10 octobre 2027 et 10 janvier 2028 font cinq charges avant le 20 février 2028. Il démontre le défaut d'une cadence appliquée sans décompte ; il ne choisit pas quelle échéance correspond au numéro déjà financé par le paiement initial.

Cas limites examinés : le changement d'année ne remet pas à zéro les quatre fractions de l'engagement ; une commande exactement à la clôture, un calendrier incomplet et un événement de paiement rejoué n'ont pas de résultat fonctionnel démontré dans ce lot documentaire. Ils restent à couvrir lors du branchement, sans inventer ici une convention d'heure ou un calendrier Imagine.

**C2 — important — `production/A-00/couverture-extensions.md:377` — Le périmètre de la grâce reste ambigu face aux autres règles de retrait d'accès.**

La question confirme globalement le maintien des droits jusqu'à la fin de grâce. Pourtant la section 4, ligne 120, prévoit le retrait sur rejet après accès anticipé SEPA ; le §3.6 dit également « retiré en cas de rejet ». Le §3.8 ouvre une grâce sur paiement échoué, tandis que le §3.13 prévoit la fermeture lorsqu'un paiement n'est pas validé à la date prévue. L'étude reprend ces règles sans signaler leur articulation non définie. Exemple : un premier mandat ouvre les droits, puis son prélèvement est rejeté ; le lecteur ne peut déterminer si le retrait doit être immédiat ou différé. Le même doute existe pour une échéance manuelle non validée.

**Correction proposée :** identifier cette ambiguïté du cahier des charges et demander un arbitrage fermé sur l'application de la grâce au premier rejet SEPA et aux paiements manuels non validés. Distinguer ces situations de l'échec d'un renouvellement automatique. Répercuter la réponse dans les besoins 4, 6 et 15 avant toute règle d'accès ; ne pas choisir la priorité à la place de Ced.

## 3. Tests

Le brief A-00 ne prescrit aucune commande de test et demande une étude sans code. Aucun test fonctionnel d'extension n'a été lancé. Les tests A-01 n'ont pas été rejoués : ils relèvent d'un autre lot et leur lanceur crée des artefacts, incompatibles avec l'écriture limitée à ce rapport.

Contrôles locaux effectués en lecture seule :

- Les SHA-256 et tailles des cinq artefacts référencés dans `verification.json` correspondent aux fichiers présents.
- L'empreinte de `verification.json` correspond à celle de `PRET`.
- Le reçu A-01 `e49f54c5e931/result.json` a l'empreinte annoncée et contient 104 entrées `PASS`, 4 `OBSERVED`.
- Le fichier A-00 contient bien 253 entrées déclarées `REUSSI`. Ce décompte ne constitue pas le rejeu des 253 contrôles.

La lecture de `wp/tests/licensed-a01/cases.php` confirme des adhésions autonomes, des contrôles API/shortcode et un renouvellement manuel témoin. Elle ne démontre pas les parcours financiers, l'attribution automatique des droits ou l'étanchéité HTTP. La présentation de ces limites dans l'étude est correcte.

La règle générale de doctrine « un lot sans tests n'est pas PRET » et le brief d'étude sont à lire avec cette portée précise : seuls des contrôles documentaires sont attestés ici. Le marqueur ne permet aucune conclusion de recette fonctionnelle.

## 4. Sécurité et données

Aucun secret ou abonné réel identifié dans les artefacts A-00 examinés. Les références de paiement lues dans les preuves pertinentes sont présentées comme fictives ; aucune sauvegarde réelle n'a été ouverte. Il ne s'agit pas d'un audit exhaustif de tous les autres lots de `wp/`.

Les besoins 13 et 14 signalent correctement les voies non démontrées, le risque de recherche et les URL PDF publiques. Aucun accès réservé n'est certifié étanche. L'achat permanent d'un numéro doit notamment survivre à l'expiration de l'abonnement global : l'étude conserve bien ces deux droits distincts. L'ambiguïté C2 empêche toutefois de considérer la politique de révocation comme entièrement spécifiée.

Nonces, échappements et requêtes préparées : sans objet pour le livrable documentaire A-00.

## 5. Doctrine

L'approche privilégie les extensions retenues et leurs interfaces. Elle évite notamment un ancien module Gifting séparé, un nouveau moteur de coupons et un second générateur de schéma. Les doutes ne sont généralement pas présentés comme des incapacités certaines des produits. Les achats, connexions et choix financiers ne sont pas réputés autorisés.

Les écarts C1 et C2 doivent néanmoins être explicitement tracés dans l'étude. Les conventions PHP ne s'appliquent pas à ce lot sans code ; aucun défaut des autres lots n'est imputé à A-00.

## 6. Études (lots sans code)

Le dossier fournit 38 adresses et des extraits, ainsi qu'un journal des accès impossibles. Leur authenticité sur les pages actuelles n'a pas été revérifiée en ligne, conformément à l'interdiction d'accès aux sites. Les constats suivants portent sur la suffisance des preuves effectivement remises, sans prétendre que les capacités annoncées sont fausses.

**C3 — important — `production/A-00/couverture-extensions.md:130` — La citation PayPal ne prouve pas les différences de capacités qui fondent le choix de Vaulting.**

Le texte affirme que PayPal Subscriptions refuse les changements de date et les paiements synchronisés/proratisés, contrairement à Vaulting. L'extrait fourni est seulement le libellé « Synchronized or prorated payments ». Les sources 11 et 12 dans les deux registres ajoutent les conditions de compte et d'approbation, mais aucune valeur des colonnes de compatibilité ni extrait sur la modification des dates. Un intitulé de ligne n'établit pas quel mécanisme accepte la fonction. Cette lacune affecte directement le choix du moteur de renouvellement.

**Correction proposée :** fournir les cellules exactes pertinentes avec leurs en-têtes, ou les phrases officielles équivalentes, pour les dates modifiables et la synchronisation/proratisation. Rattacher chaque conclusion à cette preuve ; à défaut, la qualifier « doute ». Appliquer ce contrôle au niveau des affirmations, pas seulement de la présence d'une citation par besoin.

**C4 — important — `production/A-00/couverture-extensions.md:218` — L'attribution native d'une découverte par inscription gratuite n'a pas de citation probante dans la remise.**

La phrase annonce une durée en jours et une attribution via inscription gratuite. L'unique extrait de la source 21 établit seulement le choix entre durée illimitée et durée spécifiée ; les extraits de la source 24 concernent les fichiers et les flux RSS. Aucun n'étaye le mécanisme d'inscription gratuite. La limite sur l'unicité est bien signalée, mais elle ne remplace pas la preuve du mécanisme d'attribution présenté comme acquis.

**Correction proposée :** ajouter l'extrait officiel décrivant l'attribution lors de l'inscription et les conditions de cette configuration. À défaut, garder la durée comme capacité documentée et classer l'attribution automatique en « doute », pour éviter qu'un futur lot ne s'appuie sur une couverture non démontrée.

## Verdict

**À corriger.** Les corrections portent sur l'étude et ses preuves ; aucune réécriture de code n'est demandée.

- **Bloquant :** aucun défaut d'exécution établi dans ce lot sans code. Les arbitrages financiers et d'accès restent nécessaires avant développement des parcours concernés.
- **Important :** C1 — divergence carte/SEPA ; C2 — portée de la grâce ; C3 — preuves de compatibilité PayPal ; C4 — preuve d'attribution de la découverte.
- **Mineur :** aucun point supplémentaire retenu.

Ce verdict n'est pas un GO.
