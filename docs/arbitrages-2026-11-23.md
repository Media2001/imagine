# Arbitrages du 23 novembre 2026 (16 h 30)

Questions techniques posées par les fusions de relecture. Aucune n'est visuelle ni métier : tranchées par Claude (doctrine, « qui valide quoi »).

## T-01 — commande de rejeu (`corrections/T-01.md` §5)

1. **Périmètre : oui.** Le rejeu couvre toute extension sur mesure sous `wp/` qui porte une configuration de tests (extensions, extensions obligatoires, thème), pas seulement `wp/plugins`. Une extension sur mesure sans tests est listée en avertissement.
2. **Tests ignorés : échouer.** Un test ignoré ou incomplet fait échouer le rejeu. Un relecteur doit pouvoir se fier à `PASS`.
3. **Conteneurs : balayage seul.** Au début de chaque rejeu, suppression des conteneurs orphelins portant l'étiquette propre au rejeu, et eux seuls. Pas de refonte.
4. **Reçus : `final-verification.json` fait foi.** `livraison-verifiee.json`, dont la provenance n'est pas traçable, sort des preuves (dossier d'historique, mention dans les notes).
5. Montage : `wp/` seulement, en lecture seule, plutôt que tout le dépôt.

## B-00 — site de démonstration (`corrections/B-00.md` §5)

1. **Rejouable sur le site augmenté : oui.** La recette de B-00 ne compte que ses propres contenus (ceux qui portent sa clé). Le site doit pouvoir être reconstruit à tout moment, y compris après C-08 et C-09 : c'est le site que Ced regarde.
2. **Étanchéité : entièrement à C-08.** B-00 ne porte plus d'assertion « mot de passe → corps ». La protection par mot de passe d'article disparaît dès que C-08 est actif.
3. **Reprise « trois fois, à cinq minutes » :** pour toute opération qui modifie l'outil ou un site. Une lecture d'état refusée se retente librement.
4. En plus : le site passe en `fr_FR` ; le contenu d'installation de WordPress (« Hello world! », page d'exemple, commentaire) est supprimé par le script ; `A-VOIR.md` est mis à jour sur l'état réel (thème `imagine` actif).

## B-01 — squelette du thème (`corrections/B-01.md` §5)

1. **« Hello world! » : purgé côté B-00** (ci-dessus). Le gabarit d'accueil ne filtre rien de plus ; l'assertion de la recette compare les identifiants et l'ordre, pas seulement le nombre.
2. **« Partenariat » : oui, dès maintenant.** L'étiquette et la déclaration des liens partenaires (§3.12) sont du texte et de la sémantique, pas du design. La distinction visuelle reste au designer.
3. **Preuves : régénérées une fois, sur l'état actuel**, après corrections. Un seul jeu de preuves, celui du site tel que Ced l'ouvre. La relecture du code du paywall relève de C-08.
4. **Kiosque : date de sortie obligatoire** à la publication d'un numéro, et assertée. Pas de position de repli.
5. Les mineurs M-3 à M-8 sont à corriger tels que décrits. En-tête du thème : la version minimale de WordPress est celle de la pile cible réellement installée sur le site de démonstration.

## Report

Le garde manquant sur `wc_get_page_permalink` est à traiter dans la relecture de C-08.

## C-08 — paywall sur article (`corrections/C-08.md` §5), 17 h 10

1. **Recherche interne : oui, bloquant.** Le §3.9 l'exige côté serveur. Pour un visiteur sans droit, la recherche ne porte pas sur le corps des articles réservés (titre et extrait public seulement) et n'en renvoie aucun fragment. Test : chercher la phrase témoin en anonyme ne renvoie rien ; en abonné, l'article sort. L'étanchéité ne repose plus sur le mot de passe natif.
2. **JSON-LD : `NewsArticle`, maintenant.**
3. **Mémoïsation : dans ce lot, à l'échelle d'une requête seulement.** Rien de persistant : le cache entre requêtes relève du lot cache et performance.
4. **C08-01 : aligner sur le booléen déclaré.**
5. Le garde `function_exists` sur `wc_get_page_permalink` est à ajouter (repli sur la page de connexion).

