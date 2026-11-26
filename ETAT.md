# État des chantiers — mis à jour le 26 novembre 2026, 1 h 30 (passage automatique)

## En attente de Ced

Ce que toi seul peux faire, dans l'ordre d'utilité. Rien d'autre n'attend : les deux voies ont du travail.

1. **Archive d'Imagine.** Import lancé par Ced le 26/11 à 0 h 16 : fichiers restaurés (16,9 Go), **échec à l'import de la base**, sans message exploitable. Quatrième passe demandée à Hermès (`briefs/A-01-archive-reelle-4.md`). Rien à faire pour l'instant ; quand elle sera rendue et relue, Ced lancera la répétition de la base seule (`--diagnose-database`), puis l'import sous le nom `imagine-test-a01-ced-03`.
2. **À regarder sur le site de démonstration** (`http://192.168.129.32:8085`, réseau local ; pour chaque lot, `production/<lot>/A-VOIR.md` dit quoi ouvrir). Code clos, il ne manque que ton œil : B-00, B-01, C-08, C-10, C-11, C-12, C-13 (liste d'envoi, en `e-abo` ; vérifie aussi que les menus « Imagine » ne se doublent pas), C-14 (achat d'un numéro, en `p-numero`), B-03 (mode lecture), et depuis cette nuit **B-02** (« Mon compte », `/my-account/`), **B-04** (page numéro, kiosque, thématiques) et **C-15** (écran des échéances, en `e-abo`). Visible mais encore en relecture : C-16 (commande pour un client, trois écrans, en `e-abo`).
   - **Une question pour toi sur B-04 : garde-t-on une étiquette d'accès (« Réservé »…) sur le kiosque, oui ou non ?** Les relecteurs proposent de la retirer (le cahier des charges ne demande que couverture, titre et date, et l'étiquette trompe quand le numéro contient des articles libres). Elle est laissée en place tant que tu n'as pas répondu.
3. **Questions à porter à Imagine** quand tu les verras : `docs/decisions.md` (neuf, toutes déjà réglées sur un défaut prudent ; aucune nouvelle cette nuit).
4. Plus tard, pour le site réel, trois choses que les outils attendront de toi : le plan de nettoyage (`wp/outils/bascule/plan-imagine.exemple.json`, tout y est à « garder » ; l'outil qui l'exécute, A-05, est clos), le plan de redirections (avec le référenceur), et un GO écrit pour répéter la mise à jour sur le staging d'Imagine une fois vérifié (c'est là seulement que la montée 6.9.1 → 7.0 sera prouvée).
5. Toujours ouverts de ton côté : retirer l'autorisation du port 7000 du pare-feu Windows et jeter un œil à la box (A-07) ; détruire l'ancien staging d'Imagine quand le nouveau parcours est validé.
6. Le contraste des trois fonds du mode lecture sera à revalider à l'œil **après** le choix des couleurs par le designer, pas avant.

