# C-31 — Relecture indépendante Codex

28 novembre 2026. Périmètre : brief C-31, §3.9 du cahier des charges, décisions, code et preuves livrés. Aucun accès au site, à une base ou à un compte ; rapport de l’autre relecteur non consulté.

## 1. Conformité

Le code respecte les choix principaux du brief : liste manuelle vide par défaut, domaines fictifs de démonstration, comparaison exacte sans casse, sous-domaines explicitement indépendants, message neutre, absence de révocation des comptes existants. Le changement d’adresse est raccordé au hook WooCommerce prévu. L’exception C-16 est cohérente avec l’appel direct à `wp_insert_user` dans `CommandeNative.php:107`.

La provenance de la liste est bien rangée pour Imagine dans `docs/decisions.md:105`, avec le défaut demandé. Les livrables sont présents. La garantie « aucune adresse refusée en base » reste insuffisamment établie pour la commande : voir I2.

## 2. Exactitude métier

Cas déroulés à la lecture du code, en référence au §3.9 et aux précisions du brief :

| Cas | Résultat du code |
| --- | --- |
| Liste contenant `jetable-fictif.example.org`, inscription `fictif@JETABLE-FICTIF.example.org` | Domaine ramené en minuscules ; erreur avant insertion par les deux filtres d’inscription. |
| Même adresse, liste vide | Aucun refus ajouté. |
| `fictif@sub.jetable-fictif.example.org`, seul le domaine parent listé | Accepté, conformément au choix documenté. |
| Compte existant dont le domaine vient d’être ajouté, adresse inchangée | Aucun refus ajouté à la sauvegarde ; une adresse différente sur ce domaine reçoit une erreur. |

Aucune erreur de comparaison constatée. La persistance effective du dernier cas n’est toutefois pas éprouvée par le test livré (I1).

## 3. Tests

Exécutés localement :

- `python -B production/C-31/verifier.py` : **PASS**. Vérification des empreintes et des résultats enregistrés : 32 contrôles natifs, 16 navigateur, rejeu historique de 1 219 tests / 36 748 assertions. Ces nombres ne désignent pas un nouveau rejeu PHP effectué par cette relecture.
- `python -B production/B-13/qualifier.py C-31` : **PASS**, neuf contre-exemples du vérificateur.
- Tentative ciblée de `DomainesRefusesC31Test.php` avec PHPUnit dans l’image locale `imagine-tests-t01:1`, réseau coupé et sources en lecture seule : **non exécutée**, WSL refuse l’accès (`Wsl/Service/E_ACCESSDENIED`). Le journal livré atteste deux tests C-31 et dix assertions. Aucun contournement ni installation.

Les modes `--live` et les recettes natives/navigateur n’ont pas été relancés : `relecteurs/AGENTS.md` interdit au relecteur l’accès au site et à la base. La mutation livrée retire réellement le filtre Woo, constate la création indue et supprime le compte témoin.

**I1 — Important — `wp/tests/demo/c31-runtime.php:37`.** Le test de changement d’adresse appelle uniquement `do_action`, puis constate que l’ancienne adresse est toujours en base. Aucune sauvegarde native n’a été tentée : cette seconde assertion ne prouve pas que le parcours « Mon compte » empêche l’écriture. **Correction proposée :** soumettre le véritable formulaire de modification, puis relire le compte après la requête ; couvrir le refus, un changement autorisé et l’adresse inchangée sur un domaine ajouté après création, avec restauration des données.

## 4. Sécurité et données

L’écran utilise `manage_options`, le nonce Settings API et l’échappement des sorties. Le journal emploie le format C-10 et restaure la liste si son écriture échoue. Aucun transport ni stockage d’adresse de lecteur ajouté dans les trois classes fonctionnelles. Aucun changement du paywall. Les deux tentatives de traduction du cœur, bloquées pendant la recette HTTP, sont explicitement distinguées du comportement C-31.

**I2 — Important — `wp/tests/demo/c31-runtime.php:64`.** Le contrôle « adresse absente » ne recherche que `users.user_email`, `usermeta.meta_value` et `options.option_value`. Il omet notamment les sessions WooCommerce et les données de commande. De plus, le scénario commande appelle directement `process_customer` par réflexion : il ne traverse pas le traitement complet susceptible de manipuler les coordonnées avant le refus. La preuve ne permet donc pas de conclure « nulle part en base » pour ce point d’entrée ; aucune fuite effective n’est démontrée par cette relecture. **Correction proposée :** exercer la commande réelle avec création de compte, puis rechercher l’adresse dans les stockages effectivement utilisés par ce parcours, y compris sessions et commandes, avant nettoyage. Ajouter un témoin positif de détection et, si une persistance apparaît, placer le contrôle avant cette écriture.

## 5. Doctrine

Le standard est utilisé : filtres natifs, Settings API, règle pure séparée de l’adaptation WordPress. Les références et empreintes des sources natives sont livrées ; aucune extension tierce modifiée.

**M1 — Mineur — `wp/plugins/imagine-site/DomainesRefusesRegles.php:11`.** Les blocs conditionnels sont écrits sur une seule ligne, contrairement à PSR-12 imposé par le §5 de la doctrine. **Correction proposée :** remettre les blocs de ce fichier au format prescrit et vérifier aussi les deux adaptateurs C-31 avec le contrôle de style existant.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut fonctionnel bloquant démontré.
- **Important :** I1, preuve de sauvegarde « Mon compte » ; I2, preuve de confidentialité du parcours commande.
- **Mineur :** M1, conformité PSR-12.

Ce verdict n’est pas un GO. Le refus d’accès WSL limite le rejeu indépendant ; il n’est pas imputé au code du lot.
