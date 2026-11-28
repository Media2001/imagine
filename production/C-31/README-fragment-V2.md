## C-31 — domaines refusés à l’inscription

Réglage propre « Réglages → Adresses à l’inscription », `manage_options` et Settings API : option `imagine_domaines_refuses`, un domaine exact par ligne. Liste vide par défaut ; trois domaines sous `example.org` sur la démonstration. Une ligne invalide conserve atomiquement l'ancienne liste. Comparaison sans casse, sous-domaines non hérités. ASCII/punycode seulement, aucun téléchargement ni service tiers.

La règle pure est dans `DomainesRefusesRegles`. `DomainesRefuses` la branche sur les inscriptions publiques natives WordPress/WooCommerce et sur le changement d'adresse Mon compte ; un email inchangé reste accepté même si son domaine a été ajouté après création. Message neutre proposant une autre adresse. Pas de filtre global `wp_insert_user` : administration et commande client C16 hors périmètre.

Le checkout classique est contrôlé dans `woocommerce_checkout_posted_data` **avant** la sauvegarde du client en session. Le checkout Blocks est contrôlé sur la route native `/wc/store/v1/checkout` dans `rest_request_before_callbacks`, avant son callback. Ces contrôles ne concernent que les commandes anonymes avec création de compte demandée ou obligatoire ; aucune restriction nouvelle pour l'invité sans création ni pour le compte déjà connecté. Ils corrigent une persistance réellement reproduite en session avant le refus tardif de la fabrique native.

`DomainesRefusesReglages` journalise les changements au format C10 et restaure la liste si le journal ne peut pas être écrit. Aucune adresse de lecteur n'est ajoutée aux journaux. La liste est tenue manuellement ; sa provenance reste la question déjà rangée pour Imagine.

Tests rejouables : `tests/DomainesRefusesC31Test.php`, `tests/DomainesRefusesC31AdapterTest.php`, bouchons isolés `tests/DomainesRefusesC31WPStubs.php` ; découverts automatiquement par le `phpunit.xml` existant. Recettes démo : `wp/tests/demo/c31-runtime.php`, `wp/outils/demo/c31-browser.py`, `c31-compte.py`, `c31-commande.py`. Aucune modification du runner partagé.

Depuis la racine du dépôt :

```text
python -B production/C-31/offline.py NOM-UNIQUE-V2
python -B production/C-31/offline.py AUTRE-NOM-UNIQUE-V2 --all
python -B production/C-31/verifier.py --pre-final --live
```

L'option `--all` exécute le paquet imagine-site complet dans l'image existante, hors ligne ; elle ne prépare pas l'image et ne lance pas le rejeu global. Les recettes live exigent le site fictif `imagine-test-demo` et ses gardes mail/HTTP/paiements. Ne jamais les lancer sur le réel. Les commandes finales, la distinction entre reçus historiques/courants et les captures se trouvent dans `production/C-31/FINALISATION-V2.md` et `A-VOIR.md`.