Décidé sans toi pendant ce passage, à défaire si tu n'es pas d'accord (`docs/arbitrages-2026-11-26.md`) : A-08 et A-10 clos sur preuves ; la vérification d'A-09 te renvoyait une question qui n'en était pas une (son fichier d'empreintes surveillait `A-FAIRE.md`, qui change à chaque passage) : corrigé par une règle d'empaquetage ; le profil fictif A-PAPIER, dont une action planifiée avait été annulée pendant des tests, est remis en état par son propre jeu de données ; cinq lots mis en file, tous en lecture seule ou sur données fictives (`A-FAIRE.md`, `A-FAIRE-2.md`). La voie 1 s'était arrêtée file vide à 0 h 56, juste avant que la quatrième passe d'A-01 n'y soit mise.

## Mise en route

| Sujet | État | Prochaine étape | Qui |
|---|---|---|---|
| Dépôt | Créé ; cloné sur le NUC (`C:\Users\Ced\imagine`, alias SSH `github-imagine`) | — | — |
| Hermès sur ce dépôt | Travail en continu, réveil horaire planifié le 21/11 (`/cron`, verrou `.hermes.lock`) | — | — |
| Voie 2 (ce qui se voit) | Ouverte le 23/11 : file `A-FAIRE-2.md`, verrou `.hermes-2.lock`, site fictif `imagine-test-demo` en ligne sur le réseau local (port 8085). Code clos : B-00 à B-04, C-08 à C-15, complément de C-09. Rendu le 26/11 et en relecture : C-16 (commande pour un client, encodage sans email) | En cours : C-17 (justificatifs du tarif solidaire). En file : C-18 (extractions), C-19 (tableau de bord), C-20 (« ne pas renouveler » dans Mon compte), C-21 (export et effacement des données d'un compte). Validation visuelle par Ced | Hermès, Ced |
| Synchronisation Git | En service depuis le 20/11, 8 h 55. La nuit du 19 a été perdue : Git refusait les commits faute d'identité, et le script ne le signalait pas (corrigé) | — | — |
| Circuit de relecture | `scripts/relire.ps1` adapté aux lots ; se lance sans erreur, **pas encore testé sur un lot** | Lancer à la main sur le premier lot `PRET`, puis planifier « IMAGINE - relecture » | Ced |
| Staging | Pas de Docker sur le NUC : on utilise l'outil de staging de Ced, avec Novamira pour l'accès des agents. Étape « site à abonnements » à ajouter à l'outil (`prompts/2026-11-19-staging-imagine.md`). Le `docker-compose.yml` du dépôt n'est plus utilisé | Hermès ajoute l'étape ; puis retirer Docker du dépôt | Hermès, puis Claude |
| Exécution des tests PHP | Consigne donnée à Hermès : conteneur jetable de l'outil de staging, rien sur Windows | Confirmer dans son premier rapport que ça fonctionne | Hermès |
| Recette | Profils de test et 41 cas d'acceptance proposés dans `docs/recette/` | Relecture par Ced quand il verra Imagine | Ced |
| Rejeu des tests par les relecteurs | T-01 clos le 23/11 : `wp/tests/rejouer.ps1`, autorisée dans `scripts/relire.ps1` | Le 23/11 au soir, le relecteur s'est encore vu refuser la commande ; autorisation réécrite le 24/11, à revérifier | Claude |

## A · L'existant

On repart de la production (décision du 11/11) : copie neutralisée et anonymisée dans Docker, audit, tests de non-régression, mise à jour de Memberships, nettoyage. Tout par scripts rejouables, parce que l'opération sera refaite le jour de la bascule.

| Lot | État | Prochaine étape | Qui |
|---|---|---|---|
| Sauvegarde de production | Pas encore récupérée | Export SQL + `wp-content`, déposés sur le NUC **hors du dépôt** | Ced |
| A-01 Import neutralisé | Qualifié en 6.9.1 sur archives fictives le 23/11. Diagnostics de Ced des 24 et 25/11 : l'archive réelle est lue en entier (16,9 Go, base 474 Mo). Troisième passe (base réelle) **close le 25/11** : tables hors catalogue restaurées vides, décisions par famille, deux dossiers exclus, neutralisation complétée (Stripe désactivée) | Import lancé par Ced le 26/11 à 0 h 16 : échec à l'étape de la base, refus muet. Quatrième passe en tête de la voie 1 (`briefs/A-01-archive-reelle-4.md`) ; ensuite Ced répète la base seule, puis relance l'import : sa décision | Hermès, puis Ced |
| A-07 Exposition de l'outil de staging | Fait le 20/11. Test depuis l'extérieur en IPv4 : le tableau de bord n'est pas joignable. Non vérifié : redirections, DMZ et pare-feu IPv6 dans l'administration de la box | Coup d'œil à la box quand possible ; retirer l'autorisation du port 7000 en profil public du pare-feu Windows | Ced |
| Licences WooCommerce | Obtenues le 20/11 | Déposer les archives Subscriptions et Memberships dans le dossier des extensions premium de l'outil de staging, hors dépôt | Ced |
| Staging Imagine existant | Arrêté par Hermès le 19/11, non supprimé ; la révocation du mot de passe applicatif dans WordPress n'est pas attestée | Ne pas le redémarrer ; le détruire quand le nouveau parcours est validé | Ced |
| A-00 Couverture des extensions | **Clos le 21/11** : corrigé, arbitrages appliqués, vérifié au second tour | Branchement dans un lot ultérieur | — |
| A-02 Audit | **Clos le 23/11** (script prouvé sur site fictif, classique et HPOS) | Audit réel dès que le staging d'Imagine est vérifié | Hermès |
| A-03 Non-régression | **Clos le 25/11** (trois compléments vérifiés ; 1 012 tests rejoués par le vérificateur) | Rejeu sur le staging d'Imagine le jour venu | — |
| A-04 Mise à jour | **Clos le 25/11** (six corrections vérifiées). Limite : montée 6.9.1 → 7.0 sur la pile commerciale et migrations historiques des extensions payantes non prouvables sur le banc | Répétition sur le staging d'Imagine vérifié, avec un GO écrit | Ced |
| A-05 Nettoyage | **Clos le 25/11** (cinq corrections vérifiées) : l'outil exécute un plan et ne décide rien ; plan d'exemple tout à « garder » | Le plan du site réel sera rempli par Ced après l'audit ; passage sur le staging d'Imagine avec un GO écrit | Ced |
| A-08 Répétition de la bascule | **Clos le 26/11** : audit, non-régression, mise à jour, nettoyage enchaînés sur le banc fictif (classique et HPOS), refus au milieu, reprise, second passage sans effet ; marche à suivre avec une phrase simple par bloc. Limites d'A-04 inchangées | Répétition sur le staging d'Imagine vérifié, avec un GO écrit | Ced |
| A-09 Test des redirections | Corrections de code vérifiées le 25/11 ; reste une correction d'empaquetage (son fichier d'empreintes surveillait `A-FAIRE.md`). L'outil vérifie un plan, ne décide d'aucune redirection | Correction en file, puis clôture ; le plan viendra du référenceur | Hermès |
| A-10 Inventaire des codes de réduction | **Clos le 26/11** (sept corrections vérifiées), lecture seule ; les codes encore portés par des abonnés mais dont la fiche a disparu sont visibles | Inventaire réel sur le staging d'Imagine vérifié ; reclasser ou supprimer reste à Imagine | Ced, Imagine |
| A-11 Inventaire des adresses publiques | Rendu le 26/11 : la liste dont le référenceur a besoin pour écrire le plan (§4.3), lecture seule. À éclaircir : l'outil refuse un site qui porte un cache ou un pare-feu en fichier de remplacement, ce que le site réel a sans doute | Relecture | Relecteurs |
| A-12 Inventaire des contenus | Rendu le 26/11 : structure des contenus existants (types, taxonomies, clés de champs, pièces jointes), sans aucune valeur (§4.3) | Relecture | Relecteurs |
| A-13 Contrôle d'un export hors ligne | Rendu le 26/11 : contrôle d'un fichier d'abonnés (doublons, échéances, rejets, refus de tout IBAN) sur fichier fictif ; n'importe rien | Relecture | Relecteurs |
| A-14 Rapprochement des contacts de la newsletter | Brief écrit le 26/11 : ce que donnerait le rapprochement d'un export de contacts avec les comptes (§4.3), sur fichier fictif ; n'appelle pas Brevo, n'écrit rien | En file | Hermès |
| A-15 Inventaire des emails | Brief écrit le 26/11 : la liste des emails que le site envoie aujourd'hui (§3.8), lecture seule, sans adresse ni texte | En file | Hermès |
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
