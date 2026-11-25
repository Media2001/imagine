# A-05 — Exécuter un plan de nettoyage

Outil de bascule, pas une décision de retrait. Linux, Python 3.11+, PHP 8.2+, PDO MySQL et WP-CLI déjà présents dans l'environnement cible. Les essais de ce lot se font uniquement dans un conteneur jetable hors réseau. Aucun site réel n'a été utilisé. Les bibliothèques A-03/A-04 et les gardes de staging doivent rester à leur emplacement relatif dans `wp/outils/`.

## Défaut : garder

- Une ressource absente du plan reste en place. Aucune liste d'extensions ou de tables retirées d'office.
- `plugins` : fichier principal relatif à `wp-content/plugins`, `action` = `garder`, `desactiver` ou `retirer`, et `uninstall` booléen obligatoire. Le diagnostic ne donne que les dossiers : un nom de dossier seul est donc accepté **uniquement avec `garder`**. Pour agir, remplacer ce nom par le fichier principal relevé lors de l'audit ; ne pas le deviner.
- `retirer` désactive silencieusement avec l'API native, puis supprime seulement le fichier d'une extension autonome ou son dossier. `uninstall: false` interdit l'appel à sa routine de désinstallation. `true` appelle explicitement l'API native `uninstall_plugin()` avant la suppression des fichiers : sa routine tierce peut alors effacer ses données. Ses effets ne sont pas prédictibles en octets par le mode à blanc ; auditer cette routine avant de l'autoriser. Ce n'est pas un bac à sable pour du PHP tiers malveillant.
- `tables` et `options` : règles `{ "match": "exact"|"prefix", "name": "nom", "action": "garder"|"supprimer" }`. Préfixes littéraux, pas de SQL, joker, expression régulière ou remplacement automatique du préfixe du site.
- `cron` : mêmes champs, mais `match: "exact"` uniquement, le nom est un crochet WP-Cron. Avant l'exécution, un crochet encore enregistré par du code chargé est refusé : il n'est pas orphelin. Action Scheduler n'est jamais vidé ni exécuté ; les tâches de paiement restent hors de ce nettoyage. J'ai compris « préfixe ou crochet » comme options par préfixe, WP-Cron par crochet.
- `uploads` : chemins relatifs exacts de dossiers dans le `wp-content/uploads` canonique. Pas le dossier racine, pas de fichier isolé, pas de lien symbolique, même dans un sous-dossier. Un `garder` interdit toute suppression recouvrante : son parent comme ses descendants, dans les deux ordres du plan (`A05_UPLOAD_KEEP_CONFLICT:<cible>`).
- Une règle `garder` l'emporte sur une suppression recouvrante ; c'est aussi vrai d'un dossier d'extension gardé face à son fichier principal.

`plan-imagine.exemple.json` reprend seulement les noms de `docs/ecarts.md` des 24–25 novembre : tout est à `garder`, désinstallation toujours fausse. `fsmpt_email_logs` est reproduit **tel qu'écrit dans le diagnostic**, sans corriger l'orthographe. Les préfixes effectifs, fichiers principaux, options et crochets inconnus ne sont pas inventés. Ce formulaire n'est pas le plan de nettoyage du vrai site.

## Tables d'extensions gardées : défaut prudent

WordPress n'a pas de registre générique exhaustif des tables possédées par chaque extension. Aucune déduction fiable ne peut être faite du seul nom d'un dossier. Dès qu'une règle sélectionne une table à supprimer, `table_owners` doit contenir l'inventaire **audité** de toutes les extensions installées dont les fichiers restent, y compris celles non nommées ou simplement désactivées, des MU-plugins, et du thème actif.

Exemple de forme, noms fictifs :

```json
{
  "fictive/entree.php": ["wp_fictive_"],
  "autre/entree.php": [],
  "mu:garde.php": [],
  "theme:theme-fictif": ["wp_theme_fictif_"]
}
```

Les valeurs sont uniquement des noms/préfixes de tables. `[]` signifie **audit réalisé, aucune table propre**, pas « inconnu ». Inventaire incomplet : refus avec le nom manquant. Une table correspondant à un propriétaire gardé est refusée. Les tables du cœur, de WooCommerce et d'Action Scheduler sont protégées indépendamment de cet inventaire. L'extension de maintenance A-04, comparée octet par octet à son modèle, ne possède pas de table et ne demande pas de nouvelle entrée à la reprise. Le formulaire Imagine laisse cet inventaire vide tant qu'aucune suppression n'a été décidée.

