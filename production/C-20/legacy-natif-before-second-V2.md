1. Subscriptions distingue l’annulation en fin de période prépayée (`pending-cancel`) de l’annulation effective (`cancelled`) ; documentation officielle : https://woocommerce.com/document/subscriptions/statuses/.
2. Une annulation demandée par le client conserve normalement la période déjà payée, pas un engagement de quatre numéros : même documentation.
3. À son terme l’abonnement devient `cancelled` ; une réactivation n’est alors plus disponible : même documentation.
4. Avant ce terme, le compte client propose la réactivation ; documentation officielle : https://woocommerce.com/document/subscriptions/customers-view/.
5. Le basculeur automatique/manuel est désactivé par défaut et doit être activé dans les réglages : https://woocommerce.com/document/subscriptions/renewal-process/auto-renewal-toggle/.
6. Ce basculeur change le mode d’encaissement, il n’annonce pas une fin d’engagement ; il ne constitue donc pas à lui seul « Ne pas renouveler » : même documentation (conclusion technique).
7. Revenir en automatique sans moyen de paiement exige d’en ajouter un ; aucune carte ni aucun mandat ne sera fabriqué ici : même documentation et profils natifs relus.
8. Runtime installé : `WC_Subscription::update_status`, `includes/core/class-wc-subscription.php:480`, branche `pending-cancel`, efface `next_payment` et fixe `end` à `end_of_prepaid_term` (source dans `native-source-V2.json`).
9. Runtime installé : `calculate_date`, même fichier ligne 1670, choisit la prochaine date de paiement future comme terme prépayé ; le passage à `active` restaure les dates pré-annulation et la prochaine échéance (même preuve).
10. Conclusion à vérifier par essai natif avant toute interface : ce mécanisme ne garantit pas le bloc de quatre numéros et supprime son échéance suivante ; C-06/C-13 restent inchangés, aucun filtre de dates ni ordonnanceur de substitution ne sera ajouté.
