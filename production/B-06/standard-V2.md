# B-06 — Standard d’abord (consultation du 26 novembre 2026)

1. WordPress prévoit les données supplémentaires du compte dans `usermeta`, sans ajouter un rôle ni un abonnement.
2. Les hooks natifs `show_user_profile`/`edit_user_profile` ajoutent le champ à la fiche du compte.
3. Les hooks `personal_options_update`/`edit_user_profile_update` reçoivent la sauvegarde ; un nonce B06 et le rôle strict `administrator` sont exigés en plus du droit natif d’éditer la fiche.
4. Memberships réserve déjà des pages à un ou plusieurs plans d’adhésion.
5. Ses règles et son shortcode `wcm_restrict` portent sur des plans, pas sur un attribut arbitraire du compte.
6. Transformer le statut en plan créerait une seconde adhésion et rapprocherait inutilement l’espace des droits des articles.
7. Choix : un attribut booléen, sa source `administration` et sa date UTC ; aucun plan, produit ni capacité ajoutés.
8. Les cinq pages utilisent le thème B-01 et les filtres WordPress pour contenu, requêtes, REST, flux et sitemap ; aucun CSS ajouté.
9. L’export et l’effacement sont deux callbacks enregistrés sur les filtres privacy natifs, sous une clé B06 distincte ; C-21 reste intégralement inchangé.
10. Le point nommé `imagine_cooperateur_modifie` est émis après changement audité, sans écouteur, appel, lien ni synchronisation CoopHub.

## Sources officielles lues

- WordPress, métadonnées et écrans natifs (page courante consultée ; dernière mise à jour affichée : 17 novembre 2022) : https://developer.wordpress.org/plugins/users/working-with-user-metadata/
- WooCommerce, restrictions Memberships, page courante : https://woocommerce.com/document/woocommerce-memberships-restrict-content/
- WordPress, exporteur natif, page courante : https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-exporter-to-your-plugin/
- WordPress, effaceur natif (mise à jour affichée : 16 septembre 2024) : https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-eraser-to-your-plugin/
- WordPress, sauvegarde native de la fiche : https://developer.wordpress.org/reference/functions/edit_user/

La voie REST de lecture documentaire a refusé l’extraction ; les pages ci-dessus ont été effectivement chargées et lues dans le navigateur. Rien n’est déduit d’une documentation CoopHub manquante.
