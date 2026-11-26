# B-06 — À voir sur la démonstration

Site exclusivement fictif : **http://192.168.129.32:8085**. Pas de CoopHub, service bancaire, email sortant ni accès au site réel.

## Parcours

1. Connecté en **administrateur**, ouvrir http://192.168.129.32:8085/wp-admin/user-edit.php?user_id=29 : section **Espace coopérateurs**, case « Ouvrir l’espace coopérateurs, jamais les articles », source administration et date UTC. La fiche est celle de **P-COOP**, login `p-coop`. Avec le réglage actuel, la case n’est pas proposée aux autres rôles, même munis d’une capacité large.
2. En **p-coop**, ouvrir http://192.168.129.32:8085/my-account/ : ligne **Coopérateur : oui**, source administration, date, lien vers l’espace. Les identifiants fictifs C09 restent hors dépôt, ils ne sont jamais dans les reçus.
3. Ouvrir http://192.168.129.32:8085/espace-cooperateurs/ : les quatre liens, dans le squelette B-01, sans contenu métier inventé.
   - http://192.168.129.32:8085/espace-cooperateurs/appels-a-benevolat/
   - http://192.168.129.32:8085/espace-cooperateurs/lettre-de-missions/
   - http://192.168.129.32:8085/espace-cooperateurs/cadastre-des-competences/
   - http://192.168.129.32:8085/espace-cooperateurs/relais-des-evenements/
4. Toujours en **p-coop**, ouvrir http://192.168.129.32:8085/c08-article-reserve-article/ : **extrait public**, jamais le corps réservé. L’abonné **a-carte** lit ce même corps mais pas l’espace coopérateurs.
5. Déconnecté, ou en **a-carte**/**v-inscrit**, ouvrir une des cinq pages : « Cet espace est réservé aux coopérateurs », sans contenu de l’espace. Dans Mon compte, les non-coopérateurs voient **Coopérateur : non**, sans lien d’ouverture réservé.
6. Depuis la fiche administrateur, décocher puis enregistrer : P-COOP perd immédiatement l’accès et la source/date disparaît de la fiche comme de Mon compte ; recocher rouvre l’espace. **La recette l’a réellement fait par GET/POST de la fiche native**, puis a relu le statut et les pages. L’affichage UTC brut quand le statut est vrai est inchangé.
7. Journal de l’administration : http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages : chaque vrai changement B06 est daté et attribué à son opérateur, comme C17 ; une sauvegarde identique ne crée pas d’événement.
8. Outils natifs : http://192.168.129.32:8085/wp-admin/export-personal-data.php et http://192.168.129.32:8085/wp-admin/erase-personal-data.php . B06 ajoute ses callbacks aux registres existants, sans modifier C21 ; ils ont été appelés avec de vrais comptes fictifs transactionnels. **Ne pas effacer P-COOP pour regarder l’écran** : il est laissé en état de démonstration. Aucun email de demande n’a été envoyé.
9. Dans **Imagine → Réglages**, section **Espace coopérateurs**, deux listes indépendantes : rôles posant/retirant l’attribut et rôles lisant sans attribut. Défaut : **Administrateur seul** pour les deux. Choix proposés : Administrateur, Éditeur, Gestionnaire de boutique, toutes leurs combinaisons ou aucun. Les **64 configurations croisées** ont été exercées sur les vrais adaptateurs ; aucune ne change les droits de l’article. La modification du réglage exige le rôle Administrateur et la capacité native ; les valeurs invalides sont refusées et les changements journalisés.

## Preuves et limites

- Reçu courant après les cinq corrections fusionnées : `fusion-livraison-V2.json` et ses sous-reçus : **916 contrôles verts**, **13 mutations détectées** ; dont **728 contrôles des réglages** et **88 HTTP natifs**. Vérificateur à code 0. Régression canonique horslive : **1 126 tests, 35 550 assertions**, plus **311 contrôles d’outils**, sans échec. `CooperateursReglesTest` est réellement découvert : **3 tests, 981 assertions** sans WordPress ni base. Image préparée après les nouveaux tests (`fusion-image-final-V2.json`), PSR12 sans erreur (`fusion-quality-V2.json`). Les anciens reçus à 165 contrôles/11 mutations et les rouges restent historiques, distincts de cette livraison.
- Étanchéité : pages, REST unitaire/collection/recherche, flux, recherche interne et fournisseur sitemap natif. Témoins positifs, puis mutations qui rendent les contrôles rouges ; aucune absence déduite d’une surface inexistante.
- Collection REST : page publique témoin présente et pages réservées absentes pour anonyme, abonné non coopérateur et éditeur non coopérateur ; mutation de la vraie protection `pre_get_posts` détectée. Les deux formes HTTP, `/wp-json/…` et `?rest_route=…`, sont exercées.
- Erreurs SQL avec événements présents : export refusé proprement, effacement `items_retained=true` / `done=false`. La panne de relecture finale après 50 événements sur 51 laisse un événement, détecté puis anonymisé à la reprise. L’export et l’effacement redeviennent complets après rétablissement (`fusion-livraison-privacy-V2.json`).
- **Le site est volontairement noindex** : la route HTTP sitemap est 404 native. La preuve de filtrage des URLs passe aussi par le vrai fournisseur `WP_Sitemaps_Posts::get_url_list()`, avec une page publique présente et une mutation révélant les pages réservées. Le réglage noindex n’a pas été ouvert pour les besoins du test.
- Le texte témoin de la lettre de missions est retiré ; les **cinq pages sont vides** après la recette. Les vrais événements d’audit B06 restent. Les fixtures transactionnelles sont rollbackées.
- **Seule exception conservée : l’attribut P-COOP**, posé par l’écran. Les autres comptes, métadonnées, rôles, abonnements, préférences, réglages Imagine et actions métier sont restaurés et relus exactement ; aucun reset global C09.
- Préimages durables privées écrites et relues dans le scratch avant les mutations de données ; la restauration HTTP utilise cette copie sur disque, sessions comprises. Aucun secret de session dans le dépôt : les reçus ne portent qu’identifiant opaque et empreinte de la préimage.
- Aucun nouveau style, formulaire de parts, compteur de campagne, lien ou synchronisation CoopHub. Le hook nommé `imagine_cooperateur_modifie` n’a pas d’écouteur. Aucun test de charge, cache hébergeur ni intégration réelle n’est revendiqué.

## Questions fermées pour Imagine

1. **Garder le seul rôle Administrateur pour poser/retirer le statut : oui/non ?** Défaut appliqué : oui. Un autre rôle éventuel doit être nommé explicitement ; `manage_options` seul n’est pas assimilé à ce rôle.
2. **Garder Administrateur comme seul rôle lisant l’espace sans statut coopérateur : oui/non ?** Défaut appliqué : oui. Les éditeurs/gestionnaires non coopérateurs restent refusés, y compris via l’édition native.

Ces choix sont désormais deux réglages, pas des constantes. Leur défaut prudent n’attend pas une réponse pour le rejeu technique. **Date UTC brute ou présentation locale / `datetime` machine ?** Question visuelle laissée à Ced, affichage conservé.

La présentation reste à valider par **Ced** et le code à clore par **Claude**. `PRET`, s’il est présent avec la vérification verte, signifie seulement **prêt à relire**, jamais un GO sur le réel.
