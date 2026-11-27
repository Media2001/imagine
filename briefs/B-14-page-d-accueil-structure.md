# Lot B-14 — La page d'accueil, dans l'ordre du cahier des charges

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-01 (l'accueil du squelette), B-04 (numéro, article en accès libre, thématiques), C-14 (achat d'un numéro), B-05 (partenaire du mois), B-07 (agenda), B-08 (Soutenir, coopérative), C-22 (« Nos newsletters »). **Cahier des charges** : §3.2 (« Page d'accueil »), chapitre 5 (ni vidéo ni carrousel au premier écran). Relis-les.

## Pourquoi

L'accueil de B-01 est une liste d'entrées posée avant que les pages existent. Elles existent maintenant. Le cahier des charges fixe ce que l'accueil contient et dans quel ordre ; la maquette, en cours chez le designer, en fixera la forme. On livre le contenu et l'ordre, pour que le gabarit n'ait plus qu'à habiller.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : ce que WordPress fait seul pour une page d'accueil (modèle `front-page.php`, image mise en avant, attributs de chargement d'une image), et ce qu'il faut ajouter.

Tu pars de `front-page.php` tel qu'il est, sans doubler une section. Dans cet ordre :

1. **Le numéro en cours** : couverture, titre du dossier, date, résumé. La couverture est une image fixe, la seule de la page chargée en priorité ; les autres images sont chargées à la demande. Ni vidéo, ni carrousel, ni animation : l'animation des pages intérieures dont parle le §3.2 relève de la maquette, tu ne la construis pas.
2. **Le bloc de conversion**, sous le résumé : « Découvrir le numéro » (la page numéro de B-04), « Acheter ce numéro » (le produit de C-14, absent s'il n'est pas en vente), « S'abonner » (la page d'attente déclarée telle, celle de B-13 si elle existe, sinon la même règle).
3. **Le reportage en accès libre du numéro en cours** : celui que B-04 désigne déjà. Titre, image, lien. S'il n'y en a pas, la section n'apparaît pas.
4. **Le bloc newsletter** : un lien vers « Nos newsletters ». Aucun champ de saisie d'adresse ici : l'inscription d'un visiteur sans compte attend Brevo.
5. **Puis** : l'entrée par thématiques, les événements à venir (trois au plus, ceux de B-07), Soutenir, la coopérative, le partenaire du mois (celui de B-05, tel quel).

« Le numéro en cours » est le numéro publié le plus récent, par la règle que B-04 emploie pour son kiosque : tu ne crées pas de second réglage.

- **Structure seule** : des sections titrées, dans l'ordre, lisibles sans JavaScript. Aucun style inventé.
- **Rien de réservé** : titres, images, résumé du numéro, liens. Ni extrait d'article réservé, ni texte.
- Les « Derniers articles » de B-01 ne sont pas au §3.2 : retire la section, et dis-le.

## Preuve

Proportionnée. Les sections présentes, une fois chacune, dans l'ordre, pour un anonyme et pour le profil `A-PAPIER` ; une seule image en chargement prioritaire ; ni `<video>`, ni `<iframe>` ; « Acheter ce numéro » absent quand le produit n'est pas en vente. Étiquette « Partenariat » du partenaire du mois toujours là (le contrôle de B-05 reste vert). Étanchéité : les témoins de C-26 absents de l'accueil pour un anonyme, sans étendre la matrice. Zéro appel sortant.

## Livrables

Le code, ses tests, la section du README, `production/B-14/A-VOIR.md` avec une capture, `PRET`. Rapport court.
