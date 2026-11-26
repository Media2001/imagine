# Relecture Codex — A-20

Date : 26 novembre 2026. Relecture indépendante du brief, de la production A-20, du code et des tests concernés, suivant la doctrine et les §3.4 et §4.3 du cahier des charges. Le rapport de Claude n'a pas été consulté. Aucun fichier de production n'a été modifié.

## 1. Conformité

Les agrégats demandés sont présents : quatre états vivants, produit/variation, périodicité de l'abonnement, montants et seuil de cinq, lignes de produit/frais/port, pays, devise étrangère et total nul. Les définitions accompagnent les comptes. Les deux lignes du mode d'emploi commun et le marqueur `PRET` sont présents ; un seul paquet de preuves est livré.

Les interprétations sont explicites : total enregistré plutôt que prélèvement garanti, total entier dans chaque groupe d'un abonnement à plusieurs produits, annuel défini par `1 year` ou `12 month`, pays de livraison sans repli sur la facturation. Aucune correspondance tarifaire ni qualification en anomalie n'est introduite. Cela respecte le périmètre d'observation des abonnements conservés (§4.3), sans leur appliquer la nouvelle offre (§3.4).

La garantie « aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site » reste toutefois incomplète : point B1 ci-dessous.

## 2. Exactitude métier

Cas déroulés à la main à partir du jeu fictif de `wp/tests/a20/seed.php`, puis comparés à `Analysis.php` et aux rapports classique/HPOS livrés :

- **Récurrence annuelle** : cinq abonnements actifs au même produit, à `100.00 EUR`, livrés en BE sans ligne de port. Attendu et obtenu : cinq actifs, cinq occurrences `1 year`, montant visible avec effectif cinq, pays BE visible avec effectif cinq et zéro avec port. Le rythme du catalogue, volontairement différent, n'intervient pas.
- **Ancien abonnement mensuel livré à l'étranger** : un abonnement en attente à `9.17 EUR`, livré en FR, avec port et frais gratuits. Attendu et obtenu : une occurrence `1 month`, un non-annuel, montant masqué dans « autres montants », pays masqué dans « autres pays », une présence de frais et une présence de port. Aucun reclassement vers un nouveau tarif.
- **Variation et plusieurs lignes** : l'abonnement suspendu à total nul en USD et celui en annulation à terme portant deux lignes du même produit et une variation produisent deux abonnements pour la variation ; la répétition du premier produit ne le compte qu'une fois. Les comptes globaux donnent un total nul, une devise étrangère et un abonnement à plusieurs lignes. Le total de la variation reste masqué.

Le bilan livré est cohérent : huit abonnements vivants, comptes produit de sept et deux avec recoupement, un expiré exclu, deux abonnements avec port, un pays inconnu. Les seuils quatre/cinq, les devises distinctes, les pays inconnus et les abonnements sans produit sont également traités dans les tests purs. Pas de logique de clôture de calendrier ou d'échéancier dans ce lot.

## 3. Tests

Exécutions effectuées sans écrire de résultats supplémentaires :

- `C:/Python314/python.exe -B -m unittest discover -s wp/tests/a20 -p test_*.py -v` : **8 tests réussis**, puis réussite confirmée sous `PYTHONUTF8=1 / PYTHONIOENCODING=utf-8` et sous `PYTHONUTF8=0 / PYTHONIOENCODING=cp1252`.
- `C:/Python314/python.exe -B wp/tests/a20/verify.py production/A-20/preuves/final` : **108 contrôles réussis**, code 0. Il s'agit d'une vérification des preuves existantes, pas d'une nouvelle exécution native.
- Contrôle indépendant des empreintes : **119 fichiers** du manifeste de livraison conformes ; les **21 dépendances** de chacun des relevés UTF-8/cp1252 correspondent également aux fichiers courants.

Les preuves natives fournies annoncent, pour chaque contexte, 23 contrôles PHP purs, 98 contrôles natifs et 9 contrôles du lanceur. Elles comprennent le parcours documenté avec ses trois arguments, les empreintes des tables et fichiers, les refus de configuration et les canaris. Les attendus métier sont explicitement chiffrés dans le banc, sans être calculés par la fonction testée.

