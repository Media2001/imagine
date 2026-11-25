# A-05 — Corrections du 25 novembre 2026, résultat actuel

P1, P2, P3 et M1 appliqués ; prêt à relire, pas clos et sans GO réel.
**Preuve finale actuelle : `production/A-05/preuves/8d814c18912a/`.** La section historique ci-dessous décrit uniquement le dépôt de 18 h 35, pas l'état actuel.

- **21 tests unitaires**, **149 contrôles natifs classique/HPOS et d'isolation**, **7 contrôles du runner** : tous réussis ; trois fichiers PHP lintés dans le conteneur. Durée finale : **197,836 s**, `corrections-20261125/full-native-final.json`.
- **44 refus adverses**, 22 par stockage (11 plans en mode à blanc puis réel), sans mutation de base/fichiers ni checkpoint : `classic-corrections.json`, `hpos-corrections.json`.
- **29 sources** finales sans dérive, **307 fichiers de preuves préexistantes** inchangés, **52 fichiers de dépendances protégées** inchangés depuis le précontrôle, **16 sources A-04 acceptées** comparées au manifeste `eb2aea037769`, aucune dérive : `verification-finale.json`.
- Image existante `sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2`, sans téléchargement. PHP uniquement dans les conteneurs jetables A-05 créés par le runner. Propriété/isolation vérifiées avant/après ; chaque nom exact supprimé et absence vérifiée ; aucun conteneur A-05 restant.

## Corrections et décisions prises à défaut

1. **P1** : refus de retrait de tout dossier partagé avec un autre fichier principal, en nommant le voisin, `garder` ou `desactiver`, actif ou inactif, dans les deux ordres. Variante prudente autorisée : plusieurs `retirer` dans le dossier sont aussi refusés, pour ne pas supprimer avant la désinstallation explicite du voisin.
2. **P2** : mêmes préfixes WordPress `[ \t/*#@]*` pour `Plugin Name` et `Requires Plugins`. Cas `//` et `#` testés au retrait et à la désactivation, en SQL/CLI réels ; `get_plugin_data()` confirme les en-têtes. Dépendance fictive dédiée, déclarée par cette seule extension, pour exclure un faux positif dû au scénario nominal.
3. **P3** : conflit uploads symétrique ; ancêtre gardé/descendant supprimé refusé dans les deux ordres du plan.
4. **M1** : JSON `information`, `status: "nommé, absent"`, pour plugins, tables/préfixes, options/préfixes, cron et uploads absents. Les deux stockages prouvent cinq informations, zéro opération, empreintes égales et passage réel `A05_NOOP`, sans checkpoint.

Aucune question métier, visuelle ou touchant au réel. M2 reste une fragilité surveillée, non un correctif demandé ; passerelle sans marqueur : limite documentée. Aucun retrait réel choisi.

## TDD et réception actuelle

`corrections-20261125/{P1,P2,P3,M1}-{red,green}.json` donnent commandes, codes, durées et huit chemins de preuve. Échecs attendus observés avant chaque correctif : P1 cinq sous-échecs, P2 huit, P3 deux, M1 un. Après chacun, toute la suite unitaire disponible est verte.

Le paquet final rejoue tout le brief initial : à blanc sans mutation, retrait nommé seulement, ressources non nommées intactes, désinstallation native uniquement explicite, gardes A-04 et refus antérieurs, vrai SIGKILL/reprise et deux seconds passages sans effet. Le checkpoint ambigu simulé reste étiqueté et distinct du vrai SIGKILL. A-03 natif inchangé : classique et HPOS, code 0, `changes: []`, `anormal: 0`, aucune requalification ; retrait prouvé séparément par inventaire. Photographies et journaux PHP conservés.

Le premier rejeu `cbb821169e10` reste historique : la fixture P2 a ensuite été renforcée avec sa dépendance dédiée, puis tous les contrôles ont été rejoués sur les sources finales.

Quatre fichiers `wp/` modifiés ici : `wp/outils/bascule/a05/clean.py`, `wp/tests/a05/test_clean.py`, `wp/tests/a05/inside.py`, `wp/outils/bascule/nettoyer.md`. Variations concurrentes hors périmètre enregistrées dans `verification-finale.json`, jamais restaurées ni modifiées ici. Aucun Git, A-FAIRE, verrou parent, A-08, archive/donnée réelle, site externe ou démo touché.

Commandes depuis `C:/Users/Ced/imagine` :

```bash
python -B wp/tests/a05/run.py --unit-only
python -B wp/tests/a05/run.py
python -B production/A-05/corrections-20261125/verifier.py
```

