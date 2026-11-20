# Tests de neutralisation et anonymisation

Aucun serveur ni compte réel. Les fixtures sont construites en PHP : trente utilisateurs, trente commandes classiques/abonnements, trente commandes/adresses HPOS, des réglages et journaux fictifs. Les emails hors example.org sont des **pièges synthétiques**, jamais des abonnés réels.

Prérequis : PHP 8.2+ CLI, Python 3.10+ pour les tests de contrat CLI ; aucun Composer, WP-CLI, WordPress, plugin payant ou SQL n’est nécessaire. Le dossier scratch doit être un répertoire jetable autorisé, pas le dépôt ni une copie de site.

```text
IMAGINE_TEST_SCRATCH=<scratch-autorise> php -n wp/tests/staging-data/run.php
php -n wp/tests/staging-data/mu-plugin.php
PHP_BIN=<binaire-php> IMAGINE_TEST_SCRATCH=<scratch-autorise> python wp/tests/staging-data/commands.py
```

Sous Windows, définir ces variables dans le shell utilisé. Les commandes ci-dessus montrent la syntaxe POSIX ; ne pas passer un chemin MSYS à un binaire Windows natif.

- `run.php` : guards, source production, inconnus table/colonne/CPT, neutralisation, annulation AS, retrait tokens, options opaques, anonymisation classique/HPOS, objets refusés, PHP sérialisé/JSON, pays/statuts/dates/montants/passerelle conservés, admin post-restore, réexécution, URL no-op et drift pendant sonde, contrôle refusé avant bootstrap, purge et préservation des sources PHP.
- `mu-plugin.php` : faux moteur de hooks, aucun appel réseau/mail. Vérifie les valeurs de court-circuit, le filtre officiel WCS, Cron, AS et passerelles. **Ce n’est pas une intégration WordPress réelle.** Exécuter aussi avec `IMAGINE_SYNTHETIC_ENV=production` : code attendu 78, aucun succès.
- `commands.py` : lance réellement les trois exécutables sur un bridge Store mémoire dans un dossier éphémère, secret synthétique via stdin, vérifie les codes et l’absence du secret dans stdout/stderr. Le refus de `verifier` sur fixture non traitée/sans sonde est attendu.
- `fixtures.php` : adaptateur mémoire transactionnel. Aucun dump/export/JSON de données n’est déposé dans le dépôt. Les fichiers de test portent explicitement un contenu `SYNTHETIC` et sont supprimés dans le scratch.

Les tests n’exercent pas le SQL du `PdoStore`, les callbacks réels de WordPress/WooCommerce, ni Subscriptions/Memberships sous licence. Ces limites ne sont pas masquées par les booléens de sonde fictive. Voir le contrat et les validations restantes dans `wp/outils/staging/README.md`.
