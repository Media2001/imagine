# À faire — voie 1 : l'existant

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 28 novembre 2026, 1 h 30 (passage automatique).

## FREIN — décision de Ced du 28 novembre 2026, 2 h 40

**Seulement ce qui sert directement l'import d'Imagine et la mise à jour.** Termine les corrections des lots déjà rendus. Ne commence aucun nouvel outil d'inventaire ni aucun nouveau lot de mécanique de preuve, même s'il figure plus bas. Ce qui n'est pas commencé attend la validation de Ced, lundi 30 novembre. S'arrêter file vide est attendu. Décision de Ced pour l'import : l'étape de vérification compte les contenus d'un type inconnu et refuse le statut « vérifié » tant qu'il n'a pas tranché, type par type, garder ou vider ; si le code de l'import est gelé, dis ce que ce changement demande, ne le fais pas sans consigne.

**Deux voies depuis le 23/11.** Ce fichier est la file de la voie 1. Une deuxième session d'Hermès suit `A-FAIRE-2.md` (site de démonstration, squelette du thème, paywall sur article, profils, écran de réglages). Lis la section « Les deux voies » de la consigne permanente. Ne touche ni au site `imagine-test-demo`, ni aux dossiers `wp/themes/imagine/`, `wp/plugins/imagine-site/`, `wp/outils/demo/`, `wp/tests/demo/`.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **22/11/2026 — une règle ouverte devient un réglage**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

File du 28/11, 1 h 30. Ton rapport de 22 h 24 est lu, merci : les cinq corrections d'A-32, la matrice en Python 3.14.6, l'arrêt sans `PRET` devant un portail rouge. Depuis, le dépôt montre A-32 rescellé à 22 h 29 et A-33 installé à 22 h 53, et le rejeu indépendant d'un relecteur lit « 13 paquets vérifiés, 0 échec », A-31, A-32 et A-33 compris. **Mais aucun `PRET` et aucun rapport depuis 22 h 24** : commence par dire en cinq lignes où tu en es. L'ordre que tu demandais est écrit ci-dessous, il n'a pas changé. Arbitrages : `docs/arbitrages-2026-11-28.md`, passage de 1 h.

**L'import est gelé**, à l'état scellé par A-28 : plus aucun changement de `wp/outils/staging/` ni de `wp/outils/staging-court/` sans une consigne de cette file, ni fonction, ni correction, ni mise en forme.

**Le lanceur de rejeu est gelé de la même façon** : `wp/tests/t01/` et `wp/tests/rejouer.ps1`. **Gelé veut dire : pas modifié.** Tu peux les lancer, et lancer `wp/tests/preparer-image.ps1` après avoir ajouté des tests, autant qu'il le faut. Un rejeu qui se heurte à celui de l'autre voie est un aléa : attends, rejoue, ne répare rien.

**Règle : une correction ne restructure pas un fichier commun.**

**Règle nouvelle (22 h) : un lecteur de paquet ne photographie pas ses voisins.** Le lecteur permanent d'un lot contrôle ce qui appartient au lot (ses fichiers, ses lignes dans un fichier partagé) et ce dont il dépend, **par une liste fermée écrite dans le lot**. Jamais un dossier entier d'outils, jamais le paquet d'un autre lot. La preuve que tu n'as rien touché chez les voisins se fait une fois, au sceau, dans le reçu ; elle n'est pas une condition permanente du lecteur. C'est ce qui a fait tomber A-32 à l'arrivée d'A-33, et T-03 à la retouche d'A-31. **Tu ne rouvres aucun lot clos pour cela.**

**0. A-32 : il ne manque que la borne, puis le `PRET`.** Tes cinq corrections sont appliquées et lues ; les arbitrages de 22 h tiennent (C03 sans `--as-of`, A-16 à dix sans `--limit`, aucun mode sans plafond, aucun outil clos retouché).
   - **Le sceau de 22 h 29 a précédé la règle de 22 h 30** : `wp/tests/a32/run.py` photographie encore tout `wp/outils/bascule/`. Borne-la avant le `PRET` : le dossier `tournee/`, les tests d'A-32, le gardien, l'import gelé, et les dossiers des quinze outils de `outils.jsonl`, par une liste fermée écrite dans le lot. Un outil de la tournée qui change périme toujours le paquet : c'est voulu ; A-33, A-34 et les suivants, non ;
   - rescelle par la commande du lot, relis `production/A-32/verify.py` sans argument, dépose `PRET` ;
   - **si ce nouveau sceau périme le paquet d'A-31** (son sceau lie cinq fichiers de la tournée) : un resceau d'A-31 par sa propre commande, code et tests inchangés. A-31 reste clos ; dis-le en une ligne.

