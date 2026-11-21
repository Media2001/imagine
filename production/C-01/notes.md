# C-01 — moteur de la règle des numéros

## Périmètre livré

Bibliothèque PHP 8.2 pure dans `wp/plugins/imagine-pilotage/`, objets `readonly`,
types stricts, namespace `Imagine\Pilotage\Numeros`. Aucune horloge lue dans le
moteur, aucune base, aucun hook WordPress, aucune dépendance WooCommerce, aucun
paiement, montant ou transmission comptable. Les contrats et leurs transitions
sont immuables ; les dates sont des `DateTimeImmutable` en `Europe/Brussels`.

Le moteur fournit : calendrier régulier/hors-série, quatre réguliers, premier et
dernier connus, dette de réguliers non résolus, hors-série, renouvellement lié à
l'année précédente, accès numérique sur activation, suspension/réactivation
historisées, droits à la clôture, restants et échéances à marge obligatoire.
Le README de la bibliothèque documente l'API et ses préconditions.

Le calendrier de test est fictif : rythme trimestriel civil, n° 166 en
octobre-décembre 2025, 170 en octobre-décembre 2026, 171 en janvier-mars 2027 ;
hors-série d'été. Les jours de sortie/clôture ne viennent pas d'Imagine.
Les deux exemples du cahier des charges sont testés : commande du 8 octobre 2026
→ 171–174 + HS-2027 ; renouvellement d'octobre 2027 → 175–178 + HS-2028.

## À arbitrer par Ced

Les **quatre interprétations prescrites par le brief**, non des décisions nouvelles :

1. **Quel hors-série ?** Valider le premier dont la liste reste ouverte au début
   de l'année d'abonnement : oui/non ? Isolé dans `Moteur::horsSerie`.
2. **Jour de clôture inclus.** Valider la fermeture dès minuit, date incluse,
   à Bruxelles : oui/non ? Isolé dans `Numero::estCloture`. Une activation ou
   réactivation à cet instant arrive trop tard ; le droit historique est pris
   juste avant cette borne dans `Moteur::aDroit`.
3. **Calendrier incomplet.** Valider la conservation de quatre réguliers dus,
   en exposant ceux connus et le nombre non résolu, sans inventer d'identifiant :
   oui/non ? Isolé dans `Moteur::numeros` et `nonResolus`. Le premier peut être
   connu sans le dernier ; le dernier reste `null` avant le quatrième. Une
   année renouvelée reste entièrement non résolue si la fin précédente manque.
   Un hors-série inconnu reste une dette séparée, représentée par `null`.
4. **Fin numérique.** Valider un an jour pour jour après l'ouverture, fin
   exclusive : oui/non ? Isolé dans `Annee::finNumerique`.

Points complémentaires non tranchés, **sans automatisme financier ajouté** :

- **29 février** : décision écrite de Ced du 21/11 : fin au 28 février de l'année suivante, à l'heure d'ouverture, borne exclusive ; ouverture immédiate fonctionnelle.
- **Marge de prélèvement** : valider une marge obligatoire, positive, en jours
  civils : oui/non ? Valeur à fournir par l'administration ; 7 et 3 ne sont que
  des valeurs de tests, aucune marge par défaut n'est décidée.
- **Échéance déjà passée à la commande/réactivation** : bloquer son lancement
  automatique tant que l'administration n'a pas fixé la conduite : oui/non ?
  Le lot ne fait que la signaler par `estPassee(date)` ; aucun débit ni report.
- **Restants** : valider la date de sortie comme repère théorique faute de suivi
  postal : oui/non ? Le moteur exclut à partir du jour de sortie, ne prétend pas
  savoir si le colis est livré. Les droits de futurs numéros d'un contrat
  actuellement suspendu sont des projections à son état actuel.
- **Suspension** : l'accès numérique est coupé via `accesNumerique → estActive`, confirmé par Ced le 21/11 (docs/arbitrages-2026-11-21.md, C-01/1). Le calendrier contractuel initial de quatre réguliers est
  conservé ; aucune substitution, prolongation, remise ou redistribution des
  échéances n'est décidée ici. Faut-il prévoir une compensation des numéros
  exclus dans un autre lot : oui/non ? Le non-rattrapage prescrit est testé.

## Interprétations techniques et frontières

- Une commande seule n'ouvre pas l'accès. `activer` exige un événement typé
  paiement ou mandat ; sa vérification réelle appartient au futur adaptateur.
- Les projections de contrat (`numeros`, etc.) se distinguent du droit d'envoi
  (`aDroit`). À clôture passée, ce dernier relit l'historique et non le dernier
  état du contrat ; une suspension ultérieure n'efface donc pas l'envoi passé.
