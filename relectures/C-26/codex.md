# Relecture indépendante Codex — C-26

Date : 27 novembre 2026. Références : brief C-26, doctrine, grille, cahier des charges §4.4, avec §3.9, §3.11 et §3.12 pour les droits et surfaces concernés. Sources C26 et périmètre B06 désigné dans `A-VOIR.md` examinés, y compris inventaire, contrôles, pose/retrait des témoins et mutations. Le rapport de Claude n’a pas été lu.

## 1. Conformité

Les livrables sont présents : inventaire détaillé, matrice supplémentaire, six familles de mutations, preuves de restauration et `PRET`. Le périmètre B06 à relire est explicitement nommé. La découverte livrée est lue sans ouverture forcée. Le remplacement de l’accès obligatoire à `TMPDIR` est effectif. La couverture reste toutefois incomplète.

**C26-01 — Important — `wp/outils/demo/c26.py:32` — La page d’archive de l’agenda manque à la matrice.** Après les fiches événementielles, le catalogue ajoute le flux, mais jamais `/evenements/`. Cette sortie B07 a pourtant son propre rendu dans `wp/themes/imagine/archive-imagine_evenement.php` et figure parmi les adresses à examiner dans `A-VOIR.md`. Vérification locale sur l’inventaire livré : aucune route C26 ni C23 ne cible cette archive. Une fuite propre à son rendu ne serait donc pas interrogée. **Correction proposée :** inventorier l’URL native de l’archive, l’ajouter aux publics concernés avec contrôle de sa structure et de ses événements, et vérifier qu’une injection de témoin dans cette réponse fait échouer le contrôle.

## 2. Exactitude métier

Deux cas déroulés à la main :

- **Acheteur d’un numéro (§3.9).** Pour `acheteur-autre-numero`, le filtre retire les témoins des numéros effectivement achetés et conserve ceux des autres numéros. L’accès légitime C14 n’est pas assimilé à une fuite. En revanche, l’extraction des témoins est incomplète : voir C26-05.
- **Coopérateur (§3.9 et §3.12).** P-COOP doit lire les cinq pages réservées, sans obtenir automatiquement les articles ; V-INSCRIT doit rester refusé. Les contrôles B06 vérifient le témoin pour six voies autorisées et l’objet riche/titre pour oEmbed. Mais leur attente d’autorisation provient de la fonction qu’ils doivent contrôler : voir C26-02.

La distinction entre abonné actif et propriétaire des données C26 est correctement prévue : l’abonné reste un tiers pour les inscriptions, réponses, demandes et propositions du propriétaire fictif.

**C26-02 — Important — `wp/outils/demo/c23-inventaire.php:89` — L’attendu B06 est calculé par le contrôle d’accès testé.** `cooperator_publics` est rempli en appelant `Cooperateurs::autorise()`, puis cette liste décide si la présence du témoin constitue une fuite ou un succès. Si une régression de cette fonction autorise V-INSCRIT avant l’inventaire, la matrice adopte ce droit erroné. Reproduction locale : une réponse contenant le témoin B06 échoue avec `allowed=False`, mais passe avec `allowed=True`, précisément la valeur que fournirait cet inventaire. La mutation de statut exécutée après l’inventaire ne couvre pas ce cas. **Correction proposée :** déterminer les attentes à partir des caractéristiques documentées des personnages et des réglages livrés, indépendamment de `Cooperateurs::autorise()`, puis comparer la décision native à ces attentes. Ajouter une mutation de la décision d’autorisation avant inventaire ; elle doit rougir sans modifier les réglages métier.

## 3. Tests

Exécutions locales, sans accès au site et sans écriture de reçus dans `production/` :

| Commande / contrôle | Résultat observé |
|---|---|
| `python -B wp/tests/demo/c26-tests.py`, `TMPDIR` absent, UTF-8 | 42 tests exécutés : 40 réussites, 2 erreurs de permissions lors de la création des dossiers temporaires C23 |
| Même suite, UTF-8 puis cp1252, avec `LOCALAPPDATA` dirigé vers un dossier temporaire isolé et toujours sans `TMPDIR` | 42 tests par passage : 39 réussites, 3 erreurs de permissions sur le scratch ; ce second essai n’a pas levé la limitation |
| `python -B wp/tests/demo/c26-verifier.py` | Code 0, 46/46 contrôles |
| `python -B wp/tests/demo/c26-paquet-tests.py`, dans l’environnement temporaire | Échec de création du scratch avant les neuf falsifications ; qualification complète non reproduite |
| Contre-exemples supplémentaires, exécutés en mémoire sur les fonctions du lot | Faux négatifs et défaut de restauration reproduits pour C26-02 à C26-06 ; absence de route confirmée pour C26-01 |

L’interpréteur de cette relecture est celui de `C:\Python314`, contrairement au Python 3.11.15 des reçus livrés. Les erreurs constatées sont des `PermissionError: [WinError 5]`, pas un accès manquant à `TMPDIR`. Elles sont signalées comme limites de l’environnement de relecture, sans conclure à une régression fonctionnelle du correctif. Je ne certifie donc pas ici une suite complète verte.

Les reçus livrés annoncent 1 922 contrôles C23, 1 965 C26 et 64 privacy, ainsi que les six mutations détectées et les restaurations exactes. Le vérificateur nominal les accepte, mais les deux contre-exemples suivants montrent que ses contrôles sémantiques restent insuffisants. Pour les reproduire sans écrire de fichier, les lectures des JSON ont été substituées en mémoire et les empreintes du manifeste recalculées.

