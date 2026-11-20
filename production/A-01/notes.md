# A-01 — reprise synthétique stabilisée

**20 novembre 2026 — PASS classique et HPOS sur données inventées.** Reçu exact : `wp/tests/staging-e2e/evidence/f36c72f4d187/result.json`, sortie **0**, **131 checks PASS, 2 NOT_TESTED**. Le journal du même répertoire confirme isolation avant/après et suppression relue du conteneur exact. Ces checks ne sont pas autant de tests métier indépendants.

**Aucun GO pour l'import réel.** Aucun vrai site, archive réelle, connexion Novamira, service partagé, téléchargement, installation hôte, Git, déploiement ou ouverture web utilisé dans ce sous-lot. Aucun `PRET` ajouté : l'intégration complète reste hors qualification de cette reprise ciblée.

## Causes isolées depuis `6cb3c90a73b0`

Les onze sources sujets étaient identiques au manifest du reçu de départ avant correction.

1. **Classique : décision manquante.** `wp_yoast_primary_term`, vide, comporte `taxonomy`, qui contient le motif conservateur `nom`. Le vérificateur exige `TABLE_PERSONNELLE_A_TRANCHER`, même sans ligne. Le classificateur n'a pas été assoupli. Le banc prouve le refus puis ajoute `garder` pour cette table **uniquement dans son contexte fictif**, marqué `decision_is_synthetic_not_Ced_approval`. Aucun choix de production ni arbitrage de Ced n'est créé.
2. **HPOS : collision de clé structurelle.** Le diagnostic `evidence/ff179a0b7caf/result.json` isole `PDOException`, SQLSTATE **23000**, errno **1062**, lors du remplacement de `wp_wc_order_addresses`, avec `address_type` parmi les colonnes modifiées. Le motif `address_…` vidait les discriminateurs billing/shipping : collision sur la clé unique d'une commande. La correction de `lib.php` exclut **seulement `wc_order_addresses.address_type`** de ce vidage personnel. Le nettoyage des valeurs dangereuses s'applique toujours auparavant. Aucun contrôle du vérificateur retiré.
3. **Oracle historique de note erroné.** `9ab62bc07a81` passe ensuite les traitements, la fidélité et les onze premiers résidus, mais attend à tort un avertissement pour une note liée à une commande. Le sujet et son test unitaire la classent déjà dans le périmètre transactionnel. Le banc teste désormais les **deux** branches : note de commande avec email externe refusée ; commentaire sans lien transactionnel accepté avec avertissement. Aucun affaiblissement du sujet pour obtenir du vert.

Les diagnostics exportent uniquement tags, codes SQLSTATE/errno, classes/fonctions et noms de tables/colonnes ; ni SQL, ni message PDO brut, ni valeurs de ligne. Sorties des sujets empreintées.

## Preuves dans les deux stockages

- **30 comptes et 30 commandes fictifs chacun**, créés par API WordPress/Woo ; exports/réimports SQL générés dans le même conteneur neuf. Chaîne `neutraliser → anonymiser → verifier` réussie, puis répétée.
- **Fidélité après nettoyage** : nouveau bootstrap réel de WordPress/Woo et des extensions Contact Form 7 **6.1.4**, Yoast SEO **26.5**, Meta Box **5.10.7** ; extensions actives, formulaire rendu, champs simples/clonés lus. Empreintes exactes inchangées des réglages, article et MU de champs.
- PDO indépendant : statuts, dates, montants, devise, produits, quantités, taxes, pays et moyens de paiement conservés ; mots de passe des 30 comptes remplacés et compte test ajouté. Les **60 adresses HPOS** gardent id/order_id/address_type/pays ; identités connues nettoyées. Sessions, jetons, tâches sortantes, cron et webhooks de fixture neutralisés.
- **Douze résidus par stockage** réinsérés indépendamment, détectés avant vérification, puis refusés avec le tag attendu : clé secrète/publique/restreinte/webhook/Brevo, clé en table inconnue, identifiant Stripe compte/commande, PayPal, email compte/commande/note liée. Refus de données `1` + tag exigé, pas un simple échec quelconque.
- Mail bloqué à l'exécution. Retrait du seul MU de sécurité : espion PHPMailer mémoire sensible et refus du sujet ; **aucun envoi réel**. Oracles également sensibles avant blocage.
- Table inconnue non personnelle conservée/rapportée. Table personnelle non tranchée refusée. Décisions fictives `garder`/`vider`/`anonymiser` exercées avec email externe et téléphone inventés : empreinte intégrale conservée, lignes vidées, ou seules colonnes désignées anonymisées ; présentation préservée.
- Réseau `none`, aucun port/montage/volume, capacités retirées, `no-new-privileges`, loopback seule, aucun listener TCP/IPv6, MariaDB sur socket Unix. Suppression ciblée et absence relue de chaque conteneur créé ; aucun prune.

