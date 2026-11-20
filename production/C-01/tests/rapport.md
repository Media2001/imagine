# C-01 — rapport des tests exécutés

## Résultat final (20 novembre 2026)

**39 tests PHPUnit, 101 assertions, 39 réussis, 0 échec, 0 erreur, 0 ignoré.**
Exécution finale : `2026-11-20T14:28:39.994455+00:00` (15 h 28 à Bruxelles).
PHP **8.2.36**, PHPUnit **11.5.58**, Composer **2.11.2**.

Commandes réellement exécutées dans un conteneur jetable neuf :

| Contrôle | Résultat |
|---|---|
| `composer install --no-interaction --no-progress --prefer-dist --no-scripts --no-plugins` | code 0, depuis `composer.lock` |
| `composer test` (avec export JUnit) | code 0, 39 tests / 101 assertions |
| `composer lint` (PSR-12, sources et tests) | code 0, aucune erreur ni avertissement |
| `php -l` sur chaque fichier PHP des sources et tests | code 0, aucune erreur de syntaxe |
| `composer validate --strict --no-check-publish` | code 0 |
| Correspondance SHA-256 local → conteneur | vérifiée avant exécution ; 14 fichiers de bibliothèque |
| Vérification locale après passage | les mêmes 14 empreintes et celle du lanceur correspondent |
| Nettoyage | conteneur final supprimé, absence relue ; aucun état de runner restant |

## Ce qui a effectivement été exercé

- Exemple exact du 8 octobre 2026 (171–174, HS été 2027) et renouvellement
  d'octobre 2027 (175–178, HS été 2028).
- Veille, début/fin du jour de clôture inclus, lendemain, intervalle
  clôture–sortie, décembre/janvier et conversion UTC/Bruxelles.
- Calendrier vide/partiel, dernier non résolu, compte de réguliers dus,
  renouvellement dont l'ancrage manque, résolution après calendrier complété.
- Paiement et mandat, absence d'activation, ouverture à l'instant transmis,
  anniversaire exclusif et conservation de la fin après réactivation.
- Suspension, réactivation, absence de rattrapage d'un régulier/hors-série fermé,
  conservation d'un ancien envoi, activation/réactivation exactement à clôture.
- Quatre échéances par régulier, marges distinctes, marge nulle/négative refusée,
  repérage d'une échéance passée et passage à l'heure d'été en jours civils.
- Restants connus, hors-série compris, non-sortis, avant commande et après fin
  de la série ; aucun rattrapage d'un numéro fermé pendant suspension.
- Modification future recalculant sélection/dates d'échéance, ancienne version
  immuable, refus du passé/rétroactivité/numéro inconnu/type changé et du déplacement
  d'un futur au travers d'un numéro déjà clôturé.
- Invariants de dates/identifiants/historique, normalisation des fuseaux,
  classes métier `readonly` et refus explicite de trancher le 29 février.

## Isolement et preuve

Le runner final utilise l'image synthétique existante
`sha256:b2ffa6ad01ffacc6d31b176232c8d0779c0320daba381e05cbbd80f56d5327a0`.
Entrée remplacée par `sleep` ; ce seul processus de fond a été vérifié avant la
suite. Ni WordPress ni base démarré, aucun site réel ou staging Imagine utilisé,
aucun montage/volume/port. Toutes capacités retirées, `no-new-privileges`.
Le réseau de préparation Composer est déconnecté **avant** PHPUnit, syntaxe et
lint. La suite finale a été rejouée depuis une préparation neuve, pas seulement
avec le vendor d'un cycle précédent.

Preuves principales : `final.log`, `final.xml`, `final.json`, `final-lint.log`,
`final-composer-validate.log`, `composer-install.log`, `preparation.json`,
`cleanup.json`. `final.json` lie les sources et le lanceur par SHA-256.
Les journaux `red-*`/`green-*` conservent les cycles observés : API initialement
absente puis implémentée, et vrais échecs de bornes/invariants/fuseau corrigés.
Ils ne doivent pas être pris pour l'état final.

## Incidents et limites

Le premier essai sur l'image PHP CLI minimale a échoué faute d'extracteur ZIP
(`composer-install-missing-unzip.log`). Une tentative d'ajout de l'extracteur
**dans le conteneur jetable seulement** a été refusée par ses capacités retirées ;
les protections n'ont pas été élargies. Les conteneurs de ces essais ont été
supprimés. Le runner final réutilise l'image synthétique déjà outillée ; aucun
outil n'a été installé sur Windows ou WSL. Les particularités de transmission
WSL (`$` PHP transmis désormais sur stdin, colonne PID requise par Docker top)
ont également été corrigées puis le runner final intégralement réexécuté.

Aucune recette de `docs/recette/` automatisée ou modifiée. Pas de test de tunnel,
WooCommerce, prélèvement, export figé en base, livraison postale ou site réel.
Les arbitrages de `../notes.md` restent ouverts. Le résultat autorise un marqueur
**PRET à relire**, jamais un GO client ni un déploiement.
