# B-06 — À voir sur la démonstration

Site exclusivement fictif : **http://192.168.129.32:8085**. Pas de CoopHub, service bancaire, email sortant ni accès au site réel.

## Parcours

1. Connecté en **administrateur**, ouvrir http://192.168.129.32:8085/wp-admin/user-edit.php?user_id=29 : section **Espace coopérateurs**, case « Ouvrir l’espace coopérateurs, jamais les articles », source administration et date UTC. La fiche est celle de **P-COOP**, login `p-coop`. La case n’est pas proposée aux autres rôles, même munis d’une capacité large.
2. En **p-coop**, ouvrir http://192.168.129.32:8085/my-account/ : ligne **Coopérateur : oui**, source administration, date, lien vers l’espace. Les identifiants fictifs C09 restent hors dépôt, ils ne sont jamais dans les reçus.
3. Ouvrir http://192.168.129.32:8085/espace-cooperateurs/ : les quatre liens, dans le squelette B-01, sans contenu métier inventé.
   - http://192.168.129.32:8085/espace-cooperateurs/appels-a-benevolat/
   - http://192.168.129.32:8085/espace-cooperateurs/lettre-de-missions/
   - http://192.168.129.32:8085/espace-cooperateurs/cadastre-des-competences/
   - http://192.168.129.32:8085/espace-cooperateurs/relais-des-evenements/
4. Toujours en **p-coop**, ouvrir http://192.168.129.32:8085/c08-article-reserve-article/ : **extrait public**, jamais le corps réservé. L’abonné **a-carte** lit ce même corps mais pas l’espace coopérateurs.
5. Déconnecté, ou en **a-carte**/**v-inscrit**, ouvrir une des cinq pages : « Cet espace est réservé aux coopérateurs », sans contenu de l’espace. Dans Mon compte, les non-coopérateurs voient **Coopérateur : non**, sans lien d’ouverture réservé.
6. Depuis la fiche administrateur, décocher puis enregistrer : P-COOP perd immédiatement l’accès ; recocher rouvre l’espace. **La recette l’a réellement fait par GET/POST de la fiche native**, puis a relu le statut et les pages.
7. Journal de l’administration : http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages : chaque vrai changement B06 est daté et attribué à son opérateur, comme C17 ; une sauvegarde identique ne crée pas d’événement.
8. Outils natifs : http://192.168.129.32:8085/wp-admin/export-personal-data.php et http://192.168.129.32:8085/wp-admin/erase-personal-data.php . B06 ajoute ses callbacks aux registres existants, sans modifier C21 ; ils ont été appelés avec de vrais comptes fictifs transactionnels. **Ne pas effacer P-COOP pour regarder l’écran** : il est laissé en état de démonstration. Aucun email de demande n’a été envoyé.

## Preuves et limites

- Reçu courant : `livraison-V2.json` et ses sous-reçus `livraison-*-V2.json` : **165 contrôles verts**, **11 mutations détectées** ; recettes réelles et vérificateur à code 0. Régression générale : **1 123 tests, 34 569 assertions**, plus **306 contrôles d’outils**, sans échec. Image préparée après les nouveaux tests ; PSR12 du code produit sans erreur bloquante. Les reçus rouges/historiques restent distincts et ne valent pas acceptation.
- Étanchéité : pages, REST unitaire/collection/recherche, flux, recherche interne et fournisseur sitemap natif. Témoins positifs, puis mutations qui rendent les contrôles rouges ; aucune absence déduite d’une surface inexistante.
- **Le site est volontairement noindex** : la route HTTP sitemap est 404 native. La preuve de filtrage des URLs passe aussi par le vrai fournisseur `WP_Sitemaps_Posts::get_url_list()`, avec une page publique présente et une mutation révélant les pages réservées. Le réglage noindex n’a pas été ouvert pour les besoins du test.
- Le texte témoin de la lettre de missions est retiré ; les **cinq pages sont vides** après la recette. Les vrais événements d’audit B06 restent. Les fixtures transactionnelles sont rollbackées.
- **Seule exception conservée : l’attribut P-COOP**, posé par l’écran. Les autres comptes, métadonnées, rôles, abonnements, préférences, réglages Imagine et actions métier sont restaurés et relus exactement ; aucun reset global C09.
- Aucun nouveau style, formulaire de parts, compteur de campagne, lien ou synchronisation CoopHub. Le hook nommé `imagine_cooperateur_modifie` n’a pas d’écouteur. Aucun test de charge, cache hébergeur ni intégration réelle n’est revendiqué.

## Questions fermées pour Imagine

1. **Garder le seul rôle Administrateur pour poser/retirer le statut : oui/non ?** Défaut appliqué : oui. Un autre rôle éventuel doit être nommé explicitement ; `manage_options` seul n’est pas assimilé à ce rôle.
2. **Garder Administrateur comme seul rôle lisant l’espace sans statut coopérateur : oui/non ?** Défaut appliqué : oui. Les éditeurs/gestionnaires non coopérateurs restent refusés, y compris via l’édition native.

La présentation reste à valider par **Ced** et le code à clore par **Claude**. `PRET`, s’il est présent avec la vérification verte, signifie seulement **prêt à relire**, jamais un GO sur le réel.
