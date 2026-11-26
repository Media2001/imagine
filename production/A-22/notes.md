# A-22 — checkpoints de reprise

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

