# C-10 — Livraison corrigée, 23 novembre 2026

## Résultat

Menu natif français **Imagine › Réglages** installé sur `imagine-test-demo` : 3 domaines, 8 réglages, formulaire Settings API unique vers `options.php`. Corrections arbitrées de `corrections/C-10.md` et `docs/arbitrages-2026-11-23.md` appliquées, y compris les mineurs. Le raccord administratif Paiement et `imagine-site/Paywall.php` sont modifiés dans le périmètre expressément autorisé. Aucune bibliothèque close, aucun fichier C09 ni thème modifié.

- Accès : validation stricte des trois choix ; une valeur inconnue ne devient pas silencieusement un défaut.
- Paiement : les quatre réglages C05, dont le premier SEPA ; marge vide conservée, aucune valeur inventée.
- Envoi : colonnes connues, ordonnées, uniques ; exporteur C07 réellement invoqué pour l’aperçu local fictif.
- `manage_options` seulement, nonce natif ; les anciens menus C05/C06/C07 ne sont pas branchés.
- Journal après persistance, par option modifiée, qui/ID/quand UTC/avant/après ; événement indépendant non autoloadé. Si l’insertion échoue, l’écriture métier est annulée, la restauration relue, et l’administrateur prévenu. Les refus et no-op n’ajoutent aucun événement. Pas de mécanisme de reprise ; journal sans purge, cinquante derniers affichés.
- Paiement : défaut unique dérivé du moteur clos, premier refus sans `[]`, page normalisée via `lire()`. L’écran annonce explicitement le raccord Paiement encore futur. État ouverte/tranchée explicite pour les huit mentions ; façade PSR-12.
- Les trois réglages Accès sont consommés par le point de décision article/PDF du paywall. A-VIR reste fermé avec `virement_non_valide` ; `imagine_referent_abonnements` est reconnu comme équipe pour lire, sans attribution de droits éditoriaux.
- Domaines indépendants : un domaine invalide conserve intégralement sa valeur antérieure ; un autre domaine valide peut être enregistré dans le même formulaire.

## Résultats exécutés

`verification-finale.json` :

- **`composer test` : 775 tests, 33 210 assertions, zéro échec/erreur/ignoré ; `composer lint` : code 0.** PHP 8.2.33, PHPUnit 11.5.58, image existante `imagine-tests-t01:1`, réseau `none`, aucun montage/port/installation. Les **10 tests façade (67 assertions)** sont réellement découverts dans la suite `Administration`, déclarée dans `phpunit.xml`. Sortie et JUnit : `correction-final-phpunit.log` / `.xml`, reçu `correction-final-unit.json`. Le RED préalable est dans `correction-red-phpunit.log` / `.xml` : quatre régressions attendues reproduites.
- **120 contrôles C10 réussis** : 4 tests locaux de périmètre, 26 contrôles WordPress réels, 90 contrôles HTTP réels.
- **25 soumissions invalides** : choix, types/formes, clé supplémentaire ajoutée à un domaine complet, retrait d’une seule clé obligatoire, marge négative/nulle/décimale/débordante, colonne inconnue/dupliquée/vide/HTML. Conservation aussi après réglage non standard. Cas mixte vérifié : Accès invalide conservé + Paiement valide réellement modifié, un seul événement Paiement.
- Administrateur accepté ; rédacteur et gestionnaire WooCommerce refusés en HTTP 403 avec leur propre nonce valide. Abonné refusé : page 403, POST redirigé par WooCommerce vers Mon compte, aucune écriture. Anonyme refusé. Nonces absent, faux, d’une autre session : 403, aucune écriture.
- Les trois changements valides produisent trois événements exacts ; le retour aux défauts trois autres. Le cas mixte et le changement front sont également journalisés. Dernier passage HTTP : journal **58 → 68 événements**, tous conservés ; la recette native finale conserve ensuite ses propres changements d’essai. Quatre sessions détruites et destruction relue.
- **Effet front réel prouvé** : article témoin 188 fermé → ouvert pour l’équipe seulement → refermé, par POST administratif puis GET du même article. Anonyme et compte sans droit restent fermés. Option seule changée entre les GET ; date témoin 2099 inchangée. Effet CSV C07 également conservé et vérifié.
- **30 contrôles de non-régression C08 réussis**, dont garde d’accès, étanchéité, cache et coupure email/HTTP/passerelles.
- C09 conservé : **27 comptes, 13 commandes, 12 abonnements, 14 adhésions** ; identifiants de fixture comparés à l’installation C09. Aucun reseed/reset.
- Huit fichiers PHP ciblés déployés et relus : six fichiers applicatifs autorisés (dont le paywall), recette native et témoin C10 idempotent. Parsing PHP réussi, plugin C10 actif, aucun stderr PHP.
- Cliché protégé identique avant/après : comptes, rôles, contenus et métadonnées hors les deux témoins C10, tables commerciales/HPOS, fixtures B00/C08/C09, plans de lecture, MU hors-ligne, bootstrap et bibliothèques closes. Le paywall expressément modifié est contrôlé par la relecture du déploiement, pas présenté comme inchangé. Aucun secret connu dans les artefacts.