**1. A-33, juste après.**
   - **La consigne « sors du dépôt le paquet d'A-33 » est levée** : elle valait pour un paquet aux portails rouges, il est vert. Elle ne revient que si le nouveau sceau d'A-32 le périme et que les deux se bloquent de nouveau ; dans ce cas seulement, sors-le le temps du sceau d'A-32, comme tu l'as fait pour le candidat d'A-31 ;
   - vérifie que le lecteur d'A-33 suit la règle de la liste fermée ; rejoue ses portails s'ils sont périmés, scelle, `PRET` ;
   - **la preuve qui compte** : un rejeu général après les deux `PRET`, dans les deux consoles, où A-32 et A-33 sont tous deux parmi les paquets vérifiés, aucun hors rejeu, zéro échec. Ton rapport cite la ligne `PAQUETS` ;
   - rien dans `wp/tests/t01/` ni `wp/tests/rejouer.ps1`, aucun portail assoupli, aucune empreinte changée à la main. Une étape rouge : arrêt sans `PRET`, un rapport de cinq lignes ;
   - A-33 n'entre pas dans la tournée ;
   - **Python** : A-33 mesurait 3.11.15, les commandes de réception emploient 3.14.6. Rejoue sa matrice Python avec `C:/Python314/python.exe`, ou dis en une ligne pourquoi ce n'est pas possible.

**2. T-03, la clôture, après les deux `PRET`.** Ton choix de le finaliser sur l'arbre final est retenu. Avant le sceau, applique-lui la règle : son lecteur final contrôle **ses** fichiers ; la photographie des paquets voisins reste dans le reçu du sceau, datée, et n'est plus une condition du lecteur. Puis la preuve finale, `PRET`, une vérification avec rejeu indépendant. Après sa clôture, T-03 n'est pas rescellé à chaque paquet nouveau. Le lanceur reste gelé.

**3. A-29 : rangé, tu n'y touches plus.** Pas de `PRET`, pas de nouvel essai, hors de la tournée d'A-32. Il sera repris par une consigne de cette file, pas avant.

**4. `briefs/A-34-les-liens-vers-ce-qui-part-aux-archives.md`** — dans les contenus des dix derniers numéros, les liens et les fichiers qui pointent vers ce qui n'est pas repris, comptés (§4.3). Lecture seule, des nombres ; corps lu par un analyseur HTML. **À commencer après le `PRET` de T-03.** Une demi-journée.

**À savoir : la clôture d'un lot de la voie 2 ne dépend pas de tes paquets en cours.** Un paquet rouge sur la ligne `PAQUETS` ne bloque un autre lot que s'il appartient à un lot clos ou porteur d'un `PRET`. Raison de plus pour ne déposer un `PRET` qu'avec un paquet vert. La voie 2 a vu un de ses tests échouer une fois dans un de tes rejeux, pendant qu'elle corrigeait C-29 : c'est un aléa de deux voies sur un même arbre, tu as bien fait de ne rien réparer.

**Règle nouvelle, venue d'A-30 : une suite Python passe sur une session Windows propre.** Sans `TMPDIR` : la matrice retire la variable aux processus fils et le prouve. Vaut pour les lots à venir et pour ceux que tu corriges.

À savoir, sans rien à faire : la voie 2 a créé deux types de contenu qui sont des messages de visiteurs (propositions de sujet de B-08, `imagine_contact` de B-09). L'import ne les connaît pas et **on ne le rouvre pas pour cela** : c'est noté dans `docs/ecarts.md`.

A-28, les contenus d'un type inconnu : la question est toujours chez Ced. Ne change rien.

**Ne touche plus au gardien commun sans le dire en tête de ton rapport** : tout changement rouvre les paquets de tous les outils.

**Un rapport court dans `files/rapports/` à la fin de chaque réveil**, même de cinq lignes : c'est ce que le passage automatique lit en premier. Les tiens de cette nuit étaient bien.

**Règle étendue : un canari par canal, et le fichier est un canal.** Un outil qui charge le WordPress du site prouve son silence sur chaque canal par lequel du code tiers peut parler : affichage, écriture directe sur les deux flux, arrêt anticipé, fin de processus, **et fichier de rapport altéré avant publication**. Un seul canari affiché ne prouve rien des autres.

