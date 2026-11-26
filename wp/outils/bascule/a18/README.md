# A-18 — Conservation de données, lecture seule

Standard d’abord : WooCommerce conserve des **références** via son Payment Token API, avec un type, une passerelle et éventuellement les quatre derniers chiffres ; cela ne signifie pas qu’un numéro de carte complet est stocké. L’API standard n’offre pas l’inventaire transversal de formes demandé : ce complément ne lit pas la colonne `token`, ne déclenche aucun paiement et ne contacte aucune passerelle. Référence officielle consultée : `https://developer.woocommerce.com/docs/features/payments/payment-token-api/`.

## Exécution, seulement par un opérateur autorisé sur copie vérifiée

```text
python3 wp/outils/bascule/a18/confine.py --wp-path=/copie-verifiee --audit=/rapports/audit-date/audit.json --output=/rapports/conservation-date
```

Linux déconnecté et Landlock ABI 3+ obligatoires ; PHP 8.2+, lanceur A12 et Runtime A11 inchangés. La sortie doit être neuve, sœur du rapport A02, hors du site et du dépôt, sans ancêtre commun autorisé à écrire. `conservation.json` et `conservation.md` : répertoire 0700, fichiers 0600. Le PHP direct est refusé. Aucun chemin libre sur refus : code seul, sauf six noms techniques de drop-ins fermés du Runtime. Pour lister un lien symbolique, l’opérateur peut exécuter lui-même `find /copie-verifiee -type l` ; ces résultats ne vont jamais dans le rapport.

## Lecture des comptes

- Métas des comptes, options et **deux magasins physiques** de commandes/abonnements : `posts` + `postmeta` et `wc_orders` + `wc_orders_meta`, chaque paire présente étant lue indépendamment de son activation. Valeurs sérialisées incluses. Lecture SQL SELECT paginée, jamais désérialisation d’objet, jamais valeur ni ID de personne/commande en sortie. Le champ global `storage` indique seulement le magasin actif, pour la liaison à l’audit A-02 ; ce n’est pas un filtre de conservation.
- Chaque **ligne de valeur physiquement conservée** compte au plus une fois par forme ; deux lignes identiques comptent deux fois, y compris leurs copies dans deux magasins. Groupement par portée, `store` (liste fermée `classique` / `hpos`, ou `commun` pour comptes/options) et clé technique ; aucune déduplication logique de commandes. Clés dont la syntaxe contient chemin/espace/adresse ou dépasse 100 caractères regroupées sous `autre` ; les clés techniques simples sont le nom de regroupement demandé, pas un nom de fichier.
- Les colonnes de formes sont indépendantes : **ne pas les additionner pour obtenir un nombre de lignes distinctes**. Une même ligne contenant plusieurs formes peut alimenter carte et registre. Précision sur la relecture : un seul nombre de **11 chiffres** ne peut pas alimenter la colonne carte, dont le minimum reste **13** ; le « double comptage d’un même nombre de 11 chiffres » cité dans la fusion n’est donc pas possible avec ces seuils. Aucun assouplissement artificiel de longueur n’a été ajouté.
- IBAN : structures BBAN nationales figées (89 pays), longueur exacte et modulo 97 ; espaces multiples, tabulations, CR/LF, espaces insécables U+00A0/U+202F et tirets tolérés dans le validateur **et** l’extracteur. Registre JSON chargé une seule fois par processus, partagé par `iban()` et `scan()`. Structures dérivées du registre SWIFT v101 publié par python-stdnum, provenance et empreinte dans `production/A-18/sources-officielles.json`. L’accès direct à SWIFT a été refusé ; aucune fraîcheur supérieure à cette source n’est revendiquée.
- Carte : 13 à 19 chiffres et Luhn, suites d’un seul chiffre exclues ; mêmes séparateurs que l’IBAN. Extraction carte et registre séparée : les fenêtres commencent et finissent sur des groupes entiers de chiffres, et sont réexaminées en cas d’échec. Ainsi une carte suivie de `123`, ou un registre suivi d’une année, reste détecté. Aucune tranche arbitraire d’une longue suite continue n’est testée. Pas de preuve d’existence, de titulaire, de marque ou de débit.
- Registre belge : 11 chiffres, clé 97 sur les neuf premiers ou sur ces neuf préfixés de 2 ; **forme et clé seulement**, ni identité, ni existence, ni validation de date civile. Une correspondance est un indice à examiner, jamais une preuve de donnée réelle ni une décision de suppression.
- Marque existante `imagine_staging_disabled_plugins` présente : `database.status = inconnu après neutralisation`, groupes `null`, jamais zéro rassurant sur l’avant-import. Les fichiers présents et les références de jetons demeurent comptés sur la copie courante. Marque conservée telle quelle conformément à l’arbitrage du 26 novembre, passage de 10 h : elle relève de notre import, pas d’une question à Imagine. L’import n’est pas modifié ; aucune certitude historique n’est déduite de l’absence de cette marque.
- Jetons : comptes indépendants par identifiant technique de passerelle et type, sans valeur de référence ni quatre derniers chiffres. **Ce sont des références, pas des numéros.**

