# Relecture indépendante Codex — A-33

Date : 28 novembre 2026. Références lues : `relecteurs/AGENTS.md`, doctrine et grille, brief A-33, cahier des charges §4.3, décisions, production A-33 et sources concernées dans `wp/`. La relecture Claude n’a pas été consultée. Aucun fichier de production n’a été corrigé.

## 1. Conformité

Les livrables demandés sont présents : outil, tests, section du mode d’emploi commun, paquet unique, `rejeu.json`, vérificateur sans argument et `PRET`. Les trois lignes du standard sont fournies. L’appel direct à A-16 conserve son tri et sa validation ; A-33 ajoute explicitement l’exclusion des correspondances commerciales. Les limites concernant les originaux, les dérivés, les doublons d’inscription et les dossiers écartés sont documentées.

**I1 — Important — `wp/outils/bascule/a33/Inventory.php:127` : la comparaison des dix numéros omet leurs PDF référencés sans parent correspondant.** Le classement des pièces dépend exclusivement de `post_parent`. Or la correspondance A-16 désigne le PDF par `pdf_cle`, y compris dans les métadonnées de terme. Exemple : un numéro sélectionné référence un PDF présent de 100 octets dont `post_parent=0`. A-16 accepte cette référence et constate le PDF ; A-33 ajoute les 100 octets aux orphelins et aucun à `recent_media`. Avec des numéros représentés par des termes, le PDF ne peut de toute façon pas avoir ce terme comme parent WordPress. La comparaison demandée par le brief, fondée sur §4.3 qui inclut explicitement les PDF, peut donc annoncer zéro malgré des PDF conservés. **Correction proposée :** inclure les références PDF explicites des numéros sélectionnés dans le poids de comparaison, dédupliquées par pièce jointe avec les pièces déjà retenues. Garder identifiable le décompte structurel des pièces sans parent et documenter son éventuel recoupement avec cette comparaison. Tester un PDF sans parent, un PDF rattaché à un ancien contenu et une référence partagée, en modes publication et taxonomie. Aucun rattachement ne doit être écrit.

## 2. Exactitude métier

Deux cas déroulés manuellement et comparés aux rapports livrés :

- **Copie ordinaire, douze numéros de 2010 à 2021.** Les dix retenus sont ceux de 2012 à 2021. Restent un numéro et un article en 2010, puis un numéro et un article en 2011. Les pièces de 2010 valent 7 + 11 octets et une absence : trois pièces, deux présentes, une absente, 18 octets connus, total inconnu. En 2011 : une pièce de 13 octets. Les deux pièces récentes valent 17 + 19 = 36 octets ; les deux orphelines 23 + 29 = 52. Le fichier présent de zéro octet reste présent. Ces résultats correspondent à `production/A-33/preuves/final/utf8/native/r1-nominal/archives.json`.
- **Même copie portant le marqueur d’import.** Les nombres et les 18 octets connus de 2010 ne changent pas ; son total devient « inconnu après import ». Le poids des dossiers exclus prend également cette valeur, tandis que les 36 octets récents présents restent mesurables. C’est bien le résultat de `production/A-33/preuves/final/utf8/native/r20-imported/archives.json`. Le banc simule le marqueur ; il ne rejoue pas l’import, limite correctement déclarée.

**I2 — Important — `wp/outils/bascule/a33/Inventory.php:89` : le calcul des liens peut annuler la conservation d’un numéro sélectionné par A-16.** La ligne remplace le booléen initial au lieu de préserver l’appartenance directe aux dix numéros. A-16 accepte une correspondance dont `article_type` et `numero_type` sont identiques. Avec douze publications de ce type, des dates valides, une métadonnée PDF à zéro, une thématique enregistrée et une liaison `post_parent` à zéro, A-16 sélectionne dix numéros. A-33 remet pourtant `$keep` à faux pour chacun et compte les douze publications hors sélection. Les dix identifiants restent en parallèle dans `$recent`, ce qui classe leurs pièces du côté conservé : contenus et fichiers se contredisent. **Correction proposée :** préserver sans condition l’appartenance aux identifiants sélectionnés et ajouter à cet ensemble les articles liés. Ajouter un test de cette correspondance déjà admise par A-16, sans modifier ni durcir sa règle. Constat établi par déroulement du code ; ce scénario supplémentaire n’a pas été exécuté en PHP dans cette session.

## 3. Tests

Exécutions indépendantes effectuées :

