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

## 27 novembre 2026, 4 h — lots A-28, T-03, A-29, A-30, C-26, voie 2

- **A-28 · l'import a changé deux fois dans la nuit.** La correction demandée (compter les champs restants d'un message purgé) est faite ; elle a aussi découpé le fichier de l'import en cinq, pour le style, sans que ce soit demandé. Non défait (équivalence prouvée par Hermès, à regarder par la vérification) ; règle ajoutée : une correction ne restructure pas un fichier commun. Import gelé, style compris.
- **A-28 · deux tables vidées sans phrase officielle citée.** `fluentform_draft_submissions` et `ff_scheduled_actions` restent dans la liste, marquées « doute ».
- **A-21 à A-27 · une requalification perdue.** Sept matrices rejouées avant la fusion d'A-28, périmées par sa correction. À refaire une fois, à l'arrivée de la vérification d'A-28.
- **T-03 · les lots clos avant A-21 restent hors du rejeu des paquets.** Leur ajouter une déclaration périmerait leurs preuves. Ils sont nommés « hors rejeu » ; seuls A-21 à A-30 sont rejoués par les relecteurs.
- **A-29 · pas de preuve native.** Sur la copie neutralisée, le processus finit en erreur (sortie 255) après un résultat de succès. Cause non établie ; aucun succès déclaré.
- **A-30 · sur une copie neutralisée, on ne sait pas dire « à créer » ou « existant ».** Les adresses sont anonymisées par l'import : le rapprochement vaut « inconnu ». Le nombre utile demandera le fichier d'Imagine et une lecture sur la source, par Ced : rien n'est lancé.
- **C-26 · étanchéité des sorties nouvelles non prouvée.** Le test contrôlait Soutenir, la coopérative et l'agenda contre une liste de témoins incomplète, et ne visitait pas la page `/evenements/`. Aucune fuite constatée ; six corrections de fond.
- **Voie 2 · aucun travail depuis 0 h 33**, file pleine. Blocage hors du dépôt (session arrêtée ou non réveillée) : à Ced.

## 27 novembre 2026, 7 h — lots A-26, A-27, T-03, A-30, A-31, B-07, B-09, C-23

- **A-26, A-27, A-31 · paquets périmés par un changement du lanceur de rejeu.** Les corrections de T-03 ont modifié six fichiers de `wp/tests/t01/` que ces paquets gèlent. À refaire une fois ; le lanceur est gelé comme l'import.
- **T-03 · A-20 hors du rejeu des paquets.** Le brief prévoyait A-20 à A-25 ; A-20 est sorti « déclaration absente ». Rattrapé par une consigne, sans changer ses contrôles.
- **T-03 · les tests de contrat du lanceur ne sont pas joués par la commande des relecteurs.** Leur vert est relu, pas rejoué par eux.
- **A-30 · un sceau vert masquait une suite non rejouable.** La suite Python dépendait d'une variable d'environnement du poste d'Hermès. Corrigé ; règle ajoutée (session Windows propre).
- **A-30 · sources officielles citées non vérifiables par les relecteurs.** Deux captures datées gardées hors dépôt ; deux anciennes adresses restent en « doute ».
- **A-30 · la neutralisation se reconnaît à un seul marqueur** (`imagine_staging_disabled_plugins`). Documenté : si le moteur de l'import change ce marqueur, A-30 est à reprendre.
- **A-31 · sur une copie neutralisée, la nature des commandes vaut « inconnu ».** Années, états, liens cassés et remboursements restent lisibles.
- **C-23 · paquet devenu historique.** C-26 a modifié deux de ses sources de test sans le resceller. Le test d'étanchéité à jour est celui de C-26.
- **C-26 · suite Python non rejouée par les relecteurs.** Le lancement leur est refusé ; la preuve repose sur les reçus, huit mutations et la relecture du code. À rejouer par Ced s'il le souhaite (`production/C-26/A-VOIR.md`).
- **B-08, B-09 · deux types de contenu que l'import ne connaît pas.** Les propositions de sujet et les messages de contact (`imagine_contact`, cinq clés) sont des messages de visiteurs. L'import, gelé, ne les viderait pas sur une copie du nouveau site. Sans effet aujourd'hui (l'archive est celle du site actuel) ; à ajouter à la liste fermée le jour où l'import sera rouvert.
- **B-09 · ni durée de conservation ni antispam sur le formulaire de contact.** À arrêter avant l'ouverture au public ; question rangée pour Imagine.
- **B-09 · pages hors de la matrice d'étanchéité.** Elles ne portent aucun contenu réservé ; extension de la matrice en une fois, plus tard.
- **B-07 · échappement d'un champ de texte de l'agenda à vérifier.** Signalé par Hermès, non reproduit ; complément demandé.
- **Voie 2 · arrêt de 0 h 33 à 5 h 01, cause non établie.** La session a retiré seule un verrou de plus de quatre heures.

