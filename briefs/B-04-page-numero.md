# Lot B-04 — La page numéro et le kiosque

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-01, C-08, C-11, C-14. **Cahier des charges** : §3.3 (index des numéros, page numéro, page thématique).

## Pourquoi

Le paywall, le PDF protégé et l'achat au numéro existent, chacun de son côté. La page numéro est l'endroit où un lecteur les rencontre ensemble : c'est là qu'il décide d'acheter ou de s'abonner. Aujourd'hui c'est un squelette de trente lignes. Ce lot la rend complète dans son fonctionnement, toujours sans habillage.

## Ce qu'on veut

Dans le thème `wp/themes/imagine/` :

- **Kiosque** (index des numéros) : tous les numéros, du plus récent au plus ancien, avec couverture, titre du dossier et date. Pagination native.
- **Page numéro** : présentation ; **sommaire détaillé**, où chaque article porte son **statut d'accès visible pour le visiteur courant** (libre, découverte, réservé, ouvert pour vous) ; l'article en accès libre mis en avant ; un **emplacement nommé** pour le sommaire audio (rien d'inventé : pas de lecteur, pas de fichier) ; le bouton « Acheter ce numéro » (parcours de C-14) pour qui ne l'a pas ; l'accès au PDF (C-11) pour les ayants droit, et rien pour les autres.
- **Page thématique** : les articles de la thématique, tous numéros confondus, avec le même statut d'accès visible.

Règles :

- **Le statut affiché vient de la décision d'accès** (C-06, par le même point d'entrée que le paywall de C-08). Le thème ne recalcule aucun droit : s'il affiche « ouvert pour vous », c'est que l'article s'ouvrira. Une seule fonction du thème pour ce statut, utilisée par les trois gabarits.
- **Rien ne fuit** : pour un visiteur sans droit, la page ne contient ni le texte réservé, ni l'adresse du PDF, ni un indice de son existence au-delà de ce que C-11 montre déjà.
- **Le bouton d'achat n'apparaît pas** à qui a déjà le numéro ou un abonnement qui le couvre ; il apparaît à l'anonyme.
- Attention au nombre de requêtes sur un sommaire long : dis combien pour un numéro de vingt articles.
- Gabarits sémantiques, utilisables au clavier, libellés traduisibles. Aucun parti pris graphique : variables de B-01, valeurs neutres.

## Preuve

Proportionnée. Test HTTP sur un même numéro, vu par un anonyme, par `a-carte` et par `p-numero` : statuts du sommaire, présence ou absence du bouton d'achat et du lien PDF, aucun texte réservé ni adresse de PDF dans la réponse anonyme. La fonction de statut testée seule si c'est simple.

## Livrables

Thème, tests, `production/B-04/A-VOIR.md` (trois visiteurs, quelles adresses, quoi voir), la liste de ce que le designer devra fixer, `PRET`. Rapport court.