- `python -B production/A-33/verify.py` : code 0, `A33_PACKAGE_PASS`.
- `python -B wp/tests/a33/matrix.py --include-native --parent-serialized --output=<dossier temporaire neuf hors dépôt>` : code 1. `LOCALAPPDATA` a été dirigé vers le répertoire temporaire pour les écritures du test de fichiers ; la matrice retire elle-même `TMPDIR` et impose les deux encodages.
- Dans chacun des modes UTF-8 et cp1252 : **30 tests Python exécutés, 29 réussis, une erreur** dans `test_actual_file_channel_tampering`, à l’écriture du fichier temporaire (`PermissionError`, puis refus de nettoyage du dossier). Les deux lancements natifs échouent avant création du banc avec `DOCKER_IMAGE_FAILED:4294967295`. Le contrôle de style échoue également à son préalable Docker. Les sources et dépendances restent identiques selon les reçus.

Ces échecs d’accès ne démontrent pas un défaut fonctionnel d’A-33, mais empêchent de déclarer le rejeu indépendant entièrement vert. Les journaux de cette tentative sont dans `C:/Users/Ced/AppData/Local/Temp/a33-codex-fdc339135f964ea3aef0302c1368b863/`. Les portails globaux n’ont pas été relancés après cet échec du préalable Docker. Les preuves livrées, validées par le lecteur, attestent séparément 30 tests Python, 23 contrôles purs et 52 contrôles natifs par encodage ; elles ne remplacent pas une nouvelle exécution.

Les tests existants vérifient des valeurs attendues explicites, le zéro réel, les absences, les variantes parent/taxonomie, le rejeu déterministe, les canaris des différents canaux et les empreintes avant/après. En revanche, le semis fixe tous les PDF à zéro (`wp/tests/a33/seed.php:25`) : il ne peut détecter I1. Les correspondances utilisent toujours deux types distincts : elles ne détectent pas I2. Ajouter les régressions indiquées avec leurs corrections.

**M1 — Mineur — `wp/tests/a33/seed.php:34` : la priorité annoncée pour un article lié à plusieurs numéros n’est pas éprouvée.** Chaque article reçoit exactement un terme ; la variante taxonomie ne rencontre donc jamais un article commun à un ancien numéro et à un des dix derniers. **Correction proposée :** ajouter ce cas avec une pièce de taille connue et vérifier qu’article et pièce restent uniquement du côté conservé, sans double comptage. Compléter cette variante par une égalité de dates à la frontière du dixième numéro, pour contrôler le départage par identifiant hérité d’A-16.

## 4. Sécurité et données

Aucune fuite de titre, nom de fichier ou chemin du site identifiée dans les sorties examinées. Les sorties utilisent un schéma fermé, des types anonymisés, des refus contrôlés et une liaison par empreintes entre les deux rapports. Les requêtes variables de liaison sont préparées ; les exclusions SQL proviennent d’une liste constante. Les sources réutilisent les protections de lecture seule et le gardien existants. Les mesures utilisent les métadonnées du système de fichiers sans ouvrir les médias ; le banc livré comprend un témoin positif du détecteur d’ouverture.

Aucun accès réel effectué. Les données du banc sont fictives. Cet outil CLI n’ajoute pas de route publique ni de voie de sortie du texte réservé ; droits et nonces d’une interface web ne s’appliquent pas ici. La preuve native de non-mutation a été examinée dans le paquet, mais n’a pas pu être reproduite localement pour les raisons indiquées ci-dessus.

## 5. Doctrine

Le standard est exposé, avec références officielles, et A-12/A-16/A-22 sont réutilisés. Les fichiers PHP du lot déclarent les types stricts et un espace de noms `Imagine`; les calculs simples sont séparés de l’accès WordPress. Le README documente portée, commande et limites. Le contrôle PSR-12 livré est vert ; son rejeu indépendant est empêché par le préalable Docker. Aucun changement demandé à l’import, au gardien ou au lanceur gelés.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références officielles présentes dans `STANDARD.md` ont été lues dans le dépôt ; aucune consultation de site externe n’a été effectuée, conformément au rôle de relecteur.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut classé à ce niveau.
- **Important :** I1, poids des PDF explicitement référencés absent de la comparaison ; I2, numéro sélectionné recompté hors sélection lorsque les deux rôles partagent un type.
- **Mineur :** M1, absence du cas de rattachement multiple annoncé.

Le rejeu indépendant reste partiel pour des raisons d’accès local ; le paquet livré passe son vérificateur. Les corrections et leurs tests doivent être intégrés puis les preuves renouvelées. Aucune question pour Ced. Ce verdict n’est pas un GO.