## 27 novembre 2026, 13 h — lots A-32, A-31, T-03, B-11, C-28, B-10, C-27

- **A-10 à A-25 · les outils d'inventaire ne vérifient pas où ils tournent.** Aucun ne lit le fichier de statut « vérifié » ; ils aboutissent sur un site sans ce fichier, même déclaré « production ». Ils sont en lecture seule et ne sont pas modifiés ; la tournée (A-32) fait le contrôle pour eux. Lancés un par un, ils restent sous la seule décision de Ced. Le brief d'A-32 affirmait le contraire : corrigé.
- **A-31 · compteurs de liens cassés publiés exactement.** Le regroupement des petits nombres ne s'applique qu'aux années et aux années par état. À défaire si Ced préfère « moins de 5 » partout.
- **Harnais de rejeu · un échec passager à la première passe** (« no such object »), vert à la seconde. Lanceur gelé, non rouvert.
- **T-03 · documents du lot restés à l'état de candidat à côté du `PRET`.** Mise en cohérence demandée ; le mécanisme n'est pas en cause.
- **C-28 → B-11 · un fichier partagé changé après le scellé d'un lot voisin.** L'appel ajouté dans `AchatsNumeros.php` a fait échouer un test de B-04 et périmé la réception de B-11, sans que B-11 ait bougé. Réception complémentaire, historiques conservés.
- **Paywall · un `catch` trop large.** Une erreur de programmation y devient « accès fermé » : sûr, mais elle a masqué la régression ci-dessus. Repris au gel du code, pas avant.
- **B-11 · le parcours dans les deux éditeurs réels n'est pas prouvé par automate.** Persistance prouvée par un témoin d'écriture sur le vrai WordPress ; le geste dans l'éditeur revient à Ced.
- **B-11 · une adresse de vidéo collée dans le corps réveille l'oEmbed natif.** Verrou demandé par le lot B-12.
- **Réglages · le formulaire natif rend explicites des options absentes.** Cinq options de lots antérieurs (découverte, tarif solidaire, newsletters, rétractation) sont créées à leur valeur par défaut quand l'écran est enregistré. Comportement natif de WordPress, accepté ; on compare les valeurs effectives.
- **B-10 · la désaccentuation générale dépend de l'extension intl de PHP.** Sans elle, repli sur une table latine bornée. À garantir sur l'hébergement.
- **B-10 · un arrêt brutal pendant un chargement peut laisser un verrou d'import.** Pas de reprise automatique.
- **C-27 · une lecture en échec prise pour une absence.** Deux corrections importantes en file.
- **C-28 · concurrence et arrêt en plein paiement non qualifiés.** La correction demandée couvre l'arrêt après le paiement.
- **A-30 · comptes globaux relevés pendant que l'autre voie livrait.** Ils ne se comparent pas d'un rapport à l'autre.

## 27 novembre 2026, 16 h — lots B-11, B-12, C-28, C-27, A-29, voie 1

