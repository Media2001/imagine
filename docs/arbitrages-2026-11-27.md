# Arbitrages du 27 novembre 2026

Tenu par Claude. Une ligne par question, avec la raison. Les questions métier ne sont pas tranchées ici : elles deviennent un réglage au défaut prudent et une ligne dans `docs/decisions.md`.

# Passage automatique de 1 h

Lu : les rapports de 22 h 56, 23 h 42, 0 h 53 et 1 h 02 (voie 1), ceux de 22 h 33, 23 h 16, 23 h 46 et 0 h 31 (voie 2), les vérifications d'A-23, A-24, A-25, B-07, C-24 et C-25, les fusions d'A-26, A-27, B-08 et C-25, les notes d'A-28 et la réception partielle d'A-29. Aucun accord donné sur le réel.

## B-07, C-24, C-25 — code clos

- **B-07 (agenda)** : huit instructions appliquées, six mutations de sources détectées, et l'adaptateur est entré dans la suite rejouable (1 135 tests, aucun outil hors rejeu). Le vérificateur n'a pas pu relancer la suite ; le relecteur d'A-24 l'a rejouée ensuite en entier (1 149 tests, 0 échec) : réserve levée de fait. Reste la validation visuelle de Ced.
- **C-24 (formulaire de personnalisation)** : cinq instructions appliquées, les deux défauts de fond prouvés corrigés par mutation, empreintes des sources identiques aux preuves ; le vérificateur a lancé lui-même le vérificateur hors réseau (318 contrôles). Reste la validation visuelle de Ced. Les deux questions métier étaient déjà rangées pour Imagine à 22 h.
- **C-25 (rétractation en ligne)** : quatre instructions appliquées, quinze mutations détectées, sources identiques octet pour octet au reçu de régression (1 151 tests). Le lot enregistre une demande et rien d'autre : aucun remboursement, aucune annulation, aucun accès fermé. Reste la validation visuelle de Ced. **La clôture du code ne dit rien du droit** : le délai, son point de départ et les effets d'une rétractation sont des réglages au défaut prudent et des questions pour Imagine et son conseil (cinq, dans `docs/decisions.md`).
- C-25, défaut technique de la fusion (un point d'accroche dédié dans l'écran de réglages au lieu de l'insertion actuelle) : **pas maintenant**. Trois lots insèrent désormais leur section sous le bouton « Enregistrer » (C-22, C-24, C-25) et la question de leur place est posée à Ced. On touchera l'écran de C-10 une seule fois, quand il aura répondu : la place et le point d'accroche dans le même lot. Raison : C-10 est code clos et attend son œil ; le modifier deux fois périmerait deux fois ses reçus.

## B-08 — à corriger, sept instructions

- Verdict de fusion retenu : deux importants, aucun bloquant. Une proposition contenant un antislash était refusée et perdue (les valeurs étaient déséchappées deux fois ; le bouchon de test ne reproduisait pas le comportement de WordPress et masquait le défaut) ; la création du menu ne pouvait pas être reprise après une interruption.
- Défaut technique confirmé : le lien de prise de parts n'accepte que `https`. Raison : c'est un lien sortant vers un service où l'on engage de l'argent ; rien à y gagner en `http`.
- **Le même défaut d'antislash est sorti dans C-25 une heure plus tôt**, masqué de la même façon. Règle ajoutée à la file de la voie 2 : un bouchon qui remplace une fonction d'écriture de WordPress reproduit son déséchappement, et tout champ de texte libre a un cas d'essai avec un antislash, du formulaire jusqu'à l'export.

## C-26 — rendu, en relecture

- `PRET` à 0 h 33 : 3 951 contrôles, aucune fuite, six familles de mutations détectées, le test n'exige plus `TMPDIR`, les fichiers de la couverture des pages coopérateurs sont nommés. Rien à trancher avant les deux relectures. La réserve posée à 22 h sur C-23 tient jusqu'à la clôture de C-26.

## A-28 — rendu, en relecture ; il a changé l'import, donc périmé sept paquets

- A-28 fait ce que le brief demande : les messages de la liste fermée sont vidés, un `garder` sur eux est refusé, l'étape de vérification refuse une copie où il en reste, les commandes de Ced sont identiques octet pour octet. Rien à trancher avant ses deux relectures.
- Conséquence, bien signalée par Hermès : deux fichiers de l'import ont changé et un troisième est apparu. Les vérificateurs de paquet d'A-21 à A-27 échouent sur l'empreinte de leurs dépendances (celui d'A-20 passe). Hermès n'a rescellé aucun ancien paquet : c'est le bon réflexe.
- **Question posée par la fusion d'A-26 à Ced (« resceller maintenant ou attendre que l'import soit stable ») : c'est une question de preuve, je la tranche.** Une seule requalification, sur l'import final. Ordre : la fusion d'A-28 d'abord ; si elle demande de toucher à l'import, ses corrections ; ensuite seulement les matrices d'A-21 à A-27 et d'A-29, puis leurs `PRET`. Les rejeux déjà faits cette nuit sur l'import courant (A-21 à 1 h 02) comptent si l'import ne change plus. Raison : rejouer sept matrices avant de savoir si l'import bouge encore, c'est risquer de les rejouer deux fois.
- **Un lot clos dont une dépendance change ne se rouvre pas pour autant.** A-21 reste clos : son code n'a pas changé. Son paquet est refait dans la requalification, le circuit le revérifie de lui-même sur le `PRET` redéposé, et il ne se rouvre que si sa matrice est rouge.
- **L'import est gelé après A-28** : plus aucun changement de `wp/outils/staging/` sans une consigne de la file. Un lot qui change un fichier commun le dit en tête de son rapport et livre la liste des paquets qu'il périme, comme A-28 l'a fait.
- La question d'A-28 (« supprimer aussi les contenus d'un type inconnu ? ») touche à ce qui reste d'une copie du réel : elle est à Ced. D'ici sa réponse, rien ne change : l'import garde ces contenus, parce que les contenus du magazine en font partie. Écrite dans `ETAT.md`.

## A-23, A-24, A-25 — corrections vérifiées, rien à corriger au code, clôture sur le paquet refait

- Les trois vérifications disent « prêt » : A-23 aligné sur la règle d'A-17 (les six comptes de gestion masqués sont exclus, classique et HPOS) ; A-24 compare sans la casse ni les espaces, données brutes intactes, rejeu autorisé relancé par le vérificateur (1 149 tests, A-24 : 27 contrôles) ; A-25 distingue une table d'entrées d'une table-fille et répond « couverture indéterminée » dans le doute.
- Je ne les clos pas ce passage, pour une seule raison : leurs vérifications datent d'avant A-28, et leur preuve de neutralisation passe par l'import, qui a changé depuis. C'est la règle appliquée à A-20 et A-21 à 19 h. Ils se closent au prochain passage sur leur paquet refait et la vérification complémentaire que le circuit lance de lui-même ; **code du lot inchangé, il n'y a rien à refaire au fond**.
- A-24 : le vérificateur demande de rafraîchir `RAPPORT.md` et le paragraphe « Portée » du mode d'emploi, qui décrivent encore l'état d'avant la qualification de 22 h 56. À faire avec le paquet refait. Même remarque, mineure, pour l'en-tête du mode d'emploi d'A-25.
- A-25 : son banc pose `garder` sur une table de messages et attend qu'ils restent ; A-28 refuse désormais ce `garder`. **Le banc d'A-25 s'adapte à A-28, pas l'inverse** : il attend la purge. Le code de l'outil ne change pas.
- A-23 : le chemin absolu de Python dans la commande d'exemple du mode d'emploi reste : c'est celui du poste de contrôle, et la règle du parcours du mode d'emploi veut une commande qui se lance telle quelle.

## A-26 — à corriger, trois instructions

- Verdict de fusion retenu. Le bloquant est le paquet périmé par A-28 (traité ci-dessus). L'important est réel : les adresses chargées chez des tiers étaient extraites du HTML par une expression régulière, qui s'arrête au premier `>` d'un attribut et lit un `src` à l'intérieur d'un titre ; un lecteur de balises natif de WordPress à la place, avec les deux contre-exemples en tests.
- Défauts techniques confirmés : une famille active dont on ne sait pas lire l'identifiant répond « illisible », jamais « non » ; `form-policy.json` entre dans le gel des dépendances.

## A-27 — à corriger, cinq instructions

