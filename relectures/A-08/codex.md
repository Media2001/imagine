# Relecture indépendante Codex — A-08

Date : 25 novembre 2026. Périmètre : brief A-08, production livrée et outils/tests correspondants dans `wp/`. Consignes de `relecteurs/AGENTS.md`, doctrine et grille appliquées. `relectures/A-08/claude.md` non consulté.

## 1. Conformité

L'ordre des six outils est respecté. Le choix d'une commande compagnon est expliqué et évite de modifier le lanceur accepté. Les deux rendez-vous opérateur sont justifiés par les exigences natives : lecture SQL seule pour A03, maintenance et écriture pour A04/A05. Les GO distincts sont transmis aux outils concernés. Le brief ne cite pas de paragraphe précis du cahier des charges ; les références applicables examinées sont les §4.3 et §4.4, complétés par les décisions des 11 et 19 novembre sur la conservation de l'existant et la bascule.

**R1 — Important — `wp/outils/bascule/a08/sequence.py:170` — Des refus laissent un rapport périmé.** Le gestionnaire extérieur écrit seulement sur stderr et retourne 1. Exemple : après une réception terminée, rendre un fichier d'entrée introuvable puis demander `--new-pass` fait échouer le calcul d'identité avant le chargement du checkpoint ; `rapport.md` conserve alors « TERMINÉ — réception sans anomalie ». Une exception après chargement, telle que `A08_PASS_NOT_COMPLETE`, n'actualise pas davantage le rapport. Cela contredit le rapport unique à consulter en cas d'arrêt, recommandé dans la procédure. **Correction proposée :** distinguer les refus qui permettent d'écrire dans un état sûr, sous verrou, et y produire un rapport d'arrêt explicite. Si l'état est inaccessible ou détenu par une autre exécution, signaler explicitement sur stderr que le rapport existant ne décrit pas cette tentative. Tester au minimum l'entrée disparue après succès et le second passage demandé sur état incomplet, sans écraser le rapport d'une exécution concurrente.

**R2 — Important — `wp/outils/bascule/repetition.md:46` — La reprise après anomalie de comparaison n'a pas d'issue documentée.** La consigne « Même commande et drapeau du rendez-vous » relance uniquement la comparaison lorsque celle-ci a retourné 2 : les cinq premières étapes sont déjà dans `done`, et les deux photos restent scellées. Corriger le site ne change donc pas le résultat de cette comparaison. `--new-pass` refuse cet état à cinq étapes réussies ; modifier la photo provoque un refus d'empreinte. **Correction proposée :** préciser expressément que cette reprise ne refait pas la réception et documenter d'où repartir. Défaut technique prudent, sans modifier les outils natifs : conserver les preuves d'échec, restaurer la sauvegarde de départ vérifiée et recommencer les six étapes dans un nouvel état, avec des entrées cohérentes. Si une nouvelle photo après correction est souhaitée, prévoir une opération explicite et testée qui conserve l'historique ; ne pas conseiller la suppression manuelle des checkpoints.

**R3 — Mineur — `wp/outils/bascule/a08/sequence.py:43` — Le rapport mélange plusieurs passages avec une seule comparaison.** Les durées et reçus cumulent toutes les tentatives, mais `comparison` ne contient que le dernier résultat. Le rapport final livré affiche ainsi zéro changement attendu, alors que le premier passage en avait quatre ; le lecteur doit ouvrir les anciens logs pour le découvrir. **Correction proposée :** garder un rapport unique, mais identifier les passages et présenter leur comparaison respective, ainsi que des durées clairement attribuées ou explicitement cumulées.

## 2. Exactitude métier

Deux cas applicables déroulés à la lecture du code et confrontés aux preuves scellées, sans accès à une base :

1. **Préservation de l'existant lors de la bascule** — §4.3, corrigé par la décision du 11 novembre : les comptes et abonnements existants restent en place. Dans le premier passage classique puis HPOS, les appels suivent bien audit, avant, mise à jour, nettoyage, après, comparaison. Le comparateur natif retourne 3 avec quatre changements classés attendus et zéro anormal ; le wrapper accepte ce résultat. L'inventaire séparé vérifie la disparition des déchets fictifs que la comparaison A03 ne couvre pas exhaustivement. Les preuves concordent avec ce périmètre, sans constituer une réception du site réel.
2. **Refus avant modification puis reprise** — §4.4 et préalables du brief : la maintenance manquante provoque `A04_MAINTENANCE`, code 1. Le checkpoint conserve seulement audit et avant ; nettoyage et réception ne partent pas. Après remise en place des préalables, la reprise repart à la mise à jour et conserve la photo avant. Les empreintes de fichiers et de base consignées avant/après le refus sont identiques dans les deux stockages.

Le second passage relance réellement les six outils et obtient une comparaison vide. L'interprétation de l'idempotence est annoncée : rafraîchissement possible de `.maintenance` et de l'expiration d'un transient WCS, sans autre changement selon les empreintes livrées. Cette limite technique est explicite, et non dissimulée dans un résultat prétendument immobile octet par octet. Les calendriers et dates de clôture métier ne sont pas implémentés par A08. Le cas limite manquant est surtout la sortie d'une comparaison anormale, décrite en R2.

## 3. Tests

**Exécution indépendante réussie :** `python -B production/A-08/verifier.py`, code 0. Le vérificateur contrôle les empreintes de 73 fichiers protégés, 59 sources, 166 preuves, 16 éléments historiques et 11 éléments de livraison, ainsi que les assertions sur les reçus et le lien avec `PRET`.

