# A-20 — Photographie des récurrences enregistrées

Lecture seule : aucune modification, correspondance ancien/nouveau tarif, conversion monétaire ou qualification en anomalie. Un abonnement n'est pas une personne ; ce rapport ne prouve aucun encaissement.

## Standard vérifié avant l'adaptateur

- WooCommerce Subscriptions, référence officielle des fonctions : https://woocommerce.com/document/subscriptions/develop/functions/ : `WC_Subscription` hérite de l'ordre, porte son intervalle/période et son total récurrent. **Depuis WCS 2.1, le montant effectivement prélevé peut suivre le dernier renouvellement et des personnalisations**, plutôt que ce total. Ce lot photographie le total enregistré, pas un futur prélèvement garanti.
- États natifs : https://woocommerce.com/document/subscriptions/statuses/ ; périmètre explicite du brief : `active`, `pending`, `on-hold`, `pending-cancel` uniquement.
- HPOS : https://developer.woocommerce.com/docs/features/orders/high-performance-order-storage/recipe-book/ : utiliser CRUD et non supposer `wp_posts` autoritaire.
- Référence Woo : https://woocommerce.github.io/code-reference/classes/WC-Abstract-Order.html : `get_total('edit')`, `get_items('line_item'|'fee'|'shipping')` et pays enregistré via l'ordre. Le total inclut taxes, frais, port et remises. Aucune somme de lignes ou simulation de panier.

Le standard possède les objets et les lectures ; le complément ne fait que projeter les identifiants techniques et compter en PHP pur, puis masquer les petits groupes. Aucun ordonnanceur ni écran ajouté.

## Commande opérateur

Après autorisation sur une **copie vérifiée** et son audit A-02, dans un conteneur Linux sans réseau, PHP 8.2+/pdo_mysql, Python3/Landlock existants, parent `/hors-web` existant, sortie neuve hors site/dépôt et sœur de l'audit :

```text
python3 wp/outils/bascule/a20/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/tarifs-date
```

Aucun autre argument requis. `tarifs.json` et `tarifs.md` (0700/0600) ne contiennent que des agrégats. Aucun compte, identifiant d'abonnement/commande, nom, adresse ou chemin issu du site. Les refus donnent un code fermé, plus éventuellement un nom technique de fichier de remplacement pris dans la liste fermée A-11. Le test natif lit cette ligne et la lance avec **ses seuls arguments**, en remplaçant uniquement ses chemins fictifs.

Un superviseur Python **extérieur au processus WordPress** capture stdout et stderr bruts en mémoire, attend la fin de PHP et les deux EOF (callbacks de shutdown compris), et ne conserve jamais ces flux. Seuls le succès exact et les refus de listes fermées peuvent sortir. Tout octet inattendu, y compris une écriture directe STDOUT/STDERR, ou un arrêt 0 sans résultat complet est un refus. Les rapports sont d'abord privés dans un répertoire jetable 0700, puis contrôlés : noms exacts, fichiers ordinaires sans lien, JSON sans clés dupliquées, schéma/clefs/types/listes fermés, définitions fixes, seuils et cohérence des comptes, empreinte de l'audit et Markdown identique à la projection du JSON. La sortie finale n'est publiée qu'après ces contrôles ; en échec le répertoire jetable entier est supprimé. Un succès PHP seul n'est jamais une preuve. Le tampon interne reste une défense supplémentaire, pas la frontière de confidentialité.

Confinement A-12 et runtime A-11 inchangés : compte SQL SELECT, transaction READ ONLY, garde SQL native avant bootstrap, fichiers source non inscriptibles par Landlock, blocage HTTP/mail/cron/commandes. Pas d'exécution du `wp-config.php`. Fichiers cache/pare-feu et liens symboliques refusés ; l'opérateur les examine sur sa copie selon `a11/README.md`, jamais sur la source réelle. PHP brut refuse l'absence du lanceur.

## Bases et limites

Chaque chiffre porte sa définition dans les deux rapports. Par produit/variation : un abonnement au plus une fois, même en cas de lignes répétées ; les quantités ne multiplient pas le compte. L'état, la périodicité et le total sont ceux de l'abonnement, pas du catalogue. Un rythme annuel désigne ici `1 year` ou `12 month`, sans conversion de semaines/jours et sans interpréter la durée d'engagement. Les comptes par produit peuvent se recouper. Pour plusieurs produits, **le total entier de l'abonnement est compté dans chacun des groupes**, sans répartition inventée ; les lignes de frais/port sont comptées même gratuites. Pas de reconstitution d'un prix historique de ligne.

Montants en chaînes décimales exactes, pas de flottant : normalisation des zéros, sans arrondi ni conversion, valeur visible si au moins cinq abonnements partagent le couple devise/montant **dans le même groupe produit/variation**. Les autres montants n'ont qu'un effectif cumulé. Deux devises ne sont jamais regroupées. Décimales non représentables (18 chiffres entiers, 12 décimales maximum), devise hors forme technique trois majuscules ou rythme non standard : refus fermé, aucune donnée source.

Pays de livraison uniquement, sans repli sur la facturation ni le compte : code de la liste ISO fermée, seuil cinq **global tous produits** ; autres pays avec un effectif et le sous-compte avec port, jamais les codes rares. Pays vide/inconnu séparé sans valeur. `product=0` signale seulement une référence produit absente ; `variation=0` aucune variation. Les abonnements sans ligne produit restent dans les comptes globaux/pays, pas dans un groupe produit inventé.

Un seul magasin natif faisant autorité, classique ou HPOS, jamais les deux ajoutés. Lecture exhaustive en mémoire proportionnelle au nombre d'abonnements vivants ; gros volumes non qualifiés. Le niveau de preuve est le banc synthétique WordPress/Woo/WCS/Memberships compatible d'A-02, pas Imagine 6.9.1 ni le site réel.

## Rejeu

Depuis le dépôt Windows, sans PHP hôte :

```text
C:/Python314/python.exe -B wp/tests/a20/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a20-rejeu-neuf
C:/Python314/python.exe -B wp/tests/a20/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a20-matrice-neuve
C:/Python314/python.exe -B -m unittest discover -s wp/tests/a20 -p test_*.py -v
C:/Python314/python.exe -B wp/tests/a20/verify.py production/A-20/preuves/final
```

Le runner n'accepte ni site ni archive, crée et détruit son conteneur exact sans port/montage/réseau, relit son absence et les empreintes de toutes les tables/fichiers. La bibliothèque PHP pure se copie dans le runner T-02 sans WordPress, écriture, extension ni base ; pas de test PHPUnit parallèle. Le parent seul prépare l'image finale puis joue T-01 global et dépose PRET. Ce candidat ne prétend pas ces gates acquises.
