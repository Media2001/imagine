# Relecture indépendante Codex — A-11

Date : 26 novembre 2026. Référence : `briefs/A-11-inventaire-des-adresses.md`, cahier des charges §4.3, lignes 1104–1105, doctrine et grille de relecture. Périmètre : sources A-11 dans `wp/`, dépendances A-02/A-09 utiles à leur lecture et livraison `production/A-11/`. Le rapport Claude n'a pas été consulté. Aucun fichier autre que ce rapport n'a été modifié.

## 1. Conformité

Les livrables demandés sont présents : commande, suite dédiée, deux lignes dans `wp/tests/a02-audit/README.md:63`, rapport de production et `production/A-11/PRET`. Le CSV contient les champs attendus ; les adresses sont relatives et les générateurs WordPress/WooCommerce sont employés sans crawl. Aucune redirection n'est décidée. Les choix concernant les collisions d'adresses, les dates absentes des archives, les pièces jointes et le périmètre des auteurs sont explicités dans le README et l'intégration.

**A11-C1 — important — Configuration personnalisée acceptée mais non reproduite.** Fichier : `wp/outils/bascule/a11/Runtime.php:19`.

Le refus des configurations non standard omet notamment `WPMU_PLUGIN_DIR`. Le parseur A-02 ne conserve que les quatre paramètres de connexion et le préfixe des tables ; le reste du fichier de configuration n'est pas exécuté. Une définition littérale de `WPMU_PLUGIN_DIR` est donc silencieusement perdue. Si une extension obligatoire placée dans ce dossier enregistre un type public ou filtre ses permaliens, le bootstrap de l'inventaire ne la charge pas : ses adresses disparaissent ou changent, sans refus de l'export. Cela contredit le refus annoncé des personnalisations de chemins et compromet l'inventaire du site demandé par le §4.3.

Correction proposée : refuser explicitement cette personnalisation avant le bootstrap, conformément au périmètre standard annoncé, et compléter le contrôle des constantes de disposition prises en charge ou refusées. Ajouter un cas fictif où un dossier MU personnalisé contient l'enregistrement d'un type public : l'outil doit refuser la configuration avant de produire un paquet. Constat de lecture du code, non reproduit sous PHP pendant cette relecture.

## 2. Exactitude métier

Deux cas du périmètre §4.3/brief ont été déroulés à partir du jeu fictif, des branches de collecte et des sorties conservées :

- **Publications et exclusions, variante `classic-pretty`.** Le brouillon incrémente `draft`, la page privée incrémente `private`, l'article protégé incrémente `password` ; chacun s'arrête avant la génération de son adresse. La pièce jointe du parent protégé incrémente `attachment_parent_not_public`. Le résumé contient bien quatre compteurs à 1 et aucune de ces adresses. Il reste 25 adresses uniques ; `/a11-shop/` conserve les contextes page et archive produit dans une seule ligne. Les comptes par nature totalisent 26, ce qui est cohérent avec leur caractère non additif documenté.
- **Désactivation des pages de pièces jointes.** Les trois pièces jointes publiques de la variante précédente sont retirées, y compris la pièce jointe sans parent et celle dont le parent manque ; `attachment_pages_disabled` passe à 3. Le total passe de 25 à 22, le parent protégé reste compté séparément. Les mêmes résultats figurent dans les preuves HPOS. L'accueil statique conserve aussi une seule ligne pour la page des articles et son contexte d'archive.

Les dates de clôture, changements d'année et calendriers de parution ne gouvernent aucune règle de ce lot. Le rejeu à données constantes est couvert dans le paquet ; les archives et termes restent sans date inventée.

**A11-C2 — important — Une erreur SQL peut devenir un inventaire incomplet déclaré réussi.** Fichier : `wp/outils/bascule/a11/Inventory.php:58`.

La collecte utilise directement le tableau renvoyé par `wpdb::get_col()` sans contrôler l'échec de la requête. Une erreur de lecture sur `posts` peut se traduire par un tableau vide, comme une absence légitime de contenus. Les erreurs SQL sont supprimées de l'affichage par `ReadOnlyDb` et aucune exception n'est levée pour cet échec. La collecte peut donc poursuivre avec zéro contenu et zéro exclu pour le type concerné, puis publier les fichiers et retourner `A11_OK`. Par exemple, un compte SQL pouvant lire les options mais dépourvu du droit SELECT sur `posts` ne doit jamais produire un inventaire validé comme vide.

