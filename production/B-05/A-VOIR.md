# B-05 — À voir sur la démonstration fictive

Le partenaire du mois est le choix manuel **Association des Nuages fictifs** (48), enregistré par le formulaire natif C10.
Bloc facultatif, liste et fiche portent **Partenariat** et `imagine-partnership`, sans couleur ni style nouveau.
Squelette technique prêt ; le dessin de leur distinction reste au designer, la validation visuelle à Ced.

## Adresses

- Accueil : http://192.168.129.32:8085/ — en bas du contenu, un seul bloc « Partenaire du mois », texte Partenariat, lien vers la fiche choisie.
- Liste : http://192.168.129.32:8085/partenaires/ — « Nos partenaires », les deux partenaires fictifs B00, chaque carte étiquetée ; aucune nouvelle fiche inventée.
- Fiche B01 complétée : http://192.168.129.32:8085/partenaires/demo-partners-1/ — texte Partenariat et conteneur structurel propre.
- Réglage : http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages — compte administrateur fictif existant, section « Partenaires », liste « Partenaire du mois ». Choisir « Aucun — bloc masqué » masque l’accueil ; un autre choix remplace le précédent. Un partenaire dépublié ne s’affiche plus. Aucun compte réel.
- Recherche : http://192.168.129.32:8085/?s=fictifs — aucun partenaire parmi les résultats.
- Flux rédactionnel : http://192.168.129.32:8085/?feed=rss2 — aucun partenaire, même si son type est forcé dans l’URL.

## Preuves et limites

`accueil-partenaire.png` et `fiche-partenaire.png` : Chromium 1280 × 1000, pages canoniques après restauration des canaris de test. Aucun clic sortant ; trafic hors démo bloqué dans le navigateur.

`final-http.json` relit les pages réellement rendues, avec canaris temporaires sur les deux corps partenaires : liens absolus/protocole relatif déclarés `sponsored`, `noopener nofollow` conservés, liens internes non commerciaux. Le témoin article contient réellement un lien sortant non sponsorisé. Les corps initiaux sont ensuite restaurés exactement ; les URL externes de canari ne sont pas conservées sur le site.

`final-runtime.json` exerce le réglage natif dans une transaction rollbackée ; `final-admin.json` prouve sauvegarde C10, refus nonce/capacité et relecture. Le formulaire C10 peut initialiser des options anciennes absentes : leurs lignes/absences sont restaurées exactement, leurs journaux natifs append-only ne sont pas supprimés. Seule l’option B05 conserve le choix manuel 48.

`final.json` lie sources, reçus, captures, préparation d’image et T01. Les recettes B05 natives ne sont **pas** annoncées comme nouveaux tests PHPUnit de T01 : le canonique demeure 1097 tests / 34443 assertions. C09 382/382 et action 8793 pending / abonnement 101 restent inchangés. Pas de nouvelle règle de référencement, acceptation éditoriale, style, rotation, paiement, email, compte réel ou intégration externe.

## Standard retenu

WordPress Settings API (`register_setting`, `sanitize_callback`, groupe existant `imagine_reglages`) pour la désignation ; hooks `admin_menu` pour étendre le formulaire C10 sans lire/modifier sa bibliothèque close. `pre_get_posts` et `exclude_from_search` pour fermer les sorties de recherche/flux. Le filtre B01 `WP_HTML_Tag_Processor` est conservé, sans regex de réécriture HTML ni nouvelle dépendance. Documentation officielle consultée :

- https://developer.wordpress.org/reference/functions/register_setting/
- https://developer.wordpress.org/reference/hooks/pre_get_posts/
- https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links

Extraits et HTTP 200 : `natif-sources.json`.

## Relecture ciblée

```bash
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/b05-verifier.py
```

Lecture des reçus et sources, puis empreintes exactes des fichiers installés, état métier, C09, action 8793, coupe-circuits et pages canoniques ; pas de reset ni réinstallation. Le verrou du parent est laissé intact. C22 n’est pas traité.
