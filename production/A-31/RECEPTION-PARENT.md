# A-31 — Réception réservée au parent, candidat sans PRET

## État livré et limites fermes

Écritures du worker exclusivement dans `wp/outils/bascule/a31/`, `wp/tests/a31/`, `production/A-31/` (et scratch). Aucun fichier commun modifié : les **deux lignes** `readme-ajout.txt` sont à ajouter par le parent dans `wp/tests/a02-audit/README.md`, une fois chacune ; le contrat ne scelle jamais le README partagé entier. Import A-28 lu seulement, y compris sa neutralisation générique ; ni changement ni mise en forme. Le gardien A-22 est réutilisé tel quel.

Le worker a réellement exécuté Python Windows, dont des sous-processus sur les deux pipes, refus cp1252, altérations de fichiers JSON/Markdown, mutations scratch de trois gardes et refus du reseal partiel. Les premiers RED observés étaient des fonctionnalités absentes (lanceur, projection, entrée production/déclaration et reseal) ; la régression « renouvellements standards encore lisibles après import » a été vue rouge avant correction. Les preuves de travail RED restent en scratch, pas un second paquet final.

`verification-python.json` pointe la dernière matrice locale réelle, ses compteurs et empreintes. Interpréteur découvert : `C:/Python314/python.exe`, **Python 3.14.6**, Windows ; ne pas remplacer par le Python 3.11 de `python` dans Git Bash. Les sondes mesurent stdout/stderr, locale, encodage préféré et mode UTF-8. Ce reçu reste **Python seul**. Le vérificateur de production sans argument répond honnêtement `A31_PARTIAL_EVIDENCE`, exit 1, tant qu'il n'existe pas de paquet natif complet scellé.

**Non exécuté par le worker** : PHP, lint/PSR-12, matrice classique/HPOS, code commercial installé, import sur clone, empreintes DB/fichiers, réseau/Action Scheduler natifs et commandes Docker/WSL. Le worker n'a lancé ni Docker, ni WSL, ni PHP Windows, ni préparation d'image. Le parent sérialise avec A-30 avant toute commande ci-dessous. Aucun PRET, aucune clôture et aucun GO réel n'est posé par ce candidat.

## Commandes exactes — depuis `C:/Users/Ced/imagine`

Les dossiers scratch de sortie doivent être neufs. Si un nom existe, ne changer que son suffixe. Ne jamais réutiliser un résultat ancien en vert. Les banques n'acceptent aucune URL/identifiant/site fourni par l'utilisateur : seulement leurs fixtures fictives internes, paquets commerciaux déjà autorisés et image épinglée, sans téléchargement ni montage.

### 1. Préparer l'image et ajouter les deux lignes communes (parent)

```sh
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
```

Ajouter ensuite exactement `production/A-31/readme-ajout.txt` au mode d'emploi partagé. La découverte T-02 trouve automatiquement `wp/tests/a31/unit.php` et relocalise les littéraux `/subject` et `/report` ; aucune nouvelle couche ni modification du collecteur n'est nécessaire. Le gate exige la vraie ligne `T01 TOOL : a31 ; ... controls ; 0 failures ; exit=0`, pas seulement le compteur global.

### 2. Mise en forme détenue puis gel

```sh
C:/Python314/python.exe -B wp/tests/a31/style.py --parent-serialized --fix --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-parent-style-fix-01
```

`--fix` n'écrit que les PHP A-31. Le worker a borné les lignes longues mais **n'a pas qualifié PSR-12**. Corriger toute erreur/avertissement restante, uniquement A-31. Le contrôle strict sans `--fix` est inclus dans la matrice finale ; toute correction postérieure invalide cette matrice. Rien dans l'import/commun pour obtenir du vert.

### 3. Matrice unique finale, Python et natif dans les deux consoles

```sh
C:/Python314/python.exe -B wp/tests/a31/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-parent-final-01
C:/Python314/python.exe -B wp/tests/a31/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-parent-final-01
```

Exiger **les deux exits 0**, tous les contrôles PASS et aucun stderr inattendu. Le premier exit ne suffit pas. Les cinq commandes mesurées sont Python UTF-8, natif UTF-8, Python cp1252, natif cp1252, PSR-12 strict. Chaque appel natif joue **classique puis HPOS**, sans concurrence.

Le runner prépare dans sa seule copie jetable un mutant K5=6 ; `red-unit.json` doit être rouge sur `renewal_five`, puis le code est restauré avant GREEN. Il exécute PHP pur sans extensions/écritures, les doubles de frontière WCS, l'inspection des sources Woo/WCS **installées avant le sujet**, et la vraie banque. Les empreintes installées n'ont pas été inventées depuis les branches GitHub.

#### Cases natives restantes, toutes à exécuter

