# Relecture indépendante Codex — B-10

Date : 27 novembre 2026. Périmètre : brief B-10, production B-10 et raccords dans `wp/`. Références : cahier des charges §3.14 et §4.4, doctrine et grille de relecture. Le rapport de Claude n’a pas été consulté. Aucun accès au site, à une base ou à un compte.

## 1. Conformité

Les livrables demandés sont présents : code, tests, CSV fictif de 30 commerces avec une ligne volontairement invalide, correspondance JSON, README, note de choix natif, `A-VOIR.md` et `PRET`. Le type de contenu privé, la page ordinaire, le lien ajouté au pied de page B09 et l’absence de nouveaux styles correspondent au brief. La capture mobile montre le squelette B01 et la déclaration de données fictives.

La carte est fermée par défaut ; son activation produit seulement un emplacement textuel. Aucun géocodage ni appel distant dans les deux classes du lot. Les limites techniques et la conservation de l’ancienne liste lorsqu’aucune ligne n’est acceptée sont déclarées dans la note. La recherche exacte est bien le défaut demandé, sous réserve du point I1.

## 2. Exactitude métier

Cas déroulés à la main, confrontés au code et aux preuves archivées :

- **Chargement et rejeu** : la fixture possède 30 lignes valides et une ligne 32 à deux colonnes. La projection conserve les quatre champs mappés ; la ligne 32 donne `nombre_colonnes`, sans sa valeur. Un second chargement identique rejoint le retour anticipé de `importer()` et conserve les IDs. Les recettes archivées donnent bien 30 prises, un refus et des IDs stables.
- **Recherche** : les commerces des lignes 2, 8, 14, 20 et 26 ont la localité `Étoile-Fictive` et le code `00001`. `ETOILE-FICTIVE`, `étoile-fictive`, la forme décomposée et `00001` sélectionnent ces cinq commerces ; `000` n’en sélectionne aucun. Le code et la recette navigateur concordent.
- **Fichier entièrement refusé** : le résultat contient zéro ligne prise et les numéros/motifs ; le retour avant acquisition du verrou conserve la liste active. Ce comportement prudent est documenté et couvert par la preuve native. Les limites calendaires sont sans objet pour ce lot.

**I1 — important — `wp/plugins/imagine-site/PointsVenteRegles.php:18`.** La suppression des accents repose sur une table partielle, puis retire seulement les marques Unicode déjà séparées. Ainsi, une localité fictive `Șoim-Fictif` reste `șoim-fictif`, alors que `Soim-Fictif` ou `S` suivi de U+0326 donnent `soim-fictif` : la recherche échoue selon la composition Unicode du même accent. Le CSV accepte pourtant tout UTF-8 et le brief ne limite pas les accents. **Correction proposée :** décomposer les caractères Unicode avant de retirer les marques, avec une dépendance explicitement déclarée si nécessaire ; ajouter un test comparant formes précomposée, décomposée et désaccentuée pour un caractère absent de la table. Constat par lecture du code, non exécuté en PHP dans cette session.

**I2 — important — `wp/plugins/imagine-site/PointsVente.php:115`.** Un refus de suppression d’un ancien commerce survient après la bascule vers les nouveaux IDs. L’import lève alors `nettoyage_refuse`, mais conserve la nouvelle liste ; l’administration annonce une opération refusée. Les anciens IDs restants ne sont conservés dans aucun état de reprise. Recharger le même CSV retourne ensuite immédiatement à la ligne 93 et ne retente jamais leur suppression : des commerces et leurs éventuelles métadonnées personnelles restent orphelins. **Correction proposée :** conserver explicitement les IDs restant à nettoyer, reprendre ce nettoyage même lors d’un rejeu identique et distinguer « liste remplacée, nettoyage incomplet » d’un import refusé. Ajouter un test d’échec de suppression suivi d’un rejeu. Constat sur le chemin d’erreur, non reproduit sur une base.

## 3. Tests

- **Exécuté, réussi** : `python -B wp/tests/demo/b10-verifier.py`. Les 25 empreintes, le raccord au bootstrap, le README et la cohérence des preuves archivées passent. Ce vérificateur ne réexécute pas les tests PHP ni le navigateur.
- **Rejeu PHPUnit tenté, bloqué** : commande Docker de `b10-local.py` exécutée directement, sans son écriture de journal, avec réseau désactivé et dépôt monté en lecture seule. WSL refuse le lancement : `Wsl/Service/E_ACCESSDENIED`, code de sortie 1. Aucun PHP n’est disponible dans le PATH. Les six tests PHP n’ont donc pas été rejoués indépendamment.
- **Preuves relues** : 6 tests PHPUnit / 27 assertions, 12 contrôles natifs et 26 contrôles navigateur réussis. La régression archivée annonce 1 175 tests / 36 407 assertions et 584 contrôles outils ; son signalement `A32_PARTIAL_EVIDENCE` concerne A-32.
- Les recettes nécessitant le site et la base n’ont pas été lancées, conformément aux droits du relecteur. Les tests existants couvrent notamment BOM, CSV multiligne, guillemets, doublons, refus sans données, rejeu, retrait du mapping personnel, nonce et droits. Ils ne couvrent pas les deux cas I1 et I2.

## 4. Sécurité et données

Pas de secret ni de donnée réelle identifié dans les éléments B-10 examinés. Import protégé par `manage_options`, POST, nonce et vérification du fichier téléversé ; taille bornée. Sorties publiques et administratives échappées. Les colonnes non mappées sont écartées, et retirer le mapping personnel masque immédiatement leur affichage. Le CPT est privé, exclu de la recherche et de REST ; aucune nouvelle voie de sortie de texte réservé identifiée.

Les preuves navigateur archivées montrent zéro requête tierce sur la page publique, carte éteinte comme allumée, avec témoins positifs des détecteurs. Les tentatives Gravatar de l’administration sont distinguées et bloquées. Ces observations n’ont pas été renouvelées ici. La conservation résiduelle après échec relève de I2.

## 5. Doctrine

Choix WordPress natif proportionné, logique de recherche/import séparée de l’adaptateur, espace de noms et préfixes respectés. La note donne les sources officielles du choix standard ; elles n’ont pas été ouvertes, l’accès à un site étant interdit à ce rôle.

**M1 — mineur — `wp/plugins/imagine-site/PointsVente.php:205`.** Les motifs techniques (`nombre_colonnes`, `champ_requis`, `syntaxe_csv`, etc.) sont injectés tels quels dans l’interface. Traduire seulement « Ligne %1$d : %2$s » ne rend pas le motif français ni traduisible, contrairement au §5 de la doctrine. **Correction proposée :** conserver les codes pour les tests et les convertir à l’affichage en libellés français traduisibles, sans inclure les valeurs du CSV.

## 6. Études (lots sans code)

Sans objet : lot de code. Le choix natif et les trois lignes relatives à une carte future sont présents ; aucun fournisseur n’est imposé.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun identifié.
- **Important :** I1, normalisation incomplète des accents ; I2, nettoyage non repris après échec de remplacement.
- **Mineur :** M1, motifs de refus à rendre en français traduisible.

Limite de vérification : seul le vérificateur local des sources et preuves a pu être exécuté avec succès ; le rejeu PHP reste à effectuer dans un environnement autorisé disposant du moteur de tests.
