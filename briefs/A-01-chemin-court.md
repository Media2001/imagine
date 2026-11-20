# Lot A-01 — finir par le chemin le plus court

**Date** : 21/11/2026. **Délai** : une demi-journée. Complète `briefs/A-01-reprise.md`, qui reste valable.

## Où on en est

Ton rapport du 20/11 à 15 h 35 l'établit : sur des sites jetables, avec les vrais Subscriptions et Memberships, la chaîne `neutraliser → anonymiser → verifier` passe en stockage classique et en HPOS, les données métier sont conservées, le mode staging est actif et un renouvellement forcé est bloqué. C'est le cœur du lot, et il est fait.

Ce qui manque : le branchement dans l'outil de staging. Tu le déclares « non prêt » parce que la fidélité des fichiers restaurés par l'importeur n'est pas démontrée.

## Ce qu'on veut maintenant

**Une commande que Ced lance lui-même**, qui part d'une archive `.wpress` et aboutit à un staging au statut « vérifié », ou à un rapport qui dit pourquoi il ne l'est pas. Pas une intégration complète ni qualifiée de bout en bout dans l'outil.

Prends le chemin qui demande le moins de code nouveau. Par exemple, si c'est le plus court : un script d'enchaînement, à côté de l'outil et sans le modifier, qui

1. restaure l'archive avec l'importeur existant, dans un site **sans port publié et sans sortie réseau** ;
2. lance les trois scripts ;
3. si la vérification réussit, publie le port, rétablit la sortie vers `*.wordpress.org` et `*.woocommerce.com`, et marque le site « vérifié » ;
4. sinon, laisse le site arrêté et affiche le rapport.

Si un autre chemin est plus court, prends-le et dis pourquoi.

## Sur la fidélité des fichiers

Ne cherche pas à la démontrer dans l'absolu. Démontre-la **sur un site jetable** : exporte-le en `.wpress`, restaure-le par ta commande, et compare avant et après (liste des extensions et du thème actifs, nombre de fichiers par dossier de `wp-content`, quelques empreintes). Les écarts attendus (archives purgées, drop-ins de cache retirés, mu-plugin ajouté) sont listés. C'est suffisant pour déposer `PRET`.

Le premier import réel sera lancé par Ced, et son rapport sera relu avant toute ouverture aux agents : c'est lui qui servira de preuve sur le vrai site.

## Livrables

1. La commande, et dans `production/A-01/notes.md` : comment la lancer, ce que Ced verra, combien de temps ça prend, quoi faire si une table est à trancher.
2. La preuve de l'aller-retour sur site jetable.
3. `production/A-01/PRET`.

## Limites

- Tu ne lances aucun import d'Imagine et tu n'ouvres pas son archive.
- Tu ne modifies pas le parcours d'import des autres sites de Ced. Si ton chemin exige de toucher au code partagé de l'outil, arrête-toi et pose la question.
- Ce que tu as écrit dans `wp/outils/staging-wp-integration/` et qui ne sert pas à ce chemin : laisse-le, ne le développe pas davantage, et dis ce qui est utilisé ou non.