Aucun paquet de tests/Composer ajouté, seulement des cas dans le paquet Python A-05 existant. **`preparer-image.ps1` n'est donc pas requis ni relancé pour cette correction.** Les anciens résultats T-01 ci-dessous restent historiques, pas un nouveau rejeu global. Aucun blocage. A-08 revient au parent ; audit, plan rempli et GO écrit restent requis avant toute opération réelle.

---

# HISTORIQUE — Dépôt précédent de 18 h 35 (preuves et résultats non actuels)

Le texte ci-dessous est conservé pour traçabilité ; ses mentions « finale »/« à retenir » concernent uniquement l'ancien dépôt, remplacé par `8d814c18912a`. Les originaux PRET, notes, vérification et scellement sont aussi conservés sous des noms historiques dans `corrections-20261125/`.

# A-05 — Résultat et preuves de réception

## Résultat

Outil terminé, à relire uniquement. Aucun passage sur le vrai site, aucune archive Imagine ouverte, aucun accès à un compte réel, aucune opération Git. A-03 et A-04 restent inchangés. La file et les verrous du parent ne sont pas modifiés.

Preuve finale : `production/A-05/preuves/3f1d3e3ce8f2/`.

- `unit.log` : 16 tests unitaires réussis.
- `result.json` : 93 contrôles réussis sur le banc natif classique et HPOS et sur l'isolation. Deux de ces contrôles concernent un checkpoint de désinstallation construit volontairement : ce sont des compléments de refus fermé, pas la preuve d'interruption réelle.
- `runner.json` : 7 contrôles réussis ; code final 0 ; conteneur exact supprimé et absence vérifiée. Image native réutilisée : `sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2`.
- `sources.json` : 29 sources/dépendances figées et revérifiées sans dérive. `production/A-05/verification-finale.json` compare aussi 31 fichiers aux manifestes de la preuve A-04 acceptée `eb2aea037769` : aucune dérive.
- `production/A-05/preparation-image-finale.log` : reconstruction/revérification réelle T-01, code de commande 0. Image finale `sha256:dea690d346e71c1a7fba48b7c3cd8d99c26bcc09cdacc7a818690609f19d510c`.
- `production/A-05/rejeu-global-final.log` : 1 012 tests PHPUnit, 34 006 assertions ; aucun échec, aucune erreur, aucun ignoré. Le thème sans configuration PHPUnit reste signalé par le runner commun ; ce n'est pas une validation visuelle. A-05 a son runner Python/natif distinct, il n'est pas ajouté artificiellement à ces 1 012 tests.

## Correspondance avec le brief

| Critère | Pièce et contrôle |
|---|---|
| À blanc sans changement de base ou de fichier | `classic-dry-fingerprints.json`, `hpos-dry-fingerprints.json` ; empreintes complètes avant/après égales, schémas/séquences inclus ; `*-dry-run.json` donne les lignes, octets et fichiers |
| Extension inactive avec tables, famille datée, extension active, options/cron et dossier | `*-inventory.json` avant/après : `a05-orphan`, `wp_a05_orphan`, `wp_a05_stats_2015`, `wp_a05_stats_2026`, `a05-remove`, `a05_orphan_setting`, `a05_orphan_hook`, `a05-debris` |
| Retrait nommé uniquement | `*:only_named_removed`, `*:unlisted_files_intact`, `*:unlisted_tables_intact`, `*:unlisted_option_values_intact`, `*:unlisted_cron_payloads_intact` ; les arguments des tâches conservées sont comparés par empreinte, jamais exportés |
| Désinstallation uniquement explicite | `*:default_uninstall_not_run`, `*:explicit_uninstall_dry_does_not_run`, `*:native_explicit_uninstall` ; vraie API WordPress et vrai `uninstall.php` fictif |
| Désactiver sans retirer | `*:native_deactivate_files_kept` : extension inactive, fichiers toujours présents |
| Dépendance, commerce, passerelle, thème, table cœur/gardée et sortie uploads | `*:refusal_*`, `*:resolved_upload_escape_refused`, tests unitaires ; chaque refus indique le nom/chemin fautif et ne supprime rien. Une action de thème n'existe pas : tentative par traversée vers le thème actif refusée |
| Mêmes gardes A-04 | Fonctions A-04 importées, bootstrap et runtime natifs exacts ; `*:maintenance_required`, `*:inherited_recent_backup_guard`, `*:inherited_canonical_backup_guard`, `*:inherited_verified_status_guard`, `*:dry_actual_environment_guard` |
| Crochet réellement orphelin | Tâche préalablement relue dans la base ; `*:registered_hook_not_orphan_refused` prouve le refus natif d'un crochet chargé, sans mutation |
| Arrêt puis reprise | `*:actual_cleaner_paused`, `*:same_site_other_state_locked`, `*:actual_sigkill`, `*:checkpoint_fsynced`, `*:actual_resume` ; vrai processus tué par SIGKILL, pas un checkpoint simulé ; rafraîchissement après 20 minutes fictives de maintenance expirée sous verrou |
| Second passage sans effet | `*:repeat_zero_effect` et `*:fresh_second_pass_zero_effect` ; empreintes complètes base/fichiers identiques, avec le même checkpoint puis un nouveau |
| Non-régression A-03 | `classic-before/`, `classic-after/`, `hpos-before/`, `hpos-after/` et `*-comparison.json` ; vrai collecteur, HTTP local, compte SELECT et contrôle borné des journaux PHP |
| Formulaire Imagine conservateur | 22 dossiers du diagnostic, 3 règles de tables et 3 dossiers uploads, tous à garder ; comparaison exacte au registre dans `verification-finale.json` ; aucune option ni tâche inventée |

