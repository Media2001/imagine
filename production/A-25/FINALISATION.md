# A-25 — qualification finale déléguée du 2026-11-26T22:56:39.447669+01:00

**Alerte import : les messages de formulaires peuvent rester en clair après neutralisation ; avertissement éditorial permanent, pas une mesure réelle.**

Gel exact des sources : **2026-11-26T22:56:09.803345+01:00** ; inventaire `wp/` de voie 1, hors les quatre racines dédiées voie 2 (1327 fichiers hors __pycache__) dans `files/rapports/2026-11-26-22h56-qualification-A23-A25/freeze.json`, égalité relue avant/après gates. Gardien A-22 et communs inchangés depuis le début de cette qualification.

Le premier gel volontairement trop large a détecté uniquement la création externe de `wp/outils/demo/c25-diagnostic.py`, sans changement A23/A24/A25 ni dépendance. Ses reçus restent intacts en scratch. Le gel final explicite exclut les quatre racines dédiées de l'autre voie ; toutes les gates communes ont été exécutées à nouveau après ce gel. Aucune modification de la voie 2 par ce travail. PowerShell impose lui-même une émission UTF-8 ; ses deux passages conservent respectivement les environnements Python UTF-8 et cp1252, mesurés nativement dans les matrices.

Clé primaire submission_id comptée, vraie table-fille exclue, variante pk-only sans zéro silencieux et ambiguïté fermée réellement prouvées sur classique/HPOS. L'étiquette éditoriale et la source Fluent Forms restent explicites ; import inchangé.

Paquet standard unique : `production/A-25/preuves/final/`. Essais rouges, passages de style intermédiaires et anciens paquets conservés intacts hors dépôt dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a232425-final-20261126/historical/A-25` (les rouges antérieurs restent également au scratch indiqué dans corrections-reveil.md). Aucun reçu ancien n'est présenté comme rejoué.

## Tests réellement exécutés

Windows `C:/Python314/python.exe` **3.14.6**, UTF-8/mode 1 puis cp1252/mode 0, mesurés dans les reçus.

- utf8 : unit=25, result=212, runner=9, python=33 ; tous PASS, codes 0.
- cp1252 : unit=25, result=212, runner=9, python=33 ; tous PASS, codes 0.
- PSR-12 réellement exécuté : zéro erreur, zéro avertissement. Empreintes de toutes les tables, planification et fichiers avant/après vérifiées sur les deux stockages ; recette avec ses seuls arguments exécutée.
- Cinquième canal : JSON invalide, JSON valide avec champ privé, Markdown altéré, fichier supplémentaire et projection partielle au shutdown : refus fermé sans publication, dans chaque contexte et stockage. Aucun canari retenu.

## Gates communes et sceau

`preparer-image.ps1` exécuté réellement, puis `rejouer.ps1` UTF-8/cp1252, puis vérificateurs 20/21/22 dans les deux consoles : tous codes 0 après le gel. Commandes complètes, heures et logs : `files/rapports/2026-11-26-22h56-qualification-A23-A25/`. Le rejeu global ne remplace pas la matrice native propre.

Notes finalisées avant scellement. Les reçus candidats conservant CANDIDAT_GATE_PARENT/pending décrivent leur frontière technique initiale, non une gate encore manquante : les gates parent réellement exécutées sont liées séparément dans parent-gates.json. PRET n'est déposé qu'après les réceptions scellées vertes dans les deux encodages et le contrôle sans argument ; le marqueur final fait foi. Prêt à relire, pas clos ni GO réel.

Aucune opération Git, archive, donnée/compte réel, site existant, Novamira, voie 2 ou commun modifié. Verrou laissé au parent pour sa libération.