- **Voie 1 · muette depuis 13 h 33.** File pleine, aucune question posée. Un worker d'A-31 a été interrompu par une erreur 401 (« jeton fournisseur expiré ») ; cause de l'arrêt non établie. Signalé à Ced.
- **Extension du site · le fichier d'amorçage partagé périme les réceptions des lots voisins.** B-12 a périmé B-11, C-29 a périmé B-12, sans qu'aucun code de ces lots ait bougé. Règle : contrôle par contrat, sur les lignes du lot. Les lots code clos ne sont pas rouverts.
- **B-11 · vérification « remonte à Ced » tranchée sans Ced.** Les deux points étaient techniques ; la saisie dans l'éditeur réel reste à faire par Ced avec la validation visuelle.
- **B-12 · le verrou se contournait par la casse de la route d'aperçu.** Bloquant, en correction ; il fallait un rédacteur connecté.
- **B-12 · le verrou dépend de l'ordre interne des appels du cœur de WordPress.** Vrai en 7.0.9, non garanti. Matrice native à rejouer à chaque montée de version ; elle n'est pas dans la suite scellée.
- **C-28 · second tour sans rejeu indépendant de la suite Docker.** Clos sur le rejeu du premier tour, l'intégrité des preuves et le rejeu général d'un autre vérificateur.
- **C-28 · une clé écrite en toutes lettres dans le fichier de C-14** au lieu de la constante. Sans effet ; repris au gel du code.
- **C-27 · effacement et réponse simultanés non qualifiés.** Le verrou est symétrique et testé ; l'entrelacement réel ne l'est pas.
- **A-29 · sortie 255 après un succès sur une copie neutralisée, cause non établie.** Lot rangé sans `PRET`, hors de la tournée ; le gardien refuse, aucun faux succès.

## 27 novembre 2026, 19 h — lots A-31, A-32, T-03, C-29, B-12, voie 1, voie 2

- **Voie 1 · arrêt de 13 h 33 à 17 h 34, cause non établie.** Reprise seule au réveil horaire, sur un verrou de plus de quatre heures retiré par Hermès. Quatre heures perdues.
- **A-31, A-32, T-03 · blocage croisé des portails.** Chaque lot exige un rejeu général sans paquet rouge, et chacun est le rouge de l'autre tant qu'il n'est pas scellé. Sortie retenue : la séquence conjointe d'Hermès, une fois ; la preuve est le rejeu général après les deux sceaux.
- **A-31 · consigne de la file plus large que l'arbitrage.** Les natures et les remboursements par année ont été publiés exactement sur une phrase résumée trop vite ; resserré avant le sceau. Erreur de la file, pas d'Hermès.
- **A-31 · le lanceur dit `pass=true` et sort en 0 avec un paquet rouge.** Connu : la ligne `PAQUETS` se lit à part. Le lanceur est gelé et n'est pas rouvert ; les portails des lots lisent déjà les deux canaux.
- **C-29 · un relecteur « conforme », l'autre « à corriger ».** Les deux défauts tenaient à des enchaînements que ni le jeu d'essai ni l'attendu ne couvraient ; la fusion a relu le code.
- **C-29 · plusieurs lectures par compte dans le bilan de l'écran.** Accepté pour la démonstration ; à requalifier avant tout volume réel.
- **C-29 · incident de banc.** Deux préparations de jeu d'essai avaient programmé une tâche de cache à l'arrêt ; état restauré et relu, sauf l'égalité des sessions au départ d'un ancien essai, non revendiquée.
- **B-12 · preuve « zéro sortie » hors de la suite scellée.** Réserve permanente, écrite au README : matrice native à rejouer à chaque montée de version du cœur.
- **Voie 2 · rien depuis 17 h 13**, corrections de C-29 arrivées à 17 h 53 et B-13 en file. Moins de trois heures : noté, pas d'alerte.

