# État des chantiers — mis à jour le 11 novembre 2026

## En cours

| Chantier | État | Prochaine étape | Qui |
|---|---|---|---|
| Dépôt | Créé, squelette poussé ; cloné sur le NUC (`C:\Users\Ced\imagine`, alias SSH `github-imagine`) | — | — |
| Hermès sur ce dépôt | Pas encore branché | Donner à Hermès `prompts/consigne-permanente.md` et créer ses passages | Ced |
| Synchronisation Git | `scripts/sync.ps1` prêt, pas encore planifié | Créer la tâche planifiée « IMAGINE - synchro » (toutes les 5 min) | Ced |
| Circuit de relecture | Rôles écrits (`relecteurs/`) ; `scripts/relire.ps1` adapté aux lots (installe les dépendances de test, Codex puis Claude, fusion, passe de vérification), **pas encore testé** | Lancer une première fois à la main sur le premier lot `PRET`, puis créer la tâche planifiée « IMAGINE - relecture » | Ced |
| Lot 00 — couverture des extensions | Brief écrit | Production | Hermès |
| Lot 01 — règle des numéros | Brief écrit | Production | Hermès |
| Questions ouvertes | 9 points dans `docs/decisions.md` | Réponses | Ced |

## En attente de tiers

| Sujet | Qui | Effet |
|---|---|---|
| Grille tarifaire, tarif solidaire, accès découverte | Imagine | Bloque le tunnel et les emails |
| Champs attendus par Odoo, email de facture | Step | Bloque le document d'interface |
| Documentation et accès de test CoopHub | Imagine, CoopHub | Sans réponse avant la fin de l'étude : intégration par lien |
| Maquettes | Design | Bloque les gabarits |