Runtime épinglé, pas annoncé comme le plus récent : WordPress **6.9**, WooCommerce **10.4.3**, WP-CLI **2.12.0**, PHP **8.2.36**, MariaDB **10.11.19**. Image locale sans pull : `sha256:b2ffa6ad01ffacc6d31b176232c8d0779c0320daba381e05cbbd80f56d5327a0`.

## Reçus conservés

Chemins relatifs à `wp/tests/staging-e2e/`. Historiques non écrasés.

| Reçu | Résultat |
|---|---|
| `evidence/7011e26f91ee/` | reproduction des deux blocages de départ |
| `evidence/ff179a0b7caf/` | diagnostic des colonnes HPOS, sans valeurs |
| `evidence/9ab62bc07a81/` | oracle erroné de note liée isolé après fidélité réussie |
| `evidence/a45dd77b707c/` | premier vert : sortie 0, 129 PASS / 2 NOT_TESTED |
| **`evidence/f36c72f4d187/`** | **stabilisé renforcé : sortie 0, 131 PASS / 2 NOT_TESTED** |
| `evidence/c1186257ca0c/` | fixture-selftest : sortie 0, 75 PASS / 2 NOT_TESTED |
| `evidence/safety-22eece7f2ddf/result.json` | 17 tests de sécurité du banc réussis |
| `evidence/bb87e0db2ac4/data-result.json` | échec Linux conservé : `-n` masquait PDO partagé |
| `evidence/2ea8c8781c6c/data-result.json` | 9 cas data/MU/runtime/CLI, 337 assertions et lint réussis |
| `evidence/2ea8c8781c6c/journal.json` | régression billing/shipping verte sur correction, rouge sur ancien `lib.php` empreinté ; conteneur supprimé |

Les tests data/MU sont des doubles unitaires, distincts du vrai WordPress/MariaDB et des paquets payants. Le seul contrat PDO charge maintenant l'ini normal nécessaire à son module partagé Linux, au lieu de `-n` : aucune assertion supprimée, aucun module installé. Pilote ponctuel isolé conservé avec son reçu : `data-regression-driver.py`.

## Rejeu synthétique et limites

Depuis **`C:/Users/Ced/imagine`**, Python et Docker existants :

```sh
python wp/tests/staging-e2e/harness.py acceptance
```

Journal JSON et nouveau `evidence/<run_id>/` avec résultat, manifests des sources et contrôle de suppression. Code 0 seulement si les deux stockages et contrôles requis passent. Image locale manquante : refus, pas de `prepare` sous consigne sans téléchargement. Compléments : `python wp/tests/staging-e2e/test_harness.py` puis `python wp/tests/staging-e2e/harness.py fixture-selftest`.

