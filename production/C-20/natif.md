## Livraison courante — périmètre réduit du 26 novembre 2026 à 7 h 30, corrections de fusion

**PRET technique réduit**, pas réalisation complète du §3.4 : raccord actif jusqu’au terme payé et écrans sans bouton. `fusion-native-second-V2.json` rejoue la sonde existante : la sortie postale de la seule ligne 89 (8 → 7), terme payé 25/12/2026 avant clôture 05/01/2027, est **attendue** selon C13 ; autres lignes identiques, accès/B02 inchangés, rollback et relecture fraîche. La marge C05 reste absente ; aucune fin native quatre-fois écrite ni essayée, résultat natif non prouvé et non écarté. Produits privés, pas de reprise. Bouton, confirmation et émission de `imagine_non_renouvellement_confirme` reportés au branchement sur staging vérifié avec accord de Ced.

Fusion 1–3 : sept cas locaux de bornes passent par le vrai `Paywall::decisionPdf`, les API natives doublées et l’horloge de requête contrôlée, puis le vrai C06 ; ni Paywall ni C06/C13 modifiés. Trois mutations jetables confirment que les tests détectent absence de fin gardée, perte du minimum Memberships et perte de l’ouverture pending-cancel. Présentation pure : codes seulement ; raccord WordPress : traductions littérales puis échappement HTML éprouvé avec une traduction hostile. README courant aligné, blocage ancien conservé seulement comme historique daté. Préparation d’image puis suite complète réelle : 1 111 tests / 34 499 assertions, sans échec. Recettes natives/UI/HTTP et C08/C13/C09 rejouées, successeurs préservés et C22 revérifié sans réécriture de leurs reçus.

Fusion 4–5, **au branchement seulement** : défaut technique prudent, ordre actuel `arret_a_terme` avant `quatre_fois` conservé ; décider sa priorité pour un quatre-fois natif pending-cancel à ce moment. Hors démo, A-PAPIER dont la méthode native est vide reste inconnu (`EcheancesNatives::methode()` renvoie `''`) et risque la présentation `quatre_fois` ; prévoir un raccord de méthode réelle validé, sans importer le drapeau fictif en production. Aucun changement de cet adaptateur ici.

Les rouges et sceaux historiques ci-dessous restent intacts. Le précédent texte courant est archivé sous `fusion-V2/natif.md.before`. Preuves courantes, limites et commande parent : `A-VOIR.md`.

## Historique — références et constat antérieurs (conclusions de blocage remplacées ci-dessus)

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

## Deuxième passe — 26 novembre 2026 (remplace les conclusions de raccord ci-dessus)

### 1. Memberships confirmé, raccord corrigé

Documentation officielle relue : https://woocommerce.com/document/woocommerce-memberships-subscriptions-integration/ (rubrique « Canceling subscriptions »). L’accès de l’adhésion associée continue pendant l’attente d’annulation ; l’annulation effective le ferme. Le code **installé**, `woocommerce-memberships/src/integrations/subscriptions/class-wc-memberships-integration-subscriptions.php:469–479`, traite `pending-cancel` puis appelle `update_status('pending')` sur l’adhésion. Source conservée dans `native-details-second-V2.json`, pas déduite d’un libellé.

Correction limitée à `imagine-site/Paywall.php` : `pending` + lien natif cohérent + abonnement `pending-cancel` + fin native renseignée se lit actif dans le minimum des bornes natives. C06 n’est pas changé. Les contre-exemples restent fermés : adhésion pending non liée, liée à active, A-VIR lié à son premier paiement pending. Les règles et le raccord C13 restent inchangés : C13 lit déjà les états Subscriptions `active` et `pending-cancel` comme actifs ; il ne fait pas cette confusion Memberships.

### 2. Un autre obstacle est démontré sur A-CARTE : ne pas le masquer

