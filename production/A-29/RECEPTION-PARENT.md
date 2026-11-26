# A-29 — Réception réservée au parent

**Livraison locale partielle, sans `PRET`.** Écritures du worker limitées à `wp/outils/bascule/a29/`, `wp/tests/a29/`, `production/A-29/` et au scratch Hermes. A-22, les autres lots, la file, les verrous, le README commun et l'import sont inchangés par ce worker. Aucun Docker, WSL, PHP Windows, Git, site réel, compte, archive ou Novamira exécuté/utilisé. Les commandes Docker ci-dessous sont des commandes **fournies, non exécutées**.

## Ce qui est réellement prouvé localement

- Python découvert et utilisé : **`C:/Python314/python.exe`, 3.14.6** ; pas la version annoncée par défaut. Locale Windows `cp1252`. Deux contextes mesurés : stdout/stderr UTF-8 + mode UTF-8 1 ; stdout/stderr cp1252 + mode UTF-8 0.
- Suite complète : **42 tests verts dans chaque console**. Les sous-processus fixent explicitement leur encodage. Le gardien A-22 est réellement utilisé sur des enfants Python, les deux pipes et un descendant conservant leurs handles ; aucun changement du gardien.
- RED/GREEN : trois refus initialement rouges sans lanceur, puis verts ; schéma initialement rouge, puis vert. Le paquet final contient en outre, **dans les deux encodages**, un vrai cycle baseline GREEN → mutation K5 RED (code 1, assertion nommée) → restauration exacte GREEN, dans des copies jetables ; journaux et empreintes sous `red-python/`.
- Le parcours réel de publication Python est exercé avec **doubles explicitement déclarés des frontières PHP et noyau** : affichage/arrêt, stdout, stderr, shutdown et fichiers. Retirer seulement la liaison finale permet effectivement l'altération de nombres en JSON/Markdown valides dans le miroir ; retirer seulement le schéma permet une clé privée. Ce ne sont pas des preuves PHP, Landlock, DB ou WordPress.
- Un seul paquet local dans `preuves/partiel-python/`, vérifié avec `--python-only`, jamais un paquet natif. Le sceau `manifest-python-partiel.json` ne revendique aucune disponibilité. Les empreintes des dépendances sont une **photographie**, pas une promesse qu'A-28 ne les changera plus.

Aucune assertion PHP ni native n'est comptée comme exécutée. Standard installé, syntaxe et PSR-12 PHP, oracles classique/HPOS, immutabilité DB/fichiers, absence d'exécution des tâches et de sortie réseau **restent à qualifier**.

## Commandes exactes — depuis `C:/Users/Ced/imagine`

Tous les dossiers de sortie doivent être neufs. Si un nom existe, changer seulement son suffixe. Sérialiser toutes ces commandes avec le parent : **attendre la fin d'A-28 et geler `staging/`**, ses dépendances et les sources A-29 avant la matrice. Ne pas rescell­er des reçus exécutés sur un ancien `lib.php` en remplaçant simplement leurs empreintes. Toute modification d'une dépendance exige une nouvelle matrice complète ; aucun contournement de l'import.

### 0. Intégration parent et préparation

Le parent colle lui-même les **deux lignes exactes LF**, une seule fois chacune, de `production/A-29/readme-ajout.txt` dans `wp/tests/a02-audit/README.md`. Le vérificateur compare uniquement ces lignes, jamais l'empreinte globale du fichier ; les autres lots sont autorisés avant/après. La banque `unit.php` est découvrable par T-02/T-01 selon la convention existante, sans modifier leur code ni inventer une suite PHPUnit.

```sh
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
```

Cette préparation commune n'a pas été lancée ici. Elle ne doit être lancée que par le parent autorisé. Aucun paquet commercial nouveau ni accès au réel : réemploi du banc fictif et des sources sous licence déjà autorisées d'A-02.

### 1. Style détenu A-29, avant gel final

```sh
C:/Python314/python.exe -B wp/tests/a29/style.py --parent-serialized --fix --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-parent-style-fix-01
```

Le correcteur n'écrit que le PHP A-29. Un échec ou avertissement n'est pas un succès. Après toute correction, refaire la matrice entière ; son contrôle PSR-12 est strict et sans `--fix`.

### 2. Matrice finale complète, puis son vérificateur

```sh
C:/Python314/python.exe -B wp/tests/a29/matrix.py --include-native --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-parent-final-01
C:/Python314/python.exe -B wp/tests/a29/verify.py --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-parent-final-01
```

Exiger **les deux codes zéro**, les sources exécutées égales aux sources courantes, les dépendances identiques, aucun stderr inattendu et tous les contrôles PASS. Cinq commandes principales mesurées : Python UTF-8, natif UTF-8, Python cp1252, natif cp1252, PSR-12 ; les contrôles RED/GREEN Python sont conservés à part dans le même paquet. Le runner exige le drapeau parent, utilise une image existante épinglée, `--pull never`, réseau `none`, aucun montage ni port, et supprime seulement son conteneur exact après vérification de propriété. Il ne lance aucun PHP hôte.

