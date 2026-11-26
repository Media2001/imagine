# Lot A-27 — Les moyens de paiement enregistrés, comptés

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-19, A-20, A-22 (le gardien des sorties). **Cahier des charges** : §4.3 (« Abonnés en ligne actuels : comptes, abonnements, moyens de paiement et historique repris du site actuel »), §3.6 (renouvellements par PayPal, et Bancontact vers SEPA).

## Pourquoi

Le cahier des charges promet que les abonnés en ligne gardent leur moyen de paiement. Ce moyen ne vit pas sur le site : le site n'en garde qu'une référence, chez Stripe ou PayPal. Selon la façon dont cette référence a été créée, le renouvellement automatique survivra à la bascule ou non. C'est un des points durs de l'étude (renouvellements PayPal, Bancontact vers SEPA), et il se décide sur des nombres : combien d'abonnés vivants par passerelle et par type de référence. A-19 a compté les renouvellements automatiques **sans** moyen ; ce lot compte ceux qui en ont un, et lequel.

**Ce lot n'appelle aucune passerelle, ne teste aucun paiement et ne dit pas ce qui survivra : il compte.**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné et le gardien des sorties d'A-22.

**Le standard d'abord.** Dix lignes dans le mode d'emploi : où WooCommerce range les moyens de paiement enregistrés (table des jetons, métadonnées de l'abonnement, classique et HPOS), et ce que Subscriptions lit au moment d'un renouvellement automatique, d'après la documentation officielle et le code installé.

Puis des **comptes seulement**, pour les abonnements vivants (les mêmes états qu'A-20) :

- par passerelle et par **type de référence** (liste fermée de types natifs : carte, mandat SEPA, accord PayPal, autre, illisible) : nombre d'abonnements en renouvellement automatique ;
- parmi les cartes, combien ont une date d'expiration passée, et combien expirent dans les six mois suivant la date de l'audit ;
- nombre d'abonnements dont la référence de paiement n'est rattachée à aucun jeton du compte, et nombre de jetons de comptes sans abonnement vivant ;
- nombre de comptes qui portent plus d'un moyen enregistré.

Les groupes de moins de cinq sont fondus, comme A-20. **Aucun jeton, aucune référence de client ou de mandat, aucun chiffre de carte, aucune date d'expiration individuelle, aucun identifiant de compte ou d'abonnement** ne sort : des nombres, des identifiants de passerelle et des types d'une liste fermée. Ce qu'on ne sait pas lire est « illisible », jamais « absent » (règle d'A-19).

L'import neutralise les passerelles et peut purger ces références. Regarde ce qu'il en fait, **sans le modifier** : pour chaque nombre que l'import fausse, la réponse sur une copie neutralisée est « inconnu après neutralisation », jamais zéro. S'il n'en reste aucun d'utile, dis-le : c'est un résultat, et c'est à Ced de dire comment le compte se fera.

## Preuve

Sur le banc fictif, classique et HPOS : un abonnement par carte valide, un par carte expirée, un par mandat SEPA, un par accord PayPal, un dont la référence ne correspond à aucun jeton, une référence canari. Les nombres sont exacts, le canari est absent de toutes les sorties sur chaque canal et dans les fichiers de rapport, rien n'est écrit, aucun appel sortant. Le cas neutralisé répond « inconnu » là où il le doit. **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252). Le parcours du mode d'emploi, copié tel quel, fonctionne.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-27/PRET`. Rapport court.
