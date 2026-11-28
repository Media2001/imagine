# Décisions

Ce qui est tranché par Ced, daté. Ce fichier précise ou corrige le cahier des charges. Tenu par Claude.

## Tranché

| Date | Décision |
|---|---|
| 11/11/2026 | Le cahier des charges v3.1 est la référence du projet. |
| 11/11/2026 | Ced réalise toute la production technique. |
| 11/11/2026 | Le design et le référencement sont fournis : hors du périmètre de Ced. |
| 11/11/2026 | Le dépôt de code est `Media2001/imagine`. |
| 11/11/2026 | On commence par le socle, sans attendre les maquettes. |
| 11/11/2026 | Le développement et les tests se font dans un staging Docker sur le NUC, décrit dans le dépôt. Rien ne s'installe sur la machine. |
| 11/11/2026 | **On repart de la production.** Le site actuel est copié, mis à niveau (Memberships et ce qui en dépend), puis reçoit le nouveau thème et le code sur mesure. Les abonnés en ligne, leurs mots de passe et leurs moyens de paiement ne sont donc pas migrés : ils restent en place. Seuls les abonnés hors ligne (base Access) sont importés. |
| 11/11/2026 | Trois chantiers indépendants : A l'existant, B le thème, C le code sur mesure. |
| 11/11/2026 | Toute transformation de l'existant est un script rejouable : elle sera refaite sur une copie fraîche le jour de la bascule. |
| 19/11/2026 | Le staging passe par l'outil de staging de Ced, pas par Docker. Les agents y accèdent par le MCP Novamira, uniquement après neutralisation, anonymisation et vérification de la copie. |
| 19/11/2026 | Mise en ligne : on ne pousse jamais le staging vers la production. Le jour J : gel de l'ancien site, copie fraîche sur le nouveau serveur, scripts de bascule seuls, tests, puis changement de DNS. L'ancien site reste en secours. Une répétition générale la semaine précédente. |
| 19/11/2026 | Hermès travaille en continu sur ce dépôt (pas de passages à heures fixes), et s'arrête quand la file est vide. |
| 19/11/2026 | Parution : un numéro par trimestre civil (n° 167 = janvier-mars 2026) et un hors-série, sans raison de décaler. Les échéances du paiement en quatre fois sont donc communes à tous les abonnés et régulières ; un changement de calendrier est une action exceptionnelle. |
| 20/11/2026 | Staging : fidèle à la production. On garde extensions, réglages et tables ; on ne retire que ce qui est dangereux ; cinq points bloquent le statut « vérifié ». Les listes fermées de la première version du lot A-01 sont abandonnées. |
| 20/11/2026 | Un lot a un délai (une demi-journée par défaut) ; au-delà, Hermès rend compte et passe au suivant. |
| 20/11/2026 | La production est en WordPress 6.9.1 (compatible Novamira). L'outil de staging tourne dans Docker sous WSL sur le NUC. |
| 21/11/2026 | Arbitrages sur les lots A-00 et C-01 à C-04 : voir `docs/arbitrages-2026-11-21.md`. Notamment : accès numérique coupé dès la suspension pour impayé ; quatre paiements par année d'engagement de date à date ; même compte Stripe, sans import CSV des abonnés en ligne. |
| 21/11/2026 | Les questions métier ouvertes se tranchent avec Imagine directement : le designer ne les arbitre pas. |
| 21/11/2026 | Staging : aucun réseau jusqu'à la vérification ; ensuite le filtrage de WordPress suffit (mises à jour seulement), sans filtrage au niveau du système. La publication passe par l'usage normal de l'outil de staging, sans modifier son code. |
| 21/11/2026 | Les lots de code et d'étude se clôturent sur preuves (tests, deux relectures, vérification), sans GO de Ced. Ced valide le visuel, tranche les règles métier, et donne un GO écrit pour tout ce qui touche au réel. |
| 22/11/2026 | Une règle métier que le client n'a pas tranchée devient un réglage modifiable dans l'administration, avec une valeur par défaut prudente. Elle ne bloque pas un lot. |
| 22/11/2026 | Paiement en quatre fois : quatre échéances par bloc de quatre numéros, une par numéro (corrige la formulation du 21/11). Détail des réglages : `docs/arbitrages-2026-11-22.md`. |
| 22/11/2026 | Accord de Ced : Hermès peut créer, démarrer, arrêter et supprimer des sites de test (`imagine-test-…`) dans l'outil de staging par son usage normal, activation de la licence Novamira comprise. Il ne modifie pas l'outil et ne lance aucun import d'Imagine. |
| 23/11/2026 | Import : le cœur du site suit la version de l'archive ; l'import n'installe ni ne met à jour aucune extension. Les lots de bibliothèque se clôturent sans leurs écrans de réglages, qui seront repris et montrés à Ced au branchement. |
| 22/11/2026 | Premier paiement par SEPA : la marge de confirmation est un réglage, appliquée par défaut. |
| 11/11/2026 | Architecture de production : Claude (briefs, arbitrages), Hermès (production), Codex et Claude Code (relecture), Git comme file de travail. |

