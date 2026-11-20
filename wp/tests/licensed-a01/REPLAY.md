# Rejeu ciblé A-01 — vrais paquets commerciaux, données fictives seulement

Depuis `C:/Users/Ced/imagine`, avec Python et le Docker/WSL Ubuntu déjà installés :

```sh
python wp/tests/licensed-a01/run.py
```

Cette commande **n'importe jamais une archive opérateur** et ne lit aucun vrai site. Elle exige l'image locale exacte de `compatible.lock.json` et les deux ZIP autorisés de la bibliothèque opérateur WSL, vérifiés par empreinte à l'extraction. Elle ne télécharge rien, ne connecte aucun compte/licence et ne lance aucun serveur. Ne pas ajouter un chemin d'archive ou de site en argument.

Le banc vérifie que les onze sujets correspondent toujours au reçu non commercial `f36c72f4d187`, copie uniquement les sources nommées et les paquets autorisés vers un conteneur neuf `network=none`, sans montage/volume/port, lance les deux variantes puis copie le résultat exact avant suppression ciblée et vérification d'absence. Les activations de Memberships et Subscriptions sont indépendantes. Chaque lancement crée `evidence/<run_id>/` ; aucun reçu existant n'est écrasé. Sortie 0 seulement si les contrôles exécutés ne contiennent ni FAIL ni BLOCKED ; une sortie 0 n'est pas une autorisation d'import opérateur.

## Préparation publique séparée

L'image compatible a déjà été préparée. Si elle manque, **ne pas remplacer le runtime par une installation en réseau**. Après autorisation explicite des téléchargements publics, la préparation séparée est :

```sh
python wp/tests/licensed-a01/prepare.py
```

Elle télécharge uniquement les deux versions publiques épinglées de WordPress/WooCommerce, valide les SHA-256 et tailles inscrits dans le script, vérifie l'identité de l'image de base locale puis construit sans réseau RUN et sans démarrer de site. Les ZIP publics et le contexte de construction restent dans le scratch Hermes, hors dépôt. `compatible.lock.json` consigne l'image exacte et les sources publiques ; aucune extension commerciale n'entre dans cette image. Cette préparation ne modifie pas `wp/tests/staging-e2e/dependencies.lock.json` ni la baseline. Le runtime ne fait jamais de pull.

## Interprétation des résultats

Reçu de livraison : `evidence/e49f54c5e931/result.json` — sortie 0, 104 PASS et quatre observations (pas 104 tests métier indépendants). `journal.json` prouve l'isolation avant/après et la suppression ; `driver-source.json` et `subject-source.json` permettent de relier les fichiers exécutés aux preuves. `packages.tsv` est l'inventaire système hérité de l'image publique de base ; les versions applicatives remplacées sont relues par les API et consignées dans les checks `actual_versions`, pas déduites de cet inventaire Debian.

Les adhésions sont autonomes ; le contrôle est API + shortcode, pas HTTP/thème/cache/REST. Le témoin positif Action Scheduler crée réellement une commande de renouvellement **manuel sans paiement** sur le staging fictif puis son SQL est restauré dans le même conteneur. Aucun débit ni passerelle réelle ne sont exercés. Sous verrou, le hook ne s'exécute pas et AS marque l'essai forcé failed ; les journaux Woo produits par les manipulations sont observés puis purgés explicitement par le vrai sujet Files avant le dernier vérificateur. La décision `garder` sur `wp_wc_email_unsubscribes` n'existe que dans le contexte inventé, jamais comme choix de production.

La copie/restauration des fichiers d'un import réel et l'intégration opérateur restent non qualifiées. `operator_import_ready=false`, `files_import_fidelity_tested=false`, aucun `PRET`, aucun déploiement.
