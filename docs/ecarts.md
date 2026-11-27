# Registre des écarts

Toute demande hors cahier des charges, toute contradiction interne au cahier des charges, tout blocage dû à un tiers. Une ligne par écart, datée. Tenu par Claude à partir des rapports.

| Date | Origine | Écart | Effet | Suite |
|---|---|---|---|---|
| 11/11/2026 | Cahier des charges §3.4 | Le numéro d'entreprise doit « afficher la dénomination trouvée », alors que la décision d'octobre prévoyait un simple contrôle de format. | Une recherche en ligne à développer. | À trancher (`decisions.md`, point 8). |
| 11/11/2026 | Cahier des charges §5 | « Dépôt de code chez UPARTNER, aucune dépendance à un compte personnel », alors que le dépôt est chez Media2001. | Copie ou transfert à prévoir à la réception. | Dépôt maintenu chez Media2001 (Ced, 11/11). |
| 11/11/2026 | Imagine | Décisions 3, 4 et 5 du chapitre 7 ouvertes à la date de démarrage de la production. | Tunnel et emails non finalisables. | En attente d'Imagine. |
| 11/11/2026 | Cahier des charges §4.3 | Le cahier des charges décrit une migration des abonnés en ligne vers un nouveau site. Décision : on repart de la production et on la met à niveau. | Moins de migration, mais une mise à jour de l'existant à sécuriser et à rejouer à la bascule. | Tranché (`decisions.md`). À faire savoir au pilote du projet. |
| 20/11/2026 | Étude A-00, besoin 3 · brief vs §3.6 | Le brief de l'étude supposait un prélèvement SEPA après une première carte. Le cahier des charges ne prévoit le passage au SEPA que pour Bancontact ; la carte se renouvelle par carte. | Parcours et mandat différents selon la réponse. | Ouvert : question A de `corrections/A-00.md`, pour le pilote du projet. |
| 20/11/2026 | Étude A-00, besoin 7 · §3.8 | Le cahier des charges demande que les emails de Stripe soient désactivés. Avec l'identifiant créancier de Stripe, la prénotification SEPA envoyée par Stripe est obligatoire. | « Aucun email de Stripe » ne peut pas être promis en l'état. | Ouvert : question 4 de l'étude, pour Imagine. |
| 20/11/2026 | Étude A-00, besoin 2 · §3.5 | La synchronisation native de Subscriptions ne garantit pas des dates d'échéance communes à tous les abonnés, calées sur les trimestres civils. | Un raccord sur mesure est nécessaire pour le paiement en quatre fois. | Acté. Mécanisme à soumettre (arbitrage du 21/11). |
| 20/11/2026 | Lot C-04 | Les cas de recette R-39, R-40 et R-41 ne sont couverts qu'au niveau du cœur de file. Le parcours complet est dû au lot de branchement. | La recette du connecteur ne peut pas être prononcée sur C-04 seul. | À reprendre au lot de branchement. |
| 20/11/2026 | Lot C-04 | Les messages destinés à l'administration ne passent pas encore par les fonctions de traduction (code hors WordPress). | À ré-emballer au branchement. | À reprendre au lot de branchement. |
| 20/11/2026 | Lot C-04 · Step | Le champ `payment_reference` de l'événement n'est pas confirmé par Step. | Format de l'événement provisoire. | À poser à Step avec les champs attendus par Odoo. |
| 22/11/2026 | Relecture C-07 | `docs/recette/profils.md` disait A-SANSMAIL « exclu des envois », ce qui contredisait la règle 5 du brief C-07 (il figure dans la liste postale). | Ambiguïté de rédaction, sans effet sur le code. | Corrigé le 22/11 : exclu des envois par email seulement. |
| 22/11/2026 | Lot C-05 | Le brief C-05 et l'arbitrage du 21/11 demandaient « jamais cinq » paiements par année de date à date, ce qui est incompatible avec des échéances communes à tous les abonnés. | Règle impossible à tenir pour une commande passée entre la date commune et la clôture. | Tranché le 22/11 : quatre échéances par bloc de quatre numéros ; une fenêtre de date à date peut en contenir cinq. |

## 23 novembre 2026 — voie 2

- L'extension `imagine-site` réunit le modèle de contenu provisoire (B-00) et le branchement du paywall (C-08) : B-00 ne se relit plus isolément. Accepté pour la démonstration ; à séparer quand le vrai modèle éditorial sera défini.
- Modèle de contenu de la démonstration (numéro, rattachement des articles) : provisoire, sans ACF, à remplacer après l'audit de l'existant.

