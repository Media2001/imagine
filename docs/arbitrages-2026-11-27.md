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
