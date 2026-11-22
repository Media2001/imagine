# À faire — file des consignes actives pour Hermès

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 22 novembre 2026, 13 h 20.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **22/11/2026 — une règle ouverte devient un réglage**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

File du 22/11, 13 h 20. La doctrine a changé (§4 : une règle ouverte devient un réglage) : relis-la.

**1. A-01, publication — accord de Ced donné le 22/11 à 13 h 11.** Ced t'autorise à **créer, démarrer, arrêter et supprimer des sites de test dans l'outil de staging par son usage normal**, y compris l'activation automatique de la licence Novamira et de l'accès agent que l'outil effectue à chaque création (« l'outil est là pour ça »). Termine `briefs/A-01-publication.md` :

- sites de test nommés `imagine-test-…` uniquement ; supprime-les à la fin et vérifie leur absence ;
- tu ne modifies ni le code de l'outil, ni ses modèles, ni les autres sites ;
- sur un site de test, l'accès agent créé par l'outil ne sert à rien : ne l'utilise pas. Après injection de la base et des fichiers vérifiés, contrôle et écris dans le rapport ce qu'il reste de Novamira sur le site (extension présente ou non, identifiants valides ou non) ;
- preuve attendue : archive fictive avec Subscriptions et Memberships → site de test joignable, statut « vérifié », extensions et réglages intacts ; puis le cas d'échec avec une clé piégée ;
- livre la commande unique et son mode d'emploi pour Ced, puis `production/A-01/PRET`.

Tu ne lances toujours aucun import d'Imagine et tu n'ouvres pas son archive : c'est Ced qui lancera la commande. Une demi-journée. **Ce lot passe avant tout le reste.**

**2. C-05, paiement en quatre fois — reprise.** `docs/arbitrages-2026-11-22.md` : option A retenue (quatre échéances par bloc de quatre numéros ; une fenêtre de date à date peut en contenir cinq), et les trois autres questions deviennent des réglages avec leur valeur par défaut. Adapte l'échéancier, ses tests et la proposition, rejoue la preuve sur le vrai Subscriptions, puis dépose `production/C-05/PRET`. Une demi-journée.

**3. C-06, décision d'accès — trois réglages.** `docs/arbitrages-2026-11-22.md` : sortie à venir, PDF pour un robot vérifié, PDF antérieur à l'abonnement. Chaque réglage avec sa valeur par défaut et ses tests dans les deux positions ; le motif provisoire disparaît. Deux heures. Redépose `PRET`.

**4. C-07, liste d'envoi — format d'export en réglage.** Colonnes et ordre configurables, colonnes provisoires par défaut. Une heure, à faire seulement si ce n'est pas déjà le cas. Redépose `PRET` uniquement si tu as modifié quelque chose.

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
| A-00 Couverture des extensions | 20/11, corrigé le 21/11 | **Clos le 21/11** |
| C-01 Règle des numéros | 20/11, corrigé le 21/11 | **Clos le 21/11** |
| C-02 Numéro d'entreprise | 20/11, corrigé le 21/11 | **Clos le 21/11** |
| C-03 Vérification des robots | 20/11, corrigé le 21/11 | Bloquant C03-01 corrigé. **Clos le 21/11** |
| C-04 File du connecteur | 20/11, corrigé le 21/11 | **Clos le 21/11** |
| A-01, import et vérification hors ligne | 21/11 | Fait et prouvé sur données fictives ; publication restante (consigne 1) |
