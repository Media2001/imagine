# À faire — voie 1 : l'existant

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 25 novembre 2026, 22 h 30 (passage automatique).

**Deux voies depuis le 23/11.** Ce fichier est la file de la voie 1. Une deuxième session d'Hermès suit `A-FAIRE-2.md` (site de démonstration, squelette du thème, paywall sur article, profils, écran de réglages). Lis la section « Les deux voies » de la consigne permanente. Ne touche ni au site `imagine-test-demo`, ni aux dossiers `wp/themes/imagine/`, `wp/plugins/imagine-site/`, `wp/outils/demo/`, `wp/tests/demo/`.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **22/11/2026 — une règle ouverte devient un réglage**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

File du 25/11, 22 h 30. Tes rapports de 19 h 41 à 22 h 18 sont lus : corrections d'A-05, puis A-08, A-09 et A-10 rendus, corrections d'A-08 et d'A-09 appliquées, file vide à 22 h 18. **A-05 est clos** (vérification « prêt », cinq instructions sur cinq). A-08 et A-09 attendent leur vérification, A-10 sa relecture. Arbitrages : `docs/arbitrages-2026-11-25.md`, section « Passage automatique de 22 h 30 ».

**PRIORITÉ ABSOLUE (26/11, 1 h 20) — `briefs/A-01-archive-reelle-4.md`** — le premier import réel complet a échoué à l'étape « base », après cinquante minutes, sur un refus muet (`COMMAND_REFUSED`, sortie d'erreur jetée). Plus aucun refus muet, compatibilité d'une base de production réelle, et un mode qui répète la base seule en quelques minutes. Trois heures. **Passe avant tout le reste de cette file. Ced attend pour relancer.**

**0. Corrections et vérifications d'A-08, A-09, A-10** : si l'une revient « à corriger » (`corrections/<lot>.md` plus récent que ton `PRET`), elle passe avant tout le reste. Tes décisions à défaut sont confirmées : idempotence « métier » d'A-08 (le fichier de maintenance et l'expiration d'un cache natif de Subscriptions peuvent être rafraîchis au second passage, rien d'autre) ; refus des adresses à requête vide dans A-09 ; conventions de comptage d'A-10 (douze mois calendaires, commandes annulées ou remboursées comptées comme commandes, limite de paiements initial compris).

**1. A-08, question III.6 : tranchée.** `wp/outils/bascule/repetition.md` garde son contenu exact, et tu ajoutes **une phrase simple en tête de chaque bloc** qui dit ce que le bloc fait et ce qu'on doit voir à la fin. Aucune commande ne change. C'est de la documentation : pas de rejeu Docker, la preuve est le diff (que des lignes de prose ajoutées) et l'empreinte du fichier mise à jour dans ton manifeste. Un quart d'heure. Si la vérification d'A-08 est en cours quand tu lis ceci, fais-le quand même et redépose `PRET`.

**2. `briefs/A-11-inventaire-des-adresses.md`** — la liste des adresses publiques d'un site, en lecture seule, pour que le référenceur puisse écrire le plan que vérifie A-09 (§4.3). Trois heures.

**3. `briefs/A-12-inventaire-des-contenus.md`** — la photographie de la structure des contenus (types, taxonomies, clés de champs, pièces jointes), en lecture seule, avant le modèle éditorial (§4.3, §4.2). Des structures et des nombres, jamais de valeurs. Trois heures.

**4. `briefs/A-13-controle-export-hors-ligne.md`** — l'outil qui contrôle un export d'abonnés hors ligne (doublons, échéances, rejets) sans rien importer, sur fichier fictif (§4.3). Une demi-journée.

**Règle.** Une fusion « à corriger » (`corrections/<lot>.md`) arrivée après la dernière mise à jour de cette file est à prendre tout de suite, avant le lot en cours, sans attendre que la file la cite. Avant de t'arrêter sur « file vide », regarde s'il y a une fusion plus récente que ton dernier `PRET` pour chacun de tes lots rendus.

**Preuves.** Tes derniers lots portent des centaines de fichiers de preuves par lot. Pour A-11 à A-13, qui ne font que lire : **un seul paquet de preuves par lot** (le dernier rejeu vert), les essais intermédiaires restent hors du dépôt.

Tu n'ouvres toujours pas l'archive d'Imagine ; Ced relance le diagnostic.

**Les écrans de réglages.** Dans C-05, C-06 et C-07, tu as livré des adaptateurs d'administration (pages de réglages WordPress). Ils ne font pas partie des lots clos : laisse-les en l'état. Ils sont repris par la voie 2 (lot C-10).

**Où lancer les tests PHP.** Dans un conteneur jetable, comme jusqu'ici. Rien sur Windows.

