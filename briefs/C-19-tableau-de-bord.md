# Lot C-19 — Le tableau de bord

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-13, C-15, C-18. **Cahier des charges** : §3.13 (« Tableau de bord »). Relis-le.

## Pourquoi

Imagine compte aujourd'hui ses abonnés à la main. Le cahier des charges promet un tableau de bord, dont le contenu sera arrêté lors d'un atelier avec la direction. Un atelier se passe mieux devant un écran que devant une page blanche : ce lot pose l'écran et les premiers chiffres, ceux que les données permettent aujourd'hui.

## Ce qu'on veut

Dans l'administration de `imagine-test-demo`, sous le menu Imagine existant : un écran « Tableau de bord », réservé par un droit dédié, lisible en compte `e-abo`.

Indicateurs de départ :

1. abonnés actifs, au total et par mode de paiement ;
2. abonnements arrivant à échéance à un, trois et six mois ;
3. paiements échoués en cours ;
4. entrées et sorties du mois civil en cours.

Sous chaque chiffre, **une phrase qui dit comment il est compté**. C'est elle qu'Imagine discutera.

Les autres indicateurs du §3.13 figurent dans l'écran, grisés, avec la mention « à venir » et ce qui leur manque : par tarif (grille non arrêtée), taux de rétention annuel (définition à arrêter à l'atelier), motifs de non-renouvellement, passages de l'accès découverte à l'abonnement, part du tarif solidaire et de soutien, étiquettes de persona. **Ne fabrique ni ces données ni leur formule.**

Règles :

- **Lecture seule.** Aucune écriture, aucune tâche planifiée, aucun appel sortant.
- Un abonné « actif », une échéance, un paiement échoué veulent dire la même chose ici que dans l'écran des échéances (C-15) et dans les extractions (C-18) : réemploie leurs règles, n'en écris pas de nouvelles. Si deux écrans ne peuvent pas donner le même nombre, dis pourquoi.
- Un indicateur se décrit en un seul endroit du code (son calcul, sa phrase), pour qu'en ajouter un soit l'affaire d'un fichier. Calculs en code pur, testables sans WordPress.
- Des nombres dans un tableau simple. Pas de bibliothèque de graphiques, pas de script.
- Aucun nom, aucune adresse : l'écran ne montre que des nombres.

## Preuve

Proportionnée. Avec les profils de C-09 : chaque chiffre est égal au nombre de lignes de l'extraction ou de la vue correspondante pour le même filtre ; un compte sans le droit reçoit un refus ; la base est inchangée après l'affichage.

## Livrables

Le code, ses tests, `production/C-19/A-VOIR.md`, `PRET`. Rapport court dans `files/rapports/`.