Correction proposée : distinguer explicitement une lecture réussie sans résultat d'une lecture échouée, immédiatement après cette requête, et interrompre l'export avec un code fixe sans SQL ni données. Prévoir également une propagation fiable des erreurs des lectures natives nécessaires à la collecte. Ajouter un test d'échec SELECT exigeant un code non nul et l'absence de paquet validé. Constat de lecture du code, non reproduit sous PHP pendant cette relecture.

## 3. Tests

- **Exécuté, sortie 0 :** `python -B wp/tests/a11/verifier.py production/A-11/preuves/f77a1fcd8945`. Le vérificateur confirme la concordance des sources actuelles et des preuves : 13 contrôles unitaires, 284 natifs et 7 du runner enregistrés comme réussis ; 14 fichiers sources A-11 vérifiés.
- **Exécutés sans écriture :** 50 contrôles directs supplémentaires des dix variantes conservées : comparaison des adresses/contextes à l'oracle, validation avec la fonction A-09 inchangée, comptes d'exclus, correspondance CSV/JSON et égalité des empreintes avant/après. Tous réussissent. Les empreintes des 164 fichiers référencés par le manifeste A-11 correspondent également.
- **Rejeu natif indisponible dans cette session :** le contrôle préalable de l'image du banc par `wsl.exe -d Ubuntu -- docker image inspect …` échoue avec `Wsl/Service/E_ACCESSDENIED`, code 1. Aucun PHP Windows n'est disponible dans le PATH. La suite native n'a donc pas été relancée ; les résultats natifs ci-dessus sont ceux des preuves livrées, pas une nouvelle exécution. Aucun nouveau paquet ni fichier de test n'a été créé.

La couverture existante dépasse le nominal : classique/HPOS, cinq configurations de permaliens et d'affichage, exclusions, collisions, requêtes filtrées, sorties interdites, configuration DB dynamique, drop-in et refus d'une URL externe. Les deux défauts C1/C2 ne sont pas couverts. Les cas de contenus de l'oracle sont explicitement choisis ; certaines attentes de taxonomies reprennent toutefois le même parcours natif que la collecte et ne constituent pas un contrôle indépendant de son exhaustivité.

## 4. Sécurité et données

Aucune donnée réelle ni secret identifié dans les fichiers examinés ; les fixtures emploient des données manifestement fictives. Les sorties n'incluent ni corps d'article, ni nom ou email d'auteur, ni coordonnées de client. Aucune voie de rendu du paywall n'est ajoutée par ce lot.

Les requêtes par type sont préparées. Les sorties sont refusées dans le site ou le dépôt, avec contrôle du parent résolu ; les fichiers sont créés exclusivement et les permissions restrictives sont testées sous Linux. Le CSV neutralise les préfixes de formule. L'outil est une commande CLI, sans formulaire nécessitant un nonce.

Les preuves conservées attestent l'égalité des empreintes des tables, le refus d'écriture, le blocage HTTP/mail/cron et la stabilité des fichiers sur le banc. Le README décrit correctement la nécessité du confinement système pour le code tiers arbitraire. Ces preuves ne qualifient aucun site réel. C2 reste à corriger pour que l'échec d'une lecture ne soit pas présenté comme un résultat sûr et complet.

## 5. Doctrine

Les générateurs natifs sont réutilisés ; le périmètre spécifique est le rassemblement, la normalisation A-09 et l'export. Les classes du lot portent `declare(strict_types=1)` et l'espace de noms `Imagine\PublicAddresses`. Le README décrit l'usage, les limites et les tests. Aucune modification d'extension tierce n'est nécessaire.

### Décisions techniques, défaut proposé

C1 et C2 relèvent de la technique. Défaut prudent proposé : refuser une configuration de chemins non qualifiée et interrompre l'export sur une erreur de lecture, sans publier un résultat partiel. Ces corrections ne nécessitent pas d'arbitrage métier ou visuel de Ced.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références officielles annoncées dans le README ont été lues comme documentation de livraison, sans consultation externe ni nouvelle validation de ces pages.

## Verdict

**À corriger.**

- **Bloquant :** aucun point classé dans cette gravité.
- **Important :** C1 — dossier MU personnalisé silencieusement ignoré ; C2 — erreur SQL assimilable à une absence de contenus.
- **Mineur :** aucun point supplémentaire retenu.

Le contrôle des preuves réussit, mais il ne couvre pas ces deux défauts ; le rejeu natif reste à effectuer dans un environnement disposant de WSL. Ce verdict n'est pas un GO.
