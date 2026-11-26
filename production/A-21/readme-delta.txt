# Delta exact réservé au parent — README partagé

Fichier : C:/Users/Ced/imagine/wp/tests/a02-audit/README.md
Ne remplacer ni les commandes ni les deux lignes contractuelles A-21 existantes.
Ajouter après ces deux lignes, sur sa propre ligne (annexe admise par readme_contract) :

Magasin d’extensions A-21 : lecture directe de l’option native `woocommerce_helper_data` via `get_option()`, présence de `auth.access_token` seulement ; aucun appel à `WC_Helper::is_site_connected()`, aucune vérification distante.

Le README propre A-21 annonce déjà ce choix en sa ligne 9 « standard d'abord ».
Le contrat de deux lignes de production/A-21/readme-ajout.txt reste inchangé ; aucune empreinte entière du README partagé n'est utilisée. L'ajout ci-dessus n'exige pas de réexécuter le PHP et n'invalide pas les instantanés des dépendances ; vérifier de nouveau le paquet avec verify.py après l'ajout.
