# A-26 — qualification native finale déléguée du 2026-11-26T23:42:11.856281+01:00

Paquet unique courant : `production/A-26/preuves/final/`. Windows `C:/Python314/python.exe` **3.14.6**, consoles UTF-8/mode 1 et cp1252/mode 0 mesurées dans les deux `environment.json`.

Gel exact : **2026-11-26T23:23:56.752314+01:00**, 125 fichiers, racines explicites A26/A27 + communs d'exécution voie 1 ; aucun inventaire voie 2 épinglé. Égalité avant/après chacune des 19 commandes. Aucun changement du gardien A-22 ni de l'import. README commun contrôlé uniquement par les deux lignes détenues par lot ; les quatre lignes exactes sont intégrées dans `wp/tests/a02-audit/README.md`, tous autres octets préservés (readback conservé).

## Résultats réellement exécutés

- utf8 : Python=24 tests ; PHP pur=33 assertions ; natif classique+HPOS=188 assertions ; runner=20 ; standard installé=11 contrôles par reçu ; tout PASS, codes 0.
- cp1252 : Python=24 tests ; PHP pur=33 assertions ; natif classique+HPOS=188 assertions ; runner=20 ; standard installé=11 contrôles par reçu ; tout PASS, codes 0.
- Global utf8 : 1149 tests, 36036 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS ; 18 outils, 417 contrôles, 0 échecs ; hors rejeu : aucun.
- Global cp1252 : 1149 tests, 36036 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS ; 18 outils, 417 contrôles, 0 échecs ; hors rejeu : aucun.
- `style.py --fix` exécuté en conteneur avant gel ; style strict final zéro erreur et zéro avertissement. Vraie banque PHP pur, inclusion `php -n` sans écritures/extensions, témoin RED réellement échoué puis restauration et GREEN.
- Compteurs exacts, magasins faisant autorité, rapport rejoué identique, commande documentaire avec ses seuls arguments ; empreintes de toutes tables/planificateur et fichiers identiques avant/après ; clones fictifs traversant le vrai moteur d'import inchangé ; réseau none, sans montage/port, HTTP/mail/cron/Action Scheduler bloqués.
- Tous canaux directs, arrêt anticipé, shutdown et fichiers de rapport éprouvés, y compris altération cohérente JSON/Markdown des nombres, refus sans publication. Aucun canari retenu. Les `red-unit.json` sont des témoins explicitement rouges attendus, jamais des suites PASS.

## Corrections, décisions et limites

Mauvais chemin du README dans la réception et le vérificateur corrigé vers le vrai contrat audit. Vérification sans argument vise désormais le final actuel. Détection statique bornée : dix familles, dix-sept chemins, treize services ; un seul schéma d'identifiant qualifié (Site Kit GA4), autres actifs illisibles ; pas d'exhaustivité ni conformité. Après neutralisation, contenus-source et familles retirées inconnus, jamais zéro reconstruit.

## Gates et disponibilité

`preparer-image.ps1`, puis `rejouer.ps1` UTF-8/cp1252 et vérificateurs 20/21/22/23/24/25 read-only : tous codes 0, après gel. Logs, commandes, heures et sorties intégrales : `files/rapports/2026-11-26-23h42-qualification-A26-A27/`. PowerShell émet nativement UTF-8 dans ses deux environnements Python distincts ; aucune prétention de console PowerShell cp1252. Vérifications propres : `C:/Python314/python.exe -B wp/tests/a26/verify.py` et paquet scellé : `C:/Python314/python.exe -B production/A-26/verify.py`, sans argument.

Essais rouges/intermédiaires exclusivement en scratch `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a2627-parent-20261126`. Premier contrôleur annulé honnêtement avant correction A27, son runner exact retiré après contrôle d'appartenance. Second contrôleur arrêté par le watchdog outil à 420 s : A26 entièrement terminé, exit 0 conservé ; A27 interrompu jamais accepté, runner exact supprimé puis matrice A27 entière relancée par processus suivi. Une invocation sans argument du vérificateur A20 a donné usage/exit 2 : sa vraie interface exige le chemin du paquet, désormais fourni à A20/A21/A22 sans modifier leurs sources. Un rejeu global a fini ses suites vertes mais son conteneur avait disparu avant inspect (exit global 1, cause extérieure non attribuée) ; reçu rouge conservé, aucun résultat requalifié. Préparation et toutes gates communes intégralement relancées dans le paquet frais `final-gates2`, vrais exits 0. Aucune sortie de succès fabriquée. Tous les runners acceptés relisent leur propre disparition avec diagnostic sémantique.

Notes et chiffres finalisés avant scellement ; les marqueurs candidats historiques des matrices décrivent leur frontière initiale, gates parent maintenant liées dans `parent-gates.json`. PRET seulement après vérifications scellées vertes ; relectures suivront, pas d'attente ni de clôture annoncée. Post-PRET : `2026-11-26-23h42-qualification-A26-A27-postpret.json` sous `files/rapports/`. Verrou rafraîchi et conservé au parent. Aucun Git, Novamira, archive/compte/site réel, voie 2, synchronisation ou file modifié ; aucun PHP Windows.

Vérification adversariale du sceau : 12 exécutions réelles en miroir jetable, tous résultats attendus observés (mutation/omission/ajout source, reçu natif rouge, lignes README manquante/doublée/altérée/CRLF refusés, ajout documentaire étranger accepté, commun gelé altéré refusé). Reçu `verification-probes.json` ; aucune mutation originale.
