# Arbitrages du 25 novembre 2026 (11 h 45)

## Règle nouvelle : une question technique n'arrête plus personne

Les deux voies ont attendu des heures sur des questions que la fusion adressait « à Ced » alors qu'elles étaient techniques. À partir de maintenant :

- La fusion classe chaque question : **technique**, **métier** (Imagine) ou **visuelle / réel** (Ced), et propose pour chacune un **défaut prudent**.
- **Technique** : Hermès applique le défaut proposé, sans attendre, et le note dans son rapport. Claude peut le renverser après coup.
- **Métier** : devient un réglage au défaut prudent (doctrine), noté pour Imagine. On n'attend pas.
- **Visuelle ou touchant au réel** : seule catégorie qui attend, et elle n'arrête que le lot concerné, jamais la file.
- Un lot vérifié « prêt » dont les questions restantes sont techniques ou métier **ne bloque pas le lot suivant** : Hermès enchaîne. Claude clôt quand il passe.

## A-03 — non-régression (`corrections/A-03.md` §5)

1. **Bruit après mise à jour : non, pas de bruit.** Une liste de hooks « attendus après mise à jour », classés « attendu », courte et justifiée ; tout le reste demeure anormal.
2. **Erreurs PHP : contrôle complémentaire.** Sur staging, lire le journal d'erreurs PHP entre deux horodatages, en plus de l'affichage et du statut 500.
3. **Étanchéité du paywall : hors A-03**, oui (C-08, C-11).
4. **Preuves : oui**, on retire les archives de preuves ; la preuve de clôture est un rejeu.
5. **Échec silencieux de collecte : bloquant**, pas de rapport partiel.

A-03 : code clos. A-04 peut démarrer.

## A-01 — archive réelle, deuxième reprise

Code conforme (vérification du 24/11, 22 h 33). Clos pour ce qui est du diagnostic, que Ced relance. La suite PHP n'a pas pu être rejouée à cause d'une image de test périmée : **quand un lot ajoute un paquet de tests, Hermès relance lui-même `wp/tests/preparer-image.ps1`** avant de déposer `PRET` (autorisation permanente, dépendances publiques).

## C-11 — PDF du numéro : code clos

- Robot vérifié → extrait, pas de PDF : **oui**, c'est le défaut prudent, et c'est un réglage.
- Acheteur d'un numéro : **oui, lot dédié** (C-14).
- Hébergement : **Linux uniquement**, refus explicite ailleurs.

## C-12 — accès découverte : code clos

- Désignation par la rédaction obligatoire, fermé sans elle : **oui**.
- Après épuisement, un article déjà ouvert **se referme** (défaut prudent, réglage, question notée pour Imagine).

## C-13 — écran de la liste d'envoi

Rendu le 24/11 mais jamais relu : le fichier `PRET` n'est plus dans `production/C-13/`. À redéposer.

# Passage automatique de 16 h 30

Lu : rapports de 13 h 25 à 15 h 59, fusions A-04 et C-14, vérifications A-03 (n° 2) et C-13.

## A-03 — clos

Vérification n° 2 : « prêt pour la clôture », suite rejouée par le vérificateur (1 012 tests). La liste d'un seul hook attendu après mise à jour est confirmée. Dépendance notée pour A-04 (`http-rollback.php`), déjà prise en compte par A-04.

## A-04 — à corriger (`corrections/A-04.md`)

Verdict de la fusion retenu. Les trois défauts proposés sont confirmés :

1. **Fichier principal d'une extension : déclaré dans le plan**, avec validation du chemin. Pas de détection automatique : le plan est relu par un humain, une détection peut se tromper en silence.
2. **Reprise après plus de dix minutes : on rafraîchit `.maintenance` sous verrou**, seulement si l'extension de maintenance persistante est intacte ; sinon refus. Un outil « reprenable » qui refuse de reprendre après une pause n'est pas reprenable.
3. **`bootstrap-only` : statu quo**, avec trace d'audit obligatoire dans le plan. Pas de balayage générique.
4. La question « la preuve réelle se fera sur le staging vérifié, avec un GO écrit » n'est pas une question : c'est la doctrine (§3). Rien à demander à Ced ici.

Les relecteurs n'ont pas pu rejouer la suite Python d'A-04 (accès refusé à Docker depuis leur poste). Accepté pour ce tour : le paquet de preuves a été lu, et la suite PHP globale rejouée. Pas de chantier d'outillage pour cela maintenant.

## A-01, troisième passe — rendue, pas encore relue

- **Stripe désactivée sur la copie** (en plus des clés retirées) : confirmé. Sur un staging, une passerelle chargée sans clé n'apporte rien et garde un point d'entrée ; le staging reste « fidèle » pour tout ce qui ne présente pas de danger.
- **Le plafond de quatre vérifications par lot bloquait sa relecture** : A-01 en a déjà quatre, parce qu'il a reçu trois briefs successifs. `scripts/relire.ps1` : plafond porté à huit. Raison : sans cela, la passe que Ced attend pour importer ne serait jamais vérifiée. Le garde-fou contre les boucles demeure.

