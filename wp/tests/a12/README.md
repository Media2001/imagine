# A-12 — suite dédiée sur le banc A-02

Depuis `C:\Users\Ced\imagine`, choisir **deux nouveaux dossiers hors dépôt** :

```text
python wp/tests/a12/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-style-nouveau
python wp/tests/a12/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-rejeu-nouveau
```

Copier ensuite le premier dossier sous `a12-rejeu-nouveau/style/`, puis :

```text
python wp/tests/a12/verify.py C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-rejeu-nouveau --save
```

La copie ne modifie ni les scripts ni les résultats : elle réunit dans **un paquet** les reçus PHPCS et natifs issus des mêmes empreintes. Le vérificateur refuse les divergences d'inventaire, de sources, d'audit, de fingerprints ou de statut ; il exige les cas natifs nommés, les registres exacts et les sondes système/SQL. Son exit 0 et `NATIVE_VERIFIE` qualifient la suite dédiée. Les formalités communes réservées au parent sont contrôlées séparément avant `PRET`.

## Préconditions et isolation

- Docker déjà disponible via `wsl.exe -d Ubuntu -- docker` ; PHP seulement en conteneur.
- Image publique A-02 déjà présente et épinglée par son ID dans le runner inchangé d'A-02 ; paquets Subscriptions et Memberships d'A-02 lus aux chemins et SHA-256 de ce banc, sans nouvelle licence, activation distante ou copie au dépôt.
- PHPCS/PHPCBF proviennent des dépendances de l'image `imagine-tests-t01:1` existante, dont l'ID inspecté est épinglé pour le run de style. Aucune reconstruction ni installation hôte. `--fix` est un mode facultatif de travail qui ne copie en retour que les fichiers PHP d'A-12 ; ne pas l'utiliser pour sceller les preuves finales.
- Ownership `org.imagine.a12-content`, noms distincts `imagine-a12-content-*` / `imagine-a12-style-*`, réseau `none`, aucun montage/port, capacités supprimées, `no-new-privileges`. MariaDB par socket Unix `--skip-networking`, seuls loopback et zéro listener TCP vérifiés. Cleanup par nom + label, absence relue.
- Le runner ne reçoit aucun site ni archive Imagine. Il crée des fixtures WordPress/Woo/WCS/Memberships purement fictives avec le banc A-02 inchangé. Les paramètres globaux du module importé changent **en mémoire seulement**. A-11 est copié sans modification pour charger ses vrais `Runtime.php`/`ReadOnlyDb.php` ; inventaires et empreintes d'A-02 et des sources/tests A-11 sont vérifiés stables. A-10 n'est ni importé ni modifié.
- Le lanceur A-12 applique Landlock avant d'exécuter PHP : seul le parent des rapports accepte des mutations de fichiers. Aucun fallback sans confinement. ABI réelle enregistrée, essais de création/troncature dans le site réellement refusés, mail/processus directs désactivés. La base tourne sur socket Unix, sans réseau TCP.

## Assertions

Oracle issu des vraies API WordPress et CRUD Woo avant gel : type, type vide, type de thème, taxonomie et 23 rubriques ; cinq contenus de quatre états, métadonnées dupliquées, liens produits directs/inverses et clés de casse différente ; deux PDF de 23 et 28 octets dont un orphelin, image fictive. Le média placeholder natif Woo est aussi compté dans l'oracle global : quatre médias, deux parents nuls au total, mais **un seul PDF orphelin**.

Après gel : compte SQL SELECT uniquement, empreintes indépendantes de **toutes** les tables (schémas + multisets de lignes), inventaire SHA-256 des fichiers du site, piège de configuration non exécutée. Bootstrap natif sous READ ONLY **avant le premier MU-plugin** ; même connexion pour registre, métadonnées et médias. Sondes privilégiées : UPDATE direct mysqli refusé par le serveur (1792), COMMIT/changement de transaction refusés, HTTP/mail/cron bloqués, écritures de fichiers refusées par le noyau. Les empreintes couvrent options/cron et toutes les tables Action Scheduler.

Comptes exacts, états/dates UTC, clés sans valeurs, vingt termes par usage réel distinct, poids réels, absence des canaris privés dans JSON/Markdown et sortie CLI, permissions, rejeu et refus de sorties existantes/web/dépôt, audit absent/invalide/mauvais stockage, configuration dynamique, dispositions non prises en charge, drop-in, média absent/symlink, dépendance absente à erreur fermée. Registres comparés **exactement** à l'oracle : type et taxonomie dynamiques inclus, appels non exécutés et objets retirés exclus ; fichiers cœur/WooCommerce/MU/thème exacts. Aucune analyse statique de déclarations ne subsiste.

`--unit-only` limite le run aux règles pures d'attribution de fichier ; ce mode ne peut pas qualifier le lot. Assertions nommées JSON, pas des nombres PHPUnit. Le brief impose une suite dédiée proportionnée, pas le rejeu global. Les essais RED/intermédiaires et l'ancien paquet partiel restent dans le scratch ; seul le dernier paquet vert rejoint `production/A-12/preuves/final/`. La préparation de l'image partagée et l'intégration des deux lignes communes restent à la charge du parent ; leurs reçus sont distincts des preuves natives.
