# Lot C-30 — La page d'offre de bienvenue et son code suivi

**Voie** : 2. **Chantier** : C. **Délai** : trois heures. **Dépend de** : C-10 (écran de réglages), C-14, C-16, C-19 (tableau de bord), C-21 (export et effacement), C-27 (« Comment nous avez-vous connus ? »). **Cahier des charges** : §3.7 (« Page d'offre de bienvenue accessible par QR code (affiches, magazine, événements), avec un code suivi »), §3.14 (« Suivi : codes suivis, adresses de campagne, événements de conversion »), §4.2 (« source d'acquisition »). Relis-les.

## Pourquoi

Imagine imprimera des QR codes sur ses affiches, dans le magazine, à ses événements. Chacun mène à la même page de bienvenue, avec un code qui dit d'où vient le visiteur. Le site doit pouvoir répondre : combien de commandes viennent de l'affiche, combien du magazine. Sans traceur tiers.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : ce que WooCommerce fait déjà de l'origine d'une commande (attribution native), ce qu'il en garde et où, et pourquoi on s'en sert ou non pour un code imprimé.

- **Une page « Bienvenue »**, publique, à une adresse courte, avec un lien vers la page de l'entrée « S'abonner ». Son texte est vide exprès : il viendra d'Imagine. Sans code, ou avec un code inconnu, la même page, sans erreur.
- **La liste des codes est un réglage**, journalisé comme les autres : un identifiant court et un libellé interne par code. Sur la démonstration, trois codes manifestement fictifs. Liste vide : aucun code n'est retenu.
- Le code d'une adresse n'est retenu que s'il est **dans la liste** ; une valeur inconnue n'est ni rangée, ni affichée, ni journalisée telle quelle.
- Le code retenu suit le visiteur le temps de sa session, par le mécanisme de session de WooCommerce, et il est rangé **sur la commande payée**, une fois, sans pouvoir être changé après coup. Dis ce que tu poses dans le navigateur et pour combien de temps.
- L'administration voit **des nombres par code**, sur une période, à côté de ceux de C-27 : aucune identité.
- Donnée rattachée à une commande : déclarée à l'export et à l'effacement de C-21.

Règles :

- **l'offre n'offre rien dans ce lot** : aucun prix modifié, aucun code de réduction créé ou appliqué. Ce que l'offre de bienvenue donne est une décision d'Imagine ;
- le code suivi ne remplace pas la réponse de C-27 et n'écrit pas la « source d'acquisition » du compte : les deux se lisent côte à côte ;
- aucun traceur, aucun script tiers, aucun appel sortant ; le QR code lui-même n'est pas fabriqué par le site ;
- une commande pour un client de C-16 ne porte pas de code ;
- rien n'est transmis à Odoo ni à la newsletter.

## Preuve

Proportionnée. Sur un achat fictif : venu par un code de la liste, la commande le porte ; par un code inconnu ou sans code, elle ne porte rien ; un code changé en cours de session, dis lequel gagne et prouve-le ; le compte par code est juste ; export et effacement ; aucun prix changé (le total de la commande est celui d'un achat sans code) ; une mutation témoin sur le contrôle « code inconnu non rangé ». Zéro appel sortant. Commandes, profils et réglages rendus dans leur état de départ.

## Livrables

Le code, ses tests, la section du README, `production/C-30/A-VOIR.md`, `PRET`. Rapport court.
