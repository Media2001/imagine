# A-32 — Cinq corrections appliquées, candidat vérifié sans PRET

**Fait :** les cinq instructions de `corrections/A-32.md` sont appliquées ; matrice Windows/native neuve verte, anciens essais hors dépôt.
**Prêt à relire :** candidat A-32 et sa matrice complète ; aucun PRET, aucune réception finale revendiquée.
**À arbitrer par Ced/parent :** résoudre l'ordre de réception A-32/A-33, sans modifier A-31 déjà vert.
**Bloqué :** les deux rejeux nomment A-33 `A33_GATES_INVALID` ; le portail A-32 conserve FAIL malgré des tests et outils verts.
**Ensuite :** commandes minimales et lecture seule dans `FINALISATION.md` ; le parent termine A-33 puis T-03 sur une réception réellement verte.

## Corrections et décisions prises à défaut

1. **C02 :** liste fermée locale complétée par les 21 codes dynamiques A11/A12/A15/A16/A17/A18/A19 × PROCESS_OUTPUT_INVALID/PROCESS_TIMEOUT/SUCCESS_INCOMPLETE. Classement « refusé » avec code ; inconnus et codes accompagnés de texte restent rejetés. Les deux cas de banc A-15 délai/A-19 incomplet utilisent de vrais processus PHP et le vrai gardien A-22 : **doubles de frontière explicitement déclarés**, délai réduit à 0,2 s et schéma de rapport incomplet, les treize autres outils restant réels. Les bilans portent exactement A15_PROCESS_TIMEOUT et A19_SUCCESS_INCOMPLETE.
2. **C04 :** `php_config.py` tokenize les chaînes comme données atomiques et les commentaires séparément ; aucun texte de chaîne n'est rescanné comme code. Déclaration littérale unique, autonome et au niveau supérieur seulement ; formes opaques refusées. Vrais refus natifs « define dans chaîne », « define dans commentaire », environnement absent, production et marqueurs invalides : zéro sous-processus de l'exécuteur par défaut, zéro sortie, empreintes base/fichiers identiques.
3. **C03 / A-16 :** `outils.jsonl` omet `--as-of` et `--limit`, en reconnaissant uniquement leurs défauts déjà documentés dans les README clos. A-19 relit vraiment l'UTC courant ; rejeu ultérieur, égalité stricte et passage 2026/2027 exercés par son CLI et les getters natifs. **A-16 reste N=10 par défaut, de 1 à 100 (README ligne 15), pas illimité et pas inventaire complet.** Le défaut proposé de la fusion affirme à tort que l'omission rend l'inventaire complet ; limite signalée, aucune capacité étendue ni mode d'emploi d'outil clos modifié.
4. **C01 :** seule la phrase obsolète A-32 du README commun renvoie désormais explicitement à `tournee/outils.jsonl`, A-26/A-27 inclus ; mention locale « remplacée » alignée. Les trois lignes contractuelles historiques sont intactes, sans empreinte globale du fichier partagé ni restructuration.
5. **Traçabilité :** `verified_site()` applique la décision d'arbitrage du **27 novembre, lignes 220–224** : interdiction du brief levée pour la tournée seule, lecture du statut comme A-05, refus global d'un seul code avant tout outil. Ce n'est pas une interprétation libre.

A-08 reste distinct (séquence mutante, arrêt au premier refus). La tournée continue après refus/échec, ne compte rien elle-même et conserve un bilan partiel dès qu'un incident survient. Liste inchangée de quinze : A-10/A-11/A-12/A-15/A-16/A-17/A-18/A-19/A-20/A-21/A-23/A-24/A-25/A-26/A-27. Hors tournée : A-13/A-14/A-30 (fichier Imagine), A-29/A-31 (non clos dans la file), A-02 (audit), A-03 (non-régression), A-04/A-05/A-08 (mutation), A-09 (plan), A-22 (gardien), A-28 (import).

## Exécutions réelles

Racine scratch : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a32-corrections-20261127-2158/`.

- Tests écrits et observés rouges avant les corrections : 21 refus dynamiques perdus, sept faux positifs PHP, défauts optionnels et phrase commune obsolète. Les diagnostics intermédiaires restent dans le scratch ; un semis temporel a d'abord refusé un customer_id absent, corrigé uniquement dans le semis fictif.
- `C:/Python314/python.exe -B wp/tests/a32/matrix.py --output=<racine>/matrix-final` : **exit 0**, sources stables **186 fichiers** (les huit sources A-33 incluses). Windows Python **3.14.6**, consoles mesurées UTF-8 / cp1252, PYTHONUTF8=1/0, **TMPDIR absent** dans les fils, TEMP/TMP dans le scratch. **15 tests Python par console ; 72 contrôles natifs + six contrôles runner par console**, tous PASS. Classique et HPOS dans chacune ; PHP seulement en conteneurs jetables déconnectés, aucun montage/port, suppression exacte et absence vérifiées.
- Sept canaux natifs par magasin/console : STDOUT/STDERR, arrêt anticipé bavard/muet, shutdown des deux flux, rapport fichier altéré. Aucun canari publié ; toutes tables, ordonnanceur et fichiers identiques. Commande README copiée avec ses seuls arguments, quinze succès réels dans le nominal ; doubles A-10/A-11 nommés et poursuite des autres conservés.
- Lecteur local `wp/tests/a32/verify.py --evidence=production/A-32/preuves/final` : **exit 0, A32_LOCAL_MATRIX PASS**. Qualification sur copies des vraies preuves : **9/9 attendus PASS**, huit corruptions refusées (preuve de chaîne manquante, processus lancé, base changée, code dynamique perdu/inconnu avec texte, date courante figée, égalité fausse, faux illimité A-16, empreinte falsifiée).

## Gates rouges conservées, aucun assouplissement

`wp/tests/a32/gates.py --output=<racine>/gates-current` : **exit 1, A32_CANONICAL_GATES FAIL, sources stables**. Image préparée avec succès après les ajouts de tests. Dans **chacune** des deux consoles : **1 206 tests / 36 680 assertions**, zéro échec/erreur/ignoré ; **23 outils / 852 contrôles**, zéro échec. A-20/A-21/A-22/A-28 sans argument : sortie 0. La photographie des gates couvre maintenant récursivement tout `wp/outils/bascule/`, donc A-33 aussi.

```text
PAQUETS : 12 vérifiés, 1 échecs ; hors rejeu : A-32 (journaux absents) ; A-33 A33_GATES_INVALID
```

A-32 était le candidat local installé par sa commande propre, sans gates finales : son exclusion pendant ces portails est déclarée, **pas** présentée comme une réception verte. A-33 reste inclus et rouge ; aucune exclusion ni porte n'est changée pour le faire passer. Les portails rouges authentiques sont conservés dans `preuves/final/qualification/gates-blocked/`, pas admis comme gates finales.

Un seul candidat courant, installé par `seal.py --evidence=... --archive-existing=...`, `complete=false` et `readiness_claimed=false`. Lecteur de production A-32 : **sortie 1 / A32_GATES_MISSING** ; A-31 : **sortie 0 / A31_PACKAGE_PASS**, PRET intact ; A-33 : **sortie 1 / A33_GATES_INVALID**. Aucun PRET A-32/A-33/T-03 créé. Aucun outil clos, gardien, import, lanceur, fichier A-31/A-33 modifié ; aucun Git, réel, archive, compte ni déploiement. Les 161 sources protégées de l'ancien paquet hors A-32 sont identiques ; les huit ajouts d'A-33 ne sont pas confondus avec un inventaire inchangé.

