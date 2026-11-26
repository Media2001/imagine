# À faire — voie 1 : l'existant

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 26 novembre 2026, 10 h 30 (passage automatique).

**Deux voies depuis le 23/11.** Ce fichier est la file de la voie 1. Une deuxième session d'Hermès suit `A-FAIRE-2.md` (site de démonstration, squelette du thème, paywall sur article, profils, écran de réglages). Lis la section « Les deux voies » de la consigne permanente. Ne touche ni au site `imagine-test-demo`, ni aux dossiers `wp/themes/imagine/`, `wp/plugins/imagine-site/`, `wp/outils/demo/`, `wp/tests/demo/`.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **22/11/2026 — une règle ouverte devient un réglage**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

File du 26/11, 10 h 30. Tes rapports de 7 h 54 à 9 h 13 sont lus, merci pour eux. **A-17 est clos** : le correctif au point commun est le bon, et ton rejeu d'A-11, A-12, A-14 et A-15 suffit, ces lots restent clos. A-18 et A-19 sont relus « à corriger » : leurs fusions sont arrivées à 9 h 43 et 9 h 53, après ton arrêt. A-16 est à une retouche de sa clôture. Arbitrages : `docs/arbitrages-2026-11-26.md`, passage de 10 h.

**0. Corrections d'A-19** (`corrections/A-19.md`) : un bloquant. La commande du mode d'emploi, copiée telle quelle, est refusée : le lanceur exige `--as-of`, que le mode d'emploi dit facultatif. Instructions 1 et 2 comme la fusion les écrit. **L'instruction 3 n'est pas pour ce lot** (voir T-02, consigne 3). Instruction 4 confirmée : le compte « schéma de passerelle inconnu » reste, séparé de « moyen absent ».

**1. Corrections d'A-18** (`corrections/A-18.md`) : trois importants, tous des oublis de détection. Les sept instructions, avec ces précisions :
   - instruction 1 : les deux magasins de commandes sont lus quand leurs tables existent, quel que soit celui qui est actif ;
   - instruction 6 : ton défaut sur les règles du serveur est **acquis** (présence du fichier oui ou non, interdiction « inconnu »). C'est mon brief qui se contredisait ; l'écart est reporté par moi dans `docs/ecarts.md`, tu n'as rien à écrire ;
   - la question de la fusion sur la marque de la neutralisation n'ira pas à Imagine : c'est notre import. Tu gardes la marque telle quelle, tu ne touches pas à l'import.

