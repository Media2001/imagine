# Lot A-12 — L'inventaire des contenus à reprendre

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Cahier des charges** : §4.3, premier point (« les dix derniers numéros (sommaires, articles, médias, PDF) repris du site actuel, chaque article rattaché à son numéro et à sa thématique »), §4.2.

## Pourquoi

On repart de la production : les contenus sont déjà là, mais personne ne sait encore sous quelle forme. Les articles sont-ils rattachés à un numéro ? Par une catégorie, un champ, un produit ? Où sont les PDF ? Avant d'écrire le modèle éditorial, il faut une photographie. Ce lot fournit l'outil qui la prendra sur le staging d'Imagine le jour où il sera vérifié.

**Ce lot ne décide d'aucun rattachement et ne modifie aucun contenu.** Il décrit.

## Ce qu'on veut

Un complément du script d'audit (A-02), en **lecture seule**, qui produit pour un site :

- les types de contenu et les taxonomies enregistrés, avec pour chacun : qui le déclare (cœur, thème, extension — par le nom du fichier déclarant quand il est lisible), le nombre de contenus par état, la première et la dernière date de publication ;
- pour chaque taxonomie : le nombre de termes et, pour les vingt termes les plus utilisés, leur nom et leur nombre de contenus (ce sont des rubriques du site, pas des données personnelles) ;
- les champs personnalisés des contenus : pour chaque type, la liste des **clés** de métadonnées et le nombre de contenus qui les portent. **Jamais les valeurs** ;
- les pièces jointes : nombre et poids total par type de fichier, nombre de PDF, nombre de pièces jointes orphelines ;
- les liens visibles entre contenus et produits (un article ou un numéro relié à un produit WooCommerce), comptés par clé de liaison quand elle est reconnaissable, sans interprétation.

Aucun titre d'article, aucun texte, aucun nom d'auteur, aucune donnée de client dans la sortie : des structures et des nombres. Le rapport s'écrit hors de la racine web, au même endroit que le rapport d'audit, et ne rejoint jamais le dépôt quand il vient d'un site réel.

Classique et HPOS. Aucun écrit en base, aucune tâche planifiée, aucun envoi, aucun appel HTTP.

## Preuve

Sur le banc fictif d'A-02 : un type de contenu et une taxonomie déclarés pour l'occasion, quelques contenus avec des champs, deux PDF dont un orphelin. Les comptes sont exacts ; aucune valeur de champ ni aucun titre dans la sortie ; l'empreinte de la base est identique avant et après. Preuves proportionnées : une suite dédiée, pas de rejeu global.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-12/PRET`. Rapport court.
