# C-25 — À voir sur la démonstration

Cible unique : `imagine-test-demo`, http://192.168.129.32:8085. Squelette du thème existant, sans nouveau style. **Une demande seulement : aucun remboursement, aucune annulation, aucune fermeture d’accès.** Aucune validation juridique actuelle n’est revendiquée.

## Parcours lecteur

- Se connecter avec le personnage fictif **P-NUMERO** (identifiants privés habituels de C-09), puis ouvrir `/my-account/view-order/126/`. La commande est un paiement **fictif**, pas un paiement bancaire. L’entrée « Me rétracter » conduit à `/my-account/?imagine_retractation=126`.
- Étape 1 : référence de commande, début et fin du délai UTC, motif libre **facultatif**. « Continuer » montre l’étape 2 sans enregistrer de demande. « Abandonner » n’enregistre rien.
- Étape 2 : « Confirmer ma demande de rétractation ». Ensuite, accusé daté ; on le retrouve à la même adresse et sur la vue de commande. Un second envoi montre le premier accusé.
- Les demandes de la recette ont été retirées après contrôle : cette commande reste disponible pour une démonstration, sans accusé d’essai conservé. Avec le défaut de 14 jours depuis le paiement fictif du 25 novembre 2026, elle sera naturellement hors délai après son échéance ; ne pas rajeunir sa date de paiement pour une présentation.
- Hors délai : le compte de la commande 88 n’a pas l’entrée. Un POST direct signé est également refusé. Le compte d’autrui n’obtient ni formulaire ni accusé de cette commande.
- Depuis un abonnement natif, l’entrée porte sur **sa commande initiale**, après vérification des deux titulaires. Un abonnement sans commande initiale reste fermé. Aucun lien « offert » ou « groupé » n’a été fabriqué.

## Administration

- `/wp-admin/admin.php?page=imagine-reglages` : section « Rétractation — demande seule », **14 jours** et **date de la commande payée** par défaut. Autre origine : date manuelle sur la commande. Valeurs 1 à 365 jours, invalides refusées ; sans date valide, fermé.
- La fiche native WooCommerce d’une commande porte le champ « Début manuel du délai de rétractation (UTC) ». Cette date n’est pas un changement de paiement.
- `/wp-admin/admin.php?page=imagine-retractations` : liste datée, commande et motif facultatif ; aucune commande d’annulation ou de remboursement.
- Chaque demande produit une **note privée WooCommerce** et une ligne du journal C-10. La liste sera vide avant votre propre démonstration : les essais ont été effacés et les profils restaurés.
- Outils natifs d’export/effacement : raccord « Demandes de rétractation ». Le motif et la note sont effacés, le journal retire l’auteur et l’identifiant de note. Il conserve la date et la référence de commande anti-doublon, comme trace métier C-10 : ce n’est pas une promesse d’anonymisation irréversible de la commande ; aucune politique de conservation native n’a été réécrite.

## Questions fermées pour Imagine et son conseil

1. **Accès** : après traitement humain de la demande, conserver l’accès jusqu’au terme payé, oui/non ? Dans ce lot, il reste inchangé.
2. **Remboursement** : déclencher un remboursement après décision humaine, oui/non ? Dans ce lot, aucun remboursement, même « manuel » WooCommerce.
3. **Abonnement dont le premier numéro n’est pas parti** : faire partir le délai de la première réception plutôt que du paiement, oui/non ? Dans ce lot, défaut paiement ; une date manuelle permet l’autre décision sans la choisir à votre place.

## Preuves et limites

Les commandes de rejeu, le standard consulté, les anciens reçus rouges conservés et leurs corrections sont décrits dans `NOTE.md`. Le dernier reçu de recette est `recette-livraison-V2.json` : deux confirmations HTTP concurrentes, un seul enregistrement, export/effacement, droits inchangés, puis restauration exacte et retrait des observateurs.

La validation visuelle reste à Ced. Le lot ne vaut ni validation du cadre légal mentionné par le cahier des charges, ni accord de déploiement, ni raccordement aux emails. C-23 reste clos et sa matrice n’a pas été modifiée : les nouvelles sorties seront reprises par C-26.
