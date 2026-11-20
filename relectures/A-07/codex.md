# Relecture Codex — lot A-07

Relecture indépendante du 20 novembre 2026, sur pièces. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief A-07 et décisions du projet. Lecture des deux livrables de `production/A-07`, recherche des éléments liés au lot dans `wp/` et lecture des documents de staging pertinents. Aucun fichier de code ni test propre à A-07 identifié dans `wp/`. Le brief ne cite aucun paragraphe du cahier des charges et n'introduit aucune règle métier applicative. La relecture de Claude n'a pas été consultée.

## 1. Conformité

Les deux livrables attendus sont présents. Le rapport tient en une page, présente les six rubriques et termine par des recommandations ordonnées. Les limites sont explicites. La formulation initiale s'écarte du libellé demandé, mais évite à juste titre d'affirmer une absence d'exposition qui n'est pas démontrée : conserver cette prudence.

- **A07-01 — important — `production/A-07/exposition.md:9`.** L'inventaire donne un état pour Tailscale et le Bureau à distance, mais aucun résultat pour Cloudflare/cloudflared et ngrok, pourtant explicitement demandés au point 5 du brief. La réserve sur les outils portables ne permet pas de savoir si ces deux outils ont été recherchés, trouvés inactifs ou non vérifiés. **Correction proposée :** indiquer pour chacun la présence constatée et l'activité constatée, ou « non vérifié » avec la raison ; préciser le périmètre Windows/WSL effectivement examiné. Signaler explicitement que Tailscale actif contredit l'hypothèse initiale d'absence de tunnel, sans en déduire une publication publique.

- **A07-02 — important — `production/A-07/exposition.md:8`.** Le résultat « zéro redirection » n'est pas accompagné d'un état permettant de distinguer une collection disponible et vide d'une absence de réponse exploitable. Le rapport reconnaît lui-même que la réponse de la box n'est pas certifiée : la vérification de présence du service UPnP demandée au point 4 reste donc indéterminée. **Correction proposée :** restituer séparément le résultat de découverte/réponse et celui de l'énumération, avec la commande réellement exécutée et le statut observé. Si aucune réponse exploitable n'a été obtenue, remplacer « zéro redirection » par « redirections non déterminées » et indiquer le blocage, sans consulter l'administration ni modifier de règle.

## 2. Exactitude métier

Sans code métier dans ce lot, deux cas du périmètre du brief ont été déroulés sur le raisonnement du rapport, sans accès réseau :

1. **7000 inaccessible, mais un site publié accessible depuis l'extérieur.** La procédure proposée ne teste que le tableau de bord ; elle ne permet pas de constater l'exposition du site. Voir A07-03.
2. **Collection UPnP inexploitable et redirection manuelle présente.** Le nombre annoncé ne permet pas de conclure sur la redirection. Le rapport conserve correctement cette réserve et ne conclut pas à une sécurité établie ; la qualification du résultat UPnP doit néanmoins être corrigée selon A07-02.

- **A07-03 — important — `production/A-07/exposition.md:10`.** La procédure mobile vise exclusivement le port 7000, alors que les sites sur 8081–8200 font partie de l'objectif et que plusieurs ports effectivement publiés sont recensés ligne 5. Un résultat négatif sur 7000 laisse toute cette surface sans vérification proposée. **Correction proposée :** ajouter une ouverture manuelle d'un site sur un port actuellement publié, en IPv4 et, si disponible, en IPv6, puis préciser que les autres ports restent non vérifiés tant qu'ils n'ont pas été contrôlés individuellement. Conserver l'interdiction de balayage et l'avertissement qu'un échec de connexion ne démontre pas une absence générale d'exposition.

## 3. Tests

Aucun test automatisé ni commande de test local n'est prévu par le brief ou livré dans `production/A-07`. Aucun test n'a donc été lancé. Les suites existantes de `wp/` portent sur d'autres lots et ne valident pas l'exposition effective de cette machine. Les deux cas ci-dessus constituent une vérification documentaire, pas une mesure réseau.

Les commandes d'inventaire et les constats d'Hermès n'ont pas été réexécutés : les droits du relecteur limitent l'exécution aux tests locaux du lot et interdisent l'accès à un site, une base ou un compte. Leur résultat reste déclaré par le producteur, non confirmé indépendamment.

## 4. Sécurité et données

Aucun mot de passe, adresse IP publique, identifiant de compte ou donnée personnelle relevé dans les livrables A-07. Aucun accès externe ni changement réseau effectué pendant cette relecture. Les recommandations restent des propositions. Les limites concernant IPv6, Hyper-V, les règles globales et les accès privés distants sont correctement explicitées ; elles empêchent une attestation d'absence d'exposition. Aucun contrôle de droits WordPress, nonce ou paywall n'est introduit par ce lot documentaire.

## 5. Doctrine

Aucune réimplémentation d'extension ni convention de code à examiner. La règle générale « Un lot sans tests n'est pas PRET » de `doctrine/doctrine.md`, §4, rencontre ici un brief de contrôle documentaire sans suite locale prévue. Le marqueur `PRET` précise que le rapport est prêt pour relecture et que l'absence d'exposition n'est pas attestée ; il ne doit pas être interprété comme une validation technique du staging. Cette tension entre doctrine et nature du lot est signalée sans inventer une réception automatisée.

## 6. Études (lots sans code)

Aucune affirmation fonctionnelle sur une extension WordPress ne nécessite ici de citation officielle. Les constats sur la machine doivent en revanche être traçables.

- **A07-04 — mineur — `production/A-07/exposition.md:7`.** La preuve cite séparément `Get-NetFirewallRule -PolicyStore ActiveStore` et `Get-NetFirewallPortFilter`, sans la commande d'association et de filtrage effectivement utilisée. Le lecteur ne peut pas reconstituer comment les ports ont été rattachés aux règles entrantes actives et à leurs profils. **Correction proposée :** donner la commande exacte avec ses filtres et les seuls champs non sensibles utiles (direction, activation, action, protocole, ports, profils). En l'état : **doute** sur la reproductibilité de la preuve, sans affirmer que le constat est faux.

## Verdict

**À corriger.** Ce verdict n'est pas un GO et n'atteste aucune absence d'exposition Internet.

- **Bloquant :** aucun défaut bloquant établi sur pièces ; l'exposition réelle demeure indéterminée.
- **Important :** A07-01, inventaire des tunnels incomplet ; A07-02, résultat UPnP insuffisamment qualifié ; A07-03, procédure extérieure ne couvrant pas les sites.
- **Mineur :** A07-04, preuve du pare-feu insuffisamment reproductible.
