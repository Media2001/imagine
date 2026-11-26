# À faire — voie 1 : l'existant

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 26 novembre 2026, 4 h 30 (passage automatique).

**Deux voies depuis le 23/11.** Ce fichier est la file de la voie 1. Une deuxième session d'Hermès suit `A-FAIRE-2.md` (site de démonstration, squelette du thème, paywall sur article, profils, écran de réglages). Lis la section « Les deux voies » de la consigne permanente. Ne touche ni au site `imagine-test-demo`, ni aux dossiers `wp/themes/imagine/`, `wp/plugins/imagine-site/`, `wp/outils/demo/`, `wp/tests/demo/`.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **22/11/2026 — une règle ouverte devient un réglage**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

File du 26/11, 4 h 30. Tes rapports de 2 h 27 à 3 h 55 sont lus, merci pour eux : quatrième passe d'A-01, corrections d'A-11, A-12 et A-13, manifestes d'A-08 et A-09, A-14 et A-15 rendus, file vide à 3 h 55. **La quatrième passe d'A-01, A-09, A-11 et A-12 sont clos** ; A-08 reste clos. A-14 et A-15 attendent leur relecture. Arbitrages : `docs/arbitrages-2026-11-26.md`, passage de 4 h.

**0. A-13 : un correctif ciblé, avant tout le reste** (`relectures/A-13/verification.md`). Ta suite échoue sur le poste de contrôle : Windows, Python 3.14, console en cp1252 ; `test_repository_output_refused_without_touching_fixture` plante en lisant la sortie d'un sous-processus, alors que `LIVRAISON.md` affirme « 40 tests, 0 échec ». Une preuve qui ne se rejoue pas sur le poste de Ced n'en est pas une. Tes corrections IBAN et doublons sont conformes et restent acquises. À faire :
   - instruction 1 de la fusion, comme elle était écrite : c'est **le test** qui fixe l'encodage de son sous-processus (le dictionnaire `env=` à l'appel, lignes 90-91), pas l'outil. La modification de l'outil (`reconfigure(errors='backslashreplace')`) n'était pas demandée : retire-la si aucun test ne la justifie, sinon garde-la avec le test qui la justifie, et dis lequel des deux ;
   - instruction 4 : une correspondance qui déclare `types_abonnement_autorises` sans mapper `type_abonnement` est refusée, message en français, un test ;
   - instruction 5 : le double libellé « champ obligatoire absent » et « adresse postale incomplète » est dédoublonné ou documenté ;
   - instruction 6 : la phrase dans `LIVRAISON.md` (`rejouer.ps1` ne couvre pas A-13) ; et `LIVRAISON.md` dit avec quel Python et quel encodage la suite a réellement tourné.
   La preuve : la suite entière verte **avec l'encodage de console de Windows forcé** (`PYTHONIOENCODING=cp1252`, puis `PYTHONUTF8=0` sous une locale cp1252 si tu peux la reproduire), en plus de ton environnement habituel. Redépose `PRET`. Une heure.

**Règle nouvelle pour la voie 1.** Toute suite Python d'un lot doit passer sur le poste de contrôle : Windows, console cp1252. Un test qui lance un sous-processus fixe lui-même l'encodage ; la livraison dit la version de Python et l'encodage utilisés. Vaut pour A-14 et A-15 : vérifie-les maintenant, et corrige-les sans attendre leur relecture si le même défaut s'y trouve.

**1. Corrections et relectures d'A-14 et d'A-15** : si l'une revient « à corriger » (`corrections/<lot>.md` plus récent que ton `PRET`), elle passe avant le reste. Tes décisions à défaut sont confirmées : A-14 ne choisit jamais entre deux comptes de même email et garde tels quels les statuts désinscrit, bloqué et inconnu ; A-15 ne rend aucun texte et dit ce qu'il ne voit pas.

**2. Deux retouches, sans nouvelle vérification, un quart d'heure chacune.**
   - **A-12** : la ligne « Liaisons » du mode d'emploi (`wp/outils/bascule/a12/README.md`, ligne 27) dit « clés contenant » ; le code reconnaît un jeton délimité (`product`, `produit`, `article`, `numero`, `issue`) suivi de `_id` ou `_ids`. Aligne la phrase sur le code. Le manifeste du lot suit.
   - **A-10** : son ancien vérificateur de réception est rouge sur `README_APPENDIX`, parce qu'il compare la fin du mode d'emploi partagé à un texte figé et que chaque lot y ajoute deux lignes. Même règle que pour A-09 : il contrôle que **les deux lignes d'A-10** sont présentes et exactes, rien d'autre. L'outil et ses preuves ne changent pas. La preuve : ce vérificateur à code 0 sur l'arbre courant. A-10 reste clos.

**3. `briefs/A-16-dix-derniers-numeros.md`** — l'état des lieux des dix derniers numéros (§4.3) : par numéro, ce qui est rattaché et ce qui manque, d'après une correspondance remplie par l'opérateur. Lecture seule, ne rattache rien. Trois heures.

**4. `briefs/A-17-securite-des-comptes.md`** — l'état des lieux de la sécurité des comptes de l'administration (§4.4) : des comptes par rôle et des oui ou non, aucun nom. Lecture seule. Trois heures.

**A-11, pour mémoire.** Ton refus nommé des caches, pare-feu et liens symboliques est accepté tel quel. Sur le site réel, l'inventaire se fera donc sur la copie de staging, ces fichiers écartés par l'opérateur : c'est noté pour la marche à suivre de la bascule, tu n'as rien à faire.

**Règle.** Une fusion « à corriger » (`corrections/<lot>.md`) arrivée après la dernière mise à jour de cette file est à prendre tout de suite, avant le lot en cours, sans attendre que la file la cite. Avant de t'arrêter sur « file vide », regarde s'il y a une fusion plus récente que ton dernier `PRET` pour chacun de tes lots rendus.

**Preuves.** Tes derniers lots portent des centaines de fichiers de preuves par lot. Pour A-11 à A-17, qui ne font que lire : **un seul paquet de preuves par lot** (le dernier rejeu vert), les essais intermédiaires restent hors du dépôt.

Tu n'ouvres toujours pas l'archive d'Imagine ; c'est Ced qui lance le diagnostic de la base, puis l'import. Tu ne supprimes pas `imagine-test-a01-ced-02`.

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
| Redirections : le plan | Plan validé (§4.3) ; l'outil de test (A-09) et l'inventaire des adresses (A-11) sont rendus | Audit réel, référenceur |
| A-06 Import des abonnés hors ligne | Base Access, abonnés sans email (§4.3) ; l'outil de contrôle du fichier (A-13) est rendu | Export fourni par Imagine ; règle sur les données réelles |

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
| A-08 Répétition de la bascule | 25/11, corrigé le 25/11, complété le 26/11 | **Clos le 26/11** (six corrections vérifiées, phrases d'introduction ajoutées sans toucher aux commandes). Limites d'A-04 inchangées. Manifeste restreint à son lot le 26/11 (vérification n° 3). Ce n'est pas un accord pour toucher au réel |
| A-09 Test des redirections | 25/11, corrigé le 25/11, manifeste restreint le 26/11 | **Clos le 26/11** (vérification n° 2). L'outil vérifie un plan, ne décide d'aucune redirection |
| A-10 Inventaire des codes de réduction | 25/11, corrigé le 25/11 | **Clos le 26/11** (sept corrections vérifiées, vérificateur rejoué par le relecteur). L'outil inventorie ; reclasser ou supprimer un code reste à Imagine |
| A-11 Inventaire des adresses publiques | 26/11, corrigé le 26/11 | **Clos le 26/11** (quatre corrections vérifiées). Refuse en le nommant un site à cache, pare-feu ou lien symbolique : l'inventaire réel se fera sur la copie de staging |
| A-12 Inventaire des contenus | 26/11, corrigé le 26/11 | **Clos le 26/11** (B1 et I1 vérifiés). Une ligne du mode d'emploi à aligner (consigne 2) |
| A-13 Contrôle d'un export hors ligne | 26/11, corrigé le 26/11 | IBAN et doublons vérifiés ; suite non rejouable sous Windows, correctif ciblé (consigne 0) |
| A-01 Quatrième passe (refus muets, base réelle, répétition de la base seule) | 26/11 | **Clos le 26/11** (vérification n° 6, suite rejouée : 1 069 tests). Limites : MySQL 8 non exécuté, objets exécutables refusés en les nommant. Le diagnostic de la base et l'import sont à lancer par Ced. Ce n'est pas un accord d'import |
| A-14 Rapprochement des contacts de la newsletter | 26/11 | Rendu ; relecture attendue (consigne 1) |
| A-15 Inventaire des emails | 26/11 | Rendu ; relecture attendue (consigne 1) |
| T-01 Commande de rejeu | 23/11, corrigé le 23/11 | **Clos le 23/11** ; autorisation ajoutée au script de relecture |
| A-02 Script d'audit | 23/11, corrigé le 23/11 | **Clos le 23/11** (outil et banc fictif). L'audit réel reste à lancer |
