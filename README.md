# IMAGINE — dépôt de production de la refonte du site

Refonte du site d'Imagine (magazine, coopérative de presse) : WordPress + WooCommerce, paywall côté serveur, back-office sur mesure, connecteur vers Odoo. Référence : `docs/cahier-des-charges-v3.1.pdf`.

**Règle n°1 : ce dépôt est la seule source de vérité.** Un fichier qui n'est pas ici n'existe pas pour les agents.
**Règle n°2 : jamais de secret ici** (mot de passe, clé d'API, token, wp-config, .env), même si le dépôt est privé.
**Règle n°3 : jamais de donnée réelle ici** (abonnés, export Access, contacts Brevo, clients Stripe). Uniquement des jeux fictifs.
**Règle n°4 : rien n'est déployé ni branché sur un compte réel sans un GO écrit de Ced** nommant la tâche.

## Organisation

| Dossier | Qui écrit | Contenu |
|---|---|---|
| `docs/` | Claude (avec Ced) | Cahier des charges, synthèse, décisions, registre des écarts, et `recette/` (profils de test et cas d'acceptance). |
| `doctrine/` | Claude (avec Ced) | Règles de production et leur pourquoi. Source unique. |
| `briefs/` | Claude (avec Ced) | Un fichier par lot de travail, préfixé par son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. File d'attente d'Hermès. |
| `prompts/` | Claude | Consigne permanente et grands prompts datés. |
| `wp/` | Hermès | Le code livrable : `plugins/`, `themes/`, `tests/`, et `outils/` (scripts rejouables sur l'existant). |
| `production/<lot>/` | Hermès | Ce qui n'est pas du code : études, notes de conception, `PRET`. |
| `relectures/<lot>/` | Claude Code, Codex | `claude.md` et `codex.md`, écrits séparément. |
| `corrections/<lot>.md` | Claude Code | Fusion des deux relectures + « À arbitrer par Ced ». |
| `files/rapports/` | Hermès | Rapports de passage. |
| `scripts/` | Claude | Synchronisation Git du NUC, relecture. |
| `docker-compose.yml`, `docker/` | Claude | Staging local sur le NUC : WordPress, base fictive, WP-CLI, PHP et Composer pour les tests. |
| `relecteurs/` | — | Fichiers de rôle des relecteurs (`CLAUDE.md`, `AGENTS.md`). |

## Le circuit

1. Claude écrit le brief du lot dans `briefs/` et l'inscrit dans `A-FAIRE.md`.
2. Hermès produit (`wp/` pour le code et ses tests, `production/<lot>/` pour le reste), puis dépose `production/<lot>/PRET`.
3. Codex et Claude Code relisent chacun de leur côté (`relectures/<lot>/`).
4. Claude Code fusionne (`corrections/<lot>.md`).
5. Ced et Claude arbitrent ; Hermès applique les corrections.
6. La clôture dépend de la nature du lot :
   - **Lot de code ou d'étude, sans rien de visuel** : il est clos par Claude, sans intervention de Ced, quand ses tests passent, que les deux relectures et la fusion sont faites, que la vérification du second tour conclut « prêt pour la validation » et qu'il ne reste aucune question ouverte pour Ced dans ce lot. Claude l'inscrit comme clos dans `A-FAIRE.md`.
   - **Lot visuel** (thème, écrans, emails) : Ced le valide lui-même.
   - **Règles métier** : les questions « à arbitrer » restent tranchées par Ced, ou par Imagine quand elles lui reviennent.
   - **Tout ce qui touche au réel** (import de la production, staging ouvert aux agents, compte réel, achat, déploiement) : GO écrit de Ced, règle n°4.

Tout se passe sur la branche `main`. Seule la tâche de synchronisation touche à Git (`scripts/sync.ps1`).

## Points de reprise

- `A-FAIRE.md` : file de la voie 1, l'existant (tenue par Claude, lue par Hermès à chaque cycle).
- `A-FAIRE-2.md` : file de la voie 2, ce qui se voit (site de démonstration fictif), suivie par une deuxième session d'Hermès.
- `ETAT.md` : où en est chaque chantier.
- `JOURNAL.md` : une ligne par jour.
- `docs/decisions.md` : ce qui est tranché, ce qui reste ouvert.
- `docs/ecarts.md` : demandes hors cahier des charges et retards de tiers, datés.

## Ce qui est remis au client

À la réception, Imagine reçoit `wp/` et la documentation technique. Le reste du dépôt (briefs, prompts, relectures, rapports) est l'outillage interne de production.
