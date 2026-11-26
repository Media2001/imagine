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