## Ouvert — à trancher par Ced

1. **Frontière du référencement.** Hypothèse de travail : le référenceur spécifie (balisage, redirections), Ced implémente dans le thème et le serveur. À confirmer.
2. **Pilotage.** La gestion de projet, le document d'interface avec Odoo et les deux sessions de formation sont-ils chez Ced ?
3. **Données réelles.** Appliqué par défaut : la copie de production vit sur le NUC hors du dépôt ; Ced lance lui-même l'import, qui la neutralise et l'anonymise (lot A-01) ; les agents ne travaillent que sur la copie anonymisée. À confirmer, et à préciser pour l'export Access : où et par qui est-il traité ?
4. **Environnements.** Hébergeur et préproduction (le staging local Docker est tranché).
5. **Licences.** WooCommerce (Subscriptions, Memberships) : obtenues le 20/11. Restent à confirmer : ACF Pro, Rank Math Pro, Event Tickets Plus, et Teams for Memberships si l'étude A-00 le retient.
6. **Site actuel.** Sauvegarde complète (export SQL et `wp-content`) à récupérer chez l'hébergeur actuel.
7. **Connecteur.** n8n hébergé à part ou intégré au site (§4.1).
8. **Numéro d'entreprise.** Recherche de la dénomination en ligne (cahier des charges) ou simple contrôle de format (décision d'octobre) ?
9. ~~Rythme d'Hermès~~ — tranché le 19/11 : Hermès travaille en continu sur ce dépôt.

## Ouvert — chez Imagine (chapitre 7 du cahier des charges, et questions issues des lots)

### Classement pour la rencontre avec Imagine (tenu par Claude, 28/11/2026)

Proposition de tri, à corriger par Ced. Toutes ces questions ont déjà un défaut prudent en place : aucune ne bloque un lot. Le tri dit seulement lesquelles méritent du temps de réunion.

**Celles qui changent ce qu'on construit** (une réponse différente du défaut ouvre un lot, ou en ferme un) :

