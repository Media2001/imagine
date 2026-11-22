# C-05 — proposition d’échéancier, reprise du 22 novembre 2026

**Statut : corrections de fusion 1–5 appliquées ; proposition et prototype à relire.** Quatre échéances par bloc de quatre numéros, pas par fenêtre anniversaire. Aucun branchement sur un site existant, aucun encaissement ni GO financier. Remise courante : `corrections-22nov-1458.md` et `replays/fusion-22nov-1458/`. Les reçus `preuves/` et les notes des remises précédentes sont historiques.

## 1. Unité d’engagement retenue : quatre numéros

L’arbitrage du 22/11 corrige expressément celui du 21/11 : le papier se compte par blocs de quatre numéros (§3.5), une fraction par numéro (§3.4), tandis que le numérique conserve sa fenêtre de date à date. L’anniversaire numérique ne déplace ni n’ajoute un paiement.

**Contre-exemple entièrement fictif, issu du calendrier de test de C-01 :** clôtures régulières les 10 janvier, avril, juillet et octobre, sorties les 20 ; marge de démonstration 7 jours civils, donc dates communes les 3.

- Commande le **9 avril 2027 à 12 h Bruxelles** : C-01 attribue avril, juillet, octobre 2027 et janvier 2028.
- Année initiale : 9 avril 2027, 3 juillet 2027, 3 octobre 2027, 3 janvier 2028. Le premier numéro est payé à la commande ; on ne rajoute pas le 3 avril passé.
- Bloc suivant C-01 : avril, juillet, octobre 2028 et janvier 2029, tous aux communes des 3.
- La première commune reconduite est le **3 avril 2028**, avant l’anniversaire du 9 avril. La fenêtre initiale contient **cinq dates**, mais chaque bloc conserve exactement quatre créances. C’est désormais accepté, sans exception de date ni de marge.

Le balayage des 365 jours fictifs accepte les **28 commandes** dont la première fenêtre contient cinq dates avec marge 7. Ce n’est pas une cinquième position dans un bloc. Aucun numéro substitué, aucune modification de C-01.

Le refus `HORS_ENGAGEMENT` est supprimé : il imposait l’ancienne unité de comptage. Le moteur conserve ses refus de calendrier incomplet et de dates non croissantes. Les valeurs de réglage non décidées par le client ne bloquent plus ce prototype (§6).

## 2. Standard examiné avant le sur-mesure

La référence Woo permet des périodes en jours, semaines, mois et années.[3] Mais l’alignement natif du premier renouvellement ignore l’intervalle supérieur à une unité : l’exemple officiel d’une inscription le 6 avril, tous les trois mois, donne le 1er mai, non le 1er juillet.[5] Les deux phrases de cet exemple sont conservées intégralement et séparément dans `sources/review-fusion-22nov-1458.json` (M3), avec URL finale, HTTP, heure et empreinte. Il ne suffit donc pas de cocher « trimestriel synchronisé ».

Les fonctions documentées `update_dates`, `can_date_be_updated` et les relations de commandes permettent un raccord fin plutôt qu’un nouvel encaisseur.[1] Une action de renouvellement peut être déclenchée sur calendrier ou explicitement hors calendrier ; l’action spécifique de passerelle est distincte.[4]

### Deux voies possibles — comparaison de conception, pas promesse de couverture native

