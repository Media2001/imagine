# Arbitrages de Ced — 21 novembre 2026

Réponses de Ced aux questions posées par les fusions du 20/11 (`corrections/<lot>.md`, section « À arbitrer par Ced »). Ced a validé en bloc, le 21/11 à 10 h 20, les réponses proposées par Claude. Ce fichier fait foi pour Hermès.

Une question absente de ce fichier **n'est pas tranchée** : elle reste ouverte et ne doit pas être appliquée.

## C-01 — Règle des numéros

| Question de la fusion | Réponse |
|---|---|
| 1. Accès numérique pendant une suspension pour impayé | **Coupé** dès la suspension (§3.8). Comportement actuel conservé. |
| 2. Activation un 29 février | Fin de l'accès au **28 février** de l'année suivante. |
| 3. Calendrier dont les clôtures ne suivent pas l'ordre des sorties | **Refusé à la construction**, avec un message qui nomme les numéros en cause. |

## C-02 — Numéro d'entreprise

| Question de la fusion | Réponse |
|---|---|
| 1. Documentation des conditions d'accès BCE et VIES | **Reportée.** Elle ne fait pas partie de C-02 ; l'instruction correspondante de la fusion n'est pas à appliquer. |
| 2. Motif distinct `PremierChiffre` | **Accepté tel quel.** |
| 3. Recherche de dénomination en ligne | **Contrôle de format local seul** pour l'instant. Aucun lot d'étude ni service activé tant que la question n'est pas tranchée avec le pilote du projet (`decisions.md`, point 8). |

## C-03 — Vérification des robots

| Question de la fusion | Réponse |
|---|---|
| 1. Durées 3 600 s / 60 s / 200 ms | Délai de résolution porté à **1 000 ms**. Cache positif : 3 600 s, inchangé. Cache négatif de 60 s **uniquement pour un refus établi** (nom hors domaine, résolution directe qui ne redonne pas l'adresse, adresse hors plages). **Un délai dépassé ou une panne de résolution n'est pas mis en cache** : la requête en cours est refusée, la suivante retente. Les trois valeurs restent dans la configuration. |
| 2. Clé de cache intégrant l'identité du robot et l'empreinte de configuration | **Oui**, une fois C03-01 corrigé. |
| 3. Liste des robots | **Googlebot et Bingbot seulement.** À confirmer par le référenceur ; aucun autre agent activé d'ici là. |

Question 4 (répartiteurs de confiance et adresse IP normalisée) : ce n'est pas une correction de code. C'est un prérequis du branchement, à faire confirmer par l'hébergeur quand il sera choisi. Garde-le dans `notes.md`.

## C-04 — File du connecteur

| Question de la fusion | Réponse |
|---|---|
| Injection de formule dans l'export CSV | **Neutralisée dans le code** dès ce lot. Documente la règle appliquée pour que Step sache la lire. |
| Blocage des événements suivants du même abonnement après une quarantaine ou des essais épuisés | **Maintenu**, jusqu'à une reprise administrative tracée. |
| Dépôt rejeté pour clé connue mais contenu différent | **Alerte.** |

Restent ouvertes, hors de la portée d'Hermès : l'unicité transactionnelle côté destinataire (question pour Step), et le choix entre connecteur intégré et n8n.

## A-00 — Couverture des extensions

| Question de l'étude | Réponse |
|---|---|
| 1. Paiement en quatre fois | Exactement **quatre paiements, initial compris, par année d'engagement de date à date**, et non par année civile. Tu peux **soumettre** un mécanisme qui écarte la date commune en trop ; c'est une proposition à relire, pas une mise en œuvre. |
| 10. Reprise des abonnés en ligne | **Même compte Stripe**, références conservées sur une copie fidèle, **sans import CSV** des abonnés en ligne. C'est la conséquence de la décision de repartir de la production. |

Restent ouvertes, à trancher avec le pilote du projet et Imagine : les questions 2 à 9 de l'étude, et les questions A (carte puis SEPA), B (retrait immédiat ou délai de grâce au premier rejet) et C (licence Teams) de la fusion.
