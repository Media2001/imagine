# A-29 — Les tâches planifiées, comptes en lecture seule

**Livraison locale partielle.** Aucun PHP, Docker ou WSL exécuté par le worker. Les lecteurs, banques PHP et classique/HPOS sont préparés ; leur qualification appartient au parent. Aucun `PRET`. Aucune donnée réelle, archive, compte ou site existant ne fait partie de ce lot.

## Le standard d'abord — dix lignes

1. WordPress déclenche ses événements temporels avec WP-Cron ; une visite peut réveiller des événements arrivés à échéance [S1].
2. Son stockage natif est l'option `cron`, tableau versionné : timestamp Unix UTC, hook, empreinte des arguments, déclaration de récurrence [S2 ; code installé à qualifier].
3. `_get_cron_array()` lit ce tableau ; les événements récurrents n'y représentent que leur prochaine occurrence, pas toutes leurs exécutions futures [S2].
4. Action Scheduler fournit les actions simples, récurrentes, cron et asynchrones ; un groupe est une déclaration du code appelant, pas une preuve de propriété [S3].
5. Son magasin SQL natif conserve notamment `hook`, `status`, `scheduled_date_gmt` dans `{prefix}actionscheduler_actions`, indépendamment de classique/HPOS [S4 ; code installé à qualifier].
6. Subscriptions programme le renouvellement sur `woocommerce_scheduled_subscription_payment` ; le suffixe de passerelle est une action d'exécution distincte, non assimilée par préfixe [S5].
7. Une nouvelle tentative de paiement utilise `woocommerce_scheduled_subscription_payment_retry` ; elle n'est pas un nouveau renouvellement à inclure dans les huit semaines [S6 ; code installé à qualifier].
8. L'expiration et la fin de période prépayée utilisent leurs hooks dédiés ; une fin d'essai ne signifie pas une fin d'abonnement et reste ici `autre` [S5].
9. L'ancien emailer Woo compose son hook WP-Cron depuis l'identifiant du blog et `wc_emailer` ; compter ce réveil de file n'est pas compter les messages [S7 ; code installé à qualifier].
10. Aucune API standard ne livre ce rapport agrégé privé : A-29 lit ces deux stockages sans runner, sous A-11/A-12 et le gardien A-22 inchangés ; `standard.php` doit qualifier les sources installées avant réception.

### Sources officielles

- S1 : https://developer.wordpress.org/plugins/cron/
- S2 : https://developer.wordpress.org/reference/functions/_get_cron_array/ ; code https://github.com/WordPress/wordpress-develop/blob/trunk/src/wp-includes/cron.php
- S3 : https://actionscheduler.org/api/
- S4 : https://github.com/woocommerce/action-scheduler/blob/trunk/classes/schema/ActionScheduler_StoreSchema.php ; https://github.com/woocommerce/action-scheduler/blob/trunk/classes/data-stores/ActionScheduler_DBStore.php
- S5 : https://woocommerce.com/document/subscriptions/develop/action-reference/
- S6 : https://woocommerce.com/document/subscriptions/develop/complete-guide-to-scheduled-events-with-subscriptions/
- S7 : https://github.com/woocommerce/woocommerce/blob/trunk/plugins/woocommerce/includes/class-wc-background-emailer.php

Les quatre pages S1/S3/S5/S6 et le fichier brut S7 ont effectivement été téléchargés le 26 novembre 2026 ; provenance et empreintes dans `production/A-29/sources-officielles.json`. Les références S2/S4 précisent le code à confronter sur le banc parent : leur lecture installée n'est pas revendiquée ici. Les branches publiques mobiles ne remplacent jamais les empreintes installées `classic-standard.json` / `hpos-standard.json`. Le contrôleur installé est lexical et accompagné des oracles natifs de stockage ; il ne constitue pas une preuve de comportement de toute extension. Aucun accès externe n'est fait par l'inventaire lui-même.

## Parcours du mode d'emploi — Linux confiné seulement

Prérequis : PHP 8.2+, Python 3, Landlock et réseau absent, copie fictive ou copie vérifiée expressément autorisée par Ced, audit A-02 existant. Ce mode d'emploi n'autorise pas d'accès au réel. La réserve indépendante A-22 reste entière. Parent de sortie existant, hors site **et** dépôt (ni descendant ni ancêtre) ; nouveau basename ASCII alphanumérique, tiret ou souligné. L'audit est dans un sous-dossier de ce même parent.

```sh
python3 wp/outils/bascule/a29/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/taches-date
```

Le banc copie exactement cette ligne, en substituant seulement les chemins de fixture, sans ajouter d'option. Succès : code `0`, stdout exactement `A29_OK taches.json taches.md` puis un saut de ligne, stderr vide. Refus : code `1`, stdout vide, une seule ligne fermée de `refusals.json` ; le refus A-11 de drop-in ne peut nommer qu'un de ses fichiers techniques autorisés. Ni message d'exception tiers, ni chemin/site/hook libre ne sort.

Deux fichiers 0600 dans un répertoire 0700 : `taches.json`, `taches.md`. Le processus enfant n'écrit que dans un dossier privé. A-22 attend la terminaison et les deux EOF ; A-29 exige le schéma fermé, des comptes entiers, le rendu Markdown canonique, l'empreinte/date/magasin de l'audit, et les empreintes émises avant les shutdown. Les octets finaux doivent toujours être ceux liés avant shutdown : même un JSON valablement altéré avec Markdown cohérent est refusé. Aucune sortie brute ni protocole interne ne devient public. Pas de fichier additionnel, lien symbolique, fichier vide ou partiel.