| Aspect | A — Cadence courte, prochaine date pilotée | B — Support annuel et trois appels complémentaires |
|---|---|---|
| Support Woo | Abonnement sans expiration automatique, période technique de trois mois ; chaque prochain paiement est remplacé par la date du plan C-01, via l’API de dates. La cadence n’est pas la durée d’engagement.[1][3] | Abonnement de période annuelle ; trois actions supplémentaires doivent créer des commandes reliées, ou appeler explicitement le cycle de renouvellement. Ces actions hors calendrier sont possibles, mais leur combinaison n’est pas un fractionnement annuel natif documenté.[3][4] |
| Ce que verrait l’abonné | Prochaine date et commandes natives ; le libellé technique trimestriel ne doit pas laisser croire à une résiliation trimestrielle. Un récapitulatif des quatre positions et de l’anniversaire reste à raccorder. Le compte rendu visuel n’est pas implémenté ici.[2] | L’annuel est plus proche du contrat affiché, mais les trois sommes complémentaires et leur lien à la dette annuelle exigent aussi un récapitulatif spécifique. Ne pas afficher une charge annuelle entière en plus de trois fractions. |
| Paiement échoué | Pas de rang confirmé ni paiement supplémentaire sur échec. Les créances restantes suivent le réglage du §6 ; droits et grâce restent séparés. Les retries automatiques ont leurs prérequis.[2][6] | Même politique à appliquer aussi aux commandes complémentaires, faute de quoi elles divergent du support annuel. Ce raccord n’a pas été exercé. |
| Reconduction | Quatre numéros C-01 suivants, toutes les dates communes, même avant l’anniversaire numérique. Pas de débit supplémentaire pour l’anniversaire. | L’annuel natif ne coïncide généralement pas avec la première commune. Il faut déplacer l’appel ou séparer contrat et première fraction ; complexité supplémentaire. |
| Comptage d’engagement | Quatre identités `(abonnement, cycle, rang)` attachées à quatre numéros, dont l’initial au cycle 1. Anniversaire et opposition à reconduction sont indépendants de l’intervalle technique. | Même compteur nécessaire ; le nombre de commandes de renouvellement ne suffit pas à distinguer appel annuel et fraction. |
| Côté Odoo | Proposition : chaque commande porte cycle, rang, numéro et date théorique ; paiement validé et engagement annuel sont des événements distincts, à passer ensuite par la file C-04. Aucun événement Odoo n’est émis ici ; champs, facturation et étalement restent à confirmer par Step. | Même données, avec en plus une distinction stricte entre support annuel et appels complémentaires pour éviter de compter cinq créances ou de facturer deux fois la somme annuelle. Aucun connecteur n’est ajouté. |

**Voie A recommandée.** Un seul flux natif de renouvellements et une seule prochaine action ; B multiplie les circuits sans bénéfice pour le compteur de numéros. Cette recommandation reste un prototype à relire, pas un encaisseur de production ni un GO.

## 3. Mécanisme limité et exercice réel

`Planificateur` reçoit un `Numeros\Moteur`, une `Annee` C01 et une marge explicite. Aucun calendrier, horloge ou WordPress recalculé : **seul C01** choisit les quatre numéros et leurs communes. Première position du bloc initial à la commande ; toutes les autres communes. Chaque bloc précédent est validé récursivement ; la dernière date du bloc précédent initialise le contrôle strict du suivant. Une égalité rang 4/rang 1 refuse `DATES_NON_CROISSANTES` avant retour du plan, sans déplacer une commune ni imposer de borne anniversaire. Calendrier incomplet également refusé. Le paramètre `finEngagement` est retiré : l’API est `planifier(Annee $annee, ?int $margeJours = null)`. Une année non activée, dont `finNumerique()` est null, reste projetable sans TypeError ; ce n’est pas une autorisation de débit ou d’expédition. Activation numérique et bloc papier restent distincts. Marge absente : `MARGE_OBLIGATOIRE` avant tout résultat.

`RaccordManuel` ne contient aucune logique de calendrier et ne s’enregistre sur aucun hook. Il utilise l’API officielle de dates en UTC, après vérification de modifiabilité.[1] Il refuse tout abonnement sans marqueur fictif C05, sans drapeau explicite de renouvellement manuel ou avec identifiant de passerelle non vide. Aucun booléen de mode staging n’est employé pour autoriser un paiement.

Le pilote de la fixture applique le raccord après chaque validation locale réussie, puis ne traite **que** l’action native de l’abonnement fictif concerné. L’absence de validation n’est jamais comptée comme paiement. Une deuxième application de la même date conserve une seule action en attente. Le dernier appel est stoppé à la fin de l’horizon démontré, sans annuler l’abonnement ni effacer de dette.

