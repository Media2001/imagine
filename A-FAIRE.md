# À faire — voie 1 : l'existant

Tenu à jour par Claude à chaque session avec Ced. **Hermès ne modifie pas ce fichier** : il signale dans son rapport ce qu'il a fait et ce qui bloque, et la consigne passe en « Terminé » à la session suivante.

Mis à jour le 27 novembre 2026, 1 h 30 (passage automatique).

**Deux voies depuis le 23/11.** Ce fichier est la file de la voie 1. Une deuxième session d'Hermès suit `A-FAIRE-2.md` (site de démonstration, squelette du thème, paywall sur article, profils, écran de réglages). Lis la section « Les deux voies » de la consigne permanente. Ne touche ni au site `imagine-test-demo`, ni aux dossiers `wp/themes/imagine/`, `wp/plugins/imagine-site/`, `wp/outils/demo/`, `wp/tests/demo/`.

Consigne permanente : `prompts/consigne-permanente.md`. Doctrine : `doctrine/doctrine.md` (dernière révision : **22/11/2026 — une règle ouverte devient un réglage**).

Le projet a trois chantiers indépendants. Un lot porte la lettre de son chantier : **A** l'existant, **B** le thème, **C** le code sur mesure. Les lots actifs de chantiers différents peuvent avancer en parallèle.

## Consignes actives, par ordre de priorité

File du 27/11, 1 h 30. Tes rapports de 22 h 56, 23 h 42, 0 h 53 et 1 h 02 sont lus, merci : ta liste des paquets périmés par A-28 (`production/A-28/REJEUX-PARENT.md`) est exactement ce qu'il fallait, et ne rien resceller était le bon réflexe. **A-23, A-24, A-25 : vérifiés « prêt », rien à corriger au code** ; ils se closent sur leur paquet refait (consigne 2). **A-26 et A-27 : relus « à corriger »**. **A-28 : rendu, en relecture.** A-29 : construit, preuve native attendue. Arbitrages : `docs/arbitrages-2026-11-27.md`, passage de 1 h.

**L'ordre, pour ne pas rejouer sept matrices deux fois.** A-28 a changé l'import ; sa relecture peut encore le faire changer. Donc : le code d'abord (consignes 0 et 1), la requalification ensuite, une seule fois, sur l'import final (consigne 2). Les rejeux que tu as déjà faits cette nuit sur l'import courant comptent si l'import ne change plus.

**0. Corrections de code, sans resceller** :
   - **A-26** (`corrections/A-26.md`) : remplacer l'extraction par expression régulière par un lecteur de balises natif de WordPress, avec les deux contre-exemples en tests rouges puis verts, classique et HPOS ; chemin explicite du mode d'emploi. Défauts confirmés : « illisible » plutôt qu'un « non » non prouvé ; `form-policy.json` entre dans le gel des dépendances ;
   - **A-27** (`corrections/A-27.md`) : un champ déclaré mais illisible n'est jamais « absent » (cas `ppcp-gateway`, classique et HPOS) ; un lien explicite contredit par une référence donne « illisible », sans choisir un instrument ; le repli par passerelle reste pour la référence seule. Les deux mineurs sont à ta main. « Six mois » : la borne reste au jour de l'audit, question rangée pour Imagine, n'y touche pas ;
   - **A-25** : son banc pose `garder` sur une table de messages et attend qu'ils restent. **C'est le banc d'A-25 qui s'adapte à A-28, pas l'inverse** : il attend la purge, et le nouveau refus. Le code de l'outil ne change pas. Rafraîchis l'en-tête de son mode d'emploi ;
   - **A-24** : `RAPPORT.md` et le paragraphe « Portée » du mode d'emploi décrivent encore l'état d'avant ta qualification de 22 h 56 ; mets-les à jour avec le paquet refait.

**1. Finir A-29** (`briefs/A-29-ce-que-le-site-fait-tout-seul.md`) jusqu'à sa matrice native. Tes trois défauts sont confirmés : huit semaines glissantes en temps universel sans extrapolation ; échecs lus dans la seule file de WooCommerce ; aucune attribution d'une tâche inconnue à une extension.

