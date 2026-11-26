# A-22 — checkpoints de reprise

## 2026-11-26 18 h 16 CET — fusion de 17 h 53, reprise non PRET

Les PRET A20/A21/A22 de 17 h 06 sont retirés, conservés sous `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a22-corrections-1753/`. Aucun PRET ne sera créé par cet enfant. Les paquets 07/04 ci-dessous sont désormais **historiques**, pas des preuves des sources corrigées.

TDD réel sous `C:/Python314/python.exe` : onze sous-échecs reproduits (nom A12, couverture A03, contamination des neuf rapports), puis refus de compteur JSON A03 et absence du lien final reproduits ; reçus RED en scratch. Les **24 tests Python A22 passent réellement** après correction. Les commandes réelles des sept frontends A12/A14–19 gardent leurs codes invalid-name ; A14 garde son repli fermé A14_FAILED. A03 est empreinté sous `a03`, chaque racine attendue absente est refusée, mutation Policy.php sur miroir détectée.

Rapports : contrats propres de format/comptes JSON, cohérence Markdown/JSON et CSV/comptes ; aucun contenu inconnu n'est publié. Un callback commun enregistré par auto_prepend **avant le code du site** lie les octets des fichiers terminés ; le parent vérifie ce lien seulement après les deux EOF et la fin de PHP. Une contamination en shutdown, même valide syntaxiquement, invalide le lien. Le petit protocole interne n'est jamais réémis à l'opérateur. Deux canaris fichiers réels (Markdown/CSV/JSON et JSON valide contaminé) et un témoin sans validations finales s'ajoutent aux sept canaris de flux. Les comptes métier et les rapports nominaux restent inchangés.

Sondes natives A03 et A12 terminées à code réel 0 ; A12 prouve aussi le droit exclusif WRITE_FILE sur /dev/null hors sortie privée, douze opérations noyau dont création, troncature, ajout, renommage, unlink, mkdir/rmdir et second périphérique interdit. Tous ces chemins sont synthétiques jetables ; aucun test RED ne vise un site. Les mutations témoins n'existent qu'en conteneur/scratch et aucun octet canari brut n'est gardé.

Sources figées pour les matrices **neuves**, réellement lancées : `matrix-final` (proc_58099c8cc9dd), `a20-matrix-final` (proc_c48317d807d0), `a21-matrix-final` (proc_3e619b22b55d), sous le même scratch. En cours, aucun verdict anticipé. Style initial : trois erreurs PSR12 réelles de mise en page du nouveau fichier PHP, corrigées ; nouveau style final réellement lancé (proc_8b2274d7a1d2), pas encore déclaré vert. Aucune préparation globale, T01 global, écriture README partagé, verrou parent, A23/24/25 ou voie2.

Rattachement §4.4/§2.5 **analogique** à la promesse de confidentialité des sorties, pas une règle métier/comptable nouvelle. Dette laissée conformément à la fusion : duplication des enclos A20/A21 et granularité de délai A20. La ligne error_log est fournie dans `readme-ajout.txt` (deux lignes exactes au total), à intégrer par le parent, jamais par empreinte du README entier.

## 2026-11-26 14:18 CET — périmètre et décisions

Lecture intégrale : A-FAIRE révision 13h30, arbitrages passage 13h, doctrine, consigne permanente, brief A22, corrections A20/A21. Parent possède verrou et README partagé : aucun changement enfant sur ces deux fichiers. Aucun Git, réel, archive, compte, Novamira, déploiement, voie2, A23 ou T02.

Choix technique : réemployer le lecteur borné des deux flux d'A21, une seule implémentation commune. Garder les validateurs stricts des rapports A20/A21. Les autres lots ne changent ni comptes ni formats. Protéger aussi les commandes PHP publiques A03/A11 sans changer leur ligne d'appel. A14 possède une capture mais son refus par expression régulière est trop large et ses fichiers partiels peuvent survivre : mêmes canaris, partage du gardien au besoin.

| Outil | Charge le WordPress du site | Flux PHP avant A22 | Traitement prévu |
|---|---|---|---|
| A02 audit | Non, PDO et lecture statique ; aucun require de fichier du site | Hérités | Hors bootstrap, régression existante |
| A03 non-regression | Oui, wp-load.php, sonde native et HTTP local | Hérités | Gardien commun, confinement existant inchangé |
| A10 inventorier-codes | Non, PDO/SELECT, sans bootstrap | Hérités | Hors bootstrap, régression existante |
| A11 inventorier-adresses | Oui, Runtime::boot/wp-settings.php | Hérités | Gardien commun |
| A12 inventorier-contenus | Oui | Hérités par execvp | Gardien commun |
| A13 controler-export | Non, CSV hors ligne | Pas de PHP | Hors périmètre bootstrap |
| A14 rapprocher-contacts | Oui | Deux flux capturés, protocole et refus à renforcer | Mêmes canaris et gardien commun |
| A15 inventorier-emails | Oui | Hérités par execvp | Gardien commun |
| A16 inventorier-numeros | Oui | Hérités par execvp | Gardien commun |
| A17 inventorier-securite | Oui | Hérités par execvp | Gardien commun |
| A18 inventorier-conservation | Oui | Hérités par execvp | Gardien commun |
| A19 inventorier-coherence | Oui | Hérités par execvp | Gardien commun |
| A20 inventorier-tarifs | Oui | Candidat capture non bornée | Remplacer par gardien commun ; conserver validation stricte |
| A21 inventorier-portes | Oui | Candidat capture bornée et délai | Extraire gardien commun ; conserver validation stricte |