**Rejeu complet empêché par l'environnement :** le runner documenté écrit normalement dans `production/A-08/preuves`. Une tentative de lancement avec sa seule destination de sortie redirigée en mémoire vers un répertoire temporaire, sans modifier le script, échoue avec `PermissionError / WinError 5` avant les tests. Le contrôle séparé du prérequis Docker via la commande WSL utilisée par le banc échoue également : `Wsl/Service/E_ACCESSDENIED`, code 4294967295. La chaîne classique/HPOS et les 14 tests A08 n'ont donc pas été réexécutés ici.

Deux assertions existantes sans entrées/sorties disque ont néanmoins été rejouées : ordre/arguments des commandes et transmission séparée des GO, **2 réussites**. Adaptations uniquement en mémoire : chargement du sujet depuis son chemin local et chemins `PurePosixPath`. L'essai initial du premier test avec les chemins Windows avait échoué sur les séparateurs ; ce n'est pas un défaut de la cible Linux documentée. Ces deux contrôles ne remplacent pas la suite Linux.

**Résultats livrés, contrôlés mais non reproduits intégralement :** paquet `production/A-08/preuves/2bbcefb53170`, 14 tests A08, 49 contrôles natifs, 11 contrôles du runner ; régressions A02 : 17, A03 : 10 et 5 frontières, A04 : 48, A05 : 21, tous annoncés réussis et vérifiés par le script en lecture seule. Les tests couvrent notamment refus, reprise, altération d'entrée/preuve, verrou, sorties hors site, log PHP en erreur et comparaison invalide. Ils ne couvrent pas les scénarios R1 et R4 ; le test de code 2 s'arrête au premier refus et ne traite pas R2.

Durées livrées, en secondes, cumulant deux passages et le refus :

| Étape | Classique | HPOS |
|---|---:|---:|
| Audit | 2,382 | 2,587 |
| Avant | 2,220 | 2,489 |
| Mise à jour | 82,857 | 82,289 |
| Nettoyage | 2,748 | 2,621 |
| Après | 2,509 | 2,190 |
| Comparaison | 0,078 | 0,069 |

Ces mesures excluent préparation, sauvegarde et attentes opérateur ; elles ne donnent pas la fenêtre de maintenance du site réel.

## 4. Sécurité et données

**R4 — Important — `wp/outils/bascule/a08/sequence.py:77` — L'identité des outils omet du code réellement exécuté.** Le scellement se limite à `wp/outils/bascule`. Or les fichiers A03 `Report.php` et `Policy.php` de ce répertoire sont des relais vers `wp/plugins/imagine-non-regression/src/` ; `Site.php` charge aussi la sonde de `wp/outils/staging/`. Une modification du véritable comparateur entre les rendez-vous laisse donc l'identité A08 inchangée : la reprise peut accepter une nouvelle politique de comparaison pour des photos prises avec l'ancienne. La garantie annoncée de reprise avec les mêmes outils n'est pas tenue. **Correction proposée :** définir les dépendances de code nécessaires aux outils appelés et inclure leurs empreintes dans l'identité, notamment les implémentations A03 hors de `bascule`. Tester qu'une modification de ces dépendances refuse la reprise avant tout appel natif. Le manifeste de livraison protège ces fichiers au moment de sa vérification, mais ne remplace pas ce contrôle à chaque reprise.

Aucun secret ni donnée réelle identifié dans les éléments examinés. Les rapports synthétiques ne recopient pas les valeurs des photos. Les commandes utilisent des listes d'arguments, sans shell ; les contrôles natifs et les GO ne sont pas court-circuités. Les reçus livrés décrivent un conteneur sans réseau, montage ni port, avec suppression contrôlée. Aucune connexion à un site ou compte n'a été effectuée pendant cette relecture. A08 n'ajoute pas de voie HTTP ni de paywall : les nonces et l'échappement d'une interface web sont hors de son périmètre.

## 5. Doctrine

L'orchestrateur réutilise les outils existants et n'ajoute pas de transformation métier. Le choix Python prolonge les wrappers A04/A05 ; les conventions PHP ne s'appliquent pas aux nouveaux fichiers Python. Le travail reste sur un banc fictif, avec les limites de versions et les ajustements de fixture explicités dans `notes.md`. Aucun changement d'extension tierce relevé pour ce lot.

Les corrections proposées sont techniques et assorties d'un défaut prudent. Elles ne nécessitent pas d'arbitrage métier, visuel ou touchant au réel par Ced. La restriction de rejeu décrite ci-dessus ne constitue pas un défaut du lot et n'autorise aucun assouplissement de ses garde-fous.

## 6. Études (lots sans code)

Sans objet : lot de code et de procédure, sans étude comparative d'extensions à valider.

## Verdict

**À corriger.**

- **Bloquant :** aucun identifié dans le périmètre examiné.
- **Important :** R1 — rapport périmé lors de certains refus ; R2 — procédure sans issue explicite après comparaison anormale ; R4 — dépendances exécutées absentes de l'identité de reprise.
- **Mineur :** R3 — comparaisons des passages précédents absentes du rapport cumulatif.

Ce verdict n'est pas un GO. Le contrôle des preuves livrées a réussi ; le rejeu natif complet reste non effectué dans cette session pour les raisons d'environnement documentées.
