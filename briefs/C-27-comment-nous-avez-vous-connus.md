# Lot C-27 — « Comment nous avez-vous connus ? »

**Voie** : 2. **Chantier** : C. **Délai** : trois heures. **Dépend de** : C-14, C-16, C-19, C-21. **Cahier des charges** : §3.7 (« Question "Comment nous avez-vous connus ?" après le paiement » ; « Rien de plus que le nécessaire avant le paiement »), §4.2 (« source d'acquisition »), §2.2. Relis-les.

## Pourquoi

Imagine veut savoir d'où viennent ses abonnés : c'est un des rares chiffres d'acquisition que le site peut donner sans traceur. Le cahier des charges place la question **après** le paiement, jamais avant, et la veut facultative.

## Ce qu'on veut

**Le standard d'abord.** Dis en cinq lignes ce que WooCommerce offre déjà (attribution de l'origine d'une commande) et pourquoi il faut ou non autre chose pour une réponse déclarée par le lecteur.

- Sur la page de confirmation d'une commande payée, une question facultative, une seule réponse parmi une liste fermée. Ne pas répondre ne bloque rien et la question ne revient pas en boucle.
- **La liste des réponses est un réglage** de l'écran de C-10, journalisé comme les autres. Sur la démonstration, des réponses manifestement fictives ; liste vide, la question ne s'affiche pas.
- La réponse est rangée une fois par commande, datée, modifiable par personne après coup ; elle alimente la « source d'acquisition » du compte (§4.2) seulement si le compte n'en a pas déjà une.
- L'administration voit **des nombres par réponse**, sur une période, dans le tableau de bord de C-19 ou à côté : aucune identité.
- Donnée personnelle rattachée à une commande : déclarée à l'export et à l'effacement de C-21.

Règles :

- rien n'est ajouté avant le paiement, ni dans le tunnel, ni dans la commande pour un client de C-16 (l'opérateur ne répond pas à la place du lecteur) ;
- la réponse n'est transmise ni à Odoo ni à la newsletter (§2.2) ;
- pas de champ libre : un texte libre deviendrait une donnée à relire et à effacer ;
- aucun style inventé, aucun paiement réel, aucun email.

## Preuve

Proportionnée. Sur un achat fictif de la démonstration : la question s'affiche après le paiement et pas avant ; une réponse s'enregistre une seule fois (double envoi, envoi par un autre compte refusés) ; liste vide, rien ne s'affiche ; le compte par réponse est juste ; export et effacement ; une mutation témoin sur le contrôle « pas avant le paiement ». Commandes et profils remis dans leur état de départ.

## Livrables

Le code, ses tests, la section du README de l'extension, `production/C-27/A-VOIR.md`, `PRET`. Rapport court.
