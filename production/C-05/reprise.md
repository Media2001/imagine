# C-05 — réception de la reprise du 22 novembre 2026

**Fait :** Option A, réglages purs et adaptation d’administration dédiée, proposition et tests adaptés, preuve sur vrai Subscriptions.
**Prêt à relire :** remise C05 ; PRET seulement après vérification finale des reçus, sources et nettoyage.
**À arbitrer :** aucun choix métier bloquant ; la marge doit être renseignée par l’administration avant usage, sans défaut.
**Bloqué :** rien pour le prototype demandé ; intégration commune et tout réel hors du lot.
**Ensuite :** parent et relecteurs ; aucun autre lot commencé par cet agent.

## Références et interprétation

Consigne permanente, doctrine du 22/11, A-FAIRE, brief C05, décisions/arbitrages du 22/11 et notes/proposition antérieures lus intégralement. Aucune correction C05 ni relecture C05 présente au moment de la reprise. Six références Woo préexistantes relues, deux références Settings API WP ajoutées ; courts extraits et empreintes dans `sources/review-2026-11-22.json` (huit HTTP 200).

J’ai compris quatre paiements comme quatre créances par bloc C01 de quatre numéros, pas comme un filtre dans l’année numérique. La commande du 9 avril garde la première commune reconduite au 3 avril : cinq dates dans sa fenêtre, quatre dans chaque bloc. Les 28 cas quotidiens anciennement refusés avec marge fictive 7 sont acceptés. Le paramètre historique `finEngagement` reste compatible positionnellement mais ne borne plus les paiements. Les sept fichiers PHP C01 sont vérifiés identiques à la preuve historique de référence.

Réglages : marge civile positive sans défaut (absence = refus du moteur) ; rejet `restent_dues` par défaut / `annuler_restantes` ; tarif `fige_bloc` par défaut / `courant_impayes`. Chaque choix, leurs croisements, hausse/baisse, rangs payés et valeurs invalides sont testés. `montantsRestants` ne fait qu’une projection en centimes, sans modifier les commandes Woo, rembourser ou calculer les droits. Le futur appelant conserve la somme figée par bloc ; les droits suivent séparément la grâce.

## Résultats canoniques

- `preuves/reprise-final-unit-result.json` : **380 tests, 2 289 assertions, 0 échec**, suite autonome PHP (pas PHPUnit). 365 jours et tests limites, numéros C01, validation stricte et réglages.
- `preuves/reprise-final-e2e-result.json` : classique + HPOS, quatre scénarios par stockage, deux blocs chacun ; **8 abonnements, 8 initiales, 56 vrais renouvellements, 64 commandes**. **700 contrôles de scénario/administration**, plus **12 contrôles d’enveloppe**. Veille/jour/lendemain de clôture compris ; cinq dates observées dans la première fenêtre du scénario veille sur chaque stockage.
- `preuves/reprise-final-unit.json` et `reprise-final-e2e.json` : empreintes copiées et vérifiées, syntaxe PHP, commandes et isolation avant/après.
- `preuves/cleanup.json` : suppression du conteneur possédé. `preuves/verification.json` : agrégation mécanique, empreintes actuelles de remise et absence exacte des ressources C05 connues.

TDD conservé : `reprise-red-option-a` échoue sur les 29 cas attendus puis GREEN ; RED/GREEN marge, rejet, tarif et décodage d’option distincts ; `reprise-red-admin` échoue sur la classe d’administration absente puis `reprise-green-admin` réussit dans les deux stockages. Les preuves du 21/11 restent historiques ; `notes.md` les désigne comme telles.

## Seam parent et limites

Aucun bootstrap, Composer ou README partagé modifié. L’adaptation est dans `src/Echeancier/ReglagesAdministration.php` ; après autoload, appel parent unique :

```php
(new Imagine\Pilotage\Echeancier\ReglagesAdministration())->enregistrer();
```

La fixture active ce seam explicitement, exerce la Settings API réelle, le formulaire (nonce/champs/refus anonyme), les douze combinaisons persistées/relues par stockage et leurs effets sur le moteur/projections. Pas de requête de sauvegarde HTTP ni inspection visuelle revendiquée. Aucun hook de paiement autonome de production livré ; curseur durable, concurrence, reprise, opposition à reconduction et somme figée persistée restent au futur branchement prévu par la file.

Vrais Subscriptions 9.4.1 / Woo 11.1.1 / WP 7.0.9 / PHP 8.2.36 dans une image synthétique déjà disponible. Actions futures natives vérifiées puis exécutées explicitement en accéléré ; confirmations locales à l’heure réelle, aucun débit bancaire. Pas de test de passerelle/retry bancaire/Odoo/compte abonné/taxe/port ni de suite globale des autres lots. Syntaxe PHP vérifiée ; aucun nouvel outil PHPCS/Composer installé.

Aucun PHP Windows, Git, archive Imagine, donnée/compte réel, déploiement ou installation hôte. Un seul conteneur possédé, réseau none, sans montage/volume/port, capacités supprimées, MariaDB sur socket, HTTP et emails bloqués. Verrou du parent, rapports et ressources A01/C06 intacts. PRET n’est pas une clôture par les relecteurs ni un GO réel.

Incidents non bloquants : `web_extract` échoue (backend search-only), les huit lectures publiques officielles sont donc faites en HTTP direct, sans configuration modifiée. `execute_code` est interdit en session unattended et n’a rien exécuté ; les outils normaux ont servi aux éditions, conformément au diagnostic. Aucune sortie de l’un de ces appels échoués n’est présentée comme une preuve.

## Revérification parent

Depuis `C:/Users/Ced/imagine` :

```bash
python wp/tests/echeancier-runner/verify.py
```

Rejeu Docker complet avec fermeture même sur échec : `wp/tests/echeancier-runner/README.md`. Ne pas écraser les noms de reçus à conserver.
