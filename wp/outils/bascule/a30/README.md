# A30 — passage à blanc des abonnés hors ligne

**Simulation uniquement.** Le PHP pur et le banc natif se rejouent dans les conteneurs fictifs déconnectés, sur l'import A28 gelé. Le paquet courant et les gates réellement acquis sont décrits dans `production/A-30/RECEPTION-PARENT.md`. Aucun import réel n'est autorisé par cet outil.

## Le standard d'abord — cinq lignes

1. Le CSV intégré à WooCommerce importe et met à jour des **produits**, pas un fichier de comptes et d'abonnements Access.
2. Subscriptions fournit l'ajout manuel d'un abonnement lié à un client et à un produit ; c'est une écriture, pas une simulation.
3. Sa documentation propose aussi un CSV Importer gratuit en bêta publique, séparé, avec limites de support et de migration.
4. Ces parcours de création ne constituent pas le passage à blanc A13, en lecture seule, avec cinq issues et réduction K5 demandé ici.
5. A30 réemploie donc le parseur A13 et les lecteurs natifs WordPress/Woo ; il n'appelle jamais les importeurs, ni les créations de compte/abonnement.

Sources officielles consultées le 27 novembre 2026 : `https://woocommerce.com/document/product-csv-importer-exporter/` ; `https://woocommerce.com/document/subscriptions/migrating-subscribers-woocommerce-subscriptions/`. Les deux anciennes URL « importing-subscriptions » ont répondu 404 ; la page actuelle a été retrouvée depuis l'index officiel Subscriptions et lue. Aucune extension téléchargée/installée pour A30.

## Usage — Linux isolé, copie vérifiée et export fictif hors dépôt

La commande est une seule ligne, tous ses arguments sont obligatoires. Remplacer les chemins extérieurs ; ne pas ajouter d'option cachée. Le banc parent rejoue exactement cette ligne avec ses chemins de fixture.

```sh
python3 wp/outils/bascule/a30/confine.py --wp-path=/copie-verifiee --fichier=/hors-web/export.csv --correspondance=wp/outils/bascule/a13/correspondance.exemple.json --types=/hors-web/types.json --audit=/hors-web/audit-date/audit.json --au=2026-11-25
```

`--au` est la date de référence **du contrôle A13**, explicitement saisie, jamais une prochaine échéance calculée. La date de l'exemple n'est pas la date locale implicite. L'audit A02 doit être en lecture seule et annoncer le même stockage classique/HPOS que l'observation native.

Le lanceur est Python ; il passe les seuls champs nécessaires au PHP par stdin, sous `stream_guard.supervise` d'A22, inchangé. A12 apporte Landlock ; il exige Linux déconnecté. Les identités brutes ne vont dans aucun fichier intermédiaire. PHP ne peut écrire que dans un répertoire privé adjacent au CSV, supprimé après contrôle. La transaction SQL en lecture seule, le lecteur de configuration A11 sans exécution de wp-config, les interdictions de mail/HTTP/cron/Action Scheduler et les fonctions système désactivées sont réemployés. L'affichage normal est absorbé ; flux directs, arrêts et sorties tardives sont refusés. Le digest du résultat privé est lié au succès avant shutdown ; les fichiers et leur schéma fermé sont revérifiés **après** terminaison et EOF des deux flux. A22 n'est ni copié ni modifié.

Windows peut rejouer toute la suite Python et les refus A13 ; il refuse volontairement le chemin PHP (`A30_CONFINEMENT_REQUIRED`). Le banc parent passe par Docker/WSL, jamais par PHP Windows ; il n'accepte aucun chemin de compte, site ou archive existant.

## Configuration entièrement fictive

Copier `types.exemple.json` hors dépôt. Les IDs `910001` et `910002` sont inventés, pas ceux d'un site. `types` associe exactement le libellé Access à un ID de **produit d'abonnement simple ou variation** existant sur la copie. Un produit absent, non-abonnement, parent variable sans variation concrète, ou un type absent de la table donne `type_a_decider`. Aucun rapprochement par titre ou prix.

`paiements` traduit les modes déclarés du CSV vers les trois catégories fermées `virement`, `domiciliation_papier`, `autre`. Une valeur non mappée devient `autre`, sans publier son libellé. La configuration est stricte : clés inconnues, JSON à clés doublées, mauvais types et identifiants non positifs sont refusés.

Les trois options réservées `importer_echus`, `resoudre_doublons`, `calculer_prochaine_echeance` sont toutes **false**. Les passer à true refuse `A30_OPTION_UNSUPPORTED` : ce lot n'implémente aucune de ces décisions. L'option A13 `doublon_prenom_identique` reste celle de la correspondance A13 ; A30 ne la modifie pas. Une échéance passée ou un doublon rejeté par A13 reste rejeté ici, sans décider du futur import A06.

## Cinq issues et ordre de priorité