## C-13 — code clos, validation visuelle de Ced attendue

Vérification : les sept instructions sont appliquées, banc pur rejoué par le vérificateur.

- **Abonnements groupés dans la liste d'envoi** : réglage `imagine_envoi_groupes`, fermé par défaut. Question notée pour Imagine (`decisions.md`).
- **Profils sans paiement** : la question « peut-on compléter les profils de C-09 ? » était classée « périmètre, pour Imagine ». Je la reclasse **technique** : donner à un profil fictif le paiement fictif que sa fiche décrit ne décide aucune règle. La règle, elle, ne bouge pas : actif sans paiement validé = exclu de la liste. Voir `briefs/C-09-complement-paiements-fictifs.md`. C'est un renversement partiel de la ligne du 23/11 (« aucun paiement antérieur inventé »), pour une raison écrite : trois lots ne peuvent plus être montrés. La partie « pas de renouvellement automatique sans moyen de paiement » du 23/11 est maintenue.
- Écriture de relevés à l'affichage, route anonyme qui répond 403 : acceptés pour la démonstration, à revoir au branchement réel.

## C-14 — corrections livrées, vérification à déclencher

- C14-01 (un achat payé survit à la maintenance du catalogue) : c'était bien une correction, pas un arbitrage. Confirmé.
- C14-02 : réglage `imagine_achat_remboursement` (`commande` par défaut, ou `ligne`). Confirmé, question notée pour Imagine.
- Achat sans compte : fermé, question notée pour Imagine.
- **Le fichier `PRET` n'a pas été redéposé après les corrections** : la vérification ne se déclenche que sur un `PRET` plus récent que la fusion. À redéposer.
- Incident des douze observations de liste d'envoi créées par un diagnostic : pris en compte. On ne nettoie rien : l'historique est en ajout seul, le site est fictif et reconstructible.

## B-02 — débloqué

Le lot est resté sans `PRET` parce que le brief nommait un profil `a-4x-j45` qui n'existe pas. Erreur de brief : le profil « quatre fois » du catalogue est **A-SEPA4**. `PRET` à déposer, au sens « prêt à relire », avec les réserves déjà écrites. Elles tomberont en partie avec le complément de C-09.

- Raccord ajouté par B-02 pour que la modification d'adresse d'un abonnement soit relevée par la liste d'envoi (Subscriptions n'émet pas le crochet qu'écoutait C-13) : accepté là où il est, limité au formulaire du client. À remonter dans le code de la liste d'envoi au branchement réel.
- Le brief citait §3.10, qui traite des newsletters : le minimum du brief fait foi (noté dans `ecarts.md`).

## Règle de fonctionnement

Hermès rend un lot en quarante minutes à deux heures, et la voie 1 s'est arrêtée à 15 h 59, file vide, onze minutes après la fusion d'A-04. Deux conséquences : les files reçoivent désormais **plus d'un lot d'avance**, et une fusion « à corriger » arrivée après la dernière mise à jour de la file est à prendre par Hermès sans attendre que la file la cite (ajouté aux deux files).

# Passage automatique de 19 h 30

Lu : rapports de 16 h 25 à 18 h 39, vérifications A-01 (n° 5), A-04 et C-14, fusion B-03, rapport du complément de C-09.

## A-01, troisième passe — close

Vérification n° 5 : « prêt pour la clôture », suite rejouée par le vérificateur (1 012 tests). Les six décisions du brief sont appliquées. La modification de l'outil natif partagé (`staging/lib.php`, `policy.php`) était demandée (décision D5) et reste gardée par la version de politique : acceptée. Clôture d'un lot de code : **ce n'est pas un accord d'import**. Ced relance le diagnostic quand il veut ; l'import reste sa décision.

## A-04 — clos

Vérification : les six instructions sont appliquées. Deux réserves portées à la clôture, sans effet sur elle :

1. Aucun relecteur n'a pu rejouer la suite d'intégration (pas de Docker sur leur poste). Accepté, comme au tour précédent : la suite PHP globale a été rejouée, la logique corrigée a été exercée en local par le vérificateur.
2. La montée 6.9.1 → 7.0 sur la pile commerciale complète et les migrations historiques des extensions payantes ne sont pas prouvées. Elles ne peuvent l'être que sur le staging d'Imagine vérifié, avec un GO écrit de Ced (doctrine §3). Ce n'est pas une question, c'est une limite inscrite dans `ETAT.md`.

## A-05 — rendu, relecture attendue

