# Relecture indépendante Codex — A-04

Date : 25 novembre 2026. Périmètre : `briefs/A-04-mise-a-jour.md`, sources actives A-04 dans `wp/`, documentation et preuves dans `production/A-04`. Doctrine, grille et décisions lues. Le rapport de l'autre relecteur n'a pas été consulté. Aucune correction du code n'a été effectuée.

## 1. Conformité

L'ordre cœur → WooCommerce → Subscriptions → Memberships → autres extensions est explicite. Les archives sont locales et épinglées, les étapes et migrations sont journalisées, les verrous sont hérités par les enfants, le thème est exclu de la copie et aucun nettoyage général n'est effectué. Mode d'emploi, risques et `PRET` sont présents.

La restriction de preuve est annoncée correctement : pile complète de départ WP 7.0, essai séparé du refus natif de Subscriptions 9.4.1 sur WP 6.9.1, premium à versions constantes. Cela ne prouve ni les migrations premium historiques ni la montée de la pile réelle. Le seuil de sauvegarde de six heures et les limites des adaptateurs sont signalés comme choix techniques. Le brief ne cite pas de paragraphe numéroté du cahier des charges ; les références pertinentes examinées sont les §2.3, §3.9 et chapitre 11, avec les décisions des 11 et 19 novembre sur la conservation de l'existant et la bascule rejouable.

**I1 — important — `wp/outils/bascule/a04/update.py:132` : les autres extensions doivent artificiellement porter un fichier principal identique au nom du dossier.** Le membre recherché est systématiquement `<component>/<component>.php`. Une archive fictive valide `fiction-tools/main.php`, contenant les en-têtes d'extension et de version, est refusée avec `A04_PACKAGE_METADATA`. Le plan strict ne permet pas de déclarer ce fichier principal ; la lecture de version installée fait la même hypothèse. La fixture « reste » utilise précisément le seul cas accepté. Cela empêche de traiter des extensions dont le fichier principal possède un autre nom, même sans migration différée. **Correction proposée :** identifier de manière non ambiguë le fichier principal, ou l'ajouter explicitement au plan avec validation du chemin, puis utiliser cette identité pour le paquet et l'installation. Ajouter une fixture dont dossier et fichier principal diffèrent.

**I2 — important — `wp/outils/bascule/a04/update.py:235` : une interruption de dix minutes interdit la reprise automatique malgré le MU de maintenance persistant.** `maintenance(site)` exige un horodatage `.maintenance` inférieur à 600 secondes avant de lire le checkpoint ou de vérifier le MU persistant. Après un arrêt prolongé, le même appel rend `A04_MAINTENANCE` sans reprendre ; `refresh_maintenance()` est inaccessible. La documentation mentionne ce préalable, mais la reprise nécessite donc une intervention supplémentaire, y compris lorsque le site reste effectivement fermé en HTTP 503. **Correction proposée :** distinguer démarrage et reprise ; pour un état valide lié au site et au plan, vérifier la présence et l'intégrité du MU persistant, puis rafraîchir la maintenance sous verrou avant tout bootstrap. Conserver le refus sans cette garantie. Tester une reprise après plus de 600 secondes, avec sauvegarde encore valide, ainsi que le refus si le MU a disparu.

## 2. Exactitude métier

Deux cas déroulés à partir du §3.9 et de la conservation de l'existant, puis confrontés aux photos fictives avant/après du paquet `production/A-04/preuves/9c204eb862d6` :

- **Abonné actif :** l'utilisateur fictif 3 possède l'adhésion 13 active et l'abonnement 14 actif. L'accès `3:10` doit rester ouvert et l'échéance ne doit pas être déplacée. Les photos classique et HPOS conservent l'accès à `true`, le statut, la périodicité et `next_payment_utc = 2027-02-01 10:00:00`.
- **Abonnement expiré :** l'utilisateur fictif 5 possède l'adhésion 17 expirée et l'abonnement 18 expiré. La mise à jour ne doit ni réactiver le droit ni recréer une échéance. Les deux stockages conservent `5:10 = false`, les statuts expirés et l'échéance à zéro.

Les objets `memberships` et `subscriptions` sont identiques avant/après dans les deux stockages. Il s'agit de preuves archivées contrôlées en lecture, pas d'un nouveau test sur site. A-04 ne recalcule pas de calendrier : les frontières de clôture et le changement d'année relèvent ici de la conservation des valeurs. Le rejeu identique est documenté par les reçus ; la reprise différée reste défectueuse selon I2.

## 3. Tests

**Tests lancés pendant cette relecture :**

