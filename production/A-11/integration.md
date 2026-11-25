# Intégration A-11 — réservée au parent

Le chemin transmis `C:/Users/Ced/imagine voie1` n'existe pas sur cette machine. Le dépôt trouvé et utilisé est **`C:/Users/Ced/imagine`**. Aucun verrou n'a été touché, aucune opération Git, aucun site, aucune donnée réelle. Aucun fichier A-02/A-09/A-10, script de tests partagé ni README d'audit n'a été modifié par A11.

## Les deux lignes à ajouter au mode d'emploi de l'audit

Après l'audit, lancer `php wp/outils/bascule/a11/inventorier-adresses --wp-path=/copie-verifiee/site --audit=/rapports/audit-001/audit.json --output=/rapports/adresses-001` dans la même copie confinée, avec un dossier de sortie neuf, frère du rapport d'audit et hors racine web/dépôt.
Le fichier `adresses.csv` (UTF-8, séparateur `;`) donne la colonne `ancienne` selon A-09; `resume.md` donne les nombres, les exclus et les bases de permaliens, sans client ni décision de redirection; voir `a11/README.md` pour les gardes et le rejeu dédié.

## Réception intégrée

Les deux lignes ci-dessus ont été relues dans le README partagé, à leurs octets exacts après l'ajout A-10 et avant les deux lignes A-12. Le parent a réellement exécuté `wp/tests/preparer-image.ps1`, code **0**, le **26 novembre 2026 à 00:45:29 CET** ; reçu et journal `preparer-image-parent.json` / `.log`, image T01 vérifiée. Ces formalités sont acquises et ne restent plus à faire.

Rejeu natif frais sur le baseline intégré : **13 assertions unitaires, 284 natives, 7 runner**, toutes PASS ; paquet courant unique `preuves/f77a1fcd8945`. Le vérificateur original conserve les comparaisons strictes `protected-before == protected-after == sources courantes` ; aucun README ni autre drift n'est ignoré. L'ancien paquet `bb086d5bb67e` et l'ancien manifeste sont conservés byte à byte au scratch `a10-a13-reception/historical/A-11/`, pas modifiés pour les rendre verts.

Vérification ciblée : `python -B wp/tests/a11/verifier.py production/A-11/preuves/f77a1fcd8945`. Vérification consolidée des manifestes/PRET : `python -B production/A-10/verifier-reception.py`. Un nouveau rejeu reste disponible via `python wp/tests/a11/run.py` (scratch) ; ne pas multiplier les paquets finaux au dépôt.

## Décisions prises à défaut

- Garder les contextes d'une URL commune dans une seule ligne plutôt que doubler la boutique/page/archive. Comptes par nature non additifs.
- Dates d'archives/termes vides : WordPress n'a pas de date native propre à ces objets. État `public`, versus état stocké `publish`/`inherit` des contenus.
- Archive des articles : API native spéciale de `post`, même si `has_archive` est faux. Auteurs : types publics hors pages/pièces jointes, jamais inventaire général des comptes.
- Les pages de pièces jointes désactivées et les pièces jointes d'un parent protégé sont comptées et non listées; parent manquant traité par l'héritage natif.
- Une URL filtrée native externe ou incompatible A-09 fait refuser le paquet, pas inventer une autre convention.
- Bootstrap natif nécessaire pour respecter les filtres et enregistrements réels; injection préalable de `wpdb` lecture seule, blocage HTTP/mail/cron et refus des caches externes, configuration non standard et liens symboliques. Le confinement système est obligatoire pour les effets arbitraires de code tiers; aucun accès réel n'est autorisé par ce lot.