1. **Grille tarifaire, tarif solidaire, accès découverte** (chapitre 7, points 3 à 5) : tant qu'elles sont ouvertes, le tunnel et les emails ne peuvent pas être finalisés. La forme de l'accès découverte et ce qui se passe après son épuisement en font partie (C-12).
2. **Paiement** (questions du 20/11) : prélèvement SEPA obligatoire après une première carte, retrait immédiat ou délai de grâce au premier rejet, recalcul du port en cours d'année, PayPal ; et la marge de l'échéancier en quatre fois, dont dépend le bouton « ne pas renouveler » (C-20).
3. **Abonnements offerts et groupés** : licence Teams ou liens de Memberships ; présence des bénéficiaires dans la liste d'envoi (C-13) ; leur statut pour Brevo (C-29) ; ce que devient le groupe quand le souscripteur fait effacer ses données (C-21).
4. **Rétractation** (C-25), aussi pour le conseil juridique : délai, point de départ, borne incluse, et surtout les effets (remboursement, accès gardé ou non). Aujourd'hui le site enregistre une demande et ne fait rien d'autre.
5. **Cookies et consentement** (C-30, C-32), aussi pour le conseil : le cookie de session d'un code suivi et les sept cookies d'attribution de WooCommerce demandent-ils un bandeau ? Aucun n'est construit.
6. **Offre de bienvenue** (C-30) : que donne-t-elle ? Aujourd'hui rien ; un avantage serait un lot à part.
7. **Achat sans compte** (C-14) : ouvre-t-il le numérique après création du compte ? Le parcours n'est pas livré.
8. **Import des abonnés hors ligne** (A-30) : échéance déjà passée, compte existant à la même adresse, échéance reprise ou recalculée. Les trois options sont fermées ; l'import réel ne peut pas s'écrire sans elles.
9. **Newsletters et Brevo** (C-22, C-24, C-29) : inscription d'office à la newsletter principale et par quel consentement ; noms des attributs attendus par le compte Brevo ; ce qu'on transmet des réponses de personnalisation.
10. **Tableau de bord** (C-19) : distinguer le mode de paiement (une ou quatre fois) du moyen (carte, SEPA, virement) demande un indicateur de plus ; l'ouvrir à quelqu'un qui n'a ni les extractions ni les échéances demande un droit de plus.
11. **Pack thématique** (C-28) : produit à prix unique ou produit groupé natif ; pack retiré en entier ou vendu sans le numéro dépublié.
12. **Comptes et signatures** (B-16, C-33) : page publique d'auteur pour un journaliste ; ce qu'un abonné connecté voit des comptes.
13. **Point de vente le plus proche** (B-15) : un lien vers la recherche, ou une géolocalisation.
14. **Durée de conservation des messages de contact** (B-09) : à arrêter avant l'ouverture au public ; une durée demande une purge automatique.
15. **Numéro d'entreprise** : recherche de la dénomination en ligne ou simple contrôle de format.

