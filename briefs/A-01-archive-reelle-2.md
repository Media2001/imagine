# Lot A-01 — Ce que dit le diagnostic de l'archive réelle

**Voie** : 1. **Délai** : une demi-journée. **Passe avant tout le reste, A-04 compris.**

Ced a lancé le diagnostic le 24/11. Le mode `--diagnose` a rempli son rôle : six refus d'un coup, aucune donnée personnelle dans la sortie. Le résultat montre que **la commande n'a jamais été confrontée à la forme d'une vraie archive**. Les archives de test étaient fabriquées à la main ; une vraie ne leur ressemble pas.

## Les constats (chiffres de la sortie de Ced, 49 756 entrées)

**1. `ARCHIVE_PATH_DOT`, 4 fichiers : c'est le format normal.** Extensions `.json`, `.sql`, `.php` et une autre, zone hors `wp-content`. Dans une archive All-in-One WP Migration, les fichiers de la racine (`package.json`, `database.sql`…) portent le préfixe `.`. `archive.py` construit `prefix + '/' + name` et refuse le segment `.`. C'était déjà la cause du refus du 23/11.
→ Conséquence en chaîne : `ARCHIVE_DATABASE_MISSING`, `SOURCE_CORE_METADATA_REFUSED` et `SQL_UNAVAILABLE` ne sont très probablement que le même défaut vu trois fois. **Quatre refus sur six ont une seule cause.**

**2. `ARCHIVE_LIMIT`, 45 376 fichiers sur 49 756.** Les plafonds (`max_bytes` 1 Go, base 128 Mo, `archive.py:84` et `:130`) sont ceux d'un banc d'essai. Le site réel a six ans de médias.

**3. `SECRET_OU_IDENTIFIANT`, 1 444 fichiers, bloquant : des faux positifs.** Des `.jpg`, `.mp3`, `.mp4`, `.woff2`, des PDF, le code de WooCommerce, de Matomo, d'ACF. Chercher des motifs de secret dans des fichiers binaires ou dans le code d'extensions publiques ne signifie rien, et bloquer là-dessus rend la commande inutilisable.

**4. Ce que le diagnostic ne dit pas et qui compte davantage : des données personnelles dans les fichiers.** La sortie montre dans `uploads/` : `wpallexport` (26 CSV, 16 XML, 13 ZIP), `wpallimport`, `memberships_csv_exports`, `memberships_csv_imports`, `wc-logs` (91 journaux), `wpdesk-logs`, `ur-logs`, `woocommerce_uploads` (2 CSV), `matomo`, `wpdm-cache`, et un `.zip` à la racine de `themes/`. Ce sont très probablement des exports d'abonnés et des journaux de commandes. L'anonymisation de la base ne les touche pas.

## À faire

### A. Lire le format réel, et tester sur de vraies archives

- Appuie-toi sur le format tel que l'extension All-in-One WP Migration l'écrit (son code est public) : en-tête, préfixe `.` pour la racine, fin d'archive, contenu de `package.json`. Cite les fichiers source que tu as lus.
- **Les archives de test sont désormais produites par la vraie extension**, exportées depuis un site fictif (`imagine-test-…`), y compris une « grosse » : plusieurs dizaines de milliers de fichiers, plus d'un gigaoctet de médias générés, une base de plus de 128 Mo. Les archives fabriquées à la main ne restent que pour les cas d'attaque.
- Normalise le préfixe `.` (et `./`) à la lecture ; un segment `.` ou `..` **à l'intérieur** d'un chemin reste refusé.

### B. Des plafonds réalistes

Lecture en flux, sans rien charger en mémoire. Plafonds par défaut à l'échelle d'un vrai site (ordre de grandeur : 50 Go, deux millions d'entrées, base de plusieurs gigaoctets), réglables en ligne de commande, et vérification de l'espace disque disponible avant de créer quoi que ce soit. Le diagnostic affiche la taille totale, le nombre d'entrées et la taille de la base.

### C. Secrets : chercher là où il y en a

- Dans les **fichiers** : plus de recherche dans les binaires ni dans le code des extensions et thèmes. Ne regarder que ce qui peut porter un secret propre au site : fichiers de configuration et `.php`/`.json`/`.env`/`.ini` hors des dossiers d'extensions et de thèmes connus, `mu-plugins`, racine de `wp-content`. Résultat en **avertissement à revoir**, pas en refus.
- Dans la **base** : inchangé, c'est là que sont les clés (passerelles, SMTP, Matomo, Wordfence, ManageWP), et la neutralisation les traite.

### D. Les fichiers à données personnelles : ne pas les restaurer

- Une liste d'exclusion par défaut, appliquée à la restauration : `uploads/wpallexport`, `uploads/wpallimport`, `uploads/memberships_csv_exports`, `uploads/memberships_csv_imports`, `uploads/wc-logs`, `uploads/wpdesk-logs`, `uploads/ur-logs`, `uploads/matomo`, `uploads/wpdm-cache`, les journaux et exports d'extensions de même nature que tu identifies, et toute archive (`.zip`, `.sql`, `.wpress`) hors des dossiers de médias datés. Ces fichiers ne sont **ni extraits ni lus**.
- Dans `uploads/woocommerce_uploads` et `uploads/simple-file-list` : les PDF et images sont gardés (ce sont vraisemblablement les numéros vendus, nécessaires aux tests) ; les `.csv`, `.html`, journaux et fichiers sans extension sont exclus.
- Tout dossier de premier niveau de `uploads/` qui n'est ni une année, ni dans la liste « gardé », ni dans la liste « exclu » → **refus avec son nom**, pour décision. Fermé par défaut.
- Le rapport liste ce qui a été exclu : zone, nombre, taille.

### E. Un diagnostic lisible

La sortie faisait 2 200 lignes. Par défaut : un résumé d'un écran (par règle : nombre, bloquant ou non, les cinq premières zones), plus l'inventaire utile à l'audit : extensions et thèmes présents (noms de dossiers), dossiers de premier niveau de `uploads/` avec nombre et taille. Le détail complet sur option.

## Ce que tu ne fais pas

Tu n'ouvres pas l'archive d'Imagine, tu ne lances ni diagnostic ni import dessus. Ced relancera le diagnostic.

## Livrables

Code, tests sur archives produites par la vraie extension, commande de diagnostic en tête de `production/A-01/notes.md`, rapport court, `PRET`. Preuves proportionnées.
