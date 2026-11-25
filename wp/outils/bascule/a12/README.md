# A-12 — inventaire de structure, lecture seule

Collecteur natif : `registry.runtime_verified=true`. Il réutilise **sans modification** `a11/Runtime.php` et `a11/ReadOnlyDb.php`, ainsi que le parseur de configuration A-02. Le registre vient des objets WordPress réellement enregistrés après `wp_loaded`, pas d'une analyse statique des sources.

## Commande opérateur (non exécutée sur Imagine)

Après autorisation sur une copie vérifiée, dans un conteneur Linux déconnecté (`--network=none`, capacités supprimées, aucun montage hôte sensible), PHP 8.2+ avec `mysqli`, Python 3 et noyau Landlock ABI >= 3. Base locale par socket Unix, compte SQL SELECT seulement, aucun cache externe/drop-in. Disposition `wp-content` standard :

```text
python3 /depot/wp/outils/bascule/a12/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/contenus-date
```

Le parent `/hors-web` existe déjà ; le répertoire final n'existe pas. Il est frère du répertoire de l'audit A-02, hors site **et hors dépôt**. Sorties : `contenus.json`, `contenus.md` ; répertoire 0700, fichiers 0600. Une sortie existante est refusée. Le stockage classique/HPOS doit correspondre à celui du rapport A-02, dont le SHA-256 est conservé ; cela ne garantit pas à lui seul que deux photographies concernent le même site ou la même date.

Le lanceur `confine.py` est obligatoire : refus hors Linux déconnecté ou sans Landlock ; restriction noyau des mutations de fichiers au seul parent des rapports, héritée par PHP et son code tiers ; fonctions mail/processus directes désactivées. Ne pas exposer ce parent à un service web et y conserver seulement les rapports de cette opération. Le site reste hors de cette zone inscriptible. Le marqueur d'environnement évite un lancement PHP brut accidentel, ce n'est pas une preuve de sécurité ni un substitut à Landlock. Ne jamais le fabriquer manuellement.

`wp-config.php` n'est jamais exécuté. A-11 injecte son unique connexion native `wpdb` **avant** `wp-settings.php`, déjà en REPEATABLE READ / READ ONLY, et refuse les écritures ainsi que COMMIT/changement de transaction. Ce même objet sert au bootstrap, aux métadonnées, aux pièces jointes et à toutes les agrégations ; aucune seconde connexion PDO. Les hooks natifs interdisent HTTP, mail et modifications de cron avant le chargement des extensions ; le runner Action Scheduler est suspendu. Les compteurs `native_guards` sont des tentatives **bloquées**, pas des envois. Les sorties PHP ordinaires du bootstrap sont absorbées. Erreurs fermées sans SQL, valeur ni trace. Le réseau coupé et le confinement noyau restent nécessaires : des hooks ne neutralisent pas du PHP tiers arbitraire.

## Lecture du rapport

- Tous les objets des registres natifs `get_post_types()` / `get_taxonomies()`, y compris ceux vides ou dynamiques. Attribution par la pile des **appels réellement exécutés** `register_post_type` / `register_taxonomy` ; fichier relatif lisible, catégorie cœur/thème/extension/MU. On retient le dernier objet encore enregistré ; appels conditionnels non exécutés et objets désenregistrés exclus. Injection hors API ou fichier illisible : déclarant `unknown`, jamais inventé. Les objets seulement stockés sont séparément marqués `stored_only_unregistered`, sans les compter dans les totaux du registre.
- Pour chaque type/taxonomie : contenus distincts par état, tous états inclus ; premières/dernières dates UTC des seuls contenus actuellement `publish`. Ce n'est pas un historique de publication des contenus désormais privés ou supprimés.
- Taxonomies : nombre de termes, vingt premiers par nombre réel de contenus reliés distincts, tous états ; noms des rubriques autorisés par le brief. Ex æquo : nom binaire puis identifiant interne non exporté. Ce compte n'est pas le cache natif `term_taxonomy.count`, qui peut suivre une politique de publication différente.
- Métadonnées : **toutes** les clés postmeta par type, internes comprises, sans troncature ; nombre de contenus porteurs distincts, pas nombre de lignes. Aucune valeur de champ, titre, texte, auteur ou donnée client dans les sorties.
- Pièces jointes : nombre/poids des fichiers locaux originaux par MIME enregistré, PDF, parents nuls/inexistants. Un parent nul ne prouve pas qu'un média n'est utilisé nulle part. Les miniatures ne sont pas additionnées. Fichier absent : compté séparément, jamais poids inventé ; chemin externe, traversée ou symlink : refus. Les chemins et noms de médias ne sortent pas.
- Liaisons : clés reconnaissables contenant `product`, `produit`, `article`, `numero`, `issue`, distinguées par casse. Références scalaires canoniques exactes entre contenu et produit/variation, dans les deux sens, dédoublonnées par paire et contenu. Les données sérialisées/JSON ne sont pas interprétées ; leur nombre de lignes non scalaires est signalé. Les clés candidates à zéro ne sont pas une preuve de liaison. Aucun rattachement n'est choisi ou corrigé.

## Périmètre qualifié

Photographie à la fin du bootstrap natif CLI, sans requête front/admin/REST ni identité utilisateur. Elle n'invente pas les objets qu'un code n'enregistrerait que dans un autre contexte. Le banc vérifie l'égalité exacte avec son oracle natif : `a12_dynamic` inclus, `a12_never` exclu, taxonomie dynamique incluse, appels non exécutés et objets retirés exclus. Les fichiers déclarants cœur, WooCommerce, MU et thème sont contrôlés exactement.

Site simple, configuration DB littérale, tables InnoDB, arborescence standard seulement. Refus des symlinks du site, drop-ins et constantes de disposition/URL non qualifiées par A-11, plus `WPMU_PLUGIN_DIR` et `UPLOADS`. Aucun code tiers modifié. Les contenus éditoriaux restent dans `posts/postmeta` avec HPOS ; l'outil ne lit pas les coordonnées de commande. Les empreintes de toutes les tables et des fichiers sont comparées avant/après sur les fixtures, y compris options/cron et Action Scheduler. Un futur site réel demande toujours son GO et sa copie vérifiée ; ce lot ne les autorise pas.

La préparation de l'image partagée (`wp/tests/preparer-image.ps1`) et les deux lignes du mode d'emploi commun relèvent du parent. Le banc dédié réutilise les images présentes sans modifier un tag partagé. Cette suite proportionnée n'est pas un rejeu global T01.

## Rejeu dédié

Voir `wp/tests/a12/README.md`. Les preuves synthétiques finales sont dans `production/A-12/preuves/final/` ; aucun rapport issu du réel ne doit être ajouté au dépôt. Les références officielles et leur contrôle HTTP public sont dans `production/A-12/sources-officielles.json`.
