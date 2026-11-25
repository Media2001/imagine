# Lot A-11 — L'inventaire des adresses publiques

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Cahier des charges** : §4.3, dernier point (« inventaire des adresses référencées et des pages qui reçoivent des liens, plan de redirections validé avant la bascule »).

## Pourquoi

A-09 vérifie un plan de redirections ; encore faut-il que le référenceur puisse l'écrire. Pour cela il lui faut la liste de ce que le site actuel expose aujourd'hui. Les pages « qui reçoivent des liens » viendront de ses propres outils ; la liste des adresses, elle, se lit dans le site. Ce lot fournit l'outil, prêt pour le jour où le staging d'Imagine sera vérifié.

**Ce lot ne décide d'aucune redirection et ne juge aucune adresse.**

## Ce qu'on veut

Un complément du script d'audit (A-02), en **lecture seule**, qui produit pour un site un fichier tableur des adresses publiques :

- une ligne par adresse : adresse **relative**, nature (article, page, produit, terme de taxonomie, archive d'auteur, archive de type de contenu, pièce jointe), type de contenu, état de publication, date de dernière modification ;
- seulement ce qui est public et publié ; les brouillons, les contenus privés ou protégés par mot de passe sont **comptés**, pas listés ;
- les adresses construites par les règles natives de WordPress et de WooCommerce (permaliens), pas par une visite du site : aucun appel HTTP ;
- un résumé lisible : nombre d'adresses par nature, structure de permaliens en vigueur, bases de catégories et de produits.

Le fichier ne contient **aucune donnée de client** : les archives d'auteur ne portent que l'identifiant public de l'auteur déjà visible dans l'adresse. Il s'écrit hors de la racine web, au même endroit que le rapport d'audit, et ne rejoint jamais le dépôt quand il vient d'un site réel.

Sa sortie doit pouvoir servir de colonne « ancienne adresse » au plan que lit A-09 : même convention d'écriture des adresses relatives. Si les deux conventions divergent, dis-le plutôt que d'en inventer une troisième.

Classique et HPOS. Aucun écrit en base, aucune tâche planifiée, aucun envoi.

## Preuve

Sur le banc fictif d'A-02 : quelques contenus de chaque nature, dont un brouillon, un privé et un protégé. Les comptes sont exacts, les trois contenus non publics sont absents de la liste, l'empreinte de la base est identique avant et après. Preuves proportionnées : une suite dédiée, pas de rejeu global.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-11/PRET`. Rapport court.