Un futur raccord autonome devra conserver durablement le curseur, verrouiller les concurrences, gérer échec/reprise/opposition à reconduction et empêcher une avance anticipée. Il ne suffit pas de brancher aveuglément `woocommerce_subscription_payment_complete` : la section officielle de ce hook signale que les changements de dates liés aux renouvellements anticipés sont traités différemment ; elle déconseille de se fier à cette action pour capturer la prochaine date de paiement.[4] Le nom du hook et son avertissement sont conservés dans `sources/review-fusion-22nov-1458.json` (C05-02), avec contrôle qu’ils viennent de la même section, distinctement de M3. **Ce branchement complet n’est pas livré ni déclaré prouvé.** Le prototype exerce l’API et les vraies créations manuelles demandées, pas un moteur de production.

Le renouvellement manuel natif demande normalement une action du client ; il ne constitue pas un prélèvement automatique.[2] Les reprises automatiques ont leurs prérequis et ne sont pas démontrées par ce banc manuel.[6]

## 4. Preuve acquise, sans gonfler sa portée

- PHPUnit : la suite `Echeancier` est incluse dans le `composer test` standard du XML racine, avec les cinq suites voisines. Les compteurs réels du nouveau JUnit sont dans `corrections-22nov-1458.md` et `replays/fusion-22nov-1458/final.xml`. Les 365 dates, veille/jour/lendemain, cinq dates acceptées et total de 28 fenêtres, calendriers incomplets, fuseaux/29 février, réglages/entrées restent testés ; s’ajoutent jonction égale refusée, cas 09/04 valide, API sans borne et refus admin traduit. Aucun banc unitaire autonome ne subsiste.
- Vrais **Subscriptions 9.4.1**, WordPress **7.0.9**, WooCommerce **11.1.1**, PHP **8.2.36** ; quatre commandes pour **chacun** des stockages classique et HPOS : 20 février et 9/10/11 avril 2027 (veille/jour/lendemain de clôture).
- **8 abonnements, 8 initiales, 56 vraies commandes de renouvellement, 64 commandes au total**. Deux blocs de quatre positions par scénario. **352 contrôles par stockage, 704 au total**, dont les réglages administratifs, le vrai `wp_die` traduit et le refus de jonction égale avant création de commandes ; distincts des 12 contrôles d’enveloppe Python. Ce ne sont pas 704 parcours financiers indépendants.
- Les dates enregistrées de `next_payment` et des actions natives correspondent exactement aux dates C-01, avec conversions hiver/été. Les actions futures sont exécutées explicitement en accéléré ; les confirmations locales ont l’heure réelle d’exécution. **Ce n’est pas une attente de deux ans, ni une preuve de débit bancaire à une date future.** Les reçus séparent date théorique, date native d’action et date de validation Woo.
- Le scénario du 9 avril crée réellement les huit positions et vérifie cinq dates dans sa première fenêtre, en classique et HPOS. Douze combinaisons administratives par stockage sont persistées puis relues et exercées sur le moteur et les projections. Le formulaire est rendu par WP (nonce, champs et capacité), sans sauvegarde HTTP ni inspection visuelle revendiquée.

Reçus courants : `replays/fusion-22nov-1458/final.xml`, `final.json`, `final-e2e-result.json`, `final-e2e.json`, journaux et `verification.json`. Les RED, GREEN intermédiaires et historiques sont conservés sans écrasement. Commandes et limites : `corrections-22nov-1458.md`, `wp/tests/echeancier-runner/README-corrections.md`.

## 5. Isolation et périmètre

Deux conteneurs possédés distincts : PHP/Composer (dépendances publiques verrouillées pendant préparation seulement, réseau détaché avant tests) et e2e (réseau `none` dès création). Images synthétiques existantes, aucun pull. Seul le ZIP Subscriptions autorisé est lu dans la bibliothèque de paquets, avec empreinte vérifiée ; ni ZIP ni licence dans le dépôt. Memberships non utilisé. Aucun montage/volume/port, capacités supprimées ; MariaDB e2e sur socket Unix, aucun serveur web. Emails et HTTP bloqués dans la fixture. Aucune archive de site, aucun compte réel, aucun outil installé sur l’hôte, aucune opération Git ni modification de staging. Les deux suppressions et absences exactes sont vérifiées dans le nouveau paquet. Verrou du parent intact.

