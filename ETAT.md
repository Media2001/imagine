# État des chantiers — mis à jour le 26 novembre 2026, 13 h 30 (passage automatique)

## En attente de Ced

Ce que toi seul peux faire, dans l'ordre d'utilité.

**Nouveau à 13 h : la voie 2 ne donne plus signe de vie.** Son dernier rapport date de 10 h 05, alors que sa file a du travail depuis 10 h 30 (corrections de B-05 et de C-22, puis C-23 et B-06). D'ici je ne peux pas voir pourquoi : jette un œil à sa session sur le NUC (réveil horaire, verrou `.hermes-2.lock` resté en place ?). La voie 1, elle, tourne : elle s'est arrêtée file vide à 12 h 15 et a de nouveau du travail.

1. **Archive d'Imagine : c'est à toi.** La quatrième passe d'A-01 est rendue, vérifiée et close (plus de refus muet : chaque échec dit l'étape, le code d'erreur, la ligne et la table, sans aucune valeur). Dans l'ordre :
   - d'abord la répétition de la base seule, quelques minutes, qui ne crée aucun site et ne restaure aucun fichier : `python .\wp\outils\staging-court\publish.py --diagnose-database --operator-ced --archive "$ARCHIVE_WPRESS"` (mode d'emploi en tête de `wp/outils/staging-court/README.md`) ;
   - si elle passe, l'import complet sous un nom neuf, `imagine-test-a01-ced-03` : ta décision ;
   - si elle refuse, le reçu nomme la cause ; dépose-le, la voie 1 la traitera. Refus possibles et attendus : une vue, un déclencheur ou une procédure dans la base (refusés en les nommant), une collation MySQL 8 non prévue ;
   - le site `imagine-test-a01-ced-02`, resté de l'import échoué, n'a pas été supprimé : Hermès ne peut pas prouver qu'il est vide sans lire la copie. À supprimer par toi dans l'outil de staging.
2. **À regarder sur le site de démonstration** (`http://192.168.129.32:8085`, réseau local ; pour chaque lot, `production/<lot>/A-VOIR.md` dit quoi ouvrir). Code clos, il ne manque que ton œil : B-00, B-01, C-08, C-10, C-11, C-12, C-13 (liste d'envoi, en `e-abo` ; vérifie aussi que les menus « Imagine » ne se doublent pas), C-14 (achat d'un numéro, en `p-numero`), B-03 (mode lecture), B-02 (« Mon compte », `/my-account/`), B-04 (page numéro, kiosque, thématiques), C-15 (écran des échéances, en `e-abo`), C-16 (commande pour un client), C-17 (justificatifs du tarif solidaire), C-18 (extractions), C-19 (tableau de bord, des nombres seulement), C-20 (« Mon compte » dit, profil par profil, comment se renouvelle l'abonnement ; **pas de bouton « ne pas renouveler »**, il viendra avec le staging vérifié), et depuis 13 h C-21 (export et effacement des données d'un compte, dans les outils de confidentialité de l'administration). Visibles mais pas encore clos, tu peux attendre : B-05 (partenaires, en correction), C-22 (« Mes newsletters » et la page « Nos newsletters », en correction).
   - **Une question pour toi sur B-04 : garde-t-on une étiquette d'accès (« Réservé »…) sur le kiosque, oui ou non ?** Les relecteurs proposent de la retirer (le cahier des charges ne demande que couverture, titre et date, et l'étiquette trompe quand le numéro contient des articles libres). Elle est laissée en place tant que tu n'as pas répondu.
   - **Une question pour toi sur C-22 : dans l'écran de réglages, la section « Newsletters » s'affiche sous le bouton « Enregistrer ». On la laisse là, ou on la remonte au-dessus du bouton ?** L'enregistrement fonctionne dans les deux cas ; elle reste en place tant que tu n'as pas répondu (capture : `production/C-22/reglages-newsletters.png`).
3. **Questions à porter à Imagine** quand tu les verras : `docs/decisions.md` (vingt, toutes déjà réglées sur un défaut prudent ; aucune nouvelle à 13 h).
4. Plus tard, pour le site réel, trois choses que les outils attendront de toi : le plan de nettoyage (`wp/outils/bascule/plan-imagine.exemple.json`, tout y est à « garder » ; l'outil qui l'exécute, A-05, est clos), le plan de redirections (avec le référenceur), et un GO écrit pour répéter la mise à jour sur le staging d'Imagine une fois vérifié (c'est là seulement que la montée 6.9.1 → 7.0 sera prouvée). À savoir : les outils d'inventaire refusent un site qui porte un cache ou un pare-feu en fichier de remplacement (Wordfence) ; ils tourneront sur la copie de staging, ces fichiers écartés. **Et pas avant qu'A-22 soit clos** (voir plus bas) : c'est mon avis, la décision de les lancer reste la tienne.
5. Toujours ouverts de ton côté : retirer l'autorisation du port 7000 du pare-feu Windows et jeter un œil à la box (A-07) ; détruire l'ancien staging d'Imagine quand le nouveau parcours est validé.
6. Le contraste des trois fonds du mode lecture sera à revalider à l'œil **après** le choix des couleurs par le designer, pas avant.