## 24 novembre 2026 — ce que montre l'archive de production (diagnostic, sans données)

- L'archive est celle de `kiosque.imagine-magazine.com` : 49 756 fichiers, médias de 2020 à 2026.
- Extensions présentes (dossiers) : woocommerce, woocommerce-subscriptions, woocommerce-memberships, woocommerce-subscription-downloads, woocommerce-gateway-stripe, woocommerce-product-addons, flexible-checkout-fields, woo-order-export-lite, advanced-custom-fields-pro, custom-post-type-ui, wp-all-import-pro, wpai-acf-add-on, wp-all-export, wordpress-seo (Yoast, pas Rank Math), matomo, wordfence, fluent-smtp, simple-file-list, loco-translate, user-switching, regenerate-thumbnails, worker (ManageWP).
- Thèmes : imaginev2 (sur mesure, une cinquantaine de fichiers PHP), storefront, twentytwentyfive.
- Seule passerelle de paiement visible : Stripe. Pas de Teams, pas d'Event Tickets.
- Des exports et journaux dans `uploads/` (wpallexport, memberships_csv_exports, wc-logs…) : à exclure du staging, et à signaler à Imagine (fichiers d'abonnés stockés dans un dossier de médias).
- Confirmé par Ced le 24/11 : il n'y a **qu'un seul site**, `kiosque.imagine-magazine.com` (éditorial, abonnements et boutique). Cette archive est donc tout l'existant.
- Diagnostic du 25/11 : 16,9 Go de contenu, base de 474 Mo. Des tables `ahm_*` (WordPress Download Manager, extension désinstallée, tables restées), `matomo_*` depuis 2015, `fsmpt_email_logs` (journal des emails envoyés). À nettoyer au chantier A-05 et à signaler à Imagine.

## 25 novembre 2026 — lots C-13, C-14, B-02

- **C-13 · §3.13 contre le brief.** §3.13 dit qu'un compte « sans email » est « exclu de tous les envois » ; le brief dit qu'il figure dans la liste d'envoi postale. Résolu par le brief : exclu des envois par email seulement (même lecture que le 22/11). Sur la démonstration, A-SANSMAIL est exclu pour une autre raison : pas de paiement validé.
- **C-13 · abonnements offerts et groupés.** Le raccord est livré et testé sur des liens fictifs ; les profils de C-09 n'ont pas ces liens. Limite des données de démonstration, plus du code. Le modèle des groupes (Teams ou liens de Memberships) reste à confirmer par Imagine : réglage fermé par défaut.
- **C-13 · actif n'est pas expédié.** Un abonnement actif dans l'administration sans paiement validé n'entre pas dans la liste d'envoi. Règle maintenue ; les profils reçoivent des paiements fictifs déclarés (`briefs/C-09-complement-paiements-fictifs.md`).
- **C-14 · référence du brief.** Le brief citait §3.11 (événements) ; les dispositions applicables à l'achat d'un numéro sont §3.7 (achat sans compte) et §3.9 (articles et PDF du numéro acquis, sans limite de durée). Erreur de brief, sans effet sur le code corrigé.
- **C-14 · achat sans compte.** §3.7 prévoit l'achat papier sans compte, puis la création d'un compte ; le rattachement numérique après coup n'est pas décrit. Fermé par défaut, question pour Imagine (`decisions.md`).
- **B-02 · référence du brief.** Le brief citait §3.10, qui traite des newsletters. Le cahier des charges ne détaille pas l'espace « Mon compte » au-delà de §3.7 : le minimum de cinq rubriques du brief fait foi, à confronter aux maquettes.
- **B-02 · profil inexistant.** Le brief nommait `a-4x-j45` ; le profil « quatre fois » du catalogue est A-SEPA4. Erreur de brief.
- **Diagnostic de l'archive (rappel pour A-05).** Le nettoyage du site réel se décidera sur un plan rempli par Ced après l'audit du staging ; l'outil ne retire rien d'office.


## 26 novembre 2026 — lots C-17, C-20, A-11

- **C-17 · brief contre §4.4.** Le brief faisait conserver cinq champs après la décision sur un justificatif (catégorie, décision, date de la décision, date de fin, opérateur) ; §4.4 dit « le site ne conserve que la catégorie et la date de fin ». Erreur de brief. Résolu par le cahier des charges : le dossier de l'abonné garde la catégorie, la date de fin et l'état (nécessaire au « statut » de §3.7) ; la date de la décision et l'opérateur vont au journal de l'administration. À défaire si Ced préfère (`docs/arbitrages-2026-11-26.md`).
- **C-20 · le standard et le bloc de quatre numéros.** L'annulation en fin de période de Subscriptions arrête l'abonnement à la prochaine échéance et retire celle-ci. Pour un paiement en quatre fois, cela couperait le bloc en cours, contre la décision du 22/11. Piste retenue : la date de fin native de l'abonnement, posée à la fin du bloc ; à prouver. Si le standard ne le permet pas, le non-renouvellement en ligne d'un abonnement en quatre fois demandera un développement, à signaler à Imagine.
- **C-20 · raccord de démonstration.** Le raccord du paywall lisait l'état « en attente d'annulation » de Memberships comme un virement non validé. Sans effet jusqu'ici (aucun profil n'était dans cet état) ; corrigé avec la deuxième passe de C-20.
- **A-11 · site réel.** Les outils d'inventaire refusent un site qui porte un cache ou un pare-feu en fichier de remplacement, ce que la production a (Wordfence). L'inventaire réel se fera sur la copie de staging, ces fichiers écartés par l'opérateur ; à prévoir dans la marche à suivre de la bascule.
- **C-19 · §3.13 contre le brief.** §3.13 demande les abonnés actifs « par mode de paiement » et « par moyen de paiement » ; le brief n'avait gardé qu'un axe. Ligne « Par moyen de paiement » affichée grisée, sans chiffre ; la distinction est une question pour Imagine (`decisions.md`).
- **C-19 · « droit dédié ».** Le brief parlait d'un droit dédié ; l'écran s'ouvre à qui a déjà les extractions et les échéances. Laissé tel quel (le plus fermé) ; question pour Imagine.
- **C-20 · §3.4 pas encore tenu.** « L'abonné désactive le renouvellement depuis son compte » : sur la démonstration, aucun abonnement n'est en renouvellement automatique (pas de passerelle), le bouton n'y a donc pas de profil honnête. Livré : le raccord corrigé et des écrans sans bouton. Le bouton, et la date de fin native pour le quatre-fois (ni prouvée ni écartée : la marge de l'échéancier n'a pas de valeur), passent au branchement sur le staging vérifié.
- **C-20 · critère du brief.** Le brief exigeait une liste d'envoi inchangée après « ne pas renouveler » ; faux quand la période payée finit avant la clôture du prochain numéro. Erreur de brief ; les règles de C-13 ne changent pas.
- **A-17 · le brief contre l'import.** Le brief écrivait que les nombres restent justes sur une copie anonymisée ; l'import retire les mots de passe d'application, leur compte serait donc zéro. L'outil répondra « inconnu après neutralisation ». L'import n'est pas modifié. Sur le site réel, ce nombre ne peut être lu que par Ced sur la source.
- **A-11 à A-17 · nom d'un lien symbolique.** Le refus d'un site portant un lien symbolique en recopiait le chemin, qui vient du contenu du site et peut porter un nom. Corrigé au point commun : le refus ne nomme plus que des fichiers d'une liste fermée.