Préparation globale, T01 global et PRET réservés au parent ; non exécutés par cet enfant. Ancien PRET A21 retiré et absence relue avant modification. Anciens paquets à conserver hors dépôt avant publication des nouveaux reçus après dernières sources.

## Checkpoint — gardien intégré, rejeux en cours

- `stream_guard.py` est le seul lecteur de processus et des deux flux ; extraction du candidat A21, lecture bornée à 64 Kio par flux, délai, EOF et terminaison obligatoires. A20 garde `report.py`/son contrat strict ; A21 garde sa projection canonique fermée. Les publications sont privées jusqu’à validation.
- A03/A11 gardent leur commande PHP via un petit pont sans chargement du site ; A12/A14/A15–A19 utilisent le même gardien. A02/A10 ne chargent pas le WordPress du site ; leurs suites seront également rejouées, sans changement de leurs comptes.
- TDD réel : quatre tests du gardien absents d’abord rouges, puis verts ; neuf tests Windows A22 verts après ajout des contrats. Les 34 tests A20 et 12 tests A21 sont verts. Les tests enfants fixent leur encodage ; `C:/Python314/python.exe` découvert, pas le `python` du PATH (3.11).
- L’adaptateur A22 réemploie les runners existants et leurs assertions, redirige seulement leurs anciens emplacements de preuves en mémoire, ajoute les sept sondes de flux et une vraie mutation du gardien dans les copies Docker. Les octets canaris du témoin ne sont jamais sauvegardés. Le parcours documentaire est pris mot pour mot, seuls les chemins étant substitués.
- Essais intermédiaires hors dépôt : `a22-probe-*`, `a22-matrix-final-01`, `a20-shared-final-01`, `a21-shared-final-01` dans le scratch Hermes. Ils ne sont pas des paquets livrés. Échecs réels observés et corrigés : sélection d’une mauvaise copie du gardien pour la mutation HPOS ; adaptateur de photo A03 ; liste fermée omettant des codes historiques PHP-log/A09 et le code fixe de la sonde de rollback A03 ; ancien test structurel A14 cherchant encore `subprocess.run` au lieu du transport UTF-8 en octets.
- Les appels Windows WSL concurrents de la première matrice ont retourné `4294967295` avant exécution Docker (`CREATE`, `CP`, `INSPECT`). Les reçus rouges sont conservés en scratch ; un bail interprocessus limité aux appels de nos runners les sérialise désormais. Aucun service, site ou runner d’un autre enfant n’est supprimé. Nouvelle matrice verte requise après ces dernières sources ; pas de recyclage des premières empreintes.

## 14 h 56 CET — dernières sources figées, nouvelles matrices lancées

- Les sondes A17 et A18 sont désormais réellement vertes sur les deux magasins, y compris neutralisation A17 et surveillance noyau A18. La première A18 rouge venait du banc ajouté qui ouvrait les médias pour ses propres empreintes pendant la fenêtre IN_OPEN : le nouveau banc ne fait que les métadonnées à cet endroit ; l’ancienne suite conserve ses véritables empreintes complètes avant/après, inchangées.
- A17 après neutralisation révélait un `error_log()` natif de planification, ignoré par `log_errors=0`. Diagnostic jetable : succès PHP complet, deux rapports, stderr de 401 octets, classé en mémoire comme diagnostic de planification ; aucun texte brut conservé. Décision de sortie seulement : `error_log=/dev/null` pour les anciens inventaires, et droit Landlock **WRITE_FILE sur le seul périphérique de rejet `/dev/null` (major 1, minor 3)** ; aucun droit de plus sur site ou dépôt, aucun journal créé. Le rapport et tous les comptes A17 restent ceux de la suite originale, maintenant verte ; SQL/fichiers du site restent réellement immuables. Aucun pré-filtre métier ou compteur ajouté aux lots clos.
- Délai du gardien éprouvé aussi avec un descendant Python gardant les pipes ouverts : test d’abord rouge à plus de deux secondes pour un délai de 0,1 s ; correction au propriétaire de fermeture des pipes, puis vert. Dix tests Python A22 verts. Pas de PHP sur Windows.
- PHP commun modifié : syntaxe et PSR-12 stricts verts (0 erreur/0 avertissement), reçu `a22-style-final-05/style.json`, conteneur `imagine-a22-style-2e5d0de8089e` supprimé et absence relue. A21 style également vert, `a21-shared-style-final-02`.
- Les trois matrices **neuves** sont parties après ces sources : `a22-matrix-final-02`, `a20-shared-final-02`, `a21-shared-final-02`. À ce checkpoint elles sont EN COURS, pas encore déclarées vertes. Les paquets finaux ne seront remplacés qu’après leurs codes de sortie réels et la vérification des instantanés.