**Celles qui ne sont que des réglages ou des périmètres** (le défaut tient, une réponse se règle dans l'administration ou par une retouche courte) : remboursement partiel d'une commande de plusieurs numéros (C-14) ; PDF servi ou non à un robot d'indexation (C-11) ; périmètre de « paiements en attente » et de « mandats à lancer » (C-15) ; libellé d'un abonnement suspendu dans Mon compte (B-02) ; couleurs posées à la main dans les articles (B-03) ; adresse de livraison enregistrée sur le compte créé pour un client (C-16) ; doublons de l'export hors ligne (A-13) ; une ligne par abonnement ou par abonné, et finesse du filtre par localité, dans les extractions (C-18) ; abonné en annulation à terme compté ou non comme abonné dans le rapprochement des contacts (A-14) ; numéro reçu ou non après la fin de la période payée (C-13) ; présentation des inventaires de l'existant (A-19, A-23, A-27) ; rôles qui posent le statut de coopérateur et qui lisent l'espace coopérateurs (B-06) ; localité en liste fermée dans la personnalisation (C-24) ; trace dépersonnalisée d'une rétractation après effacement (C-25) ; sommaire audio réservé (B-11) ; numéros gardés par l'acheteur d'un pack modifié (C-28) ; recherche exacte des points de vente (B-10) ; sélection du menu étendu par la rédaction ou par date (B-13) ; refus de désinscription conservé après retrait d'une lettre, et identification du contact à retirer (C-29) ; code suivi rangé à côté de la source d'acquisition (C-30) ; origine de la liste des domaines refusés (C-31) ; appel à l'abonnement en fin d'article pour un abonné actif (B-16).

Issues des relectures du 20/11 (`docs/arbitrages-2026-11-21.md`, questions non tranchées) : prélèvement SEPA obligatoire après une première carte ; retrait immédiat ou délai de grâce au premier rejet ; licence Teams pour les abonnements groupés ; forme de l'accès découverte ; recalcul du port en cours d'année ; emails SEPA de Stripe ; recherche de la dénomination d'entreprise ; PayPal sous condition d'approbation.


Issues des lots, au 26/11 à 10 h (chacune est un réglage au défaut prudent, aucun lot n'attend) :

| Question fermée pour Imagine | Défaut appliqué | Réglage |
|---|---|---|
| Un remboursement partiel d'une commande de plusieurs numéros ferme-t-il tous les accès de la commande ? | Oui, toute la commande | `imagine_achat_remboursement` : `commande` ou `ligne` (C-14) |
| Un achat sans compte ouvre-t-il le numérique après création du compte (§3.7) ? | Non, fermé, pas de rapprochement par email | Parcours non livré (C-14) |
| Les bénéficiaires d'un abonnement groupé figurent-ils dans la liste d'envoi à partir des liens de Memberships, sans Teams ? | Non, fermé | `imagine_envoi_groupes` : `ferme` ou `liens_memberships` (C-13) |
| Après épuisement de l'accès découverte, un article déjà ouvert se referme-t-il ? | Oui | Réglage de C-12 |
| Un robot d'indexation vérifié reçoit-il le PDF du numéro ? | Non, l'extrait seulement | Réglage de C-11 |
| « Paiements en attente » de l'écran des échéances : inclure les commandes à l'unité (numéro, don, pack) réglées par virement et non reçues ? | Non : seulement les paiements liés à un abonnement | Pas de réglage : périmètre de la vue (C-15) |
| Un abonnement sur mandat papier suspendu figure-t-il dans « mandats à lancer » dans tous les cas, ou seulement quand un renouvellement exigible est impayé ? | Seulement le renouvellement exigible impayé | Pas de réglage : périmètre de la vue (C-15) |
| Dans « Mon compte », un abonnement suspendu avec adhésion en attente s'affiche-t-il « virement en attente de validation » ? | Non : ce libellé est réservé au circuit virement ; sinon « suspendu » ou « en délai de grâce » | Pas de réglage : libellé (B-02) |
| Les articles portent-ils des couleurs de texte ou de fond posées à la main par la rédaction ? | Non : texte neutre, la couleur relève du thème. En vue de lecture, ces couleurs sont de toute façon neutralisées | Pas de réglage : garde-fou du mode lecture (B-03) |
| Dans la commande pour un client, l'adresse de livraison saisie est-elle enregistrée sur le compte créé par ce parcours ? | Oui, sur le seul nouveau compte ; jamais sur un compte existant | Réglage oui ou non, dans l'écran de réglages (C-16) |
| Dans le contrôle d'un export d'abonnés hors ligne, deux personnes de même nom à la même adresse sont-elles un doublon, ou faut-il aussi le même prénom (conjoints, colocataires) ? | Doublon : les deux lignes sont signalées, rien n'est fusionné | `doublon_prenom_identique`, désactivée, dans la correspondance des colonnes (A-13) |
| Les extractions rendent-elles une ligne par abonnement (un compte à deux abonnements apparaît deux fois) ou une ligne par abonné ? | Une ligne par abonnement | Pas de réglage : dédoublonnage à ajouter à la demande (C-18) |
| Dans les extractions, le filtre par localité doit-il accepter un début de code postal, une plage ou plusieurs pays ? | Non : pays et code postal exacts | Pas de réglage : filtre à affiner à la demande (C-18) |
| Dans le rapprochement des contacts de la newsletter, un abonné qui a désactivé le renouvellement mais dont la période payée court encore compte-t-il comme « abonné » ? | Non : seul l'état actif compte. À accorder avec le paywall, qui garde l'accès jusqu'au terme (§3.4) | Pas de réglage : périmètre du compte (A-14) |
| Qui peut ouvrir le tableau de bord (des nombres, aucune identité) : seulement ceux qui ont déjà les extractions et les échéances, ou aussi quelqu'un qui n'a ni l'un ni l'autre ? | Seulement ceux qui ont les deux droits | Pas de réglage : un droit à part serait à créer (C-19) |
| Le tableau de bord doit-il distinguer le « mode » de paiement (une ou quatre fois) du « moyen » de paiement (carte, SEPA, virement…), comme l'écrit §3.13 ? | Un seul axe chiffré ; « par moyen de paiement » affiché grisé, sans chiffre | Pas de réglage : indicateur à ajouter (C-19) |
| Un abonné qui ne renouvelle pas reçoit-il encore le numéro dont la liste d'envoi se clôt après la fin de sa période payée ? | Non : règles de la liste d'envoi inchangées | Pas de réglage : règle de C-13 |
| À la création d'un compte, le lecteur est-il inscrit d'office à la newsletter principale (§3.10), et par quel consentement explicite ? | Non : aucune case cochée tant que le lecteur ne l'a pas fait lui-même | Réglage fermé « inscrire par défaut à la principale », dans l'écran de réglages (C-22) |
| Quand le souscripteur d'un abonnement groupé ou l'offrant d'un abonnement offert fait effacer ses données, que devient le groupe ou le cadeau du côté de l'administration (nouveau gestionnaire, appel à renouvellement) ? | Les bénéficiaires gardent leur adresse, leurs droits et leur numéro ; rien d'autre n'est changé | Pas de réglage : règle de l'effacement, les tiers sont préservés (C-21) |
| Dans l'inventaire des abonnements du site actuel, faut-il distinguer « moyen de paiement absent » de « passerelle dont on ne sait pas lire le moyen », ou tout compter comme « sans moyen enregistré » ? | Distinguer : on ne déclare pas absent ce qu'on ne sait pas lire | Pas de réglage : présentation de l'inventaire (A-19) |
| Qui peut poser ou retirer le statut de coopérateur sur un compte : le seul rôle Administrateur, ou aussi un autre rôle (à nommer) ? | Administrateur seul | Réglage des rôles autorisés, dans l'écran de réglages (B-06) |
| Qui peut lire l'espace coopérateurs sans être coopérateur (rédaction, gestionnaires) ? | Administrateur seul ; les autres rôles sont refusés | Réglage des rôles autorisés, dans l'écran de réglages (B-06) |
| Dans le formulaire de personnalisation, la localité est-elle un texte libre ou un choix dans une liste fermée ? | Liste fermée : un texte libre deviendrait tel quel une étiquette | Les questions et leurs choix sont un réglage (C-24) |
| Pour la transmission des réponses de personnalisation (§3.10, « inscrit à au moins une newsletter »), une inscription créée d'office à la création du compte compte-t-elle comme une inscription ? | Non : seule une inscription choisie par le lecteur ouvre la transmission | Pas de réglage : règle de la transmission ; aucun envoi n'existe encore (C-24) |
| Dans le compte des abonnés du site actuel, une adresse ou un identifiant de lecteur partagé avec un compte de l'administration compte-t-il comme un doublon du lecteur ? | Oui : c'est un obstacle à la reprise du compte | Pas de réglage : présentation de l'inventaire (A-23) |
| Rétractation en ligne : la borne finale du délai est-elle incluse (la demande reste possible jusqu'à la fin du dernier jour) ? | Oui, incluse | Réglages du délai (nombre de jours, point de départ), dans l'écran de réglages (C-25). À faire valider par le conseil juridique d'Imagine |
| Rétractation : pour un abonnement dont le premier numéro n'est pas encore parti, le délai court-il du paiement ou de la première réception ? | Du paiement ; une date de départ manuelle peut être posée sur la commande | Réglage du point de départ : paiement ou date manuelle (C-25). À faire valider par le conseil juridique |
| Rétractation : après traitement de la demande par l'administration, l'accès numérique est-il gardé jusqu'au terme payé ? | Le site ne change rien : la demande n'a aucun effet automatique | Pas de réglage : aucun effet n'est livré (C-25) |
| Rétractation : la demande acceptée déclenche-t-elle un remboursement depuis le site ? | Non : aucun remboursement, même manuel, n'est lancé par ce parcours | Pas de réglage : aucun effet n'est livré (C-25) |
| Après l'effacement des données d'un compte, garde-t-on la trace d'une demande de rétractation (date et référence de commande, sans motif ni identité), pour empêcher un second dépôt ? | Oui, trace dépersonnalisée gardée | Pas de réglage : règle de l'effacement (C-25) |
| Dans le compte des moyens de paiement du site actuel, « carte qui expire dans les six mois » inclut-il tout le mois d'expiration, ou s'arrête-t-il au jour de l'audit six mois plus tard ? | Au jour de l'audit : une carte de mai 2027 n'est pas « dans les six mois » d'un audit de novembre 2026 | Pas de réglage : présentation de l'inventaire (A-27) |
| Import des abonnés hors ligne : un abonné dont l'échéance est déjà passée dans le fichier est-il importé ? | Non décidé : l'import à blanc le compte à part et n'en fait rien | Option de la configuration, fermée ; « oui » est refusé tant qu'aucune règle n'est écrite (A-30) |
| Import des abonnés hors ligne : quand une ligne du fichier tombe sur un compte qui existe déjà à la même adresse, rattache-t-on l'abonnement à ce compte, ou la ligne revient-elle à l'administration ? | Rien n'est rattaché : la ligne est comptée « compte existant » | Option de la configuration, fermée (A-30) |
| Import des abonnés hors ligne : la prochaine échéance est-elle reprise telle quelle du fichier, ou recalculée d'après les numéros dus et le calendrier de parution (§3.5) ? | Aucune échéance n'est calculée | Option de la configuration, fermée (A-30) |
| Combien de temps le site garde-t-il un message envoyé par le formulaire de contact ? | Aucune suppression automatique : le message reste jusqu'à ce que l'administration l'efface ou que la personne demande l'effacement de ses données | Pas de réglage pour l'instant ; à arrêter avant l'ouverture au public (B-09) |
| Le sommaire audio d'un numéro (§3.3) est-il réservé à ceux qui ont droit au numéro, ou ouvert à tous ? | Réservé, comme le PDF du numéro | Pas de réglage : il suit la décision d'accès du numéro (B-11) |
| Pack thématique (§3.3) : si la rédaction ajoute ou retire un numéro après un achat, que garde l'acheteur ? | Les numéros que le pack contenait au moment du paiement, ni plus ni moins | Pas de réglage : règle de l'achat (C-28) |
| Points de vente (§3.14) : la recherche porte-t-elle sur une localité ou un code postal exacts, ou faut-il aussi un début de code postal, un rayon ? | Localité ou code postal exacts, sans tenir compte de la casse ni des accents | Pas de réglage pour l'instant (B-10) |
| Un pack thématique (§3.3, « produits groupés ») est-il bien un produit à prix unique pour l'ensemble, et non le « produit groupé » natif de WooCommerce, où chaque numéro s'ajoute et se paie séparément ? | Produit simple à prix unique | Pas de réglage : forme du produit (C-28) |
| Pack thématique dont un numéro a été dépublié : le pack est-il retiré de la vente en entier, ou vendu sans ce numéro à un prix recalculé ? | Retiré de la vente en entier, refusé au panier et à la commande ; aucun prix recalculé | Pas de réglage (C-28) |
| Menu étendu des thématiques (§3.1, « une sélection d'articles illustrés ») : la sélection est-elle choisie par la rédaction, ou faite des articles les plus récents ? | Les articles les plus récents de la thématique | Nombre d'articles en réglage (B-13) |
| Brevo (§3.10) : quels noms d'attributs le compte Brevo d'Imagine attend-il, et quel statut porte le bénéficiaire d'un abonnement offert ou groupé ? | Clés internes du site ; statut « inconnu » pour un bénéficiaire. Rien n'est transmis | Correspondance des noms à mettre en réglage au branchement (C-29) |
| Pied de page (§3.2, « point de vente le plus proche ») : le site cherche-t-il le point de vente le plus proche du visiteur, par géolocalisation, ou renvoie-t-il vers la recherche par localité ? | Un lien vers la recherche ; aucune géolocalisation, ni par le navigateur, ni par l'adresse IP | Pas de réglage pour l'instant (B-15) |
| Brevo (§3.10) : un lecteur s'est désinscrit d'une newsletter, puis cette newsletter est retirée du catalogue. Reste-t-il signalé « à retirer » de l'outil d'envoi ? | Oui : un refus explicite est conservé, la fiche reste « à retirer » ; la suppression d'une lettre encore choisie ne vaut pas désinscription. Rien n'est transmis | Pas de réglage (C-29) |
| Brevo (§3.10) : le bénéficiaire d'un abonnement groupé dont l'adhésion est suspendue est-il « inconnu » ou « non abonné » ? | « Inconnu » dès qu'il est identifié comme bénéficiaire, adhésion active ou non | Pas de réglage (C-29) |
| Brevo (§3.10) : au branchement, le contact à retirer est-il identifié par le compte du site, ou par une adresse portée dans la fiche ? | Par le compte ; la fiche « à retirer » ne porte rien d'autre | À arrêter avec la correspondance Brevo (C-29) |
| Offre de bienvenue (§3.7, page atteinte par QR code) : que donne l'offre (une réduction, un numéro offert, rien d'autre qu'un accueil) ? | Rien : la page accueille et renvoie vers « S'abonner » ; aucun prix modifié, aucun code de réduction | Liste des codes suivis en réglage ; l'avantage sera un lot à part, après la décision (C-30) |
| Code suivi (§3.7, §3.14) : le code d'un QR code remplit-il la « source d'acquisition » du compte (§4.2), ou se lit-il à côté de la réponse à « Comment nous avez-vous connus ? » ? | À côté : le code est rangé sur la commande, la source du compte n'est pas écrite par lui | Pas de réglage (C-30) |
| Adresses email jetables (§3.9) : d'où vient la liste des domaines refusés à l'inscription, et qui la tient à jour ? | Une liste tenue à la main par Imagine ; vide, rien n'est refusé ; aucune liste téléchargée ni service tiers | Liste des domaines en réglage (C-31) |
| Page article (§3.3) : l'appel à l'abonnement en fin d'article s'affiche-t-il aussi pour un abonné actif ? | Non : seulement pour un lecteur qui a lu le texte complet sans être abonné (acheteur du numéro, accès découverte) ; le non-abonné a déjà le bloc du paywall | Pas de réglage (B-16) |
| Cookies (§3.14, §4.4) : le cookie de session posé pour retenir un code suivi (C-30) et ceux de l'attribution d'origine des commandes de WooCommerce demandent-ils un consentement, donc un bandeau ? À voir aussi avec le conseil juridique | Aucun bandeau construit ; les cookies sont inventoriés dans une liste fermée, affichée sur la page « Gestion des cookies », et un test refuse tout cookie hors liste | Pas de réglage pour l'instant ; le choix de l'outil de consentement n'est pas fait (C-32) |
| Comptes de la rédaction (§3.3, §4.4) : un journaliste a-t-il une page publique d'auteur, avec la liste de ses articles ? | Non : la signature est un texte sans lien, et le site ne montre aucun compte à un visiteur (archives d'auteur, interface REST, plan du site, flux) | Pas de réglage (B-16, C-33) |
| Comptes (§4.4) : un abonné connecté, qui n'a pas le droit de lister les utilisateurs, voit-il les comptes du site (archives d'auteur, interface REST), ou est-il traité comme un visiteur ? | Le lot livré ferme ces voies au visiteur anonyme, comme le brief l'écrit ; rien n'est changé pour un compte connecté. Défaut proposé par la relecture, non appliqué : traiter l'abonné connecté comme l'anonyme | Pas de réglage (C-33) |
| Cookies (§3.14, §4.4) : les sept cookies d'attribution d'origine de WooCommerce, posés dès la simple lecture d'une page, demandent-ils un consentement, et faut-il éteindre l'attribution ? À voir avec le conseil juridique | L'attribution reste activée, comme WooCommerce la livre ; l'écart avec « aucun cookie en simple lecture » est constaté et écrit, rien n'est éteint, aucun bandeau | Réglage natif de WooCommerce, laissé tel quel (C-32) |

Rappel de règle, sans question : un abonnement actif dans l'administration mais **sans paiement validé** ne figure pas dans la liste d'envoi.

Prioritaires : grille tarifaire (3), tarif solidaire (4), accès découverte (5). Tant qu'elles sont ouvertes, le tunnel ne peut pas être finalisé.

## Ouvert — chez Step (chapitre 8)

Points 1 à 4 : champs attendus par Odoo, liste d'envoi, email de facture. Ils conditionnent le document d'interface.
