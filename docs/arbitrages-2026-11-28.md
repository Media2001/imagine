# Arbitrages du 28 novembre 2026

Tenu par Claude. Une ligne par question, avec la raison. Les questions métier ne sont pas tranchées ici : elles deviennent un réglage au défaut prudent et une ligne dans `docs/decisions.md`.

# Passage automatique de 1 h

Lu : les rapports de 22 h 24 (voie 1) et de 22 h 40 à 1 h 11 (voie 2), les vérifications de C-29, B-13 et B-14, les fusions de B-13, B-14, B-15 et B-16. Aucun accord donné sur le réel.

## Clôtures

- **C-29 (la fiche du contact pour Brevo) : code clos**, sur sa vérification « prêt » (cinq instructions appliquées, 3 tests et 51 assertions verts). Réserve : le rejeu du vérificateur rendait FAIL pour une seule erreur, étrangère au lot, dans un test de B-16 alors en cours d'écriture ; B-16 a été rendu depuis, et les cinq rejeux suivants d'Hermès sont verts (1 211 à 1 217 tests, 13 paquets, zéro échec). La règle de 19 h s'applique : un rouge d'un lot en cours ne bloque pas la clôture d'un autre. La question « un refus explicite survit-il à la suppression de sa lettre » reste tranchée sur le défaut prudent (oui) et rangée pour Imagine.
- **B-13 (menu principal et menu étendu) : code clos**, sur sa vérification « prêt » (huit instructions appliquées, trois rouges témoins). Réserve : le contrôle sur le site (`--live`) n'a pas été rejoué par le vérificateur. Validation visuelle de Ced attendue.
- **B-14 (page d'accueil, structure) : code clos**, sur sa vérification « prêt » (cinq instructions traitées). Réserves : le vérificateur n'a pas pu relancer le rejeu en conteneur, il a contrôlé les reçus contre les empreintes des fichiers présents ; la recette de B-01 n'a pas reconfirmé l'ancre (ligne suivante). Validation visuelle de Ced attendue.

## Lots clos dont un contrôle ancien ne passe plus

- **B-01** : sa recette d'origine est rouge sur deux contrats dépassés par des lots clos depuis (le jeton du PDF, remplacé par C-11 ; « aucun script », remplacé par le mode lecture de B-03) et sur un inventaire de B-00 et C-08 qui a grandi. **B-01 reste code clos et sa recette devient historique ; elle n'est ni réécrite ni rejouée lot par lot.** Raison : la réécrire périmerait ses reçus pour un contrat que personne ne conteste. L'ancre `imagine-abonnement`, seul point que la fusion de B-14 voulait y relire, est désormais tenue par le test rejouable de B-14 et par le clic réel du paywall.
- **B-11** : son lecteur contrôle l'empreinte de deux gabarits (`single-imagine_numero.php`, `single.php`) que B-14 puis B-16 ont modifiés à bon droit. **B-11 reste code clos ; son paquet devient historique pour ces deux gabarits.** La preuve à jour est le complément déposé sous le lot qui a modifié le fichier : le diff borné et les 23 contrôles natifs de B-11 rejoués (sous B-14, puis sous B-16). Aucun reçu clos n'est réécrit.
- **Règle qui en sort, pour la voie 2 : un lot qui modifie à bon droit un gabarit scellé par un lot code clos le dit en tête de son rapport, dépose sous son propre dossier le diff borné et le rejeu des contrôles du lot clos, et ne rescelle pas le lot clos.** Les lecteurs historiques seront requalifiés en une seule fois, au gel du code, avec le passage PSR-12.

## Défauts des fusions, retenus

- **B-13** : ordre alphabétique des thématiques dans le menu étendu ; un article récent sans image reste sans image (ni image inventée, ni article écarté) ; la sur-invalidation du cache à l'enregistrement d'un contenu est laissée, notée.
- **B-14** : quand une page cible n'est pas publiée (« S'abonner », « Soutenir », « Notre coopérative », « Nos newsletters »), le lien disparaît sans repli visible. Retenu : pas de lien mort, et c'est le même comportement dans le pied de page (B-15) et en fin d'article (B-16). La fusion le posait à Ced comme confirmation non bloquante : signalé dans `ETAT.md`, à défaire s'il préfère un repli visible.
- **B-14** : l'écart de comptage 1 206 → 1 208 vient des deux tests de B-15, pas d'A-32 ni d'A-33 comme la fusion le supposait. Noté, sans suite.
- **B-15** : l'invalidation large du cache du pied de page et les adresses par nom de page sont gardées. La preuve de cache refaite (une construction, zéro, puis une après invalidation ; un mutant sans retour anticipé échoue) attend sa vérification.
- **B-16** : l'appel de fin d'article est piloté par le motif que rend la décision d'accès de C-08, et non par une seconde lecture de Memberships : retenu, c'est la règle « une seule projection des droits ». Un article libre lu par un anonyme n'a pas d'appel : conforme au brief. Attend sa vérification.
- **C-30** : la sélection provisoire rangée sur la commande pendant un paiement asynchrone est un choix de code, documenté ; la relecture le lira. Seule une commande payée compte.

