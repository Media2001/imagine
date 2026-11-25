# Lot C-17 — Les justificatifs du tarif solidaire

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : B-02, C-10, C-11. **Cahier des charges** : §3.13 (« Justificatifs du tarif solidaire »), §4.4 (même titre), §3.7 (« Tarif solidaire : statut, date de fin, dépôt d'un nouveau justificatif »). Relis-les.

## Pourquoi

Le tarif solidaire repose sur un justificatif que l'abonné dépose et que le référent administratif valide. C'est un document personnel : le cahier des charges exige qu'il soit stocké hors du dossier public et **supprimé dès la décision**, le site ne gardant que la catégorie et la date de fin. C'est le genre de promesse qui se prouve par un test.

## Ce qu'on veut

Sur `imagine-test-demo`, deux côtés.

**Côté abonné**, dans « Mon compte » (B-02), à l'emplacement que B-02 a nommé pour les justificatifs : le statut (aucun, en attente, validé jusqu'au…, refusé), le dépôt d'un fichier (image ou PDF, taille plafonnée), et la phrase qui invite à masquer le numéro de registre national.

**Côté administration**, sous le menu Imagine existant, en compte `e-abo` : la file d'attente des justificatifs, et pour chacun, l'ouverture du fichier, puis **valider** (avec une date de fin saisie par le référent) ou **refuser**, en un clic chacun, avec confirmation.

Règles :

- Le fichier est stocké **hors de la racine publique**, servi seulement au titulaire et au référent, par un contrôle de droit à chaque lecture : la même mécanique que le PDF du numéro (C-11). Réemploie-la, ne la refais pas.
- **À la décision, le fichier est supprimé du disque**, validation comme refus. Le site ne conserve que la catégorie, la décision, sa date, la date de fin et le nom de l'opérateur. Un nouveau dépôt remplace le précédent : jamais deux fichiers pour un même compte.
- Le type du fichier est vérifié sur son contenu, pas sur son nom. Aucun fichier exécutable, aucune prévisualisation qui exécuterait quoi que ce soit.
- **Ce lot ne touche ni au prix ni à l'accès.** Ce que la validation ou le refus changent au tarif de l'abonnement, et ce qui se passe à la date de fin, ne sont pas arrêtés par Imagine (question 4 du chapitre 7). L'écran enregistre un statut ; il ne modifie aucun abonnement, aucune commande, aucun droit.
- Les catégories de bénéficiaires ne sont pas arrêtées non plus : c'est une liste en réglage (écran de C-10), livrée avec une seule valeur neutre, « à préciser ».
- Droit dédié, jeton de sécurité, aucun email sortant.
- Que des fichiers fictifs fabriqués pour le test. Aucun vrai document, de personne.

## Preuve

Proportionnée. Les règles de statut en code pur, testées. Sur le site : P-SOL-ATT dépose un fichier fictif, il apparaît dans la file ; l'adresse du fichier, demandée par un anonyme ou par un autre abonné, est refusée ; après validation, **le fichier n'existe plus sur le disque** et le compte affiche « validé jusqu'au… » ; même chose après un refus ; un second dépôt remplace le premier. P-SOL-OK montre l'état validé. Si ces deux profils n'ont pas ce qu'il faut dans le catalogue de C-09, dis-le et ajoute le strict nécessaire au jeu de C-09, sans autre profil. Retour à l'état de départ par le reset de C-09.

## Livrables

Le code, ses tests, `production/C-17/A-VOIR.md` (les deux côtés, en quels comptes), les besoins du designer, `PRET`. Rapport court dans `files/rapports/`.
