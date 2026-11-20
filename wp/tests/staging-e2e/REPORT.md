# Rapport du site synthétique — 19 novembre 2026

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