- **Paquets payants déjà testés, non relancés ni remplacés.** `results/reprise-licensed-acceptance.json` : Subscriptions **9.4.1** exige WordPress **7.0** et WooCommerce **11.1**, incompatibles avec **6.9 / 10.4.3**. Pas de contournement/licence/achat/téléchargement. Mode staging réel, son piège inverse, abonnements et renouvellements non qualifiés. Memberships **1.30.3** avait été activé ; droits non qualifiés.
- Les deux `NOT_TESTED` du reçu vert sont `paid_plugins_scope` et `real_staging_and_start_gate`. Aucun booléen de substitution crédité comme preuve commerciale.
- Bootstrap CLI, pas de serveur web exposé. Importeur d'archive complet/fidélité des fichiers production, service partagé/API/MCP, Novamira, bascule, réseau après vérification et mises à jour externes non exercés.
- Emails/IP éditoriaux hors transaction restent signalés, pas effacés globalement. Inconnues/formats opaques rapportés. La fixture verte ne qualifie pas toutes les extensions de production. Un avertissement conservateur d'identité sur `address_type` subsiste dans le vérificateur, sans blocage.
- Intégration opérateur non modifiée. Son ancien blocage data dans `OPERATEUR-A01.md` est dépassé par ces reçus ; ses autres réserves (importeur fichiers, Novamira, réseau) subsistent. Sa commande ne devient pas autorisée pour une archive réelle par ce résultat.
- Les anciens arrêts et révocations évoqués ci-dessous n'ont pas été revérifiés. **Ne pas réactiver l'ancien staging.** La réussite actuelle porte exclusivement sur la chaîne synthétique demandée.

## Notes antérieures — historiques, remplacées par le point ci-dessus

### Profil « site à abonnements » : ancien point de recette

**Décision de recette : ne pas lancer l’import réel.** L’outil partagé n’a pas été modifié. L’ancien site a été arrêté sans suppression ; la liaison agent est désactivée dans l’outil, mais la révocation du mot de passe applicatif dans WordPress n’est pas attestée. Ne pas redémarrer cette copie.

**Fait.** Les trois traitements hors ligne, les protections persistantes, le lanceur de bascule et le banc de test existent. Sur deux sites jetables (classique et HPOS), chacun avec 30 comptes et 30 commandes inventés, le banc a contrôlé l’absence de réseau et de port ouvert. Les tests propres au banc ne valent pas validation de la chaîne.

**Échec initial à conserver.** Dans les deux stockages, la neutralisation s’est arrêtée avant nettoyage sur quatre tables WooCommerce non reconnues. Les scripts n’ont donc pas encore démontré, ensemble, la réussite sur une copie propre puis le refus d’une copie contenant un résidu. L’intégration opérateur doit aussi être reliée aux scripts réels et exercée sans doublure Docker avant qualification. Voir `wp/tests/staging-e2e/REPORT.md` et `wp/tests/staging-e2e/results/acceptance.json`.

**Reprise du 20 novembre 2026.** Les quatre tables ne bloquent plus le précontrôle. Après correction de la prise en charge du type `shop_order_placehold` (champs texte anonymisés comme les commandes), la recette `wp/tests/staging-e2e/evidence/4bfcf5ac22d1/` passe la neutralisation dans les deux stockages. En classique, l’anonymiseur termine mais le vérificateur signale `SECRET_OU_IDENTIFIANT` ; en HPOS, l’anonymiseur refuse (78), cause exacte à isoler. Les 16 tests du banc passent ; conteneur jetable supprimé. Le paquet d’intégration et les sources du worker sont présents dans le dépôt, sans qualification bout en bout. Prochain diagnostic : localiser la table et la colonne sans afficher les valeurs ; identifier l’opération refusée en HPOS. Aucun import réel.

**À arbitrer par Ced :** des paquets de test autorisés pour Subscriptions et Memberships sont-ils disponibles pour le site jetable (oui/non) ? À défaut, les contrôles de ces extensions restent non validés ; pas de contournement du contrôle Subscriptions, ni d’achat.
