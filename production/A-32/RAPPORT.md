# A-32 — état livré, arrêté sur le contrat commun

## Standard d'abord (les deux briefs relus)
A-08 fournit déjà l'enchaînement audit → photos de non-régression → mise à jour → nettoyage → comparaison, avec arrêt au premier refus ; son brief et ses commandes restent inchangés.
La tournée réemploie ce principe d'appel des commandes existantes, mais ne lance aucune étape d'A-08 : uniquement les inventaires clos en lecture seule, avec poursuite après chaque refus/échec.
WordPress/WooCommerce fournissent les lectures des outils acceptés ; A-32 ne crée ni inventaire, ni accès, ni contrôle de statut de remplacement ; aucune nouvelle recherche web n'était nécessaire pour ce réemploi local.

## Obstacle bloquant : aucun PRET
Le brief A-32 demande que les outils eux-mêmes refusent un site non vérifié et interdit d'ajouter un contrôle d'accès dans la tournée. Le parcours natif classique/HPOS montre les treize commandes acceptant un arbre sans `.imagine-staging-verified.json`, y compris après remplacement de l'environnement déclaré par `production`. La tournée ne contourne aucun contrôle : elle lance les commandes documentées avec uniquement leurs chemins substitués. On ne corrige ni les outils clos ni le gardien dans ce lot. **Arrêt limité à A-32**, à arbitrer par le parent/Ced ; pas de PRET, pas de préparation d'image, pas de rejeu global et pas de resceau voisin.

## Périmètre et listes fermées
Inclus : A-10, A-11, A-12, A-15, A-16, A-17, A-18, A-19, A-20, A-21, A-23, A-24, A-25, en cet ordre. Une ligne JSON par outil dans `wp/outils/bascule/tournee/outils.jsonl`, commande exacte vérifiée contre son README ; interpréteurs, ordre, `--limit=10` et date A-19 conservés. A-11 appelle son pont gardien natif ; A-10, SQL pur sans chargement du site, est supervisé extérieurement par l'API existante du gardien. Aucun fichier commun modifié hors section A-32 du README local.
Exclus : A-13/A-14/A-30 demandent les fichiers Imagine ; A-26/A-27/A-29/A-31 non clos dans A-FAIRE du 27/11 à 7 h 30 ; A-22 gardien réemployé ; A-28 import gelé ; A-02/A-03/A-04/A-05/A-08 étapes distinctes ; A-09 test d'un plan, non inventaire. Raisons fermées dans `exclusions.json`. A-29 non repris.

## Preuves et limites
Les essais intermédiaires restent dans le scratch Hermes. Le paquet `preuves/final` conserve une exécution réellement rouge, pas une qualification verte. Les tournées nominales lancent réellement tous les outils sur les deux magasins. Les doubles limités A-10 (refus `A10_AUDIT_GUARD`) et A-11 (sortie 255) sont nommés ; les onze suivants sont réels et aboutissent. Les canaux stdout/stderr, arrêt anticipé muet/bavard, shutdown stdout/stderr et fichier JSON altéré ont été exercés par code MU réel, avec bilan sans canari et empreintes intégrales identiques sur chaque tournée. Les refus/erreurs ne recopient aucun flux brut ; le bilan n'ouvre aucun rapport métier pour en extraire des nombres.
Le banc réemploie A-02 sans l'éditer, sources copiées en lecture seule, sans montage/port/réseau, PHP uniquement en conteneur, suppression du seul runner possédé puis lecture de son absence. Le seed A-16 est réemployé sans édition ; les seuls chemins absolus de pièces jointes sont normalisés par API native sur la fixture jetable **avant gel**, pour satisfaire le contrat A-12. Aucun changement d'un outil pour faire passer la tournée.
Les tests Python sont rejoués sous Windows propre (Python 3.14.6) : **3 tests verts en UTF-8, 3 en cp1252**, TMPDIR retiré aux fils, TEMP/TMP dans deux scratch distincts. La matrice native finale comporte **40 lignes : 36 PASS et 4 FAIL** (deux refus de statut non obtenus, puis leurs deux exceptions de fixture) ; le runner sort réellement 1. Sur chaque magasin, les **13/13** commandes aboutissent sans marqueur et en environnement déclaré production, base/fichiers identiques. Le RED initial et les diagnostics Docker restent hors dépôt. Le contrôle négatif de statut reste rouge : la matrice d'acceptation complète, le second passage natif cp1252, les gates image/global et PAQUETS A-32 ne sont donc **pas acquis**. Le vérificateur sans argument refuse ce paquet par `A32_PARTIAL_EVIDENCE` ; `rejeu.json` le déclare honnêtement, donc un futur PAQUETS incluant A-32 sera rouge tant que ce contrat n'est pas arbitré.

## Relecture parent en lecture seule
`C:/Python314/python.exe -B production/A-32/verify.py`
`production/A-32/preuves/final/native/classic-unverified-proof.json`
`production/A-32/preuves/final/native/hpos-unverified-proof.json`
`production/A-32/preuves/final/native/result.json`
`production/A-32/preuves/final/native/runner.json`

Le verrou du parent est rafraîchi et conservé ; aucun autre lot commencé.
