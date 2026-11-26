# Lot A-01 — Quatrième passe : l'import de la base réelle échoue, et ne dit pas pourquoi

**Voie** : 1. **Délai** : trois heures. **Passe avant tout le reste.**

## Ce qui s'est passé

Le 26/11 à 0 h 16, Ced a lancé l'import réel (diagnostic préalable : `NO_STATIC_BLOCKER`). Rapport : `production/A-01/publication-23nov/3151645bb471/result.json`. Prévol, création du site, restauration des 16,9 Go de fichiers : tout a passé. Échec après cinquante minutes : `stage: database`, `code: COMMAND_REFUSED`, rien d'autre. Le site `imagine-test-a01-ced-02` est créé, arrêté, sans injection.

Dans `inside.py`, l'import de la base (`mariadb … < a01-validated.sql`) jette sa sortie d'erreur (`stderr=subprocess.DEVNULL`) et renvoie un code générique partagé avec toutes les autres commandes. **C'est la deuxième fois qu'un refus muet coûte un aller-retour avec Ced** (le premier : `ARCHIVE_PATH`, le 23/11). Ced est le seul à pouvoir lancer cette commande, et chaque essai lui prend une heure.

## À faire

**1. Plus aucun refus muet, nulle part dans la commande.** Passe en revue tous les `Refusal` et tous les appels externes de `publish.py`, `inside.py`, `run.py`, des trois phases et du pont. Chaque échec doit donner : l'étape précise (créer la base / importer / relire les moteurs / réglage / neutraliser…), et pour MariaDB : le **numéro d'erreur**, le SQLSTATE, le numéro de ligne dans le fichier importé, le type d'instruction et le **nom de la table**. Jamais le texte du message ni un extrait de l'instruction : ils peuvent contenir une valeur (« Duplicate entry '…' »). Pour PHP : la classe de l'erreur, le fichier relatif à `wp-content` et la ligne, pas le message. Un délai dépassé est nommé comme tel, avec la durée.

**2. Une base réelle n'est pas une base de test.** La source est un site en production depuis des années, peut-être sur MySQL 8, importée ici dans MariaDB. Sans attendre de connaître l'erreur, fais passer ce qui casse le plus souvent, chaque cas avec son test sur un export de la vraie extension :
- collations et jeux de caractères inconnus de la cible (`utf8mb4_0900_ai_ci` et la famille MySQL 8) : correspondance explicite, écrite au rapport ;
- mode SQL : dates à zéro, valeurs par défaut invalides, colonnes trop strictes ; importer avec le mode de la source plutôt que le mode strict de la cible ;
- instructions très longues (`max_allowed_packet`), lignes très larges, types `JSON`, colonnes générées, index préfixés, `ROW_FORMAT` ;
- moteurs autres qu'InnoDB (le diagnostic signale `wfls_role_counts`) : MyISAM, MEMORY ;
- commentaires conditionnels `/*!…*/`, `DEFINER`, vues, déclencheurs ;
- la durée : 474 Mo de SQL, délai de 1 200 s aujourd'hui. Mesure sur ta grosse archive et dimensionne.
Dis clairement ce que tu as pu reproduire et ce que tu n'as pas pu.

**3. Répéter la base sans restaurer les fichiers.** Un mode `--diagnose-database` (avec `--operator-ced --archive …`) : lit seulement `database.sql` dans l'archive, l'importe dans le conteneur hors ligne, applique la politique des tables, joue neutraliser / anonymiser / vérifier **si c'est possible sans les fichiers** (sinon s'arrête après l'import et le dit), ne crée aucun site, détruit tout en sortant, et rend le même rapport sans données. Objectif : quelques minutes au lieu d'une heure, pour que Ced n'attende plus pour apprendre un échec.

**4. Reprise.** Si l'import complet échoue après la restauration des fichiers, dis ce qui est conservé et ce qui est refait au lancement suivant. Si une reprise sûre de l'étape « base » est simple, propose-la ; sinon ne la fais pas.

**5. Nettoyage.** Le site `imagine-test-a01-ced-02` est vide (aucune injection) : tu peux le supprimer par l'API normale de l'outil, par son nom exact, après avoir vérifié par lecture qu'il ne contient ni fichier ni base issus de l'archive. Si tu as le moindre doute, laisse-le et dis-le.

Tu n'ouvres pas l'archive d'Imagine. Rapport court, puis `PRET`.