## Checkpoint — A20 publié, dernière matrice A22 sélectionnée

- **A20 terminé sur son périmètre enfant** : `a20-shared-final-02` code réel 0 ; paquet courant remplacé, ancien paquet et reçus racine archivés hors dépôt (`a22-superseded-a20`). Par console : 34 tests Python, 23 assertions pures, 158 contrôles natifs, 9 contrôles runner et 21 contrôles additionnels du gardien. Vérificateur réel : **111 contrôles PASS**, code 0 en UTF-8 et cp1252. Six mutations de vérificateur sur miroir jetable sont vertes, dont PRET futur accepté uniquement dans ce miroir, fichier altéré refusé, cas natif obligatoire retiré puis rescellé refusé, dérive du gardien commun refusée, restauration verte. Aucun PRET du dépôt créé.
- Le parseur de réception A22 a été éprouvé sur les **vrais schémas** des anciens reçus : A02 `unit.json` n’a historiquement pas de champ `exit_code`, A03 porte un dictionnaire `tests` de booléens. TDD rouge puis vert pour ces formes ; pas de reçu natif réécrit ou de code retour inventé. La tolérance A02 est explicite et limitée au reçu pur, dont le vrai runner atteste séparément la sortie zéro. `tests` et `checks` sont tous deux contrôlés si présents. Totaux exacts et noms uniques de chaque banque existante sont exigés ; doublons JSON refusés.
- Cette dernière correction de vérificateur exige une nouvelle photographie propre : **seule `a22-matrix-final-03` est candidate à la livraison A22**. `a22-matrix-final-02` restera un intermédiaire scratch, même si ses banques sont vertes. A20/A21 ne dépendent pas de ce vérificateur A22 et leurs instantanés courants restent vérifiables.
- Le harnais de style commun est livré et a été réellement rejoué à son chemin final : `production/A-22/style.py`, reçu `a22-style-final-06`, code 0, trois fichiers PHP, zéro erreur/avertissement, sources exactes avant/après et suppression du conteneur exact relue. A21 et les banques A22 continuent leur matrice ; aucun résultat futur n’est revendiqué ici.

## Checkpoint — deux frontières d’arguments restaurées, nouvelle sélection de preuves

La revue du passage par un dossier privé a trouvé deux validations à faire **avant** la substitution : un `--wp-path=` vide d’A12 ne doit pas devenir le dossier courant, et un nom final A20 invalide ne doit pas être masqué par le nom privé `result`. Deux tests réels ont d’abord échoué (codes observés `A12_AUDIT_GUARD` / `A20_CONFINEMENT_FAILED` au lieu des refus d’argument), puis sont verts après une garde de valeur et une garde de basename. Aucun compte, format de rapport ou paramètre nominal changé. Treize tests Python A22 sont verts en UTF-8 ; toutes les sous-commandes fixent leur encodage.

Ces **deux lignes applicatives** changent les dépendances : les paquets A20/A21 de matrice 02 et A22 de matrices 02/03 sont désormais historiques, non rescellables sur les nouvelles sources. Leurs FINALISATION portent le checkpoint ; PRET reste absent. Les nouvelles matrices complètes sont réellement lancées : **`a22-matrix-final-04`, `a20-shared-final-03`, `a21-shared-final-03`**. Seules celles-ci seront publiées si leurs retours réels sont verts. Style A21 `a21-shared-style-final-03` déjà vert ; style commun `a22-style-final-06` reste exact, ses trois fichiers PHP étant inchangés. Aucun gate parent exécuté.

## Checkpoint — compatibilité des refus et sélection finale 06 / 04

Six sous-échecs TDD supplémentaires ont montré que le proxy devait garder les refus historiques de chemin A03/A11 et le refus générique A14, au lieu de les rebaptiser par des codes techniques nouveaux. Mappages fermés restaurés, sans recopier les arguments ni une exception brute. **Les 16 tests Python A22 sont réellement verts** après ces corrections ; le gardien est toujours unique. Sources applicatives désormais identiques à celles lancées pour la sélection ci-dessous.

