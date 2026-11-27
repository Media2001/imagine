# Lot B-15 — Le pied de page, identique sur toutes les pages

**Voie** : 2. **Chantier** : B. **Délai** : deux à trois heures. **Dépend de** : B-01 (squelette), B-09 (liens légaux déjà posés dans le menu du pied de page), B-10 (points de vente), B-04 (numéro en cours), C-22 (« Nos newsletters »). **Cahier des charges** : §3.2 (« Pied de page identique sur toutes les pages : abonnement, newsletter, numéro en cours, point de vente le plus proche, mentions »). Relis-le.

## Pourquoi

Le pied de page ne porte aujourd'hui que les liens légaux de B-09. Le cahier des charges y veut cinq choses, les mêmes partout. C'est la dernière zone commune à toutes les pages qui n'a pas son contenu.

## Ce qu'on veut

**Le standard d'abord.** Trois lignes : ce qu'un emplacement de menu et une zone de widgets natifs font seuls, et pourquoi on s'en sert ou non.

Tu pars de `footer.php` et du menu `imagine-footer` tels qu'ils sont, sans recréer le menu ni doubler une entrée de B-09. Cinq zones, dans cet ordre :

1. **Abonnement** : un lien « S'abonner », vers la même page que l'entrée du menu principal.
2. **Newsletter** : un lien vers « Nos newsletters ». Aucun champ de saisie d'adresse : l'inscription d'un visiteur sans compte attend Brevo.
3. **Le numéro en cours** : couverture en petit, titre, lien vers la page numéro. Le même numéro que celui de l'accueil, par la même règle.
4. **Point de vente** : un lien « Trouver un point de vente » vers la page de B-10. **Aucune géolocalisation**, ni par le navigateur, ni par l'adresse IP, ni par un service tiers : « le plus proche » est une question rangée pour Imagine. Le lien suffit.
5. **Mentions** : le menu de B-09, inchangé.

- **Identique partout** : même contenu pour un anonyme et pour un lecteur connecté, sur toutes les pages publiques, mode lecture de B-03 excepté s'il masque déjà le pied de page (dis ce qu'il fait).
- **Structure seule**, lisible sans JavaScript, aucun style inventé.
- **Rien de réservé** : titre, couverture, liens.
- La zone du numéro en cours est construite une fois et gardée en cache ; dis ce qui la renouvelle (publication ou dépublication d'un numéro).

## Preuve

Proportionnée. Les cinq zones dans l'ordre, une fois chacune, sur l'accueil, un article réservé, une page numéro et « Mon compte » ; le même HTML de pied de page pour un anonyme et pour le profil `A-PAPIER` ; les liens de B-09 toujours présents, une seule fois ; après publication d'un numéro d'essai plus récent, la zone change, puis revient quand il est retiré. Étanchéité : les témoins de C-26 absents du pied de page pour un anonyme, sans étendre la matrice. Zéro appel sortant. Menu et numéros rendus dans leur état de départ.

## Livrables

Le code, ses tests, la section du README, `production/B-15/A-VOIR.md` avec une capture, `PRET`. Rapport court.
