# C-10 — Livraison et preuves

## Résultat

Menu natif français **Imagine › Réglages** réellement installé sur `imagine-test-demo` : 3 domaines, 8 réglages, formulaire Settings API unique vers `options.php`. Réutilisation des trois adaptateurs existants, sans changer leurs fichiers ni les bibliothèques closes. Bootstrap C10 distinct ; aucun fichier de `imagine-site`, du thème, de C08 ou de C09 n’a été modifié.

- Accès : validation stricte des trois choix ; une valeur inconnue ne devient pas silencieusement un défaut.
- Paiement : les quatre réglages C05, dont le premier SEPA ; marge vide conservée, aucune valeur inventée.
- Envoi : colonnes connues, ordonnées, uniques ; exporteur C07 réellement invoqué pour l’aperçu local fictif.
- `manage_options` seulement, nonce natif ; les anciens menus C05/C06/C07 ne sont pas branchés.
- Journal après persistance, par option modifiée, qui/ID/quand UTC/avant/après ; un événement indépendant non autoloadé par écriture. Les refus et les no-op ne créent aucun faux changement.
- Domaines indépendants : un domaine invalide conserve intégralement sa valeur antérieure ; un autre domaine valide peut être enregistré dans le même formulaire.

## Résultats exécutés

`verification-finale.json` :

- **96 assertions C10 réussies** : 4 tests locaux de périmètre, 13 contrôles WordPress réels, 79 contrôles HTTP réels.
- **23 soumissions invalides** : choix, types/formes, clés manquantes/surnuméraires, marge négative/nulle/décimale/débordante, colonne inconnue/dupliquée/vide/HTML ; conservation aussi démontrée après réglage non standard, pas seulement aux défauts.
- Administrateur accepté ; rédacteur et gestionnaire WooCommerce refusés en HTTP 403 avec leur propre nonce valide. Abonné refusé : page 403, POST redirigé par WooCommerce vers Mon compte, aucune écriture. Anonyme refusé. Nonces absent, faux, d’une autre session : 403, aucune écriture.
- Les trois changements valides produisent trois événements exacts ; le retour aux défauts trois autres. Dernier passage : journal de **12 à 18 événements**, tous conservés. Quatre sessions de test détruites et destruction relue.
- Effet réel prouvé : neuf colonnes CSV → `ville,destinataire,pays` et ligne fictive correspondante, produites par `ExportCsv::lignes` avec le réglage relu ; retour aux neuf colonnes vérifié.
- **30 contrôles de non-régression C08 réussis**, dont garde d’accès, étanchéité, cache et coupure email/HTTP/passerelles.
- C09 conservé : **27 comptes, 13 commandes, 12 abonnements, 14 adhésions** ; identifiants de fixture comparés à l’installation C09. Aucun reseed/reset.
- Six fichiers PHP déployés (5 fichiers d’administration dont 3 adaptateurs existants identiques, 1 recette) : parsing PHP et SHA-256 relus exactement, plugin C10 actif. Aucun stderr PHP.
- Empreinte protégée identique avant/après : comptes, rôles, contenu, métadonnées, tables commerciales/HPOS, fixtures B00/C08/C09, plans de lecture, MU hors-ligne, bootstrap/paywall et bibliothèques closes. Aucun secret connu trouvé dans les artefacts C10.

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

Réception, sources et preuves : `production/C-10/` (notamment `A-VOIR.md`, `references.md`, reçus des sources officielles, RED initial, installation, tests locaux, HTTP, vérification finale et `PRET`). Les captures intégrales HTML des sources officielles ont été supprimées après consultation ; les URL et leurs reçus sont conservés.

## Limites et écarts

1. **Effet choisi : C07, pas une ouverture d’accès.** Le raccord C08 ne consomme pas encore l’option C06 dans son appel au moteur ; il conserve les défauts existants. Aucun cycle découverte, téléchargement PDF protégé ou paiement n’est présenté comme livré par C10. Le branchement futur des consommateurs reste distinct de l’écran, comme le branchement bancaire C05.
2. **Navigateur authentifié non ouvert** : la connexion fonctionne mais le coffre ne possède aucun identifiant pour ce site. Aucun mot de passe n’a été saisi ni aucun cookie injecté dans le navigateur. Recette sur vraies requêtes HTTP et sessions WordPress natives éphémères ; pas de capture admin authentifiée. Validation visuelle Ced toujours attendue.
3. Les premiers essais ont montré deux particularités corrigées/qualifiées : WordPress masque un sous-menu unique de même slug (slugs parent/enfant désormais distincts), WooCommerce redirige l’abonné vers Mon compte avant `options.php` (refus réel, pas un 403 de ce contrôleur). Les preuves finales sont toutes vertes.
4. **Écart de séquencement documentaire** : la liste de références et le choix du standard ont été écrits avant le code, mais la récupération réseau des pages officielles a eu lieu après le premier squelette. Elles ont été effectivement consultées et contrôlées avant finalisation ; ne pas présenter cette chronologie comme une consultation réseau intégrale avant toute écriture. Le test écran RED a bien précédé son implémentation ; la garde stricte d’URL a aussi son RED→GREEN conservé dans la sortie d’exécution.
5. Les corrections B00/B01 non arbitrées n’ont pas été appliquées, B00 n’a pas été relancé. Aucun Git, autre site, verrou ou rapport global ; aucun changement dans `docs/` ni `corrections/`.

`PRET` signifie prêt à relire sur démonstration fictive, pas clôture métier ou validation visuelle par Ced.