## Médias et limite explicitement conservée

Seuls les sous-dossiers de premier niveau autres que quatre chiffres sont parcourus. Dossiers reconnus : exports, logs, backups, wc-logs, woocommerce_uploads, ai1wm-backups, wpallimport, gravity_forms, wpcf7_uploads, formidable, wpforms ; tous les autres fusionnent sous `autre`. Extensions sur liste fermée, sinon `autre`. Nombre de dossiers fusionnés, fichiers par extension et poids total ; aucun nom de fichier, chemin profond ni contenu n’est lu.

**Écart technique du brief :** on ne peut pas affirmer « un fichier interdit la lecture : oui/non » tout en n’ouvrant aucun fichier et sans connaître le serveur. Le défaut prudent est donc `server_rule_file_present` (oui/non sur la seule présence de `.htaccess` ou `web.config`) et `reading_denied = null` (inconnu). Ni la présence, ni l’absence, ni le texte supposé d’un fichier ne deviennent une assurance d’étanchéité HTTP ; des règles héritées ou ignorées sont possibles. Aucune lecture de ces fichiers ni requête HTTP n’a été ajoutée pour obtenir un faux oui/non. Cette réserve est à arbitrer techniquement par Claude lors de la relecture, pas une demande d’accès au réel.

## Rejeu fictif

```text
python -B wp/tests/a18/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a18-rejeu-NOUVEAU
C:/Python314/python.exe -B wp/tests/a18/windows_matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a18-matrice-NOUVEAU
python -B wp/tests/a18/verify.py production/A-18/preuves/final --candidate
```

Aucun argument de site dans le banc. Vrai WordPress/Woo/Subscriptions/Memberships, classic et HPOS, SQL SELECT et transaction READ ONLY, Landlock, empreintes toutes tables et fichiers. Inotify mesure l’absence d’ouverture/accès aux fichiers médias pendant le sujet. Canaris, six drop-ins fermés, symlinks fichier/dossier, variantes neutralisation et règles, consoles Windows UTF8 et cp1252. PHP seulement en conteneurs jetables, supprimés et absence vérifiée. Aucun réel ni déploiement, aucune correction ou suppression de donnée.

`windows_matrix.py` mesure l’interpréteur et chaque console puis exécute **la suite native complète et les tests lanceur** dans chacun des deux contextes ; chaque sous-processus utilise un encodage explicite. Sous cet environnement, le `python` générique est le venv Hermes 3.11.15 : le binaire Windows natif `C:/Python314/python.exe` annonce réellement **3.14.6**, et non le 3.14.7 indiqué dans le contexte initial. Le vérificateur accepte la branche 3.14 et conserve la version exacte mesurée, sans la réétiqueter. Le contrôle de style utilise aussi le runner : `python -B wp/tests/a18/run.py --style-only --output=CHEMIN_SCRATCH_NEUF` (option `--fix` pour PHPCBF sur les seuls PHP A-18).

Le paquet candidat n’inclut **aucune ancienne preuve de build** et ne vaut pas PRET. `verify.py --candidate` vérifie ce statut explicite ; sans ce drapeau, il exige le vrai reçu de `wp/tests/preparer-image.ps1`, à fournir après reconstruction par le parent, puis un nouveau scellement. Les comptes du vérificateur sont calculés dans `check_count`, jamais saisis à la main.
