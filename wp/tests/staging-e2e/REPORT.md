# Rapport du site synthétique — reprise du 20 novembre 2026

**Résultat : acceptance non validée. Aucun `PRET`, aucune ouverture ni opération réelle.**

## Reçus courants

| Contrôle | Exécution exacte | Résultat |
|---|---|---|
| Sécurité du harness | `safety-ea3ab1ab37b7` | 17 tests réussis ; `results/reprise-host-safety.json` |
| Fixtures + oracles + référence gratuite avant traitement | `b425004823b0` | sortie 0 ; 75 PASS, 2 NOT_TESTED ; `results/reprise-fixture-selftest.json` |
| Vrais scripts, classique + HPOS enrichis | `1e34902aea35` | sortie 2 ; 15 PASS, 4 FAIL, 18 NOT_TESTED ; `results/reprise-acceptance.json` |
| Deux ZIP payants nommés par Ced | `73dd48355408` | sortie 2 ; 9 PASS, 2 FAIL, 20 NOT_TESTED ; `results/reprise-licensed-acceptance.json` |
| Contrats orchestration/worker dans Linux sans réseau | `905db63c580e` | suites de 7 et 6 tests réussies, 3 fichiers PHP lintés ; `results/reprise-integration-final.json` |

Les chiffres de PASS concernent des assertions journalisées, pas autant de tests métier indépendants. Les suites d'intégration utilisent des doubles de transport/stockage : elles ne qualifient pas un import `.wpress` ou le service partagé. Chaque conteneur nommé ci-dessus a été supprimé et son absence relue dans son reçu. L'image publique réutilisable est conservée, pas les sites/bases.

### Premier blocage des vrais scripts

En classique et HPOS : création des 30 comptes/30 commandes, bootstrap des trois extensions gratuites et préflight passent ; **`neutraliser` renvoie 78**. Le diagnostic séparé dans le conteneur synthétique confirme `PDOException`, **SQLSTATE `23000`, errno `1062`**, métadonnée mentionnée `wp_options.option_name`, dans `pdo-store.php:117` (`execute → replace → transform → neutraliser`). Aucun message PDO ni valeur de ligne n'est exporté. Une collision de nom d'option est observée, sans édition du script sujet pour la contourner.

Contact Form 7 **6.1.4**, Yoast SEO **26.5** et Meta Box **5.10.7** restent effectivement actifs dans la référence avant nettoyage ; formulaire rendu et champs simples/clonés lus. Leurs réglages sont empreintés. **La comparaison post-nettoyage n'a pas été atteinte**, de même que `anonymiser`, le vrai `verifier`, les décisions de tables, les refus de résidus et l'idempotence. Aucun de ces contrôles n'est annoncé réussi.

Les scripts sujets sont travaillés simultanément par le pair : les empreintes exactes sont conservées, ainsi que la liste d'éventuelles dérives au moment de l'emballage. Ces reçus décrivent leur snapshot, pas une attestation de toute révision ultérieure.

### Paquets payants : présence distincte de la réussite

Les seuls fichiers autorisés, `/home/ced/staging-wp/plugins/woocommerce-subscriptions.zip` et `woocommerce-memberships.zip`, ont été lus comme entrées, copiés directement dans les conteneurs neufs puis détruits avec eux. Aucun paquet/code payant dans le dépôt, aucun téléchargement de remplacement ni activation de licence.

- Subscriptions **9.4.1**, SHA-256 `ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083` : activation effectivement refusée sur WordPress **6.9**, car **7.0** requis. Le header impose aussi WooCommerce **11.1**, au-delà du **10.4.3** préparé.
- Memberships **1.30.3**, SHA-256 `d3a858a8d6ebc7153248a10d665c6752948ea4fa8a1836d6bdd8a8f267ee3285` : activation constatée dans les deux tentatives, mais ni droits d'accès ni fidélité après nettoyage qualifiés.

Versions, tailles, headers et résultats : `results/reprise-licensed-inputs.json`. La création d'abonnements synthétiques par API n'a pas été atteinte ; le mode staging réel, son piège inverse et les renouvellements restent non testés. Ne pas supprimer les gardes de version pour obtenir du vert.

### Intégration corrigée, limites maintenues

Contrats alignés sur `wordpress_staging`, `imagine-test-admin`, `production_hosts` et les adaptateurs image `/opt/staging/<phase>`. Fichier de décisions transmis au worker et à son contexte, verrou de résolution des tables, diagnostics filtrés visibles dans le rapport opérateur même en échec, absence de licence ne remplaçant plus le verdict du vérificateur natif. Ces changements ne sont **pas déployés**.

