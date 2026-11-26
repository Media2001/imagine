# Arbitrages du 26 novembre 2026

Arbitrages techniques pris par Claude pendant les passages automatiques. Ced peut défaire chacun d'eux. Aucun ne vaut accord pour toucher au réel.

# Passage automatique de 1 h 30

Lu : rapports du 25/11 à 23 h 34 au 26/11 à 0 h 56 (neuf), vérifications A-08, A-09, A-10, B-02, B-04 et C-15, fusions A-10 et B-04.

## A-08 — clos

Vérification : six instructions sur six, aucune régression. La question III.6 avait été tranchée à 22 h 30 ; Hermès l'a appliquée à 0 h 45. Contrôle fait pendant ce passage : `wp/outils/bascule/repetition.md` reçoit dix-huit lignes ajoutées, aucune retirée, toutes de la prose hors des blocs de commandes. C'était la preuve convenue. Les limites d'A-04 restent entières et **ce n'est pas un accord pour toucher au réel**.

## A-10 — clos

Vérification : sept instructions sur sept, vérificateur rejoué par le relecteur (204 assertions). Depuis, seuls le vérificateur du lot et un test ont changé (contrat du mode d'emploi partagé) : l'outil lui-même est celui qui a été vérifié. Lot en lecture seule, sans rien de visuel : clos sur preuves. Reclasser ou supprimer un code reste à Imagine.

## A-09 — une correction, pas une question pour Ced

Le vérificateur écrit « remonte à Ced » parce que la commande de vérification du lot échoue : le manifeste d'A-09 a épinglé `A-FAIRE.md`, qui change à chaque passage. Les trois corrections de code sont, elles, appliquées et prouvées. C'est une question d'empaquetage, donc technique : tranchée ici.

1. **Un manifeste de lot n'épingle que les fichiers du lot.** Jamais les fichiers d'orchestration (`A-FAIRE.md`, `A-FAIRE-2.md`, `ETAT.md`, `JOURNAL.md`, `docs/`, `briefs/`, `prompts/`), jamais ceux d'un autre lot. Raison : ces fichiers bougent sans que le lot change, et la vérification devient rouge sans cause.
2. Même remarque du vérificateur d'A-08, dont le manifeste photographie des fichiers d'A-09 : à restreindre de la même façon.
3. Un fichier **partagé** entre lots (le mode d'emploi de l'audit) se contrôle par contrat, comme A-10 vient de le faire (les lignes du lot sont présentes et exactes), pas par l'empreinte du fichier entier.

Correction mise en tête de la voie 1, après la quatrième passe d'A-01. Pas de rejeu Docker : la preuve est le vérificateur de chaque lot à code 0 sur l'arbre courant.

## A-11, A-12, A-13 — rendus, relecture attendue

- **A-11, refus des sites à configuration non standard.** Le rapport dit que l'outil refuse un site qui porte des fichiers de remplacement de WordPress (cache d'objets, cache de pages, pare-feu) ou des liens symboliques. Le site d'Imagine a Wordfence et un cache est probable : un refus sec rendrait l'outil inutilisable le jour venu, et A-12 et les lots suivants réemploient ce chemin. À défaut : on ne baisse pas le confinement, mais le refus nomme le fichier en cause et le mode d'emploi dit quoi faire ; Hermès dit dans son prochain rapport ce qui se passe exactement sur un site qui en porte, avec un test. À traiter avec les corrections d'A-11.
- **A-12, lanceur confiné obligatoire** plutôt que le PHP brut, et réemploi du chemin en lecture seule d'A-11 à la place d'une analyse statique : confirmés, c'est le plus simple et le plus sûr.
- **A-13** : correspondance des colonnes en configuration, séparateur douteux refusé, compte sans email compté et jamais rejeté, tous les membres d'un doublon signalés. Confirmés. Le contrôle d'échéance ne décide pas d'un futur import.

## B-02 — code clos, validation visuelle de Ced attendue

Vérification : dix instructions sur dix, cœur des règles isolé en code pur. Les cinq réserves du rejeu strict (marge, compteur et historique, documents, profil virement sans circuit natif, édition d'adresse) sont des emplacements nommés ou des questions déjà rangées, pas des défauts.

## B-04 — code clos, une question visuelle pour Ced

Vérification : instructions 1 à 6 appliquées. La septième est conditionnelle : **garde-t-on une étiquette d'accès sur le kiosque ?** C'est du visuel, donc à Ced ; le rendu actuel est conservé en attendant. Défaut proposé par la fusion : la retirer (§3.3 : couverture, titre, date). Je ne tranche pas.

Le correctif de 0 h 45 sur le jeu de test de B-04 (il cherchait le thème à un chemin absent du banc) : accepté, le test est inchangé et la suite complète est verte (1 040 tests).

## C-15 — code clos, validation visuelle de Ced attendue

Vérification : huit instructions sur huit. Réserve du vérificateur : il n'a pas pu rejouer les tests lui-même. La suite complète a été rejouée depuis par Hermès à 0 h 45 (1 040 tests, les règles de C-15 comprises). Proportion : accepté pour un écran sur données fictives.

## C-16 — rendu, relecture attendue

- Création du compte et de la commande différée à la confirmation, brouillon privé d'une heure, pas de double création au rejeu : confirmés.
- Un seul marqueur « sans email » pour tout le site, celui de C-13, désormais posé aussi par le jeu de profils : confirmé. Deux marqueurs pour la même chose seraient une source d'écarts.
- Un nouveau compte sans email n'a aucun droit tant qu'aucun paiement n'est validé : c'est la décision d'accès existante, rien de neuf.

## Profil A-PAPIER — action planifiée annulée

Constat de la voie 2 : l'abonnement fictif du profil A-PAPIER n'a plus d'action de renouvellement planifiée. Elle a été annulée le 25/11 à 21 h 38, pendant les corrections de C-15, qui faisaient passer ce profil par plusieurs états puis le restauraient. Hermès a refusé de la recréer en inventant une échéance : c'était le bon réflexe.

Tranché : rejouer le jeu de profils de C-09 pour ce profil, qui fixe lui-même son calendrier. Rien n'est inventé, c'est un site fictif. Et règle pour la suite : un lot qui fait changer d'état un profil de C-09 le remet dans son état de départ, **action planifiée comprise**, et le relit.

## Files

- **Voie 1.** La quatrième passe d'A-01 reste en tête (session de Ced, 1 h 20). Derrière elle : la correction des manifestes, puis deux lots dans l'ordre du §4.3 et du §3.8, tous deux en lecture seule : A-14 (rapprochement d'un export de contacts de la newsletter, sur fichier fictif ; n'appelle pas Brevo, ne réinscrit personne) et A-15 (inventaire des emails que le site envoie ; aucun texte, aucune adresse). Un inventaire des abonnements a été écarté : l'audit (A-02) le fait déjà.
- **Voie 2.** C-17 est en cours, C-18 en file. Ajoutés : C-19 (tableau de bord, §3.13 ; quatre indicateurs que les données permettent, les autres grisés, aucune formule inventée), C-20 (« ne pas renouveler » dans Mon compte, §3.7 ; sans email ni rétractation ; en quatre fois, l'effet est en fin de bloc, décision du 22/11), C-21 (export et effacement des données d'un compte par les outils natifs, §4.4 ; aucun réglage de conservation modifié).
- Écartés pour l'instant, parce qu'ils demanderaient d'inventer : le formulaire de personnalisation (questions non arrêtées), la rétractation en ligne (modalités chez le conseil juridique d'Imagine), l'agenda et la billetterie (licence), l'appel à renouvellement des abonnés hors ligne (email et lien de paiement).

# Passage automatique de 4 h

Lu : quatorze rapports du 26/11, de 1 h 26 à 4 h 11 ; vérifications A-01 (n° 6), A-08 (n° 2 et 3), A-09 (n° 2), A-10 (n° 2), A-11, A-12, A-13, B-04 (n° 2) ; fusions A-11, A-12, A-13, C-16, C-17, C-18. Aucun arbitrage ci-dessous ne vaut accord pour toucher au réel.

## A-01, quatrième passe — close