- Verdict de fusion retenu. Bloquant : le même paquet périmé. Deux importants confirmés : un champ de paiement déclaré mais illisible était traité comme absent (cinq abonnements PayPal modernes pouvaient compter zéro) ; un lien explicite contredit par une référence donnait quand même un instrument. Dans les deux cas : « illisible », jamais un choix.
- Mineurs, laissés à la main d'Hermès comme la fusion le propose : le compte des cartes garde ses deux nombres de plus (complétude sans risque).
- « Dans les six mois » : la borne reste au jour de l'audit du sixième mois ; rangé pour Imagine.
- Le résultat « tout est inconnu sur une copie neutralisée » est un résultat, pas un défaut ; le comptage sur la source est une décision de Ced, déjà écrite dans `ETAT.md` pour A-24. Reporté aux écarts.

## A-29 — construit, preuve native attendue ; défauts confirmés

- Paquet partiel, Python seulement, sans `PRET` : honnête, rien n'y est compté comme natif.
- Défauts techniques confirmés : huit semaines glissantes en temps universel à partir de l'audit, sans extrapoler les occurrences futures ; l'historique des échecs ne vaut que pour la file de WooCommerce (WordPress n'en tient pas) ; une tâche inconnue n'est attribuée à aucune extension. Raison commune : ne rien affirmer qu'on ne lit pas.

## A-22 — toujours pas clos ; la commande demandée à Ced ne vaut plus

- Son paquet est périmé comme les autres (sa source de rejeu inclut l'import) : la commande d'une minute que j'avais demandée à Ced à 22 h échouerait aujourd'hui. Retirée d'`ETAT.md`.
- La cause de fond reste : aucun relecteur ne peut lancer un vérificateur de paquet. Lot T-03 : la commande de rejeu autorisée joue aussi les vérificateurs sans argument, dans le même conteneur isolé, sans commande nouvelle à autoriser. C'est la même nature que T-02. A-22 se clora sur ce rejeu indépendant ; à défaut, sur la commande de Ced, que je lui redonnerai quand le paquet sera refait.

## Files

- **Voie 1** : corrections de code d'A-26 et d'A-27, banc d'A-25, fin d'A-29 ; à l'arrivée de la fusion d'A-28, ses corrections puis une seule requalification. Deux lots de plus : T-03 (les vérificateurs de paquet rejoués par les relecteurs) et A-30 (l'import à blanc des abonnés hors ligne : ce que ferait l'import, en nombres, sans rien écrire ; §4.3).
- **Voie 2** : sa file était vide à 1 h 08, hors corrections de B-08. Trois lots de plus, dans l'ordre du §3.14 et du §3.7 : B-09 (FAQ, pages légales, contact), C-27 (« Comment nous avez-vous connus ? », après le paiement), B-10 (points de vente, sans fond de carte par défaut).
- « Tunnel et emails » reste en attente des décisions 3 à 5 d'Imagine : aucun de ces lots n'y touche.

# Passage automatique de 4 h

Lu : les rapports de 1 h 30, 1 h 45, 2 h 25, 2 h 52 et 3 h 52 (voie 1), les deux relectures et la fusion d'A-28, les deux relectures et la fusion de C-26, les notes et le `PRET` d'A-28 corrigé, les réceptions de T-03, d'A-29 et d'A-30. **Aucun rapport de la voie 2 depuis 0 h 31, et aucun fichier d'elle dans le dépôt depuis 0 h 33.** Aucune clôture ce passage. Aucun accord donné sur le réel.

## A-28 — à corriger, corrigé à 3 h 52, vérification attendue

- Verdict de fusion retenu : aucun bloquant, un important. L'étape de vérification comptait les messages de formulaires restants, mais pas leurs champs (`postmeta`) quand le message lui-même avait disparu : le filet avait un trou là où vit le texte du visiteur. Corrigé : les identifiants des messages connus sont relevés avant la purge, gardés hors du site et hors du rapport, et la vérification refuse s'il reste une ligne rattachée à l'un d'eux. Témoin demandé livré (purge des champs seule omise : refus ; contrôle retiré : accepté ; remis : refus), classique et HPOS.
- Défauts techniques de la fusion (instructions 4 et 5) : appliqués par Hermès, confirmés. L'exception reçoit la liste déjà chargée ; un `garder` posé sur une table de la liste est refusé avec le même code, que la table soit ou non dans l'archive. Raison : un seul code pour un seul refus.
- Deux tables de la liste (`fluentform_draft_submissions`, `ff_scheduled_actions`) sans phrase officielle citée : elles **restent dans la liste**, marquées « doute » dans `standard.md`, comme la fusion le permettait. Raison : dans le doute, vider une table de brouillons de formulaires sur une copie de travail est le choix prudent ; la retirer laisserait du texte de visiteur.
- **Ce que la correction a fait en plus, et que personne n'avait demandé : le fichier de l'import a été découpé en cinq** (`lib.php`, `engine.php`, `store.php`, `guard.php`, `form-decision-refused.php`) pour passer PSR-12 sans exclusion. Je ne le fais pas défaire. Raison : revenir en arrière serait un troisième changement de l'import dans la nuit ; Hermès livre une preuve d'équivalence des jetons, le différentiel hors formulaires rejoué, et les commandes de Ced identiques octet pour octet. Mais :
  - **A-28 ne se clôt que si sa vérification a regardé ce découpage** (équivalence, charge utile de l'import portant bien les cinq fichiers, commandes de Ced inchangées). Si elle dit « prêt » sans en parler, une vérification complémentaire sera demandée avant la clôture ;
  - règle étendue à la voie 1 : **une correction ne restructure pas un fichier commun**, et n'y fait entrer ni fonction ni mise en forme. Le style de l'import est une dette jusqu'au gel du code, comme pour la voie 2 ;
  - **l'import est gelé pour de bon** à l'état scellé par A-28 (empreintes dans `production/A-28/preuves/final/dependency-invalidations.json`), style compris.
- La question des contenus d'un type inconnu reste à Ced, inchangée (`ETAT.md`).

## La requalification — faite une fois trop tôt, à refaire une fois

- Les matrices d'A-21 à A-27 ont été rejouées au vert entre 1 h 30 et 2 h 25, avant l'arrivée de la fusion d'A-28 ; la correction d'A-28 a rechangé l'import à 3 h 27. Ces candidats sont périmés. Hermès ne les a pas scellés et ne les requalifie pas par un simple changement d'empreinte : c'est juste.
- Ordre maintenu, précisé : la requalification part **quand la vérification d'A-28 est arrivée**. « Prêt » : elle part tout de suite. « À corriger » en touchant à l'import : ses corrections d'abord. Si la vérification n'est pas là au réveil suivant, la requalification part quand même sur l'import gelé : elle comptera si l'import ne bouge plus. Raison : ne pas rester à l'arrêt plus d'une heure pour économiser une heure de matrices.
- Les corrections de code d'A-26 (lecteur de balises) et d'A-27 (« illisible », jamais « absent ») sont faites et ont passé leur matrice une fois ; leur `PRET` vient avec le paquet refait.
- A-23, A-24, A-25 : rien de changé au fond ; toujours « clôture sur le paquet refait ». A-25 : son banc attend maintenant le refus du `garder` et la purge, comme demandé.

## T-03 — candidat rendu, sans preuve native ; trois questions tranchées

- Honnête : contrats Python et doubles seulement, aucun nombre natif revendiqué, pas de `PRET`.
- **Les déclarations `rejeu.json` s'ajoutent pendant la requalification, lot par lot, avant le sceau** (A-21 à A-30). Raison : ajouter un fichier dans un paquet déjà scellé le périme.
- **Les lots clos avant A-21 ne reçoivent pas de déclaration** : ils sortent « hors rejeu : déclaration absente », nommés sur la ligne `PAQUETS`. Raison : leur ajouter un fichier périmerait des paquets clos pour rien ; ce n'est pas un échec.
- A-21 et A-22, dont le vérificateur exige un argument : un point d'entrée sans argument dans `production/<lot>/`, qui appelle le vérificateur existant sur l'unique paquet du lot. **Aucun contrôle n'est changé pour rendre la ligne verte.**
- T-01 et T-02 restent clos : T-03 change leur lanceur, il ne les rouvre pas (règle d'A-21). C'est le paquet de T-03 qui prouve que les anciennes frontières tiennent, en natif.
- Le montage de la racine du dépôt en lecture seule dans le conteneur isolé : accepté. Raison : rien de réel ni de secret n'est dans le dépôt (doctrine §3), le conteneur n'a ni réseau ni écriture. Il ne s'élargit jamais à un dossier parent.

## A-29 — bloqué en natif, pas de règle assouplie

- Sur la copie neutralisée, le processus finit en sortie 255 après avoir écrit un résultat de succès, sans message. Hermès n'a déclaré aucun succès : c'est juste. **Une sortie 255 n'est pas un succès, quel que soit le résultat écrit avant.**
- Le diagnostic se borne à un réveil, sur l'import gelé, sans retirer de canari ni de compteur. S'il n'aboutit pas : un rapport de dix lignes (ce qui est établi, ce qui ne l'est pas, les deux hypothèses) et le lot attend le passage suivant. Raison : A-29 ne bloque personne.

## A-30 — construit, natif attendu

- Paquet Python seulement, sans `PRET`. Défauts retenus : les trois règles laissées en option fermée (importer un abonné échu, résoudre un doublon, calculer la prochaine échéance) refusent la valeur « oui » au lieu de l'interpréter ; un courriel qui correspond à deux comptes refuse le passage. Trois questions rangées pour Imagine.
- Priorité entre les issues d'une même ligne (refus d'A-13, puis sans adresse, puis type à décider, puis rapprochement) : c'est un ordre de comptage, pas une règle métier ; confirmé. Raison : une ligne n'est comptée qu'une fois, et le motif le plus bloquant d'abord.
- Sur une copie neutralisée, « à créer » et « existant » ne se distinguent pas : « inconnu après neutralisation », pas une sixième issue. Confirmé, reporté aux écarts.

## C-26 — à corriger, un bloquant sur la preuve, aucune fuite constatée

- Verdict de fusion retenu, les dix instructions. Le bloquant : les sorties nouvelles (Soutenir, coopérative, agenda) étaient contrôlées contre une liste de témoins plus étroite que celle de C-23 ; « aucune fuite » y repose donc sur un contrôle incomplet. Ce n'est pas une fuite trouvée, c'est une étanchéité non prouvée.
- Les trois défauts techniques de la fusion (instructions 7 à 9) : confirmés.
- **Ordre** : les corrections de B-08 d'abord, celles de C-26 ensuite. Raison : C-26 contrôle les sorties de B-08 ; les prouver avant que B-08 ne change obligerait à les reprouver.
- Instruction 10 (rejeu de la suite par les relecteurs sous Python 3.11) : Hermès écrit dans `A-VOIR.md` la commande exacte, sans argument. Si les relecteurs ne peuvent toujours pas la lancer, ce n'est pas un motif de troisième tour : le constat s'écrit, et la clôture se fera sur les mutations et la relecture du code. Raison : proportion sur le site fictif.
- La réserve sur la couverture des pages coopérateurs de C-23 tient toujours.

## Voie 2 — à l'arrêt depuis 0 h 33

- Sa file est pleine depuis 1 h 30 (corrections de B-08, B-09, C-27, B-10) et rien n'en est sorti. Ce n'est pas un blocage que je peux lever par écrit : aucune question n'est posée, aucun rapport n'est déposé. Signalé à Ced en tête d'`ETAT.md`. Aucun brief de plus pour elle ce passage.

## Files

- **Voie 1** : T-03 (déclarations, image), la requalification à l'arrivée de la vérification d'A-28, A-29, A-30. Un lot de plus, qui ne dépend pas de l'issue d'A-28 pour être construit : **A-31, l'historique des commandes des abonnés, compté** (§4.3 : les abonnés en ligne gardent leur historique).
- **Voie 2** : corrections de B-08, puis de C-26, puis B-09, C-27, B-10.

# Passage automatique de 7 h

Lu : les rapports de 5 h 01 à 7 h 09 (les deux voies), la vérification d'A-28, les vérifications complémentaires d'A-21 à A-25, les vérifications d'A-26, A-27, B-08 et C-26, les deux relectures et la fusion de T-03, les deux relectures et la fusion d'A-30, la réception des corrections de T-03 et d'A-30, le rapport d'A-31, la note et l'`A-VOIR` de B-09. Aucun accord donné sur le réel.

## Clôtures

- **A-28 clos.** Sa vérification dit « prêt » : cinq instructions appliquées, les témoins des champs orphelins tournent réellement en PHP (82 contrôles, 62 avant). La condition posée à 4 h est tenue : la vérification a regardé le découpage du fichier de l'import (extractions sans changement de comportement, équivalence des jetons, différentiel hors formulaires préservé, aucune commande de Ced modifiée) ; et l'import découpé a ensuite été rejoué en vrai, sept fois, par les matrices d'A-21 à A-27 sur archives fictives. L'import n'a plus changé depuis 3 h 28. Ce n'est pas un accord d'import.
- **A-22 clos.** Son seul point ouvert était le rejeu indépendant de son vérificateur de paquet : un relecteur l'a lancé lui-même par la commande autorisée, au vert (`PAQUETS : 9 vérifiés, 0 échecs`). Raison de ne pas attendre le `PRET` de T-03 : le mécanisme a rendu un résultat indépendant et vert pour A-22, et les corrections de T-03 portent sur le temps et la mémoire du lanceur, pas sur ce que le vérificateur d'A-22 contrôle.
- **A-23, A-24, A-25 clos** : code inchangé depuis leur « prêt » du 26, paquet refait sur l'import gelé, vérification complémentaire « prêt », paquet revu au vert par le rejeu indépendant. **A-21 reste clos** (vérification n° 3).
- **B-08 code clos** : six instructions appliquées et vérifiées, la septième (colonne de liste) était facultative et n'est pas faite. Validation visuelle de Ced attendue.
- **C-26 code clos** : dix instructions appliquées, le bloquant sur la preuve levé (tous les témoins réservés, `/evenements/` dans la matrice, attendu des coopérateurs déduit des personnages). Les relecteurs n'ont toujours pas pu rejouer la suite Python ; comme écrit à 4 h, ce n'est pas un troisième tour : la clôture repose sur les huit mutations et la relecture du code. **La réserve sur la couverture des pages coopérateurs de C-23 est levée** : elle a maintenant ses relectures, par C-26.
- C-26 a modifié deux sources de test de C-23 sans resceller son paquet : accepté. C-23 reste clos, son paquet est de l'historique ; le test d'étanchéité vivant est celui de C-26. Raison : un seul test à jour vaut mieux que deux paquets à tenir.

## A-26 et A-27 — vérifiés « prêt », pas clos : leur paquet est redevenu rouge

- Vérifiés « prêt » à 5 h 58 et 6 h 03, sceaux verts. À 6 h 46, les corrections de T-03 ont changé six fichiers du lanceur de rejeu (`wp/tests/t01/`) que ces paquets gèlent : leur vérificateur refuse (`SEALED_VERIFICATION_FAILED`), et Hermès a retiré leur `PRET` plutôt que de changer une empreinte. C'est juste.
- Rien à corriger au fond. **Ils se closent sur leur paquet refait une fois, et sur une ligne `PAQUETS` verte lue par un relecteur** ; pas de nouveau tour de fond. Raison : le code n'a pas changé depuis la vérification.
- **Ordre, pour ne refaire qu'une fois** : les sources du lanceur ne bougent plus ; resceau d'A-26, A-27, A-30, A-31 sur ce lanceur ; puis la preuve finale de T-03 (dix paquets verts, un octet changé dans A-28 sur copie) et son `PRET`.
- **Règle : le lanceur de rejeu est gelé comme l'import**, dès maintenant (`wp/tests/t01/`, `wp/tests/rejouer.ps1`). Plus de changement sans une consigne de la file. Raison : c'est la troisième fois en deux jours qu'un changement d'un fichier commun périme des paquets vérifiés (le gardien le 26, l'import cette nuit, le lanceur ce matin).

## T-03 — à corriger, corrigé en candidat

- Verdict de fusion retenu : deux importants. Un paquet lent (C1) ou bavard (S1) pouvait faire échouer le bilan des tests d'une suite verte, par le temps ou par la mémoire. Corrigé : une échéance commune, la phase des paquets bornée au temps restant, les sorties plafonnées pendant la lecture, les processus descendants arrêtés. Tests réels, rouges avant, verts après.
- Défauts de la fusion confirmés : **A-20 reste hors rejeu**, nommé, et entre dans le rejeu par une consigne à part (ci-dessous) ; le montage de la racine en lecture seule reste tel quel ; les tests de contrat de T-03 ne s'ajoutent pas à la commande des relecteurs. Raison : aucun des trois ne touche à l'indépendance du bilan des tests.
- L'écart 582 / 584 contrôles : la preuve finale donnera le nombre réellement observé ; pas de valeur imposée.
- **A-20 dans le rejeu** : un point d'entrée sans argument et sa déclaration, joués avec le resceau. Si l'ajout périme le paquet d'A-20, il est refait par sa matrice réelle. Aucun contrôle changé. A-20 reste clos ; il ne se rouvre que si sa matrice est rouge (règle d'A-21).

## A-30 — à corriger, corrigé, paquet à refaire

- Verdict de fusion retenu : un important. La suite Python exigeait une variable `TMPDIR` que Windows ne définit pas : 22 tests sur 25 en erreur sur une session propre, et un sceau vert qui le masquait. Corrigé (dossier temporaire standard, refus s'il tombe dans le dépôt), rejoué 34 sur 34 en UTF-8 et en cp1252, la variable absente.
- Défauts de la fusion confirmés : dossier temporaire standard ; **l'axe produit garde sa clé `0`** pour les lignes sans produit reconnu. Raison : c'est ce que le brief demande (les axes comptent toutes les lignes du fichier contrôlé), et c'est documenté.
- « Repartir d'un arbre propre » (instruction 5) : pas de Git, pas de remise à zéro par Hermès. Il mesure les comptes obtenus et les écrit. Raison : un compte global qui bouge parce que l'autre voie livre n'est pas un défaut du lot ; la règle du 26 tient (un fichier partagé se contrôle par contrat, pas par son empreinte entière).
- **Règle pour toute suite Python de la voie 1 : elle passe sur une session Windows propre, sans `TMPDIR`**, et la matrice le prouve en retirant la variable aux processus fils.

## A-31 — construit, paquet à refaire, pas encore relu

- Rendu à 6 h 44 avec `PRET`, puis périmé par les corrections de T-03 comme A-26 et A-27 (`A31_PARENT_GATES_MISSING`). Resceau, `PRET`, première relecture.
- Règle d'A-19 reprise telle quelle pour « vivant », comme demandé. Sur une copie neutralisée, seule la répartition par nature vaut « inconnu » ; le reste se lit. Reporté aux écarts.

## A-29 — rien de nouveau

- Le réveil de diagnostic n'a pas eu lieu : la requalification, T-03, A-30 et A-31 sont passés avant. La consigne tient, après le resceau. A-29 ne bloque personne.

## Voie 2 — repartie à 5 h 01

- La session a retiré elle-même un verrou vieux de plus de quatre heures et a repris. La cause de l'arrêt n'est pas établie. L'alerte à Ced est levée ; le fait reste noté.
- **B-09 rendu à 7 h 13**, en relecture. Défauts d'Hermès laissés tels quels jusqu'à la fusion (case de recontact facultative et non cochée, brouillon natif de confidentialité conservé).
- **B-09 crée un type de contenu `imagine_contact`** (messages du formulaire de contact) que l'import de la voie 1 ne connaît pas. On ne rouvre pas l'import pour cela. Raison : l'import traite l'archive du site actuel, où ce type n'existe pas ; il ne comptera que le jour où le nouveau site sera lui-même copié. Dette écrite dans les écarts, avec les propositions de sujet de B-08.
- Les pages de B-09 n'entrent pas dans la matrice d'étanchéité de C-26 : elles ne portent aucun contenu réservé, et B-09 prouve lui-même que ses messages ne sortent ni par REST ni par la recherche. La matrice sera étendue une fois, quand la série de pages sera finie.
- **B-07, signalé par Hermès** : `Agenda.php` écrirait un champ de texte sans l'échappement que WordPress attend, comme B-08 et C-25 avant lui. Non reproduit. Consigne : reproduire d'abord, par un cas d'essai avec antislash sur un bouchon fidèle ; corriger à la seule frontière d'écriture si c'est rouge ; l'écrire en trois lignes si c'est vert. B-07 reste code clos, c'est un complément.

## Questions rangées pour Imagine

- Combien de temps garde-t-on un message du formulaire de contact ? Défaut : aucune suppression automatique n'est inventée.
- Le sommaire audio d'un numéro est-il réservé aux ayants droit du numéro ? Défaut : oui, comme le PDF.
- Quand un pack thématique change après un achat, que garde l'acheteur ? Défaut : les numéros du pack au moment du paiement.

## Files

- **Voie 1** : resceau unique (A-26, A-27, A-30, A-31, avec A-20 dans le rejeu), preuve finale et `PRET` de T-03, A-29. Un lot de plus : **A-32, la tournée des inventaires** (une commande qui enchaîne les outils d'inventaire clos et rend un bilan), à commencer après le `PRET` de T-03.
- **Voie 2** : corrections de B-09 quand elles arrivent, C-27 (en cours), le complément de B-07, B-10. Deux lots de plus : **B-11** (vidéos externes sans appel à un tiers, podcasts, sommaire audio servi comme le PDF), **C-28** (packs thématiques : l'achat ouvre, numéro par numéro, ce que C-14 ouvre).

# Passage automatique de 13 h

Lu : les rapports de 7 h 34 à 12 h 58 (les deux voies), les vérifications de T-03, B-09, B-10, les vérifications complémentaires d'A-26 et d'A-27, la vérification d'A-30, les fusions d'A-31, C-27, B-10, B-11 et C-28, le rapport d'A-32, les corrections de B-10 et la reprise des preuves de B-11. Aucun accord donné sur le réel.

## Clôtures

- **A-26 et A-27 clos.** Leurs vérifications complémentaires disent « prêt pour la clôture » : matrice réelle rejouée, code inchangé, aucune empreinte changée à la main, `PRET` redéposé, ligne `PAQUETS` verte lue par le rejeu indépendant du relecteur (11 paquets, 0 échec). C'est la condition écrite à 7 h.
- **A-30 clos.** Sa vérification dit « prêt » : les cinq instructions traitées, 38 tests verts en UTF-8 et en cp1252 sur une session Windows propre, paquet refait par le parent après T-03, vert au rejeu de 12 h 58. Les deux réserves sont hors lot (comptes globaux qui bougent avec l'autre voie ; un changement de source périmerait le sceau, comme pour tout lot).
- **B-09 code clos** : cinq instructions appliquées et vérifiées (reprise du menu après une interruption entre le marqueur et l'option ; un effacement n'annonce sa fin qu'après disparition vérifiée des métadonnées). Les pages légales et la FAQ restent volontairement vides : les textes viennent d'Imagine et de son conseil. Validation visuelle de Ced attendue.
- **B-10 code clos** : huit instructions appliquées, 14 tests rejoués par le vérificateur lui-même. Défauts de la fusion confirmés : l'écran propre « Réglages → Points de vente » reste (l'écran de C-10 n'est pas rouvert) ; la désaccentuation passe par `Normalizer` quand l'extension intl est là, sinon par une table latine bornée, et la dépendance est écrite ; l'ordre des clés de la correspondance compte pour l'idempotence stricte, limite documentée. Validation visuelle de Ced attendue.
- **B-07, le complément de l'antislash** : reproduit rouge sur un bouchon fidèle, corrigé à la seule frontière d'écriture (`wp_slash` sur le nom), 206 assertions vertes, reçu déposé. B-07 reste code clos, pas de nouveau paquet.

## T-03 — vérifié « remonte à Ced » : rien pour Ced, une mise en cohérence

- La vérification confirme le fond : les six instructions sont appliquées, les deux défauts (temps, mémoire) sont corrigés et testés pour de vrai. Elle bloque sur deux points de forme, et les adresse à Ced. Aucun n'est visuel, métier ou réel : tranchés ici.
- **A-20 dans le rejeu n'est pas une divergence.** La fusion disait de le laisser dehors ; l'arbitrage de 7 h, postérieur, a demandé de l'y faire entrer avec le resceau. Hermès a suivi la consigne la plus récente. Le relecteur comparait à la fusion seule.
- **Les documents du lot se contredisent** : un `PRET` et une preuve finale verte, à côté d'un manifeste, d'un rapport, d'une réception et d'une convention restés à l'état de candidat, au point que le lecteur du candidat refuserait l'arbre. Décision : **une seule version, celle de la clôture.** Hermès aligne ces documents sur l'état réel (A-20 dans le rejeu, `PRET` posé), sans toucher au lanceur gelé (`wp/tests/t01/`, `wp/tests/rejouer.ps1`) ; le lecteur du candidat dit qu'il ne vaut qu'avant le `PRET`, ou accepte l'état final. Puis une vérification, avec un rejeu indépendant. Raison : retirer le `PRET` rouvrirait un mécanisme prouvé pour un défaut de papier.
- T-03 n'est pas clos tant que cette vérification n'a pas dit « prêt ». Les lots clos par son rejeu le restent : le mécanisme a rendu des résultats indépendants.

## A-31 — à corriger, un important ; la question posée à Ced est technique, tranchée

- Verdict de fusion retenu. Le regroupement des petits nombres, appliqué à des compteurs de liens cassés, ou bien ne cache rien (un seul compteur dans son groupe), ou bien fond trois nombres que la migration doit lire séparément.
- **Les quatre compteurs de liens cassés sont publiés exactement**, de 0 à 4 compris ; le regroupement reste sur les années et les années par état. **Le total des remboursements est exact** quand une seule année est présente. Raison : ce sont des totaux d'anomalies techniques à réparer avant la bascule, pas des groupes de personnes ; un « 2 » ne désigne personne, et le lot existe pour le lire. Le rapport ne sort que par le gardien, sans identifiant. À défaire si Ced préfère « moins de 5 » partout (la fusion décrit la variante).
- Lancer `preparer-image.ps1` et `rejouer.ps1` après avoir ajouté des tests est permis : le gel interdit de les modifier, pas de les lancer. Une collision avec un rejeu de l'autre voie est un aléa, pas un défaut : on attend, on rejoue.
- L'aléa du harnais (« no such object » à la première passe) est noté aux écarts ; le lanceur gelé n'est pas rouvert pour lui.

## A-32 — construit, arrêté au bon endroit : le brief se trompait

- Le brief affirmait que « ce sont les outils qui refusent un site non vérifié ». C'est faux pour les outils d'inventaire (A-10 à A-25) : la preuve montre que les treize aboutissent sans le fichier `.imagine-staging-verified.json`, même sur un environnement déclaré « production ». Seuls les outils qui écrivent (A-03, A-04, A-05, A-09) lisent ce fichier. L'erreur est dans le brief, pas dans le lot ; s'arrêter sans ajouter de garde ni toucher aux outils clos était juste.
- **Les outils clos ne sont pas modifiés.** Raison : ils sont en lecture seule, et trois d'entre eux (A-23, A-24, A-27) ne se lisent utilement que sur la source, par Ced, hors agents ; un refus dans chaque outil fermerait cette porte, et rouvrirait treize paquets.
- **L'interdiction du brief est levée pour la tournée seule** : la tournée, qui sert à la copie vérifiée, contrôle elle-même le fichier de statut avant de lancer quoi que ce soit, le lit comme A-05 le lit, et refuse la tournée entière, d'un seul code, s'il manque, s'il est invalide ou si l'environnement est déclaré « production ». Aucune option pour passer outre.
- La preuve négative devient : sans le fichier, aucun outil n'est lancé, base et fichiers identiques. Les doubles d'A-10 et d'A-11 restent.
- A-26 et A-27, clos ce passage, entrent dans la liste (une ligne chacun). A-30 reste dehors (il demande un fichier d'Imagine), A-29 et A-31 aussi (pas clos).
- Consigné pour Ced : lancés un par un, les outils d'inventaire ne vérifient pas où ils tournent.

## A-29 — toujours pas de diagnostic

- Quatrième passage sans le réveil de diagnostic : le resceau, T-03, A-31 et A-32 sont passés avant, à raison. A-29 ne bloque personne et, sur une copie neutralisée, ses six nombres vaudront « inconnu ». La consigne tient, en dernier.

## C-27 — à corriger, deux importants et un mineur

- Verdict de fusion retenu. Une lecture en échec de la source du compte est prise pour une absence : elle peut écraser une source existante, et laisser un effacement s'annoncer complet alors que la source reste. Une proposition vue, jamais répondue puis effacée peut être redéposée par un ancien formulaire.
- Défaut de la fusion confirmé : la métadonnée du compte garde sa forme structurée, et le README l'écrit.
- Les corrections datent de 9 h 18 et n'ont pas été prises : elles passent en tête, après celles de C-28 en cours.
- La place de la section dans l'écran de réglages : c'est la question déjà posée à Ced pour C-22, C-24 et C-25 ; une quatrième section, une seule réponse.

## B-11 — code conforme, preuve à reprendre ; deux blocages tranchés

- Verdict de fusion retenu : aucun défaut fonctionnel, aucune fuite ; la réception était périmée par un fichier partagé changé par C-28 après le scellé, et trois contrôles de recette étaient plus faibles qu'annoncés. Ne pas poser de `PRET` sur une preuve rouge était juste.
- **Cinq options absentes deviennent explicites quand le vrai formulaire de réglages est soumis.** C'est le comportement natif de WordPress : le formulaire écrit toutes les options de son groupe. Décision : le contrôle de conservation compare les **valeurs effectives** (lues avec leur valeur par défaut enregistrée), avant et après. Une option absente qui devient explicite à sa valeur par défaut exacte est verte, et listée dans le reçu ; une valeur différente est rouge, signalée comme défaut du lot qui possède l'option, et n'est pas corrigée dans B-11. Aucun préremplissage.
- **Les deux éditeurs réels restent hors de portée de l'automate** (boîte masquée sur le numéro, clic intercepté sur l'article). Décision en deux temps, un réveil au plus. D'abord établir si le champ est atteignable à la main dans l'éditeur livré : s'il ne l'est pas, c'est un défaut fonctionnel de B-11 (la rédaction ne pourrait pas saisir l'adresse), à corriger à la seule déclaration de la boîte, avec son test. S'il l'est, on ne se bat pas contre l'éditeur : la persistance est prouvée par le témoin d'écriture sur le vrai WordPress (valeurs changées, effacement, deux courts-circuits détectés), et le parcours dans l'éditeur devient trois lignes pour Ced dans `A-VOIR.md`. Raison : règle de proportion, c'est un site fictif.
- Avec cela, `PRET` permis, la limite écrite en tête de la note ; la vérification jugera.
- **L'adresse d'une vidéo collée dans le corps d'un article réveille l'oEmbed natif** : la fusion demandait à Ced s'il acceptait que le « zéro appel sortant » repose sur une consigne à la rédaction. Ce n'est ni visuel ni réel : tranché au plus prudent, **un verrou technique, par un petit lot (B-12)**. Raison : une consigne oubliée une fois charge un lecteur tiers et ses cookies sans consentement (§4.4). À défaire si Ced préfère la consigne.
- Le `catch` trop large du paywall, qui a masqué la régression venue de C-28 : noté aux écarts, repris au gel du code avec le passage de style ; on ne rouvre pas un lot code clos pour lui.

## C-28 — à corriger, deux importants ; corrections en cours

- Verdict de fusion retenu. Un pack dont un numéro est dépublié reste payable alors qu'il n'ouvre plus rien : l'indisponibilité doit être refusée par le serveur, au panier et à la validation. Et un instantané manquant ne se reconstruit jamais après coup depuis la liste vivante.
- Défaut de la fusion confirmé : l'enregistrement de C-14 délie aussi la métadonnée de pack. Cela touche un fichier d'un lot code clos : accepté, ajout seul, le paquet de C-14 est de l'historique.
- Le bouchon de lecture de B-04 a reçu `apply_filters` : accepté, aucune assertion affaiblie.
- En attendant Imagine, un pack qui contient un numéro dépublié est bloqué en entier ; aucun prix n'est recalculé.

## Questions rangées pour Imagine

- La recherche d'un point de vente : localité ou code postal exacts, ou aussi un début de code postal, un rayon ? Défaut : exacts, sans casse ni accents.
- Un pack thématique est-il bien un produit simple à prix unique (et non le « produit groupé » natif, qui n'a pas de prix d'ensemble) ? Défaut : produit simple.
- Un pack dont un numéro est dépublié : bloqué en entier, ou vendu sans ce numéro à un prix recalculé ? Défaut : bloqué en entier.
- La sélection d'articles du menu étendu, par thématique : choisie par la rédaction, ou les plus récents ? Défaut : les plus récents, nombre en réglage (B-13).
- Les noms des attributs du contact attendus par Brevo, et le statut d'un bénéficiaire d'abonnement offert ou groupé. Défaut : clés internes du site ; statut « inconnu » pour un bénéficiaire (C-29).

## Files

- **Voie 1** : corrections d'A-31 (en cours), mise en cohérence de T-03, A-32 débloqué, A-29. Un lot de plus : **A-33, le poids des archives** (ce qui reste hors des dix derniers numéros, compté), à commencer après les `PRET` d'A-31 et d'A-32.
- **Voie 2** : corrections de C-28 (en cours), corrections de C-27, reprise de la preuve de B-11. Trois lots de plus : **B-12** (aucun appel sortant depuis le corps d'un contenu), **C-29** (la fiche du contact pour Brevo, sans Brevo), **B-13** (menu principal et menu étendu des thématiques).

# Passage automatique de 16 h

Lu : les rapports de la voie 2 de 13 h 35, 14 h 07, 14 h 45 et 15 h 20, les vérifications de B-11, C-27 et C-28, les deux relectures et la fusion de B-12, le diagnostic d'A-29, la note de reprise d'A-31. Aucun rapport de la voie 1 depuis 12 h 50. Aucun accord donné sur le réel.

## Clôtures

- **C-27 code clos.** Sa vérification dit « prêt » : les cinq instructions appliquées (une lecture en échec n'est plus une absence, à l'écriture de la source comme à l'effacement ; une proposition vue puis effacée ne se redépose pas), vérificateur du lot rejoué par le relecteur (628 portes), quatorze contre-exemples verts. La place de la section dans l'écran de réglages reste la question déjà posée à Ced. Validation visuelle attendue.
- **C-28 code clos.** Sa vérification dit « prêt » : le pack indisponible est refusé par le serveur à l'ajout et à la validation, l'instantané ne se reconstruit plus après coup, empreintes des sources livrées égales au sceau, vérificateur hors ligne rejoué (31 contrôles). Réserve du relecteur acceptée : au second tour il n'a pas pu relancer la suite Docker ; il l'avait rejouée au premier, et les mêmes tests sont verts dans le rejeu fait par le vérificateur de B-11 (1 201 tests). Les deux questions du lot sont chez Imagine, sur leur défaut prudent. Validation visuelle attendue.

## B-11 — vérifié « remonte à Ced » : rien pour Ced, une règle

- La vérification confirme le fond : six instructions appliquées, code fonctionnel identique à la réception, empreinte par empreinte, suite rejouée au vert par le relecteur. Elle remonte deux points à Ced. Aucun n'est visuel, métier ou réel au sens de la doctrine : tranchés ici.
- **La réception est de nouveau périmée, par une ligne d'un autre lot.** B-12 a ajouté son enregistrement dans `imagine-site.php` après le scellé de B-11 ; C-29 a fait de même à B-12 une heure plus tard. Tant que chaque lot scelle l'empreinte entière du fichier d'amorçage, chaque lot suivant périme tous ses voisins. Décision : **le fichier d'amorçage partagé de l'extension se contrôle par contrat, sur les lignes du lot, jamais par son empreinte entière.** C'est la règle qui vaut déjà en voie 1 pour un mode d'emploi commun. Le vérificateur d'un lot contrôle l'empreinte de ses propres fichiers, et la présence dans l'amorçage de son bloc d'enregistrement, tel qu'il l'a livré. Vaut pour B-11, B-12, C-29 et les lots à venir ; les lots code clos ne sont pas rouverts, leurs paquets sont de l'historique. Raison : le choix le plus simple, et le seul qui arrête la récurrence sans geler le fichier.
- **La saisie dans l'éditeur réel revient à Ced** : c'est la décision de 13 h, que le relecteur ne pouvait pas lire dans la fusion. Elle tient. La boîte est proposée par l'éditeur livré (11 sur 11), la persistance est prouvée sur le vrai WordPress ; le geste reste trois lignes dans `A-VOIR.md`, à faire avec la validation visuelle.
- B-11 n'est pas clos : une réception par contrat, puis une vérification. Rien à réécrire dans le code du lot.

## B-12 — à corriger, un bloquant

- Verdict de fusion retenu. Le garde de l'aperçu compare la route à une chaîne exacte, alors que le routeur de WordPress ne tient pas compte de la casse : une variante de casse atteint le service natif sans passer par le verrou. Il faut être un rédacteur connecté pour l'emprunter, et le site de démonstration bloque de toute façon le transport ; mais le lot est le verrou, donc bloquant.
- Défauts de la fusion confirmés : reconnaître la route comme le routeur le fait ; la matrice native n'entre pas dans la suite scellée (elle demande un vrai WordPress), elle se rejoue à chaque montée de version du cœur, condition écrite dans le README.
- **L'instruction 3 de la fusion est remplacée par la règle ci-dessus.** Elle demandait une réception complémentaire couvrant la ligne de C-29 ; B-13 la périmerait de nouveau. Le vérificateur de B-12 passe au contrat. L'assertion sur les sources n'est pas neutralisée : elle porte sur les fichiers du lot et sur son bloc d'amorçage.

## A-29 — diagnostic fait, cause non établie : le lot est rangé

- Le réveil de diagnostic a eu lieu. Établi : sur une base non neutralisée, l'outil passe (classique et HPOS) ; sur les deux copies neutralisées, le processus sort en 255 après avoir écrit un succès, le gardien refuse, la sortie publique est vide, aucun faux succès. Non établi : la cause. Deux hypothèses, aucune prouvée (un rappel de fin de requête, ou un destructeur, qui échoue sous l'interdiction d'écrire).
- Décision : **A-29 est rangé, sans `PRET`, hors de la tournée.** Raison : sur une copie neutralisée, ses six nombres vaudraient « inconnu » ; un vert n'y apprendrait rien, et chercher la cause demande une trace de fin de processus que le lot ne justifie pas aujourd'hui. Rien n'est assoupli : une sortie 255 reste un refus, aucun canari ni compteur n'est retiré.
- Il sera repris si Ced veut cet inventaire sur la source, ou le jour où un staging vérifié permet d'observer la fin du processus en vrai. Un outil sans `PRET` n'est pas proposé à Ced.

## Voie 1 — muette depuis 13 h 33

- Dernier fichier de la voie 1 : 13 h 33 (reprise d'A-31, diagnostic d'A-29). Depuis, ni rapport, ni preuve, ni `PRET`, file pleine, aucune question posée. La note de reprise d'A-31 dit que son worker a été interrompu par une erreur 401, « jeton fournisseur expiré », et que le parent reprenait.
- La voie 2 a travaillé pendant ce temps : le NUC et la synchronisation fonctionnent. Je ne peux ni relancer une session ni renouveler un jeton : signalé à Ced en tête d'`ETAT.md`. Aucune consigne nouvelle n'y changerait rien ; la file de la voie 1 est laissée telle quelle, A-29 en moins.

## Questions rangées pour Imagine

- « Point de vente le plus proche » dans le pied de page (§3.2) : par géolocalisation du visiteur, ou un lien vers la recherche ? Défaut : un lien, aucune géolocalisation (B-15).

## Files

- **Voie 1** : inchangée (corrections d'A-31, mise en cohérence de T-03, A-32, puis A-33) ; A-29 en sort.
- **Voie 2** : corrections de B-12 et passage au contrat pour B-11, B-12 et C-29, C-29 (en cours), B-13. Deux lots de plus, dans l'ordre du §3.2 : **B-14** (la page d'accueil, contenu et ordre, sans la forme), **B-15** (le pied de page, cinq zones, sans géolocalisation).

# Passage automatique de 19 h

Lu : les rapports de la voie 2 de 16 h 28, 17 h 00 et 17 h 11, ceux de la voie 1 de 17 h 34, 17 h 38, 18 h 20 et 18 h 42, les vérifications de B-11 (troisième tour) et de B-12, les deux relectures et la fusion de C-29, les réceptions d'A-31 et de T-03, la note de finalisation d'A-32. Aucun accord donné sur le réel.

## Clôtures

- **B-11 code clos.** Sa vérification dit « prêt pour la clôture » : réception par contrat (fichiers du lot, bloc d'amorçage exact et unique, section du README bornée), vérificateur hors ligne rejoué au vert par le relecteur (32 contrôles), suite rejouée (1 204 tests), aucun code du lot modifié. Les deux raisons du « remonte à Ced » du tour précédent sont levées. Reste à Ced : la validation visuelle et le geste de trois lignes dans l'éditeur (`production/B-11/A-VOIR-contrat-V2.md`).
- **B-12 code clos.** Sa vérification dit « prêt » : le bloquant est corrigé en une ligne (comparaison de la route sans tenir compte de la casse, permissions natives intactes), couvert par une matrice native (trois variantes de casse, cache absent puis ancien : 52 contrôles, zéro tentative sortante, un simple lien) et un test dans la suite ; réception par contrat verte ; trois mineurs appliqués. Réserve permanente acceptée et écrite au README : la preuve « zéro sortie » repose sur une matrice native hors de la suite scellée, à rejouer à chaque montée de version du cœur. Validation visuelle attendue.

## Règle de clôture — un paquet rouge de l'autre voie, pour un lot non rendu, ne bloque pas

- La fusion de C-29 propose de ne clore aucun lot tant que la commande de rejeu affiche un paquet rouge, même étranger au lot. Non retenu. **Un lot se clôt sur la ligne `REJEU … PASS`, la ligne `OUTILS` sans échec, et son propre vérificateur.** Un paquet rouge sur la ligne `PAQUETS` ne bloque que s'il appartient au lot, ou à un lot clos ou porteur d'un `PRET`.
- Raison : A-31 et A-32 sont rouges parce qu'ils sont en cours, sans `PRET` ; c'est leur état normal, déjà écrit dans `ETAT.md` (« deux rouges attendus »). C-27, C-28, B-11 et B-12 ont été vérifiés dans cet état, et leurs vérificateurs le disent. Faire dépendre la voie 2 de la voie 1 arrêterait une file sur le travail en cours de l'autre. L'instruction 5 de la fusion de C-29 est donc remplacée par cette règle.

## C-29 — à corriger, deux importants

- Verdict de fusion retenu (un relecteur disait « conforme », l'autre « à corriger » ; la fusion a relu le code et confirme les deux défauts).
- **C29-01 : une désinscription explicite disparaît si la newsletter est ensuite retirée du catalogue.** La fusion pose la question à Ced. Elle n'est ni visuelle ni réelle (rien ne part vers Brevo, le site est fictif), et le brief la règle déjà : « un compte qui s'est désinscrit de tout a une fiche réduite à "à retirer" ». Tranché sur le défaut de la fusion : **un refus explicite du lecteur est conservé, même pour une lettre sortie du catalogue**, et la fiche reste « à retirer » ; la suppression administrative d'une lettre encore choisie ne vaut jamais désinscription. Raison : le choix le plus prudent, celui qui ne laisse personne dans un outil d'envoi après qu'il a demandé à en sortir. Signalé à Ced, à défaire ; la question est aussi rangée pour Imagine.
- **C29-02 : un bénéficiaire de groupe dont l'adhésion est suspendue devenait « non abonné » au lieu d'« inconnu ».** Le brief dit « inconnu » pour un bénéficiaire, sans condition d'activité. Correction du côté de C-29, sans toucher aux règles postales de C-13. La portée exacte reste une question pour Imagine.
- Mineurs retenus : appels multilignes du fichier neuf mis en PSR-12 (c'est le code du lot en cours, pas un reformatage d'un lot clos), libellés traduisibles déclarés sur des chaînes littérales. Les lectures multiples par compte dans le bilan sont acceptées pour la démonstration et notées aux écarts.
- La fiche « à retirer » sans identifiant : gardée telle quelle, comme le brief ; l'identification du contact se fera par le compte au branchement. Rangé pour Imagine.

## Voie 1 — repartie à 17 h 34

- Le réveil de 17 h 34 a trouvé un verrou vieux de plus de quatre heures, l'a retiré et a repris. La cause de l'arrêt de 13 h 33 n'est pas établie. Alerte levée.

## A-31 — corrigé ; une lecture trop large de ma consigne, à resserrer avant le sceau

- Les six instructions sont appliquées : quatre compteurs de liens cassés exacts, corbeille, frontières de date, matrice native complète (192 scénarios de liens), suite verte sur une session Windows propre.
- **Un point à reprendre, et la faute est dans ma file.** J'avais tranché à 13 h : les quatre compteurs de liens exacts, et le total des remboursements exact quand une seule année est présente. La file l'a résumé en « le regroupement reste sur les années et les années par état », et Hermès l'a appliqué à la lettre : les natures et les remboursements par année ne sont plus regroupés. Ce n'était pas décidé, et aucune relecture ne le demandait. **Les natures et les remboursements par année reviennent sous le regroupement des petits nombres, comme au premier tour ; seuls sortent du regroupement les quatre compteurs de liens et le total des remboursements.** Raison : le choix le plus prudent ; on n'élargit pas ce qu'un outil publie exactement au-delà de ce qui a été demandé, et un nombre de remboursements par année publié exactement à côté d'années par état regroupées serait incohérent.
- À faire avant le sceau, pour ne refaire le paquet qu'une fois.

## A-31, A-32, T-03 — un blocage croisé, et la sortie proposée par Hermès est retenue

- Constat : le portail d'A-31 exige un rejeu général sans aucun paquet rouge, celui d'A-32 aussi, et chacun des deux est le rouge de l'autre tant qu'il n'est pas scellé. T-03 attend les deux. Hermès s'est arrêté sans rien assouplir et sans `PRET` : c'était juste.
- **La séquence conjointe écrite dans `production/A-32/FINALISATION.md` est autorisée, une fois** : sortir le candidat d'A-31 de son emplacement, jouer les deux portails pendant que le lanceur range les deux lots « hors rejeu, journaux absents », resceller chacun par sa propre commande, puis rejouer la commande générale dans les deux consoles.
- Raison : elle ne modifie ni le lanceur gelé, ni un portail, ni un vérificateur, et ne remplace aucune empreinte à la main ; un lot dont le paquet n'est pas installé est déjà, pour le lanceur, « hors rejeu », pas vert.
- **La preuve qui compte est la dernière étape** : un rejeu général après les deux sceaux, où A-31 et A-32 figurent parmi les paquets vérifiés, aucun des deux hors rejeu, zéro échec. C'est elle que les relecteurs rejouent et lisent ; les portails joués pendant la séquence n'établissent pas à eux seuls qu'un paquet est vert, et les rapports le disent.
- Si une étape reste rouge : arrêt sans `PRET`, rien d'assoupli, un rapport.
- T-03 ensuite : sa mise en cohérence est faite (documents alignés, A-20 dans le rejeu, lecteur déclaré « avant `PRET` seulement », `PRET` retiré le temps du travail). Il lui reste la preuve finale sur une base verte, le `PRET`, puis une vérification avec rejeu indépendant.

## Questions rangées pour Imagine

- Un lecteur s'est désinscrit d'une newsletter, puis cette newsletter est retirée du catalogue : reste-t-il signalé « à retirer » de l'outil d'envoi ? Défaut : oui (C-29).
- Un bénéficiaire d'abonnement groupé dont l'adhésion est suspendue : « inconnu », ou « non abonné » ? Défaut : « inconnu », dès qu'il est identifié (C-29).
- Au branchement, le contact à retirer est-il identifié par le compte du site plutôt que par une adresse portée dans la fiche ? Défaut : par le compte ; la fiche « à retirer » ne porte rien d'autre (C-29).

## Files

- **Voie 1** : retouche d'A-31 (regroupement), séquence conjointe A-31 et A-32, clôture de T-03, puis A-33. Aucun brief nouveau : la file a plus d'un lot d'avance.
- **Voie 2** : corrections de C-29 en tête, puis B-13, B-14, B-15. Aucun brief nouveau : trois lots d'avance. Rien de la voie 2 depuis 17 h 13 ; noté pour Ced, sans alerte à ce stade.

# Passage automatique de 22 h

Lu : les rapports de la voie 1 de 19 h 30, 20 h 02, 20 h 39, 20 h 41, 21 h 31 et 21 h 47, ceux de la voie 2 de 21 h 18, 21 h 36, 21 h 59 et 22 h 17, la vérification d'A-31 (second tour), les deux relectures et la fusion d'A-32, la note de blocage d'A-33. Aucun accord donné sur le réel.

## Clôture

- **A-31 clos.** Sa vérification de second tour dit « prêt » : les six instructions appliquées, la retouche de 19 h 30 faite (natures et remboursements par année de nouveau regroupés ; seuls les quatre compteurs de liens cassés et le total des remboursements sont exacts), suites Python rejouées par le vérificateur, preuves natives lues (552 contrôles par console, témoin de non-refonte discriminant), import et gardien intacts. Après le resceau, deux rejeux généraux d'Hermès donnent douze paquets vérifiés, aucun hors rejeu, A-31 et A-32 compris.
- Les deux questions que la vérification renvoie à Ced (liens cassés et total des remboursements publiés exactement, ou plafonnés) sont celles tranchées à 13 h, déjà signalées à Ced comme « à défaire » : rien de nouveau.
- Réserve écrite : le vérificateur n'a pas pu lancer la matrice dans les conteneurs ; il s'appuie sur les preuves déposées. Le lecteur du paquet ne se rejoue pas hors du NUC (journaux non versionnés) : je ne l'ai pas rejoué.
- **Aucune clôture en voie 2** : C-29 (corrigé, `PRET` à 21 h 36), B-13 (21 h 59) et B-14 (22 h 17) attendent leur vérification ou leur relecture.

## A-32 — à corriger, trois importants ; les défauts proposés par la fusion sont retenus, sauf un mot sur A-16

- **C02, retenu** : les codes de supervision que le gardien émet pour les outils de la tournée (sortie invalide, délai dépassé, réussite incomplète) entrent dans la liste fermée que lit la tournée, et le bilan porte le code. Ni le gardien ni un outil clos ne sont modifiés.
- **C04, retenu** : le contenu d'une chaîne PHP ne compte pas comme une déclaration d'environnement ; une forme non comprise reste refusée. C'est une défense en profondeur, derrière le fichier de statut : important, pas bloquant.
- **C03, retenu pour A-19** : la tournée n'écrit pas `--as-of` ; l'outil prend l'instant courant, qui est son défaut documenté. Une date d'exemple figée fausserait le diagnostic le jour de la bascule.
- **A-16, précisé** : la tournée n'écrit pas `--limit`, et l'outil prend son défaut documenté, **dix**. La fusion parlait d'« inventaire complet » : ce n'est pas le sens. Dix numéros est le périmètre du cahier des charges (§4.3) ; aucun mode sans plafond n'est créé, aucun mode d'emploi d'outil clos n'est retouché.
- **C01, mineur, retenu** : la phrase du mode d'emploi commun renvoie à la liste de la tournée.
- La garde de la tournée (lecture du fichier de statut) n'est pas un écart : c'est l'arbitrage de 13 h. Une ligne de traçabilité au rapport suffit.
- **La question que la fusion pose à Ced sur le `PRET` d'A-32 est technique, et elle est sans objet** : le `PRET` a été retiré à 21 h 43. Il reviendra après les corrections, sur un rejeu général où A-32 est vérifié pour de bon.
- Hermès a commencé ces corrections à 21 h 53, après un rapport qui disait attendre un mandat. Une fusion « à corriger » se prend sans mandat : c'est la règle de la file.

## Règle — un lecteur de paquet ne photographie pas ses voisins

- Constat, deux fois dans la soirée. Le lecteur d'A-32 prend l'empreinte de tout `wp/outils/bascule/` : les huit fichiers d'A-33 l'ont fait passer au rouge sans qu'une ligne d'A-32 ait changé, et A-33 se retrouve bloqué par le rouge qu'il a causé. Le lecteur final de T-03 englobe les paquets voisins : la retouche d'A-31, autorisée, l'a périmé quarante minutes après son `PRET`.
- **Règle : le lecteur permanent d'un lot contrôle ce qui appartient au lot (ses fichiers, ses lignes dans un fichier partagé) et ce dont il dépend, par une liste fermée écrite dans le lot.** Jamais un dossier entier, jamais le paquet d'un autre lot. La preuve qu'on n'a rien touché chez les voisins se fait une fois, au moment du sceau, dans le reçu ; elle n'est pas une condition permanente du lecteur.
- Raison : c'est la règle du contrat, déjà écrite pour les fichiers partagés ; sans elle, chaque lot nouveau de la voie 1 rouvre A-32 et T-03, et le blocage croisé de 19 h se reproduit à chaque livraison.
- **A-32** : sa photographie se borne à son dossier `tournee/`, à ses tests, au gardien, à l'import gelé et aux dossiers des quinze outils de sa liste. Un outil de la tournée qui change périme toujours le paquet : c'est voulu. L'élargissement de `gates.py` à tout le dossier, fait à 21 h 53, est à défaire.
- **T-03** : son lecteur final contrôle ses propres fichiers ; la photographie des voisins reste dans le reçu du sceau, datée. Après sa clôture, T-03 n'est pas rescellé à chaque paquet nouveau.
- **A-33** et les lots à venir : même règle.
- **Les lots clos ne sont pas rouverts pour cela.** Le sceau d'A-31 lie cinq fichiers de la tournée : si les corrections d'A-32 le périment, un resceau d'A-31 par sa propre commande, code inchangé, clôture maintenue.

## A-33 — construit, bloqué par A-32 : l'ordre

- L'outil et sa matrice sont verts ; son paquet garde volontairement des portails rouges, parce que le rejeu général trouvait A-32 rouge. Hermès s'est arrêté sans `PRET` et sans rien assouplir : c'était juste.
- **Ordre, sans séquence conjointe** : corrections d'A-32 et photographie bornée, sceau d'A-32 ; puis portails d'A-33 rejoués, sceau, `PRET` ; la preuve est un rejeu général, dans les deux consoles, où A-32 et A-33 sont tous deux vérifiés, aucun hors rejeu, zéro échec.
- Pendant le sceau d'A-32, le paquet d'A-33 est encore rouge par construction. **Un seul paquet par lot, et c'est le dernier rejeu vert** : un paquet aux portails rouges n'est pas un paquet et ne reste pas installé ; Hermès le sort du dépôt, comme il l'a fait pour le candidat d'A-31, et le lanceur range A-33 « hors rejeu, journaux absents » jusqu'à son propre sceau. Ni le lanceur gelé ni un portail ne sont modifiés.
- A-33 n'entre pas dans la tournée : il n'est pas clos.
- A-33 et la requalification d'A-32 mesurent Python 3.11.15 sous Windows ; les lots précédents et les commandes de réception emploient 3.14.6. La matrice Python se rejoue avec celui des commandes de réception.

## T-03 — `PRET` posé à 19 h 57, retiré à 20 h 41 : après A-32 et A-33

- La retouche d'A-31 a périmé sa photographie ; son code n'a pas changé. Hermès propose de le finaliser sur l'arbre final, après A-33, plutôt que de sceller une photographie aussitôt périmée : retenu.
- Avec la règle ci-dessus, son lecteur ne dépendra plus des paquets voisins. Ensuite : preuve finale, `PRET`, une vérification avec rejeu indépendant, clôture.

## Voie 2 — repartie à 21 h 18

- Arrêt de 17 h 13 à 21 h 18, repris seul sur un verrou ancien retiré ; cause non établie. Depuis : corrections de C-29, B-13, B-14, B-15 en cours.
- **B-13** : le libellé « Connexion » pour un lecteur connecté est une question de présentation, pour Ced avec le lot. La sélection manuelle des articles du menu étendu n'est pas construite : question déjà rangée pour Imagine. Le lecteur de C-29 borné à ses fichiers : conforme à la règle du contrat.
- **B-14** : le retrait de la liste « Derniers articles » de l'accueil suit le §3.2, qui ne la prévoit pas ; B-05, clos, n'est pas modifié. À confirmer par la relecture.
- Le balisage de contenu payant (§3.9) est déjà dans le paywall de C-08 : pas de lot pour lui.

## Questions rangées pour Imagine

- Que donne l'offre de bienvenue atteinte par QR code ? Défaut : rien, une page d'accueil et un code suivi (C-30).
- Le code suivi écrit-il la source d'acquisition du compte ? Défaut : non, il se lit à côté (C-30).
- D'où vient la liste des adresses jetables refusées ? Défaut : tenue à la main par Imagine, vide au départ (C-31).
- L'appel à l'abonnement de fin d'article s'affiche-t-il pour un abonné actif ? Défaut : non (B-16).

## Files

- **Voie 1** : corrections d'A-32 et photographie bornée ; A-33 (sceau, `PRET`) ; T-03 (preuve finale, `PRET`). Un lot de plus, dans l'ordre du §4.3 : **A-34** (les liens internes des contenus repris vers ce qui part aux archives, comptés).
- **Voie 2** : B-15 en cours, il ne restait rien derrière. Trois lots de plus : **B-16** (la page article : résumé, mots-clés, signature, numéro d'origine, appel de fin d'article, §3.3), **C-30** (la page d'offre de bienvenue et son code suivi, §3.7), **C-31** (les adresses jetables refusées à l'inscription, §3.9).
