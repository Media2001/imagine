# À faire — file des consignes actives pour Hermès

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 22 novembre 2026, 11 h 40.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **21/11/2026 — qui valide quoi**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

File du 22/11, 11 h 40. Ton rapport de 3 h 44 est lu.

**1. Corrections de C-07** — `corrections/C-07.md`, section « Instructions pour Hermès ». Applique les instructions 1 à 7 et 9. L'instruction 8 (registre des écarts) est faite par Claude : n'écris pas dans `docs/`. Délai : deux heures. Puis redépose `PRET`.

Précisions de Claude sur son propre brief, qui répondent aux questions 1 à 3 de la fusion (ce ne sont pas des arbitrages de Ced, seulement la levée d'ambiguïtés de rédaction) :

- **Grâce.** Un abonné en délai de grâce à la clôture **figure** dans la liste, quel que soit `paiementValide`. C'est l'interprétation du brief ; elle reste soumise à la décision d'Imagine sur le délai de grâce, donc isole-la derrière un réglage unique.
- **A-SANSMAIL.** « Exclu des envois » voulait dire « par email ». Il **figure** dans la liste postale. `docs/recette/profils.md` est corrigé.
- **Doublons.** Deux exemplaires conservés, chacun signalé en anomalie. Le rapprochement s'appuie sur `destinataire_id` quand il est commun, et sinon sur le nom et l'adresse normalisés.

Reste ouvert, pour Imagine : l'ordre, les colonnes et le format attendus par le routeur. Colonnes provisoires d'ici là. La borne de fin suit la règle de C-01 : ne la redéfinis pas.

Les six avertissements de style que tu signales dans `tests/Echeancier/run.php` (lot C-05) : corrige-les dans cette passe, ils ne touchent à aucune règle.

**En attente d'une réponse de Ced — ne pas reprendre :**

- **A-01, publication.** Ton diagnostic est clair : la création normale d'un site dans l'outil active la licence Novamira et provisionne l'accès agent, sans option pour l'éviter. La question est posée à Ced.
- **C-05, paiement en quatre fois.** La contradiction que tu as trouvée est réelle (une commande entre la date commune et la clôture donnerait cinq paiements dans l'année de date à date). Le choix entre A, B et C est posé à Ced.
- **C-06, décision d'accès.** Vérifié au second tour. Trois questions sur les droits sont posées à Ced.

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
