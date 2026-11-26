# Relecture indépendante Codex — C-20

26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, deux briefs C-20, cahier des charges §3.4 et §3.7, arbitrages du 26 novembre et consigne de 7 h 30. Lecture de `production/C-20/` et des sources concernées dans `wp/`. Aucun accès au site, à une base ou à un compte ; aucune lecture de `relectures/C-20/claude.md`.

## 1. Conformité

Le périmètre réduit est explicitement autorisé par `A-FAIRE-2.md:15` et par l’arbitrage de 7 h : raccord d’accès, présentations sans bouton, phrase de demande à Imagine pour le quatre-fois. Le bouton, sa confirmation, l’émission du hook et la preuve de fin native du quatre-fois sont reportés. Leur absence n’est donc pas un défaut de cette livraison. L’écart restant avec le §3.4 est déclaré dans `docs/ecarts.md`.

Le raccord modifie uniquement la lecture du couple Memberships `pending` / Subscriptions `pending-cancel`, avec fin native renseignée. Le code ne change pas C06 ni les règles postales. Le hook de confirmation est réservé, sans émission ni email. La marge C05 absente reste absente ; aucun échec du moteur natif du quatre-fois n’est abusivement revendiqué.

**M1 — mineur — `wp/plugins/imagine-site/README.md:291`.** La documentation courante affirme encore « Pas PRET : le point 2 reste bloqué » et traite la sortie postale comme un obstacle. Cela contredit le périmètre accepté et le PRET courant. **Correction proposée :** aligner cette section et ses commandes sur la livraison réduite ; conserver l’ancien constat seulement comme historique explicitement daté, avec retour attendu actuel du vérificateur.

## 2. Exactitude métier

Cas déroulés à la main et confrontés au code et aux reçus :

- **A-CARTE, §3.4 :** après annulation native, Memberships devient `pending`, la souscription `pending-cancel`, fin au 25/12/2026 à 18:01:50 UTC. `Paywall.php:249` produit un droit actif borné par le minimum des fins Memberships/Subscriptions. Avant cette fin, C06 rend `abonnement_actif`, comme les états avant/après du reçu courant. À la fin exacte, C06 refuse puisque `instant >= fin` ; il ne dépend pas de l’exécution ponctuelle de l’action d’annulation.
- **A-VIR, §3.4 :** une adhésion `pending` liée au premier paiement `pending` passe par la branche `virement_non_valide`, sans atteindre la nouvelle exception. Aucun accès payé ni bouton de renouvellement automatique n’est inventé. Le contre-exemple est présent dans la sonde.
- **Passage d’année et liste d’envoi :** le 25/12/2026 précède la clôture du 05/01/2027, 00:00 Europe/Brussels. C13 exclut donc la seule souscription 89 avec le motif `expire` : huit lignes deviennent sept, les autres restent identiques. C’est conforme à l’arbitrage. Une fin exactement égale à la clôture est également exclue par `EnvoiRegles.php:230` (`end <= cloture`).
- **A-SEPA4, calendrier non exploitable :** marge C05 nulle, arrêt avant toute écriture de fin ; présentation de la demande à Imagine, échéances intactes. Ce repli respecte le périmètre réduit. La reprise refusée est expliquée par les produits privés, conformément au code natif conservé, et non simplement par la méthode de paiement vide.

Aucune mutation commerciale C20 n’est exposée : un nouvel affichage ne change ni état ni date. Le rejeu d’un événement commercial n’est pas ajouté par ce lot.

## 3. Tests

Exécutions indépendantes, sans écriture de fichiers de test ou de reçus :

- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` : **code 1 avant PHPUnit**, accès WSL refusé (`Wsl/Service/E_ACCESSDENIED`) ; bilan du lanceur : 0 test, 0 assertion, 1 erreur. Aucun résultat PHP indépendant obtenu. Aucun PHP/PHPUnit local trouvé dans le PATH ; aucune installation effectuée.
- `python -B -m unittest discover -s wp/tests/demo -p test_c08_scope.py -v` : **5 tests réussis**, sous Python 3.14. Ces tests vérifient les gardes de portée C08 avec appels simulés ; ils ne remplacent pas les recettes métier.

Les reçus livrés annoncent C20 natif **11/11**, présentation **18/18**, C08 **30/30**, C13 **24/24**, C09 **382/382**, avec restauration et relecture des profils/actions. Les résultats détaillés consultés concordent avec ces annonces. Ce sont les preuves du producteur, pas des recettes rejouées ici. Les commandes `c20-second.py --verify`, `--probe`, `--regressions` et le parcours HTTP accèdent au site ; elles n’ont pas été exécutées, conformément aux droits du relecteur. Le lanceur ciblé `c20-unit.py` écrit des reçus hors du seul fichier autorisé ; il n’a pas été utilisé.

**I1 — important — `wp/tests/demo/c20-second-native.php:60`.** La nouvelle ouverture du paywall n’est vérifiée qu’à l’instant courant, avant le terme. Les contre-exemples couvrent le lien absent, le statut actif et le premier paiement, mais pas `pending-cancel` sans fin ni les bornes effectives du nouveau droit. Une régression ouvrant un droit sans terme, ou transmettant une borne trop longue, pourrait passer cette réception. Les tests C06 couvrent déjà les bornes d’un droit fourni ; ils ne prouvent pas les dates assemblées par le raccord Memberships/Subscriptions. **Correction proposée :** ajouter un test local du raccord, avec doublures et horloge contrôlée, vérifiant la fermeture sans fin native, l’accès juste avant la fin et le refus à la fin exacte/après, ainsi que la priorité d’une fin Memberships antérieure. Conserver les règles C06 et C13 inchangées. Il s’agit d’un manque de couverture du livrable principal, pas d’une fuite constatée dans le code actuel.

## 4. Sécurité et données

`Renouvellement::afficher()` relit la souscription et contrôle son propriétaire avant toute sortie. Les sorties variables sont échappées. Aucun nouveau contrôleur de mutation, requête SQL ou traitement de nonce n’est introduit. Le refus d’une mutation par un autre propriétaire est contrôlé par la recette native livrée. Le retrait des boutons standard est limité à la démonstration locale désignée ; ce filtre de présentation ne constitue pas un contrôle d’autorisation.

Le raccord conserve la vérification des propriétaires, les bornes natives et la fermeture sur exception. Aucune nouvelle voie de sortie du texte réservé identifiée à la lecture. Aucun secret ni donnée d’abonné réel identifié dans les éléments examinés ; profils explicitement fictifs. La réserve de couverture I1 reste applicable.

## 5. Doctrine

Standard conservé : aucune passerelle, aucun ordonnanceur, aucune modification d’extension tierce, aucun changement forcé d’état. La présentation pure est séparée du raccord WordPress ; namespace et `strict_types` sont présents. La source Memberships archivée contient effectivement la branche `pending-cancel` appelant `update_status('pending')` hors période d’essai.

**M2 — mineur — `wp/plugins/imagine-site/Renouvellement.php:48`.** `__($view['message'], 'imagine-site')` reçoit une variable ; les phrases définies dans la classe pure ne sont pas des littéraux d’appels de traduction extractibles. Le passage apparent par `__()` ne suffit donc pas à alimenter le catalogue standard, contrairement à l’objectif de la doctrine §5. **Correction proposée :** renvoyer un code de message depuis la classe pure et associer chaque code à un appel de traduction contenant une chaîne littérale dans le raccord WordPress, puis conserver l’échappement HTML.

## 6. Études (lots sans code)

Sans objet comme catégorie autonome : lot avec code. `natif.md` fournit les adresses officielles et les références du code installé. Les sources natives archivées corroborent le mappage Memberships et le refus lié aux produits non publiés. Les pages officielles n’ont pas été consultées en ligne, l’accès à un site étant interdit au relecteur ; leur actualité n’est pas certifiée par cette relecture. La piste quatre-fois reste explicitement non prouvée.

## Verdict

**À corriger**, sur le seul périmètre réduit autorisé.

- **Bloquant :** aucun identifié.
- **Important :** I1 — compléter la couverture du raccord d’accès sur l’absence de fin et les bornes natives.
- **Mineur :** M1 — README resté sur le blocage historique ; M2 — messages non extractibles pour la traduction.

Le refus d’accès à WSL est une limite de vérification, pas un échec métier démontré. Aucune question nouvelle pour Ced ou Imagine. Ce verdict ne vaut ni validation visuelle, ni clôture, ni GO.
