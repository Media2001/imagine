# Lot C-07 — Liste d'envoi d'un numéro

**Chantier** : C. **Nature** : PHP pur et tests, sans WordPress.
**Emplacement** : `wp/plugins/imagine-pilotage/src/Envoi/`, `tests/Envoi/`.
**Délai** : une demi-journée.
**Cas d'acceptance concerné** : R-32, et en partie R-08, R-11, R-15, R-20.

## Pourquoi

À chaque parution, l'administration envoie à l'imprimeur-routeur la liste des personnes qui doivent recevoir le numéro. Aujourd'hui elle sort de la base Access. Demain elle sort du site (§3.5, §3.13) : c'est l'un des usages quotidiens que l'équipe d'Imagine jugera en recette. Une erreur se voit tout de suite : un abonné qui ne reçoit pas son magazine, ou un numéro envoyé à quelqu'un qui n'a pas payé.

Ce lot écrit la règle, seule et testée. L'écran du back-office et la lecture des abonnements dans WooCommerce viendront dans un lot de branchement.

## À implémenter

**Entrées**, toutes passées en arguments : le numéro (régulier ou hors-série) ; le calendrier de parution ; la liste des abonnements avec, pour chacun, son état et ses dates, ses numéros dus (moteur C-01), son destinataire et son adresse de livraison ; l'instant de la clôture.

**Sortie** : la liste d'envoi du numéro, une ligne par exemplaire à expédier : destinataire, adresse complète, pays, et l'origine du droit (abonnement, abonnement offert, abonnement groupé).

Règles :

1. **Qui y figure** : tout abonnement dont le numéro fait partie des numéros dus, et qui est en règle à l'instant de la clôture. Le droit au numéro vient de C-01 : ne le recalcule pas.
2. **Abonnement offert** : l'exemplaire va au destinataire, à son adresse, pas à l'acheteur.
3. **Abonnement groupé** : un exemplaire par bénéficiaire attribué, à l'adresse de chacun. Une place non attribuée à la clôture ne produit pas d'exemplaire.
4. **Qui n'y figure pas** : abonnement suspendu pour impayé ; commande par virement ou mandat papier dont le paiement n'est pas validé ; abonnement arrivé à terme ; acheteur d'un numéro à l'unité (son envoi relève de la commande, pas de la liste des abonnés).
5. **Abonné sans adresse électronique** : il y figure comme les autres.
6. **Hors-série** : un par année d'abonnement, selon la règle de C-01.
7. **Le gel** : la liste est établie à l'instant de la clôture et ne change plus. Un abonnement créé, payé ou réactivé après la clôture n'y entre pas ; une adresse modifiée après la clôture n'y est pas reportée. Rejouer le calcul avec le même instant de clôture donne exactement le même résultat.
8. **Les anomalies ne sont pas envoyées en silence** : adresse incomplète, pays manquant, deux exemplaires pour le même destinataire à la même adresse. Elles sortent dans une liste à part, avec le motif, pour que l'administration les traite avant l'envoi.
9. **L'export** : un fichier CSV aux colonnes stables, avec la même protection contre l'injection de formules que l'export du lot C-04. Réutilise ce qui existe.

## Tests à écrire en priorité

- Chaque profil de `docs/recette/profils.md` concerné : A-CARTE, A-SEPA4, A-GRACE, A-SUSP, A-VIR, A-PAPIER, A-EXPIRE, A-NONRENOUV, A-ETRANGER, A-SANSMAIL, P-OFFERT, P-BENEF, P-NUMERO. Tu t'en sers comme jeux de données ; tu ne modifies pas ces fichiers.
- Abonnement payé une seconde avant et une seconde après la clôture.
- Changement d'adresse avant et après la clôture.
- Bénéficiaire d'un groupe remplacé avant et après la clôture.
- Premier et dernier numéro d'un abonnement ; numéro juste avant le premier, juste après le dernier.
- Rejeu : même entrée, même sortie, ligne pour ligne.

## Ce que tu ne décides pas

Applique l'interprétation indiquée, isole-la, et liste-la en question fermée dans `notes.md` :

- **Abonné en délai de grâce à la clôture.** Interprétation : il figure dans la liste (§3.8 : il ne sort de la liste qu'au terme du délai).
- **Deux abonnements pour la même personne à la même adresse.** Interprétation : deux exemplaires, signalés en anomalie.
- **Ordre et colonnes attendus par le routeur.** Non connus : colonnes provisoires, à confirmer par Imagine.

## Exigences

Celles du lot C-01 ; espace de noms `Imagine\Pilotage\Envoi`. Aucune donnée réelle : uniquement des personnes manifestement inventées.
