# A-12 — suite dédiée sur le banc A-02

Depuis `C:\Users\Ced\imagine`, choisir **deux nouveaux dossiers hors dépôt** :

```text
python wp/tests/a12/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-style-nouveau
python wp/tests/a12/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-rejeu-nouveau
```

Copier ensuite le premier dossier sous `a12-rejeu-nouveau/style/`, puis :

```text
python wp/tests/a12/verify.py C:/Users/Ced/AppData/Local/hermes/cache/scratch/a12-rejeu-nouveau
```

La copie ne modifie ni les scripts ni les résultats : elle réunit dans **un paquet** les reçus PHPCS et natifs issus des mêmes empreintes. Le vérificateur refuse les divergences d'inventaire, de sources, d'audit, de fingerprints ou de statut. Son exit 0 prouve la cohérence de la **livraison partielle** : sa sortie reste `PARTIEL_NON_PRET`, jamais une autorisation de déposer `PRET`.

## Préconditions et isolation

- Docker déjà disponible via `wsl.exe -d Ubuntu -- docker` ; PHP seulement en conteneur.
- Image publique A-02 déjà présente et épinglée par son ID dans le runner inchangé d'A-02 ; paquets Subscriptions et Memberships d'A-02 lus aux chemins et SHA-256 de ce banc, sans nouvelle licence, activation distante ou copie au dépôt.
- PHPCS/PHPCBF proviennent des dépendances de l'image `imagine-tests-t01:1` existante, dont l'ID inspecté est épinglé pour le run de style. Aucune reconstruction ni installation hôte. `--fix` est un mode facultatif de travail qui ne copie en retour que les fichiers PHP d'A-12 ; ne pas l'utiliser pour sceller les preuves finales.
- Ownership `org.imagine.a12-content`, noms distincts `imagine-a12-content-*` / `imagine-a12-style-*`, réseau `none`, aucun montage/port, capacités supprimées, `no-new-privileges`. MariaDB par socket Unix `--skip-networking`, seuls loopback et zéro listener TCP vérifiés. Cleanup par nom + label, absence relue.
- Le runner ne reçoit aucun site ni archive. Il crée des fixtures WordPress/Woo/WCS/Memberships purement fictives avec le banc A-02 copié en lecture seule. Les paramètres globaux du module importé sont changés **en mémoire seulement**, pas les fichiers partagés. Les bancs A-10/A-11 ne sont ni importés ni modifiés.

## Assertions

Oracle issu des vraies API WordPress et CRUD Woo avant gel : type, type vide, type de thème, taxonomie et 23 rubriques ; cinq contenus de quatre états, métadonnées dupliquées, liens produits directs/inverses et clés de casse différente ; deux PDF de 23 et 28 octets dont un orphelin, image fictive. Le média placeholder natif Woo est aussi compté dans l'oracle global : quatre médias, deux parents nuls au total, mais **un seul PDF orphelin**.

Après gel : compte SQL SELECT uniquement, empreintes indépendantes de **toutes** les tables (schémas + multisets de lignes), inventaire SHA-256 des fichiers du site, piège de bootstrap et tentative d'UPDATE zéro ligne sous root refusée par la transaction du sujet. Les empreintes couvrent notamment options/cron et tables Action Scheduler.

Comptes exacts, états/dates UTC, clés sans valeurs, vingt termes par usage réel distinct, poids réels, absence des canaris privés dans JSON/Markdown, permissions, rejeu et refus de sorties existantes/web/dépôt, audit absent/invalide/mauvais stockage, configuration dynamique, média absent/symlink, dépendance absente à erreur fermée. Le type dynamique réellement enregistré et le faux candidat conditionnel sont comparés au registre natif : c'est une **preuve de non-exhaustivité**, pas un faux feu vert.

`--unit-only` limite le run à l'analyseur pur ; ce mode ne peut pas qualifier le lot. Assertions nommées dans JSON, pas des nombres PHPUnit. Le brief impose une suite dédiée proportionnée, pas le rejeu global. Les essais RED/intermédiaires restent dans le scratch ; seul le dernier paquet vert rejoint `production/A-12/preuves/final/`. La préparation de l'image partagée demandée avant `PRET` reste à la charge du parent.
