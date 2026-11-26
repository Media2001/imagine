# B-05 — À voir sur la démonstration fictive

## Corrections du 26 novembre 2026 — reçu courant V2

Les sept instructions de `corrections/B-05.md` sont appliquées. Le reçu courant est **`final-V2.json`** ; `final.json` et les reçus sans suffixe sont historiques et ne certifient plus l’arbre courant. Les captures courantes sont `accueil-partenaire-V2.png` et `fiche-partenaire-V2.png`. Détail, commandes et RED→GREEN : `CORRECTIONS-V2.md`.

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

`accueil-partenaire-V2.png` et `fiche-partenaire-V2.png` : Chromium 1280 × 1000, pages canoniques après restauration des canaris de test. Captures inspectées : bloc et étiquette présents, fiche sans canari résiduel visible. Aucun clic sortant ; trafic hors démo bloqué dans le navigateur.

`final-http-V2.json` : 50 contrôles réels, dont la liste d’articles non vide de l’accueil et trois mutations DOM (article sponsorisé, fiche partenaire et liste vide) détectées puis annulées. Canaris temporaires sur les deux corps partenaires : liens absolus/protocole relatif et les deux formes R1 malformées déclarés `sponsored`, `noopener nofollow` conservés, liens internes non commerciaux. Témoin article sortant non sponsorisé. Les corps et l’option B05 sont ensuite restaurés exactement.

`final-runtime-V2.json` : 15 contrôles natifs en transaction rollbackée. `final-admin-V2.json` : 12 contrôles de présence C10, refus nonce/capacité, lecture sans soumission du formulaire partagé et deux captures ; aucun réglage C22 n’est sauvegardé. La sauvegarde C10 nominale est historique ; la validation native B05 est rejouée. Option manuelle 48 inchangée.

`final-V2.json` lie les sources propres, contrats partagés, reçus et captures courants. Rejeu réel T01 : **1123 tests / 34569 assertions**, zéro échec/erreur/ignoré ; outils purs : 14 outils / 279 contrôles / zéro échec. B05 hors T01 : 64 contrôles PHP isolés, 9 contrôles Chromium hors réseau, 8 gates syntaxe/PSR12/nettoyage. C09 : 382/382, état métier et action 8793 inchangés. L’ancien `final.json` garde son constat daté 1097/34443 uniquement comme archive historique. Le hash global du bootstrap partagé n’est plus un verrou : le raccord B05 y est contrôlé par contrat, sans écrire ce fichier. Pas de nouvelle règle de référencement, style, rotation, paiement, email, compte réel ou intégration externe.

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

Sans argument : contrôles hors démo sur sources et reçus V2, sans réseau. Ajouter `--live` pour relire seulement les trois fichiers corrigés installés, le contrat du bootstrap partagé, les coupe-circuits et l’état métier. Rejeu comportemental hors live : `PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py relecture-IDENTIFIANT-UNIQUE-V2` (image WordPress publique déjà présente, aucun téléchargement). Les doubles de stockage ne simulent ni `wp_parse_url` ni le processeur HTML : les deux sont ceux du cœur WordPress réel embarqué. Aucun reset/réinstallation. C22, les verrous et les fichiers d’orchestration sont laissés intacts.
