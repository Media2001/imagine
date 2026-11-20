# Tests de neutralisation et anonymisation

Aucun serveur ni compte réel. Les fixtures sont construites en PHP : trente utilisateurs, trente commandes classiques/abonnements, trente commandes/adresses HPOS, des réglages et journaux fictifs. Les emails hors example.org sont des **pièges synthétiques**, jamais des abonnés réels.

Prérequis : PHP 8.2+ CLI, Python 3.10+ pour les tests de contrat CLI ; aucun Composer, WP-CLI, WordPress, plugin payant ou SQL n’est nécessaire. Le dossier scratch doit être un répertoire jetable autorisé, pas le dépôt ni une copie de site.

Suite A-01 reprise complète de ce dossier (résultats, comptes et SHA-256 après exécution dans `results.json`) :

```text
PHP_BIN=<binaire-php> IMAGINE_TEST_SCRATCH=<scratch-autorise> python wp/tests/staging-data/verify.py
```

Le lanceur exécute réellement les scripts, les variantes MU quarantainée/vérifiée, les sondes avec classe absente/présente et package installé sans classe, le contrat PDO, la chaîne CLI persistante ; puis lint PHP et manifest des fichiers propres à ce lot. Les comptes d’assertions sont calculés depuis les sorties, pas estimés. Il ne lance ni service, ni réseau, ni Git.

```text
IMAGINE_TEST_SCRATCH=<scratch-autorise> php -n wp/tests/staging-data/run.php
php -n wp/tests/staging-data/mu-plugin.php
PHP_BIN=<binaire-php> IMAGINE_TEST_SCRATCH=<scratch-autorise> python wp/tests/staging-data/commands.py
```

Sous Windows, définir ces variables dans le shell utilisé. Les commandes ci-dessus montrent la syntaxe POSIX ; ne pas passer un chemin MSYS à un binaire Windows natif.

- `run.php` : guards source production, conservation inconnus table/colonne/CPT et formats opaques sans exécution, AS/tokens, anonymisation classique/HPOS, pays/statuts/dates/montants/passerelle, admin post-restore, réexécution, URL no-op/drift, pas de bootstrap avant refus offline, purge et conservation des MU/drop-ins non-cache et sources.
- `reprise.php` : réglages et plugins formulaire/SEO/ACF intacts, liste négative SMTP, tables inconnues et décisions synthétiques garder/vider/anonymiser, chaque blocage du brief, emails JSON échappés, motifs/champs Stripe/PayPal même opaques, secrets en clés JSON échappées, sandbox PPCP, champs secrets Brevo seuls retirés, preuve absent impossible pour plugin actif, drift après sonde, rapports sans valeurs.
- `mu-plugin.php` : faux moteur de hooks sans transport. Mail/WCS/Cron/AS/passerelles ; allowlist HTTPS/443 seulement après marqueur vérifié, tromperies d’hôtes/userinfo/ports/schémas refusées, redirections bloquées. En production, WP_HTTP_BLOCK_EXTERNAL=false, WP_ACCESSIBLE_HOSTS=* ou DOING_CRON : code attendu 78.
- `runtime.php` : API/hook doubles, vérifie qu’un vrai appel de fonction wp_mail a lieu dans le double et zéro transport, classe WCS présente, absence réelle et package installé sans classe distingués. **Pas une preuve WordPress réelle ni l’usage des packages opérateur.**
- `pdo-contract.php` : PDO/Statement doubles, inventaire ouvert avec vues/MyISAM/triggers/events/identifiants SQL inhabituels, aucun corps SQL/valeur divulgué. Pas un serveur SQL.
- `commands.py` : vrais processus CLI, mémoire persistant en JSON synthétique dans le scratch, secret seulement stdin, refus des contextes/flags MU dangereux, décision fichier JSON appliquée, vrai enchaînement neutraliser/anonymiser/verifier accepté sur fixture propre et refus de chaque piège ajouté. Aucune valeur de fixture ne sort au rapport.
- `fixtures.php` : adaptateur mémoire transactionnel. Aucun dump/export/JSON de données n’est déposé dans le dépôt. Les fichiers de test portent explicitement un contenu `SYNTHETIC` et sont supprimés dans le scratch.

Limites : pas de serveur MySQL/MariaDB dans ce dossier, ni callbacks réels WordPress/WooCommerce. Les booléens unitaires ne sont pas une preuve runtime de staging. Les packages Subscriptions/Memberships sont confirmés disponibles par l’opérateur ; le pair possède leurs E2E synthétiques réels, ainsi que les WordPress classiques/HPOS enrichis de plugins gratuits. Ne pas déclarer ces critères satisfaits sur la seule base de cette suite. Voir le contrat et les limites dans `wp/outils/staging/README.md` et `HANDOFF-A-01.md`.