**Limite du rejeu indépendant :** la tentative d'exécution d'une sonde PHP locale dans l'image du banc a échoué avant son démarrage : `Wsl/Service/E_ACCESSDENIED`. Les suites PHP, classique/HPOS et PHPCS n'ont donc pas été rejouées ici. Aucun résultat natif nouveau n'est revendiqué.

La couverture des sorties s'arrête à un `echo` suivi d'un retour normal et à une exception interceptable (`wp/tests/a20/inside.py:42`). Les écritures directes dans les flux et les arrêts anticipés manquent ; leur ajout fait partie de la correction B1.

## 4. Sécurité et données

**B1 — bloquant — `wp/outils/bascule/a20/confine.py:23` : les flux du processus PHP sont transmis sans filtrage externe.**

Le lanceur se remplace par PHP avec `os.execvp`, qui conserve stdout et stderr. Le tampon ouvert par `inventorier-tarifs` ne capture pas une écriture directe telle que `fwrite(STDERR, ABSPATH)` ou `fwrite(STDOUT, $nom)` pendant le chargement d'une extension. Une extension qui fait `echo $nom; exit;` interrompt aussi le parcours avant `ob_end_clean()` ; le tampon est alors vidé à la fin du processus. Ces cas laissent sortir un chemin ou un nom du site malgré les réglages `display_errors=0` et `log_errors=0`. Le confinement des écritures sur disque ne filtre pas ces flux hérités. Le défaut est établi par lecture du chemin d'exécution ; sa reproduction PHP n'a pas pu être exécutée à cause du refus WSL indiqué plus haut.

**Correction proposée :** conserver un superviseur hors du processus qui charge WordPress, capturer les deux flux PHP sans jamais les retransmettre bruts, et n'émettre que des messages conformes à une liste fermée après validation du résultat et des rapports attendus. Un arrêt anticipé sans rapport complet doit être un échec, même avec un code de sortie zéro. Ajouter au banc classique et HPOS des canaris écrits directement sur stdout/stderr, un `echo` suivi de `exit`, et une sortie lors de l'arrêt du processus ; vérifier leur absence de toutes les sorties et des artefacts conservés.

Pour le reste du périmètre inspecté : projection limitée aux champs techniques, seuils appliqués avant sérialisation, exceptions ordinaires filtrées, droits de sortie privés, lecture native via le runtime A-11 et confinement A-12 réutilisés. Les jeux examinés sont fictifs. Aucun accès à un site, à une base ou à un compte n'a été réalisé pendant cette relecture. Nonces et paywall sans objet pour cet outil CLI.

## 5. Doctrine

Les règles de comptage sont isolées en PHP pur ; l'adaptateur utilise les objets natifs WooCommerce/Subscriptions et le magasin faisant autorité. Les fichiers PHP de production portent `strict_types` et l'espace de noms `Imagine`. Le README documente les limites et les références officielles utilisées ; le paquet contient leurs reçus de consultation. Aucun développement d'une correspondance tarifaire ou d'un moteur de paiement supplémentaire.

Les preuves PHPCS fournies sont vertes et liées aux sources courantes. La finalisation parent explique explicitement que les mentions « gates en attente » des reçus candidats sont historiques. Aucun arbitrage métier ou visuel supplémentaire n'est nécessaire pour corriger B1.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références documentaires ont été examinées dans les fichiers livrés, sans consultation de sites externes.

## Verdict

**À corriger.**

- **Bloquant : B1** — fermer les sorties du processus PHP chargé de lire WordPress et couvrir les flux directs ainsi que les arrêts anticipés.
- **Important :** aucun autre point retenu.
- **Mineur :** aucun point retenu.

Ce verdict n'est pas un GO. Les tests Python et le contrôle du paquet réussissent ; le rejeu natif indépendant reste limité par le refus d'accès à WSL.