Les seules écritures d'accompagnement dans le site sont la maintenance persistante réutilisée d'A-04 et le rafraîchissement de sa date lors de la reprise ; elles sont explicitement distinguées des ressources supprimées. Les journaux et sauvegardes fictives sont hors site ; les sauvegardes de fixture disparaissent avec le conteneur et ne sont pas livrées en archives.

## Ce que montre réellement A-03

Dans les deux stockages, le comparateur **natif et inchangé** rend `0`, `changes: []`, `anormal: 0`. Aucun retrait n'a été reclassé en « attendu ». A-03 ne constitue pas un inventaire exhaustif des plugins ordinaires et de WP-Cron : le retrait de l'extension et de la tâche fictives est établi par l'inventaire séparé. Les photographies PHP avant/après ont toutes un journal vérifié sans erreur. La preuve historique `7d5190caa8a9` avait une mauvaise attente du test de banc (il supposait une anomalie de plugin) ; le résultat natif était déjà 0. Seul cet oracle du banc a été corrigé, jamais A-03 ni sa classification.

## Décisions prises à défaut

1. Aucun chemin principal d'extension inventé depuis le diagnostic : dossier seul autorisé pour `garder`, fichier principal exact exigé pour agir. Les noms inconnus restent en place.
2. Pas de déduction automatique de propriété des tables : inventaire audité obligatoire pour toutes les extensions dont les fichiers restent, MU-plugins et thème actif. Une liste vide veut dire « audit, aucune table », pas « inconnu ». Sans cet inventaire, pas de suppression de table.
3. Inspection à blanc par SQL en lecture seule, sans démarrage des extensions. La validation dynamique des crochets orphelins et de la sûreté du runtime s'effectue avant la première mutation réelle.
4. Désactivation native silencieuse, mais ses hooks de mise à jour d'option pouvaient encore retirer des transients Woo/Jetpack. La preuve rouge `593433826e29` l'a révélé. Les écritures de cette opération sont maintenant bornées à `active_plugins` ; les empreintes finales prouvent la conservation des options non nommées. Le banc prouve aussi la présence réelle du cron initial : la garde de staging bloquait sa planification habituelle, il est donc semé directement par l'adaptateur de fixture, jamais exécuté.
5. Le nom du journal `fsmpt_email_logs` reste celui du diagnostic, même s'il paraît atypique. Préfixes SQL effectifs et routines inconnus attendent l'audit, pas une correction devinée.
6. Reprise automatique des opérations idempotentes ; refus fermé si une routine tierce de désinstallation a commencé sans reçu final. Elle n'est pas rejouée aveuglément. Cette limite est documentée, et son refus est distinct de la vraie preuve SIGKILL/reprise du nettoyage ordinaire.
7. Site unique, racines conventionnelles uniquement ; chemins personnalisés refusés. Tâches = WP-Cron par crochet exact ; aucune purge ni exécution Action Scheduler. Un filtre arbitraire redéfinissant les chemins demande une qualification propre.

## Rejeu exact depuis la racine du dépôt

```bash
python -B wp/tests/a05/run.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Mode d'emploi et forme des commandes d'exploitation : `wp/outils/bascule/nettoyer.md`. Les passages historiques rouges sont conservés comme tels. La preuve à retenir est exclusivement `3f1d3e3ce8f2`, produite après le dernier changement de source. Aucun appendice du runner commun, aucun fichier A-03/A-04 et aucun fichier de la voie 2 n'ont été modifiés.

## Limites et suite

Le passage sur le site Imagine attend toujours l'audit, le plan rempli par Ced, les préalables et le GO écrit requis pour toute opération réelle. Il n'y a aucune question métier à inventer ni autorisation d'exploitation dans ce rendu. Les routines tierces de désinstallation demandent leur propre audit ; leurs effets ne peuvent pas être estimés automatiquement. Ce lot est prêt à relire, pas clos.
