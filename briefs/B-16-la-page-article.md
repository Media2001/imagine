# Lot B-16 — La page article : ce qui entoure le texte

**Voie** : 2. **Chantier** : B. **Délai** : trois heures. **Dépend de** : B-01 (squelette), C-08 (paywall sur article), B-03 (mode lecture), B-04 (page numéro, thématiques). **Cahier des charges** : §3.3 (« Page article : lecture longue adaptée au mobile, résumé et mots-clés en tête (fiche du 23 avril), signature du journaliste, numéro d'origine, appel à l'abonnement en fin d'article et dans le paywall » ; « HTML sémantique (balise article, titres hiérarchisés, paragraphes, figures légendées), sans contenu parasite dans le flux du texte »). Relis-le.

## Pourquoi

La page article a son paywall et son mode lecture, pas encore ce que le cahier des charges met autour du texte : le résumé et les mots-clés en tête, la signature, le numéro d'origine, l'appel à l'abonnement en fin d'article. C'est la page la plus lue du site ; sa structure doit être là avant les maquettes.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : ce que WordPress donne déjà (extrait, étiquettes, auteur), et pourquoi on s'en sert ou non pour le résumé, les mots-clés et la signature.

Tu pars de `single.php` tel qu'il est. Dans cet ordre :

1. **En tête** : le titre, le résumé, les mots-clés, la thématique (lien vers sa page), la signature, le **numéro d'origine** (lien vers la page numéro), le temps de lecture de B-03 s'il existe déjà.
2. **Le texte**, rendu par C-08 sans y toucher : complet pour l'ayant droit, extrait puis bloc d'abonnement pour les autres.
3. **En fin d'article**, pour un lecteur qui a lu le texte complet sans être abonné (acheteur du numéro, accès découverte) : un appel à l'abonnement, un lien vers la page de l'entrée « S'abonner » du menu. Un abonné actif ne le voit pas. Le non-abonné a déjà le bloc du paywall : pas de second appel sous le premier.

Règles :

- **le résumé et les mots-clés sont publics** : ils sont affichés à tous, comme le titre. Le résumé est un champ saisi par la rédaction, jamais tiré du texte réservé par le site ; champ vide, rien ne s'affiche. Dis où tu le ranges ;
- la signature est un nom affiché, sans page d'auteur ni adresse ; article sans signature, rien ne s'affiche ;
- un article sans numéro n'affiche pas de numéro d'origine et ne casse pas la page ;
- HTML sémantique : une balise `article`, un seul titre de premier niveau, des titres hiérarchisés, rien de parasite dans le flux du texte ; **le mode lecture de B-03 continue de n'afficher que le texte** (dis ce qu'il fait de l'en-tête) ;
- structure seule, lisible sans JavaScript, aucun style inventé ;
- le balisage de contenu payant et les descriptions que C-08 pose déjà dans l'en-tête de la page ne sont pas modifiés ; le résumé de la rédaction ne les remplace pas dans ce lot.

## Preuve

Proportionnée. Sur un article réservé et un article libre de la démonstration : l'ordre des éléments pour un anonyme, pour `A-PAPIER` et pour un acheteur du numéro ; l'appel de fin d'article présent pour l'acheteur, absent pour l'abonné et pour l'anonyme ; résumé, signature et numéro vides sans trace ; un seul titre de premier niveau. Étanchéité : les témoins de C-26 absents de l'en-tête et de la fin d'article pour un anonyme, sans étendre la matrice ; une mutation témoin sur ce contrôle. Mode lecture inchangé. Données rendues dans leur état de départ.

## Livrables

Le code, ses tests, la section du README, `production/B-16/A-VOIR.md` avec une capture, `PRET`. Rapport court.