Documentation officielle : https://woocommerce.com/document/subscriptions/statuses/ (attente d’annulation/expiration) ; https://woocommerce.com/document/subscriptions/customers-view/ (actions du compte). L’annulation à terme se borne à la période déjà payée, pas aux quatre numéros projetés par C01.

La sonde réelle et rollbackée conserve maintenant `abonnement_actif`, mais le terme natif calculé vaut **2026-12-25 18:01:50 UTC**. Le prochain numéro papier sort le **15 janvier 2027**, sa liste clôture le **5 janvier 2027 à 00:00 Europe/Brussels**. Sur cette projection future C13, la ligne 89 est réellement retirée (8 lignes → 7). Ce n’est pas une identité d’objets PHP : le contrôle final compare des JSON normalisés et les lignes de la liste. `native-final-blocked-second-V2.json` garde cette réception rouge. Pas de mutation C20 proposée au client, pas de règle postale retouchée pour obtenir du vert. A-CARTE est un profil natif **manuel**, méthode vide ; aucune carte automatique réelle n’a été exercée.

### 3. Quatre fois : prérequis C05 absent, fin native non essayée

Documentation de l’API : https://woocommerce.com/document/subscriptions/develop/functions/ (`get_date`, `update_dates`, dépendances entre dates). Le code installé confirme l’API native ; aucune extension tierce n’est modifiée.

Sur le site courant, `ReglagesAdministration::lire()->margeJours === null`. `Planificateur::planifier()` refuse explicitement `MARGE_OBLIGATOIRE`. B02 nommait déjà ses dates non raccordées pour cette raison. Aucune date de fin C05 du bloc suivant ne peut donc être lue sans choisir une marge inexistante. **La sonde s’arrête sur ce prérequis avant `update_dates(['end'=>...])` : ce n’est pas une preuve d’échec du planificateur natif Subscriptions.** La branche de sonde est disponible si un calendrier C05 valide est fourni, mais non revendiquée exécutée. Rien n’est calculé à la main ni enregistré à défaut. Fallback prudent : aucun bouton quatre-fois, demande à Imagine en une phrase, créances et action native existante conservées. Reprise par retrait de fin non prouvée et non proposée.

### 4. Cause exacte de la reprise refusée

`WC_Subscription::can_be_updated_to('active')`, source installée ligne 337 : le premier verrou est `contains_unavailable_product()` hors administration habilitée. Cette méthode, ligne 446, refuse tout produit non publié. A-CARTE contient le produit **192**, statut **private** ; A-SEPA4 le **193**, également private. Les deux objets sont déjà manuels (`requires_manual_renewal=true`, méthode vide), donc le test natif `is_manual()` permettrait la branche ultérieure pending-cancel : **l’absence de carte n’est pas la cause immédiate du refus constaté**. Aucun produit n’est publié, aucune passerelle/méthode inventée et aucun statut forcé. Aucun cas de reprise native permis n’a été trouvé parmi ces profils.

### Portée des preuves

Les écritures de statut de la sonde restent dans des transactions InnoDB annulées, puis profils et actions sont relus dans un autre processus. La restauration du cas A-CARTE inclut son ancienne date de fin plus longue : ne pas la recréer par simple réactivation refusée. A-PAPIER : action 8793, abonnement 101, pending, date UTC 2026-11-26 02:13:28, inchangés. Les caches/sessions/options de bootstrap peuvent évoluer à la fermeture d’une requête ; pas de promesse d’identité de la base entière entre requêtes.

La confirmation d’une action sûre n’est **pas livrée** : seule la présentation d’un état pending-cancel réel est vérifiée avec date native et valeurs B02 identiques (compteur `restants=null`, nommé non raccordé). Point d’accroche réservé : `Renouvellement::HOOK_CONFIRMATION = imagine_non_renouvellement_confirme`, non émis. Aucun email, paiement externe, remboursement ou rétractation. Conclusion : **livraison partielle, pas PRET**, arrêt point 2 et prérequis manquant point 3.
