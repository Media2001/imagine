# A-32 — Tournée des inventaires

## Le standard d'abord

A-08 (`../a08/sequence.py`, `../repetition.md`) enchaîne audit, photographies, mise à jour et nettoyage, avec arrêt au premier refus.
La tournée ne lance aucune de ces étapes : elle ne fait que lire par les commandes d'inventaire closes et continue après leur refus ou échec.
Une commande distincte évite donc de réemployer une séquence mutante pour un besoin exclusivement en lecture seule ; aucun outil ni gardien commun n'est changé.

## Mode d'emploi courant

La tournée ne tourne que sur une copie vérifiée ; lancer un outil seul reste la décision de Ced.

Avant tout outil, `.imagine-staging-verified.json` est lu à la racine du site : `status` vaut `verified`, `offline_verified` et `runtime_probe_passed` valent strictement `true`, exactement la règle de lecture d'A-05 (`clean.py`, lignes 210–211), recopiée localement pour ne pas importer un outil de mutation. Aucun champ ou format de marqueur supplémentaire n'est requis. Le fichier est régulier, non symbolique et borné à 16 Mio comme le lecteur A-04 utilisé par A-05. Le chemin du site est canonique sans lien symbolique.

Le `WP_ENVIRONMENT_TYPE` de `wp-config.php` doit être une déclaration littérale unique `staging`, lue sans exécuter PHP ; une déclaration production (y compris environnement hérité ou champ optionnel `environment` du marqueur), absente ou opaque est refusée. Fichier absent/invalide ou environnement refusé : sortie 1, stdout vide, stderr exactement `A32_NOT_VERIFIED`, aucun outil lancé et aucune sortie créée. Pas d'option de contournement.

Prérequis : Linux déconnecté avec Landlock/PHP CLI et les prérequis natifs de chaque outil ; audit A-02 déjà réalisé sur cette même copie ; correspondance A-16 fournie. Le parent privé de sortie existe, hors dépôt/site et disjoint dans les deux sens (pas un ancêtre), frère du dossier d'audit. Le nom de sortie est neuf, ASCII alphanumérique/tiret/souligné ; toutes les sorties suffixées d'outils sont neuves également.

```sh
python3 wp/outils/bascule/tournee/tournee.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --correspondance=/hors-web/correspondance.json --output=/hors-web/tournee-date
```

Seuls les chemins d'exemple changent. La tournée conserve interprètes, options et littéraux des commandes documentées dans `outils.jsonl`. Chaque ligne est contrôlée contre le mode d'emploi de son outil. Le gardien A-22 est réemployé inchangé ; les outils appliquent leurs propres confinements et contrôles de rapports.

A32-CONTRAT : outils clos et ordre fermés dans tournee/outils.jsonl ; chaque commande documentée garde ses seuls arguments, seuls les chemins opérateur changent ; gardien commun inchangé.
A32-BILAN : bilan.json et bilan.md hors dépôt, statuts et codes fermés, sorties entières et chemins opérateur seuls ; tous les outils continuent, sortie 1 au moindre refus/échec, bilan partiel jamais complet.

Code 0 et `A32_COMPLETE bilan.json bilan.md` uniquement si les quinze outils réussissent. Sinon code 1 et `A32_PARTIAL bilan.json bilan.md`, bilan `partielle` même lorsque tous les outils ont été tentés. En cours de tournée le bilan reste toujours `partielle`. Chaque ligne contient l'outil, `réussi`, `refusé` avec code fermé ou `en échec` avec entier de sortie, et le chemin opérateur du rapport. Aucun nombre des rapports ni sortie brute n'est recopié. Une interruption ne peut pas laisser une déclaration de tournée complète.

## Liste fermée et exclusions

Ordre : A-10, A-11, A-12, A-15, A-16, A-17, A-18, A-19, A-20, A-21, A-23, A-24, A-25, A-26, A-27. Ajouter un outil clos est une ligne dans `outils.jsonl`, après qualification du paquet ; aucun mécanisme de découverte de nouveaux outils.

Hors tournée : A-02 est le prérequis d'audit ; A-03 relève de la non-régression ; A-04/A-05/A-08 sont des séquences mutantes ; A-09 exige un plan opérateur hors inventaire ; A-13/A-14/A-30 demandent un fichier d'Imagine ; A-22 est le gardien ; A-28 est l'import gelé ; A-29/A-31 ne sont pas clos. Raisons fermées dans `exclusions.json`. Aucune lecture d'archive ou donnée réelle, aucun compte, réseau ou déploiement n'est autorisé par ce mode d'emploi.

## Preuves

`wp/tests/a32/matrix.py --output=<dossier-neuf-hors-depot>` exécute réellement les suites Python puis la tournée native classique/HPOS dans les deux consoles Windows UTF-8/cp1252, sans TMPDIR dans les enfants. Tests de refus global avant tout outil, base/fichiers immuables, doubles nommés A-10/A-11, tous les canaux de fuite et commande ci-dessus copiée sans argument caché.

Le mode d'emploi de référence du lot est ce fichier local, conformément au périmètre d'écriture strict A-32. L'ancienne section du README commun n'est pas réécrite par ce lot ; son ancienne phrase d'exclusion A-26/A-27 est remplacée par la présente liste courante. Les trois lignes communes historiquement contractuelles restent contrôlées par contenu, jamais par empreinte globale.