## Ce qui est compté

- Une ligne d'Action Scheduler, ou un événement WP-Cron à un timestamp et une empreinte d'arguments, est **une tâche**. Les deux magasins sont additionnés, pas dédupliqués par identifiant d'abonnement. Le réveil technique d'un runner est lui aussi une tâche distincte ; ce n'est pas un deuxième paiement.
- `pending` : WP-Cron présent et actions AS `pending`. `overdue` est leur sous-ensemble dont l'échéance est **strictement antérieure** à `audit.json.generated_at_utc`, jamais à l'heure du lancement. Égalité = pas en retard. Le zéro natif AS des actions asynchrones signifie à exécuter immédiatement ; il entre dans les retards, pas dans les paiements futurs.
- `failed` : actions AS au statut `failed`, et **AS seulement** (`failed_scope=action_scheduler_only`). WP-Cron ne conserve pas d'historique d'échec : aucune absence d'échec globale n'est déduite d'un zéro AS. `complete`, `canceled`, `in-progress` ne sont ni en attente ni en échec ici.
- Les sept familles fermées : renouvellement, nouvelle tentative, fin d'abonnement, email, entretien de WooCommerce, entretien de WordPress, autre. `Analysis::HOOKS` est une correspondance **exacte**, jamais une heuristique de préfixe ; tout hook non reconnu est `autre`, même celui d'une extension active ou un nom ressemblant à Woo. Le hook de fin d'essai reste `autre`.
- `renewal_weeks` : les prochaines occurrences **déjà présentes** des seuls paiements de renouvellement `pending`. Huit fenêtres glissantes de sept jours UTC à partir de l'audit, soit `[audit+7j×(n−1), audit+7j×n)` pour `n=1..8`. Borne basse incluse, haute exclue ; exactement audit+56 jours est hors fenêtre. Ce choix prudent explicite évite une semaine civile partielle ; ce n'est ni une prévision des prochaines créations du scheduler, ni la garantie de paiements réussis. Fuseau du site et changements d'heure n'interviennent pas.
- Chaque petite cellule de famille ou de semaine est fondue dans `autres`, sans son libellé ; seuil de visibilité : cinq. Les cellules à zéro n'apparaissent pas. Les semaines 1 à 8 sont des indices relatifs, aucune date individuelle n'est publiée. Le total des cellules fondues reste exact, conformément au pooling A-20.
- `other_tasks` compte les tâches `autre` en attente **ou** en échec, une seule fois (les retards ne sont pas ajoutés une deuxième fois). Une valeur de 1 à 4 devient `moins de cinq` ; 0 et les valeurs ≥5 sont visibles.
- `other_active_extensions` : en présence de tâches `autre`, **attribution indéterminée**. Ni hook, groupe AS, préfixe, nom d'extension active ni fichier d'un callback ne prouvent l'auteur de la planification. Aucun nombre n'est inventé à partir de ces indices. S'il n'y a aucune tâche `autre` dans le périmètre observé, cette contribution vaut 0 ; cela ne prétend pas inventorier les intentions futures de toutes les extensions. Cette limite fonctionnelle est explicite.
- Magasin AS personnalisé, migration hybride, données/date/statut/structure non reconnus : refus fermé, jamais zéro de remplacement. Classic/HPOS est relu par l'utilitaire Woo natif et doit correspondre à l'audit ; aucun magasin d'abonnements n'est concaténé.

## Import et résultat sur une copie neutralisée

Lecture du code commun sans modification : `wp/outils/staging/lib.php`, `transform()` vide `cron`, supprime les actions `failed`/`complete` et certains hooks d'import/export, annule les actions `pending`/`in-progress`, efface leurs charges opaques, et pose `imagine_staging_disabled_plugins`. Ce marqueur existe même si aucune extension n'a été désactivée. A-29 le teste par **présence en base**, pas par vérité du tableau et pas en déduisant la provenance de queues vides.

Ces transformations faussent **tous les six comptes** : `pending`, `overdue`, `failed`, `renewal_weeks`, `other_tasks`, `other_active_extensions`. Sur copie marquée, ils deviennent tous **inconnu après neutralisation**, jamais zéro et jamais une reconstruction des tâches annulées. Aucun des nombres demandés sur la source n'y reste utile. C'est le résultat prudent attendu, non une raison de toucher l'import ou d'autoriser un agent à lire la source. Les banques parent doivent encore le prouver par le véritable moteur inchangé sur un clone fictif ; aucun changement d'A-28 ne doit être contourné.

## Tests et réception

```sh
C:/Python314/python.exe -B -m unittest discover -s wp/tests/a29 -p "test_*.py" -v
C:/Python314/python.exe -B wp/tests/a29/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-python-neuf
C:/Python314/python.exe -B wp/tests/a29/verify.py --python-only --evidence=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a29-python-neuf
```

La matrice Python seule est **partielle** : refus CLI, schéma, copies jetables mutées, vrais pipes et vraie publication Python avec doubles explicites des frontières PHP et noyau. Pas de PHP, DB, WordPress, Docker ni Landlock validés par ces tests. Banques PHP pur, classique/HPOS, immutabilité intégrale, absence d'actions/appels sortants, standard installé, cinq canaux natifs et commande documentée : `production/A-29/RECEPTION-PARENT.md`. Une matrice finale complète, après gel A-28 et style, doit remplacer l'unique paquet local partiel ; aucun `PRET` ici.
