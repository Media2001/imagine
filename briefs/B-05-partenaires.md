# Lot B-05 — Les partenaires

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-00, B-01. **Cahier des charges** : §3.12 (« Partenaires »). Relis-le.

## Pourquoi

Imagine veut montrer ses partenaires sans que le lecteur les confonde avec le travail de la rédaction, et sans que les moteurs de recherche prennent ces liens pour des recommandations éditoriales. Le cahier des charges est précis là-dessus ; c'est donc faisable avant les maquettes, en squelette.

## Ce qu'on veut

Sur le site de démonstration, avec les partenaires fictifs de B-00 :

- un bloc **« partenaire du mois »** sur la page d'accueil. Le partenaire du mois est désigné à la main dans l'administration (un seul à la fois) ; sans désignation, le bloc n'apparaît pas. Aucune rotation automatique, aucune règle de choix ;
- une page **« Nos partenaires »** : la liste, et la fiche de chacun (celle de B-01, complétée si besoin) ;
- sur le bloc, la liste et la fiche : l'étiquette **« Partenariat »**, lisible sans la couleur, et un conteneur distinct de ceux des articles. Le dessin est celui du designer : pose l'étiquette et une classe, pas un style ;
- tout lien sortant vers un partenaire porte la déclaration de lien commercial pour les moteurs de recherche (`rel="sponsored"`), posée par le gabarit, y compris quand le lien est saisi dans le texte de la fiche ;
- un partenaire n'apparaît jamais dans les listes d'articles, la recherche interne des articles ni les flux de la rédaction.

Les règles d'acceptation d'un partenaire relèvent de la rédaction : rien dans ce lot.

## Preuve

Proportionnée. Un test qui relit les pages rendues : étiquette présente aux trois endroits, tous les liens sortants des partenaires déclarés commerciaux, aucun lien d'article qui le soit, bloc absent quand aucun partenaire n'est désigné, aucun partenaire dans la recherche ni dans le flux. Deux captures.

## Livrables

Le code, ses tests, `production/B-05/A-VOIR.md` (avec ce que le designer devra dessiner), `PRET`. Rapport court.
