# A-01 — quatrième passe, 26 novembre 2026

**Code prêt à relire sur archives fictives seulement.** Aucun import Imagine, compte réel, publication, Novamira ou nettoyage de site partagé. La commande et ses limites opérateur sont en tête de `wp/outils/staging-court/README.md`.

## Résultat prouvé

`archive-reelle-4/4d311daa09cc/result.json` : PASS. Vraie chaîne gratuite inchangée AI1WM **7.109**, WordPress fictif **7.0.9**, PHP **8.2.36**, runner neuf sans réseau/port/montage, MariaDB socket Unix. Base exportée **522 327 313 octets**, une vraie ligne de **18 Mio**, 481 lignes de volume : validation **25,374 s**, import avec lignes conservées **9,656 s**. JSON, colonne générée stockée, index préfixé, ROW_FORMAT DYNAMIC et dates zéro relus dans MariaDB ; MyISAM et MEMORY conservés.

Neuf contrôles runtime, dont vraie erreur **1062 / 23000 / ligne 272 / INSERT / SERVMASK_PREFIX_options**, vraie exception PHP `LogicException / plugins/fiction/fatal.php / ligne 1`, véritable timeout de 0,1 s ; aucun message, valeur ou adresse canari dans les diagnostics. Les trois scripts natifs passent aussi sur le même export avec la politique fermée par défaut. Le mode `--diagnose-database --operator-ced --archive ...` est réellement lancé sur cette archive fictive : **9,277 s** pour la partie interne base, aucun site ni wp-content extrait, phases natives explicitement différées, runner supprimé et absence relue. Les temps n'incluent pas tous les transports hôte ; ce n'est pas une garantie sur la production.

`archive-reelle/5754d4a5d8b8/result.json` : 109 tests Python Linux, **108 réussis, 1 ignoré NTFS**. La branche NTFS a été réellement exercée sur Windows : banque de 29 tests, 21 réussis et 8 branches Linux ignorées (déjà passées dans le runner). Ne pas cumuler ces banques. Neuf tests ciblés nouveaux passent. Rejeu T01 réel : **1 062 tests, 34 271 assertions, 0 échec/erreur/ignoré**. `preparer-image.ps1` a réellement terminé à code 0 avant PRET.

## Compatibilité et limites

- Le vrai export MariaDB ne contient **pas** le mode SQL de la source. Le rapport ne l'invente pas : SET SQL_MODE supporté conservé quand présent, sinon repli explicite non strict `NO_AUTO_VALUE_ON_ZERO`. Import 256 Mio/paquet, borne 3 600 s ; enveloppe restauration 5 400 s.
- MySQL 8 n'a **pas** été exécuté : son cas est une variante explicitement dérivée des CREATE du vrai export. Correspondances au rapport : `0900_ai_ci`/`0900_as_ci` → `unicode_520_ci`, `0900_as_cs`/`0900_bin` → `bin`, dans utf8mb4 uniquement. Les différences de tri peuvent déclencher un refus de contrainte, jamais une correction silencieuse des valeurs. Les variantes linguistiques non qualifiées sont refusées.
- Commentaires conditionnels : SET fermé seulement. Vues, DEFINER, triggers, procédures et événements restent **refusés explicitement** avant import (`SQL_EXECUTABLE_OBJECT_REFUSED`). Pas de SQL général de repli. Expressions DDL hors grammaire et instructions conservées au-delà de 64 Mio restent refusées. La passe n'est pas une qualification MySQL 8 générale ni de toutes les extensions historiques.
- Les erreurs des trois phases et du pont ont désormais un reçu assaini : étape, classe PHP, fichier relatif à wp-content si applicable, ligne ; erreurs PDO : errno/SQLSTATE et dernière opération/table. Les échecs des commandes externes et délais sont structurés, sans stderr brut. Les transferts de publication ont leurs étapes et codes séparés ; pas de nouvelle publication E2E dans ce lot.
- Après échec avant injection, le site de l'outil reste arrêté sur sa baseline initiale ; runner et copie de travail sont détruits. Au rejeu : nouveau nom, fichiers et base refaits. Pas de reprise sur copie non anonymisée conservée. Le diagnostic base seul évite de restaurer les fichiers pour découvrir une erreur SQL.
- `imagine-test-a01-ced-02` laissé intact : je ne peux pas prouver indépendamment son absence d'injection sans ouvrir la copie. Ced peut le vérifier/supprimer par l'API normale. Aucun GO nouveau.

Les essais ratés et l'interruption réelle d'une regex trop lente sont conservés comme historiques ; la regex a été rendue possessive et une régression de temps borné l'éprouve. Seuls les reçus ci-dessus lient les sources finales. Vérification pure :

```text
python wp/tests/a01-court/verify_fourth.py production/A-01/archive-reelle-4/4d311daa09cc/result.json production/A-01/archive-reelle/5754d4a5d8b8/result.json
```