## 26 novembre 2026, 10 h — lots A-16, A-18, A-19, C-21

- **A-16 · le brief contre la règle du chemin de refus.** Le brief demandait qu'une correspondance désignant une clé absente soit refusée « en la nommant » ; la règle posée à 7 h ne laisse sortir qu'un code et des noms d'une liste fermée. Résolu : le refus nomme le champ de la correspondance (liste fermée de quatre noms), pas la valeur saisie par l'opérateur.
- **A-18 · contradiction interne du brief.** Le brief demandait un oui ou non sur l'interdiction de lecture par une règle du serveur, tout en interdisant d'ouvrir le moindre fichier. Indémontrable ainsi. L'outil dit si un fichier de règles est présent et répond « inconnu » sur l'interdiction effective. Sur le site réel, la protection du dossier des médias se vérifiera autrement (une requête depuis l'extérieur, par Ced ou avec l'hébergeur).
- **A-18 · « stockage classique et HPOS ».** Le brief voulait les deux magasins de commandes ; la première livraison ne lisait que le magasin actif. Corrigé par la fusion : un reste dans le magasin inactif est une donnée conservée.
- **A-19 · le mode d'emploi contre le lanceur.** La commande écrite dans le mode d'emploi était refusée par le lanceur (date exigée, dite facultative). Règle ajoutée : un test lance la commande du mode d'emploi telle qu'elle est écrite.
- **C-21 · « l'export ne divulgue jamais un tiers ».** La première livraison le contredisait sur trois chemins (export de l'opérateur d'une commande, effacement du payeur d'un cadeau, retrait d'un membre d'un groupe), sous une suite verte. Corrigé ; vérification attendue. Rappel de méthode : une suite verte ne prouve que les chemins que ses jeux d'essai traversent.
- **Outils de la voie 1 · rejeu par les relecteurs.** La commande de rejeu autorisée ne joue aucun test des outils d'inventaire ; les relecteurs contrôlent les reçus sans rejouer. Lot T-02 ouvert pour les tests purs ; les matrices natives resteront hors de portée des relecteurs.
- **Outils de la voie 1 · « aucune sortie ne recopie un nom ou un chemin du site ».** Les briefs l'exigent depuis A-17 ; le lanceur commun laissait PHP hériter des deux flux, si bien qu'une extension du site pouvait écrire à l'opérateur hors du tampon (écriture directe, arrêt pendant le chargement, fonction de fin de processus). Trouvé par une relecture sur deux, sur A-20 et A-21 ; les bancs ne posaient qu'un canari affiché. Corrigé par un gardien commun (A-20, A-21), étendu aux outils clos par A-22. Rappel de méthode : un canari se pose sur chaque canal, pas sur le plus commode.


