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

Préparation globale, T01 global et PRET réservés au parent ; non exécutés par cet enfant. Ancien PRET A21 à retirer avant modification ; anciens paquets hors dépôt puis nouveaux reçus après dernières sources.