## 27 novembre 2026, 22 h — lots A-31, A-32, A-33, T-03, C-29, B-13, B-14, voie 2

- **Voie 2 · arrêt de 17 h 13 à 21 h 18, cause non établie.** Reprise seule, sur un verrou ancien retiré par Hermès. Troisième arrêt de ce genre en vingt-quatre heures (voie 2 la nuit, voie 1 l'après-midi, voie 2 le soir) ; chaque fois, environ quatre heures perdues.
- **A-32 · un relecteur « conforme » sur trois points où l'autre voyait juste.** Codes de supervision perdus dans le bilan, `define` dans une chaîne PHP accepté par la garde, date d'exemple d'A-19 figée : la fusion a relu le code et confirmé. Corrections en cours.
- **A-32 · la fusion lit le plafond d'A-16 comme une troncature.** Dix numéros est le périmètre du cahier des charges (§4.3) et le défaut documenté de l'outil ; il n'y a pas de mode sans plafond et il n'en est pas créé.
- **A-32, T-03 · un lecteur de paquet qui photographie les voisins.** Le lecteur d'A-32 prenait l'empreinte de tout le dossier des outils : l'arrivée d'A-33 l'a fait passer au rouge sans qu'une ligne d'A-32 ait changé. Celui de T-03 englobait le paquet d'A-31 : la retouche d'A-31 l'a périmé quarante minutes après son `PRET`. Règle écrite (liste fermée), valable pour les lots à venir ; les lots clos ne sont pas rouverts.
- **A-31 · le sceau lie cinq fichiers de la tournée d'A-32.** Les corrections d'A-32 peuvent donc périmer le paquet d'A-31, clos : un resceau par sa commande, code inchangé, sans rouvrir la clôture.
- **A-31 · clos sans rejeu natif par un relecteur.** Le vérificateur a rejoué les suites Python et lu les preuves déposées ; la matrice dans les conteneurs n'a été jouée que par Hermès. Les journaux des paquets ne sont pas versionnés : un lecteur de paquet ne se rejoue pas hors du NUC.
- **A-33 · deux versions de Python sous Windows.** A-33 et la requalification d'A-32 mesurent Python 3.11.15 ; les lots précédents et les commandes de réception, 3.14.6. À rejouer avec celui des commandes de réception.
- **A-33 · un échec passager d'un test de C-29 dans un rejeu général**, pendant que la voie 2 corrigeait C-29 ; non reproduit ensuite. Aléa de deux voies sur un même arbre, noté.
- **B-13 · « Connexion » reste le libellé de l'entrée du menu pour un lecteur connecté.** Elle mène au compte. Présentation, à voir par Ced avec le lot.
- **B-13 · le lecteur de C-29 borné à ses propres fichiers pendant B-13.** Conforme à la règle du contrat ; C-29 n'est pas clos, sa vérification le lira.
- **B-14 · la liste « Derniers articles » de l'accueil est retirée.** Le §3.2 ne la prévoit pas. Le contrôle que B-05 faisait sur cette liste n'a plus d'objet sur l'accueil ; B-05, clos, n'est pas modifié. À confirmer par la relecture de B-14.
- **C-08 · le balisage de contenu payant (§3.9) est déjà posé** par le paywall de la démonstration ; pas de lot nouveau pour lui. Sa description reprend l'extrait public.

## 28 novembre 2026, 1 h — lots C-29, B-13, B-14, B-15, B-16, C-30, A-32, A-33, voie 1

- **Voie 1 · aucun dépôt depuis 22 h 53, aucun rapport depuis 22 h 24.** A-32 rescellé et A-33 installé, portails verts, sans `PRET` ni rapport de fin. Moins de trois heures à 1 h 20 : noté, pas d'alerte. Ce serait le quatrième arrêt en vingt-huit heures.
- **A-32 · rescellé à 22 h 29 sur une photographie encore récursive.** Le sceau a précédé d'une minute la règle de la liste fermée écrite à 22 h 30. À borner avant le `PRET`, sinon A-34 le fera retomber.
- **C-29 · vérifié « prêt » sur un rejeu rouge pour une cause étrangère.** Une erreur dans un test de B-16 alors en cours d'écriture, non suivi par Git au moment du rejeu. Les rejeux suivants sont verts. Aléa de deux lots sur un même arbre ; clos.
- **B-14 · le vérificateur n'a pas pu relancer le rejeu en conteneur** (commande derrière une approbation, session non interactive). Il a contrôlé les reçus contre les empreintes des fichiers. Clos avec cette réserve.
- **B-14 · la recette d'origine de B-01 ne passe plus.** Deux contrats dépassés par C-11 et B-03, un inventaire dépassé. B-01 reste clos, sa recette devient historique ; requalification d'ensemble au gel du code.
- **B-14, B-16 · le lecteur de B-11 est rouge sur deux gabarits modifiés à bon droit.** Compléments déposés sous B-14 et B-16 (diff borné, 23 contrôles natifs rejoués). B-11 reste clos, son paquet devient historique pour ces deux fichiers.
- **B-14 · la fusion attribuait à tort un écart de comptage à A-32 et A-33.** Il venait de deux tests de B-15. Sans suite.
- **B-15, B-16 · un relecteur « conforme » là où l'autre voyait juste, deux fois dans la nuit.** B-15 : la preuve de cache ne prouvait que le déterminisme. B-16 : l'appel à l'abonnement s'affichait pour un abonné offert ou en résiliation à échéance, et le contrôle d'étanchéité ne lisait que le texte visible de l'appel. Les fusions ont relu le code et tranché ; corrections rendues, vérifications attendues.
- **B-16 · des tâches planifiées créées hors de l'annulation pendant la recette.** Les caches de rapports de Subscriptions s'écrivaient à la fermeture du processus : quatre actions créées et quatre annulées, restaurées par leurs identifiants, empreinte de départ retrouvée. Site fictif ; noté.
- **C-30 · la table des sessions trop grosse pour le transport du banc.** Restauration reprise ligne par ligne, trois sessions rendues à l'identique. Site fictif ; noté.
- **C-30 · un visiteur qui arrive avec un code suivi connu reçoit le cookie de session de WooCommerce.** Pas de cookie propre au code ; savoir s'il demande un consentement est rangé pour Imagine et son conseil. Lot C-32 pour l'inventaire.
- **Rapports · Hermès travaille par délégation** (« relais parent », « liste initiale déléguée ») : un lot ajouté à la file pendant une délégation n'est pris qu'au relais suivant. Sans conséquence cette nuit ; noté.

## 28 novembre 2026, 4 h — lots A-32, A-33, B-15, B-16, C-30, C-31, C-32, C-33, voie 1

- **C-32 · « aucun cookie en simple lecture » n'est pas tenu sur la démonstration.** Zéro cookie posé par le serveur, mais sept cookies d'attribution d'origine de WooCommerce posés par script. Constat gardé rouge, rien n'est éteint ; question chez Imagine et son conseil.
- **C-32 · le parcours de lecture oubliait quatorze pages** (« Notre coopérative » et ses pages filles, « Soutenir », « Proposer un sujet », quatre fiches d'événement) : le total de 44 pages masquait l'oubli. Corrigé par identité d'adresse avec l'inventaire de C-26.
- **C-32 · la restauration des sessions supprimait ce qu'elle ne savait pas attribuer.** Une session d'un autre visiteur, arrivée pendant la recette, aurait été effacée. Corrigé : seules les sessions attribuées avec certitude sont reprises. Site fictif.
- **C-31 · le câblage n'avait de preuve que sur le site.** L'ordre des arguments à l'inscription et le parcours « Mon compte » n'étaient exercés par aucun test rejouable ; correction en cours.
- **C-33 · deux contrôles qui ne pouvaient pas échouer.** Les en-têtes étaient inspectés après filtrage, et la signature des flux cherchée n'importe où dans la page. Correction en cours, avec une mutation témoin pour chacun.
- **C-33 · la route d'un fournisseur de plan du site absent rend une page ordinaire (200), pas une erreur 404.** Comportement natif de WordPress, aucun compte montré ; laissé tel quel.
- **C-30 · la démonstration ne couvre que la commande classique**, pas la commande par blocs ; le raccord à la Store API est prouvé sur son accroche, pas sur un paiement.
- **C-30 · un rapport de cache de Subscriptions écrit à la fermeture du processus, hors de l'annulation.** État de départ retrouvé à l'identique, banc corrigé. Site fictif ; noté (déjà vu sous B-16).
- **A-33 · un relecteur « conforme » là où l'autre voyait deux défauts.** Le poids des PDF des numéros manquait à la comparaison, et un numéro sélectionné pouvait être recompté hors sélection. La suite était verte parce que le jeu d'essai ne portait aucun PDF. Troisième fois en deux nuits (B-15, B-16).
- **A-32, A-33 · des vérificateurs de paquet en dépassement de délai dans les rejeux de la voie 2** (2 h 19, 2 h 44), pendant que les deux voies rejouaient. Non reproduit seul ; à mesurer par la voie 1, lanceur inchangé.
- **Voie 1 · quatrième arrêt en trente heures**, d'environ 22 h 53 à 3 h : reprise seule, verrou périmé retiré, cause non établie.
- **Rapports · un rapport de la voie 2 a reçu la sortie d'une commande à la place de son texte** (accents graves interprétés par le terminal, qui a relancé la préparation de l'image). Corrigé aussitôt, aucun reçu touché.
- **Vérifications · trois vérificateurs sur quatre n'ont pas pu relancer le rejeu en conteneur** (session non interactive). Ils ont contrôlé les reçus contre les empreintes ; seul celui de C-30 a rejoué la suite.

## 28 novembre 2026, 7 h — lots C-31, C-32, C-33, A-33, voie 1

- **Voie 1 · cinquième arrêt en deux jours** : aucun dépôt ni rapport depuis 3 h, constaté à 7 h 20. Les corrections d'A-33 ne sont pas commencées. Cause non établie, comme les quatre premières fois.
- **A-33 · un `PRET` antérieur à la relecture est resté dans le dépôt** depuis 2 h 25, alors que le lot est « à corriger » depuis 3 h 48. Le vérificateur de C-33 l'a relevé. Retrait demandé en tête de la voie 1.
- **A-33 · un dépassement de délai de son vérificateur, lu une fois par la voie 2 rejouant seule** (vers 5 h 10), disparu au rejeu suivant. La voie 1 étant à l'arrêt, ce n'est plus seulement un aléa de deux rejeux simultanés ; à mesurer par la voie 1, lanceur inchangé.
- **C-31 · une adresse refusée restait dans la session de commande avant le refus** (table des sessions de WooCommerce, commande classique et par blocs). Reproduit puis corrigé en avançant le contrôle ; site fictif.
- **C-31 · la première visite du panier par blocs a fait migrer la page « Panier » et créé une note de WooCommerce.** État de départ retrouvé depuis les préimages, restauration intégrée à la recette. Site fictif ; noté.
- **C-31, C-32 · des fichiers `A-VOIR.md` et une section du README périmés** : ils disent « `PRET` absent » ou « local seulement » alors que la réception est faite. Les preuves font foi ; lots non rouverts pour cela.
- **C-32 · deux relevés de restauration rouges pour des caches natifs** (styles de blocs, délai du cache des compositions du thème). Reçus rouges conservés, exceptions bornées à ces deux noms.
- **Vérifications · les recettes sur le site ne sont pas rejouées par les vérificateurs** (C-31, C-32, C-33) ; ils ont relancé les suites hors ligne et lu les reçus. Clos avec cette réserve.