- `refuse_a13` : la ligne a au moins un défaut A13 ; aucun motif ou contenu n'est recopié.
- `sans_email` : ligne A13 admissible sans email ; aucune adresse technique créée ici.
- `type_a_decider` : ligne avec email, sans produit d'abonnement natif reconnu par la table.
- `compte_existant` : une seule entrée de compte possède cette adresse, selon la comparaison native SQL WordPress.
- `compte_a_creer` : pas de compte trouvé pour cette adresse sur une copie **non neutralisée** ; ce n'est jamais une autorisation d'import.

Deux comptes du site à la même adresse provoquent `A30_EXISTING_EMAIL_AMBIGUOUS` : A30 n'en choisit ni n'en fusionne aucun. Un doublon dans l'entrée reste traité par A13. Le fichier entièrement refusé par A13 (notamment IBAN ou encodage indéterminé) sort avec **le même code 2 et le même message fermé**, sans fichier A13/A30. A30 appelle directement `lire_config`, `decoder`, `lire_csv`, `analyser` d'A13 ; jamais `controler`, `ecrire` ou `main`.

### Copie neutralisée : connaissance manquante, pas une sixième décision

Le marqueur de neutralisation rend `accounts` et les deux listes de rapprochement « **inconnu après neutralisation** », jamais zéro. Les lignes admissibles avec produit connu restent dans `rapprochement_inconnu` (numéros seuls), sans attribuer arbitrairement l'une des deux issues de compte. Les trois autres issues restent observables. Techniquement, l'issue privée est alors null ; il ne s'agit pas d'une sixième issue métier. Cette exception explicite est indispensable : cinq décisions exclusives par ligne ne peuvent pas simultanément prétendre connaître un rapprochement rendu inconnaissable par anonymisation. Pour une répartition exclusive complète, refaire le passage opérateur dans le contexte autorisé adéquat ; A30 ne contourne pas la neutralisation.

## Sorties à côté du CSV, jamais dans un dépôt

Pour `export.csv`, deux fichiers UTF-8 créés exclusivement, mode 0600 sous Linux :

- `export.a30-resume.json` : total et nombres par issue, produit, mode de paiement ; chaque groupe de 1 à 4 est fondu dans `autres`, sans son identifiant/libellé. Groupe visible à partir de cinq. Produit `0` signifie correspondance non reconnue, jamais un produit inventé.
- `export.a30-lignes.json` : exactement les cinq clés d'issue et leurs numéros de lignes physiques d'entrée, plus la métadonnée des lignes au rapprochement inconnu. Aucune cellule, email, identité, référence, motif A13 ou chemin. Cette liste de travail est privée et **n'est pas K5** : elle ne doit pas être publiée avec le résumé.

Les trois axes comptent les **lignes du fichier contrôlé**, rejets compris, pas les comptes créés ni des paiements effectués. Le produit d'une ligne rejetée peut être connu ; cela ne la rend pas importable. Les axes séparés ne constituent pas des sous-totaux croisés. Les résultats existants et les liens symboliques sont refusés, jamais écrasés. Le CSV reste inchangé. Code 0 : aucune ligne refusée A13 ; code 1 avec `A30_OK` : simulation terminée avec lignes refusées A13 ; code 1 sans succès : refus A30 fermé ; code 2 : refus de fichier/configuration A13. Aucun mot de passe, activation, invitation, commande, accès ou transmission Odoo n'est produit.

## Rejeu et limites de preuve

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 C:/Python314/python.exe -m unittest discover -s wp/tests/a30 -p 'test_*.py' -v
C:/Python314/python.exe -B wp/tests/a30/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-matrice-neuve --with-native
C:/Python314/python.exe -B wp/tests/a30/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a30-style-neuf
C:/Python314/python.exe -B production/A-30/verify.py
```

Chaque sortie de banc doit être neuve. Sans `--with-native`, la matrice ne lance **que Python** ; avec lui, elle joue aussi classique et HPOS dans chaque contexte Windows UTF-8/cp1252 (`PYTHONUTF8=0` pour cp1252). Le style strict réemploie le banc A20 inchangé, sur les seuls PHP d'A30. Les anciens paquets restent hors dépôt ; ne pas effacer leurs preuves pour les remplacer. Le parent installe le seul paquet vert dans `production/A-30/preuves/final/`, avec son sous-dossier `style/`, et scelle après la déclaration `rejeu.json`. Le lecteur **sans argument** `production/A-30/verify.py` vérifie l'inventaire puis appelle `wp/tests/a30/verify.py` sans argument ; il ne lance ni PHP ni Docker et refuse un paquet incomplet. Image commune et gates globaux sont obligatoires avant tout PRET. Le complément de deux lignes est dans le vrai mode d'emploi de l'audit `wp/tests/a02-audit/README.md`, contrôlé par ces deux lignes exactes seulement.
