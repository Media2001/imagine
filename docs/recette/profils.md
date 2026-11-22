# Profils de test

Comptes fictifs, créés par script sur le staging. Noms manifestement inventés, adresses en `@example.org`. Les dates sont relatives à la date du test et au calendrier de parution fictif.

## Visiteurs

| Code | Profil | État de départ |
|---|---|---|
| V-ANON | Anonyme | Aucun compte, aucune session |
| V-ROBOT | Robot d'indexation vérifié | Agent utilisateur d'un robot reconnu **et** adresse IP qui passe la vérification |
| V-FAUX | Faux robot | Agent utilisateur d'un robot reconnu, adresse IP quelconque |
| V-DEC | Découverte en cours | Compte vérifié, accès découverte ouvert et non épuisé |
| V-DEC-FIN | Découverte consommée | Compte vérifié, accès découverte épuisé, aucun abonnement |
| V-INSCRIT | Compte sans droit | Compte vérifié, jamais abonné, découverte non ouverte |

## Abonnés

| Code | Profil | État de départ |
|---|---|---|
| A-CARTE | Abonné, une fois, carte | Actif, tarif normal, renouvellement activé, 3 numéros restants |
| A-SEPA4 | Abonné, quatre fois, domiciliation en ligne | Actif, 2 échéances payées sur 4, prochaine échéance planifiée |
| A-PAYPAL | Abonné, une fois, PayPal | Actif, accord de facturation en place |
| A-VIR | Abonné par virement, en attente | Commande créée par l'administration, paiement non validé, accès fermé |
| A-PAPIER | Abonné sur mandat papier | Actif, mode « domiciliation bancaire », échéance à lancer ce mois-ci |
| A-GRACE | Abonné en délai de grâce | Dernier prélèvement rejeté il y a moins que la durée du délai |
| A-SUSP | Abonné suspendu | Délai de grâce écoulé, accès fermé, sorti de la liste d'envoi |
| A-EXPIRE | Ancien abonné | Abonnement arrivé à terme sans renouvellement |
| A-NONRENOUV | Abonné qui a désactivé le renouvellement | Actif jusqu'au terme, 1 numéro restant |
| A-ETRANGER | Abonné livré hors de Belgique | Actif, supplément de port appliqué |
| A-SANSMAIL | Abonné sans adresse électronique | Créé par l'administration, adresse technique interne. Exclu des envois **par email** ; il reçoit le magazine et figure dans la liste d'envoi postale |
| A-ECHEANCE | Abonné à 30 jours de son échéance annuelle | Actif, renouvellement activé, rappel de reconduction pas encore envoyé |

## Cas particuliers

| Code | Profil | État de départ |
|---|---|---|
| P-OFFRANT | Acheteur d'un abonnement offert | A offert un abonnement, avec renouvellement à sa charge |
| P-OFFERT | Destinataire d'un abonnement offert | Compte rattaché à l'abonnement offert, jamais prélevé |
| P-GEST | Gestionnaire d'un abonnement groupé | Lot de 5 abonnements, 3 attribués, 2 libres |
| P-BENEF | Bénéficiaire d'un abonnement groupé | Compte propre, droits d'abonné, jamais prélevé |
| P-PRO | Professionnel | Compte avec numéro d'entreprise belge valide |
| P-SOL-ATT | Tarif solidaire, justificatif en attente | Accès ouvert, justificatif déposé, non traité |
| P-SOL-OK | Tarif solidaire validé | Statut validé, date de fin dans 45 jours |
| P-NUMERO | Acheteur d'un numéro à l'unité | A acheté le numéro N, compte créé après l'achat, aucun abonnement |
| P-COOP | Coopérateur non abonné | Attribut coopérateur posé, aucun abonnement |

## Équipe

| Code | Profil | Droits |
|---|---|---|
| E-ADMIN | Administrateur technique | Tous |
| E-REDAC | Rédaction | Contenus, calendrier de parution |
| E-ABO | Référent administratif | Commandes pour compte de client, écran des échéances, justificatifs, liste d'envoi, extractions |

## Données communes

- **Calendrier de parution fictif** : numéros trimestriels et un hors-série d'été, sur trois ans, avec date de sortie et date de clôture de la liste d'envoi.
- **Contenus** : au moins deux numéros, chacun avec un article réservé, un article ouvert et un PDF.
- **Grille tarifaire fictive** : trois tarifs, en une et en quatre fois, tant qu'Imagine n'a pas arrêté la sienne (décision 3).
