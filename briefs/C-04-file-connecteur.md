# Lot C-04 — File d'attente du connecteur

**Chantier** : C · code sur mesure. **Nature** : PHP pur et tests, sans WordPress, sans Odoo.
**Emplacement** : `wp/plugins/imagine-connecteur/src/` et `tests/`.
**Livrables** : code, tests, `production/C-04/notes.md`, puis `production/C-04/PRET`.
**Cas d'acceptance concernés** : R-39, R-40, R-41.

## Pourquoi

À chaque événement qui appelle une facture (commande payée, abonnement créé ou renouvelé, remboursement), le site transmet à Odoo le contact et la commande (§2.2). Trois garanties sont exigées (§2.4, §2.5, §4.5) :

- une donnée anormale n'atteint jamais la comptabilité : elle est mise en quarantaine et signalée ;
- si Odoo est indisponible, l'événement attend et il est rejoué ; **rejoué, il ne crée pas de doublon** ;
- tant que l'interface d'Odoo n'existe pas, un export quotidien la remplace.

Les champs attendus par Odoo ne sont pas encore connus (chapitre 8, point 1) et le choix entre un connecteur intégré et n8n n'est pas arrêté (§4.1). Ce lot construit donc le **cœur indépendant de ces deux inconnues** : la file, ses états, ses règles. Il servira dans les deux cas.

## À implémenter

1. **L'événement** : type (commande payée, abonnement créé, abonnement renouvelé, remboursement), identifiant de l'objet d'origine, date, contenu, et une **clé d'idempotence** déterministe, calculée à partir du type et de l'objet d'origine. Deux événements de même clé sont le même événement.
2. **Les états** : en attente, en cours, envoyé, en échec temporaire, en quarantaine. Écris la table des transitions permises ; toute autre transition est refusée.
3. **Le contrôle avant envoi** : une suite de règles, chacune nommée, qui valident le contenu. Livre les règles évidentes d'après le §2.2 (identité présente, adresse complète, montants cohérents entre lignes et total, mode de paiement connu, numéro d'entreprise valide s'il est présent, par le lot C-02 quand il existe). Un échec → quarantaine, avec le nom de la règle et un message lisible par l'administration. Les règles doivent pouvoir être ajoutées sans toucher au moteur.
4. **Le rejeu** : nombre d'essais et attente croissante entre deux essais, configurables. Distingue l'échec temporaire (destination injoignable, délai dépassé : on réessaie) de l'échec définitif (donnée refusée par la destination : quarantaine). Au-delà du nombre d'essais : alerte, et l'événement reste en file.
5. **L'ordre** : les événements d'un même abonnement sont envoyés dans l'ordre où ils sont survenus. Un événement en quarantaine ne bloque pas ceux des autres abonnements ; explique dans `notes.md` ce que tu fais de ceux du même abonnement, et pourquoi.
6. **Les interfaces** : le stockage de la file, la destination (envoi d'un événement), l'horloge et l'alerte sont des interfaces. Livre une mise en œuvre en mémoire pour les tests, et une fausse destination qu'on peut faire tomber, ralentir ou faire refuser à la demande.
7. **L'export quotidien** : une destination qui, au lieu d'appeler Odoo, écrit un fichier par jour avec les événements de la veille. Aucun événement ne manque et aucun n'apparaît deux fois d'un jour à l'autre, même si l'export d'un jour est relancé. Format provisoire : CSV avec une ligne par événement et le contenu en colonnes stables ; le format réel viendra de Step.

## Tests à écrire en priorité

- Le même événement déposé deux fois → une seule entrée.
- Un événement envoyé, puis rejoué par erreur → la destination n'est pas appelée une seconde fois.
- Destination tombée pendant trois essais puis rétablie → l'événement part, une seule fois.
- Destination qui répond après que le délai est dépassé (l'envoi a réussi, mais on ne le sait pas) → au rejeu, pas de doublon. Dis dans `notes.md` ce que cela exige de la destination réelle.
- Événement invalide → quarantaine, les suivants passent.
- Export relancé pour un jour déjà exporté → fichier identique.
- Passage de minuit et changement d'heure (fuseau `Europe/Brussels`).

## Ce que tu ne décides pas

- Les champs exacts attendus par Odoo et le format de l'export : à Step.
- Connecteur intégré ou n8n : à Ced. Dans `notes.md`, dis en une demi-page ce que ton cœur de file change à cette décision, dans un sens et dans l'autre.
- Rien n'est transmis des étiquettes de personnalisation, des préférences ou des réponses au formulaire (§2.2) : aucun champ de ce type dans le contenu d'un événement.

## Exigences

Celles du lot C-01 ; espace de noms `Imagine\Connecteur`. Aucune écriture de fichier en dehors d'un dossier passé en paramètre.
