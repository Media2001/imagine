# Lot C-06 — Décision d'accès à un contenu

**Chantier** : C. **Nature** : PHP pur et tests, sans WordPress.
**Emplacement** : `wp/plugins/imagine-pilotage/src/Acces/`, `tests/Acces/`.
**Délai** : une demi-journée.
**Cas d'acceptance concernés** : R-25 à R-31.

## Pourquoi

Le paywall (§3.9) repose sur une seule question, posée à chaque requête : *ce visiteur a-t-il droit au texte complet de ce contenu ?* Aujourd'hui la réponse serait éparpillée entre Memberships, le thème et des cas particuliers. Ce lot l'écrit une fois, en un seul endroit, testée, sans dépendre de WordPress. Le branchement (page, REST, flux, PDF, cache) viendra ensuite et appellera cette décision partout.

## À implémenter

Une fonction de décision. **Entrées**, toutes passées en arguments (aucune lecture de base, de session ou d'horloge) :

- le contenu : réservé ou ouvert ; le numéro auquel il appartient ; son type (article, PDF du numéro) ;
- le visiteur : anonyme ou identifié ; et pour un visiteur identifié, ses droits au moment de la requête ;
- le résultat de la vérification des robots (lot C-03), déjà calculé ;
- l'instant de la requête.

**Sortie** : texte complet ou extrait, avec un **motif nommé**, et le bloc à afficher à la place (abonnement, connexion, régularisation, découverte épuisée).

Les droits à couvrir, d'après le cahier des charges :

| Situation | Décision |
|---|---|
| Contenu ouvert | Complet pour tous |
| Anonyme, contenu réservé | Extrait |
| Robot d'indexation vérifié | Complet |
| Faux robot (non vérifié) | Traité comme un anonyme |
| Abonné actif, bénéficiaire d'un abonnement offert ou groupé | Complet |
| Abonné en délai de grâce | Complet, avec le bandeau de régularisation |
| Abonné suspendu, expiré, ou virement non validé | Extrait |
| Acheteur d'un numéro | Complet pour les articles et le PDF **de ce numéro**, sans limite de durée ; extrait pour les autres |
| Accès découverte en cours | Complet dans les limites réglées |
| Accès découverte épuisé | Extrait |
| Coopérateur non abonné | Extrait |
| Équipe (rédaction, administration) | Complet |

Plusieurs droits peuvent coexister (un ancien abonné qui a acheté un numéro) : le plus favorable l'emporte, et le motif dit lequel.

## Exigences

- **Fermé par défaut.** Entrée manquante, incohérente ou inconnue : extrait. Jamais d'exception qui laisserait passer le texte.
- La décision ne renvoie **jamais le texte** : elle dit quoi servir. Aucun contenu ne transite par elle.
- L'accès découverte : sa forme n'est pas arrêtée (décision 5 d'Imagine). Modélise les deux variantes derrière une interface (durée, nombre d'articles), réglables, sans en choisir une.
- Table de vérité exhaustive en test : chaque ligne du tableau, les combinaisons de droits, les bornes de date (seconde avant et seconde après une échéance), et les entrées incohérentes.
- Celles du lot C-01 ; espace de noms `Imagine\Pilotage\Acces`.

## Ce que tu ne décides pas

Questions fermées dans `notes.md` : le PDF d'un numéro pour un abonné dont l'abonnement a commencé après ce numéro ; ce que voit un abonné en délai de grâce au-delà du bandeau ; la longueur de l'extrait (décision 20), qui n'est pas du ressort de ce lot.