Décisions à défaut d'Hermès confirmées : fichier principal audité exigé pour agir ; cartographie auditée obligatoire avant de supprimer une table ; désinstallation d'une extension seulement si le plan la demande, reprise refusée si sa fin est incertaine ; Action Scheduler ni purgé ni exécuté ; un seul site, chemins conventionnels. Le plan d'exemple laisse tout à « garder » : c'est ce qui était demandé.

## C-14 — code clos, validation visuelle de Ced attendue

Vérification : cinq instructions appliquées, la sixième (optionnelle) assumée et documentée. Les deux questions pour Imagine sont déjà des réglages au défaut prudent (`decisions.md`).

## B-03 — à corriger (`corrections/B-03.md`)

Verdict de la fusion retenu.

1. **Couleurs posées dans le contenu : neutralisées dans les trois fonds.** Défaut de la fusion confirmé. Raison : c'est la seule façon de tenir « les trois fonds tiennent le contraste AA » sans dépendre de ce que la rédaction saisit, et c'est le sens d'une vue de lecture. Le contenu enregistré et les images ne sont pas touchés.
2. **Bloc `prefers-reduced-motion` redondant : on le retire.** Le plus simple ; la garantie est ailleurs.
3. **Instruction 5 (rejouer la part non reproduite par les relecteurs) : ne bloque pas la clôture.** C'est une limite du poste des relecteurs, pas un défaut du lot, et le site est fictif (proportion). Hermès rejoue ses tests après correction ; le vérificateur rejoue ce qu'il peut.
4. La question « les articles portent-ils des couleurs posées à la main ? » est rangée pour Imagine (`decisions.md`). Elle ne change rien au code.
5. La revalidation visuelle du contraste par Ced se fera **après** le choix des couleurs par le designer : la faire avant porterait sur des valeurs neutres provisoires.

## Complément de C-09 — rendu, vérification attendue

- Les paiements fictifs sont déclarés comme tels, sans passerelle, mandat ni jeton : conforme au brief.
- Rôle rétabli après les transitions de Subscriptions au reset : accepté (correctif de banc).
- **Liens « offert » et « groupé » absents** : on ne les fabrique pas. Ils dépendent du modèle des groupes, question ouverte chez Imagine. C-13 et B-02 restent donc « recette partielle » en mode strict sur ce point, et cela ne bloque ni leur démonstration ni la suite.
- La seconde échéance payée que le tableau de B-02 ne lit pas est un défaut de B-02, à traiter dans sa relecture.

## B-02 — toujours sans `PRET`

Demandé à 16 h 30, non déposé à 19 h 30 : le lot n'a donc jamais été relu. Redit en tête de file, avec la précision que `PRET` ne veut pas dire « recette complète ».

## Files

- Voie 1, vide à 18 h 39 : A-08 (répétition de la bascule sur le banc fictif), A-09 (test des redirections, §4.3), A-10 (inventaire des codes de réduction, §4.3). Trois outils, aucune décision : les plans et les reclassements restent à Ced, au référenceur et à Imagine.
- Voie 2 : B-04 (page numéro, kiosque, thématique, §3.3), C-15 (écran des échéances, §3.13). C-15 n'a qu'une action d'écriture (« paiement reçu » sur un virement, par les fonctions natives) et n'ajoute aucune règle d'accès.
- La voie 2 n'a pas déposé de rapport depuis 16 h 25 alors qu'elle a rendu deux lots : rappel ajouté à sa file.


# Passage automatique de 22 h 30

Lu : rapports de 19 h 34 à 22 h 18 (onze), vérifications A-05, B-03, C-09 (n° 2) et C-14 (n° 2), fusions A-05, A-08, A-09, B-02 et C-15.

## A-05 — clos

Vérification : cinq instructions sur cinq appliquées (dossier partagé, en-têtes de dépendance, ancêtre gardé dans `uploads`, affichage à blanc), preuve régénérée, aucune régression. Le vérificateur écrit « la clôture revient à Ced » : c'est un lot de code sans rien de visuel, il se clôt sur preuves (doctrine §6, décision du 21/11). **Ce n'est pas un accord pour toucher au réel** : le plan rempli par Ced, les préalables et un GO écrit restent requis avant tout nettoyage sur le staging d'Imagine.

## B-03 — code clos, validation visuelle de Ced attendue

Vérification : instructions 1 à 4 appliquées, la 5 partiellement (rejeu indépendant de la part PHP et HTTP). Déjà arbitré à 19 h 30 : cette instruction ne bloque pas la clôture du code, c'est une limite du poste des relecteurs sur un site fictif. La réécriture de `b03-final.py` (reçus datés, réconciliation avec C-15 qui touchait la base au même moment) n'était pas demandée ; elle ne touche pas le code livré et protège les reçus : acceptée. Reste à Ced : l'œil, et le contraste après le choix des couleurs par le designer.