**Cas d'acceptance.** `docs/recette/` : proposition du 19/11, pas encore validée. Ne les automatise pas, ne les modifie pas.

**Staging et Novamira.** Tu n'utilises Novamira que sur un staging au statut « vérifié ». Il n'en existe pas encore. L'ancienne copie d'Imagine reste arrêtée.

**Registre des écarts.** Tu n'écris pas dans `docs/`. Signale les écarts dans tes notes, comme tu l'as fait : Claude les reporte.

## En attente (ne pas commencer)

### A · L'existant

| Lot | Contenu | Attend |
|---|---|---|
| A-02 Audit | Versions de WordPress, PHP, WooCommerce, Subscriptions, Memberships, passerelles ; extensions et thème actifs ; taille de la base ; ce qui doit être retiré | Staging créé et vérifié |
| A-05 Nettoyage sur le site réel | L'outil est clos ; son passage sur le staging d'Imagine attend un plan rempli par Ced | Audit réel, plan de Ced |
| Redirections : le plan | Plan validé (§4.3) ; l'outil de test est rendu (A-09), l'inventaire des adresses est en consigne 2 | Audit réel, référenceur |
| A-06 Import des abonnés hors ligne | Base Access, abonnés sans email (§4.3) ; l'outil de contrôle du fichier est en consigne 4 | Export fourni par Imagine ; règle sur les données réelles |

### B · Le thème

| Lot | Contenu | Attend |
|---|---|---|
| Modèle éditorial | Numéro, article, thématique, événement, partenaire (§4.2) ; rattachement des contenus existants | A-02, licence ACF Pro |
| Gabarits et mode lecture | §3.1 à §3.3 | Maquettes |
| Performance et accessibilité | Seuils du chapitre 5 | Gabarits |

### C · Le code sur mesure

| Lot | Contenu | Attend |
|---|---|---|
| Paywall serveur et test d'étanchéité | §3.9, §4.4 | Staging vérifié (le paywall de démonstration est fait en voie 2) |
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
| C-05 Échéancier en quatre fois | 22/11 | **Clos le 23/11** (bibliothèque et preuve sur le vrai Subscriptions ; écran de réglages exclu) |
| C-06 Décision d'accès | 21 et 22/11 | **Clos le 23/11** (bibliothèque ; écran de réglages exclu) |
| C-07 Liste d'envoi | 22/11 | **Clos le 23/11** (bibliothèque ; écran de réglages exclu) |
| A-01, import, vérification et publication | 22 et 23/11 | **Clos le 23/11** (mode diagnostic et règles de chemin vérifiés à 16 h 33) : qualifié en 6.9.1 sur archives fictives, mais refus `ARCHIVE_PATH` sur l'archive réelle. Limite : Subscriptions non testable en 6.9.1, le premier import réel fera foi. Ce n'est pas un accord d'import |
| A-01 Archive réelle (format AI1WM, plafonds, exclusions, diagnostic court) | 24/11 | **Clos le 25/11** |
| A-03 Non-régression | 24/11, corrigé le 25/11, complété le 25/11 | **Clos le 25/11** (trois compléments vérifiés, suite rejouée par le vérificateur : 1 012 tests) |
| A-04 Mise à jour | 25/11, corrigé le 25/11 | **Clos le 25/11** (six corrections vérifiées). Limite : montée 6.9.1 → 7.0 sur la pile commerciale et migrations historiques des extensions payantes non prouvables sur le banc ; la preuve se fera sur le staging d'Imagine vérifié. Ce n'est pas un accord pour toucher au réel |
| A-01 Troisième passe (base réelle) | 25/11 | **Clos le 25/11** (vérification n° 5, suite rejouée : 1 012 tests). Le diagnostic réel est à relancer par Ced. Ce n'est pas un accord d'import |
| A-05 Script de nettoyage | 25/11, corrigé le 25/11 | **Clos le 25/11** (cinq corrections vérifiées). L'outil exécute un plan et ne décide rien ; le plan du site réel sera rempli par Ced. Ce n'est pas un accord pour toucher au réel |
| A-08 Répétition de la bascule | 25/11, corrigé le 25/11 | Rendu ; vérification attendue (consigne 0) ; phrase d'introduction par bloc à ajouter (consigne 1) |
| A-09 Test des redirections | 25/11, corrigé le 25/11 | Rendu ; vérification attendue (consigne 0) |
| A-10 Inventaire des codes de réduction | 25/11 | Rendu ; relecture attendue (consigne 0) |
| T-01 Commande de rejeu | 23/11, corrigé le 23/11 | **Clos le 23/11** ; autorisation ajoutée au script de relecture |
| A-02 Script d'audit | 23/11, corrigé le 23/11 | **Clos le 23/11** (outil et banc fictif). L'audit réel reste à lancer |
