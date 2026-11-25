# B-03 — Corrections du 25/11/2026

**Fait** : corrections fonctionnelles appliquées ; suppression prioritaire de 19h30 testée et déployée seule.
**Prêt à relire** : recette réconciliée après clôture C15 ; verdict courant lié dans `reconciliation-c15-current.json`. PRET redéposé uniquement après statut `VERIFIED` de ce nouveau reçu.
**À valider par Ced** : valeurs du designer puis contraste/rendu sur article réel ; validation visuelle toujours en attente.
**Réserve historique conservée** : quatre empreintes de tables diffèrent de l'ancienne référence ; leur identité historique n'est pas revendiquée. Ce n'est pas un échec fonctionnel courant du mode lecture.
**Ensuite** : retour au parent ; aucun rapport global V2, file ou verrou touché.

## État final après travail parallèle C15

L'ancien `verification-finale.json` racine reste `FAILED`, intact avec `corrections-before.json`, `preservation-corrections.json` et tous les anciens reçus. Il comparait la photographie antérieure avec l'état postérieur à l'action/reset C15 autorisée. Le nouveau reçu est dans `reconciliation-c15/<horodatage>/`, lié par `reconciliation-c15-current.json` avec SHA-256 ; il ne remplace pas cette preuve historique.

La garde courante prend avant ses propres tests le **même snapshot PHP**, puis exige après PHP/HTTP/JS/régressions/T01/C09 une égalité exacte des quatre tables non-utilisateur et des fichiers plugins/thème, **sans aucune exemption C15**. Elle compare aussi en mémoire le snapshot métier de `c15-action.py` avant/après (fixture, rôles, découverte, états/paiements/montants/propriétaires/adresses/dates métier), sans exécuter son action ni son reset, ni publier les adresses. Les 149 contrôles C09 natifs sont relus fraîchement, avec vérification des octets du test déjà déployé, sans upload C09 ni mutation de droits. Sept contre-exemples unitaires exercent le refus des dérives courantes, sources étrangères et mauvais octets C15.

Les seules différences historiques de sources admises sont exactement les deux assets B03 et les quatre chemins C15. Les empreintes de ces derniers doivent correspondre localement, à distance, à `C-15/verification.json`, `installation.json` et `livraison.json`. Le lien documentaire exige l'action/reset C15 verts, `restauration.json` sémantiquement égal et le SHA-256 de `c15-action.py` lié à la livraison. Les anciens reçus et pièces C15 sont contrôlés intacts pendant B03.

**Limite maintenue** : `wp_posts`, `wp_postmeta`, `wp_wc_orders`, `wp_wc_orders_meta` ont réellement changé depuis la référence historique. Chaque paire d'empreintes est conservée dans `preservation-reconciliation.json`. Le reset C15 peut légitimement changer dates techniques, lignes Woo et notes d'audit, mais les seules empreintes historiques ne permettent pas l'attribution exhaustive et exclusive de chaque ligne changée à C15. Ni identité binaire historique, ni attribution exclusive inventée, ni effacement de notes. Acceptation B03 limitée à son fonctionnement courant et à la stabilité exacte de sa propre fenêtre de rejeu ; cette réserve rétrospective reste visible.

## Résultat vérifié

- Couleurs inline et classes de blocs neutralisées **dans les trois thèmes**, uniquement en CSS de lecture ; contenu enregistré et images intacts. Paragraphe noir et bloc rouge testés dans Chromium à 390 et 1440 px : **21:1 / 14,255:1 / 16,157:1**, tous ≥ 4,5:1. Sondes uniquement dans le DOM client, supprimées.
- `pagehide` et `visibilitychange` recalculent synchroniquement la fraction avant sauvegarde ; hors lecture, la position mémorisée reste intacte. TDD rouge réel (reprise 0 au lieu de 1200) puis vert.
- Le HTTP lit la constante serveur, sans vitesse magique dans le contre-calcul. Le bloc reduced-motion redondant est supprimé, conformément à la file de 19h30 ; reprise JS toujours `instant`.
- **10 assertions PHP, 43 contrôles HTTP, 8 tests JS, 15 tests locaux, 1 012 tests T01 / 34 006 assertions et 77 contrôles navigateur**, zéro échec courant/ignoré. L’unique échec B01 historique « aucun JS » reste explicitement conservé, adapté en mémoire seulement.
- Octets locaux/déployés/HTTP identiques ; seuls `reading.css` et `reading.js` avaient été redéployés. **Aucun nouvel envoi** pendant la réconciliation. Égalité exacte avant/après du rejeu courant et 149 contrôles C09 frais, sans seed, reset, sauvegarde de commande ni paiement. Les différences historiques restent distinguées, sans prétendre que toutes les tables historiques sont inchangées.
- Script : **6 045 octets**, **1 956 gzip**. Vitesse serveur inchangée : **200 mots/minute**. Les corps C08 sont inchangés et le témoin réservé reste absent des réponses anonymes sondées.

## Décisions et incident résolu

Défaut prudent : neutralisation sur les trois fonds, pas de conservation des couleurs d’auteur en mode clair. L’éventuelle politique éditoriale d’Imagine reste une question client ; aucun contenu n’est réécrit. Progression non live inchangée, observation non bloquante.

Le Python d’origine a été retrouvé : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe` possède html5lib ; **`b03-final.py` a réellement réussi avec lui**. Le navigateur utilise le venv Hermes déjà équipé de Playwright. `REJOUER.md` donne les commandes exactes, séparées. Aucun paquet ni préparateur modifié ; pas d’installation globale. Deux erreurs initiales de harnais (échappement de la sonde SVG et test lexical prenant HTTP 200 pour une vitesse) ont été corrigées avant les résultats retenus.

**Amendement de 19h30** : suppression réelle du seul bloc redondant, contrat rouge puis vert (`reduced-motion-*.txt`), seul CSS envoyé et relu (`deploy-reduced-motion.json`). Le nouveau final est exécuté après cet amendement et après PRET C15. Les quatre chemins C15 ne sont plus une exemption fondée seulement sur une propriété déclarée : les octets finaux doivent égaler les reçus C15 et restent strictement stables pendant B03. Aucun plugin déployé ou restauré par B03. Les 77 contrôles navigateur anonymes déjà reçus sont réutilisés après liaison au CSS/JS courant, pas présentés comme une nouvelle inspection visuelle.

**Périmètre** : thème, seuls tests B03 sous `wp/tests/demo`, `production/B-03`. Site fictif `imagine-test-demo` uniquement ; aucun Git, plugin, autre lot, reset, compte/paiement réel, file, verrou ou rapport global modifié. PRET signifie prêt à relire, pas clôture, approbation visuelle ni GO de production.
