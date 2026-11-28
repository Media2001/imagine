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
