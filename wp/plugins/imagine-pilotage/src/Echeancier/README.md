# Échéancier — C-05, prototype non branché

- `Planificateur` et `Versement` : PHP pur. Le calendrier, les numéros et les dates communes sont fournis par `Imagine\Pilotage\Numeros\Moteur` (C-01), jamais recalculés ici.
- `planifier(Annee, DateTimeImmutable $finEngagement, ?int $margeJours = null)` : quatre positions ordonnées **par bloc de quatre numéros**. L’argument historique de fin reste un contexte numérique validé, pas une borne de paiement. La marge absente refuse `MARGE_OBLIGATOIRE`. Aucune lecture d’horloge.
- Première année : le premier versement prend la date de commande. Reconduction liée par C-01 : tous les versements gardent la date commune.
- Refus avant résultat exploitable : marge absente ou non positive, calendrier incomplet, fin numérique non postérieure au début, dates non strictement croissantes. Une exception n’est pas un échéancier partiel à exécuter.
- `RaccordManuel` : adaptateur Woo de démonstration **uniquement** pour une fixture marquée C05, drapeau manuel explicite et passerelle vide. Aucun hook enregistré, aucun automatisme ajouté au plugin. Il ne prouve ni un traitement des rejets ni l’idempotence financière concurrente.

**Option A du 22/11 :** cinq dates dans une fenêtre anniversaire sont acceptées, jamais cinq positions dans un bloc. Toutes les communes et la marge restent intactes. Voir `production/C-05/proposition.md`.

- `Reglages` : marge civile positive sans défaut, rejet `restent_dues` (défaut) / `annuler_restantes`, tarif `fige_bloc` (défaut) / `courant_impayes`. Chaque choix et leurs interactions sont testés ; les valeurs numériques représentatives 1/3/7/30 et les entrées invalides aussi. `montantsRestants` projette en centimes les seuls rangs impayés, sans opération financière ni calcul de droits.
- `ReglagesAdministration` : option `imagine_c05_reglages`, Settings API, capacité `manage_woocommerce`, nonce standard, sorties échappées, pas de REST. Saisie invalide : ancienne option conservée. Option corrompue : lecture fermée. Vide : moteur bloqué.
- Seam parent après autoload, une fois : `(new Imagine\Pilotage\Echeancier\ReglagesAdministration())->enregistrer();`. Aucun bootstrap commun modifié. Le banc active explicitement l’adaptation. Lire les réglages puis passer `margeJours` au moteur ; fournir à la projection la somme figée du bloc et les rangs confirmés payés.

Tests depuis la racine du dépôt, avec Python déjà présent (aucune installation hôte) :

```bash
python wp/tests/echeancier-runner/run.py prepare
python wp/tests/echeancier-runner/run.py unit --name relecture-unit
python wp/tests/echeancier-runner/run.py e2e --name relecture-e2e
python wp/tests/echeancier-runner/run.py close
```

Toujours fermer le conteneur possédé, y compris en cas d’échec. Le banc réutilise une image publique synthétique existante et le ZIP autorisé de Subscriptions en lecture seule, sans accès au staging. Aucun Composer/README partagé modifié. Voir `wp/tests/echeancier-runner/README.md` et les reçus dans `production/C-05/preuves/`.