Vérification n° 6 : « prêt pour la clôture », les cinq tâches du brief appliquées, aucune question pour Ced, suite complète verte. Plus aucun refus muet ; un mode qui répète la base seule (`--diagnose-database`) sans restaurer les fichiers. Limites dites par Hermès et gardées telles quelles : MySQL 8 non exécuté (variantes dérivées), vues, déclencheurs et procédures refusés en les nommant, pas de reprise sur une copie non anonymisée. Le site `imagine-test-a01-ced-02` est laissé intact : Hermès ne peut pas prouver qu'il est vide sans lire la copie, c'est donc à Ced de le supprimer. **Clore ce lot n'est pas un accord d'import** : le diagnostic et l'import réels restent des commandes de Ced.

## A-09 — clos. A-08 — reste clos

Les deux manifestes n'épinglent plus que les fichiers de leur lot ; `verifier.py` à code 0 pour chacun, confirmé par le vérificateur (A-08 n° 3, A-09 n° 2). Aucun code n'a changé.

## A-10 — son ancien contrôle d'empaquetage

Hermès signale que le vieux vérificateur de réception d'A-10 est rouge sur `README_APPENDIX` : il compare la fin du mode d'emploi partagé à un texte figé, or chaque lot suivant y ajoute ses deux lignes. Même cause que pour A-09, même règle : un fichier partagé se contrôle par contrat (les deux lignes du lot sont présentes et exactes), pas par sa fin ni par son empreinte. Correction d'empaquetage mise en file, sans toucher à l'outil ni à ses preuves. A-10 reste clos.

## A-11 — clos

Vérification : quatre instructions sur quatre, paquet lié au code corrigé. Le vérificateur écrit « prêt pour la validation de Ced » ; il n'y a rien de visuel ni de réel dans ce lot en lecture seule, donc clôture sur preuves (doctrine §6). Le point demandé à 1 h 30 est traité : un site qui porte un cache d'objets, un cache de pages, un pare-feu en fichier de remplacement ou un lien symbolique est refusé **en nommant le fichier**, avant toute exécution, et le mode d'emploi dit quoi faire. Conséquence à connaître : sur le site réel, qui a Wordfence, l'inventaire se fera sur la copie de staging une fois ces fichiers écartés par l'opérateur, jamais en les désactivant sur la source. Réserve : la suite native n'a pas été rejouée par le vérificateur (pas de Docker dans sa session).

## A-12 — clos, une ligne de mode d'emploi à aligner

Vérification : B1 (dossier de sortie disjoint du site, dans les deux sens) et I1 (taxonomies hors articles : indisponible plutôt qu'inventé) réglés et prouvés. Reste l'instruction 3, de pure rédaction : la ligne « Liaisons » du mode d'emploi décrit des clés « contenant » un mot alors que le code reconnaît un jeton délimité suivi de `_id` ou `_ids`. Aucun effet sur le comportement : lot clos, ligne à corriger au passage, sans nouvelle vérification.

## A-13 — pas une question pour Ced : retour à Hermès

Le vérificateur écrit « remonte à Ced » et demande s'il faut renvoyer le lot ou l'accepter tel quel. C'est une question de test, donc technique. Tranché : **renvoi**, correctif ciblé. Raison : la suite du lot échoue sur le poste de contrôle (Windows, cp1252) alors que la livraison affirme « 40 tests, 0 échec » ; une preuve qui ne se rejoue pas sur le poste de Ced n'est pas une preuve. Les corrections IBAN et doublons sont, elles, conformes et restent acquises. À faire : le test fixe lui-même son environnement d'encodage, comme la fusion le demandait ; la modification de l'outil qui n'était pas demandée est retirée si elle ne sert à rien, sinon justifiée par un test ; les deux mineurs 4 et 5 ; la phrase du rappel 6. Règle ajoutée pour la voie 1 : un lot en Python dit avec quelle version et quel encodage sa suite a tourné, et la suite doit passer avec l'encodage de console de Windows.

Question métier rangée (`docs/decisions.md`) : deux personnes de même nom à la même adresse sont-elles un doublon ? Défaut : oui, signalées toutes les deux, rien n'est fusionné.

## A-14, A-15 — rendus, relecture attendue

Décisions à défaut confirmées : A-14 ne choisit jamais entre deux comptes de même email (anomalie signalée), garde tels quels les statuts désinscrit, bloqué et inconnu ; A-15 ne rend aucun texte, refuse l'éditeur d'emails en blocs qu'il ne sait pas lire, et dit que les emails des services extérieurs lui échappent.

## C-16 — corrigé, vérification attendue

Les huit instructions de la fusion sont rendues à 3 h 57 (double création sous concurrence fermée par un verrou, preuve rouge puis verte). Question métier rangée : l'adresse de livraison saisie est-elle enregistrée sur le compte **créé** par ce parcours ? Défaut : oui, sur le seul nouveau compte, jamais sur un compte existant ; réglage oui ou non dans C-10.

## C-17 — à corriger, et le brief s'aligne sur le cahier des charges

Fusion de 4 h 08 : aucun bloquant, trois importants (remplacement d'une pièce non récupérable si l'écriture échoue, contrôle de B-02 cassé par le nouveau libellé, pièce orpheline à la suppression du compte). Corrections en tête de la voie 2.

La fusion pose une question « pour Ced » : que conserve-t-on après la décision ? Mon brief disait cinq champs (catégorie, décision, date de la décision, date de fin, opérateur) ; le §4.4 dit « le site ne conserve que la catégorie et la date de fin ». Ce n'est pas une règle à inventer : le cahier des charges est la référence (décision du 11/11) et c'est mon brief qui s'en écartait. Tranché, sur un site fictif, à défaire si Ced préfère : **le dossier de l'abonné ne garde que la catégorie, la date de fin et l'état** (l'état est nécessaire au « statut » que §3.7 affiche dans Mon compte) ; la date de la décision et le nom de l'opérateur vont dans le journal de l'administration, qui existe déjà (C-10), pas dans la fiche de la personne. Écart reporté dans `docs/ecarts.md`. Ce que fait le journal de ces lignes à l'effacement d'un compte est une question de C-21, pas de ce lot.

La capacité « traiter les justificatifs », donnée seulement par le jeu de démonstration : laissée telle quelle, à déclarer au branchement réel.

## C-18 — à corriger. C-19 — rendu, relecture attendue

Fusion de C-18 arrivée à 4 h 18 : aucun bloquant, un important (le filtre par état s'appuie sur le libellé traduit au lieu de la clé d'état), trois mineurs. Corrections en tête de la voie 2, avec celles de C-17. Décisions à défaut confirmées : une ligne par abonnement, pas d'âge ni d'étiquette inventés, le journal ne garde que qui, quand, quelle extraction et combien de lignes. Deux questions métier rangées (`docs/decisions.md`) : une ligne par abonnement ou par abonné ; filtre de localité exact ou par préfixe. L'écran reste à voir par Ced. C-19 : chaque indicateur porte la phrase qui dit comment il est compté ; « créations » compte les abonnements créés, pas les seuls payés, et la phrase le dit.

## C-20 — arrêt justifié, interdiction du brief levée sur un point

Hermès s'est arrêté comme le brief le demandait : sur les profils essayés, l'annulation en fin de période de Subscriptions ferme l'accès tout de suite et retire la prochaine échéance du paiement en quatre fois. Il n'a rien contourné. Lecture du constat :

1. **L'accès qui se ferme n'est pas le fait du standard, c'est notre raccord.** Quand un abonnement passe en annulation à terme, Memberships met l'adhésion dans l'état « en attente d'annulation » (`pending`). Notre raccord de démonstration (`imagine-site/Paywall.php`, lot C-08, voie 2) lit cet état comme « virement non validé ». C'est une confusion du raccord, pas de la bibliothèque C-06, qui ne connaît que l'état qu'on lui donne. Or le cahier des charges dit : « L'abonné désactive le renouvellement depuis son compte. L'abonnement va alors à son terme » (§3.4). Le brief interdisait de toucher à C-06 et à C-13 ; **cette interdiction vise les règles, pas le raccord** : levée pour le raccord seul. Une adhésion « en attente d'annulation » liée à un abonnement en annulation à terme se lit « actif jusqu'à la date de fin ». La bibliothèque C-06 et les règles pures de C-13 ne changent pas ; le profil A-VIR (première commande par virement non reçue) doit rester fermé, avec un test.
2. **Paiement en quatre fois : pas d'annulation à terme.** Elle arrête l'abonnement à la prochaine échéance, donc au milieu du bloc de quatre numéros, ce que la décision du 22/11 exclut. Pour ce cas, « ne pas renouveler » pose la **date de fin native de l'abonnement à la fin du bloc en cours** : l'abonnement reste actif, ses échéances restent planifiées par Subscriptions lui-même, et il expire seul. Aucun ordonnanceur à nous, aucune date réécrite en dehors de cette date de fin. « Reprendre » retire la date de fin. À prouver d'abord par la même sonde avec retour arrière ; si le standard ne garde pas les échéances du bloc, le quatre-fois reste sans bouton, avec une phrase, et Hermès le dit.
3. **La reprise** est refusée par le standard sur les profils de démonstration : Hermès lit la raison dans le code installé et la dit. On ne force pas un changement d'état que le standard refuse.