- `Calendrier::modifier` est la voie de modification : refuse passé, rétroactivité,
  changement de type et déplacement au travers d'un numéro déjà clôturé.
  Refaire le moteur avec le résultat recalcule les projections futures et les
  échéances. Le constructeur hydrate un calendrier de confiance ; pas de base
  ni de liste d'envoi persistante/figée écrite par ce lot.
- Le calendrier fourni est une liste exhaustive de parutions connues jusqu'à
  son horizon. Les identifiants sont opaques : aucun calcul « id + 1 » ne crée
  un numéro. Un trou dans un calendrier prétendument exhaustif doit être corrigé
  par son fournisseur ; ce moteur ne sait pas déduire une parution absente.
- Ce lot répond à la commande explicite de moteur pur C-01. Il ne tranche ni la
  couverture native des extensions (A-00), ni leur branchement (lot en attente).
- Les cas R-02, R-16, R-20, R-32, R-34 restent des **cas d'acceptance non validés**.
  Leur catalogue est inchangé et aucun parcours de recette n'est automatisé.
  Les tests présents sont uniquement les tests unitaires métier demandés par
  C-01 ; aucun tunnel, export réel ou back-office n'est prétendu testé.

## Corrections et traçabilité — 21 novembre 2026

Décisions écrites lues après mise à jour de la file à 10 h 25 : clôtures régulières monotones exigées à la construction (donc à modifier), erreur nommant les deux numéros ; fin 29/02 au 28/02 ; suspension numérique conservée. Aucun arbitrage inventé. Tests nouveaux : CorrectionsTest (construction, modification refusée, séquence/dernier/échéances inchangés, paiement et mandat le 29/02, lendemain, suspension, avant/à/après fin). Fixture simplifiée sans changement de dates.

Règle → source → test :
- Calendrier et modification → brief 1, §3.4/3.5 + décision Ced C-01/3 → InvariantsTest, CorrectionsTest.
- Ouvrir/activer, accès numérique → brief 5, §3.5 ; suspension §3.8 confirmée C-01/1 ; anniversaire C-01/2 → MoteurTest::testAccesAttendPaiementOuMandatEtExpireALAnniversaire, CorrectionsTest.
- numeros/premier/dernier/nonResolus → brief 2/3, §3.5 ; dette provisoire prescrite par brief → MoteurTest::testExempleDuCahierDesCharges, testRenouvellementEtDetteSansInventerUnNumero.
- horsSerie → brief 4, §3.5 ; premier HS ouvert reste interprétation à confirmer → mêmes tests.
- renouveler → brief 6, §3.5 → testRenouvellementEtDetteSansInventerUnNumero.
- echeances/estPassee → brief 7, §3.6, marge non fixée → testEcheancesParNumeroAvecMargeEnJoursCivilsEtRestants, InvariantsTest.
- restants → brief 8, §3.7 ; sortie comme repère provisoire → testEcheancesParNumeroAvecMargeEnJoursCivilsEtRestants.
- aDroit/suspendre/reactiver/estActive → brief 9 et cas limites, §3.13/3.8 ; clôture incluse prescrite par brief → testSuspensionEtReactivationNeRattrapentPasUneListeCloturee, testActivationOuReactivationALaClotureEstTropTard.

Preuves fraîches tests-21nov/ : Numeros seul 42 tests / 121 assertions (numeros.xml : aucune autre suite), puis suite complète 175 / 19 911 ; PHPUnit, PHPCS, syntaxe, Composer strict et vérificateur ciblé PASS. Conteneurs supprimés. Historiques tests/ conservés. Questions absentes du fichier de décisions toujours ouvertes, aucun branchement/GO.

## Tests et preuves

Lanceur autonome : `wp/tests/numeros-runner/run.py`. Il réutilise une image
publique synthétique déjà présente dans Docker sous WSL ; entrée remplacée par
`sleep`, aucune base ni WordPress lancé. Aucun montage, volume, port ou accès au
staging Imagine. Réseau uniquement pour Composer et les dépendances publiques,
puis déconnecté avant PHPUnit et le lint. Aucun outil installé sur Windows/WSL.

Les journaux RED/GREEN, JUnit, empreintes des sources réellement copiées,
préparation et nettoyage se trouvent dans `production/C-01/tests/`.
Le bilan final est `production/C-01/tests/rapport.md`.

`PRET` signifie uniquement **prêt à relire**, pas validé par Ced, pas déployable,
pas GO. Les arbitrages ci-dessus restent ouverts.