Pour ne pas laisser les replays obsolètes consommer le délai, les quatre contrôleurs intermédiaires A22 02/03/04/05 ont été arrêtés via le gestionnaire de processus possédés, **sans revendiquer une sortie normale**. Relecture CIM : leurs interpréteurs et wrappers ne restent pas actifs. Cinq conteneurs orphelins précis, identifiés par nom, label de propriétaire, image, absence de montage/réseau et protections avant action, ont été retirés puis leur absence a été relue sémantiquement. `cancelled-intermediates.json` conserve ces noms et le reçu de récupération ; ce n’est pas une preuve de tests verts et aucun de ces replays n’entre dans le paquet final.

Dernières exécutions sélectionnées, réellement lancées après les dernières écritures applicatives :
- A22 `a22-matrix-final-06` — suivi `proc_cacc6f7aa504` ;
- A20 `a20-shared-final-04` — suivi `proc_56bcf265268d` ;
- A21 `a21-shared-final-04` — suivi `proc_d733a019bf04`.

Les replays A20/A21 03 éventuels restent aussi historiques après le dernier changement du gardien commun. Les nouveaux paquets ne seront publiés qu’après les vrais retours et comparaison exacte des dépendances exécutées. **Style commun 07 et style A21 04 déjà verts**, avec zéro erreur/avertissement et suppression du runner exact relue. README partagé, verrou, T02 et A23 laissés à leurs propriétaires. Préparation globale, T01 global et PRET toujours non exécutés par cet enfant.

## Checkpoint — A20/A21 04 publiés et définitivement revérifiés

Les matrices **A20 04 et A21 04 sont terminées à code 0** (cinq et six commandes respectivement). Leurs nouveaux paquets ont été publiés après comparaison exacte des sources et dépendances exécutées ; anciens paquets et reçus copiés hors dépôt, un seul `preuves/final` par lot. A20 : **111 contrôles PASS** du vérificateur dans chacune des consoles UTF-8/cp1252 ; A21 : **49 PASS** dans chacune. Six sondes de miroir jetable sont vertes par vérificateur, notamment PRET futur accepté uniquement dans le miroir, omission rescellée refusée et dérive du gardien refusée. Dernière vérification effectuée après les notes/FINALISATION corrigées ; manifestes racine relus et exacts, **PRET réel absent**.

**Ne pas refaire A20/A21.** Seule la matrice A22 **06** reste en cours ; quinze reçus runner déjà observés à `2026-11-26T16:17:16+01:00`, aucun verdict final anticipé. Le finaliseur A22 est livré à `production/A-22/finalise.py` ; sa garde `--seal-only` a réellement refusé le paquet encore absent (code 1), sans créer de manifeste ni PRET. Il sera exercé sur la vraie matrice terminée avant remise.

## Checkpoint — matrice 06 rouge pour banques Python inexistantes, sélection 07

La matrice 06 a terminé normalement à **code 1**, avec sources stables. Ses **22 commandes natives sont toutes à code 0** : banques PHP, canaris, mutations et parcours documentés passent. Quatre invocations Python A03/A11 renvoient toutefois réellement **5 / NO TESTS RAN**, car ces deux lots n’ont **aucun** `test_*.py` ; leurs banques PHP existent et restent entièrement obligatoires. Ce résultat n’est pas maquillé en vert et le paquet 06 n’est pas livré.

TDD d’applicabilité d’abord rouge, puis **17 tests Python A22 verts**. La matrice déclare et vérifie maintenant l’absence des deux seules banques Python inexistantes ; elle ne convertit aucun code 5 en 0. Le vérificateur exige la liste exacte des commandes effectivement applicables et garde toutes les banques PHP inchangées. Seuls `matrix.py`, `verify.py` et leur test A22 changent, **aucune source applicative**. A20/A21 revérifiés après ces changements : toujours **111 / 49 PASS par console**, sources/dépendances exactes, aucune nouvelle matrice de ces deux lots nécessaire.

Nouveau rejeu **complet et neuf A22 07**, pas de recyclage des sorties/empreintes 06 : `proc_da07e2aa136d`, réellement lancé après cette correction. Il reste à attendre sa sortie réelle, publier via le finaliseur, vérifier/sceller le paquet et relire les suppressions exactes. PRET, préparation globale et T01 global toujours au parent.



## Remise finale du paquet 07

Matrice complète réellement terminée à **code 0**, 42 commandes, sources stables. Paquet 07 publié et vérificateur livré réellement exécuté sous les deux consoles : **159 / 159 PASS**, code 0. Les comptes détaillés, absence explicite des banques Python A03/A11, mutations et frontière parent sont dans `FINALISATION.md` et `execution-summary.json`. A20/A21 04 restent les paquets courants, 111 / 49 contrôles PASS par console. Aucun PRET ni gate global créé/exécuté par cet enfant.