Sont refusés également : retrait ou désactivation d'une dépendance d'une extension gardée (en-têtes lus sans chargement, avec les préfixes de commentaire WordPress `[ \t/*#@]*`), WooCommerce/Subscriptions/Memberships, passerelles reconnaissables par leur identité ou code de passerelle, chemin d'extension traversant ou lié, dossier partagé contenant un autre fichier principal, options et crochets commerciaux protégés. Le conflit de dossier nomme le voisin (`A05_SHARED_PLUGIN_DIRECTORY:<voisin>`), qu'il soit gardé ou à désactiver, actif ou déjà inactif. Défaut prudent : même plusieurs `retirer` dans ce dossier sont refusés, pour ne jamais supprimer les fichiers avant leurs désactivations/désinstallations explicites. Il n'existe aucune action de suppression de thème ; tenter d'atteindre le thème actif par `../themes/...` est rejeté avec le chemin fautif. Les noms de fichiers commerciaux usuels sont protégés même si l'extension est inactive.

## Préalables hérités d'A-04

L'outil importe **sans modifier** `a04/update.py` : validation de chemins, JSON, empreintes, sauvegarde récente, maintenance, écritures atomiques et rafraîchissement de maintenance. Les processus WP-CLI chargent le bootstrap et le contrôle de sûreté natif d'A-04, en mode `guard` seulement : aucune migration et aucune file globale ne tournent.

- Sauvegarde locale de la base **et** des fichiers, non vide, datée de moins de six heures, hors du site sur son chemin résolu, sans parent symbolique, empreintes exactes. Format du manifeste identique à A-04 (`site`, `created_at`, `database` et `files`, chacun avec `path` et `sha256`). L'outil ne fabrique pas ces sauvegardes.
- Maintenance native déjà active. L'extension persistante A-04 est conservée ; une reprise peut rafraîchir `.maintenance` sous les deux verrous seulement si cette extension est intacte et le checkpoint lié au même site, plan et `wp-config.php`.
- Marqueur de staging vérifié et MU de sûreté exact ; drop-ins DB/cache refusés. La production nécessite un **GO A-05 distinct**, jamais un GO historique A-04. Même forme de GO A-04, mais `task: "A-05-nettoyage"`, site et SHA-256 du plan exacts, auteur Ced, `go: true`, échéance future au plus six heures. Ce mécanisme ne constitue aucun GO réel.
- Réutiliser le verrou site `.imagine-a04-bascule.lock` créé par A-04. S'il manque, le faire créer explicitement lors de la préparation opérateur, **avant** la photographie du mode à blanc. A-05 refuse de le créer en douce : cela changerait l'empreinte des fichiers. Le verrou du site est partagé avec A-04 ; le verrou du checkpoint est distinct. Les enfants natifs héritent des descripteurs `flock`.
- Configuration littérale conventionnelle et site unique. Multisite et racines personnalisées `UPLOADS`, `WP_CONTENT_DIR`, `WP_PLUGIN_DIR`, `WPMU_PLUGIN_DIR`, ou option `upload_path` non conventionnelle : refus prudent, pas d'adaptation implicite. Un filtre PHP arbitraire redéfinissant les chemins demanderait une qualification spécifique.

Les fichiers de travail, plans d'exploitation, sauvegardes et éventuel GO restent hors du site. Ne pas les déposer dans les médias ni dans le dépôt s'ils contiennent autre chose que des noms et des données fictives.

## Commandes

Ces chemins Linux sont des **exemples fictifs**, pas des chemins du site Imagine :

```bash
python3 -B wp/outils/bascule/nettoyer --wp-path=/srv/fiction/site --plan=/srv/fiction/plan.json --backup=/srv/fiction/sauvegarde.json --state=/srv/fiction/etat-a05 --dry-run > /srv/fiction/nettoyage-a-blanc.json
python3 -B wp/outils/bascule/nettoyer --wp-path=/srv/fiction/site --plan=/srv/fiction/plan.json --backup=/srv/fiction/sauvegarde.json --state=/srv/fiction/etat-a05
```

