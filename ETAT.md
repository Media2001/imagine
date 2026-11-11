# État des chantiers — mis à jour le 11 novembre 2026, 18 h 30

## Mise en route

| Sujet | État | Prochaine étape | Qui |
|---|---|---|---|
| Dépôt | Créé ; cloné sur le NUC (`C:\Users\Ced\imagine`, alias SSH `github-imagine`) | — | — |
| Hermès sur ce dépôt | Pas encore branché | Donner à Hermès `prompts/consigne-permanente.md` et créer ses passages | Ced |
| Synchronisation Git | `scripts/sync.ps1` prêt, pas encore planifié | Créer la tâche planifiée « IMAGINE - synchro » (toutes les 5 min) | Ced |
| Circuit de relecture | `scripts/relire.ps1` adapté aux lots ; se lance sans erreur, **pas encore testé sur un lot** | Lancer à la main sur le premier lot `PRET`, puis planifier « IMAGINE - relecture » | Ced |
| Staging Docker | `docker-compose.yml` (WordPress vide) écrit, **jamais lancé**. Il sert aux tests ; le site lui-même viendra de la copie de production (lot A-01) | Premier `docker compose run --rm php php -v` sur le NUC | Ced |

## A · L'existant

On repart de la production (décision du 11/11) : copie neutralisée et anonymisée dans Docker, audit, tests de non-régression, mise à jour de Memberships, nettoyage. Tout par scripts rejouables, parce que l'opération sera refaite le jour de la bascule.

| Lot | État | Prochaine étape | Qui |
|---|---|---|---|
| Sauvegarde de production | Pas encore récupérée | Export SQL + `wp-content`, déposés sur le NUC **hors du dépôt** | Ced |
| A-01 Import neutralisé | Brief écrit | Production | Hermès |
| A-00 Couverture des extensions | Brief écrit | Production | Hermès |
| A-02 à A-06 | En attente | Voir `A-FAIRE.md` | — |

## B · Le thème

| Lot | État | Prochaine étape | Qui |
|---|---|---|---|
| Maquettes | Attendues | Livraison, mobile d'abord, avec le choix des polices | Design |
| Gabarits | En attente des maquettes | — | — |

## C · Le code sur mesure

| Lot | État | Prochaine étape | Qui |
|---|---|---|---|
| C-01 Règle des numéros | Brief écrit | Production | Hermès |
| Suite | En attente | Voir `A-FAIRE.md` | — |

## En attente de tiers

| Sujet | Qui | Effet |
|---|---|---|
| Grille tarifaire, tarif solidaire, accès découverte | Imagine | Bloque le tunnel et les emails |
| Champs attendus par Odoo, email de facture | Step | Bloque le document d'interface et le connecteur |
| Documentation et accès de test CoopHub | Imagine, CoopHub | Sans réponse avant la fin de l'étude : intégration par lien |
| Maquettes | Design | Bloque le chantier B |
| Export de la base Access | Imagine | Bloque A-06 |

## Calendrier visé

Mise en ligne estimée fin janvier 2027 (§10), donc site complet en préproduction début janvier pour la recette d'Imagine. Tenable si la sauvegarde de production et les maquettes arrivent d'ici fin novembre.