Banques préparées : PHP pur sans extensions tierces ni fonctions d'écriture ; mutation renouvellement→autre rouge puis restauration ; lecture installée avec empreintes avant le sujet ; WP-Cron + AS ; retards stricts à l'audit ; huit fenêtres UTC, égalité audit/semaine/horizon et fuseau non UTC ; un puis cinq exemplaires ; statuts et familles fermés ; extension active inconnue **et** hook orphelin, sans attribution supposée ; commande du README avec ses seuls arguments ; tous les canaux, dont fichier JSON/Markdown encore valides altérés au shutdown ; témoins confinés sans gardien jetés ; empreintes de toutes les tables et fichiers ; tentatives SQL direct/indirect, fichier, HTTP, email et quatre planifications AS refusées ; callbacks sentinelles non exécutés. Un clone fictif traverse le moteur commun inchangé : WP-Cron effacé, AS pending annulé, failed supprimé, puis tous les comptes A-29 inconnus et copie immuable.

`standard.php` est un contrôleur **lexical** des sources réellement installées, avec SHA-256, complété par les API natives de création/lecture des fixtures. Le worker ne lui attribue pas un succès non observé. S'il refuse une version ou une composition de hook différente, inspecter cette source installée et corriger seulement la correspondance ou l'oracle détenu A-29 avec nouvelle preuve ; ne pas assouplir l'attribution, les canaris, les permissions ou la neutralisation. Un échec dans l'import après A-28 reste un vrai échec à diagnostiquer avec son propriétaire.

Diagnostic PHP pur facultatif, ne remplaçant rien :

```sh
C:/Python314/python.exe -B wp/tests/a29/run.py --parent-serialized --unit-only --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-parent-pure-01
```

### 3. Portes communes après le dernier gel

```sh
C:/Python314/python.exe -B wp/tests/a29/gates.py --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-parent-gates-01
```

Le wrapper rejoue réellement, en série : préparation d'image, `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` dans les deux contextes d'encodage, puis les trois vérificateurs **avec argument positionnel** : `wp/tests/a20/verify.py production/A-20/preuves/final`, idem A-21 et A-22. Les PS1 existants forcent leur sortie UTF-8 ; ce contrôle n'est pas présenté comme une autre console Python cp1252. Le wrapper lie les journaux, garde les codes réels, exige la ligne finale REJEU PASS non vide et refuse tout résultat de paquet non vert. Si une dépendance a périmé un paquet commun, le parent le rejoue selon son propre périmètre ; A-29 ne le modifie ni ne le rescell­e à sa place. A-22 n'est pas déclaré clos par ces portes : son rejeu indépendant de relecture reste distinct.

### 4. Paquet unique et scellement, seulement après tous les verts

Déplacer le paquet **partiel** intact hors dépôt, ne pas le confondre avec la matrice native ; les trois commandes suivantes n'écrivent que le lot A-29 et le scratch :

```sh
C:/Python314/python.exe -B -c "from pathlib import Path; import shutil; d=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-local-historique-01'); d.mkdir(exist_ok=False); p=Path('production/A-29'); [shutil.move(str(p/n),str(d/Path(n).name)) for n in ['preuves/partiel-python','manifest-python-partiel.json','verification-python-partielle.json'] if (p/n).exists()]"
C:/Python314/python.exe -B -c "import shutil; shutil.copytree('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-parent-final-01','production/A-29/preuves/final')"
C:/Python314/python.exe -B -c "import shutil; shutil.copytree('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-parent-gates-01','production/A-29/portes')"
C:/Python314/python.exe -B wp/tests/a29/verify.py --evidence=production/A-29/preuves/final
C:/Python314/python.exe -B wp/tests/a29/seal.py --evidence=production/A-29/preuves/final --gates=production/A-29/portes/parent-gates.json
C:/Python314/python.exe -B wp/tests/a29/seal.py --check
```

Avant ce sceau final, le parent actualise le rapport court de cette livraison partielle, sans effacer ses limites historiques. Le scellement refuse un paquet partiel encore présent, des portes absentes/périmées, les liens symboliques et un sceau déjà existant ; les reçus d'échecs ou sceaux antérieurs vont au scratch historique, jamais réétiquetés verts. Le contrôle `--check` compare l'inventaire exact et les empreintes, puis rejoue le vérificateur de paquet. Aucun de ces outils ne crée `PRET`. Deux relectures, fusion et vérification indépendante restent nécessaires ; clôture et éventuel signal de relecture appartiennent au parent/Claude, jamais un GO réel.

## Défauts prudents / limites fonctionnelles

- Huit semaines = huit périodes UTC glissantes de sept jours, pas des semaines civiles partielles. Seules les prochaines occurrences déjà stockées sont comptées, sans extrapoler les récurrences. Égalité à l'audit : pas en retard ; égalité à audit+56 jours : exclue.
- WP-Cron n'a pas d'historique d'échec : la section failed est explicitement AS seulement. Elle ne prétend pas que les événements WP-Cron n'échouent jamais.
- L'auteur de planification d'une tâche inconnue n'est pas récupérable de manière probante à partir de son nom, groupe ou callback : **attribution indéterminée**, pas un compte inventé d'extensions actives. C'est une limite du nombre demandé, non un détecteur d'extension fiable.
- L'import rend tous les nombres demandés inconnus sur la copie neutralisée ; aucun compte utile n'est reconstitué. L'import n'est pas modifié et aucun procédé de lecture de la source réelle n'est autorisé à l'agent.
- K5 : petites cellules fondues sans noms, petits scalaires masqués, aucun hook libre, argument, ID ou date individuelle dans les rapports. La date globale de l'audit reste publiée pour définir l'horloge.
- Toute preuve Python locale doit être relue contre les dépendances courantes : A-28 peut encore les changer. Une empreinte ancienne honnêtement conservée n'est pas une qualification du code futur.