Même commande et mêmes arguments pour reprendre. Codes : `0` terminé ou aucun effet ; `1` refus/erreur avec code et nom concernés ; `75` arrêt demandé à un checkpoint. `--stop-after=N` arrête après la N-ième opération durable ; `--pause` y attend en gardant les verrous (utilisé par l'essai de SIGKILL). Ne jamais supprimer un verrou ou modifier le journal pour forcer une reprise.

### À blanc

Lecture SQL seule, sans charger WordPress, ses extensions ou leur code de désinstallation. Aucune création de fichier dans le site, aucun checkpoint, aucune écriture SQL. Sortie JSON : noms des opérations, lignes exactes, octets des valeurs d'options, octets sérialisés et nombre d'événements cron, octets/fichiers des dossiers. Pour les tables, les octets désignent l'espace alloué données + index fourni par MariaDB, pas une prévision de réduction du fichier physique. Les effets propres à une routine tierce de désinstallation sont explicitement inconnus.

Le champ JSON `information` liste les noms planifiés absents sous la forme `{ "kind": "plugin"|"table"|"option"|"cron"|"upload", "name": "nom", "status": "nommé, absent" }`, y compris les préfixes sans correspondance et les noms à garder. Un dossier de plugin gardé déjà présent n'est pas marqué absent. Ces lignes ne sont pas des opérations : aucune désinstallation, création de checkpoint ni écriture n'en découle.

La vérification dynamique des crochets réellement orphelins et du runtime A-04 précède toute mutation du passage réel. Le mode à blanc n'exécute pas du PHP tiers pour tenter de prédire ces effets. Le plan est entièrement validé avant toute suppression.

### Passage réel et reprise

L'inventaire exact des cibles est figé dans `etat.json`, lié aux empreintes du plan et de la configuration. Une famille ne s'élargit pas au milieu d'une reprise. `journal.json` et `journal.txt` donnent dates, noms et phases `start`, `done`, `interruption_requested`, `complete`. Une phase commencée sans `done` indique un passage interrompu/échoué. La maintenance n'est jamais retirée automatiquement.

La désactivation native est silencieuse ; ses écritures SQL sont limitées à `active_plugins`, pour ne pas effacer les transients de Woo/Jetpack par les hooks de modification de cette option. Options et WP-Cron orphelins sont retirés par accès SQL borné aux noms figés, avec relecture ; WP-Cron est réécrit par comparaison atomique de sa valeur antérieure. Cela évite d'exécuter une file ou des hooks de suppression. Les drop-ins de cache étant refusés et les processus terminés entre opérations, aucun cache persistant accepté n'est laissé divergent.

Un checkpoint déjà terminé n'écrit plus dans le site ou la base. Un nouveau checkpoint sur un site déjà nettoyé rend aussi `A05_NOOP`. Si une nouvelle ressource apparaît dans une famille après la fin, le checkpoint terminé refuse `A05_COMPLETED_DRIFT` : il ne la détruit pas sans un nouveau passage préparé. Les préalables de sauvegarde et de maintenance restent exigés, même pour un second passage.

Une routine tierce de désinstallation peut contenir du DDL et des effets non transactionnels. Si elle a commencé mais que sa fin n'a pas été journalisée, reprise **refusée** par `A05_UNINSTALL_AMBIGUOUS:<extension>`, sans la rejouer aveuglément. Restaurer la sauvegarde puis repartir d'un état propre après vérification opérateur ; ne pas fabriquer un checkpoint « terminé ». C'est une limite volontaire et non un succès simulé.

## Rejouer les preuves

Depuis `C:/Users/Ced/imagine`, Python Windows ne fait que piloter Docker ; tout PHP tourne dans le conteneur jetable :

```bash
python -B wp/tests/a05/run.py
python -B wp/tests/a05/run.py --unit-only
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Le runner A-05 ne démarre aucun ancien site, ne monte aucun dossier hôte, ne télécharge rien, utilise son étiquette propre, copie uniquement ses sources et les dépendances A-03/A-04 en lecture, vérifie l'isolation puis supprime et vérifie l'absence de son seul conteneur exact. Les ZIP de licences déjà autorisés sont lus seulement dans `/home/ced/staging-wp/plugins/`, comme dans A-04 ; aucune archive Imagine n'est ouverte. Aucun appendice du runner commun n'a été nécessaire.

Le banc natif classique et HPOS conserve les photographies A-03 avant/après et sa comparaison **non modifiée**. Si cette comparaison signale une anomalie, elle doit rester visible ; un inventaire de nettoyage ne la requalifie pas. Sur le scénario livré, le comparateur reste identique (code 0) : ses champs ne constituent pas l'inventaire exhaustif des plugins et de WP-Cron. La disparition effective des ressources nommées et l'intégrité des autres sont prouvées séparément par les empreintes/inventaires, pas déduites de ce code 0.

### Standard d'abord — références officielles

Consultées pour choisir les opérations natives :

- WordPress `deactivate_plugins()` : https://developer.wordpress.org/reference/functions/deactivate_plugins/ — mode silencieux et mise à jour de la liste active.
- WordPress `uninstall_plugin()` : https://developer.wordpress.org/reference/functions/uninstall_plugin/ — routine explicitement distincte de la simple désactivation/suppression de fichiers.
- WordPress `wp_unschedule_hook()` : https://developer.wordpress.org/reference/functions/wp_unschedule_hook/ — sémantique de suppression de tous les événements d'un crochet. Le wrapper conserve cette sémantique sans lancer les filtres tiers ni le cron.

Le sur-mesure est le plan explicite, l'inventaire à blanc sans bootstrap, les protections, les accès SQL bornés et la reprise. Ce lot ne décide aucune suppression réelle et ne vaut ni validation visuelle, ni autorisation d'exploitation.