- Un jeu à dix commandes : parent, renewal, switch, resubscribe, standalone, renewal orphelin, compte supprimé, état inconnu canari, relation opaque, relation tierce supprimable ; un refund séparé ; actif sans parent et annulé exclu. Un second jeu répète cinq fois les cas. L'année la plus ancienne est rare au premier jeu, visible au second.
- Quatre cellules à qualifier (classique/HPOS × UTF-8/cp1252). Pour chaque magasin : résultats nominaux, rejeu identique, ligne du mode d'emploi avec ses seuls arguments, jeu K5 et copie neutralisée.
- Dix-sept refus de canaux par magasin : stdout direct, stderr direct, affichage/exit, sortie silencieuse anticipée, trois shutdown, UTF-8 invalide, dépassement, exception, faux succès, JSON invalide/canari, Markdown, fichier supplémentaire, fichier partiel et JSON+Markdown altérés mais encore cohérents. Onze témoins sans gardien sont observés uniquement en RAM puis détruits ; jamais de canari conservé dans le paquet.
- Tentatives SQL via wpdb **et** mysqli, fichier du site, HTTP, mail, WP-Cron et les quatre planifications AS bloquées ; compte SQL SELECT-only et transaction lecture seule ; empreintes de toutes les tables (actions/logs compris) et de tous les fichiers identiques avant/après.
- Clone DB fictif : appel effectif `Engine::neutraliser()` puis `anonymiser()` de l'import gelé ; clé d'extension détruite, liens WCS standards et structure conservés ; inventaire post-import en lecture seule, empreintes clone/site stables.
- Sortie neuve hors site/dépôt, chemins refusés sans recopie, audit invalide/magasin contradictoire, PHP hors gardien refusé, permissions privées, fin réelle du processus et absence du conteneur propre vérifiées.

Ces listes décrivent des tests **préparés**, pas des réussites déjà mesurées.

### 4. Portes communes après le dernier gel

```sh
C:/Python314/python.exe -B wp/tests/a31/gates.py --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-parent-gates-01
```

Ce runner exécute sériellement : préparation canonique ; T-01/T-03 global sous environnements UTF-8 et cp1252 ; vérificateurs de production **sans argument** A-20, A-21, A-22 et A-28. Il contrôle les sorties et leurs exits, les sources figées, `T01_RESULT.pass`, aucun échec outils/paquets, présence réelle d'A-22/A-28 dans les paquets tentés et de l'unité pure A-31. Il ne modifie aucun de ces lots, aucun contrôle et aucun import.

Avant archivage, A-31 est normalement « hors rejeu : journaux absents » dans le collecteur T-03 : ses 28 journaux requis sont déjà déclarés, pas reconstruits. Les autres paquets ne sont pas déclarés hors rejeu de force. Si l'un des gates est rouge (255 compris), conserver le vrai reçu en scratch, diagnostiquer puis recommencer sur sorties neuves. Pas de détournement de compteur ni de déclaration qui contourne un test. A-22 reste **NON CLOS** jusqu'à sa relecture indépendante ; ce gate auteur n'est pas cette relecture et ne lève aucun GO réel.

### 5. Un seul paquet final, reseal puis vérificateur de production

```sh
C:/Python314/python.exe -B wp/tests/a31/reseal.py --parent-serialized --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-parent-final-01 --gates=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a31-parent-gates-01
C:/Python314/python.exe -B production/A-31/verify.py
```

`reseal.py` vérifie le candidat natif et les gates **avant toute publication**, refuse Python seul, vérifie que la déclaration énumère exactement tous les `.log`, copie uniquement les preuves réelles vers `production/A-31/preuves/final/` (gates dans ce même paquet), puis scelle tout A-31 sauf `manifest.json` lui-même et PRET. Le vérificateur de production exige ces empreintes, les gates et la matrice native complète. Aucun argument ni échappatoire `--python-only` à cette entrée.

Le reseal **refuse un final/manifeste déjà présent**, ne l'écrase pas et ne supprime rien. Pour refaire une réception périmée, le parent déplace explicitement l'ancien paquet/manifeste A-31 hors dépôt, après identification exacte, puis rejoue toute la chaîne sur sorties neuves ; aucun ancien paquet n'est promu en preuve du code changé. `verification-python.json` est un reçu de travail, pas un deuxième paquet natif.

Contrôle indépendant T-03 après le sceau :

```sh
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Exiger cette fois A-31 dans `T01_RESULT.packets.lots` sans échec ; cette sortie de réception indépendante appartient au parent, pas à une réécriture de ses gates antérieurs. Deux relectures, fusion, vérification indépendante, rapport global et éventuel PRET restent au parent. Ne pas écrire PRET sur ces seules commandes non exécutées.

## Résultats métier après import : précisément ce qui reste inconnu

**Seul `natures` est « inconnu après neutralisation ».** Le nettoyeur générique peut supprimer `_subscription_stripe_subscription_id` : une nature illisible avant import deviendrait faussement none si l'on oubliait cette provenance. Pas de zéro ou de classement par défaut.

Restent lisibles sous le contrat natif : années/états, renouvellements orphelins **aux références WCS standards numériques** (l'import ne supprime pas `_subscription_renewal`), parents originaux des actifs, comptes manquants, refunds/année, oldest protégé par K5. Une référence opaque n'est jamais normalisée en ID ; son nettoyage ne fabrique donc aucun lien numérique. La banque mesure ces conservations, pas seulement un drapeau « neutralisé » posé à la main.

**Défaut A-19 : vivant = active seulement**, exactement son filtre actif ; pas les quatre états d'A-20. Parent/root de tous les abonnements pour classer les commandes d'origine, mais seuls les actifs entrent dans « sans commande d'origine ». Aucun montant, ID ou jour/heure n'est exporté ; oldest rare reste `fusionne`, jamais l'année suivante visible.