L'importeur prototype élimine encore les fichiers de l'archive au lieu de préserver l'ensemble extensions/thème/MU/médias ; l'étape Novamira n'est pas réalisée ; le réseau runtime reste `none`, donc les mises à jour externes ne sont pas qualifiées. L'image worker réelle, le serveur partagé/API/MCP, l'import d'archive et la publication n'ont pas été exercés. Voir `../../outils/staging-wp-integration/OPERATEUR-A01.md` : la commande opérateur est documentée mais **pas autorisée pour un import réel dans cet état**.

## Rapport historique du 19 novembre 2026 — conservé pour traçabilité

**Résultat : fixtures et isolation exécutées ; acceptance des scripts de staging en échec. Aucun staging réel créé et aucun jalon de livraison globale déclaré.**

## Exécuté réellement

- Dépendances publiques préparées avant création/import : WordPress **6.9**, WooCommerce **10.4.3**, WP-CLI **2.12.0**. Runtime observé : PHP **8.2.36**, MariaDB **10.11.19**. Versions choisies et épinglées, pas présentées comme les dernières versions.
- Deux sites jetables indépendants dans chaque passage : stockage classique puis HPOS, chacun avec **30 comptes et 30 commandes** entièrement fictifs. Exports et imports SQL exclusivement générés dans le même conteneur neuf.
- `test_harness.py` : **16 tests réussis**, aucune erreur ni test sauté. Reçu : `results/host-safety.json`.
- `fixture-selftest` : sortie **0**, **73 checks journalisés PASS**, deux rubriques `NOT_TESTED`. Cas propre accepté, neuf familles de pièges refusées par les oracles WordPress et PDO, sept réinsertions PDO contrôlées ; réimports propres et invariants retrouvés dans les deux stockages. L'espion PHPMailer confirme la détection d'un transport non bloqué **sans aucun envoi réel**. Reçu : `results/fixture-selftest.json`, passage `8cb0b564484d`.
- Avant import et après exécution : réseau `none`, aucun port, aucun volume/montage, capacités retirées ; dans le conteneur : seule interface `lo`, aucun listener TCP/IPv6, MariaDB sur socket Unix. Tous les conteneurs de ces passages ont été supprimés et leur absence relue.

## Échec observé, non masqué

L'acceptance appelle les **vrais lanceurs copiés** via leur interface `--worker-bridge`, sans les modifier. Sortie du harness **2** ; `neutraliser` renvoie **78** en classique **et** en HPOS. Le préflight en lecture seule rapporte `SCHEMA_INCONNU` pour quatre tables créées normalement par le WooCommerce public utilisé :

- `wp_wc_admin_note_actions`
- `wp_wc_admin_notes`
- `wp_wc_product_download_directories`
- `wp_wc_tax_rate_classes`

Le harness n'a ni supprimé ces tables pour forcer le succès, ni modifié le catalogue de staging. Les étapes dépendantes `anonymiser`, `verifier`, conservation après nettoyage, refus de résidus par le vrai vérificateur et répétition de la chaîne **n'ont donc pas pu être exercées**. Les refus de pièges réussis ci-dessus concernent les **oracles du harness**, pas une qualification du vrai vérificateur.

Preuve : `results/acceptance.json`, passage `110c4c2018f2`, avec empreintes des sources réellement copiées. Il s'agit d'un défaut d'acceptance concret, distinct des licences manquantes.

## Dépendances et hors périmètre

- Subscriptions et Memberships : aucune licence/code fournis au site jetable ; extensions absentes, aucun double factice déclaré valide. Mode staging Subscriptions et comportements d'abonnement/droits **non testés** ; la sonde réelle reste susceptible de bloquer ensuite.
- Aucun WordPress/outil installé sur l'hôte : Docker existant utilisé via WSL. Les paquets PHP/MariaDB vivent uniquement dans les images jetables.
- Aucun secret/donnée réelle, archive réelle de site, volume de site, service marchand, SMTP réel, Novamira, orchestrateur ou script de bascule utilisé. Aucune opération Git et aucune édition des scripts staging/bascule/outil.
- Dépendances publiques et image de test conservées uniquement pour rejouer : `results/dependencies.json` et inventaire public `results/public-packages.tsv`. Les sites/bases ne subsistent pas après suppression du conteneur.

## Rejeu

```bash
python wp/tests/staging-e2e/test_harness.py
python wp/tests/staging-e2e/harness.py fixture-selftest
python wp/tests/staging-e2e/harness.py acceptance
```

Sur une autre machine déjà équipée : exécuter d'abord `python wp/tests/staging-e2e/harness.py prepare`. Les journaux nouveaux sont séparés par identifiant dans `evidence/` ; les reçus livrés dans `results/` ne sont pas réécrits automatiquement.
