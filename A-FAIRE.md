# À faire — file des consignes actives pour Hermès

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 20 novembre 2026, 13 h 40.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **19/11/2026 — outil de staging et Novamira à la place de Docker**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

**0. `briefs/A-07-exposition-outil-staging.md`** — contrôle en lecture seule : l'outil de staging est-il joignable depuis Internet ? Une heure, aucune modification. À faire en premier.

**1. `briefs/A-01-reprise.md`** — chantier A, lot A-01. **Changement de principe, décidé le 20/11 après lecture de ton rapport** : le staging doit rester fidèle à la production. On garde les extensions, les réglages et les tables ; on ne retire que ce qui est dangereux ; on signale ce qu'on ne connaît pas. Cinq points seulement bloquent le statut « vérifié ». Lis le brief en entier avant de reprendre : il remplace les listes fermées de la version actuelle. Délai : une demi-journée, puis tu passes à la suite.

**Licences WooCommerce (20/11).** Ced dispose des licences. Il dépose les archives de WooCommerce Subscriptions et de WooCommerce Memberships dans le dossier des extensions premium de l'outil de staging (`plugins`), hors du dépôt. Dès qu'elles y sont : installe-les sur tes sites jetables et teste réellement ce qui ne l'était pas dans A-01 (mode staging de Subscriptions, abonnements en stockage classique et HPOS, adhésions Memberships, actions planifiées de renouvellement). Règles : aucune archive, aucune clé de licence et aucun identifiant du compte WooCommerce.com dans le dépôt ni dans un rapport ; ne connecte aucun site au compte WooCommerce.com ; si les archives ne sont pas encore là, continue sans elles et dis-le.

**2. `briefs/C-01-regle-des-numeros.md`** — chantier C. Moteur de la règle des numéros en PHP pur, avec ses tests. Le brief a changé le 19/11 (plus de Docker) : relis-le.

**3. `briefs/A-00-couverture-extensions.md`** — chantier A. Étude : ce que les extensions retenues font nativement, sources officielles à l'appui. Aucune installation, aucun achat.

**4. `briefs/C-04-file-connecteur.md`** — chantier C. Cœur de la file d'attente du connecteur : idempotence, quarantaine, rejeu, export quotidien. PHP pur, sans Odoo.

**5. `briefs/C-03-verification-robots.md`** — chantier C. Décider si une requête vient d'un robot d'indexation vérifié. PHP pur, résolution DNS simulée dans les tests.

**6. `briefs/C-02-numero-entreprise.md`** — chantier C. Normalisation et contrôle du numéro d'entreprise belge. PHP pur. Aucune recherche en ligne.

Les lots C-01 à C-04 sont indépendants entre eux et ne dépendent ni du staging ni des licences.

**Où lancer les tests PHP.** Rien ne s'installe sur Windows. Tu peux lancer `composer install` et `composer test` dans un conteneur jetable de l'outil de staging, sans base et sans lien avec le staging d'Imagine. Si ce n'est pas possible, écris le code et les tests, dis qu'ils n'ont pas été lancés, et ne dépose pas `PRET`.

**Cas d'acceptance.** `docs/recette/` contient les profils de test et le catalogue des cas (proposition du 19/11, pas encore validée). Chaque brief cite les cas qu'il sert. Ne les automatise pas encore et ne les modifie jamais : si un cas te semble faux ou incomplet, dis-le dans ton rapport.

**Staging et Novamira.** Tu n'utilises Novamira que sur un staging au statut « vérifié ». La connexion établie avant le 19/11 sur le staging non neutralisé ne doit plus servir.

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

(rien)
