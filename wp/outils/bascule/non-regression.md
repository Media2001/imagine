# A-03 — mode d’emploi
1. Exécuter seulement sur copie fictive ou staging déjà vérifié par A-01, jamais sur production ; aucun GO réel n’est donné ici.
2. Conserver le MU de sécurité A-01 intact et le témoin `.imagine-staging-verified.json` ; les blocages courrier, réseau, passerelles et ordonnanceurs sont recontrôlés nativement.
3. Copier `wp/tests/a03-non-regression/exemple.json` hors du site et adapter mois UTC, IDs restreints, sept chemins relatifs et marqueurs publics ; conserver ce même fichier avant/après.
4. Photo : `php wp/outils/bascule/non-regression --wp-path=/site-verifie --config=/travail/config.json --output=/travail/avant` ; configuration SQL du site en SELECT seulement, aucune modification automatique de celle-ci.
5. Rejouer vers un nouveau dossier `apres`, puis `php wp/outils/bascule/comparer /travail/avant/non-regression.json /travail/apres/non-regression.json` ; sorties : 0 identique, 2 anormal, 3 changement à regarder/attendu, 1 refus.
6. Versions = attendu ; droits, états, nombres, montants, échéances et actions = anormal ; HTTP sain modifié = à regarder, marqueur perdu/erreur PHP visible/HTTP défaillant = anormal ; aucune valeur personnelle n’est exportée.
7. Test distinct opt-in : ajouter `--renewal-test` avec configuration SQL inscriptible ; il produit seulement la sonde de renouvellement, crée une commande manuelle impayée via Subscriptions, nettoie et annule sa transaction, sans paiement ni file globale.
8. Relecture fictive reproductible sous Windows : `python wp/tests/a03-non-regression/run.py --name relecture-a03` ; WSL/Docker existants, image et deux ZIP de plugins acceptés par A-02 requis, aucun téléchargement ni PHP hôte.
9. Périmètre : site simple sans drop-in DB/cache, tables InnoDB pour la sonde ; douze mois UTC de création, montants séparés par devise, GET visiteur sans session ni redirection hors site, erreurs PHP visibles seulement ; AUTO_INCREMENT peut avancer lors de la sonde.
