# Lot C-16 — La commande pour le compte d'un client, et l'encodage sans email

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-10, C-15. **Cahier des charges** : §3.13 (« Commande pour le compte d'un client », « Encodage sans email », « Ventes sans identité »), §2.3. Relis-les.

## Pourquoi

« Une seule porte d'entrée » (§2.3) : un abonnement pris par téléphone, par virement ou sur un salon doit naître dans le site, sinon il n'ouvre aucun droit et n'apparaît pas dans la liste d'envoi. C'est donc le référent administratif qui l'encode, plusieurs fois par jour. Le cahier des charges demande trois écrans au plus.

## Ce qu'on veut

**Le standard d'abord.** WooCommerce sait déjà créer une commande et un abonnement depuis l'administration. Commence par écrire, en dix lignes, ce que le parcours natif fait et combien d'écrans il demande ; ne construis que ce qui manque pour tenir en trois écrans.

Dans l'administration de `imagine-test-demo`, sous le menu Imagine existant (un seul menu), en compte `e-abo` :

1. **Le client** : recherche d'un compte existant (nom, adresse électronique, localité) ou création immédiate. Si la personne n'a pas d'adresse électronique : une case « sans email ». Le site génère alors une adresse technique interne sur un domaine réservé qui ne reçoit rien, marque le compte « sans email », et ne lui envoie rien. Le marquage est celui que lisent déjà C-09 (A-SANSMAIL) et la liste d'envoi : ne crée pas un second marqueur.
2. **La commande** : un abonnement ou un numéro à l'unité parmi les produits fictifs du site, l'adresse de livraison, le mode de paiement parmi ceux qui ont un sens hors ligne (virement, mandat papier).
3. **La confirmation** : récapitulatif, puis création de la commande **native**, en attente de paiement.

Règles :

- La commande créée est une commande native en attente : c'est l'écran des échéances (C-15) qui la fera passer à « payé ». Ce lot ne valide aucun paiement et n'ouvre aucun accès par lui-même ; l'accès reste la décision d'accès (C-06).
- Un seul compte par adresse électronique : si l'adresse saisie existe, on retombe sur le compte existant, on ne crée pas de doublon.
- **Vente sans identité** : un compte générique « vente directe », fictif, proposé en un clic à l'étape 1.
- Droit dédié (celui de C-15 ou un voisin), jeton de sécurité, aucun email sortant, aucun appel extérieur.
- Don, pack, abonnement offert, abonnement groupé : **hors de ce lot**. Leurs règles ne sont pas arrêtées ; laisse des emplacements nommés, pas des parcours inventés.
- Aucune règle nouvelle. S'il en faut une que personne n'a écrite, c'est un réglage au défaut prudent dans l'écran de C-10, et tu le signales.

## Preuve

Proportionnée. Sur le site : un abonnement par virement encodé pour un compte existant, puis pour un compte créé « sans email » ; la commande apparaît dans « virements à valider » de C-15 ; le compte sans email n'apparaît dans aucun envoi par email et son accès reste fermé tant que rien n'est payé ; une adresse déjà connue ne crée pas de second compte ; un compte sans le droit reçoit un refus. Retour à l'état de départ par le reset de C-09 : ce que tu crées pour la preuve est supprimé.

## Livrables

Le code, ses tests, `production/C-16/A-VOIR.md` (en quel compte, quelle adresse, le parcours à suivre), `PRET`. Rapport court dans `files/rapports/`.