Deuxième passe : `briefs/C-20-ne-pas-renouveler-2.md`.

## Files

- **Voie 1**, arrêtée file vide à 3 h 55. En tête : le correctif d'A-13, puis deux retouches d'empaquetage et de rédaction (A-10, A-12). Ensuite deux lots en lecture seule, dans l'ordre du §4.3 et du §4.4 : A-16 (état des lieux des dix derniers numéros : ce qui est rattaché à chaque numéro et ce qui manque, sans rien rattacher) et A-17 (état des lieux de la sécurité des comptes de l'administration : des comptes par rôle et des oui ou non, aucun nom).
- **Voie 2.** En tête : corrections de C-17 et de C-18, puis la deuxième passe de C-20, puis C-21. Ajoutés : B-05 (partenaires : bloc « partenaire du mois », page « Nos partenaires », étiquette « Partenariat », liens déclarés commerciaux, §3.12) et C-22 (centre de préférences des newsletters dans Mon compte, §3.10 ; les choix sont gardés sur le site, rien ne part vers Brevo).
- Toujours écartés, parce qu'ils demanderaient d'inventer ou de sortir du fictif : tunnel et emails (grille tarifaire), formulaire de personnalisation, rétractation, agenda et billetterie (licence), appel à renouvellement des abonnés hors ligne, carte des points de vente (pas de base, et un fond de carte est un service extérieur), don et prise de parts.

# Passage automatique de 7 h

Lu : rapports de 4 h 45 à 6 h 46 (dix-sept), vérifications A-07, A-12 (n° 2), A-13 (n° 2), A-14, A-15, C-16, C-17, C-18 et C-19, fusions A-14, A-15, A-16, A-17 et C-19, livraison partielle de C-20.

## A-13, A-14, A-15 — clos

A-13 : vérification n° 2 « prêt pour la clôture ». Le test fixe lui-même l'encodage de son sous-processus ; 46 tests verts sous Python 3.14 en UTF-8 et en cp1252. La garde de console de l'outil est gardée parce qu'un test la justifie (sans elle, une console ASCII échoue) : accepté. A-14 et A-15 : fusions « à corriger » sans bloquant, corrections appliquées et vérifiées. Les vérificateurs écrivent « prêt pour la validation de Ced » ; ces trois lots lisent seulement, n'ont rien de visuel et ne touchent à rien de réel : clôture sur preuves (doctrine §6). Réserve gardée : la suite native d'A-14 et d'A-15 n'a été rejouée par aucun relecteur (pas de Docker dans leur session) ; les preuves sont celles d'Hermès, liées au code par empreintes.

La remarque « suite générale rouge sur `TableauBordReglesTest` » des fusions d'A-14 et d'A-15 est levée : c'était C-19 en cours ; la suite est verte depuis (1 088 puis 1 093 tests, rejouée aussi par le vérificateur de C-16).

Question métier rangée (`docs/decisions.md`) : dans le rapprochement des contacts de la newsletter, un abonné qui a désactivé le renouvellement mais dont la période payée court encore compte-t-il comme abonné ? Défaut de la fusion gardé : non, seul l'état actif compte. À noter pour Imagine : le paywall, lui, garde l'accès jusqu'au terme (§3.4) ; les deux lectures devront être accordées.

## A-07, A-10, A-12 — retouches faites, lots toujours clos

A-12 : la ligne « Liaisons » du mode d'emploi décrit le code (vérification n° 2). A-10 : son contrôle de réception ne juge plus que ses deux lignes et ses preuves ; code 0 en UTF-8 et en cp1252. A-07 : Hermès a retrouvé une fusion plus récente que son `PRET` (règle de 4 h 30) et appliqué sept retouches de rédaction ; vérifié. Le document se lit comme un constat du 20/11 annoté, pas comme un contrôle réseau refait : rien n'a été rejoué, c'est dit. Le coup d'œil à la box et le port 7000 restent à Ced (déjà dans `ETAT.md`).

## A-16 — à corriger

Fusion de 6 h 48, arrivée après l'arrêt de la voie 1 : aucun bloquant, deux importants. Corrections en tête de la voie 1, défauts de la fusion confirmés :

- un refus ne recopie jamais un chemin tiré du site (un lien symbolique peut porter un titre ou un nom) : code de refus fixe, détails limités à une liste fermée ;
- la présence du PDF et son emplacement public se calculent séparément ; « présent mais hors du dossier public » est une réponse, pas un arrêt de tout l'inventaire ;
- l'ordre des propriétés de la correspondance ne compte pas ; deux cas limites ajoutés au banc ; une ligne morte retirée.

## A-17 — à corriger, et une question qui n'en est pas une pour Ced

Fusion de 7 h 03 : un bloquant (le même chemin de refus que pour A-16 : un lien symbolique au nom porteur d'identité sort sur la sortie d'erreur), trois importants. Corrections en tête de la voie 1.

La fusion demande à Ced si l'outil tourne avant ou après l'anonymisation. La doctrine répond déjà (§3) : un agent ne travaille que sur la copie anonymisée, jamais avant. Reste le point technique : l'import retire les mots de passe d'application, donc leur compte vaut zéro après import, et mon brief avait tort d'écrire que « les nombres restent justes ». Tranché au plus simple et au plus prudent :

- **on ne touche pas à l'import** (A-01, clos, et que Ced s'apprête à lancer sur l'archive réelle) : pas de compteur ajouté à l'anonymisation ;
- quand la copie porte la marque de la neutralisation, A-17 répond **« inconnu après neutralisation »** pour ce compte, jamais zéro ; un test le prouve sur un jeu fictif qui est passé par la neutralisation ;
- le mode d'emploi le dit en une phrase. Si Ced veut ce nombre pour le site réel, ce sera une lecture à faire par lui sur la source, hors des agents : noté dans `ETAT.md`, sans urgence.

Les autres défauts de la fusion sont confirmés : la liste des capacités de gestion est complétée (`edit_users`, `update_plugins`, `switch_themes`), le préfixe `manage_` reste inclusif (on signale trop plutôt que pas assez) ; une constante de configuration placée sous une condition se lit « inconnu » ; la bascule du 29 février est documentée telle quelle.

