# État des chantiers — mis à jour le 19 novembre 2026, 20 h

## Mise en route

| Sujet | État | Prochaine étape | Qui |
|---|---|---|---|
| Dépôt | Créé ; cloné sur le NUC (`C:\Users\Ced\imagine`, alias SSH `github-imagine`) | — | — |
| Hermès sur ce dépôt | Démarré le 19/11 | Premier rapport dans `files/rapports/` | Hermès |
| Synchronisation Git | Tâche planifiée « IMAGINE - synchro » créée le 19/11, toutes les 5 min | — | — |
| Circuit de relecture | `scripts/relire.ps1` adapté aux lots ; se lance sans erreur, **pas encore testé sur un lot** | Lancer à la main sur le premier lot `PRET`, puis planifier « IMAGINE - relecture » | Ced |
| Staging | Pas de Docker sur le NUC : on utilise l'outil de staging de Ced, avec Novamira pour l'accès des agents. Étape « site à abonnements » à ajouter à l'outil (`prompts/2026-11-19-staging-imagine.md`). Le `docker-compose.yml` du dépôt n'est plus utilisé | Hermès ajoute l'étape ; puis retirer Docker du dépôt | Hermès, puis Claude |
| Exécution des tests PHP | Consigne donnée à Hermès : conteneur jetable de l'outil de staging, rien sur Windows | Confirmer dans son premier rapport que ça fonctionne | Hermès |
| Recette | Profils de test et 41 cas d'acceptance proposés dans `docs/recette/` | Relecture par Ced, puis validation par le pilote du projet | Ced |

## A · L'existant

On repart de la production (décision du 11/11) : copie neutralisée et anonymisée dans Docker, audit, tests de non-régression, mise à jour de Memberships, nettoyage. Tout par scripts rejouables, parce que l'opération sera refaite le jour de la bascule.

| Lot | État | Prochaine étape | Qui |
|---|---|---|---|
| Sauvegarde de production | Pas encore récupérée | Export SQL + `wp-content`, déposés sur le NUC **hors du dépôt** | Ced |
| A-01 Import neutralisé | Audit de l'outil rendu par Hermès le 19/11 (rien n'est neutralisé aujourd'hui) ; accord de Ced donné | Scripts, tests sur site jetable, `production/A-01/notes.md` | Hermès |
| Staging Imagine existant | Copie de production non neutralisée, au statut « running » | L'arrêter ou vérifier le mode staging de Subscriptions ; le détruire quand le nouveau parcours est validé | Ced |
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
| C-04 File du connecteur | Brief écrit | Production | Hermès |
| C-03 Vérification des robots | Brief écrit | Production | Hermès |
| C-02 Numéro d'entreprise | Brief écrit | Production | Hermès |
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
