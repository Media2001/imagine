# Lot B-03 — Le mode lecture

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-01, C-08. **Cahier des charges** : §3.3, paragraphe « Mode lecture » et sa note technique. Relis-les : ils sont précis.

## Pourquoi

C'est la seule partie du thème que le cahier des charges décrit jusqu'au mécanisme. Elle ne dépend pas des maquettes : le designer choisira les valeurs, pas le fonctionnement. Et c'est ce qu'un lecteur d'Imagine fera le plus souvent sur le site.

## Ce qu'on veut

Sur la page article du thème `wp/themes/imagine/` :

- un bouton « Lire l'article » qui bascule la page en vue de lecture : menu, colonnes et appels à l'abonnement disparaissent, le texte reste seul, en grands caractères, sur une colonne de 65 à 75 signes ;
- réglage de la taille du texte ; fond clair, sépia ou sombre ;
- réglages et position de lecture mémorisés dans le navigateur (stockage local, aucun compte, rien envoyé au serveur) ;
- temps de lecture estimé et barre de progression.

Comme le cahier le demande : une feuille de style dédiée activée par **une classe sur la racine**, plus un script léger. Aucune extension, aucune bibliothèque. Dis le poids du script.

- **Le paywall ne bouge pas.** Pour un visiteur sans droit, la vue de lecture montre l'extrait puis le bloc d'abonnement, et la réponse du serveur ne contient rien de plus qu'aujourd'hui (C-08). Le corps de l'article passe toujours par le point de sortie unique de B-01.
- **Gabarit sémantique** : `article`, titres hiérarchisés, paragraphes, figures légendées, rien de parasite dans le flux du texte, pour que le mode lecture des navigateurs fonctionne aussi. Corrige le gabarit si besoin.
- **Sans JavaScript**, l'article se lit normalement et le bouton n'apparaît pas.
- **Accessibilité** : un vrai bouton, état annoncé, utilisable au clavier, respect de la préférence de mouvement réduit ; les trois fonds tiennent le contraste AA.
- **Aucun parti pris graphique** : tailles, largeur de colonne et couleurs des trois fonds passent par les variables de B-01, avec des valeurs neutres. Le temps de lecture est calculé côté serveur à partir d'une vitesse fixe, écrite à un seul endroit : dis laquelle.

## Preuve

Proportionnée. Test HTTP : abonné, texte complet et bouton présents ; anonyme, extrait seul, aucun texte réservé dans la réponse ni dans les données de la page. La logique du script (réglages, mémorisation, progression) testée hors navigateur si c'est simple ; sinon, décris la manipulation dans `A-VOIR.md`. Pas de banc de navigateurs.

## Livrables

Thème, tests, `production/B-03/A-VOIR.md` (en `a-carte` et en anonyme, sur un écran étroit et un large : quoi cliquer, quoi voir, y compris après rechargement), la liste de ce que le designer devra fixer, `PRET`. Rapport court.
