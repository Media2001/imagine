# Lot C-20 — « Ne pas renouveler », deuxième passe

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Suite de** : `briefs/C-20-ne-pas-renouveler.md`, qui reste valable pour tout ce que cette page ne change pas. **Cahier des charges** : §3.4 (« L'abonné désactive le renouvellement depuis son compte. L'abonnement va alors à son terme »), §3.7. **Arbitrage** : `docs/arbitrages-2026-11-26.md`, passage de 4 h.

## Pourquoi

Tu t'es arrêté au bon endroit, et ta sonde a montré deux choses différentes. L'accès qui se ferme tout de suite n'est pas le fait de Subscriptions : c'est notre raccord qui lit mal un état de Memberships. L'échéance du quatre-fois qui disparaît, elle, est bien le fait du standard : l'annulation en fin de période n'est pas le bon outil pour un bloc de quatre numéros.

## Ce qu'on veut

**1. Le raccord.** Dans `imagine-site/Paywall.php`, l'état `pending` de Memberships est lu « virement non validé ». Or c'est l'état « en attente d'annulation » que Memberships pose quand l'abonnement lié passe en `pending-cancel`. Vérifie-le d'abord dans le code installé et dans la documentation officielle, et écris-le dans `natif.md`. Si c'est confirmé : une adhésion `pending` liée à un abonnement `pending-cancel` se lit **actif jusqu'à la date de fin** ; tous les autres cas gardent leur lecture actuelle (une adhésion `pending` sans abonnement lié, ou liée à un abonnement en attente de premier paiement, reste « virement non validé »). Même correction dans le raccord natif de la liste d'envoi (C-13) s'il porte la même confusion. **L'interdiction du premier brief est levée pour ces raccords seulement** : la bibliothèque C-06 (`imagine-pilotage`) et les règles pures de C-13 ne changent pas.

**2. Abonnement payé en une fois, renouvellement automatique.** L'annulation en fin de période du standard, telle quelle. L'écran et la confirmation restent ceux du premier brief.

**3. Paiement en quatre fois.** Pas d'annulation en fin de période. « Ne pas renouveler » pose la **date de fin native de l'abonnement à la fin du bloc en cours** (la date à laquelle le bloc suivant aurait commencé, lue dans l'échéancier de C-05, pas calculée à la main). L'abonnement reste actif, Subscriptions garde lui-même les échéances du bloc et fait expirer l'abonnement à cette date. « Reprendre le renouvellement » retire la date de fin. Aucun ordonnanceur à nous, aucune autre date touchée. **Prouve-le d'abord par ta sonde avec retour arrière** : les échéances restantes du bloc sont toujours planifiées, aucune ne l'est après la date de fin, l'accès et la liste d'envoi ne bougent pas. Si le standard ne tient pas cela, ne contourne pas : le quatre-fois n'a pas de bouton, l'écran dit en une phrase que la demande se fait auprès d'Imagine, et tu le dis dans ton rapport.

**4. La reprise.** Le standard l'a refusée sur tes profils. Lis pourquoi dans le code installé (moyen de paiement vide, renouvellement manuel, autre) et écris-le. Si le standard la permet dans un cas, montre-la dans ce cas ; sinon l'écran ne propose pas un bouton qui échouerait. On ne force pas un changement d'état refusé par le standard, et on ne fabrique ni passerelle ni moyen de paiement.

## Preuve

Proportionnée, sur `imagine-test-demo`. A-CARTE : après « Ne pas renouveler », la décision d'accès reste « abonnement actif » et la liste d'envoi du prochain numéro est la même ; A-VIR reste fermé (test) ; A-SEPA4 selon le point 3 ; A-VIR et A-PAPIER sans bouton ; un abonné ne peut pas agir sur l'abonnement d'un autre. Les tests de C-08 et de C-13 restent verts. Les profils sont remis dans leur état de départ, action planifiée comprise, et relus (C-09 : 382 sur 382).

## Livrables

Le code, ses tests, `production/C-20/natif.md` complété, `A-VOIR.md`, `PRET`. Rapport court. Si tu t'arrêtes de nouveau, dis sur quel point des quatre et livre les autres.
