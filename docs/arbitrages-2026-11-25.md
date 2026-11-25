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