## 26 novembre 2026, 16 h — lots C-23, A-22

- **C-23 · ce que le test d'étanchéité ne prouve pas sur la démonstration.** §4.4 demande que le cache de pages distingue connectés et anonymes, et que les robots soient vérifiés par résolution inverse. Ni l'un ni l'autre ne se démontre sur le site fictif (pas de cache d'hébergement, aucun appel extérieur). Le test couvre les faux robots et les faux en-têtes ; le reste se prouvera chez l'hébergeur, qui n'est pas choisi.
- **C-23 · plans de site.** Ils sont fermés sur la démonstration : le test vérifie leur fermeture, pas leur contenu. À reprendre quand le référenceur les fera ouvrir.
- **A-22 · le brief sous-estimait le périmètre.** Le brief citait A-12 et A-15 à A-19 « au moins » ; l'inventaire d'Hermès ajoute A-03, A-11 et A-14, qui chargent aussi le WordPress du site. A-02 et A-10 n'en chargent rien.


## 26 novembre 2026, 19 h — lots A-22, A-24, C-23

- **A-22 · le brief ne visait que les flux.** Ses quatre canaris écrivaient sur les sorties du processus ; aucun n'altérait un fichier de rapport avant sa publication. La fusion l'a vu. Le canari par canal compte désormais un cinquième canal, le fichier.
- **A-24 · les adresses ne se lisent pas sur une copie neutralisée.** L'import efface les champs d'adresse sauf le pays : restent les effectifs et la répartition par pays ; le reste vaut « inconnu après neutralisation ». L'état réel des adresses de livraison (§3.13) ne peut se lire que sur la source, hors agents : décision de Ced.
- **C-23 · le public « découverte épuisée » n'existe pas sur l'état livré.** La découverte est livrée fermée (défaut de C-12, question 5 ouverte chez Imagine). Le test de livraison contrôle alors ce personnage comme un compte sans droit ; le cas « épuisé » se prouve dans une recette à part, réglage remis ensuite. À revoir quand l'accès découverte sera arrêté.


## 26 novembre 2026, 22 h — lots A-25, A-22, C-23, B-07, C-24