- `python -B -m unittest discover -s wp/tests/a04 -p 'test_*.py' -v` : sortie 1. La suite n'est pas validée dans cet environnement Windows : refus d'accès aux fichiers temporaires (`PermissionError`) et chemins POSIX `/package.zip` non absolus pour `WindowsPath`, ce qui provoque notamment `A04_PACKAGE` avant les assertions attendues. Ces résultats ne sont pas présentés comme des régressions de l'outil Linux.
- Même découverte via `wsl.exe -d Ubuntu -- python3 -B ...` : sortie 1 avant exécution, `Wsl/Service/E_ACCESSDENIED`. Aucun rejeu Docker/PHP/intégration n'a donc pu être effectué. Le lanceur `run.py` n'a pas été utilisé directement, car il écrit systématiquement hors du seul rapport autorisé, dans `production/A-04/preuves`.
- Trois sondes unitaires ponctuelles, sans fichier de test ajouté : **3/3 réussies** pour reproduire les comportements I1, I2 et I3. Archive ZIP en mémoire pour I1 ; horloge ancienne et objet fichier simulé pour I2 ; fichier source local utilisé comme contenu fictif de sauvegarde pour I3. Ce sont des reproductions ciblées, pas une validation d'intégration.

**Preuves du producteur contrôlées :** les 15 empreintes de `sources.json` et les 15 empreintes de `dependencies.json` du paquet final correspondent aux fichiers présents. `unit.log` annonce 32 tests réussis ; `result.json` contient 70 contrôles réussis ; `runner.json` contient huit contrôles réussis et une sortie 0, dont les trois lints PHP. Les comparaisons A-03 archivées classent uniquement les quatre changements attendus ; l'aller-retour production fictif est identique.

La couverture dépasse le nominal : sauvegarde périmée, concurrence, enfant survivant, SIGKILL, callback falsifié, classique et HPOS. Elle ne couvre pas les trois cas signalés. Les arrêts de reprise documentés sont courts ; ils ne valident pas une reprise après expiration de `.maintenance`.

## 4. Sécurité et données

**I3 — important — `wp/outils/bascule/a04/update.py:96` : la localisation de la sauvegarde est vérifiée lexicalement, pas sur sa destination réelle.** `file.is_relative_to(site)` accepte un chemin extérieur en apparence contenant `..`, alors que sa résolution désigne un fichier dans le site. Reproduction sans écriture : site fictif égal au dossier `wp`, chemin `doctrine/../wp/outils/bascule/a04/update.py` rendu absolu, hash exact ; `check_backup()` accepte ce fichier alors que `resolve().is_relative_to(site.resolve())` vaut `True`. Un lien dans un répertoire parent pose également problème : `is_symlink()` ne vérifie que le dernier élément. La garantie « sauvegarde hors du site » est donc contournée. **Correction proposée :** contrôler les chemins canoniques des deux sauvegardes, refuser leur présence dans le site et appliquer explicitement la politique concernant les liens dans les parents. Ajouter les cas `..` et répertoire parent symbolique aux tests de refus.

Aucun secret ni donnée réelle identifié dans les fichiers examinés. Les garde-fous mail/HTTP/paiements et le refus de queue globale sont présents ; les limites face aux appels réseau directs sont documentées. Aucune nouvelle route HTTP ni voie de paywall n'est ajoutée par ce lot. Aucun site, compte, service externe ou base n'a été consulté pendant la relecture.

## 5. Doctrine

L'orchestration réutilise les mécanismes natifs de migration et ne modifie pas les sources tierces. Les PHP A-04 portent `strict_types=1` et l'espace de noms `Imagine\Bascule`. Le recours à Python pour l'orchestration est explicite. Les limites de qualification sont distinguées de l'autorisation d'agir sur le réel. Les défauts I1 à I3 demandent des corrections techniques et leurs preuves, pas un arbitrage métier.

### Décisions techniques, défaut proposé

Appliquer les corrections proposées avec refus prudent en cas d'identité d'extension ambiguë, de maintenance persistante non vérifiable ou de sauvegarde située dans le site. Hermès peut les mettre en œuvre sans attendre ; Claude arbitre après coup. Aucune question visuelle, métier ou touchant au réel à adresser à Ced pour cette relecture.

## 6. Études (lots sans code)

Sans objet : lot de code. `production/A-04/sources.md` fournit les références officielles et décrit les API natives inspectées par le producteur. Les pages externes n'ont pas été consultées pendant cette relecture, conformément au périmètre local imposé.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut classé à ce niveau dans le périmètre examiné.
- **Important :** I1, identification du fichier principal des extensions ; I2, reprise après expiration de la maintenance native ; I3, contrôle canonique de l'emplacement des sauvegardes.
- **Mineur :** aucun point supplémentaire retenu.

Le rejeu complet indépendant reste non effectué en raison des restrictions d'exécution décrites. Ce verdict n'est ni un GO, ni une autorisation de mise en ligne ou d'accès au réel.
