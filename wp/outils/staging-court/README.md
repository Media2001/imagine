# A-01 — corrections du 22 novembre, remise globale NON PRÊTE

**Le PRET précédent est invalidé.** R4/R3/R1/R2/R6/R7 corrigés et exécutés ; R5 attend le choix Ced **admin / scripts**. Protections inchangées : `DISALLOW_FILE_MODS=true`, édition et mises à jour automatiques désactivées. Aucun arbitrage implicite. Voir le point courant de `production/A-01/notes.md` et `production/A-01/NON-PRET-22nov.md`.

Contrôle source/cœur strict : `package.json → WordPress.Version` obligatoire et identique au cœur épinglé avant import SQL/bootstrap. La recette commerciale conserve **7.0.9** ; une archive **6.9.1** est refusée avec `SOURCE_CORE_VERSION_MISMATCH`, jamais mise à niveau silencieusement. Le refus conserve étape/code sûrs dans `offline_failure`, sans stderr brut. Le format reste `.wpress` non compressé, site simple, grammaire fermée ; moteurs locaux acceptés sans conversion : InnoDB/MyISAM/Aria/Memory, moteurs non-InnoDB signalés. Seul MyISAM est qualifié ici en E2E.

**La commande opérateur est désormais `publish.py`, pas l'ancien `run.py --archive`.** Mode d'emploi complet, mot de passe stdin, décisions de tables, reprise fraîche, limites et preuves : **`production/A-01/notes.md`**. Ced seul lance le premier import réel ; aucun agent n'ouvre l'archive Imagine.

```sh
# Ced uniquement ; chemins fournis par lui, mot de passe demandé sans écho.
PYTHONDONTWRITEBYTECODE=1 python wp/outils/staging-court/publish.py \
  --operator-ced --archive "$ARCHIVE_WPRESS" \
  --name imagine-test-a01-ced-01 --production-url "$URL_SOURCE" \
  --table-decisions "$DECISIONS_CED" --php-version 8.2

# Rejeu réel synthétique, nouveaux tests nommés et suppression finale ; borne 600 s.
PYTHONDONTWRITEBYTECODE=1 python wp/outils/staging-court/publish.py --self-test-publication

# Lecture seule ; bornes outil 60 s et 300 s.
PYTHONDONTWRITEBYTECODE=1 python wp/tests/a01-court/test_publication.py
PYTHONDONTWRITEBYTECODE=1 python wp/tests/a01-court/verify_publication.py \
  --report production/A-01/publication-22nov/6d5fac463e61/result.json --live-cleanup
```

Omettre `--table-decisions` sans décision écrite. Nom `imagine-test-…` strict, minuscules/chiffres/tirets simples, 40 caractères maximum, nouveau site obligatoire. Restauration et traitements natifs hors ligne avant injection/démarrage ; API normale uniquement pour le cycle du test, aucun nouveau frontal ni modification de l'outil. Les accès agent créés automatiquement ne sont jamais utilisés. Succès : témoin racine `.imagine-staging-verified.json` relu et rapport `verified`, dashboard `running`. Échec : site arrêté et rapport, jamais faux verified.

**Preuve corrigée : `production/A-01/publication-22nov/6d5fac463e61/result.json`, 4 cas PASS** : classique/HPOS publiés avec vrais Subscriptions/Memberships et MyISAM conservé ; secret et table personnelle non tranchée refusés avant injection. Diagnostics et double panne R4 réellement exercés par `wp/tests/a01-court/exercise_corrections.py` ; reçu `production/A-01/corrections-22nov/faults-a4d2ca414cea/result.json`. Huit nouveaux sites supprimés et absence relue ; runner R4 volontairement refusé puis récupéré/supprimé explicitement. Réseau après vérification : filtrage WordPress seulement, pas pare-feu système.

`run.py --self-test` reste le banc hors ligne, avec `full_staging_ready=false` attendu : rejeu `production/A-01/tests-21nov/3c4e0cfbc8c4/result.json`, 18 contrôles PASS, 12 tests archive, 17 banc, 9 cas/337 assertions données. `publication_preflight.py` garde son verdict historique du 21/11 ; seul son collecteur en lecture seule est réutilisé, pas ce verdict licence obsolète après GO.

---

# Historique du 21 novembre — pas le mode d'emploi actuel

# A-01 — chemin court hors ligne, lot complet encore bloqué

21 novembre 2026. Aucun GO, import réel, publication web ou modification de l'outil partagé.

## Commande exécutée et disponible

Depuis la racine du checkout :

    python wp/outils/staging-court/run.py --self-test

