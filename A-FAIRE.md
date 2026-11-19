# À faire — file des consignes actives pour Hermès

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 19 novembre 2026, 20 h.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **19/11/2026 — outil de staging et Novamira à la place de Docker**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

**1. `briefs/C-01-regle-des-numeros.md`** — chantier C. Moteur de la règle des numéros en PHP pur, avec ses tests. Le brief a changé le 19/11 (plus de Docker) : relis-le.

**2. `briefs/A-00-couverture-extensions.md`** — chantier A. Étude : ce que les extensions retenues font nativement, sources officielles à l'appui. Aucune installation, aucun achat.

**Retiré de ta file : A-01.** L'import neutralisé et anonymisé est repris par Claude Code dans l'outil de staging de Ced (`prompts/2026-11-19-staging-imagine.md`). Ne produis rien dans `wp/outils/`. Si tu avais commencé, laisse en l'état et dis-le dans ton rapport.

**Tu n'as accès à aucun staging pour l'instant.** Tu y accéderas par Novamira quand Ced l'écrira ici.

## En attente (ne pas commencer)

### A · L'existant

| Lot | Contenu | Attend |
|---|---|---|
| A-01 Import neutralisé | Scripts `wp/outils/staging/` et lanceur `wp/outils/bascule/`, intégrés à l'outil de staging | Claude Code (hors file d'Hermès) |
| A-02 Audit | Versions de WordPress, PHP, WooCommerce, Subscriptions, Memberships, passerelles ; extensions et thème actifs ; taille de la base ; ce qui doit être retiré | Staging créé et vérifié |
| A-03 Tests de non-régression | Avant toute mise à jour : un abonné accède à ses contenus, un non-abonné non, un renouvellement de test passe | A-02 |
| A-04 Mise à jour | Memberships et ce qui en dépend, par script rejouable ; A-03 rejoué après | A-03, licences |
| A-05 Nettoyage | Retrait des extensions et réglages inutiles, par script rejouable | A-02 |
| A-06 Import des abonnés hors ligne | Base Access, abonnés sans email (§4.3) | Export fourni par Imagine ; règle sur les données réelles |

### B · Le thème

| Lot | Contenu | Attend |
|---|---|---|
| Modèle éditorial | Numéro, article, thématique, événement, partenaire (§4.2) ; rattachement des contenus existants | A-02, licence ACF Pro |
| Gabarits et mode lecture | §3.1 à §3.3 | Maquettes |
| Performance et accessibilité | Seuils du chapitre 5 | Gabarits |

### C · Le code sur mesure

| Lot | Contenu | Attend |
|---|---|---|
| Paywall serveur et test d'étanchéité | §3.9, §4.4 | A-00, A-04 |
| Abonnement et échéances | Branchement de C-01 sur Subscriptions | A-00, C-01, licences |
| Connecteur en mode export | File, rejeu, quarantaine, export quotidien (§2.4, §2.5) | Choix n8n ou intégré ; champs attendus par Step |
| Back-office | Échéances, justificatifs, liste d'envoi, extractions (§3.13) | Lots précédents |
| Tunnel et emails | §3.7, §3.8 | Décisions 3 à 5 d'Imagine |

## Terminé

(rien)
