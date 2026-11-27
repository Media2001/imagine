# Relecture indépendante Codex — B-13

Date : 27 novembre 2026. Périmètre : brief B-13, cahier des charges §3.1, doctrine, décisions, code et tests dans `wp/`, livraison `production/B-13`. Le rapport Claude n'a pas été consulté. Aucun accès à un site, à une base ou à un compte ; aucune correction du code.

## 1. Conformité

La structure utilise le menu natif et son filtre de rendu, avec des listes imbriquées et des liens accessibles sans JavaScript. Aucun style ni animation n'est ajouté par B-13. Les preuves archivées montrent les huit entrées dans l'ordre sur l'accueil, l'article réservé et le numéro, pour les deux profils testés. La capture demandée et `PRET` sont présents. Le réglage du nombre et le choix des articles récents correspondent au brief et à `docs/decisions.md`. Le comportement de « Connexion » est documenté : libellé conservé et destination Mon compte.

**B13-01 — Important — Sélection partiellement dépourvue d'images.** Fichier : `wp/plugins/imagine-site/Navigation.php:123`.

L'appel à `get_the_post_thumbnail()` peut produire une chaîne vide, sans traitement de ce cas. Ce n'est pas seulement théorique : dans chacune des six surfaces de `production/B-13/browser-final-V2.json`, les neuf articles sélectionnés ne contiennent que trois images. Les articles 44, 37, 43, 36, 45 et 42 n'en ont aucune ; la capture confirme ces liens sans illustration. Le brief demande une sélection titre/image à la une/lien et le §3.1 des articles illustrés.

Correction proposée : compléter les images à la une des articles fictifs retenus pour la démonstration, sans inventer d'habillage, puis vérifier chaque article sélectionné individuellement. Documenter aussi le comportement lorsqu'un article récent n'a pas d'image ; ne pas le remplacer silencieusement par un article plus ancien pour faire passer la preuve.

## 2. Exactitude métier

Cas déroulés à la lecture du code et comparés aux preuves archivées, sans nouvelle manipulation de WordPress :

- **Article dépublié** : `save_post` invalide le fragment ; la requête suivante exige `post_status = publish`. L'article disparaît. Les contrôles archivés `depublication_invalide` et `depublication_retire_article` concordent avec ce chemin.
- **Thématique sans article** : `hide_empty = false` conserve le terme ; une sélection vide n'ajoute pas de sous-liste d'articles. Le contrôle archivé `thematique_vide_conservee` concorde avec cette règle.
- **Rejeu B-08 puis B-13 après une première installation B-13** : B-08 réécrit l'URL de « S'abonner » avec `/#imagine-abonnement` ; B-13 retrouve sa fixture et quitte avant de rétablir la page d'attente. Ce chemin contredit le résultat attendu du rejeu.

**B13-02 — Important — Le rejeu ne rétablit pas le lien d'abonnement.** Fichier : `wp/outils/demo/b13-seed.php:14`.

La présence de `imagine_b13_fixture` entraîne un retour immédiat, sans contrôler la page ni l'URL du menu. Or le script dépendant B-08 fixe explicitement l'ancienne ancre dans `wp/outils/demo/b08-seed.php:73`. Après le scénario ci-dessus, l'instruction B-13 qui répare le lien, ligne 31, n'est jamais exécutée. Un état de livraison peut donc être annoncé alors que « S'abonner » ne pointe plus vers la page d'attente déclarée.

Correction proposée : au rejeu, vérifier les objets détenus par B-13 et réappliquer le raccord sur l'entrée existante, en conservant son identifiant. Ajouter un test B-08 → B-13 → B-08 → B-13 qui vérifie la destination finale et l'absence de doublons.

**B13-03 — Important — Invalidation incomplète lors du retrait d'une thématique.** Fichier : `wp/plugins/imagine-site/Navigation.php:16`.

Le cache écoute `set_object_terms`, mais pas `deleted_term_relationships`. Un retrait effectué directement par l'API native `wp_remove_object_terms()` ne passe pas par `set_object_terms` et ne nécessite pas de sauvegarde de l'article. Le fragment déjà construit peut donc conserver l'article dans son ancienne thématique jusqu'à une autre invalidation ou à l'expiration d'un jour. Le test livré ne couvre que `wp_set_object_terms($article, [], ...)`, qui emprunte le chemin déjà écouté. Constat par analyse des raccords, non reproduit sur une instance durant cette relecture.

Correction proposée : couvrir aussi la suppression native des relations de la taxonomie `imagine_thematique`. Tester le retrait direct après construction du cache, puis vérifier que la sélection est renouvelée et que le terme devenu vide reste affiché.

