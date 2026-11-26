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

Rappel de règle, sans question : un abonnement actif dans l'administration mais **sans paiement validé** ne figure pas dans la liste d'envoi.

Prioritaires : grille tarifaire (3), tarif solidaire (4), accès découverte (5). Tant qu'elles sont ouvertes, le tunnel ne peut pas être finalisé.

## Ouvert — chez Step (chapitre 8)

Points 1 à 4 : champs attendus par Odoo, liste d'envoi, email de facture. Ils conditionnent le document d'interface.