**2. A-16, une retouche** (un quart d'heure). Le vérificateur a raison sur un point, et la faute est dans mes textes : le brief voulait qu'une clé absente soit refusée « en la nommant », ma règle de 7 h disait « code seul ». Tranché : le refus `A16_MAPPING_KEY_ABSENT` **nomme le champ de la correspondance en cause**, pris dans une liste fermée écrite dans le code (`numero_type`, `thematique`, `pdf_cle`, `liaison.cle`), **jamais la valeur** que l'opérateur y a mise. Le point commun garde sa forme : un code, et des noms d'une liste fermée. Un test par champ, le canari toujours absent, `PRET` redéposé ; les autres outils ne bougent pas.

**Règle nouvelle : le parcours du mode d'emploi.** Pour chaque outil, un test lance la commande du mode d'emploi avec **les seuls arguments que sa ligne donne**. A-19 avait un banc vert et une commande documentée qui échouait. Vaut pour les lots à venir et pour ceux que tu corriges ; les lots clos ne sont pas repris pour cela.

**3. `briefs/T-02-rejeu-des-outils.md`** — la commande de rejeu des relecteurs joue aussi les tests purs de tes outils (`unit.php`), sans changer de nom, d'isolation ni de dernière ligne. Deux heures.

**4. `briefs/A-20-ce-que-paient-les-abonnes.md`** — ce que paient aujourd'hui les abonnés en ligne : par produit, rythme, montant et pays de livraison (§3.4, §4.3). Lecture seule, des comptes, aucune correspondance proposée. Trois heures.

**5. `briefs/A-21-portes-vers-l-exterieur.md`** — les clés d'interface et les envois automatiques de WooCommerce, comptés (§4.4). Lecture seule, aucune clé, aucune adresse. Deux heures.

**La règle du chemin de refus reste** (passage de 7 h) : aucune sortie d'un outil de la voie 1, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du contenu du site ; seuls sortent un code de refus et des noms pris dans une liste fermée écrite dans le code.

**Règles qui restent.**
- Une fusion « à corriger » (`corrections/<lot>.md`) arrivée après la dernière mise à jour de cette file est à prendre tout de suite, avant le lot en cours, sans attendre que la file la cite. Avant de t'arrêter sur « file vide », regarde s'il y a une fusion plus récente que ton dernier `PRET` pour chacun de tes lots rendus.
- Toute suite Python d'un lot passe sur le poste de contrôle : Windows, console cp1252. Un test qui lance un sous-processus fixe lui-même l'encodage ; la livraison dit la version de Python et l'encodage utilisés.
- **Un seul paquet de preuves par lot** (le dernier rejeu vert) ; les essais intermédiaires restent hors du dépôt.
- Un fichier partagé (mode d'emploi commun) se contrôle par contrat, sur les lignes du lot, jamais par son empreinte entière.

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
| « Ne pas renouveler » : le bouton | Bouton, confirmation, et date de fin native pour le quatre-fois (§3.4) ; le raccord et les écrans sans bouton sont faits en voie 2 (C-20) | Staging vérifié avec Stripe en mode test, donc un accord de Ced ; marge de l'échéancier arrêtée par Imagine |

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
| A-12 Inventaire des contenus | 26/11, corrigé le 26/11 | **Clos le 26/11** (B1 et I1 vérifiés ; ligne du mode d'emploi alignée, vérification n° 2) |
| A-13 Contrôle d'un export hors ligne | 26/11, corrigé deux fois le 26/11 | **Clos le 26/11** (vérification n° 2 : 46 tests verts en UTF-8 et en cp1252). L'outil contrôle un fichier ; l'import des abonnés hors ligne (A-06) attend l'export d'Imagine |
| A-01 Quatrième passe (refus muets, base réelle, répétition de la base seule) | 26/11 | **Clos le 26/11** (vérification n° 6, suite rejouée : 1 069 tests). Limites : MySQL 8 non exécuté, objets exécutables refusés en les nommant. Le diagnostic de la base et l'import sont à lancer par Ced. Ce n'est pas un accord d'import |
| A-14 Rapprochement des contacts de la newsletter | 26/11, corrigé le 26/11 | **Clos le 26/11** (quatre corrections vérifiées). N'appelle pas Brevo, n'écrit rien ; un abonné en annulation à terme n'est pas compté actif, question rangée pour Imagine |
| A-15 Inventaire des emails | 26/11, corrigé le 26/11 | **Clos le 26/11** (trois corrections vérifiées). Aucun texte ni adresse ; les emails des services extérieurs lui échappent |
| A-16 État des lieux des dix derniers numéros | 26/11, corrigé le 26/11 | Cinq corrections vérifiées. Une retouche avant clôture : le refus d'une clé absente nomme le champ de la correspondance (consigne 2) |
| A-17 Sécurité des comptes de l'administration | 26/11, corrigé le 26/11 | **Clos le 26/11** (neuf corrections vérifiées ; chemin de refus corrigé au point commun, 60 refus au canari verts). Le compte des mots de passe d'application vaut « inconnu après neutralisation » ; l'import n'est pas modifié |
| A-18 Ce que le site garde et ne devrait pas garder | 26/11 | Relu « à corriger » : trois importants (consigne 1). Défaut sur les règles du serveur acquis |
| A-19 Cohérence des abonnements et des adhésions | 26/11 | Relu « à corriger » : un bloquant, la commande du mode d'emploi est refusée (consigne 0) |
| A-07 Retouches de rédaction | 26/11 | Sept retouches vérifiées ; constat du 20/11 annoté, rien de rejoué. Reste clos |
| T-01 Commande de rejeu | 23/11, corrigé le 23/11 | **Clos le 23/11** ; autorisation ajoutée au script de relecture |
| A-02 Script d'audit | 23/11, corrigé le 23/11 | **Clos le 23/11** (outil et banc fictif). L'audit réel reste à lancer |
