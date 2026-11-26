# État des chantiers — mis à jour le 26 novembre 2026, 22 h 30 (passage automatique)

## En attente de Ced

Ce que toi seul peux faire, dans l'ordre d'utilité.

**À 22 h 30 : les deux voies tournent, rien n'est à l'arrêt.** Trois choses nouvelles pour toi depuis 19 h 30 : une précaution avant ton import (point 1, dernière ligne), une commande d'une minute si tu veux clore A-22 (point 5), et B-06 à regarder (point 2).

1. **Archive d'Imagine : c'est à toi.** La quatrième passe d'A-01 est rendue, vérifiée et close (plus de refus muet : chaque échec dit l'étape, le code d'erreur, la ligne et la table, sans aucune valeur). Dans l'ordre :
   - d'abord la répétition de la base seule, quelques minutes, qui ne crée aucun site et ne restaure aucun fichier : `python .\wp\outils\staging-court\publish.py --diagnose-database --operator-ced --archive "$ARCHIVE_WPRESS"` (mode d'emploi en tête de `wp/outils/staging-court/README.md`) ;
   - si elle passe, l'import complet sous un nom neuf, `imagine-test-a01-ced-03` : ta décision ;
   - si elle refuse, le reçu nomme la cause ; dépose-le, la voie 1 la traitera. Refus possibles et attendus : une vue, un déclencheur ou une procédure dans la base (refusés en les nommant), une collation MySQL 8 non prévue ;
   - le site `imagine-test-a01-ced-02`, resté de l'import échoué, n'a pas été supprimé : Hermès ne peut pas prouver qu'il est vide sans lire la copie. À supprimer par toi dans l'outil de staging.
   - **nouveau, à savoir avant l'import : n'écris jamais `garder` sur une table de formulaires dans ton fichier de décisions.** Sans décision de ta part, l'import vide les tables qu'il ne connaît pas, donc les messages reçus par les formulaires du site ; avec `garder`, ils restent en clair dans la copie (prouvé sur le banc par A-25). Ce qui n'est pas encore prouvé : le sort des messages qu'une extension rangerait comme des contenus. Le lot A-28 ferme les deux cas et fera refuser par la vérification une copie où il en reste. Mon avis : n'ouvre pas une copie du réel aux agents avant qu'A-28 soit clos ; la décision reste la tienne.
2. **À regarder sur le site de démonstration** (`http://192.168.129.32:8085`, réseau local ; pour chaque lot, `production/<lot>/A-VOIR.md` dit quoi ouvrir). Code clos, il ne manque que ton œil : B-00, B-01, C-08, C-10, C-11, C-12, C-13 (liste d'envoi, en `e-abo` ; vérifie aussi que les menus « Imagine » ne se doublent pas), C-14 (achat d'un numéro, en `p-numero`), B-03 (mode lecture), B-02 (« Mon compte », `/my-account/`), B-04 (page numéro, kiosque, thématiques), C-15 (écran des échéances, en `e-abo`), C-16 (commande pour un client), C-17 (justificatifs du tarif solidaire), C-18 (extractions), C-19 (tableau de bord, des nombres seulement), C-20 (« Mon compte » dit, profil par profil, comment se renouvelle l'abonnement ; **pas de bouton « ne pas renouveler »**, il viendra avec le staging vérifié), C-21 (export et effacement des données d'un compte, dans les outils de confidentialité de l'administration), B-05 (partenaires : page, fiche, étiquette « Partenariat » sur l'accueil ; la façon de distinguer graphiquement cette étiquette est au designer), C-22 (« Mes newsletters » dans Mon compte et la page « Nos newsletters »), et depuis 22 h **B-06 (espace coopérateurs : la page réservée, le statut posé sur un compte, les deux réglages de rôle)**. C-23, clos lui aussi, est un test : rien à regarder.
   - **Une question pour toi sur B-04 : garde-t-on une étiquette d'accès (« Réservé »…) sur le kiosque, oui ou non ?** Les relecteurs proposent de la retirer (le cahier des charges ne demande que couverture, titre et date, et l'étiquette trompe quand le numéro contient des articles libres). Elle est laissée en place tant que tu n'as pas répondu.
   - **Une question pour toi sur C-22 : dans l'écran de réglages, la section « Newsletters » s'affiche sous le bouton « Enregistrer ». On la laisse là, ou on la remonte au-dessus du bouton ?** L'enregistrement fonctionne dans les deux cas ; elle reste en place tant que tu n'as pas répondu (capture : `production/C-22/reglages-newsletters.png`).
   - **Une question pour toi sur B-06 : la date à laquelle le statut de coopérateur a été posé s'affiche brute, en temps universel. On la laisse ainsi, ou on l'affiche à l'heure belge, en clair ?** Elle reste telle quelle tant que tu n'as pas répondu (`production/B-06/A-VOIR.md`).
