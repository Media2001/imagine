# A-13 — Correctif prioritaire du 26 novembre 2026

## Corrections appliquées

1. **Encodage fixé dans le test**, à l'appel `subprocess.run` de
   `test_repository_output_refused_without_touching_fixture` :
   `env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}`,
   lecture également en UTF-8. L'erreur cp1252 a été reproduite avant correction,
   puis le même test est passé sous Python 3.14.7, mode UTF-8 désactivé et console
   cp1252. L'outil n'impose pas UTF-8 à la console.
2. **Garde `reconfigure(errors='backslashreplace')` conservé**, car justifié par
   `test_console_cp1252_or_ascii_does_not_fail_after_outputs` : sans ce garde dans
   une copie jetable, le succès ASCII lève `UnicodeEncodeError` après écriture des
   fichiers. Ce n'est **pas** le correctif du défaut cp1252 ci-dessus.
   `test_console_cp1252_or_ascii_refusal_without_traceback_or_outputs` vérifie aussi
   le refus, son encodage et l'absence de traceback ou de fichiers ; stderr Python
   échappe déjà les caractères non encodables indépendamment du garde.
3. Une liste `types_abonnement_autorises` non vide avec
   `colonnes.type_abonnement=null` est **refusée en français, sans sortie**.
   Le filtre vide accepte toujours ce champ facultatif non mappé. Les deux
   combinaisons sont testées ; aucun mapping vers un produit n'est ajouté.
4. **Libellés postaux dédoublonnés** : une absence signalée par « Champ obligatoire
   absent : <champ> » n'ajoute pas « Adresse postale incomplète ». Ce dernier motif
   reste présent pour un autre champ postal absent non obligatoire. Tests sur les
   quatre champs postaux et le cas mixte ; mode d'emploi aligné.
5. Corrections IBAN et doublons acquises intactes : sonde NFKC par cellule sans
   joindre les colonnes ; nom + adresse sans exiger le prénom par défaut, option
   `doublon_prenom_identique=false`. Le prénom absent est désormais testé à part.

## Dernier rejeu vert — un seul paquet de preuves

**46 tests, 0 échec, 0 erreur, 0 ignoré dans chacun des cinq contextes Windows**.
Chaque contexte exécute ensuite les trois vraies CLI fictives, codes **0, 1 et 2**.
La locale Windows mesurée est `cp1252` ; ces encodages sont mesurés dans Python.

| Python exécuté | stdout / stderr | PYTHONIOENCODING | PYTHONUTF8 / mode UTF-8 | Encodage préféré |
|---|---|---|---|---|
| 3.11.15, environnement habituel du terminal | utf-8 / utf-8 | utf-8 | 1 / 1 | utf-8 |
| 3.14.7, cible | utf-8 / utf-8 | utf-8 | 1 / 1 | utf-8 |
| 3.14.7, console forcée | cp1252 / cp1252 | cp1252 | 1 / 1 | utf-8 |
| 3.14.7, console et locale héritées | cp1252 / cp1252 | cp1252 | 0 / 0 | cp1252 |
| 3.14.6, interpréteur du poste de contrôle | cp1252 / cp1252 | cp1252 | 0 / 0 | cp1252 |

**230 exécutions de tests**, sous-tests non additionnés, et quinze CLI supplémentaires.
`verification.json` contient les cinq contextes, commandes exactes, versions,
encodages, résultats et empreintes ; `verification.tests.txt` rassemble leurs cinq
transcriptions intégrales UTF-8. Les sources A-13 sont identiques avant/après
chaque rejeu et entre les contextes.

- Propre : 30 lignes sans défaut, code 0.
- Défauts : 25 lignes rejetées / 25 motifs, 5 sans défaut, 6 lignes en doublon,
  1 sans email, non rejetée pour la seule absence d'email.
- IBAN fictif : colonne 14 refusée, code 2, aucune sortie ni valeur recopiée.
- Les 25 diagnostics attendus tombent sur leur ligne physique exacte.
- Les preuves ne conservent que résumés sans données, compteurs et empreintes.
  Fixtures copiées en scratch puis nettoyées, aucun export réel.

`wp/tests/preparer-image.ps1` relancé **après ajout des tests**, code 0 ; journal
courant : `preparer-image-corrections-26nov.log`. Vérification hors réseau après
construction. Avertissement partagé « T01 sans tests : themes/imagine » et lignes
de transport PowerShell `System.Management.Automation.RemoteException` présents ;
la commande termine néanmoins sur `T01 IMAGE READY` et `PREPARATION T01 : image
verifiee`, code 0. Aucune validation du thème ou de la voie 2 n'est revendiquée.

**`wp/tests/rejouer.ps1` ne couvre pas A-13** : c'est la non-régression PHP.
A-13 est validé séparément par sa suite Python. Aucun rejeu PHP global revendiqué
pour ce correctif ; préparer l'image n'exécute pas ce rejeu.

## Rejouer à la racine C:/Users/Ced/imagine

Commandes bash de vérification directe exécutées ; les preuves de relecture
parent vont hors dépôt :

```bash
export TMPDIR='C:/Users/Ced/AppData/Local/hermes/cache/scratch'
PY3147='C:/Users/Ced/AppData/Local/hermes/tools/python-3.14.7+20260901-win32-x64/python.exe'
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 "$PY3147" -B -m unittest discover -s wp/tests/a13 -v
PYTHONIOENCODING=cp1252 PYTHONUTF8=1 "$PY3147" -B -m unittest discover -s wp/tests/a13 -v
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 "$PY3147" -B -m unittest discover -s wp/tests/a13 -v
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 C:/Python314/python.exe -B -m unittest discover -s wp/tests/a13 -v
python -B -m unittest discover -s wp/tests/a13 -v
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 "$PY3147" -B wp/tests/a13/verifier_livraison.py --preuve "$TMPDIR/a13-relecture-parent.json"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/preparer-image.ps1
python -B production/A-13/verifier_manifeste.py
```

Le paquet a été produit par cinq appels à `verifier_livraison.py` (suite entière
puis trois CLI chacun). Leurs commandes exactes et exécutables absolus figurent
dans le JSON. Les cinq appels directs `unittest` ci-dessus vérifient aussi la suite,
sans ajouter de paquet au dépôt. Ne pas contrôler une fixture directement dans
le dépôt : les sorties y sont refusées.

`manifeste.json` ne couvre que les fichiers A-13 et leurs octets SHA-256, ni
orchestration ni lot frère ; il exclut lui-même et `PRET`. `reception.json` lie ce
paquet à la préparation image réussie ; `PRET` désigne l'empreinte du manifeste.
Essais rouges et anciens paquets conservés hors dépôt, dans le scratch Hermes.

## Décisions prises à défaut

Garde console conservé avec sa contre-épreuve ASCII ; dédoublonnage postal précis ;
filtre contradictoire refusé. Aucun arbitrage technique en attente. Le défaut
ignore le prénom conformément au brief ; Imagine peut demander l'activation de
l'option existante, sans bloquer le lot.

Aucun compte, archive ou site réel ouvert ; aucun import, droit d'accès, paiement
ou écriture comptable. Aucun GO de migration ou de déploiement.