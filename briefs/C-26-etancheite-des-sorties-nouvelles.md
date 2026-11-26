# Lot C-26 — Le test d'étanchéité suit les sorties nouvelles

**Voie** : 2. **Chantier** : C. **Délai** : deux heures. **Dépend de** : C-23, B-06, B-07, C-24, C-25, B-08 (rendus). **Cahier des charges** : §4.4 (« Un test automatisé vérifie, à chaque livraison, qu'un visiteur anonyme ne peut obtenir le texte réservé par aucune de ces voies »).

## Pourquoi

Un test de livraison ne vaut que s'il suit ce qu'on livre. Depuis C-23, le site a gagné des sorties : l'agenda et ses inscriptions (B-07), le formulaire de personnalisation (C-24), la demande de rétractation (C-25), « Soutenir » et « Notre coopérative » (B-08). Et la couverture des pages coopérateurs (B-06) est entrée dans le test pendant un tour de correction, sans ses deux relectures : elle est en place et verte, mais elle ne compte pas encore comme prouvée.

**Ce lot ne touche ni au paywall, ni au thème : il met le test à jour.**

## Ce qu'on veut

- **L'inventaire des sorties ajoutées depuis C-23**, une ligne chacune : ce qu'elle peut laisser sortir (un texte réservé, ou une donnée d'un autre compte : une inscription, une réponse, une demande), et par quelle voie (page, REST, flux, recherche, oEmbed).
- **Chacune entre dans la matrice** de C-23, avec le public qui ne doit rien voir. Une mutation témoin par famille nouvelle.
- **Les pages coopérateurs restent dans la matrice.** Leur code est dans le périmètre de relecture de ce lot : nomme dans `A-VOIR.md` les fichiers et fonctions concernés (routes des coopérateurs et leur contrôle, inventaire des cinq pages, pose et retrait du témoin, recette de mutation), pour que les deux relecteurs les lisent comme du code neuf.
- Un test du lot lit `TMPDIR` sans repli et échoue sur un poste qui ne le définit pas : corrige-le.

Le test continue de lire les réglages livrés sans rien forcer (arbitrage de 19 h sur la découverte).

## Preuve

Proportionnée. Rejeu normal vert sous un nom de reçu neuf, aucune fuite ; chaque mutation témoin rouge ; le vérificateur de paquet tourne sans réseau et sans écrire dans `production/` ; la suite du lot passe sans `TMPDIR` défini. Les profils et réglages touchés reviennent à leur état métier de départ.

## Livrables

Le test mis à jour, `production/C-26/A-VOIR.md` (l'inventaire et la liste des fichiers à relire), `PRET`. Rapport court.