## Complément de C-09 — code clos

Vérification n° 2 : « prêt pour la clôture ». Réserve inchangée : les décomptes sur le site de démonstration sont ceux d'Hermès, non rejoués par le relecteur. Proportion : accepté pour un site fictif.

## C-14

Vérification n° 2 : rien de neuf, le redépôt de `PRET` était administratif. Déjà clos à 19 h 30.

## A-08 — corrigé, vérification attendue

1. **III.6, présentation de `repetition.md`** : la fusion l'adressait à Ced parce que c'est la page qu'il lira le jour J. Ce n'est ni du visuel ni une décision sur le réel, c'est la lisibilité d'un mode d'emploi : tranché au défaut proposé par la fusion. Contenu exact conservé, une phrase simple en tête de chaque bloc, aucune commande modifiée. Ced peut le défaire.
2. **Idempotence « métier »** : au second passage, le fichier de maintenance d'A-04 et l'expiration d'un cache natif de Subscriptions peuvent être rafraîchis ; rien d'autre ne change. Accepté : exiger l'immobilité de ces deux points demanderait de modifier une extension tierce (doctrine §5).
3. Après une anomalie (code 2) : on conserve l'échec, on restaure la sauvegarde de départ, on repart dans un nouvel état. Confirmé, c'est le sens de la doctrine.
4. Les durées mesurées sur le banc ne dimensionnent pas la maintenance réelle : noté, à ne pas reprendre comme estimation.

## A-09 — corrigé, vérification attendue

Refus global des adresses à requête vide (`/a?`), plutôt qu'une normalisation : confirmé, c'est le plus simple et il n'y a pas de faux verdict possible. Adresses relatives à la racine, déclaration explicite de l'origine testée : confirmés.

## A-10 — rendu, relecture attendue

Conventions de comptage confirmées, elles sont écrites dans le rapport : douze mois calendaires, bornes incluses ; commandes annulées ou remboursées comptées comme commandes et non comme ventes ; états « en attente » et « annulation en attente » séparés ; limite de paiements initial compris. Ce sont des conventions de lecture, pas des règles : aucun code n'est reclassé ni supprimé.

## B-02 — corrigé, vérification attendue

- Libellé d'un abonnement suspendu avec adhésion en attente : défaut de la fusion confirmé, « virement en attente » est réservé au circuit virement identifié. Question rangée pour Imagine.
- Marge du paiement en quatre fois : c'est déjà un réglage (22/11). B-02 n'y met aucune valeur : confirmé.
- Recette partielle assumée (marge, compteur et historique, documents) : ce sont des emplacements nommés, pas des défauts.

## C-15 — corrigé, vérification attendue

- « Paiements en attente » limité aux paiements liés à un abonnement ; « mandats à lancer » limité au renouvellement exigible impayé. Défauts de la fusion confirmés, deux questions rangées pour Imagine.
- L'export garde une colonne devise en plus des quatre champs du cahier des charges : accepté, elle ne retire rien.
- Deux confirmations simultanées d'un même virement : un succès, un refus, une seule note. C'est le comportement voulu.

## B-04 — rendu, relecture attendue

Jeu fictif propre au lot (un produit public à zéro euro, vingt articles temporaires créés puis supprimés) : accepté, rien n'est acheté ni payé.

## Séparation des voies

Un worker de la voie 2 a lu `A-FAIRE.md` malgré l'interdiction. Lecture seule, signalée par Hermès lui-même, recadrée. Sans suite.

## Files

Les deux voies se sont arrêtées file vide (22 h 17 et 22 h 18) : trois lots chacune, dans l'ordre du cahier des charges.

- Voie 1, suite du §4.3 : A-11 (inventaire des adresses publiques, pour le plan de redirections), A-12 (inventaire de la structure des contenus, avant le modèle éditorial), A-13 (contrôle d'un export d'abonnés hors ligne). Les trois lisent et décrivent ; aucun ne décide. A-13 **n'importe rien** et ne verra jamais le vrai fichier : format inconnu, donc correspondance des colonnes en configuration ; refus de tout IBAN (§4.3).
- Voie 2, suite du §3.13 : C-16 (commande pour le compte d'un client, encodage sans email, vente sans identité), C-17 (justificatifs du tarif solidaire), C-18 (extractions). C-17 ne touche **ni au prix ni à l'accès** : l'effet d'une validation ou d'un refus sur le tarif n'est pas arrêté par Imagine (chapitre 7, question 4) ; les catégories sont un réglage livré avec une valeur neutre. C-16 laisse le don, le pack, l'offert et le groupé en emplacements nommés. C-18 ne fabrique ni tranche d'âge ni étiquette.
- Voie 1 : les lots récents déposent plusieurs centaines de fichiers de preuves chacun. Pour des outils en lecture seule, un seul paquet de preuves par lot (proportion).
