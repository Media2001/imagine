# B-03 — Corrections du 25/11/2026

**Fait** : corrections fonctionnelles appliquées ; suppression prioritaire de 19h30 testée et déployée seule.
**Prêt à relire** : premier final passé et PRET déposé avant B04 ; **PRET retiré en fin de passage**, voir garde de préservation ci-dessous.
**À valider par Ced** : valeurs du designer puis contraste/rendu sur article réel ; validation visuelle toujours en attente.
**Bloqué en clôture de passage** : quatre empreintes de tables ont changé pendant le travail C15 parallèle ; réconciliation par le parent nécessaire.
**Ensuite** : retour au parent ; aucun rapport global V2, file ou verrou touché.

## État final après travail parallèle C15

Le final a réellement réussi après suppression CSS, avant la tranche B04. En fin de passage, tous les contrôles fonctionnels réussissent encore (10 PHP, 43 HTTP, 8 JS, 15 locaux, 1012 T01, 77 navigateur liés au CSS), mais la garde globale de préservation échoue : `wp_posts`, `wp_postmeta`, `wp_wc_orders`, `wp_wc_orders_meta` diffèrent de la photographie antérieure. Ce constat persiste après deux attentes de 30 puis 60 secondes. Les quatre chemins de plugin C15 déclarés sont séparés nominativement ; **les tables n’ont pas été exclues, réinitialisées ni remises à une nouvelle référence**. Ce worker n’a exécuté aucun seed ni sauvegarde de commande. Attribution exacte de ces différences au parent, pas une preuve inventée de préservation C09. Le reçu final reste donc `FAILED` sur cette seule garde ; PRET retiré, sans corriger les tables ni toucher C15.

## Résultat vérifié

- Couleurs inline et classes de blocs neutralisées **dans les trois thèmes**, uniquement en CSS de lecture ; contenu enregistré et images intacts. Paragraphe noir et bloc rouge testés dans Chromium à 390 et 1440 px : **21:1 / 14,255:1 / 16,157:1**, tous ≥ 4,5:1. Sondes uniquement dans le DOM client, supprimées.
- `pagehide` et `visibilitychange` recalculent synchroniquement la fraction avant sauvegarde ; hors lecture, la position mémorisée reste intacte. TDD rouge réel (reprise 0 au lieu de 1200) puis vert.
- Le HTTP lit la constante serveur, sans vitesse magique dans le contre-calcul. Le bloc reduced-motion redondant est supprimé, conformément à la file de 19h30 ; reprise JS toujours `instant`.
- **10 assertions PHP, 43 contrôles HTTP, 8 tests JS, 15 tests locaux, 1 012 tests T01 / 34 006 assertions et 77 contrôles navigateur**, zéro échec courant/ignoré. L’unique échec B01 historique « aucun JS » reste explicitement conservé, adapté en mémoire seulement.
- Octets locaux/déployés/HTTP identiques ; seuls `reading.css` et `reading.js` ont été redéployés. Empreintes avant/après : contenus, métadonnées, commandes/paiements et dates inchangés ; seules les modifications des quatre fichiers C15 explicitement attribués au worker parallèle sont isolées du contrôle des autres sources. Le complément C09 est conservé. Aucune recette C09/B02 ni fixture rejouée.
- Script : **6 045 octets**, **1 956 gzip**. Vitesse serveur inchangée : **200 mots/minute**. Les corps C08 sont inchangés et le témoin réservé reste absent des réponses anonymes sondées.

## Décisions et incident résolu

Défaut prudent : neutralisation sur les trois fonds, pas de conservation des couleurs d’auteur en mode clair. L’éventuelle politique éditoriale d’Imagine reste une question client ; aucun contenu n’est réécrit. Progression non live inchangée, observation non bloquante.

Le Python d’origine a été retrouvé : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe` possède html5lib ; **`b03-final.py` a réellement réussi avec lui**. Le navigateur utilise le venv Hermes déjà équipé de Playwright. `REJOUER.md` donne les commandes exactes, séparées. Aucun paquet ni préparateur modifié ; pas d’installation globale. Deux erreurs initiales de harnais (échappement de la sonde SVG et test lexical prenant HTTP 200 pour une vitesse) ont été corrigées avant les résultats retenus.

**Amendement de 19h30** : suppression réelle du seul bloc redondant, contrat rouge puis vert (`reduced-motion-*.txt`), seul CSS envoyé et relu (`deploy-reduced-motion.json`). Rejeu final avec l’interpréteur d’origine après cet amendement. Les fichiers parallèles C15 `EcheancesRegles.php`, `EcheancesNatives.php`, `EcheancesAdmin.php` et `imagine-site.php` sont observés localement et à distance : différences tracées et exclues nominativement du contrôle B03 selon leur propriété déclarée ; aucun plugin déployé ou restauré par B03. La base distante et tous les autres chemins restent comparés à la photographie initiale.

**Périmètre** : thème, seuls tests B03 sous `wp/tests/demo`, `production/B-03`. Site fictif `imagine-test-demo` uniquement ; aucun Git, plugin, autre lot, reset, compte/paiement réel, file, verrou ou rapport global modifié. PRET signifie prêt à relire, pas clôture, approbation visuelle ni GO de production.
