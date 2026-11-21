# Échéancier — C-05, prototype non branché

- `Planificateur` et `Versement` : PHP pur. Le calendrier, les numéros et les dates communes sont fournis par `Imagine\Pilotage\Numeros\Moteur` (C-01), jamais recalculés ici.
- `planifier(Annee, DateTimeImmutable $finEngagement, int $margeJours)` : quatre positions ordonnées. La borne exclusive d’engagement est obligatoire, fournie par l’appelant selon le contrat ; elle n’est pas présumée égale à une ouverture numérique retardée. Aucun défaut de marge, aucun montant, aucune lecture d’horloge.
- Première année : le premier versement prend la date de commande. Reconduction liée par C-01 : tous les versements gardent la date commune.
- Refus avant résultat exploitable : calendrier incomplet, fin non postérieure au début, date hors fenêtre, dates non strictement croissantes. Une exception n’est pas un échéancier partiel à exécuter.
- `RaccordManuel` : adaptateur Woo de démonstration **uniquement** pour une fixture marquée C05, drapeau manuel explicite et passerelle vide. Aucun hook enregistré, aucun automatisme ajouté au plugin. Il ne prouve ni un traitement des rejets ni l’idempotence financière concurrente.

**Blocage métier :** pour une commande située après le lancement commun de son premier numéro mais avant sa clôture, la première date commune reconduite peut précéder l’anniversaire et produire cinq dates dans la première année. Le prototype refuse ce cas ; il n’invente aucune dérogation. Voir `production/C-05/proposition.md`.

Tests depuis la racine du dépôt, avec Python déjà présent (aucune installation hôte) :

```bash
python wp/tests/echeancier-runner/run.py prepare
python wp/tests/echeancier-runner/run.py unit --name relecture-unit
python wp/tests/echeancier-runner/run.py e2e --name relecture-e2e
python wp/tests/echeancier-runner/run.py close
```

Toujours fermer le conteneur possédé, y compris en cas d’échec. Le banc réutilise une image publique synthétique existante et le ZIP autorisé de Subscriptions en lecture seule, sans accès au staging. Aucun Composer/README partagé modifié. Voir `wp/tests/echeancier-runner/README.md` et les reçus dans `production/C-05/preuves/`.