- **A-25 · l'import et les messages de formulaires.** Avec la décision `garder` posée sur une table de messages, les messages restent en clair après neutralisation et anonymisation (prouvé sur le banc). Le parcours de Ced vide par défaut les tables hors catalogue ; le sort des messages rangés comme des contenus n'est pas prouvé. Contraire à l'esprit du §3 de la doctrine. Lot A-28 ouvert ; d'ici là, pas de `garder` sur une table de formulaires.
- **A-22 · un paquet de preuves ne se rejoue que sur le NUC.** Les journaux des paquets (`*.log`) ne sont pas versionnés : depuis une copie du dépôt, le vérificateur de paquet refuse (fichier absent). Les relecteurs du NUC, eux, ne peuvent pas lancer une commande avec argument. Le rejeu indépendant du vérificateur d'A-22 attend donc Ced.
- **C-23 · une fonction entrée par un tour de correction.** La couverture des pages coopérateurs a été ajoutée au test pendant les corrections, hors des six instructions et sans les deux relectures de la doctrine §6. Gardée, non comptée comme prouvée ; relue avec C-26. Règle rappelée dans la file.
- **B-07 · inscription ouverte sans garde.** Un visiteur anonyme peut créer une inscription par adresse et par événement, sans limite. Le brief demandait une inscription simple, sur un site fictif : rien n'est ajouté. À reprendre avant toute ouverture au public.
- **C-24 · « inscrit à au moins une newsletter » (§3.10).** Le cahier des charges ne dit pas si une inscription créée d'office compte. Défaut prudent : non. Question rangée pour Imagine.
- **Voie 2 · PSR-12 (doctrine §5).** Le code d'`imagine-site` et du thème condense des instructions sur une ligne. Dette acceptée jusqu'au gel du code, pour ne pas périmer les reçus des lots code clos ; un seul passage mécanique alors.


## 27 novembre 2026, 1 h — lots A-28, A-27, A-26, A-29, A-22, C-25, B-08

- **A-28 · les contenus d'un type inconnu restent dans la copie.** L'import vide désormais les messages de formulaires d'une liste fermée (six tables, deux types de contenu). Un message qu'une autre extension rangerait comme un contenu d'un type inconnu de l'outil reste tel quel, comme les contenus du magazine. La copie n'est donc pas prouvée vide de tout texte libre de visiteur. Question posée à Ced (`ETAT.md`) ; rien n'est supprimé d'ici là.
- **A-28 · un changement de l'import périme les paquets de sept lots.** Les preuves d'A-21 à A-27 gèlent l'empreinte de l'import. Une seule requalification après la fusion d'A-28 ; l'import est gelé ensuite. Un lot clos ne se rouvre pas pour une dépendance changée, sauf matrice rouge.
- **A-27 · aucun nombre utile sur une copie neutralisée.** L'import purge jetons et références de paiement : les abonnements par passerelle, par type de moyen et les cartes qui expirent valent tous « inconnu ». Le compte réel demanderait une lecture de la source par Ced, hors agents : sa décision, rien n'est lancé.
- **A-26 · les intégrations ajoutées par un script ne sont pas vues.** L'outil compte ce qui est écrit dans les contenus et les réglages lus ; ce qu'un script charge une fois la page affichée lui échappe. Limite du brief, rappelée ; une famille qu'on ne sait pas lire répond « illisible ».
- **A-29 · pas d'historique d'échec pour les tâches de WordPress.** Seule la file de WooCommerce garde ses échecs ; un zéro ne prouve pas l'absence d'échec ailleurs. Une tâche inconnue n'est attribuée à aucune extension.
- **A-22 · le rejeu indépendant attend toujours, et le paquet est à refaire.** La commande demandée à Ced le 26/11 ne vaut plus (dépendance changée). Lot T-03 pour que les relecteurs rejouent eux-mêmes les vérificateurs de paquet.
- **C-25 · une demande sans effet, et un droit non validé.** Le §3.7 demande la fonction de rétractation en deux étapes ; il ne dit ni ce que la demande déclenche, ni comment le délai se compte. Livré : la demande datée, visible de l'administration, rien d'autre. Délai (14 jours), point de départ (paiement) et borne (incluse) sont des défauts techniques, pas une lecture de la loi : à faire valider par le conseil juridique d'Imagine, comme le §3.8 le prévoit.
- **C-25, B-08 · un antislash perdu, deux fois.** Les bouchons de test ne reproduisaient pas le déséchappement de WordPress ; un texte libre contenant un antislash était refusé ou altéré. Corrigé dans C-25, à corriger dans B-08 ; règle ajoutée à la file de la voie 2.
- **C-22, C-24, C-25 · trois sections insérées dans l'écran de réglages par réécriture du HTML.** Pas de point d'accroche dédié dans C-10. Dette acceptée jusqu'à la réponse de Ced sur la place de ces sections ; un seul changement de l'écran alors.
