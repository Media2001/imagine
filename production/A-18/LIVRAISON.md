# A-18 — Livraison du 26 novembre 2026

Outil et banc fictif prêts à relire, **non clos**. Lecture seule : formes IBAN (structures nationales et modulo 97), cartes (13–19 chiffres/Luhn), registre belge (11 chiffres/clé des deux siècles), groupées par portée et clé ; références de jetons comptées à part. Médias par dossier premier niveau connu ou `autre`, extensions fermées, poids total, **aucun contenu média ouvert** (preuve noyau inotify). Aucun nettoyage décidé ou exécuté.

## Preuves et commandes réelles

Paquet unique `preuves/final`, dernier rejeu cp1252 à la racine et UTF8 sous `utf8/`. Par console : **10 assertions PHP, 80 assertions natives classic/HPOS, 7 gardes runner, 3 tests Python**, tous verts. Python **3.14.7 Windows** natif, locale cp1252 ; stdout/stderr cp1252 et UTF8=0 mesurés, puis contexte UTF8 distinct. Sous-processus des tests à encodage explicitement fixé. PSR12 strict zéro erreur/avertissement ; `wp/tests/preparer-image.ps1` relancé code 0 après ajout des tests. Commandes exactes, environnements et codes retour : `preuves/final/windows-matrix.json`.

Vérifier : `python -B wp/tests/a18/verify.py production/A-18/preuves/final`.
Rejouer : `python -B wp/tests/a18/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a18-rejeu-NOUVEAU`.

Deux stockages natifs, métadonnée IBAN valide/invalide, carte de test, registre belge, option sérialisée, jeton natif, trois fichiers exports et dossiers inconnus dont un vide, année exclue. Canaris absents de toutes les sorties et de tous les fichiers produits. Refus symboliques fichier/dossier par code seul ; six drop-ins par liste fermée, sorties disjointes, PHP non confiné refusé. Runtime commun inchangé. Tentatives SQL/mail/HTTP/cron/fichiers bloquées ; empreintes de **toutes** les tables et fichiers inchangées, y compris Action Scheduler. Marque de neutralisation : « inconnu après neutralisation », jamais zéro. Les deux lignes du README partagé seules font contrat ; manifeste limité au lot. Essais RED et intermédiaires exclusivement en scratch.

## Décision prudente et écart à faire relire

Le brief exige à la fois de n’ouvrir aucun fichier et de rendre un oui/non disant qu’une règle serveur interdit effectivement la lecture. Ce résultat est indémontrable par les seules métadonnées de fichiers : la règle peut être héritée, ignorée ou ne pas interdire. **Le code ne simule pas cette preuve** : `server_rule_file_present` rend la présence oui/non d’un fichier au nom technique fermé, et `reading_denied=null` reste inconnu. Défaut prudent documenté dans le README et exercé par un fichier de règles fictif ; aucune lecture de son contenu ni requête HTTP. Cette partie du oui/non demandé demeure une **limite non satisfaite à l’identique**, à arbitrer techniquement en relecture ; PRET signifie ici paquet prêt à examiner, jamais conformité totale ni clôture.

## Autres limites

Formes et sommes de contrôle seulement, pas preuve d’existence ni identité. Clés techniques simples autorisées comme groupement demandé ; celles contenant chemins/adresses ou hors syntaxe sont masquées sous `autre`. Structures IBAN figées : source primaire de données python-stdnum issue du registre SWIFT v101, 89 pays ; accès direct SWIFT refusé, aucune fraîcheur au-delà revendiquée. Référence officielle Woo Token API consultée avant le sur-mesure ; aucun code tiers copié ni dépendance hôte installée. Aucun réel, archive, compte, service externe, staging ou déploiement ; PHP seulement dans des conteneurs jetables supprimés. Le passage sur copie vérifiée appartient à l’opérateur autorisé.