## 3. Tests

Contrôles effectivement exécutés localement :

| Contrôle | Résultat |
| --- | --- |
| `python -B production/B-13/verifier.py` | PASS : cohérence des sources et des preuves archivées |
| `python -B production/B-13/qualifier.py` | PASS : neuf contre-exemples du vérificateur |
| PHPUnit ciblé `NavigationB13Test`, via l'image Docker T01 existante, sans réseau et avec source montée en lecture seule | Non exécuté : WSL refuse le démarrage, `Wsl/Service/E_ACCESSDENIED`, code 1 |
| Lecture structurée du HTML des six surfaces archivées | Neuf articles par surface, trois images ; constat B13-01 |

Le vérificateur valide des résultats **archivés** : 19 contrôles natifs, 45 contrôles navigateur sur six surfaces, un test PHPUnit B-13 ; le rejeu global enregistré compte 1 205 tests et 36 677 assertions, ainsi que 852 contrôles d'outils. Ces résultats ne constituent pas un nouveau passage des tests fonctionnels pendant cette relecture. Les échecs de paquets A-32/A-33 signalés par ce journal sont étrangers au lot.

`--live`, les essais natifs et navigateur n'ont pas été lancés : ils accèdent au site et à sa base, contrairement aux droits du relecteur. La préparation d'image, qui télécharge des dépendances, n'a pas été lancée. Le rejeu global n'a pas été tenté après le refus d'accès WSL. Les preuves archivées indiquent une restauration des états et sessions ; cette restauration n'a pas été vérifiée en direct.

**B13-04 — Mineur — Le contrôle du nombre accepte une sélection vide.** Fichier : `wp/tests/demo/b13-runtime.php:53`.

Avec le réglage à un article, le test exige seulement que le total des articles soit inférieur ou égal au nombre de thématiques. Zéro article satisfait cette assertion, tout comme une répartition incorrecte entre thématiques. Il ne démontre donc pas que le réglage est appliqué à chacune des sélections.

Correction proposée : sur des thématiques fictives contenant assez d'articles, comparer les identifiants attendus par thématique pour les réglages 1, 3 et 10, dans l'ordre des dates puis des identifiants en cas d'égalité. Conserver un cas distinct pour la thématique vide. Renforcer également la vérification d'image par article dans le cadre de B13-01.

## 4. Sécurité et données

Le fragment ajouté ne rend ni extrait ni corps : uniquement titre échappé, lien échappé et image à la une native. La requête exclut les articles non publiés et protégés par mot de passe. Le cache porte sur ce seul fragment public. Aucun contournement du paywall identifié dans ce rendu.

Le réglage utilise `manage_options`, l'API Settings et son nonce ; sa valeur est bornée de 1 à 10. Aucun secret ni donnée réelle identifié dans les fichiers du lot examinés. Les contrôles navigateur archivés vérifient la présence d'un titre de sélection avant l'absence des témoins C-26 et du marqueur d'extrait B-13, avec un contre-exemple positif du détecteur. Ils ne remplacent pas un nouvel essai sur instance.

## 5. Doctrine

Le standard est privilégié : menu et filtre natifs, requêtes WordPress, Settings API et Transients. La section README explique ces choix en cinq lignes avec les adresses officielles. `Navigation.php` utilise le typage strict, l'espace de noms Imagine et les traductions des textes d'administration ; aucune extension tierce n'est modifiée.

Le défaut de rejeu B13-02 contrevient à l'exigence de reproductibilité de la doctrine §4. Les corrections proposées restent techniques et ne nécessitent pas d'arbitrage de Ced. La sélection manuelle demeure une question métier déjà consignée, avec le défaut « articles les plus récents » ; aucune fonctionnalité de sélection manuelle supplémentaire n'est demandée ici. La forme du menu reste à valider sur maquette.

## 6. Études (lots sans code)

Sans objet : lot avec code. Les références officielles sont présentes dans le README et `sources-officielles-V2.json` ; elles n'ont pas été consultées en ligne pendant cette relecture, conformément à l'interdiction d'accès à un site.

## Verdict

**À corriger.**

- **Bloquant** : aucun identifié.
- **Important** : B13-01, six articles sélectionnés sans image ; B13-02, lien d'abonnement non rétabli au rejeu ; B13-03, cache non invalidé lors d'un retrait direct de relation de thématique.
- **Mineur** : B13-04, assertion insuffisante sur le nombre d'articles par thématique.

Les contrôles locaux de réception passent, mais le test PHPUnit n'a pas pu démarrer et les essais sur instance n'ont pas été rejoués. Ce verdict n'est pas un GO.