## Voie 1 — état constaté, et l'ordre ne change pas

- Le rapport de 22 h 24 demandait l'ordre de finalisation d'A-32 et d'A-33 : il a été écrit à 22 h 30 (A-32, puis A-33, puis T-03). Il tient.
- Constaté dans le dépôt : A-32 a été rescellé à 22 h 29, portails verts, **avant** la règle de 22 h 30, donc sur une photographie encore récursive de tout le dossier des outils ; A-33 a été installé à 22 h 53. Le rejeu indépendant du vérificateur de C-29 lit « 13 paquets vérifiés, 0 échec », A-31, A-32 et A-33 compris. Aucun `PRET`, aucun rapport depuis 22 h 24, aucun dépôt de la voie 1 depuis 22 h 53.
- **La photographie d'A-32 se borne avant son `PRET`, pas après.** Raison : sans cela, A-34 le refera tomber, cette fois sur un lot rendu ou clos. C'est un changement d'une fonction (la liste des racines), suivi d'un sceau par la commande du lot.
- **La consigne « sors du dépôt le paquet d'A-33 » est levée** : elle valait pour un paquet aux portails rouges ; il est vert. Elle ne revient que si le nouveau sceau d'A-32 périme A-33 et que les deux se bloquent de nouveau.
- Python : la question du 3.11.15 d'A-33 reste posée dans la file ; le rapport de 22 h 24 mesure bien 3.14.6 pour A-32.

## Questions rangées pour Imagine

- Le cookie de session posé pour retenir un code suivi (C-30), et ceux de l'attribution d'origine de WooCommerce, demandent-ils un consentement ? Défaut : le lot C-32 les inventorie et ne construit aucun bandeau ; à faire valider par Imagine et son conseil.
- Les comptes de la rédaction ont-ils une page publique d'auteur ? Défaut : non, la signature de B-16 est un texte sans lien (C-33).

## Files