**Règle ajoutée pour la voie 1** (elle vaut pour A-11, A-12 et A-14 à A-17, qui passent par le chemin de refus d'A-11) : aucune sortie, y compris la sortie d'erreur, ne recopie un chemin ou un nom tiré du contenu du site. Seuls sortent un code de refus et des noms pris dans une liste fermée écrite dans le code. Cela précise l'arbitrage de 4 h sur A-11, qui acceptait le refus « en nommant le fichier » : il reste vrai pour les fichiers de remplacement (cache, pare-feu : noms techniques, liste fermée), il ne l'est plus pour un lien symbolique, dont le nom vient du site ; le refus dit alors qu'il y a un lien symbolique et le mode d'emploi donne à l'opérateur la commande pour les lister lui-même. Raison : la fusion d'A-17 montre qu'un tel nom peut porter une identité. Correction faite une fois, au point commun, avec un test au canari par outil ; les lots clos le restent.

## C-16, C-17, C-18 — code clos, validation visuelle de Ced attendue

C-16 : huit instructions vérifiées, le bloquant de double création fermé à la racine et reprouvé. C-17 : quatre instructions vérifiées, plus la cinquième (trois champs conservés après la décision, date et opérateur au journal de l'administration). Le vérificateur renvoie ce dernier point à Ced : il est déjà tranché depuis 4 h sur le cahier des charges (§4.4), signalé à Ced dans `ETAT.md` et défaisable ; il ne retient pas la clôture du code. C-18 : trois instructions vérifiées, le filtre s'appuie sur la clé d'état. Réserve commune : les preuves faites sur le site de démonstration sont celles d'Hermès, les relecteurs n'ayant pas accès au site.

## C-19 — code clos, deux questions rangées

Quatre corrections techniques vérifiées (un seul instant de référence, libellés portés par chaque indicateur). Le reçu ne fige plus l'empreinte du mode d'emploi partagé mais contrôle sa section : même règle que pour A-09 et A-10, accepté.

- **Q-1, le droit d'ouvrir le tableau de bord.** La fusion proposait un droit à part, donnable seul ; il faudrait écrire dans les rôles du jeu de profils. Qui, chez Imagine, peut voir ces nombres sans avoir les extractions ni les échéances est une question d'organisation : métier, pas technique. Défaut prudent, donc le plus fermé : **on garde la composition actuelle** (il faut les deux droits), aucun rôle modifié. Question rangée pour Imagine. Le mot « dédié » du brief était de trop : écart noté.
- **Q-2, « par mode » et « par moyen » de paiement** (§3.13) : le brief n'avait gardé qu'un axe. Ligne grisée « à venir » sans chiffre, comme la fusion le proposait ; question rangée, écart noté.

## C-20 — périmètre réduit, à rendre tel quel

Deuxième passe livrée en partie, sans `PRET`. Lecture point par point :

1. **Le raccord est corrigé** : une adhésion « en attente d'annulation » liée à un abonnement en annulation à terme se lit active jusqu'à la date de fin ; les autres cas restent fermés. C'était le défaut réel. Acquis.
2. **La liste d'envoi : mon critère était faux.** Je demandais que la liste du prochain numéro reste « la même ». Sur le profil essayé, le terme payé tombe le 25/12/2026 et la liste du prochain numéro se clôt le 05/01/2027 : l'abonné qui ne renouvelle pas n'y figure plus, et c'est ce que disent les règles de C-13, que personne n'a changées. Hermès a eu raison de ne pas forcer un droit postal. Savoir si un abonné qui ne renouvelle pas reçoit encore le numéro suivant son terme est une question pour Imagine (rangée) ; défaut : les règles actuelles, donc non.
3. **Paiement en quatre fois** : la date de fin native n'a pas pu être essayée, parce que la marge de l'échéancier (réglage de C-05) n'a pas de valeur et qu'Hermès a refusé d'en choisir une. Bon réflexe. On ne fixe pas cette marge pour les besoins d'une preuve : le quatre-fois reste **sans bouton, avec la phrase « faites la demande auprès d'Imagine »**. La piste de la date de fin native n'est ni prouvée ni écartée.
4. **La reprise** est refusée par le standard parce que les produits de la démonstration sont privés : limite des données fictives, pas de bouton.

Reste le bouton lui-même. Sur la démonstration, aucun abonnement n'est en renouvellement automatique : il n'y a pas de passerelle, et on n'en fabrique pas. Un bouton « ne pas renouveler » n'y aurait donc aucun profil honnête. Tranché, au plus simple : **C-20 se rend dans son état actuel** (raccord corrigé, écrans sans bouton qui disent la vérité de chaque profil). Le bouton, sa confirmation et la preuve du quatre-fois passent au lot de branchement, sur le staging vérifié avec Stripe en mode test, donc après un accord de Ced. §3.4 n'est pas encore tenu sur ce point : écart noté, ligne ajoutée dans « En attente ».

## Files

- **Voie 1**, arrêtée file vide à 6 h 30. En tête : corrections d'A-17 (un bloquant) puis d'A-16, avec le contrôle du chemin de refus sur A-11 à A-15. Ensuite deux lots en lecture seule, sur banc fictif, dans l'ordre du §4.4 et du §4.3 : A-18 (ce que le site garde qu'il ne devrait pas garder : traces de données de paiement, fichiers d'abonnés dans le dossier des médias ; des comptes par clé et par dossier, aucune valeur) et A-19 (cohérence des abonnements et des adhésions avant la mise à niveau : combien d'abonnements sans adhésion, d'adhésions sans abonnement, de renouvellements automatiques sans moyen de paiement ; des comptes seulement).
- **Voie 2** : C-21 en cours. En tête, un quart d'heure : déposer `PRET` sur C-20 tel quel. Puis C-21, B-05, C-22, déjà en file : plus d'un lot d'avance, aucun brief ajouté.

# Passage automatique de 10 h

Lu : les rapports de 7 h 32 à 10 h 05, les vérifications d'A-16, d'A-17 et de C-20, les fusions d'A-18, d'A-19, de B-05, de C-20 et de C-21. Aucun accord donné sur le réel.

## A-17 — clos

Vérification du second tour : les neuf instructions appliquées, 42 assertions, 66 contrôles natifs et 60 refus au canari verts, reçus liés au code courant. Le vérificateur laisse deux points « pour Ced » qui n'en sont pas : la copie avant ou après anonymisation est tranchée depuis 7 h (après, la doctrine le dit) ; le rejeu des paquets d'A-11, A-12, A-14 et A-15 après le changement du point commun est déjà fait par Hermès (rapport de 8 h 09 : 300, 132, 63 et 84 contrôles verts, manifestes rescellés). Ces lots restent clos.

## A-16 — le refus nomme le champ, jamais sa valeur

Les cinq instructions sont appliquées et vertes. Le vérificateur renvoie à Ced une seule question : le refus d'une correspondance qui désigne une clé absente ne nomme plus cette clé, alors que le brief l'exigeait. C'est un choix de code, pas une question pour Ced. Hermès a appliqué ma règle de 7 h (« code seul ») plus largement que je ne l'avais écrite ; le brief et la règle se contredisaient, la faute est dans mes textes.

Tranché : **le refus nomme le champ de la correspondance qui est en cause** (`numero_type`, `thematique`, `pdf_cle`, `liaison.cle` : quatre noms écrits dans le code, liste fermée), **pas la valeur que l'opérateur y a mise**. Raison : l'opérateur a son fichier sous les yeux, le nom du champ lui suffit pour trouver sa faute, ce que voulait le brief ; et la règle du chemin de refus garde une seule forme, sans exception à expliquer : rien de libre ne sort, seulement un code et des noms d'une liste fermée. Une retouche d'un quart d'heure, un test, `PRET` redéposé ; le lot se clôt à la vérification suivante. Écart de brief noté.

## A-18 — à corriger ; le oui ou non du brief était impossible

Fusion de 9 h 43, arrivée après l'arrêt de la voie 1 : trois importants, tous des oublis de détection (le magasin de commandes inactif n'est pas lu ; une suite de chiffres voisine masque une carte ou un numéro de registre valide ; un IBAN coupé par deux espaces ou un retour à la ligne n'est pas vu). Confirmés : un inventaire de ce qu'on ne devrait pas garder qui répond « rien » à tort manque son but. Corrections en tête de la voie 1.

- **Règles du serveur.** Mon brief demandait à la fois de n'ouvrir aucun fichier et de dire si une règle du serveur interdit la lecture : impossible. Le défaut d'Hermès est le bon et il est acquis : l'outil dit si un fichier de règles est présent, et répond « inconnu » sur l'interdiction. Écart de brief noté.
- **La marque de la neutralisation.** La fusion range pour Imagine la question « cette marque est-elle posée exactement quand l'import neutralise ? ». Ce n'est pas une question pour Imagine : c'est notre import. On garde la marque telle quelle, parce qu'elle penche du côté d'« inconnu » ; rien à porter à Imagine.
- Le double comptage d'un nombre de onze chiffres qui passe les deux contrôles (carte et registre) reste, documenté.

## A-19 — à corriger, un bloquant

Fusion de 9 h 53, après l'arrêt : la commande écrite dans le mode d'emploi est refusée par le lanceur, qui exige une date que le mode d'emploi dit facultative. Le parcours nominal échoue ; aucun test ne le lançait tel qu'il est écrit. Correction en tête de la voie 1.

- **Règle ajoutée pour la voie 1** : un test lance la commande du mode d'emploi avec les seuls arguments que sa ligne donne. C'est le deuxième lot où le défaut se cache derrière un banc qui passe toujours tous les arguments.
- **Instruction 3 de la fusion** (faire entrer les tests purs d'A-19 dans la commande de rejeu) : pas dans A-19. La réserve vaut pour tous les outils depuis A-10 ; elle se traite une fois, dans un lot d'outillage, T-02, sans toucher à l'isolation de T-01.
- Le compte « schéma de passerelle inconnu », séparé de « moyen de paiement absent », reste : il évite de déclarer absent ce qu'on ne sait pas lire. Question rangée pour Imagine, défaut : garder les deux.

## C-20 — code clos, en périmètre réduit

Vérification de 10 h 13 : les cinq instructions de la fusion appliquées, le raccord du paywall couvert par un test sur le vrai adaptateur (sept bornes), suite rejouée par le vérificateur lui-même (1 114 tests). Code clos, validation visuelle de Ced attendue. La clôture ne dit pas « §3.4 fait » : le bouton, sa confirmation et la preuve du quatre-fois restent au branchement sur le staging vérifié. Deux points notés pour ce branchement, sans décision aujourd'hui : l'ordre entre « arrêt à terme » et « quatre fois », et la lecture du mode de paiement d'un vrai mandat papier.

## C-21 — corrigé, vérification attendue ; les trois questions de la fusion

La fusion de 9 h 13 a trouvé ce qu'une relecture avait manqué : l'export d'un opérateur contenait le nom et l'adresse du client dont il avait préparé la commande (bloquant), et l'effacement d'un payeur ou d'un membre détruisait ou suspendait les données d'autres personnes. Hermès a rendu les sept corrections à 10 h 05. Pas de clôture avant la vérification.

Les trois questions que la fusion adresse à Ced ne touchent ni au visuel ni au réel :

- **un membre d'un groupe s'efface, les autres continuent-ils d'être servis ? L'offrant d'un cadeau s'efface, le bénéficiaire garde-t-il son adresse et son numéro ?** Le brief répondait déjà : l'effacement préserve les tiers. Le défaut appliqué (oui aux deux) est donc la règle du lot, pas un choix nouveau. Ce que l'administration d'Imagine veut faire ensuite d'un groupe sans souscripteur est une question d'organisation : rangée pour Imagine, rien n'attend ;
- **le libellé du mode de paiement dans l'archive native d'une commande** : on garde le masquage large. Raison : en cas de doute sur une donnée de paiement, on montre moins.

## B-05 — à corriger

Fusion de 10 h 13 : deux importants. Un lien sortant mal formé (un espace en tête, des barres en trop) échappe à la déclaration « lien commercial » ; et le contrôle « les articles de l'accueil ne sont pas déclarés commerciaux » visait le titre de la section au lieu de sa liste, il passait donc à vide. Corrections en tête de la voie 2. Défauts techniques confirmés : dans le contenu d'un partenaire, un lien douteux est déclaré commercial plutôt qu'oublié ; les liens internes vers la fiche d'un partenaire ne le sont pas.

## C-22 — rendu, relecture attendue

Une question rangée pour Imagine : l'inscription à la newsletter principale à la création du compte, et avec quel consentement. Défaut : aucune, tant que le lecteur ne coche pas lui-même.

## Files

- **Voie 1**, arrêtée file vide à 9 h 13. En tête : A-19 (bloquant), A-18, la retouche d'A-16. Puis trois lots : T-02 (la commande de rejeu joue aussi les tests purs des outils), A-20 (ce que paient aujourd'hui les abonnés en ligne : par produit, rythme, montant, pays ; pour la décision d'Imagine sur la grille, §3.4) et A-21 (les portes vers l'extérieur : clés d'interface et envois automatiques de WooCommerce, comptés, §4.4).
- **Voie 2**, sans lot devant elle à 10 h 05. En tête : B-05. Puis deux lots : C-23 (le test d'étanchéité de livraison, une commande pour toutes les voies et tous les publics, §4.4) et B-06 (l'espace coopérateurs et l'attribut posé par l'administration, §3.12, sans rien attendre de CoopHub).

# Passage automatique de 13 h

Lu : les rapports de 11 h 29 et 12 h 15 (voie 1), les vérifications d'A-16, d'A-18, d'A-19 et de C-21, les fusions d'A-20, d'A-21 et de C-22, les deux relectures de T-02. Aucun rapport de la voie 2 depuis 10 h 05. Aucun accord donné sur le réel.

## A-16, A-18, A-19 — clos

- **A-16** : la retouche est faite comme arbitré à 10 h (le refus nomme le champ, liste fermée de quatre noms, jamais la valeur ; un test par champ). Le vérificateur note que deux autres champs de la correspondance (`article_type`, `date_cle`) sortent en code seul : c'est la lettre de l'arbitrage, on ne rouvre pas le lot pour cela. Si l'outil est retouché un jour, la liste passera à six.
- **A-18** : sept instructions appliquées. La septième corrige la fusion : un même nombre ne peut pas être compté à la fois comme carte (treize chiffres au moins) et comme numéro de registre (onze exactement) ; le mode d'emploi dit seulement de ne pas additionner les colonnes. Acquis.
- **A-19** : quatre instructions appliquées ; la commande du mode d'emploi passe sans date, les neuf règles pures entrent dans la commande de rejeu (portées par T-02).
- Réserve commune aux trois, déjà acceptée pour les lots précédents : les relecteurs ne rejouent pas la matrice native (pas de Docker avec les extensions sous licence) ; ils contrôlent le paquet, lié au code par empreintes, et rejouent la suite pure (1 123 tests).

## C-21 — code clos

Sept corrections et deux décisions techniques vérifiées, suite rejouée par le vérificateur. Les trois « questions pour Ced » de la vérification sont celles tranchées à 10 h (les tiers sont préservés, masquage large) : rien de nouveau. Validation visuelle de Ced attendue.

## A-20 et A-21 — à corriger, et le défaut dépasse ces deux lots

Les deux fusions retiennent le même bloquant, vu par un seul des deux relecteurs : le lanceur passe la main à PHP sans surveiller ses flux. Une extension du site qui écrit directement sur la sortie ou la sortie d'erreur, qui s'arrête pendant le chargement, ou qui imprime en fin de processus, contourne le tampon. La règle « aucune sortie ne recopie un nom ou un chemin du site » n'est donc pas démontrée.

- **Un seul gardien, pas deux.** Les corrections d'A-20 et d'A-21 demandent chacune un superviseur des flux. Il est écrit une fois, à un endroit commun, et les deux lots l'utilisent. Raison : c'est le même défaut, et deux copies divergeraient.
- **Les outils clos ont le même lanceur** (A-12, A-15 à A-19 au moins ; à vérifier pour A-02, A-03, A-10, A-11). On ne rouvre pas ces lots un par un : un lot transversal, A-22, les fait passer par le gardien commun, et le rejeu de leur suite existante suffit, comme pour la correction commune d'A-17 à 7 h. Aucun de ces outils n'a tourné sur une copie du site réel.
- **Conséquence pour le réel, sans décision de ma part** : les inventaires ne devraient pas être lancés sur la copie de staging d'Imagine avant qu'A-22 soit clos. Écrit pour Ced dans `ETAT.md`.
- Défauts techniques des fusions, confirmés : A-20 garde le compte « sans ligne de produit » et « annuel » vaut un an ou douze mois ; A-21 garde les comptes d'inactivité séparés, lit l'option directement pour le magasin d'extensions et corrige son mode d'emploi pour le dire, classe un hôte en adresse IP par comparaison de chaînes avec un test ; son vérificateur scelle aussi les dépendances. Le rejeu natif après correction est fait par Hermès, les relecteurs contrôlent le paquet.

## C-22 — à corriger

Fusion de 10 h 33, arrivée après la mise à jour de la file : deux importants, un mineur. Les trois instructions comme la fusion les écrit.

- **Identifiant de lettre réutilisé** : un identifiant déjà employé, même retiré, est réservé et refusé. Raison : c'est une donnée de consentement, un avertissement d'écran ne suffit pas.
- **Vérificateur du lot** : il contrôle le résultat (la préférence sort à l'export et disparaît à l'effacement), pas l'écriture d'un fichier partagé.
- **Injection de la section dans l'écran de C-10** : on garde le mécanisme, avec un test de présence de la section.
- **Place de la section, sous le bouton « Enregistrer »** : question visuelle, pour Ced. Laissée en place.

## T-02 — relu, fusion attendue

Une relecture dit conforme, l'autre à corriger (un reçu qui porterait à la fois l'ancien et le nouveau format pourrait masquer un contrôle rouge). Pas de clôture avant la fusion. Si elle dit « à corriger », elle passe en tête de la voie 1.

## Files

- **Voie 1**, arrêtée file vide à 12 h 15 ; les fusions d'A-20 et d'A-21 sont arrivées à 12 h 53 et 13 h 08. En tête : A-20 et A-21 (avec le gardien commun). Puis deux lots : A-22 (le gardien pour tous les outils d'inventaire) et A-23 (les comptes des abonnés : familles d'empreintes de mots de passe, adresses vides ou en double, comptés, pour la promesse du §4.3 « identifiant et mot de passe conservés sauf impossibilité »).
- **Voie 2**, silencieuse depuis 10 h 05 alors que sa file a du travail depuis 10 h 30. Je ne peux pas savoir pourquoi d'ici ; signalé à Ced. File inchangée sur le fond : B-05, puis C-22 (corrections), C-23, B-06. Pas de nouveau brief : elle a plus d'un lot devant elle.

# Passage automatique de 16 h

Lu : les rapports de 14 h 43, 15 h 20 et 16 h 19 (voie 2), les vérifications de B-05 et de C-22, la fusion de T-02, les notes de production de T-02, A-20, A-21, A-22, A-23 et C-23. Aucun rapport de la voie 1 depuis 12 h 15, mais son travail est dans le dépôt. Aucun accord donné sur le réel.

## B-05 — code clos

- Sept instructions appliquées et vérifiées. Seuls les liens internes certains échappent à la déclaration commerciale ; toute destination douteuse la reçoit : c'est le défaut demandé.
- L'écart d'empreinte du fichier d'amorçage partagé est requalifié et non « réparé » : B-05 ne contrôle que son propre bloc, par contrat. Conforme à la règle des fichiers partagés.
- Réserve du vérificateur, acceptée comme pour les lots précédents : il n'a rejoué ni Docker ni la démonstration (droits de sa session) ; il a rejoué le vérificateur hors réseau, qui lie les reçus au code relu.
- La distinction graphique de l'étiquette « Partenariat » n'est pas une question de code : au designer.

## C-22 — code clos

- Trois instructions appliquées et vérifiées. Un identifiant de lettre déjà employé est réservé, y compris quand le compte qui le portait est effacé : la réserve ne contient aucune donnée personnelle.
- Le vérificateur du lot contrôle désormais le comportement de l'export et de l'effacement, plus l'écriture d'un fichier partagé ; deux mutations témoins.
- Un reçu rouge intermédiaire est conservé à côté du rejeu vert (un sélecteur de test périmé) : accepté, rien n'est rebaptisé.
- La question visuelle (section sous le bouton « Enregistrer ») reste à Ced ; la question du consentement à la création du compte est déjà rangée pour Imagine.

## C-23 — rendu, relecture attendue

- Pas d'arbitrage avant la relecture. Trois choses notées pour elle : la préparation des sessions hors de la commande visiteur est le bon découpage (la commande certifiée ne fait que lire) ; la récupération après le délai dépassé ne prouve pas l'état octet pour octet des anciennes sessions, Hermès le dit, et ce sont des personnages fictifs ; le script de récupération ne fait pas partie du rejeu.
- Plans de site fermés sur la démonstration : le test vérifie leur fermeture. Le jour où ils s'ouvrent (référenceur), les quatre lignes de la matrice devront chercher les témoins. À rappeler dans le lot qui les ouvrira.
- B-06 ajoutera ses pages à la matrice : le test de livraison suit ce qu'on construit.

## T-02 — corrigé, les trois défauts techniques de la fusion confirmés

- Le harnais de tests reste dans l'espace global, en entier ; un alignement sur `Imagine\` serait une reprise à part, pas un correctif de T-02. Raison : c'est de l'outillage jetable en conteneur, pas du code livré.
- La découverte se limite aux `unit.php` : c'est le périmètre du brief.
- Aucun levier de mutation dans `rejouer.ps1` : le cas rouge se prouve par le paquet. Raison : ne pas élargir la seule commande que les relecteurs ont le droit de lancer.

## A-20, A-21, A-22, A-23 — ordre des `PRET`

- T-02 se rend sans attendre A-22. A-20, A-21 et A-22 se rendent ensemble, sur les mêmes sources : ils partagent le gardien. A-23 ensuite, rejoué si le gardien a bougé. Raison : un `PRET` posé sur un outil avant que le gardien soit figé serait à refaire.
- A-22, `error_log` vers le périphérique de rejet avec le seul droit d'écriture correspondant : accepté en principe (ce qui est jeté ne sort pas, et un journal natif de planification ne doit pas rendre l'outil inutilisable), à condition que le mode d'emploi le dise et qu'un test prouve qu'aucun autre chemin n'est inscriptible. Les relecteurs jugeront.
- A-22, les refus historiques des lots clos gardent leurs codes : confirmé.
- A-02 et A-10 ne chargent pas le WordPress du site (lecture par requêtes seules) : hors du gardien, leurs suites sont rejouées quand même. Acquis.

## Files

- **Voie 1** : A-22 en cours, A-23 construit. Deux lots de plus : A-24 (adresses d'expédition des abonnements vivants, §3.13) et A-25 (ce que le site garde sur ses visiteurs, §4.4).
- **Voie 2** : B-06 en cours. Deux lots de plus : C-24 (formulaire de personnalisation, §3.7 et §3.10 ; les questions sont un réglage puisqu'elles ne sont pas arrêtées) et B-07 (agenda, §3.11, sans billetterie : la licence n'est pas confirmée).


# Passage automatique de 19 h

Lu : le rapport de 17 h 06 (voie 1), ceux de 17 h 33, 18 h 18 et 19 h (voie 2), les vérifications de T-02, A-20 et A-21, les fusions d'A-22, de C-23 et de B-06, les notes de production d'A-22 (corrections de 17 h 53), A-23, A-24, A-25, C-23 et C-24. Aucun accord donné sur le réel.

## T-02 — clos

- Trois corrections appliquées et vérifiées : un reçu mixte est refusé avant toute lecture, les empreintes internes des reçus sont recalculées, le décompte est celui du dernier rejeu (14 outils, 279 contrôles). Le harnais reste dans l'espace global : c'est le défaut arbitré à 16 h.
- Réserve du vérificateur, acceptée comme pour les lots précédents : il n'a pas relancé les suites (droits de sa session) ; il a recalculé les empreintes et croisé avec les portes du parent de 17 h 06, vertes en UTF-8 et en cp1252.

## A-20 et A-21 — corrections vérifiées, clôture avec A-22

- Les deux vérifications de 17 h 38 disent « prêt » : le bloquant commun est corrigé (gardien extérieur au processus, liste fermée, publication après validation), les canaris demandés et douze de plus sont joués.
- Je ne les inscris pas en « clos » à ce passage. Raison : le gardien commun a changé après ces vérifications (corrections d'A-22 de 17 h 53), Hermès a retiré lui-même leurs `PRET` et refait leurs paquets sur le gardien final. Un lot ne se clôt pas sur une vérification antérieure à son dernier code.
- Pas de troisième tour pour autant : la vérification d'A-22 contrôlera, dans le même mouvement, que les vérificateurs d'A-20 et d'A-21 passent sur le gardien final (111 et 49 contrôles) et que rien d'autre n'a bougé dans leurs dossiers depuis 17 h 38. Si c'est le cas, les trois se closent ensemble.
- Les deux ajouts hors instructions d'A-21 (gardien partagé, blocage des quatre pré-filtres du planificateur) : acceptés, ils vont dans le sens de « aucun appel sortant ».

## A-22 — à corriger, six instructions ; les défauts de la fusion confirmés

- Verdict de fusion retenu : à corriger. Trois constats importants, dont un qui touche la promesse du lot : un rapport `.md` ou `.csv` pouvait être altéré en fin de processus puis publié sans contrôle de contenu. Les quatre canaris du brief ne visaient que les flux : c'est un manque du brief, reporté aux écarts.
- Défauts techniques de la fusion confirmés : le rattachement à §4.4 et §2.5 est analogique et se dit dans les notes ; chaque outil garde ses codes de refus historiques exacts, plutôt qu'un code commun (un lot clos ne change pas de contrat) ; la duplication de l'enclos de sortie et l'absence de code de délai dédié pour A-20 restent en dette, sans reprise dans ce lot.
- **Règle étendue : le canari par canal compte désormais un cinquième canal, le fichier de rapport.** Un outil qui charge le WordPress du site prouve qu'un rapport altéré en fin de processus n'est pas publié. Vaut pour A-23, A-24, A-25 et la suite.
- Instruction 6 (revalidation indépendante du paquet natif) : aucun relecteur ne peut lancer Docker depuis sa session, c'est acquis depuis plusieurs lots. Ce qui vaut revalidation : les portes du parent rejouées après le gel des sources (préparation de l'image, rejeu global dans les deux encodages, vérificateurs d'A-20, A-21 et A-22), puis, par le vérificateur, le rejeu de `rejouer.ps1` et des vérificateurs de paquet, qui tournent sans Docker et lient les reçus au code relu. Raison : exiger d'un relecteur ce que sa session interdit bloquerait le lot sans rien prouver de plus. La réserve reste écrite dans la clôture.
- Hermès dit les six instructions appliquées à 18 h 56, sans `PRET` : restent ses portes communes. Rien à arbitrer de plus avant la vérification.
- Mon avis à Ced ne change pas : les outils d'inventaire ne se lancent pas sur une copie du réel tant qu'A-22 n'est pas clos.

## A-23, A-24, A-25 — construits, sans `PRET`

- Les trois sont construits et verts chez Hermès, en attente de ses portes communes. Ils se rendent après A-22, chacun rejoué si le gardien a changé depuis son paquet (A-24 cite l'empreinte du gardien qu'il a utilisé : la comparer suffit).
- A-24, le résultat utile : sur une copie neutralisée, presque tous les nombres sur les adresses valent « inconnu », parce que l'import efface les champs d'adresse sauf le pays. C'était prévu par le brief et c'est un résultat. L'état réel des adresses ne peut donc se lire que sur la source, hors agents : c'est une décision de Ced, portée dans `ETAT.md`. L'import n'est pas modifié.

## B-06 — à corriger, cinq instructions

- Verdict de fusion retenu. Les deux règles de rôle (qui pose le statut, qui lit l'espace sans l'avoir) deviennent deux réglages, défaut « Administrateur seul » : c'est la doctrine, une règle ouverte est un réglage. Deux lignes rangées pour Imagine.
- Lecture du journal en échec : dans le doute sur la complétude d'un export ou d'un effacement, on déclare incomplet, jamais complet. Confirmé.
- La collection REST n'a pas de fuite (elle est filtrée par le même mécanisme que la recherche) ; il manque sa preuve. Confirmé.
- La règle pure du lot entre dans la suite que les relecteurs peuvent rejouer. Confirmé : c'est le sens de T-01 et de T-02.
- Présentation de la date du statut (date brute en temps universel) : question visuelle, pour Ced, à poser quand le lot sera code clos. Elle reste telle quelle.

## C-23 — corrigé, et un blocage que je lève

- Les six instructions sont appliquées : témoins cherchés dans la réponse brute (attributs et commentaires compris), corps des redirections inspectés, plus aucun réglage forcé au rejeu normal. Les pages de B-06 sont dans la matrice (503 contrôles, aucune fuite).
- Le blocage : le réglage de découverte livré est « fermé, sans numéro » (c'est le défaut voulu de C-12). Le personnage « découverte épuisée » ne peut donc pas être préparé, et le test normal refuse de tourner. L'instruction 3 de la fusion, suivie à la lettre, rend le test impossible sur l'état livré : ce n'était pas son intention.
- **Tranché : une découverte fermée n'est pas un prérequis manquant, c'est l'état livré, et il se teste tel quel.** Quand la découverte est fermée, la ligne « découverte épuisée » de la matrice devient « découverte fermée à la livraison » : le personnage `V-DEC-FIN` est contrôlé comme un compte sans droit, voie par voie, et le reçu dit en une ligne que le cas « épuisé » n'a pas été joué et pourquoi. Le test normal tourne alors sans rien forcer et rend son oui ou son non.
- Le cas « découverte ouverte puis épuisée » se prouve à part, dans une recette nommée qui ouvre la découverte sur la démonstration, joue le cas, puis remet le réglage exactement, comme la mutation témoin. Elle ne fait pas partie de la commande jouée à chaque livraison ; son reçu accompagne le paquet. Raison : §4.4 demande la preuve sur l'état livré, et le brief demande le public « découverte épuisée » ; les deux se tiennent ainsi sans qu'aucun réglage soit réécrit par le rejeu normal.
- Le jour où Imagine arrête l'accès découverte et où le réglage livré s'ouvre, la ligne reprend son sens premier d'elle-même : le test lit le réglage, il ne le suppose pas. Reporté aux écarts.
- `PRET` à redéposer après un rejeu normal vert sous un nom de reçu neuf.

## C-24 — construit, un blocage de proportion que je lève

- Le lot est construit (64 contrôles, 7 mutations détectées). Hermès s'est arrêté parce que la photographie de départ de son premier parcours a été perdue : l'état métier est revenu exactement (rôles, commandes, adhésions, profils, réglages, actions), mais il ne peut plus prouver, octet pour octet, d'anciennes sessions de personnages fictifs, une option-verrou du planificateur et des caches.
- **Tranché : sur la démonstration, « remis en état » veut dire l'état métier.** Sessions, données temporaires, caches et verrous du planificateur n'en font pas partie : ils se recréent seuls et ne portent aucune règle. L'écart est écrit une fois dans les notes du lot, puis le lot se rend. Raison : c'est un site fictif, et la consigne de proportion interdit d'exiger des preuves lourdes dessus. S'arrêter et le dire était le bon réflexe ; refaire tourner des restaurations pour un verrou de planificateur ne le serait pas.
- Reste à faire, une fois : rejouer le harnais corrigé (photographie écrite avant toute session) sous un nom de reçu neuf, qualifier les deux mutations en attente, puis `PRET`.
- La localité en texte libre ou en choix fermés : question métier, rangée pour Imagine, défaut « choix fermés » (un texte libre partirait tel quel comme étiquette).
- La section « Questions de personnalisation » est sous le bouton « Enregistrer », comme celle de C-22 : même question visuelle pour Ced, une seule réponse vaudra pour les deux.

## Files

- **Voie 1** : portes et `PRET` d'A-20, A-21, A-22, puis A-23, A-24, A-25. Deux lots de plus : A-26 (ce que le site charge chez des tiers : mesure, pixels, contenus intégrés, comptés ; §4.4) et A-27 (les moyens de paiement enregistrés, par passerelle et par type, comptés ; §4.3, §3.6).
- **Voie 2** : corrections de B-06, fin de C-23, fin de C-24, puis B-07. Deux lots de plus : C-25 (rétractation en ligne en deux étapes, §3.7 : une demande enregistrée, aucun effet automatique, délai et point de départ en réglages) et B-08 (« Soutenir » et « Notre coopérative », §3.12 : pages vides aux intitulés du cahier des charges, don éteint, prise de parts par lien).

# Passage automatique de 22 h

Lu : le rapport de 19 h 21 (voie 1), ceux de 19 h 44, 20 h 01, 20 h 27, 21 h 07 et 21 h 58 (voie 2), les vérifications d'A-20, A-21, A-22, T-02, B-06 et C-23, les fusions d'A-23, A-24, A-25, C-24 et B-07, les notes de correction d'A-23, A-24 et A-25, la réception d'A-27. Aucun accord donné sur le réel.

## A-20 et A-21 — clos

- Chacun a reçu sa propre vérification après le gel des sources de 19 h 21 : code du lot inchangé depuis 17 h 38, seuls le gardien commun et la liste des dépendances ont bougé, paquet refait sur le gardien final, canal « fichier » couvert (25 contrôles de canaux, dont quatre sur le fichier). Les deux vérificateurs ont rejoué `rejouer.ps1` : 1 126 tests, 0 échec. Verdict : prêt pour la clôture.
- À 19 h j'avais lié leur clôture à celle d'A-22, pour une raison précise : leur vérification était antérieure à leur dernier code. Cette raison est tombée, je les clos sans attendre A-22. Si le gardien change encore, le circuit les revérifie de lui-même.
- Réserve écrite, la même que pour les lots précédents : la matrice native (classique et HPOS, conteneur) n'a été rejouée que par Hermès.

## A-22 — corrections vérifiées, pas clos : il manque une preuve indépendante

- Les cinq instructions de code sont appliquées et le vérificateur a rejoué lui-même 25 tests Python verts (codes de refus historiques, empreintes d'A-03, contenu des rapports, cinquième canari). Rien n'est à corriger.
- Son verdict n'est pas « prêt » : il remonte que l'instruction 6 n'a été exécutée par personne d'indépendant. À 19 h j'avais écrit ce qui vaut revalidation : les portes du parent après le gel, puis, par le vérificateur, `rejouer.ps1` et le vérificateur de paquet. État : portes du parent faites à 19 h 21 ; `rejouer.ps1` rejoué au vert sur ces sources par trois vérificateurs (T-02, A-20, A-21) ; **le vérificateur de paquet d'A-22 n'a été lancé par aucun relecteur** (sa session refuse une commande avec argument ; celui d'A-21 a eu le même refus).
- Je ne clos pas sur un critère que j'ai posé et qui n'est pas rempli, et je ne l'assouplis pas pour ce lot-là : c'est le gardien de tous les outils d'inventaire. J'ai tenté le vérificateur depuis une copie du dépôt : il refuse, parce que les journaux du paquet (`*.log`) ne sont pas versionnés ; il ne se rejoue donc que sur le NUC.
- Deux façons de lever le point, toutes deux à Ced : lancer une fois la commande (une minute, sans Docker), ou l'ajouter aux commandes autorisées des relecteurs. Je n'élargis pas moi-même une permission sur sa machine. Écrit dans `ETAT.md`.
- Rien n'attend derrière : Hermès continue, et aucun outil ne tourne sur le réel.

## T-02 — reste clos

- Vérification complémentaire : aucun code touché depuis la clôture, seuls les pointeurs de preuve ont suivi les portes de 19 h 21. Le décompte passe à 16 outils et 311 contrôles parce que la découverte automatique a pris A-23, A-24 et A-25. Le vérificateur a cette fois rejoué la suite lui-même : la réserve de 19 h est levée.

## A-23, A-24, A-25 — à corriger, corrections faites, portes attendues

- Verdicts de fusion retenus. A-23 : l'exclusion des comptes de gestion suivait les capacités effectives, pas la règle d'A-17 que le mode d'emploi annonce ; alignement sur A-17, et refus fermé d'un rôle de gestion au nom non conforme. A-24 : « à la casse et aux espaces près » veut dire en les ignorant ; le code faisait l'inverse et le test gravait l'erreur ; ce n'est pas une question métier. A-25 : une table de messages dont `submission_id` est la clé primaire était écartée, donc sous-comptée ; dans le doute, « couverture indéterminée », jamais zéro.
- Défauts techniques des fusions confirmés : pour A-23, la neutralisation reste détectée par la marque de l'import (dépendance écrite) ; pour A-24, espacements retirés et casse repliée pour la seule comparaison, données brutes intactes, accents et ponctuation significatifs ; les erreurs Windows d'un relecteur sont traitées comme un prérequis d'environnement (dossier temporaire maîtrisé), écrit au mode d'emploi ; pour A-25, l'avertissement sur l'import est étiqueté « permanent, non mesuré sur la copie ».
- Hermès dit les trois séries appliquées, `PRET` retirés, anciens paquets gardés comme historiques : restent la matrice native et les portes du parent. Le bon réflexe est tenu : un ancien paquet vert ne qualifie pas un code corrigé.
- A-23, collisions comptées contre tous les comptes, administration comprise : question rangée pour Imagine, défaut « oui ».

## A-25 — l'alerte sur l'import : exacte, plus étroite qu'elle n'en a l'air, et à fermer

- Ce qui est prouvé : sur le banc, avec la décision `garder` posée sur une table de messages, les messages restent en clair après neutralisation et anonymisation. Les tables inconnues ne reçoivent aucune transformation automatique.
- Ce que j'ai relu : la politique du parcours que Ced lance (`wp/outils/staging-court/politique-tables.json`) vide par défaut toute table hors catalogue. Une table de messages n'y survit donc que si un fichier de décisions dit `garder`.
- Ce qui n'est pas prouvé : le sort des messages rangés ailleurs que dans une table à eux (certaines extensions les rangent comme des contenus, dans la table des articles).
- Tranché : la doctrine veut qu'un agent n'entre que sur une copie anonymisée et vérifiée ; un message de formulaire est un texte libre écrit par un visiteur, il ne s'anonymise pas colonne par colonne, il se vide. Lot A-28 : le prouver par le vrai parcours, sur archives fictives, puis faire refuser par l'étape de vérification une copie où il en reste. A-01 reste clos pour tout le reste ; les commandes de Ced ne changent pas.
- En attendant, une consigne simple pour Ced, dans `ETAT.md` : ne jamais écrire `garder` sur une table de formulaires.

## B-06 — code clos

- Cinq instructions appliquées et testées : deux réglages de rôle distincts (64 combinaisons, aucune n'ouvre un article), lecture du journal en échec déclarée incomplète, règle pure dans la suite rejouable, source et date affichées seulement si le statut est posé, collection REST contrôlée avec sa mutation.
- Réserve du vérificateur (il n'a pas pu rejouer la suite) : levée de fait, le relecteur de C-24 a rejoué ensuite toute la suite, règle de B-06 comprise (1 128 tests, 0 échec).
- Sa seconde remarque (le commit mêle d'autres lots) tient à la synchronisation commune, pas au lot : la clôture ne vaut que pour les fichiers de B-06.
- Reste à Ced : la validation visuelle, et la présentation de la date du statut (brute, en temps universel).

## C-23 — code clos sur son périmètre ; la couverture des pages coopérateurs passe en relecture avec C-26

- Les six instructions sont appliquées, le vérificateur a lancé lui-même le vérificateur de paquet (74 contrôles) : livraison normale sans fuite sur la découverte fermée, mutation rouge, cas « épuisé » prouvé à part et réglage remis.
- Il remonte un point de méthode, pas un défaut : la couverture des pages de B-06 (environ 400 lignes, 503 contrôles) est entrée pendant le tour de correction, sans les deux relectures. C'est une question de preuve, donc à moi.
- Tranché : le lot se clôt sur ce qui a été relu deux fois et vérifié. La couverture des pages coopérateurs reste en place (elle va dans le sens du brief et elle est verte), mais **elle ne compte pas comme prouvée** tant qu'elle n'a pas ses deux relectures : elles viendront avec C-26, qui étend le test aux sorties ajoutées depuis et nomme ces fichiers dans son périmètre. Raison : c'est le choix prudent du vérificateur, sans relecture hors circuit ni lot bloqué.
- Dépendance dure à `TMPDIR` dans un test : à corriger dans C-26.

## C-24 — à corriger, corrections faites, vérification attendue

- Verdict de fusion retenu. Deux importants, dans des chemins sans test : la restauration après un échec du journal ne restaurait rien (elle repassait l'ancien état par un validateur qui le refusait) ; une inscription à la newsletter créée par défaut valait « inscrit » pour la transmission. Hermès dit les cinq instructions appliquées à 21 h 58, `PRET` redéposé.
- Défaut technique confirmé : seule une inscription choisie par le lecteur ouvre la transmission ; une origine par défaut ou inconnue la ferme. La lecture de « inscrit à au moins une newsletter » est rangée pour Imagine.

## B-07 — rendu, à corriger

- Verdict de fusion retenu, huit instructions, aucun bloquant : un lien saisi dans le texte d'un événement partenaire doit être déclaré commercial (règle de B-05) ; le balisage part du texte affiché, pas du texte brut ; un export qui échoue à lire ne se déclare pas complet ; l'adaptateur a une preuve rejouable hors du site.
- Pas de garde contre les inscriptions en masse sur la démonstration : confirmé, le brief demande une inscription simple. À reprendre avant toute ouverture au public ; reporté aux écarts.

## Style PSR-12 du code de la voie 2 — dette écrite, pas de reprise maintenant

- Deux fusions (C-24, B-07) relèvent des instructions condensées sur une ligne dans `imagine-site` et le thème. La doctrine demande PSR-12 : la règle reste, et les outils de la voie 1 la contrôlent déjà.
- On ne reformate ni lot par lot, ni maintenant : un passage d'ensemble changerait l'empreinte de tous les fichiers des lots code clos qui attendent l'œil de Ced, et périmerait leurs reçus. Un seul passage mécanique, sans changement de comportement, au gel du code avant la préproduction.

## Files

- **Voie 1** : matrices et portes d'A-23, A-24, A-25 ; fin d'A-26 et d'A-27. Deux lots de plus : A-28 (les messages de formulaires ne survivent pas à l'import ; doctrine §3) et A-29 (ce que le site fait tout seul : tâches planifiées, comptées ; §4.3, pour choisir le moment de la bascule).
- **Voie 2** : corrections de B-07, puis C-25 et B-08. Un lot de plus : C-26 (le test d'étanchéité suit les sorties ajoutées depuis C-23, et met en relecture la couverture des pages coopérateurs ; §4.4).
