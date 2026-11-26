# C-22 — corrections du 26 novembre 2026

## Résultat

Trois instructions appliquées ; `A-VOIR.md` et `PRET` actualisés seulement après les gates réels verts. La section C10 reste sous Enregistrer ; son injection est inchangée et sa présence/position sont testées. Défaut de création : Non. Pas de Git ni délégation.

- C22-01 : `NewslettersReglages.php` réserve les identifiants actifs et historiques (préférences et journaux C10) dans des options sans donnée personnelle. Le hook préalable à la suppression des préférences préserve également la réservation avant effacement. Refus après retrait, y compris catalogue vide et préférences effacées ; ancien choix exportable/effaçable sans réattribution.
- C22-02 : `NewslettersRegles.php` mesure en caractères avec `mb_strlen(..., 'UTF-8')` ; 150/500 caractères accentués acceptés, 151/501 refusés.
- C22-03 : `c22-verifier.py` exerce les vrais callbacks natifs C21 sur un choix historique retiré, puis rollback et relecture. Plus d'assertion sur le littéral de `Confidentialite.php` ni de reconstruction de son ancienne empreinte. L'installateur C22 ne déploie désormais que les trois fichiers Newsletters ; aucun fichier partagé réécrit.

## TDD et preuves exactes

Les reçus sont tous dans ce dossier, sans réécriture des historiques.

| Cycle | Rouge exécuté | Vert exécuté |
|---|---|---|
| Retrait et consentement réel | `correction-red-retired-V2.json` : quatre échecs métier attendus | `correction-green-retired-V2.json`, puis `correction-final-retired-V2.json` : 9/9 |
| Ancien choix hors catalogue | `correction-red-history-V2.json` : deux échecs attendus | `correction-green-history-V2.json` |
| Effacement avant édition / journal historique seul | `correction-red-history-erased-V2.json` : deux échecs attendus | `correction-green-history-erased-V2.json`, puis `correction-final-history-V2.json` : 8/8 |
| Longueurs UTF-8 | `correction-red-utf8-V2.json` : borne accentuée refusée à tort | `correction-green-utf8-V2.json`, puis `correction-final-utf8-V2.json` : 6/6 |
| Vérificateur livré incompatible | `correction-red-verifier-V2.json` : AssertionError sur le littéral partagé | `python -B wp/tests/demo/c22-verifier.py --seal`, puis sans argument : code 0 |

`correction-final-privacy-V2.json` : 6/6. Les deux mutations témoins sont rouges attendues : `correction-mutation-export-V2.json` détecte exactement l'omission du champ, `correction-mutation-erase-V2.json` détecte exactement l'absence d'effacement. Aucun mutant du fichier partagé n'est écrit.

Commandes principales réellement exécutées depuis la racine :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/Users/Ced/imagine/wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/Users/Ced/imagine/wp/tests/rejouer.ps1
python -B wp/outils/demo/c22-quality.py correction-quality-V2
python -B wp/outils/demo/c22.py runtime correction-native-V2
python -B wp/tests/demo/c22-http.py correction-http-rejeu-V2
python -B wp/tests/demo/c22-verifier.py --seal
python -B wp/tests/demo/c22-verifier.py
```

Préparation image : code 0. Rejeu : **1 123 tests / 34 569 assertions**, zéro échec/erreur/ignoré, **14 outils / 279 contrôles**, zéro échec. Nouveaux parcours natifs de correction : **29/29**, séparés du compteur PHPUnit. Régression native : **19/19**. HTTP/Chromium : **40/40**. C09 : **382/382**. PSR12 des sources Newsletters et du test PHPUnit existant : zéro erreur.

## Restauration et périmètre

Identité `imagine-test-demo` vérifiée par la garde C22 avant les opérations. Transactions annulées pour les sondes natives ; parcours HTTP restauré par lignes/absences exactes pour préférences, réglages, réservations et cache de première visite. Empreintes des profils et état métier du planificateur relus exacts ; action **8793**, abonnement **101**, toujours **pending**, date GMT **2026-11-26 02:13:28**. Journaux C10 append-only conservés. Observateur retiré et absence relue.

`correction-scope-V2.json` constate les empreintes inchangées de `Confidentialite.php` et du bootstrap, côté dépôt et démonstration. **39 reçus historiques** conservés octet pour octet. Sceau courant : `correction-final-V2.json`, `correction-manifest-V2.json`.

Réseau HTTP final : **41 requêtes observées**, zéro email, **54 tentatives natives de bootstrap / 54 bloquées avant transport**, zéro tentative du raccord newsletter, **6 demandes Gravatar bloquées** dans Chromium. Aucun transport API externe.

## Incidents et limites

- `correction-http-V2.json` est conservé rouge : le sélecteur supposait une ancienne classe CSS de notice WordPress. Le rejeu vise l'identifiant Settings API réel ; refus métier et données étaient déjà corrects. Aucun rouge rebaptisé vert.
- Le premier reçu de préparation a été rangé accidentellement sous `production/B-05/correction-preparation-V2.log` par le helper importé. Il a été immédiatement déplacé par son nom exact dans C-22 ; absence relue à l'ancien emplacement. Aucun artefact ne reste dans B-05.
- Aucun bloqueur technique. Questions restantes : position visuelle de la section (inchangée, Ced), consentement à la création (défaut Non, Imagine). Réservations prudentes, pas de schéma nouveau ; la lecture historique est locale et limitée aux clés nécessaires. Les tests spécifiques ne sont pas ajoutés au banc partagé T01.
- Aucun rapport écrit dans `files/rapports/` : réservé au parent. Aucun autre lot entrepris. Prêt à relire n'est pas clôture, validation visuelle ou GO sur le réel.
