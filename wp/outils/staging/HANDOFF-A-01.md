# Contrat A-01 reprise (handoff intégration / E2E)

- `Engine(Store, context, prefix, array $decisions = [])` ; aussi `context['table_decisions']`. Command bridge accepte `table_decisions`. Fichier JSON contrôlé par Ced, map nom exact de table -> `{ "action": "garder" }`, `{ "action": "vider" }` ou `{ "action": "anonymiser", "columns": ["email", "phone"] }`. Aucun choix de Ced prérempli. Passer le même fichier aux trois phases.
- Inconnues : tables/colonnes/CPT gardés. Table inconnue avec colonne personnelle sans décision => `TABLE_PERSONNELLE_A_TRANCHER` ; même une table vide attend la décision. Le rapport inclut `unknown_tables` (`name`, `columns`, `rows`, `personal_columns`, `decision`), `unknown_columns`, `unknown_post_types`, `disabled_plugins`, `active_plugins`, `warnings`, sans valeurs.
- Configuration négative plugins : `policy.php`. Options conservées, nettoyage ciblé, passerelles test sans clé, plugins formulaire/SEO/ACF conservés.
- Cinq blocages + table personnelle : emails hors example.org dans comptes/commandes/abonnements, motifs connus de service/identifiants paiement partout, mail runtime non coupé, Subscriptions présent non staging. Autres contrôles data => warnings. Les guards cible/offline/fichiers et les barrières externes worker restent obligatoires ; Engine ne produit aucune autorisation réseau/web.
- Probe : `subscriptions_present` bool, `subscriptions_staging` bool ou null quand absent. Ne jamais exiger une licence sur les jetables. `mail_blocked` nécessite vrai wp_mail exécuté ; pas un booléen simulé pour intégration.
- MU : avant vérification sorties toutes interdites. Le worker pourra définir `IMAGINE_STAGING_VERIFIED === true` UNIQUEMENT depuis son état persistant vérifié. Alors `WP_ACCESSIBLE_HOSTS='*.wordpress.org,*.woocommerce.com'` et filtre HTTP identique ; aucune ouverture avant, aucun autre hôte. Pare-feu système reste responsabilité worker (WP ne filtre ni sockets ni SDK).
- Aucun fichier de l'intégration/E2E ni rapport global/PRET modifié par ce worker data.

En cours : tests synthétiques et finalisation MU / PDO / filesystem. Lire README final pour résultats et limites.
