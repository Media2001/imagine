# Lot C-29 — La fiche du contact pour Brevo, sans Brevo

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-22 (préférences des newsletters), C-24 (personnalisation), B-06 (coopérateurs), C-06 (décision d'accès). **Cahier des charges** : §3.10 (« les contacts vont du site vers Brevo, avec leur statut — abonné, non-abonné, coopérateur, tarif — tenu à jour par le site » ; étiquettes « uniquement si le lecteur a consenti »), §4.4 (consentements), §2.2 (Odoo ne reçoit aucune étiquette). Relis-les.

## Pourquoi

Le site sera la référence de ce que Brevo sait d'un lecteur. Le jour du branchement, il faudra pouvoir dire, compte par compte, ce qui part et ce qui ne part pas. Aujourd'hui rien ne part, et le compte Brevo n'est pas ouvert aux agents : on construit la fiche, et un écran qui la montre.

**Ce lot calcule et affiche. Il ne transmet rien.**

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : ce que l'extension officielle de Brevo pour WordPress et WooCommerce synchroniserait d'elle-même, et pourquoi on ne l'active pas ici (pas de compte, et le statut vient de règles du site).

- **Une seule fonction, en code pur** : pour un compte, sa fiche. Elle contient le statut d'abonné (abonné, non-abonné), l'attribut coopérateur (oui, non), le tarif, les newsletters choisies, et les étiquettes de personnalisation.
- **Qui a une fiche** : un compte qui a choisi lui-même au moins une newsletter et qui peut recevoir un email. Pas de choix, compte sans email : pas de fiche, rien ne partirait. Un compte qui s'est désinscrit de tout a une fiche réduite à « à retirer ».
- **Les étiquettes** viennent de `Personnalisation::attributsConnecteur`, telle quelle : tu ne refais pas la règle du consentement distinct.
- **Le statut** suit une seule règle, déjà écrite : « abonné » veut dire abonnement à l'état actif, comme dans le rapprochement d'A-14. Pour le bénéficiaire d'un abonnement offert ou groupé, la question est chez Imagine : la fiche dit « inconnu ».
- **Le tarif** est lu sur l'abonnement actif, dans une liste fermée en réglage ; une valeur hors liste donne « inconnu », jamais une valeur devinée. La grille n'est pas arrêtée : sur la démonstration, les tarifs fictifs des profils.
- **Un écran de l'administration, en lecture seule** : « Ce qui partirait vers Brevo ». Pour un compte choisi, sa fiche ou la raison de son absence ; et le nombre de fiches par statut. Même droit que le tableau de bord de C-19.
- Les noms des attributs sont les clés internes du site ; la correspondance avec les noms de Brevo viendra au branchement.

Ce que le lot ne fait pas : aucun appel, aucune clé, aucune file, aucune tâche planifiée, aucun écouteur qui envoie ; rien n'est enregistré (la fiche se calcule à la demande). Odoo n'est pas concerné.

## Preuve

Proportionnée. Sur les profils de C-09 : un tableau attendu, profil par profil, avec au moins un abonné actif avec choix, un non-abonné avec choix, un compte sans choix (pas de fiche), un compte sans email (pas de fiche), un coopérateur. Les étiquettes sont absentes sans consentement distinct (un contrôle qui les trouve d'abord avec le consentement, puis constate leur absence ; une mutation témoin). Aucune option ni métadonnée écrite par l'écran ; zéro requête sortante. Profils rendus dans leur état de départ.

## Livrables

Le code, ses tests, la section du README, `production/C-29/A-VOIR.md`, `PRET`. Rapport court, avec ce que tu as dû laisser à « inconnu ».
