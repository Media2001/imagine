# A-28 — réception et limites

## Périmètre

La liste fermée et ses sources officielles figurent en dix points dans `standard.md`, avec les reçus de récupération dans `official-sources.json`. Elle couvre six tables de données Fluent Forms et deux types de contenu Flamingo, avec leurs révisions et métadonnées. Le formulaire Contact Form 7 (`wpcf7_contact_form`), ses réglages, le magazine et les types hors liste ne sont pas supprimés. Ni extension nouvelle, ni heuristique générique sur « form » ou « message », ni lecture de l'archive d'Imagine.

La politique obligatoire est un seul JSON versionné, transmis dans le vrai payload de l'import pour les lecteurs Python et PHP. Une table connue ne se conserve ni par `garder` ni par `anonymiser` : seul `vider` est admis. Le refus Python donne `sql_preflight / FORM_MESSAGES_DECISION_REFUSED / table` ; le refus PHP réel donne `native_neutraliser`, le même code et un suffixe technique fermé, sortie 78. Il n'ajoute pas la dernière table arbitraire visitée par PDO. Le reste du diagnostic A-01 garde son ancien contrat.

Le compteur `form_message_residues` s'ajoute au rapport de vérification ; une valeur positive produit `FORM_MESSAGES_REMAIN`, sortie 1, sans amorcer WordPress. La relecture après la sonde contrôle aussi un résidu créé pendant le chargement. La suppression se fait dans les transformations de neutralisation/anonymisation existantes, sans nouveau parcours ni commande de Ced.

## Preuve avant correction

`preuves/final/before/native.json` est la vraie exécution ancienne, sur six imports complets classique/HPOS d'archives fabriquées dans le runner : **108 contrôles verts**, qui attestent le défaut, pas sa correction. Par défaut les six tables connues et la table inconnue sont vides, mais les deux types Flamingo et quatre métadonnées canaris restent. Avec `garder` sur la table connue, son canari reste ; avec `garder` sur la table inconnue, celui de cette table reste. Le type fictif inconnu reste dans tous les passages. Les empreintes de l'ancien import et son runner supprimé sont conservés ; ses deux sources PHP authentiques sont dans `reference/` pour le test différentiel, pas dans le runtime livré.

Un `garder` est une décision **de table** dans A-01 ; il n'existe pas de décision par type de contenu. Aucun faux réglage par type n'a été inventé pour ce banc.

## Preuves corrigées et commandes de relecture

Le paquet courant est uniquement `preuves/final`. Son vérificateur en lecture seule ne prend aucun argument :

```powershell
C:/Python314/python.exe -B production/A-28/verify.py
```

Les matrices et portes exécutées sont décrites dans `RESULTATS.md`. Rejeu explicite du banc sur une sortie neuve, hors des preuves reçues : `python -B wp/tests/a28/matrix.py --output "$SORTIE_NEUVE"`. Il effectue de vrais imports complets dans les deux environnements Windows ; PHP n'est jamais lancé sur Windows. La copie vers `/subject` utilise le payload A-01 réel, pas une liste de dépendances parallèle cachée. Le parseur historique et les suites sont transportés à leur chemin canonique, et la suite diagnostique PDO a une vraie base fictive à contrainte unique.

Les témoins de mutation retirent réellement le seul blocage spécifique dans la copie **du conteneur** : chaque résidu est refusé, passe sous mutation, puis est refusé après restauration exacte de `lib.php`. Les canaris ne sont pas publiés. Les refus `garder` sont aussi appelés par le vrai CLI PHP, avec empreintes SQL et fichiers identiques avant/après. Un différentiel en deux processus PHP compare l'ancien et le nouvel import sur un jeu hors formulaires : tables, rapport (hors nouveau compteur zéro) et anciens diagnostics sont strictement identiques.

Les essais rouges, erreurs de montage du banc et rejeux intermédiaires restent en scratch ; `red-green.json` donne leurs handles et empreintes. Le premier global UTF-8 a réellement échoué dans `RetractationAdapterTest`, hors périmètre, tandis que les sources A-28 étaient stables ; aucun fichier de ce lot voisin n'a été corrigé ici. Les neuf portes ont été entièrement rejouées sous un dossier neuf, toutes vertes, sans changement des sources gelées. L'échec initial reste dans `scratch/a28-work/global-gates-first-red`, pas rebaptisé PASS. Le paquet d'avant correction est une preuve historique explicitement nécessaire au brief, pas une qualification du code actuel.

## Hors liste : question fermée

**Faut-il supprimer également les types de contenu hors liste : oui ou non ?** A-28 n'en décide rien : le comportement A-01 est conservé. Le canari du type fictif `fiction_magazine`, ses révisions et ses métadonnées restent exactement identiques après import. Une table inconnue reste vide par défaut et peut encore être conservée par la décision existante `garder` lorsqu'A-01 l'admet. Ce lot ne prouve donc pas une anonymisation universelle de tous les messages possibles, des pièces jointes, des taxonomies libres ou d'autres extensions. Leur qualification reste nécessaire ; ne pas transformer ce PRET en GO sur le réel.

## Limites et voisins

Banc WordPress/WooCommerce réel de l'image locale A-01, avec tables Fluent et contenus Flamingo **entièrement fictifs** ; aucun site partagé, compte réel, service commercial ou nouvelle compatibilité de version n'est qualifié. Pas de publication web/Novamira. Les réglages/rendus de formulaires, champs, SEO, commandes et fichiers retenus sont comparés dans chaque import réussi ; les commandes de Ced sont comparées byte pour byte, avec seulement les trois lignes autorisées ajoutées au README de l'import.

Les dépendances historiques d'A-21 à A-27 ne qualifient plus l'import courant ; A-20 passe encore. Les vrais refus, les cas précis et les commandes de rejeu parent figurent dans `REJEUX-PARENT.md`. **Aucun de ces paquets n'est rescellé ici.** Le gardien commun est intact, la réserve indépendante d'A-22 n'est pas levée, les PRET voisins ne sont ni retirés ni réécrits. La photographie initiale a observé des changements concurrents dans trois fichiers des racines de la voie 2 : `scope.json` conserve leurs empreintes originales et courantes séparément, sans les réécrire ni les attribuer à A-28. Le premier scellement a réellement refusé cette différence de propriétaire ; le contrôle de périmètre a été corrigé dans A-28, puis les matrices natives et portes entièrement refaites sur ce dernier code d'empaquetage. Aucun fichier d'orchestration, autre lot ou voie 2 n'est modifié par A-28 ; le verrou commun est seulement rafraîchi, pas libéré.
