# C-31 — Adresses à l'inscription

Démo uniquement : `http://192.168.129.32:8085`.

- Administration : `Réglages → Adresses à l’inscription` (`/wp-admin/options-general.php?page=imagine-domaines-refuses`). Un domaine par ligne ; liste vide = aucune restriction. Liste tenue à la main, aucun service ni téléchargement.
- Trois domaines de démonstration : `jetable-fictif.example.org`, `temporaire-fictif.example.org`, `usage-unique-fictif.example.org`. Aucun abonné réel concerné.
- Comparaison exacte sans casse. `sub.jetable-fictif.example.org` n'est pas refusé par héritage : ajouter explicitement ce sous-domaine si voulu. ASCII/punycode saisi, pas de correction automatique, URL, wildcard ou adresse complète dans le réglage.
- Message neutre : « Cette adresse ne peut pas être utilisée pour créer ou modifier votre compte. Merci d’utiliser une autre adresse email. » L'adresse refusée n'est ni enregistrée ni journalisée.
- Formulaires natifs WP `/wp-login.php?action=register` et Woo « Mon compte » : même refus avant insertion ; commande avec création de compte : même fabrique native ; changement d'email « Mon compte » : même règle. Un email existant identique reste accepté même si son domaine a été ajouté après.
- Créations administratives et C16 hors de ces filtres, aucune fermeture de compte ni modification de droit. La recette a ouvert temporairement l'inscription des formulaires pour les éprouver, puis restauré les deux réglages exactement ; elle ne rend pas ce parcours publiquement ouvert en permanence.

Preuves : `native-final-V2.json` (32 contrôles : vrais register_new_user, wc_create_new_customer, WC_Checkout::process_customer, compte, SQL/journal, liste vide/casse/sous-domaine, exceptions et mutation réelle du filtre retiré) ; `browser-final-V2.json` (16 contrôles, vrais POST WP/Woo, zéro compte et aucune adresse dans users/usermeta/options, sonde retirée, profils/options/sessions restaurés). Capture `browser-final-V2.png`.

**Limite native hors lot** : le pied du formulaire wp-login appelle deux fois l'API de traductions du cœur via `login_footer → wp_dropdown_languages → translations_api`. Ces tentatives sont bloquées par la sonde hors ligne, identifiées par leurs traces sans arguments ; aucun autre HTTP ni aucun mail. Woo et le code C31 ne font aucun appel. La preuve ne prétend pas « zéro tentative du cœur ». Ne pas changer le cœur ni les gardes pour faire disparaître ce constat.

Image préparée avant PRET ; rejeu réel : **1219 tests / 36748 assertions PASS ; outils 23/852 zéro échec ; paquets13 zéro échec**. Sources officielles installées et contrats natifs : `standard-V2.json`, section README ; références documentaires sans visite externe.

```
python -B production/C-31/verifier.py
python -B production/C-31/verifier.py --live
python -B production/B-13/qualifier.py C-31
```

Rien de réel, aucun email envoyé, aucun prix, paiement, compte externe, cron ni bibliothèque close modifié. Validation visuelle de l'écran propre attendue.
