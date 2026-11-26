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
