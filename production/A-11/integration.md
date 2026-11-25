# Intégration A-11 — réservée au parent

Le chemin transmis `C:/Users/Ced/imagine voie1` n'existe pas sur cette machine. Le dépôt trouvé et utilisé est **`C:/Users/Ced/imagine`**. Aucun verrou n'a été touché, aucune opération Git, aucun site, aucune donnée réelle. Aucun fichier A-02/A-09/A-10, script de tests partagé ni README d'audit n'a été modifié par A11.

## Les deux lignes à ajouter au mode d'emploi de l'audit

Après l'audit, lancer `php wp/outils/bascule/a11/inventorier-adresses --wp-path=/copie-verifiee/site --audit=/rapports/audit-001/audit.json --output=/rapports/adresses-001` dans la même copie confinée, avec un dossier de sortie neuf, frère du rapport d'audit et hors racine web/dépôt.
Le fichier `adresses.csv` (UTF-8, séparateur `;`) donne la colonne `ancienne` selon A-09; `resume.md` donne les nombres, les exclus et les bases de permaliens, sans client ni décision de redirection; voir `a11/README.md` pour les gardes et le rejeu dédié.

## Dernier geste réservé au parent

La consigne permanente exige `wp/tests/preparer-image.ps1` après l'ajout d'un paquet de tests. Sa reconstruction m'a été expressément interdite : **elle reste au parent**, ainsi que l'insertion des deux lignes ci-dessus dans le README partagé. Aucun `PRET` n'est déposé tant que cette exigence n'est pas prouvée. Le parent peut déposer `production/A-11/PRET` après son succès et le contrôle du paquet final par `python wp/tests/a11/verifier.py production/A-11/preuves/IDENTIFIANT`.

Le runner dédié `python wp/tests/a11/run.py --final` ne reconstruit rien et n'effectue aucun rejeu global. Les essais intermédiaires sont hors dépôt, dans le scratch Hermes A11; le seul dossier `production/A-11/preuves/` doit contenir le dernier rejeu vert.

## Décisions prises à défaut

- Garder les contextes d'une URL commune dans une seule ligne plutôt que doubler la boutique/page/archive. Comptes par nature non additifs.
- Dates d'archives/termes vides : WordPress n'a pas de date native propre à ces objets. État `public`, versus état stocké `publish`/`inherit` des contenus.
- Archive des articles : API native spéciale de `post`, même si `has_archive` est faux. Auteurs : types publics hors pages/pièces jointes, jamais inventaire général des comptes.
- Les pages de pièces jointes désactivées et les pièces jointes d'un parent protégé sont comptées et non listées; parent manquant traité par l'héritage natif.
- Une URL filtrée native externe ou incompatible A-09 fait refuser le paquet, pas inventer une autre convention.
- Bootstrap natif nécessaire pour respecter les filtres et enregistrements réels; injection préalable de `wpdb` lecture seule, blocage HTTP/mail/cron et refus des caches externes, configuration non standard et liens symboliques. Le confinement système est obligatoire pour les effets arbitraires de code tiers; aucun accès réel n'est autorisé par ce lot.
