# A-17 — Sécurité des comptes d'administration, lecture seule

Après GO ponctuel de Ced sur copie vérifiée seulement, conteneur Linux sans réseau ni montage sensible, PHP 8.2+ / mysqli, Python 3, Landlock ABI ≥3 :

```text
python3 wp/outils/bascule/a17/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/securite-date
```

`--as-of=2026-11-26T12:00:00Z` fixe facultativement l'horloge UTC du diagnostic ; sinon maintenant. Douze mois calendaires en UTC ; un enregistrement exactement à la borne n'est pas ancien. Répertoire neuf, parent existant hors site/dépôt dans les deux sens et frère du rapport A-02. `securite.json` et `.md`, 0700/0600 ; aucun compte ni réglage modifié, aucune tentative de connexion. Même lanceur Landlock A-12 et unique connexion READ ONLY A-11 avant le bootstrap, sans exécuter wp-config. Les caches, pare-feu en drop-in et liens symboliques restent refusés en les nommant : préparer une copie sans ces fichiers, jamais modifier la source pour les besoins du diagnostic.

## Ce qui est mesuré

- Rôles natifs `administrator`, `shop_manager`, `editor` et rôles dont une capacité accordée commence par `manage_`, `edit_others_`, `delete_others_`, ou permet gestion des plugins/thèmes/cœur/utilisateurs. Seulement l'identifiant du rôle. Les simples auteurs/abonnés ne sont pas assimilés à des gestionnaires. Comptes multi-rôles dans chaque rôle ; `unique_management_accounts` dédoublonne. Périmètre : appartenance aux rôles ; permissions directes isolées ou permissions conditionnelles d'une extension ne sont pas reconstituées.
- Mots de passe d'application : API native `WP_Application_Passwords::get_user_application_passwords`, nombre de comptes ayant au moins une entrée ; jamais libellé, hash, date ni secret.
- Double authentification : adaptateur **Two-Factor**, API `Two_Factor_Core::is_user_using_two_factor`. Un compteur est une réponse de cette API au contexte CLI de l'audit, pas un essai de connexion ni la preuve d'une politique universelle. API indisponible/autre extension : `two_factor_active: null`, adaptateur `inconnu`, **jamais zéro déduit**. Les protections d'autres extensions peuvent être présentes sans que leurs comptes soient lisibles. Le banc utilise une extension fictive portant cette API, pas un audit d'un déploiement réel de Two-Factor.
- Dernière connexion : adaptateur **WP Last Login**, extension active `wp-last-login/wp-last-login.php`, métadonnée timestamp `wp-last-login`. Ancien timestamp valide : compteur `no_recent_record`. Entrée absente/nulle/invalide/future : `unknown_accounts`, sans estimer une inactivité ; aucun journal reconnu : statut `inconnu`, compteur `null`. Le cœur seul ne conserve pas un historique complet ; les sessions ne sont pas détournées en historique.
- Extensions de protection : en-têtes natifs des plugins installés, nom/version/active ou non, sans option. Familles repérées par identifiant/nom (`two-factor`, `2fa`, authenticator/login-security ; limit-login/loginizer ; wordfence/firewall/sucuri/solid/ithemes/all-in-one-wp-security). Liste de candidats identifiés, **pas une détection exhaustive ni une preuve de protection effective** ; les noms suspects sont masqués. Aucun réglage de ces extensions n'est lu ni exposé.
- Configuration : inscription et rôle par défaut natifs ; édition de fichiers d'après les booléens **du fichier original** `DISALLOW_FILE_EDIT`/`DISALLOW_FILE_MODS`, pas les valeurs forcées du confinement. Expression non littérale/doublon : inconnu ; absence = défaut natif autorisé. `xmlrpc_authenticated_methods` lit le filtre natif `xmlrpc_enabled` : ce n'est pas un test HTTP, n'établit pas le routage du serveur ni la disponibilité des pingbacks. Disponibilité des mots de passe d'application par l'API native, sans tenter d'en utiliser un.

## Rejouer

`python wp/tests/a17/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a17-rejeu-NOUVEAU`, puis `python wp/tests/a17/verify.py production/A-17/preuves/final`. PHP dans les seuls conteneurs jetables classic/HPOS A-02 ; WordPress/Woo natifs, extensions de sécurité **fictives**. Tests Python hôte : `python wp/tests/a17/test_launcher.py`. Python 3.14.7 Windows : UTF-8 puis cp1252/PYTHONUTF8=0 ; chaque sous-processus de test fixe son UTF-8. Paquet unique final, essais dans scratch. `wp/tests/rejouer.ps1` ne sélectionne pas cette suite dédiée.