## Fichiers

Nouveaux fichiers applicatifs/documentaires :

- `wp/plugins/imagine-pilotage/imagine-reglages.php`
- `wp/plugins/imagine-pilotage/src/Administration/Reglages.php`
- `wp/plugins/imagine-pilotage/src/Administration/README.md`
- `wp/outils/demo/c10.py`
- `wp/tests/demo/c10-runtime.php`
- `wp/tests/demo/test_c10_scope.py`
- `wp/tests/demo/c10-verifier.py`
- `wp/tests/demo/c10-final.py`
- `wp/tests/demo/c10-unit.py` (nouveau banc de correction, image existante uniquement)
- `wp/tests/demo/c10-fixture.php` (nouveau témoin permanent : article 188, numéro brouillon 187)
- `wp/plugins/imagine-pilotage/tests/Administration/ReglagesTest.php` et `WordPressFictif.php` (nouveaux)
- `wp/plugins/imagine-pilotage/phpunit.xml` (déclaration de suite autorisée)
- `wp/plugins/imagine-pilotage/src/Echeancier/ReglagesAdministration.php`
- `wp/plugins/imagine-site/Paywall.php`

Réception, sources et preuves : `production/C-10/` (notamment `A-VOIR.md`, `references.md`, reçus des sources officielles, RED initial, installation, tests locaux, HTTP, vérification finale et `PRET`). Les captures intégrales HTML des sources officielles ont été supprimées après consultation ; les URL et leurs reçus sont conservés.

## Limites et écarts

1. **Effet exigé : maintenant sur l’article.** `A-VOIR.md` permet de changer un réglage puis recharger le témoin permanent. Les deux paramètres PDF sont exercés via l’adaptateur et les options natives, avec une décision robot explicitement synthétique : aucun robot réel vérifié, aucun DNS sortant ni nouveau téléchargement PDF. Paiement reste un raccord futur, annoncé dans l’écran. Les bibliothèques closes restent intactes.
2. **Navigateur authentifié non ouvert** : la connexion fonctionne mais le coffre ne possède aucun identifiant pour ce site. Aucun mot de passe n’a été saisi ni aucun cookie injecté dans le navigateur. Recette sur vraies requêtes HTTP et sessions WordPress natives éphémères ; pas de capture admin authentifiée. Validation visuelle Ced toujours attendue.
3. Les premiers essais ont montré deux particularités corrigées/qualifiées : WordPress masque un sous-menu unique de même slug (slugs parent/enfant désormais distincts), WooCommerce redirige l’abonné vers Mon compte avant `options.php` (refus réel, pas un 403 de ce contrôleur). Les preuves finales sont toutes vertes.
4. **Écart de séquencement documentaire** : la liste de références et le choix du standard ont été écrits avant le code, mais la récupération réseau des pages officielles a eu lieu après le premier squelette. Elles ont été effectivement consultées et contrôlées avant finalisation ; ne pas présenter cette chronologie comme une consultation réseau intégrale avant toute écriture. Le test écran RED a bien précédé son implémentation ; la garde stricte d’URL a aussi son RED→GREEN conservé dans la sortie d’exécution.
5. Aucun seed B00/C08/C09 ni reconstruction. Le témoin C10 possède son propre marqueur ; numéro brouillon hors kiosque et article daté de 2000 hors nouveautés. Test du rôle C09 par injection **en mémoire seulement**, définition native et comptes inchangés : sa création/affectation appartient au parent avec C09. Aucun Git, autre site, verrou, installation NUC ou rapport central ; aucun changement dans `docs/` ni `corrections/`.

## Commandes exactes de rejeu

Depuis `C:/Users/Ced/imagine`, avec l’image T01 **déjà présente** :

```bash
wsl.exe docker create --name imagine-c10-correction --label org.imagine.c10-correction=true --network none --cap-drop ALL --security-opt no-new-privileges --entrypoint sleep imagine-tests-t01:1 infinity
wsl.exe docker start imagine-c10-correction
python -B wp/tests/demo/c10-unit.py correction-final
python -B wp/outils/demo/c10.py
python -B wp/tests/demo/c10-verifier.py
python -B wp/tests/demo/c10-final.py
wsl.exe docker rm -f imagine-c10-correction
wsl.exe docker inspect imagine-c10-correction
```

Dans le conteneur : `composer test -- --log-junit /tmp/c10/result.xml`, puis `composer lint` avec `COMPOSER_ROOT_VERSION=dev-main`. Sources copiées sans montage, dépendances déjà préparées de l’image. Le dernier `inspect` doit répondre **No such object** : seul le conteneur C10 possédé est supprimé. Ne pas recréer un conteneur du même nom s’il existe déjà sans vérifier son étiquette.

`PRET` signifie prêt à relire sur démonstration fictive, pas clôture métier ou validation visuelle par Ced.
