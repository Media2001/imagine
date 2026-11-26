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
- Depuis les corrections du 27 novembre, **chaque création/modification des deux réglages C25** produit aussi un événement avant/après avec auteur et date UTC dans ce même journal. En cas de panne du journal, l’ancienne valeur (ou l’absence initiale) revient effectivement après relecture. L’injection HTML existante est conservée ; aucun changement du markup ni nouveau hook C10.
- Un motif tel que `Document C:\dossier` est maintenant accepté, conservé et exporté avec ses antislashs. En cas de panne SQL persistante empêchant le nettoyage lors de `delete_user`, `wp_die` refuse la suppression du compte par prudence ; réparer le stockage puis réessayer.
- Outils natifs d’export/effacement : raccord « Demandes de rétractation ». Le motif et la note sont effacés, le journal retire l’auteur et l’identifiant de note. Il conserve la date et la référence de commande anti-doublon, comme trace métier C-10 : ce n’est pas une promesse d’anonymisation irréversible de la commande ; aucune politique de conservation native n’a été réécrite.

## Questions fermées pour Imagine et son conseil

1. **Accès** : après traitement humain de la demande, conserver l’accès jusqu’au terme payé, oui/non ? Dans ce lot, il reste inchangé.
2. **Remboursement** : déclencher un remboursement après décision humaine, oui/non ? Dans ce lot, aucun remboursement, même « manuel » WooCommerce.
3. **Abonnement dont le premier numéro n’est pas parti** : faire partir le délai de la première réception plutôt que du paiement, oui/non ? Dans ce lot, défaut paiement ; une date manuelle permet l’autre décision sans la choisir à votre place.

4. **Borne finale** : doit-elle rester incluse, oui/non ? Défaut inchangé : incluse.
5. **Après effacement C21** : garder la trace anti-doublon dépersonnalisée, oui/non ? Défaut inchangé : conservation date/référence, sans motif ni identité.

## Preuves et limites — état courant du 27 novembre 2026

Commandes exactes, TDD rouge/vert et incidents de harnais conservés : `CORRECTIONS-002-V2.md`. `NOTE.md` sépare désormais les preuves courantes de l’historique.

- `canonique-corrections002-V2.json` : **10 tests, 172 assertions** ; `mutations-corrections002-V2.json` : **15/15 détectées**.
- `image-corrections002-V2.json` : préparation officielle réellement exécutée ; `regression-corrections002-V2.json` : **1151 tests, 36062 assertions**, zéro échec/erreur/ignoré ; **20 outils, 521 contrôles**, zéro échec.
- `recette-corrections002-V2.json` : **57 contrôles HTTP/natifs**, tous verts. Création/modification des réglages et panne SQL du journal par le vrai `options.php`, retour effectif à la préimage relu séparément ; groupe de recette borné à C25 pour préserver les autres lots. Motif à antislash du vrai POST jusqu’à sa métadonnée et au callback enregistré de l’export natif C21. Deux confirmations concurrentes, une seule note ; rollback réel après panne du journal de demande, effacement sans tiers, droits inchangés.
- Préimages privées durables avant sessions/mutations, restauration et readback exacts des profils, options, commandes classiques/HPOS et calendrier/actions métier. Scripts temporaires retirés, aucun mail ni transport extérieur effectif. Les caches techniques ne sont pas assimilés à un droit métier.
- `livraison-corrections002-V2.json` et `PRET` : paquet courant vérifiable par `python -B wp/outils/demo/c25-finaliser.py verifier` ; anciens reçus conservés, jamais rebaptisés.

À Ced : le parcours (étapes, accusé, réglages, liste admin) est-il à sa bonne place et lisible en l’état, oui/non ? L’affichage actuel est conservé. La validation visuelle reste à Ced. Aucune validation juridique du délai ni du cadre légal, aucun accord de déploiement ou d’email. C23/C26 et leurs preuves restent inchangés dans cette correction.