Décidé sans toi pendant ce passage, à défaire si tu n'es pas d'accord (`docs/arbitrages-2026-11-26.md`, passage de 13 h) :
- A-16, A-18 et A-19 clos sur preuves ; C-21 code clos, il ne lui manque que ton œil ;
- **A-20 et A-21 renvoyés en correction, et le défaut touche aussi les outils déjà clos.** Nos outils d'inventaire promettent qu'aucun nom ni chemin du site ne sort, erreurs comprises. Une relecture a montré qu'une extension du site peut écrire à l'opérateur en contournant notre filtre (écriture directe, arrêt en plein chargement, message de fin de processus). Les bancs ne le voyaient pas. Aucun de ces outils n'a tourné sur une copie du site réel, donc rien n'est sorti. J'ai demandé un seul gardien des sorties, commun, pour A-20 et A-21, puis un lot A-22 qui y fait passer tous les outils clos (A-12, A-15 à A-19 au moins) sans rouvrir ces lots : le rejeu de leurs suites suffira ;
- C-22 renvoyé en correction : un identifiant de newsletter retiré puis réutilisé aurait fait apparaître une case cochée que le lecteur n'a jamais cochée ; un identifiant déjà employé sera refusé. Rien ne part vers Brevo dans ce lot ;
- T-02 (les relecteurs rejouent eux-mêmes les tests purs des outils : 13 outils, 242 contrôles) est rendu et relu, les deux relecteurs ne sont pas d'accord ; j'attends la fusion ;
- voie 1 : deux lots nouveaux derrière les corrections, tous sur banc fictif : A-22 (le gardien commun) et A-23 (les comptes des lecteurs, comptés : familles d'empreintes de mots de passe, adresses vides ou en double ; pour savoir si la promesse « identifiant et mot de passe conservés » du §4.3 tient). Voie 2 : pas de nouveau brief, elle a quatre choses devant elle ;
- à savoir : un vérificateur signale un fichier parasite `prefix}u0024s` à la racine du dossier du NUC, hors Git ; à supprimer à l'occasion.

## Mise en route

| Sujet | État | Prochaine étape | Qui |
|---|---|---|---|
| Dépôt | Créé ; cloné sur le NUC (`C:\Users\Ced\imagine`, alias SSH `github-imagine`) | — | — |
| Hermès sur ce dépôt | Travail en continu, réveil horaire planifié le 21/11 (`/cron`, verrou `.hermes.lock`) | — | — |
| Voie 2 (ce qui se voit) | Ouverte le 23/11 : file `A-FAIRE-2.md`, verrou `.hermes-2.lock`, site fictif `imagine-test-demo` en ligne sur le réseau local (port 8085). Code clos : B-00 à B-04, C-08 à C-21 (C-20 en périmètre réduit, sans bouton), complément de C-09. B-05 et C-22 relus « à corriger ». **Aucun rapport depuis 10 h 05** | En file : corrections de B-05 et de C-22, C-23 (test d'étanchéité de livraison), B-06 (espace coopérateurs). Vérifier que la session tourne ; validation visuelle par Ced | Hermès, Ced |
| Synchronisation Git | En service depuis le 20/11, 8 h 55. La nuit du 19 a été perdue : Git refusait les commits faute d'identité, et le script ne le signalait pas (corrigé) | — | — |
| Circuit de relecture | `scripts/relire.ps1` adapté aux lots ; se lance sans erreur, **pas encore testé sur un lot** | Lancer à la main sur le premier lot `PRET`, puis planifier « IMAGINE - relecture » | Ced |
| Staging | Pas de Docker sur le NUC : on utilise l'outil de staging de Ced, avec Novamira pour l'accès des agents. Étape « site à abonnements » à ajouter à l'outil (`prompts/2026-11-19-staging-imagine.md`). Le `docker-compose.yml` du dépôt n'est plus utilisé | Hermès ajoute l'étape ; puis retirer Docker du dépôt | Hermès, puis Claude |
| Exécution des tests PHP | Consigne donnée à Hermès : conteneur jetable de l'outil de staging, rien sur Windows | Confirmer dans son premier rapport que ça fonctionne | Hermès |
| Recette | Profils de test et 41 cas d'acceptance proposés dans `docs/recette/` | Relecture par Ced quand il verra Imagine | Ced |
| Rejeu des tests par les relecteurs | T-01 clos le 23/11 : `wp/tests/rejouer.ps1`, autorisée dans `scripts/relire.ps1` ; le 26/11, le vérificateur de C-20 l'a lancée lui-même (1 114 tests). T-02 rendu le 26/11 : elle joue aussi les tests purs des outils de la voie 1 (1 123 tests, 13 outils, 242 contrôles), rejouée ainsi par trois vérificateurs. Relu, avis partagés | Fusion de T-02 attendue | Relecteurs |

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
| A-20 Ce que paient les abonnés en ligne | Rendu le 26/11, relu « à corriger » (un bloquant : les sorties du processus ne sont pas toutes filtrées) : abonnements par produit, rythme, montant et pays de livraison, groupes de moins de cinq fondus (§3.4, §4.3) ; les comptes eux-mêmes sont exacts | Corrections en tête de la voie 1 | Hermès |
| A-21 Les portes vers l'extérieur | Rendu le 26/11, relu « à corriger » (le même bloquant) : clés d'interface et envois automatiques de WooCommerce, comptés (§4.4) ; aucune clé, aucune adresse, ne révoque rien | Corrections en tête de la voie 1 | Hermès |
| A-22 Un seul gardien pour les sorties | Brief écrit le 26/11 : tous les outils d'inventaire passent par le même filtre des sorties ; les lots clos le restent | En file | Hermès |
| A-23 Les comptes des abonnés | Brief écrit le 26/11 : familles d'empreintes de mots de passe, adresses vides ou en double, identifiants, comptés (§4.3) ; aucune empreinte ni adresse ne sort | En file | Hermès |
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