## 6. Trois réglages, aucune question bloquante pour le prototype

`Reglages` est pur PHP. `ReglagesAdministration` fournit la Settings API [7][8], option `imagine_c05_reglages`, sans exposition REST :

| Clé | Défaut | Autre valeur / effet |
|---|---|---|
| `marge_jours` | **null, aucun défaut** | Entier positif en jours civils. Vide = non configuré, moteur bloqué. 1/3/7/30 testés, pas recommandés ; 0, négatif, décimal, texte, booléen, tableau et dépassement d’entier refusés. |
| `apres_rejet` | `restent_dues` | `annuler_restantes` : ne plus devoir les rangs impayés après rejet, sans effet sur les confirmations payées. Sans rejet, pas de suppression. |
| `tarif` | `fige_bloc` | `courant_impayes` : tarif courant pour les seuls rangs non payés. Hausse/baisse, nouvelle capture par bloc et interaction avec rejet testées. |

`montantsRestants` renvoie une **projection** en centimes par rang. L’appelant fournit la somme par échéance figée à l’ouverture du bloc, le tarif courant et les seuls rangs confirmés payés. Pas de division d’un annuel, taxe, port, remboursement ou remise Woo exécutée. Le nouveau bloc capture sa propre somme. Aucun changement de réglage ne réécrit une commande payée. L’accès suit séparément le délai de grâce, sans nouveau choix C05.

### Seam parent, sans modifier le bootstrap commun

Après l’autoload, le parent pourra appeler une fois :

```php
(new Imagine\Pilotage\Echeancier\ReglagesAdministration())->enregistrer();
```

Cela enregistre `admin_init`, le sous-menu Woo et la capacité `manage_woocommerce` du groupe. Formulaire `options.php`, nonce et contrôles de capacité standards WP [7], sorties échappées, libellés traduisibles. Une saisie invalide conserve intégralement l’option précédente avec erreur ; une option persistée corrompue échoue fermée à la lecture. La marge peut rester vide mais interdit toute planification.

```php
$reglages = (new Imagine\Pilotage\Echeancier\ReglagesAdministration())->lire();
$positions = $planificateur->planifier($anneeC01, $reglages->margeJours);
$restant = $reglages->montantsRestants($centimesFiges, $centimesCourants, $rangsConfirmes, $rejet);
```

Ce seam est activé explicitement dans la fixture, **pas** dans le bootstrap partagé. Il ne déploie aucun écran sur le vrai site. Aucun choix métier restant ne bloque la remise de code ; une marge effective reste à renseigner avant usage. PRET n’est ni clôture par les deux relecteurs, ni validation visuelle, ni GO réel.

## Sources

[1] https://woocommerce.com/document/subscriptions/develop/functions
[2] https://woocommerce.com/document/subscriptions/renewal-process
[3] https://woocommerce.com/document/subscriptions/creating-subscription-products
[4] https://woocommerce.com/document/subscriptions/develop/action-reference
[5] https://woocommerce.com/document/subscriptions/billing-date-alignment/creating-an-aligned-subscription-product
[6] https://woocommerce.com/document/subscriptions/failed-payment-retry
[7] https://developer.wordpress.org/plugins/settings/settings-api/
[8] https://developer.wordpress.org/reference/functions/register_setting/

Huit sources officielles relues le 22/11 : URL finale, HTTP 200, heure, empreinte et court extrait dans `sources/review-2026-11-22.json`. Complément distinct M3/[5] et C05-02/[4] : `sources/review-fusion-22nov-1458.json`. Les collectes antérieures restent historiques, pas réécrites.

## Q1 maintenue pour le futur parcours SEPA

Faut-il appliquer aussi une marge de confirmation au premier numéro SEPA quand la commande arrive juste avant clôture ? Aucune décision financière nouvelle ni politique SEPA n’est créée ici : le paiement initial du prototype manuel reste à la commande. Q2 n’est pas reposée comme blocage : le défaut `restent_dues` est déjà explicite dans les arbitrages du 22/11. L’item 6 de la fusion est transmis à Claude dans la note dédiée ; aucun fichier `docs/` modifié.
