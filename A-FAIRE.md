# À faire — file des consignes actives pour Hermès

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 21 novembre 2026, 0 h 45.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **19/11/2026 — outil de staging et Novamira à la place de Docker**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

Les six lots de la première file sont rendus et relus (voir « Terminé »). Nouvelle file du 21/11.

**1. Corrections qui n'attendent aucun arbitrage.** Pour chaque fusion `corrections/<lot>.md`, applique les instructions de la section « Instructions pour Hermès » **qui ne dépendent pas d'une question posée à Ced** dans la section « À arbitrer ». Laisse les autres en l'état et liste-les dans ton rapport. Ordre :

1. `corrections/C-03.md` — **le bloquant C03-01 d'abord** (collision de la clé de cache), puis les instructions 2 à 4.
2. `corrections/C-01.md` — les deux défauts hors du cas nominal (C01-02, C01-03) et le reste.
3. `corrections/C-04.md`.
4. `corrections/C-02.md`.
5. `corrections/A-00.md`.

Pour chaque lot : rejoue toute la suite de tests, mets `notes.md` à jour avec ce qui est corrigé et ce qui attend, puis **redépose `PRET`** (la passe de vérification se déclenche dessus). Un rapport par lot. Tu ne tranches aucune des questions posées à Ced : en cas de doute sur la dépendance d'une instruction, ne l'applique pas et dis-le.

**2. `briefs/A-01-chemin-court.md`** — finir A-01 par le chemin le plus court : une commande unique pour Ced. Une demi-journée.

Les arbitrages de Ced sur les fusions arriveront ici dès qu'il les aura donnés.

**Où lancer les tests PHP.** Dans un conteneur jetable, comme tu l'as fait le 20/11. Rien sur Windows.

**Cas d'acceptance.** `docs/recette/` : proposition du 19/11, pas encore validée. Ne les automatise pas, ne les modifie pas.

**Staging et Novamira.** Tu n'utilises Novamira que sur un staging au statut « vérifié ». Il n'en existe pas encore. L'ancienne copie d'Imagine reste arrêtée.

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

| Lot | Rendu | Relecture |
|---|---|---|
| A-07 Exposition de l'outil de staging | 20/11 | Clos |
| A-00 Couverture des extensions | 20/11 | À corriger, sans bloquant |
| C-01 Règle des numéros | 20/11 | À corriger, sans bloquant |
| C-02 Numéro d'entreprise | 20/11 | À corriger, aucun défaut fonctionnel |
| C-03 Vérification des robots | 20/11 | À corriger, un bloquant (C03-01) |
| C-04 File du connecteur | 20/11 | À corriger |
