# A-17 — corrections du 26 novembre 2026

Les neuf instructions sont appliquées. **42 assertions PHP, 66 contrôles natifs classic/HPOS, 7 gardes du runner et 3 tests Python : verts**, en Python **3.14.7 natif Windows**, UTF-8 puis console **cp1252 / PYTHONUTF8=0** (encodages mesurés). PSR-12 des fichiers PHP A-17 : 0 erreur, 0 avertissement. `wp/tests/preparer-image.ps1` exécuté à code 0 avant PRET. Le vérificateur du paquet passe dans les deux contextes Windows.

Paquet unique : `production/A-17/preuves/final`. Les essais intermédiaires et les anciens paquets sont hors dépôt, dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a17-session/`.

| Instruction | Résultat et preuve dans le paquet |
|---|---|
| 1, règle commune | `refusal-common/` : 60 cas réels, dix par frontière PHP A-11/A-12/A-14/A-15/A-16/A-17, avec Landlock. Liens fichier/répertoire au nom-canari : stdout vide, stderr code fixe, aucun rapport créé. Constantes arbitraires masquées ; six drop-ins de liste fermée restent nommés. |
| 2 | `*-neutralisation.json` : clone fictif passant par les **vrais** `Engine::neutraliser()` et `anonymiser()`, import inchangé. Une ligne `_application_passwords` avant, zéro après, marqueur existant présent. `*-neutralised/securite.json` répond « inconnu après neutralisation » pour chaque rôle, jamais zéro déduit. Empreintes de toutes les tables et fichiers identiques pendant le diagnostic après neutralisation. |
| 3 | Rôles portant uniquement `edit_users`, `update_plugins`, `switch_themes` inclus ; rôle de simple contenu exclu. Onze capacités administratives ajoutées et exercées isolément, accordées et refusées ; liste complète dans le mode d'emploi. |
| 4 | `*-no-last-login/` : WP Last Login réellement exclu du chargement natif pour ce processus (il lève s'il est chargé), adaptateur/statut inconnus, compteur ancien null et inconnus = comptes. |
| 5 | Compte éditeur à la borne exacte du 26/11/2025 12:00 UTC non ancien ; compte daté du futur rangé inconnu. |
| 6 | Deux fournisseurs fictifs 2FA actifs, un seul reconnu. `two_factor_coverage: supported_adapter_only` empêche de lire le compteur comme le total certain du site. |
| 7 | Syntaxes alternatives `if`/boucles/switch, fonctions et contrôle de flux non démontré inconditionnel renvoient null, sans exécution de wp-config. |
| 8–9 | `manage_` volontairement inclusif (dont `manage_categories`) ; convention native du 29 février vers le 1er mars documentée et testée. |

**Rejeu** : `python wp/tests/a17/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a17-rejeu-NOUVEAU` ; `python wp/tests/a17/refusal-common.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/refus-rejeu-NOUVEAU`. **Contrôle** : `python wp/tests/a17/verify.py production/A-17/preuves/final`. Les deux lignes du mode d'emploi partagé sont contrôlées seules ; son empreinte entière n'est pas épinglée.

Le seul code de production commun modifié est **`wp/outils/bascule/a11/Runtime.php`** : détails arbitraires retirés à la source et filtrage fermé à la sortie. Aucun changement des six points d'entrée n'a été nécessaire. Modes d'emploi dédiés et attentes des canaris A-11/A-12 alignés. Non-régression native entièrement rejouée pour A-11 (300 contrôles), A-12 (132), A-14 (63), A-15 (84), tous verts sous Windows cp1252 ; leurs manifestes suivent, ces lots restent clos. Le reçu A-16 est additif (`production/A-16/refus-commun-A17.json`) : son paquet complet relève du worker A-16, pas de ce lot.

**Limites conservées** : extensions de sécurité fictives ; aucune preuve d'une vraie politique 2FA, d'un service externe, d'une tentative de connexion ou d'un routage HTTP. La preuve de neutralisation exécute les moteurs PHP sur une base fictive clonée, pas l'orchestration complète d'import d'archive. Le nombre historique de mots de passe d'application reste irrécupérable après import. Aucun PHP Windows, compte, donnée réelle, archive réelle, Git, déploiement, site voie 2, ni modification de `wp/outils/staging/`. Aucune clôture ni GO réel.
