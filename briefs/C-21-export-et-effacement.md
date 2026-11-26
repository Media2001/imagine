# Lot C-21 — Exporter et effacer les données d'un compte

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-12 à C-18. **Cahier des charges** : §4.4 (« RGPD : […] export et suppression de compte depuis le back-office »).

## Pourquoi

Quand un lecteur demande ce que le site sait de lui, ou demande à être effacé, le référent administratif doit pouvoir répondre depuis l'administration, sans appeler un développeur. WordPress a des outils pour cela et WooCommerce s'y branche. Mais ces outils ne connaissent pas ce que nous avons ajouté : tout ce qui est `imagine_` leur échappe tant qu'on ne le leur déclare pas.

## Ce qu'on veut

D'abord le standard : dix lignes dans `production/C-21/natif.md` sur les outils d'export et d'effacement de WordPress, et sur ce que WooCommerce, Subscriptions et Memberships y déclarent, d'après leur documentation officielle.

Puis :

- l'**inventaire** de ce que nos lots attachent à une personne (historique postal, marqueur « sans email », état de l'accès découverte, achats de numéros, catégorie et date de fin du tarif solidaire, et ce que tu trouveras d'autre) : une table dans le rapport, une ligne par donnée, avec le lot d'origine ;
- pour chacune, sa déclaration dans l'export natif et dans l'effacement natif. Rien n'est construit à côté des outils de WordPress.

Règles :

- **Tu ne changes aucun réglage de conservation** de WooCommerce et tu n'effaces rien de plus que ce que le standard efface déjà pour les commandes et les abonnements. Ce qu'Imagine doit garder pour sa comptabilité n'est pas arrêté : cite les réglages en vigueur dans `A-VOIR.md`, sans y toucher.
- Un compte avec un abonnement en cours : comportement natif, décris-le, n'ajoute pas de règle.
- L'export ne contient jamais de mot de passe, de jeton, de référence de moyen de paiement ni de note interne. L'adresse technique d'un compte « sans email » n'y figure pas comme une adresse électronique.
- Les lignes de journal qui ne contiennent aucune donnée d'abonné (extractions, C-18) ne sont pas concernées : dis-le dans l'inventaire.
- Si le parcours natif exige un email de confirmation au lecteur, les envois restent coupés : passe par le chemin d'administration qui s'en dispense s'il existe, sinon dis ce qui n'a pas pu être montré.

## Preuve

Proportionnée. Un compte fictif créé pour le lot, qui porte chacune des données de l'inventaire : l'export les contient toutes ; après effacement, une relecture n'en trouve plus aucune ; les profils de C-09 sont intacts ; le compte du lot est supprimé à la fin.

## Livrables

Le code, ses tests, `production/C-21/A-VOIR.md` (où ouvrir les deux outils, ce qu'on y voit), `PRET`. Rapport court dans `files/rapports/`.
