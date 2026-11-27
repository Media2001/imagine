# À faire — voie 1 : l'existant

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 27 novembre 2026, 7 h 30 (passage automatique).

**Deux voies depuis le 23/11.** Ce fichier est la file de la voie 1. Une deuxième session d'Hermès suit `A-FAIRE-2.md` (site de démonstration, squelette du thème, paywall sur article, profils, écran de réglages). Lis la section « Les deux voies » de la consigne permanente. Ne touche ni au site `imagine-test-demo`, ni aux dossiers `wp/themes/imagine/`, `wp/plugins/imagine-site/`, `wp/outils/demo/`, `wp/tests/demo/`.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **22/11/2026 — une règle ouverte devient un réglage**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

File du 27/11, 7 h 30. Tes rapports de 5 h 03, 5 h 14, 5 h 53, 6 h 44 et celui des corrections de T-03 sont lus, merci. **Clos ce passage : A-28, A-22, A-23, A-24, A-25.** A-21 reste clos (vérification n° 3). La requalification est partie une fois, au bon moment. Retirer le `PRET` d'A-26 et d'A-27 plutôt que changer une empreinte : c'était le bon réflexe. Arbitrages : `docs/arbitrages-2026-11-27.md`, passage de 7 h.

**L'import est gelé**, à l'état scellé par A-28 : plus aucun changement de `wp/outils/staging/` ni de `wp/outils/staging-court/` sans une consigne de cette file, ni fonction, ni correction, ni mise en forme.

**Le lanceur de rejeu est gelé de la même façon, dès maintenant** : `wp/tests/t01/` et `wp/tests/rejouer.ps1`, dans l'état de tes corrections de T-03. Ces corrections étaient demandées, mais elles ont périmé trois paquets (A-26, A-27, A-31) : on ne le refait pas. Si la preuve finale de T-03 révèle un défaut du lanceur, écris-le et arrête-toi sur ce point ; je trancherai.

**Règle : une correction ne restructure pas un fichier commun.**

**0. Le resceau, une seule fois, sur l'import et le lanceur gelés** : A-26, A-27, A-30, A-31. Des matrices réelles, jamais un changement d'empreinte.
   - A-26, A-27 : vérifiés « prêt » ce matin, code inchangé. Paquet refait, `PRET`. Ils se closent sur une ligne `PAQUETS` verte lue par un relecteur, sans nouveau tour de fond ;
   - A-30 (`corrections/A-30.md`) : tes corrections sont faites ; matrice native, paquet neuf, `PRET`, second tour. Confirmés : dossier temporaire standard de Python, refus s'il tombe dans le dépôt ; l'axe produit garde sa clé `0` ;
   - A-31 : paquet refait, `PRET`, première relecture ;
   - **A-20 entre dans le rejeu** au même moment : un point d'entrée sans argument dans `production/A-20/` et sa déclaration `rejeu.json`. Si l'ajout périme son paquet, tu le refais par sa matrice réelle. Aucun contrôle changé. A-20 reste clos ; il ne se rouvre que si sa matrice est rouge ;
   - « repartir d'un arbre propre » (A-30, instruction 5) : ni Git, ni remise à zéro. Tu mesures les comptes obtenus et tu les écris. Un compte global qui bouge parce que la voie 2 livre n'est pas un défaut de ton lot.

**1. T-03, la preuve finale et le `PRET`** (`production/T-03/RECEPTION-CORRECTIONS.md`, §4), après le resceau : la ligne `PAQUETS` avec tous les paquets déclarés verts, puis un octet changé dans A-28 sur copie, qui ne rougit que lui. Défauts de la fusion confirmés : le montage de la racine reste tel quel, les tests de contrat de T-03 ne s'ajoutent pas à la commande des relecteurs. La ligne `OUTILS` donne le nombre réellement observé.

**2. A-29** : la consigne tient. Une sortie 255 n'est pas un succès. **Un réveil de diagnostic, pas plus**, sans retirer ni canari ni compteur, sans toucher à l'import, au gardien ni au lanceur. S'il n'aboutit pas : dix lignes dans ton rapport (ce qui est établi, ce qui ne l'est pas, tes deux hypothèses) et tu passes à la suite ; je trancherai. A-29 ne bloque personne.

**3. `briefs/A-32-la-tournee-des-inventaires.md`** — une commande qui enchaîne, en lecture seule, les outils d'inventaire clos, chacun par la commande de son mode d'emploi, et rend un bilan d'une page (réussi, refusé, en échec) sans recopier un seul nombre. Elle ne change aucun outil. À commencer après le `PRET` de T-03. Trois heures.

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
| A-26 Ce que le site charge chez des tiers | 26/11, corrigé le 27/11 | Vérifié « prêt » le 27/11, **pas clos** : paquet périmé par les corrections de T-03, à refaire une fois (consigne 0) |
| A-27 Les moyens de paiement enregistrés | 26/11, corrigé le 27/11 | Vérifié « prêt » le 27/11, **pas clos** : paquet périmé par les corrections de T-03, à refaire une fois (consigne 0) |
| A-28 Les messages de formulaires et l'import | 27/11, corrigé le 27/11 | **Clos le 27/11** (cinq corrections vérifiées, découpage du fichier de l'import regardé par la vérification et rejoué par sept matrices). Import gelé. Ce n'est pas un accord d'import |
| A-07 Retouches de rédaction | 26/11 | Sept retouches vérifiées ; constat du 20/11 annoté, rien de rejoué. Reste clos |
| T-01 Commande de rejeu | 23/11, corrigé le 23/11 | **Clos le 23/11** ; autorisation ajoutée au script de relecture |
| A-02 Script d'audit | 23/11, corrigé le 23/11 | **Clos le 23/11** (outil et banc fictif). L'audit réel reste à lancer |