Elle crée un conteneur neuf, sans réseau, port, montage, volume ni accès aux autres sites. Les archives .wpress sont créées depuis WordPress/WooCommerce fictifs dans ce conteneur, restaurées dans ce même conteneur, puis détruites avec lui. Aucun fichier d'archive n'est exporté vers l'hôte.

Le dernier reçu est dans production/A-01/tests-21nov/d1cc212680fd/result.json : 18 contrôles d'aller-retour PASS en classique/HPOS et du vrai entrypoint opérateur, 12 tests défensifs du lecteur, 17 tests du banc, 9 cas/337 assertions de la suite de données. Syntaxe PHP ajoutée et sources contrôlées. La suite native E2E complète est également rejouée séparément : wp/tests/staging-e2e/evidence/9ff611303d90/ (131 PASS, 2 hors périmètre). Les conteneurs sont supprimés et leur absence vérifiée.

## Commande opérateur prévue pour Ced uniquement — pas encore à utiliser sur du réel

    python wp/outils/staging-court/run.py --operator-ced --archive "$ARCHIVE_WPRESS" --target-url "$URL_STAGING" --production-url "$URL_SOURCE" --table-decisions "$DECISIONS_CED"

Les variables sont fournies par Ced, pas découvertes ou remplies par l'agent. Omettre --table-decisions sans décisions écrites. Le mot de passe neuf du compte test est demandé sans écho et transmis par stdin, jamais dans argv, les rapports ou le dépôt. Rien n'est installé sur l'hôte ; aucun pull ou téléchargement runtime. L'image publique locale épinglée est une baseline synthétique 6.9/10.4.3, pas une compatibilité garantie avec une archive quelconque.

Cette commande ne publie aucun port, ne raccorde aucun réseau et n'écrit aucun statut dans l'outil partagé. Si les données sont vérifiées, elle retourne actuellement 78, status imported, data_verified true et verification_state DATA_VERIFIED_PUBLICATION_BLOCKED, avec un rapport ; jamais un faux statut global verified. Le conteneur exact est arrêté et conservé pour l'opérateur. En refus, le rapport contient étape, tags, tables/colonnes/nombres de lignes et décisions manquantes, aucune valeur de ligne. Un agent ne lance pas cette branche.

## Ce qui fonctionne

Le code .wpress conserve réellement les fichiers wp-content (extensions, thèmes, MU et médias), contrairement au prototype qui les élimine. Le format accepté est le flux non compressé à en-têtes de 4 377 octets ; chemins ambigus, doublons sans sensibilité à la casse, traversées, troncatures, dépassements, multisite et configurations racine sont refusés. Le SQL utilise le parseur fermé existant, sans repli vers du SQL arbitraire. Ajustements locaux : ON UPDATE/utf8mb3_general_ci et ordre du suffixe AUTO_INCREMENT, par groupes CREATE seulement ; littéraux INSERT inchangés. Des exports AI1WM chiffrés/compressés, multi-volume, syntaxe SQL hors sous-ensemble et versions différentes ne sont pas qualifiés.

Les trois scripts natifs sont réutilisés inchangés. Une table personnelle non tranchée bloque ; le test prouve d'abord ce refus, puis une décision nommée exclusivement fictive. Ced doit décider garder/vider/anonymiser telles colonnes dans son JSON, puis relancer sur une nouvelle copie. Aucune décision réelle préremplie.

La preuve compare tous les fichiers avant nettoyage et les seuls écarts attendus après : archive fictive purgée, deux drop-ins retirés, MU de sécurité ajouté. Active plugins et thème, formulaire rendu, SEO, champs simples/clonés, commandes et empreintes survivent en classique et HPOS.

## Pourquoi pas PRET global

Le chemin archive -> fichiers fidèles -> neutraliser -> anonymiser -> verifier est exercé. Le passage vers un staging utilisable et publié, avec sortie système limitée aux hôtes de mise à jour, n'est pas implémenté. Une whitelist WordPress ne constitue pas un confinement système pour les sockets des extensions. Ouvrir simplement bridge/port serait une fausse conformité ; aucune barrière n'est desserrée.

Le code de l'importeur partagé fidèle n'est pas fourni dans ce checkout ; son prototype disponible supprime les fichiers. Le rechercher hors checkout ou le modifier dans le service partagé est exclu par la consigne. Une nouvelle orchestration frontend/proxy/réseaux dépasserait le chemin court : arrêt de cette extension au titre de la proportion, sans inventer d'adoption ni de GO. Aucun PRET A-01 n'est déposé. Les fichiers ci-dessus sont un sous-lot vérifié, pas une commande d'import réel adoptée.

Les couches overlay/API, bascule, Novamira et worker runtime de staging-wp-integration restent non déployées et non développées. Seul le parseur SQL pur de worker.py est réutilisé en lecture ; aucune écriture partagée, recherche de site ou d'archive extérieure.