**2. La requalification commune, une seule fois, à l'arrivée de la fusion d'A-28** (`corrections/A-28.md`) :
   - si la fusion demande de toucher à l'import, ses corrections d'abord ;
   - ensuite les matrices d'A-21 à A-27 et d'A-29 sur l'import final, un paquet neuf par lot, l'ancien sorti du dépôt quand le nouveau est vert, puis leurs `PRET` ;
   - **A-21 reste clos** : son code n'a pas changé ; son paquet est refait et son `PRET` redéposé pour que le circuit le revérifie ; il ne se rouvre que si sa matrice est rouge. A-20 passe encore : rien à faire ;
   - A-22 : même chose ; sa clôture attend toujours un rejeu indépendant de son vérificateur (consigne 3) ;
   - A-23, A-24, A-25 : code inchangé depuis leur vérification, rien à refaire au fond ; le circuit lance de lui-même la vérification complémentaire ;
   - en attendant la fusion, tu n'es pas à l'arrêt : consignes 0, 1, 3 et 4.
   - A-28, les contenus d'un type inconnu : tu n'en as rien décidé et c'est bien ; la question est portée à Ced. Ne change rien.

**L'import est gelé après A-28.** Plus aucun changement de `wp/outils/staging/` sans une consigne de cette file. Un lot qui change un fichier commun (import, gardien) le dit en tête de son rapport et livre la liste des paquets qu'il périme, comme tu l'as fait.

**3. `briefs/T-03-rejeu-des-verificateurs-de-paquet.md`** — la commande de rejeu autorisée joue aussi les vérificateurs de paquet sans argument, dans le même conteneur isolé ; une ligne `PAQUETS` de plus, la dernière ligne ne change ni de forme ni de sens. C'est ce qui permettra de clore A-22 sans attendre Ced. Deux heures.

**4. `briefs/A-30-import-a-blanc-des-abonnes-hors-ligne.md`** — ce que ferait l'import des abonnés hors ligne, ligne par ligne, en nombres : comptes à créer, comptes existants, lignes sans adresse, types sans correspondance. Rien n'est écrit, rien n'est importé ; fichiers fictifs d'A-13. Une demi-journée.

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
| A-22 Un seul gardien pour les sorties | 26/11, corrigé le 26/11 | Six corrections faites, cinq vérifiées par des tests rejoués ; **pas clos** : paquet périmé par A-28, à refaire ; puis rejeu indépendant de son vérificateur (T-03, ou Ced) |
| A-23 Les comptes des abonnés | 26/11, corrigé le 26/11 | Quatre corrections vérifiées « prêt » (règle d'A-17, six comptes de gestion masqués exclus). **Clôture sur le paquet refait** après A-28, code inchangé |
| A-24 Les adresses d'expédition | 26/11, corrigé le 26/11 | Sept corrections vérifiées « prêt » (comparaison sans casse ni espaces, données brutes intactes). **Clôture sur le paquet refait** après A-28, rapport et « Portée » mis à jour |
| A-25 Ce que le site garde sur ses visiteurs | 26/11, corrigé le 26/11 | Quatre corrections vérifiées « prêt » (table d'entrées et table-fille distinguées, « couverture indéterminée »). Banc à adapter à A-28, puis **clôture sur le paquet refait** |
| A-26 Ce que le site charge chez des tiers | 26/11 | Relu « à corriger » le 27/11 : lecteur de balises à la place de l'expression régulière, paquet à refaire (consigne 0) |
| A-27 Les moyens de paiement enregistrés | 26/11 | Relu « à corriger » le 27/11 : « illisible » jamais « absent », contradiction sans choix d'instrument, paquet à refaire (consigne 0) |
| A-28 Les messages de formulaires et l'import | 27/11 | Rendu à 0 h 58, en relecture. A changé l'import : paquets d'A-21 à A-27 à refaire une fois (consigne 2) |
| A-07 Retouches de rédaction | 26/11 | Sept retouches vérifiées ; constat du 20/11 annoté, rien de rejoué. Reste clos |
| T-01 Commande de rejeu | 23/11, corrigé le 23/11 | **Clos le 23/11** ; autorisation ajoutée au script de relecture |
| A-02 Script d'audit | 23/11, corrigé le 23/11 | **Clos le 23/11** (outil et banc fictif). L'audit réel reste à lancer |