3. **Questions à porter à Imagine** quand tu les verras : `docs/decisions.md` (vingt-cinq, toutes déjà réglées sur un défaut prudent ; deux nouvelles à 22 h : une inscription d'office à la newsletter vaut-elle « inscrit » pour la personnalisation, et un lecteur qui partage son adresse avec un compte de l'administration compte-t-il comme un doublon).
4. Plus tard, pour le site réel, trois choses que les outils attendront de toi : le plan de nettoyage (`wp/outils/bascule/plan-imagine.exemple.json`, tout y est à « garder » ; l'outil qui l'exécute, A-05, est clos), le plan de redirections (avec le référenceur), et un GO écrit pour répéter la mise à jour sur le staging d'Imagine une fois vérifié (c'est là seulement que la montée 6.9.1 → 7.0 sera prouvée). À savoir : les outils d'inventaire refusent un site qui porte un cache ou un pare-feu en fichier de remplacement (Wordfence) ; ils tourneront sur la copie de staging, ces fichiers écartés. **Et pas avant qu'A-22 soit clos** (point 5) : c'est mon avis, la décision de les lancer reste la tienne. **À savoir, depuis A-24 : l'état des adresses de livraison des abonnés ne se lira pas sur la copie neutralisée** (l'import efface les adresses, sauf le pays ; il ne reste que les effectifs et la répartition par pays). Pour savoir combien d'adresses sont vides ou incomplètes avant la première liste d'envoi, il faudra une lecture sur la source, par toi, hors agents : à décider le moment venu, rien n'est lancé.
5. **Si tu veux clore A-22 (une minute, sans Docker, rien de réel).** Tout est corrigé et vérifié, sauf une chose qu'aucun relecteur n'a le droit de lancer : le vérificateur du paquet de preuves. Depuis `C:\Users\Ced\imagine` : `C:/Python314/python.exe -B wp/tests/a22/verify.py production/A-22/preuves/final`. Il doit finir sur le code 0. Dis-le-moi et je clos ; s'il refuse, garde la sortie. Autre voie, si tu préfères ne plus avoir à le faire : ajouter cette commande à celles des relecteurs dans `scripts/relire.ps1` (ligne 24). Je ne l'ai pas fait moi-même : c'est une permission sur ta machine.
6. Toujours ouverts de ton côté : retirer l'autorisation du port 7000 du pare-feu Windows et jeter un œil à la box (A-07) ; détruire l'ancien staging d'Imagine quand le nouveau parcours est validé.
7. Le contraste des trois fonds du mode lecture sera à revalider à l'œil **après** le choix des couleurs par le designer, pas avant.

Décidé sans toi pendant ce passage, à défaire si tu n'es pas d'accord (`docs/arbitrages-2026-11-26.md`, passage de 22 h) :
- **A-20 et A-21 clos** (ce que paient les abonnés en ligne ; les clés d'interface et envois automatiques) : chacun a eu sa vérification sur le gardien final. **A-22 n'est pas clos** : rien à corriger, une preuve indépendante manquante (point 5) ;
- **A-23, A-24, A-25 relus « à corriger »**, sans bloquant : les comptes de gestion étaient mal écartés des lecteurs dans un cas rare (A-23), deux adresses qui ne diffèrent que par une majuscule ou un espace étaient comptées différentes (A-24), une forme de table de messages n'était pas comptée (A-25). Hermès dit tout corrigé ; restent ses bancs. A-26 et A-27 sont construits, en cours de preuve ;
- **l'alerte d'A-25 sur l'import devient un lot, A-28** (point 1) ;
- **B-06 code clos** (espace coopérateurs) ; **C-23 code clos** (test d'étanchéité de livraison : aucune fuite). Pour C-23, une partie du test, celle qui couvre les pages coopérateurs, a été ajoutée pendant les corrections et n'a pas été relue deux fois : je la garde, mais je ne la compte pas comme prouvée avant sa relecture, prévue avec le lot C-26 ;
- **C-24 (formulaire de personnalisation) relu « à corriger »** : la remise en état après une panne du journal ne marchait pas, et une inscription d'office à la newsletter valait accord pour la transmission. Corrigé à 21 h 58, vérification attendue. **B-07 (agenda) rendu, relu « à corriger »**, sans bloquant, corrections en cours ;
- le style du code de la voie 2 n'est pas strictement PSR-12 : je le laisse en dette jusqu'au gel du code, pour ne pas périmer les preuves des lots que tu dois encore regarder ;
- trois lots nouveaux, tous sur données fictives. Voie 1 : A-28 (les messages de formulaires ne survivent pas à l'import) et A-29 (les tâches planifiées du site actuel, comptées : renouvellements attendus par semaine, tâches en retard ; pour choisir le moment de la bascule). Voie 2 : C-26 (le test d'étanchéité étendu à l'agenda, à la personnalisation, à la rétractation et à « Soutenir ») ;
- une question visuelle t'attendra quand C-24 sera code clos : sa section placée sous le bouton « Enregistrer », comme celle de C-22 (une seule réponse vaudra pour les deux) ;
- à savoir : le dossier parasite `prefix}u0024s` à la racine du dossier du NUC, hors Git, est toujours là ; à supprimer à l'occasion.

## Mise en route

| Sujet | État | Prochaine étape | Qui |
|---|---|---|---|
| Dépôt | Créé ; cloné sur le NUC (`C:\Users\Ced\imagine`, alias SSH `github-imagine`) | — | — |
| Hermès sur ce dépôt | Travail en continu, réveil horaire planifié le 21/11 (`/cron`, verrou `.hermes.lock`) | — | — |
| Voie 2 (ce qui se voit) | Ouverte le 23/11 : file `A-FAIRE-2.md`, verrou `.hermes-2.lock`, site fictif `imagine-test-demo` en ligne sur le réseau local (port 8085). Code clos : B-00 à B-06, C-08 à C-23 (C-20 en périmètre réduit, sans bouton), complément de C-09. Le 26/11 : C-24 (formulaire de personnalisation) corrigé, vérification attendue ; B-07 (agenda) relu « à corriger » | En file : corrections de B-07, C-25 (rétractation en ligne), B-08 (« Soutenir » et « Notre coopérative »), C-26 (test d'étanchéité étendu). Validation visuelle par Ced | Hermès, Ced |
| Synchronisation Git | En service depuis le 20/11, 8 h 55. La nuit du 19 a été perdue : Git refusait les commits faute d'identité, et le script ne le signalait pas (corrigé) | — | — |
| Circuit de relecture | `scripts/relire.ps1` adapté aux lots ; se lance sans erreur, **pas encore testé sur un lot** | Lancer à la main sur le premier lot `PRET`, puis planifier « IMAGINE - relecture » | Ced |
| Staging | Pas de Docker sur le NUC : on utilise l'outil de staging de Ced, avec Novamira pour l'accès des agents. Étape « site à abonnements » à ajouter à l'outil (`prompts/2026-11-19-staging-imagine.md`). Le `docker-compose.yml` du dépôt n'est plus utilisé | Hermès ajoute l'étape ; puis retirer Docker du dépôt | Hermès, puis Claude |
| Exécution des tests PHP | Consigne donnée à Hermès : conteneur jetable de l'outil de staging, rien sur Windows | Confirmer dans son premier rapport que ça fonctionne | Hermès |
| Recette | Profils de test et 41 cas d'acceptance proposés dans `docs/recette/` | Relecture par Ced quand il verra Imagine | Ced |
| Rejeu des tests par les relecteurs | T-01 clos le 23/11 : `wp/tests/rejouer.ps1`, autorisée dans `scripts/relire.ps1`. **T-02 clos le 26/11** : elle joue aussi les tests purs des outils de la voie 1 et refuse un reçu mixte. Au 26/11, 22 h : 1 128 tests, 16 outils, 311 contrôles, rejoués par les vérificateurs eux-mêmes. Limite : les relecteurs ne peuvent lancer ni Docker ni une commande avec argument (vérificateurs de paquet) | — | — |

## A · L'existant

On repart de la production (décision du 11/11) : copie neutralisée et anonymisée dans Docker, audit, tests de non-régression, mise à jour de Memberships, nettoyage. Tout par scripts rejouables, parce que l'opération sera refaite le jour de la bascule.

| Lot | État | Prochaine étape | Qui |
|---|---|---|---|
| Sauvegarde de production | Pas encore récupérée | Export SQL + `wp-content`, déposés sur le NUC **hors du dépôt** | Ced |
| A-01 Import neutralisé | Qualifié en 6.9.1 sur archives fictives le 23/11. Diagnostics de Ced des 24 et 25/11 : l'archive réelle est lue en entier (16,9 Go, base 474 Mo). Troisième passe (base réelle) **close le 25/11** : tables hors catalogue restaurées vides, décisions par famille, deux dossiers exclus, neutralisation complétée (Stripe désactivée) Import lancé par Ced le 26/11 à 0 h 16 : échec à l'étape de la base, refus muet. Quatrième passe **close le 26/11** : reçus d'erreur assainis, compatibilité d'une base de production, répétition de la base seule | Ced répète la base seule (`--diagnose-database`), puis relance l'import sous un nom neuf : sa décision. Supprimer `imagine-test-a01-ced-02` | Ced |
| A-07 Exposition de l'outil de staging | Fait le 20/11. Test depuis l'extérieur en IPv4 : le tableau de bord n'est pas joignable. Non vérifié : redirections, DMZ et pare-feu IPv6 dans l'administration de la box | Coup d'œil à la box quand possible ; retirer l'autorisation du port 7000 en profil public du pare-feu Windows | Ced |
| Licences WooCommerce | Obtenues le 20/11 | Déposer les archives Subscriptions et Memberships dans le dossier des extensions premium de l'outil de staging, hors dépôt | Ced |
| Staging Imagine existant | Arrêté par Hermès le 19/11, non supprimé ; la révocation du mot de passe applicatif dans WordPress n'est pas attestée | Ne pas le redémarrer ; le détruire quand le nouveau parcours est validé | Ced |
| A-00 Couverture des extensions | **Clos le 21/11** : corrigé, arbitrages appliqués, vérifié au second tour | Branchement dans un lot ultérieur | — |
| A-02 Audit | **Clos le 23/11** (script prouvé sur site fictif, classique et HPOS) | Audit réel dès que le staging d'Imagine est vérifié | Hermès |
| A-03 Non-régression | **Clos le 25/11** (trois compléments vérifiés ; 1 012 tests rejoués par le vérificateur) | Rejeu sur le staging d'Imagine le jour venu | — |
| A-04 Mise à jour | **Clos le 25/11** (six corrections vérifiées). Limite : montée 6.9.1 → 7.0 sur la pile commerciale et migrations historiques des extensions payantes non prouvables sur le banc | Répétition sur le staging d'Imagine vérifié, avec un GO écrit | Ced |
| A-05 Nettoyage | **Clos le 25/11** (cinq corrections vérifiées) : l'outil exécute un plan et ne décide rien ; plan d'exemple tout à « garder » | Le plan du site réel sera rempli par Ced après l'audit ; passage sur le staging d'Imagine avec un GO écrit | Ced |
| A-08 Répétition de la bascule | **Clos le 26/11** : audit, non-régression, mise à jour, nettoyage enchaînés sur le banc fictif (classique et HPOS), refus au milieu, reprise, second passage sans effet ; marche à suivre avec une phrase simple par bloc. Limites d'A-04 inchangées | Répétition sur le staging d'Imagine vérifié, avec un GO écrit | Ced |
| A-09 Test des redirections | **Clos le 26/11** (manifeste restreint à son lot). L'outil vérifie un plan, ne décide d'aucune redirection | Le plan viendra du référenceur | Ced, référenceur |
| A-10 Inventaire des codes de réduction | **Clos le 26/11** (sept corrections vérifiées), lecture seule ; les codes encore portés par des abonnés mais dont la fiche a disparu sont visibles | Inventaire réel sur le staging d'Imagine vérifié ; reclasser ou supprimer reste à Imagine | Ced, Imagine |
| A-11 Inventaire des adresses publiques | **Clos le 26/11** : la liste dont le référenceur a besoin pour écrire le plan (§4.3), lecture seule. Refuse, en nommant le fichier, un site qui porte un cache ou un pare-feu en fichier de remplacement | Inventaire réel sur la copie de staging vérifiée, ces fichiers écartés | Ced |
| A-12 Inventaire des contenus | **Clos le 26/11** : structure des contenus existants (types, taxonomies, clés de champs, pièces jointes), sans aucune valeur (§4.3) | Inventaire réel sur la copie de staging vérifiée | Ced |
| A-13 Contrôle d'un export hors ligne | **Clos le 26/11** : contrôle d'un fichier d'abonnés hors ligne (doublons, échéances, aucun IBAN), sur fichier fictif ; suite rejouable sous Windows | Servira à A-06 quand l'export d'Imagine arrivera | Imagine |
| A-14 Rapprochement des contacts de la newsletter | **Clos le 26/11** : ce que donnerait le rapprochement d'un export de contacts avec les comptes (§4.3), sur fichier fictif ; n'appelle pas Brevo, n'écrit rien | Rapprochement réel le jour venu, sur un export fourni par Imagine : décision de Ced | Ced |
| A-15 Inventaire des emails | **Clos le 26/11** : la liste des emails que le site envoie aujourd'hui (§3.8), lecture seule, sans adresse ni texte | Inventaire réel sur la copie de staging vérifiée | Ced |
| A-16 État des lieux des dix derniers numéros | **Clos le 26/11** (cinq corrections et une retouche vérifiées) : par numéro, ce qui est rattaché et ce qui manque (§4.3) ; ne rattache rien | État des lieux réel sur la copie de staging vérifiée | Ced |
| A-17 Sécurité des comptes de l'administration | **Clos le 26/11** (neuf corrections vérifiées) : comptes par rôle, protections présentes (§4.4) ; aucun nom, ne modifie rien. Sur une copie neutralisée, le compte des mots de passe d'application vaut « inconnu » | Inventaire réel sur la copie de staging vérifiée | Ced |
| A-18 Ce que le site garde et ne devrait pas garder | **Clos le 26/11** (sept corrections vérifiées) : valeurs en forme d'IBAN ou de carte comptées par clé, dans les deux magasins de commandes ; fichiers d'abonnés dans le dossier des médias comptés par dossier (§4.4) ; aucune valeur, ne supprime rien. Ne dit pas si le serveur protège ces fichiers | Inventaire réel sur la copie de staging vérifiée ; la protection du dossier des médias se vérifie autrement | Ced |
| A-19 Cohérence des abonnements et des adhésions | **Clos le 26/11** (quatre corrections vérifiées) : abonnements sans adhésion, adhésions sans abonnement, renouvellements automatiques sans moyen de paiement (§4.3) ; des comptes seulement, ne corrige rien | Inventaire réel sur la copie de staging vérifiée | Ced |
| A-20 Ce que paient les abonnés en ligne | **Clos le 26/11** (cinq corrections vérifiées, paquet refait sur le gardien final) : abonnements par produit, rythme, montant et pays de livraison, groupes de moins de cinq fondus (§3.4, §4.3) ; des comptes seulement | Inventaire réel sur la copie de staging vérifiée | Ced |
| A-21 Les portes vers l'extérieur | **Clos le 26/11** (quatre corrections vérifiées, paquet refait sur le gardien final) : clés d'interface et envois automatiques de WooCommerce, comptés (§4.4) ; aucune clé, aucune adresse, ne révoque rien | Inventaire réel sur la copie de staging vérifiée | Ced |
| A-22 Un seul gardien pour les sorties | Corrigé le 26/11 : six corrections faites, cinq vérifiées par des tests rejoués (un seul lecteur des flux pour tous les outils qui chargent le WordPress du site, contenu des rapports contrôlé avant publication). **Pas clos** : le vérificateur du paquet n'a été lancé par aucun relecteur | Une commande d'une minute par Ced (« En attente de Ced », point 5), puis clôture | Ced, Claude |
| A-23 Les comptes des abonnés | Relu « à corriger » le 26/11 (comptes de gestion mal écartés dans un cas rare) ; corrections faites, sans `PRET` : familles d'empreintes de mots de passe, adresses vides ou en double, identifiants, comptés (§4.3). Sur une copie neutralisée, ces nombres valent « inconnu » | Matrice native et portes d'Hermès, `PRET`, vérification | Hermès, relecteurs |
| A-24 Les adresses d'expédition | Relu « à corriger » le 26/11 (comparaison au compte trop littérale) ; corrections faites, sans `PRET` : adresses de livraison des abonnements vivants, vides ou incomplètes, comptées (§3.13). Sur une copie neutralisée, presque tous ces nombres valent « inconnu » | Matrice native et portes d'Hermès, `PRET`, vérification ; la lecture sur la source est une décision de Ced | Hermès, Ced |
| A-25 Ce que le site garde sur ses visiteurs | Relu « à corriger » le 26/11 (une forme de table de messages non comptée) ; corrections faites, sans `PRET` : commentaires, messages de formulaires, commandes sans compte, comptés par année (§4.4, registre des traitements). A levé l'alerte sur l'import (A-28) | Matrice native et portes d'Hermès, `PRET`, vérification | Hermès, relecteurs |
| A-26 Ce que le site charge chez des tiers | Construit le 26/11, sans `PRET` : mesure d'audience, pixels, contenus intégrés, comptés par famille (§4.4, cookies et registre) ; aucun identifiant ne sort | Matrice native, portes, `PRET` | Hermès |
| A-27 Les moyens de paiement enregistrés | Construit le 26/11, sans `PRET` : abonnements en renouvellement automatique comptés par passerelle et par type de référence (§4.3, §3.6) ; aucun jeton ne sort. Sur une copie neutralisée, tous ces nombres valent « inconnu » (l'import purge jetons et références) | Matrice native, portes, `PRET` ; le compte sur la source serait une décision de Ced | Hermès, Ced |
| A-28 Les messages de formulaires et l'import | Brief écrit le 26/11 : prouver par le vrai parcours ce qu'il reste des messages de formulaires, vider ceux d'une liste fermée, refuser un `garder` sur eux, faire refuser par la vérification une copie où il en reste (doctrine §3). Archives fictives ; aucune commande de Ced ne change | En file | Hermès |
| A-29 Ce que le site fait tout seul | Brief écrit le 26/11 : tâches planifiées comptées par famille, en retard, en échec, renouvellements attendus par semaine (§4.3, §3.8) ; rien n'est exécuté | En file | Hermès |
| A-06 Import des abonnés hors ligne | En attente de l'export Access ; A-13 prépare le contrôle du fichier | — | Imagine |

## B · Le thème

| Lot | État | Prochaine étape | Qui |
|---|---|---|---|
| Page d'accueil | En cours de maquette | Validation par Imagine | Design |
| Déclinaison complète | Note pour le designer prête (`prompts/2026-11-19-design-complet.md`) : le système de design avec ses valeurs et une page par point. Le design reste son domaine | À transmettre quand l'accueil est validé ; maquettes et système de design remis ensuite à Hermès | Ced, puis Design |
| Gabarits | En attente des maquettes | — | — |

## C · Le code sur mesure

| Lot | État | Prochaine étape | Qui |
|---|---|---|---|
| C-01 Règle des numéros | **Clos le 21/11** : corrigé, arbitrages appliqués, vérifié au second tour | Branchement dans un lot ultérieur | — |
| C-04 File du connecteur | **Clos le 21/11** : corrigé, arbitrages appliqués, vérifié au second tour | Branchement dans un lot ultérieur | — |
| C-03 Vérification des robots | **Clos le 21/11** : corrigé, arbitrages appliqués, vérifié au second tour | Branchement dans un lot ultérieur | — |
| C-02 Numéro d'entreprise | **Clos le 21/11** : corrigé, arbitrages appliqués, vérifié au second tour | Branchement dans un lot ultérieur | — |
| C-06 Décision d'accès | **Clos le 23/11.** Trois réglages, 63 tests | Branchement dans un lot ultérieur | — |
| C-05 Échéancier en quatre fois | **Clos le 23/11.** Bibliothèque et preuve sur le vrai Subscriptions ; 765 tests dans la suite | Branchement dans un lot ultérieur, avec l'écran de réglages | — |
| C-07 Liste d'envoi | **Clos le 23/11.** Format d'export en réglage | Branchement dans un lot ultérieur | — |
| Suite | En attente | Voir `A-FAIRE.md` | — |

## En attente de tiers

| Sujet | Qui | Effet |
|---|---|---|
| Grille tarifaire, tarif solidaire, accès découverte | Imagine | Bloque le tunnel et les emails |
| Champs attendus par Odoo, email de facture | Step | Bloque le document d'interface et le connecteur |
| Documentation et accès de test CoopHub | Imagine, CoopHub | Sans réponse avant la fin de l'étude : intégration par lien |
| Maquettes | Design | Bloque le chantier B |
| Export de la base Access | Imagine | Bloque A-06 |

## Calendrier visé

Mise en ligne estimée fin janvier 2027 (§10), donc site complet en préproduction début janvier pour la recette d'Imagine. Tenable si la sauvegarde de production et les maquettes arrivent d'ici fin novembre.
