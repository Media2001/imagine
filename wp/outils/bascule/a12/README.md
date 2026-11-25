# A-12 — inventaire de structure, lecture seule

**Livraison partielle, pas prête au titre du brief complet.** Les comptes stockés sont qualifiés, mais un inventaire statique ne prouve pas tous les types/taxonomies effectivement enregistrés. `registry.runtime_verified=false` et `A12_OK_PARTIAL_REGISTRY` l'indiquent jusque dans la sortie. Aucun `PRET` n'est déposé.

## Commande opérateur (non exécutée sur Imagine)

Après autorisation sur une copie vérifiée, dans son conteneur PHP 8.2+ avec `pdo_mysql`, disposition `wp-content` standard :

```text
php /depot/wp/outils/bascule/a12/inventorier-contenus --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/contenus-date
```

Le parent `/hors-web` existe déjà ; le répertoire final n'existe pas. Il est frère du répertoire de l'audit A-02, hors site **et hors dépôt**. Sorties : `contenus.json`, `contenus.md` ; répertoire 0700, fichiers 0600. Une sortie existante est refusée. Le stockage classique/HPOS doit correspondre à celui du rapport A-02, dont le SHA-256 est conservé ; cela ne garantit pas à lui seul que deux photographies concernent le même site ou la même date.

L'outil réutilise **sans modification** la tokenisation de configuration et les identifiants sûrs d'`audit`. Il ne charge ni `wp-config.php`, ni WordPress, ni thème/extension. PDO : transaction `READ ONLY`, requêtes applicatives exclusivement `SELECT`, rollback final. Aucun HTTP, tâche, envoi ou transformation. Erreurs fermées, sans SQL, valeur ou trace.

## Lecture du rapport

- Types présents en base et candidats déclarés littéralement dans les sources actives, y compris ceux sans contenu ; fichiers déclarants relatifs au site, classés cœur/thème/extension/MU. **Un candidat n'est pas un enregistrement runtime confirmé.** Les sources illisibles ou liens symboliques sont refusés ; les appels dynamiques sont comptés, sans en exporter les arguments.
- Pour chaque type/taxonomie : contenus distincts par état, tous états inclus ; premières/dernières dates UTC des seuls contenus actuellement `publish`. Ce n'est pas un historique de publication des contenus désormais privés ou supprimés.
- Taxonomies : nombre de termes, vingt premiers par nombre réel de contenus reliés distincts, tous états ; noms des rubriques autorisés par le brief. Ex æquo : nom binaire puis identifiant interne non exporté. Ce compte n'est pas le cache natif `term_taxonomy.count`, qui peut suivre une politique de publication différente.
- Métadonnées : **toutes** les clés postmeta par type, internes comprises, sans troncature ; nombre de contenus porteurs distincts, pas nombre de lignes. Aucune valeur de champ, titre, texte, auteur ou donnée client dans les sorties.
- Pièces jointes : nombre/poids des fichiers locaux originaux par MIME enregistré, PDF, parents nuls/inexistants. Un parent nul ne prouve pas qu'un média n'est utilisé nulle part. Les miniatures ne sont pas additionnées. Fichier absent : compté séparément, jamais poids inventé ; chemin externe, traversée ou symlink : refus. Les chemins et noms de médias ne sortent pas.
- Liaisons : clés reconnaissables contenant `product`, `produit`, `article`, `numero`, `issue`, distinguées par casse. Références scalaires canoniques exactes entre contenu et produit/variation, dans les deux sens, dédoublonnées par paire et contenu. Les données sérialisées/JSON ne sont pas interprétées ; leur nombre de lignes non scalaires est signalé. Les clés candidates à zéro ne sont pas une preuve de liaison. Aucun rattachement n'est choisi ou corrigé.

## Limites bloquantes

Les registres natifs `get_post_types()` / `get_taxonomies()` consultent des objets construits à l'exécution. Les appels `register_*` peuvent être dynamiques, conditionnels, filtrés ou non appelés. Exécuter le bootstrap du site contredirait la contrainte de lecture seule robuste conservée depuis A-02. Le banc démontre les deux écarts : `a12_dynamic` réellement enregistré mais absent des candidats, `a12_never` candidat littéral non enregistré. Ni l'un ni l'autre n'est maquillé en résultat exact. Une stratégie de collecte du registre runtime doit être qualifiée séparément avant `PRET`.

Site simple, configuration DB littérale, tables InnoDB et arborescence standard seulement. Sources inspectées : cœur `post.php`/`taxonomy.php`, répertoires des extensions actives, MU de premier niveau et thèmes parent/enfant ; `vendor`, tests et fixtures exclus. Les MU chargeant des sous-modules, fabriques, appels dynamiques ou attributs produits ne donnent pas un registre exhaustif. Les contenus éditoriaux restent dans `posts/postmeta` avec HPOS ; l'outil ne lit pas les coordonnées de commande.

La préparation de l'image partagée (`wp/tests/preparer-image.ps1`) est réservée au parent : elle n'a pas été lancée ici. Le banc dédié réutilise les images déjà présentes, sans reconstruire de tag partagé. La réussite de cette suite bornée n'est pas un rejeu global T01.

## Rejeu dédié

Voir `wp/tests/a12/README.md`. Les preuves synthétiques finales sont dans `production/A-12/preuves/final/` ; aucun rapport issu du réel ne doit être ajouté au dépôt. Les références officielles et leur contrôle HTTP public sont dans `production/A-12/sources-officielles.json`.
