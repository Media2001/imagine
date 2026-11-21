# À faire — file des consignes actives pour Hermès

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 21 novembre 2026, 13 h.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **19/11/2026 — outil de staging et Novamira à la place de Docker**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

La file du 21/11 au matin est rendue (voir « Terminé »). Nouvelle file du 21/11, 13 h.

**1. `briefs/A-01-publication.md`** — dernière étape de A-01. Deux arbitrages lèvent ton blocage : le filtrage réseau au niveau du système n'est plus exigé après vérification, et la publication passe par l'usage normal de l'outil de staging (site vide créé par son API, puis base et fichiers vérifiés injectés), sans modifier son code. Une demi-journée.

**2. `briefs/C-06-decision-acces.md`** — chantier C. La décision d'accès du paywall en un seul endroit, PHP pur, fermée par défaut. Une demi-journée.

**3. `briefs/C-05-echeancier-quatre-fois.md`** — chantier C. Proposition de mécanisme pour le paiement en quatre fois, avec preuve sur site jetable et le vrai Subscriptions. Une demi-journée.

Les lots 2 et 3 sont indépendants de A-01 : si A-01 se bloque, passe à la suite.

**Où lancer les tests PHP.** Dans un conteneur jetable, comme jusqu'ici. Rien sur Windows.

**Cas d'acceptance.** `docs/recette/` : proposition du 19/11, pas encore validée. Ne les automatise pas, ne les modifie pas.

**Staging et Novamira.** Tu n'utilises Novamira que sur un staging au statut « vérifié ». Il n'en existe pas encore. L'ancienne copie d'Imagine reste arrêtée.

**Registre des écarts.** Tu n'écris pas dans `docs/`. Signale les écarts dans tes notes, comme tu l'as fait : Claude les reporte.

## En attente (ne pas commencer)

### A · L'existant

| Lot | Contenu | Attend |
|---|---|---|
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
| Connecteur : branchement | Branchement de C-04 sur WooCommerce et sur Odoo ou n8n | C-04 ; choix n8n ou intégré ; champs attendus par Step |
| Profils de test | Script de création des profils de `docs/recette/profils.md` sur le staging | Validation des profils par Ced ; staging vérifié |
| Back-office | Échéances, justificatifs, liste d'envoi, extractions (§3.13) | Lots précédents |
| Tunnel et emails | §3.7, §3.8 | Décisions 3 à 5 d'Imagine |

## Terminé

| Lot | Rendu | État au 21/11 |
|---|---|---|
| A-07 Exposition de l'outil de staging | 20/11 | Clos |
| A-00 Couverture des extensions | 20/11, corrigé le 21/11 | Vérifié : prêt pour la validation de Ced |
| C-01 Règle des numéros | 20/11, corrigé le 21/11 | Vérifié : prêt pour la validation de Ced |
| C-02 Numéro d'entreprise | 20/11, corrigé le 21/11 | Vérifié : prêt pour la validation de Ced |
| C-03 Vérification des robots | 20/11, corrigé le 21/11 | Bloquant C03-01 corrigé. Vérifié : prêt pour la validation de Ced |
| C-04 File du connecteur | 20/11, corrigé le 21/11 | Vérifié : prêt pour la validation de Ced |
| A-01, import et vérification hors ligne | 21/11 | Fait et prouvé sur données fictives ; publication restante (consigne 1) |