- **Voie 1** : de l'avance (borne et `PRET` d'A-32, `PRET` d'A-33, T-03, A-34). Pas de lot nouveau.
- **Voie 2** : B-15 et B-16 corrigés, C-30 rendu, C-31 en cours, rien derrière. Deux lots de plus : **C-32** (les cookies qu'un visiteur reçoit, §3.14 et §4.4) et **C-33** (ce que le site montre de ses comptes à un anonyme, §4.4).

# Passage automatique de 4 h

Lu : le rapport de 3 h (voie 1) et ceux de 1 h 36 à 4 h 09 (voie 2), les vérifications d'A-32, de B-15, de B-16 et de C-30, les fusions d'A-33, de C-30, de C-31, de C-32 et de C-33. Le frein posé par Ced à 2 h 40 s'applique : aucun brief, aucun lot nouveau. Aucun accord donné sur le réel.

## Clôtures

- **A-32 (la tournée des inventaires) : clos**, sur sa vérification « prêt » de 3 h 33 (cinq instructions appliquées, 16 tests Python rejoués par le vérificateur, 72 contrôles natifs sur 72 lus sur preuves dans les deux consoles), `PRET` déposé avec la photographie bornée par une liste fermée. Réserves : le banc natif n'est pas rejouable par un relecteur ; le rejeu général qui montre A-32 et A-33 tous deux vérifiés n'est pas encore cité (ligne suivante).
- **B-15 (pied de page) : code clos**, sur sa vérification « prêt » (quatre instructions traitées, code du pied de page inchangé, preuve de cache refaite avec un mutant). Réserve : le vérificateur n'a pas pu relancer le rejeu en conteneur ; les cinq rejeux d'Hermès qui ont suivi sont verts (1 217 à 1 229 tests). Validation visuelle de Ced attendue.
- **B-16 (page article) : code clos**, sur sa vérification « prêt » (cinq instructions appliquées, vérificateur du lot relancé au vert, 15 contrôles natifs et 77 au navigateur). Validation visuelle de Ced attendue, structure de l'en-tête à revoir sur maquette.
- **C-30 (page « Bienvenue » et codes suivis) : code clos**, sur sa vérification « prêt » (sept instructions traitées, suite rejouée par le vérificateur : 1 229 tests, zéro échec). Réserves : la recette sur le site n'a pas été rejouée par le vérificateur ; la preuve « prix inchangé » au calcul réel de WooCommerce vit dans cette recette, la suite scellée la couvre sur bouchons. Validation visuelle de Ced attendue.

## Voie 1

- **A-33 relu « à corriger »** (3 h 48) : en tête de file. Les deux défauts de la fusion sont retenus. Le PDF désigné par `pdf_cle` est un fichier du numéro et compte dans le poids des dix numéros, dédoublonné avec les pièces rattachées : sans lui la comparaison est vide en mode taxonomie. Un numéro sélectionné reste du côté conservé quand article et numéro partagent un type ; aucun refus nouveau, la règle d'A-16 n'est pas touchée. Son `PRET` de 2 h 25 précède la relecture : il se redépose après correction.
- **A-16 garde dix numéros par défaut.** La vérification d'A-32 rappelle qu'omettre `--limit` rend dix, pas « tout ». C'est ce que §4.3 demande (les dix derniers numéros) ; A-16 est clos, on ne l'élargit pas.
- **La preuve conjointe reste due** : un rejeu général, après le nouveau `PRET` d'A-33, où A-32 et A-33 sont tous deux parmi les paquets vérifiés, zéro échec. La voie 2 a lu `VERIFIER_TIMEOUT` sur A-32 et A-33 à 2 h 19, puis sur A-33 seul à 2 h 44, pendant que les deux voies rejouaient. Tant que ce n'est pas reproduit par un rejeu lancé seul, c'est un aléa de deux voies sur un même arbre. Le lanceur reste gelé : on mesure, on ne règle aucun délai.
- **T-03 se clôt après le `PRET` d'A-33.** C'est un lot rendu : le finir n'est pas un lot nouveau au sens du frein.
- **A-34 attend.** Non commencé, hors de ce que le frein laisse à la voie 1.
- **Import, contenus d'un type inconnu : pas de dégel par ce passage.** Hermès répond que la décision demande une consigne de dégel ciblée. Je ne l'écris pas. Raisons : l'import gelé est le code que Ced lancerait sur l'archive réelle, et sa réserve a été levée sur cet état précis ; la réponse de Ced est à confirmer lundi. Demandé à la voie 1 : une note de cadrage dans son rapport (fichiers touchés, commandes de Ced inchangées ou non, tests, durée), sans une ligne de code. Signalé à Ced dans `ETAT.md` et `docs/validation-ced.md`.

## Voie 2

- **C-31, C-32, C-33 relus « à corriger »** (3 h 08 à 3 h 58), pris par Hermès sans attendre la file : c'est la règle. Après leurs `PRET`, la voie 2 s'arrête, file vide : voulu par le frein.
- **C-30** : le raccord minimal à la Store API est gardé tel quel. Le tunnel de la démonstration est la commande classique ; la preuve sur un paiement réel par la Store API se fera avec le tunnel (§3.7), sur un staging vérifié. L'optimisation des requêtes, différée par Hermès comme la fusion le permettait, reste différée.
- **C-31** : une ligne invalide rejette toute la liste des domaines et garde l'ancienne ; les noms de domaine en Unicode sont refusés (ASCII ou punycode). Défauts de la fusion retenus, déjà documentés.
- **C-32** : le filtre sur le contenu de la page est gardé (la liste s'affiche sans que personne la recopie). **Le lot se clôt sur le verdict d'inventaire** ; le contrôle strict « aucun cookie en simple lecture » reste rouge et doit le rester tant que les sept cookies d'attribution de WooCommerce sont posés : c'est un constat, pas un défaut du lot, à condition que la tolérance soit bornée à ces sept noms. Rien n'est éteint. Le choix d'Hermès de garder le reçu de rejeu historique et d'en déposer un nouveau aux totaux courants est retenu.
- **C-33** : le test léger des accroches est à faire. La question « un abonné connecté voit-il les comptes » est rangée pour Imagine ; le lot reste conforme au brief (visiteur anonyme).
- **Les quatre réponses visuelles de Ced** (kiosque, menu connecté, sections de réglages, date de coopérateur) ne touchent aucune correction en cours, et Hermès ne rouvre aucun lot clos pour elles : retenu. Elles s'appliqueront en une fois après la confirmation de Ced lundi.

## Questions rangées pour Imagine

- Un abonné connecté, sans droit de lister les utilisateurs, est-il traité comme un visiteur pour ce que le site montre de ses comptes ? Défaut : le lot ferme les voies au visiteur anonyme ; rien de plus n'est appliqué (C-33).
- Les sept cookies d'attribution de WooCommerce, posés en simple lecture, demandent-ils un consentement, et faut-il éteindre l'attribution ? Défaut : laissée telle que WooCommerce la livre, écart écrit (C-32). Précise la question déjà posée à 1 h.

## Files

- Aucun brief écrit, rien d'ajouté à la file de la voie 2 : frein.
- `docs/validation-ced.md` créé : le parcours de lundi, sept questions en tête. Classement des questions pour Imagine ajouté à `docs/decisions.md`.

# Passage automatique de 7 h

Lu : les quatre rapports de la voie 2 (4 h 42 à 5 h 26), les vérifications de C-31, de C-32 et de C-33. Rien de la voie 1 depuis son rapport de 3 h. Le frein de Ced s'applique : aucun brief, aucun lot nouveau. Aucun accord donné sur le réel.

## Clôtures

- **C-31 (adresses jetables refusées à l'inscription) : code clos**, sur sa vérification « prêt » (cinq instructions appliquées ; suite rejouée par le vérificateur : 1 243 tests, 37 036 assertions, zéro échec, 13 paquets verts). Réserve : les quatre recettes sur le site (104 contrôles) ne sont pas rejouées par lui. Validation visuelle de Ced attendue : l'écran de réglages et le ton du message.
- **C-32 (les cookies qu'un visiteur reçoit) : code clos sur son verdict d'inventaire**, comme décidé à 4 h (sept instructions appliquées ; 20 tests purs, le banc local et la réception relancés par le vérificateur). Le contrôle strict « aucun cookie en simple lecture » reste rouge, borné aux sept noms `sbjs_…` : constat, pas défaut. Rien n'est éteint, aucun bandeau.
- **C-33 (ce que le site montre de ses comptes) : code clos**, sur sa vérification « prêt » (trois instructions appliquées, code métier inchangé ; contrôleur pur et vérificateur relancés par le vérificateur, l'ancien contrôleur rejoué rouge). Réserve : PHPUnit lu sur reçus.

## Voie 2

- **C-31, les deux gardes ajoutées à la commande** (commande classique et Store API) : retenues. Ce n'est pas une fonction entrée par une correction : le brief demandait le refus à la création d'un compte pendant une commande, et la correction 3 demandait d'avancer le contrôle si une écriture précédait le refus, ce qui a été reproduit. Elles n'agissent que hors connexion et quand un compte est créé.
- **C-32, C-31 : textes périmés** (`A-VOIR.md`, section C-32 du README, qui décrivent l'état d'avant la réception). Les lots ne sont pas rouverts pour cela : une retouche de texte périmerait leurs reçus. À reprendre avec la première retouche qui les touchera, ou au gel du code.
- **C-32, exceptions de cache** : deux noms natifs exacts admis dans la restauration (styles de blocs, cache des compositions du thème), reçus rouges conservés. Retenu : ce sont des caches de rendu, et la borne est fermée.
- **C-33, le vérificateur du lot n'accepte plus aucun paquet rouge** : il est plus strict que la règle « un paquet rouge d'un lot en cours de l'autre voie ne bloque pas ». Laissé tel quel, le lot est clos ; la règle reste celle de la file, et ce lecteur ne se rejoue pas à chaque paquet nouveau.
- **La voie 2 est à l'arrêt, file vide** : voulu. Rien n'est ajouté.

## Voie 1

- **Aucun dépôt depuis 3 h** : cinquième arrêt. La file ne change pas (A-33, T-03, la note sur l'import). Je ne peux pas la relancer ; signalé à Ced sans urgence, le frein étant posé.
- **Le `PRET` d'A-33 de 2 h 25 est à retirer en premier** : il précède la relecture « à corriger ». Tant qu'il est là, A-33 n'est ni clos ni à relire.
- **Le rejeu de la voie 2 où A-32 et A-33 sont verts ne vaut pas la preuve conjointe** : il porte sur A-33 d'avant corrections. La preuve reste due après le nouveau `PRET`.

## Questions rangées pour Imagine

- Aucune nouvelle. Le ton du message de refus de C-31 est une question visuelle pour Ced.

## Files

- Aucun brief, rien d'ajouté à `A-FAIRE-2.md` hors des trois clôtures. `docs/validation-ced.md` : C-31, C-32 et C-33 ajoutés à l'annexe.

# Passage automatique de 10 h

Lu : les trois rapports de la voie 2 (7 h 28, 8 h 29, 9 h 30 : file vide, arrêt, rien touché), la vérification d'A-33 (8 h 33), `production/A-33/RAPPORT.md`, `production/T-03/BLOCAGE.md` et `FINALISATION.md`. La voie 1 a repris seule à 7 h 33 et déposé jusqu'à 8 h 33 ; elle n'a laissé aucun rapport dans `files/rapports/`. Le frein de Ced s'applique : aucun brief, aucun lot nouveau. Aucun accord donné sur le réel.

## Clôtures

- **A-33 (le poids des archives) : clos**, sur sa vérification « prêt » (deuxième tour : les cinq instructions de la fusion appliquées ; lecteurs scellés d'A-33, d'A-32 et d'A-31 relancés par le vérificateur, tous verts ; 30 tests Python relancés par lui). Réserve : le rejeu en conteneur n'a pas été relancé par le vérificateur, les contrôles natifs et les unités PHP sont lus sur les traces scellées. C'est un outil de lecture, sans rien de visuel ; sa clôture n'est pas un accord pour le lancer sur le réel.
- **La preuve conjointe due depuis A-32 est rendue** : après le nouveau `PRET`, `PAQUETS : 13 vérifiés, 0 échecs ; hors rejeu : aucun`, A-32 et A-33 compris, dans les deux consoles (1 243 tests, 37 036 assertions), d'après le rapport du lot. La réserve écrite sur A-32 est levée.
- **T-03 n'est pas clos** : pas de `PRET`, Hermès le dit lui-même. Voir plus bas.

## Voie 1

- **A-33, deux élargissements non demandés par la fusion, signalés par le vérificateur : retenus.** La liste `DEPS` du banc, resserrée à une liste fermée de fichiers, applique la règle « un lecteur ne photographie pas ses voisins ». Le mode « paquet bloqué » (un paquet à portail rouge conservé sans jamais recevoir `PRET`) n'a servi que l'état transitoire ; le paquet livré n'est pas dans ce mode. Aucun nombre produit ne change. Le lot n'est pas rouvert pour les retirer.
- **Python** : la question est close, la matrice d'A-33 est rejouée en 3.14.6 avec `C:/Python314/python.exe`.
- **Délais** : aucun `VERIFIER_TIMEOUT` au rejeu général quand la voie 1 rejoue seule ; lecteurs seuls mesurés à 0,24 s (A-32) et 0,22 s (A-33). Les dépassements lus de nuit par la voie 2 sont donc rangés comme un aléa de deux rejeux simultanés. **Ils réapparaissent en revanche dans la preuve native de T-03**, sur sa copie jetable (ligne suivante).
- **T-03 reste « candidat bloqué, sans `PRET` »** : son lecteur est borné à ses fichiers (fait, régression reproduite puis corrigée), mais la preuve native ne trouve pas de base verte, trois fois de suite, A-32 et A-33 dépassant le délai sur la copie jetable. Hermès n'a relevé aucun délai et n'a fabriqué aucun vert : retenu. **Le lanceur reste gelé, aucun délai n'est relevé par ce passage** : relever un délai du lanceur rouvre la preuve de tous les paquets, et la cause n'est pas établie. Demandé : un diagnostic de cinq lignes, sans réparation (quel vérificateur, sa durée mesurée sur la copie jetable contre 0,2 s sur l'arbre, le verdict du troisième reçu, et si le délai appartient au script de T-03 ou au lanceur gelé). Pas de quatrième essai de la preuve native à l'identique. La clôture de T-03 est de la mécanique de preuve : elle ne bloque ni l'import, ni la validation de lundi, ni un lot clos ; elle attend.
- **La note sur l'import (contenus d'un type inconnu) n'est pas rendue** : toujours due, dix lignes, aucun code. Pas de dégel.
- **Un rapport manque** : la voie 1 a travaillé une heure sans rien déposer dans `files/rapports/`. Rappelé dans la file.

## Voie 2

- À l'arrêt, file vide, trois rapports d'une ligne : voulu. Rien n'est ajouté.

## Questions rangées pour Imagine

- Aucune nouvelle.

## Files

- Aucun brief. `A-FAIRE.md` : A-33 en « Terminé », il reste le diagnostic de T-03 et la note sur l'import, puis arrêt. `A-FAIRE-2.md` inchangé. `docs/validation-ced.md` : la question 7 mise à jour, rien d'autre (A-33 n'a rien de visuel).