**Règle du parcours du mode d'emploi** (passage de 10 h) : pour chaque outil, un test lance la commande du mode d'emploi avec **les seuls arguments que sa ligne donne**. Vaut pour les lots à venir et pour ceux que tu corriges.

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
| A-16 État des lieux des dix derniers numéros | 26/11, corrigé le 26/11 | **Clos le 26/11** (cinq corrections et la retouche vérifiées : le refus d'une clé absente nomme le champ, liste fermée de quatre noms, jamais la valeur). Ne rattache rien |
| A-17 Sécurité des comptes de l'administration | 26/11, corrigé le 26/11 | **Clos le 26/11** (neuf corrections vérifiées ; chemin de refus corrigé au point commun, 60 refus au canari verts). Le compte des mots de passe d'application vaut « inconnu après neutralisation » ; l'import n'est pas modifié |
| A-18 Ce que le site garde et ne devrait pas garder | 26/11, corrigé le 26/11 | **Clos le 26/11** (sept corrections vérifiées : les deux magasins de commandes lus, détection des formes bruitées). Ne dit pas si le serveur protège les fichiers ; ne supprime rien |
| A-19 Cohérence des abonnements et des adhésions | 26/11, corrigé le 26/11 | **Clos le 26/11** (quatre corrections vérifiées ; la commande du mode d'emploi passe sans date). Des comptes seulement, ne corrige rien |
| T-02 Rejeu des tests purs des outils | 26/11, corrigé le 26/11 | **Clos le 26/11** (trois corrections vérifiées : un reçu mixte est refusé, empreintes des reçus recalculées). Vérification complémentaire : suite rejouée par le vérificateur, 16 outils, 311 contrôles |
| A-20 Ce que paient les abonnés en ligne | 26/11, corrigé et repris le 26/11 | **Clos le 26/11** (cinq corrections vérifiées ; vérification n° 3 sur le gardien final, canal « fichier » couvert). Matrice native rejouée par Hermès seul. Des comptes seulement |
| A-21 Les portes vers l'extérieur | 26/11, corrigé et repris le 26/11 | **Clos le 26/11** (quatre corrections vérifiées ; vérification n° 3 sur le gardien final). Matrice native rejouée par Hermès seul. Aucune clé, aucune adresse, ne révoque rien |
| A-22 Un seul gardien pour les sorties | 26/11, corrigé le 26/11, paquet refait le 27/11 | **Clos le 27/11** (vérification n° 2 : vérificateur de paquet rejoué au vert par le relecteur lui-même, par T-03). Tout changement du gardien rouvre les paquets de tous les outils |
| A-23 Les comptes des abonnés | 26/11, corrigé le 26/11, paquet refait le 27/11 | **Clos le 27/11** (vérification n° 2, code inchangé, paquet revu au vert par le rejeu indépendant). Sur une copie neutralisée, ces nombres valent « inconnu » |
| A-24 Les adresses d'expédition | 26/11, corrigé le 26/11, paquet refait le 27/11 | **Clos le 27/11** (vérification n° 2, rapport et « Portée » à jour). Sur une copie neutralisée, presque tous ces nombres valent « inconnu » ; la lecture sur la source est une décision de Ced |
| A-25 Ce que le site garde sur ses visiteurs | 26/11, corrigé le 26/11, paquet refait le 27/11 | **Clos le 27/11** (vérification n° 2 : banc adapté au refus du `garder` et à la purge) |
| A-26 Ce que le site charge chez des tiers | 26/11, corrigé le 27/11, paquet refait le 27/11 | **Clos le 27/11** (vérification n° 2 : matrice réelle rejouée, code inchangé, ligne `PAQUETS` verte lue par le rejeu indépendant du relecteur). Des nombres par famille, aucune adresse |
| A-27 Les moyens de paiement enregistrés | 26/11, corrigé le 27/11, paquet refait le 27/11 | **Clos le 27/11** (vérification n° 2, même condition). Sur une copie neutralisée, tous ces nombres valent « inconnu » ; le compte sur la source serait une décision de Ced |
| A-28 Les messages de formulaires et l'import | 27/11, corrigé le 27/11 | **Clos le 27/11** (cinq corrections vérifiées, découpage du fichier de l'import regardé par la vérification et rejoué par sept matrices). Import gelé. Ce n'est pas un accord d'import |
| A-30 L'import à blanc des abonnés hors ligne | 27/11, corrigé le 27/11 | **Clos le 27/11** (cinq instructions vérifiées : suite rejouée sur une session Windows propre, 38 tests en UTF-8 et en cp1252 ; paquet refait après T-03). Rien n'est écrit ; trois règles laissées fermées pour Imagine |
| A-31 L'historique des commandes | 27/11, corrigé et retouché le 27/11 | **Clos le 27/11** (vérification n° 2 : six instructions et la retouche vérifiées ; quatre compteurs de liens cassés et total des remboursements exacts, le reste regroupé sous cinq ; suites Python rejouées par le vérificateur, matrice native lue sur preuves). Aucun montant. Sur une copie neutralisée, seule la nature vaut « inconnu » |
| A-07 Retouches de rédaction | 26/11 | Sept retouches vérifiées ; constat du 20/11 annoté, rien de rejoué. Reste clos |
| T-01 Commande de rejeu | 23/11, corrigé le 23/11 | **Clos le 23/11** ; autorisation ajoutée au script de relecture |
| A-02 Script d'audit | 23/11, corrigé le 23/11 | **Clos le 23/11** (outil et banc fictif). L'audit réel reste à lancer |
