# Lot A-08 — La répétition de la bascule, sur le banc fictif

**Voie** : 1. **Chantier** : A. **Délai** : une demi-journée. **Dépend de** : A-02, A-03, A-04, A-05 (tu construis sur A-05 sans attendre sa clôture ; ses corrections passent avant).

## Pourquoi

Les quatre outils de bascule existent et sont prouvés un par un : audit, non-régression, mise à jour, nettoyage. Le jour de la mise en ligne, et la semaine d'avant pour la répétition générale (décision du 19/11), quelqu'un les enchaînera sur une copie fraîche, sous pression. Personne ne les a encore lancés à la suite. Ce lot vérifie que la chaîne tient, et écrit la marche à suivre que Ced aura sous les yeux.

## Ce qu'on veut

1. **Une séquence**, dans `wp/outils/bascule/`, qui enchaîne sur un site : audit → photo de non-régression « avant » → mise à jour (A-04) → nettoyage (A-05) → photo « après » → comparaison. Elle s'appuie sur le lanceur existant ou sur une commande à côté de lui : choisis le plus simple et dis pourquoi.
2. **Elle n'ajoute aucune logique** : elle appelle les outils existants avec leurs garde-fous, sans les contourner ni les réécrire. Les préalables (sauvegarde, maintenance, statut du site, GO écrit pour la branche production) restent ceux d'A-04 et d'A-05.
3. **Arrêt au premier refus ou à la première anomalie**, avec le nom de l'étape et ce qu'il faut regarder. Reprise à l'étape interrompue si les outils le permettent ; sinon dis-le, et dis d'où on repart.
4. **Un seul rapport de fin**, court, lisible par Ced : chaque étape, sa durée, son résultat, où sont ses preuves ; la comparaison avant/après en clair (attendu, anormal). Aucune valeur de la base dans le rapport.
5. **La marche à suivre** `wp/outils/bascule/repetition.md` : une page, dans l'ordre, avec pour chaque étape la commande exacte, ce que Ced doit avoir préparé (plan de mise à jour, plan de nettoyage, sauvegarde), ce qui est un arrêt normal et ce qui ne l'est pas. Les endroits où un GO écrit de Ced est requis sont marqués comme tels.

## Preuve

Sur le banc fictif d'A-04 et A-05, classique et HPOS :

- la séquence complète va au bout, et la comparaison ne montre que les changements attendus ;
- une étape en échec au milieu (un refus provoqué) arrête tout, rien de ce qui suit n'est lancé ;
- une reprise après arrêt ;
- un second passage complet sur le site déjà traité ne change rien.

Dis les durées mesurées : elles serviront à estimer la fenêtre de maintenance, en sachant que le site réel est bien plus gros.

Preuves proportionnées. Tu n'ouvres pas l'archive d'Imagine, tu ne remplis aucun plan pour le site réel, tu ne touches ni au site de démonstration ni à l'outil de staging.

## Livrables

La séquence, ses tests, `repetition.md`, `production/A-08/PRET`. Rapport court, avec ce qui t'a surpris en enchaînant.