**C26-03 — Important — `wp/tests/demo/c26-verifier.py:83` — Les identités et plusieurs inverses C23 peuvent disparaître sans rejet du paquet.** Le vérificateur filtre les résultats sur le seul produit routes × publics et vérifie ce sous-ensemble. J’ai supprimé les 16 lignes dont le public n’appartient pas à `c23['publics']` dans chacun des deux reçus C23, puis ajusté `total` : identités REST et inverses abonné disparaissent, mais `verify()` renvoie encore `True`, sans échec. Les inverses B06 contrôlés séparément ne remplacent ni ces identités ni les inverses article/PDF/C08. **Correction proposée :** exiger l’ensemble exact des contrôles supplémentaires, leur unicité et leurs résultats positifs ; recalculer les échecs et fuites sur toutes les lignes. Ajouter cette suppression aux falsifications du paquet.

**C26-04 — Important — `wp/tests/demo/c26-verifier.py:79` — Un inverse privacy vide est accepté s’il se déclare négatif.** Le choix entre présence et absence du témoin dépend de `x['positive']`, sans vérifier sa cohérence avec `x['public']`. En remplaçant, pour les quatre lignes `inverse-proprietaire`, `positive` par `False` et `witnesses_found` par `0`, les deux reçus privacy passent encore les 46 contrôles après rescellement en mémoire. La présence des données pour leur propriétaire n’est alors plus prouvée. **Correction proposée :** imposer `positive is True` exactement pour `inverse-proprietaire`, et `False` pour chaque tiers ; déduire l’attente de témoin du public attendu, puis ajouter ce contre-exemple à la qualification.

Les rejeux HTTP, leurs mutations persistées et la préparation de l’image n’ont pas été relancés : `relecteurs/AGENTS.md` interdit au relecteur l’accès à un site, une base ou un compte et limite l’exécution aux tests locaux. Les preuves correspondantes ont été examinées sur disque seulement.

## 4. Sécurité et données

**C26-05 — Bloquant — `wp/outils/demo/c26.py:142` — Les nouvelles sorties ignorent une partie des témoins réservés existants.** `denied_markers()` ne reprend que le motif `CONTENU_FICTIF_RESERVE_*` des articles et les marqueurs privés C26. Il omet notamment les phrases témoins C08 déjà surveillées par C23 et les témoins des cinq pages B06. Reproduction avec l’inventaire livré et une réponse HTML valide de Soutenir : l’ajout de `CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1` donne `ok=False, leak=True`, tandis que l’ajout de `Les lucioles violettes de C08 gardent le secret du village fictif.` ou de `C23_COOP_TEMOIN_2867` donne `ok=True, leak=False` pour l’anonyme. Le passage C23 ne compense pas ce défaut : il n’interroge pas la nouvelle page Soutenir. **Correction proposée :** reprendre l’inventaire complet des témoins réservés pour chaque nouvelle sortie, en appliquant séparément les droits sur les numéros et l’espace coopérateurs. Refuser aussi un contenu réservé inventorié sans témoin reconnu. Couvrir les familles de témoins omises par des tests négatifs et un rejeu approprié.

**C26-06 — Important — `wp/outils/demo/c26-preparer.py:51` — Un échec de restauration B06 empêche la restauration des profils.** `cleanup`, `restore_cooperator` et la remise en état des métadonnées utilisateur sont exécutés séquentiellement. Or `restore_cooperator()` peut volontairement lever une exception lorsqu’une page a dérivé. Dans ce cas, les réponses de personnalisation temporaires et les sessions ne sont pas restaurées, et l’appelant ne produit pas son bilan final de restauration. Reproduction locale avec cette exception simulée : zéro appel au bloc de restauration des métadonnées. **Correction proposée :** rendre les restaurations indépendantes par des `finally` ou une collecte d’erreurs, tenter chaque remise en état et produire un bilan d’échec même si une autre restauration échoue. Ajouter des tests d’erreur pour le nettoyage privé et la restauration B06, en conservant le refus d’écraser une dérive concurrente.

Aucun secret de session ni donnée réelle repéré dans les éléments examinés. Les fixtures exigent une cible fictive et des adresses `@example.org`. Le transport de la matrice est GET et les redirections hors démonstration sont refusées. Les constats ci-dessus portent sur la fiabilité de la preuve et du nettoyage ; ils ne démontrent pas une fuite effective du site, qui n’a pas été consulté.

## 5. Doctrine

L’extension reste un outil de test ; elle réemploie les callbacks natifs et ne nécessite pas de modification du paywall ou du thème pour corriger les constats. Les restaurations nominales sont documentées, mais le chemin d’échec C26-06 ne satisfait pas l’exigence de retour à l’état métier initial. Les faux négatifs C26-02 et C26-05 empêchent de considérer l’étanchéité comme prouvée au sens du §4.4 et de la doctrine §4.

Aucune question métier, visuelle ou touchant au réel à arbitrer. Les corrections proposées sont techniques et peuvent être réalisées sans changer les réglages livrés.

## 6. Études (lots sans code)

Sans objet : lot de code et de tests.

## Verdict

**À corriger.**

- **Bloquant :** C26-05 — témoins réservés non surveillés sur les nouvelles sorties.
- **Importants :** C26-01 — archive agenda absente ; C26-02 — attendu B06 dépendant du code testé ; C26-03 — identités/inverses C23 facultatifs pour le vérificateur ; C26-04 — inverse privacy vide accepté ; C26-06 — restauration des profils interrompue par une autre erreur.
- **Mineurs :** aucun point retenu.

Ce verdict n’est pas un GO.
