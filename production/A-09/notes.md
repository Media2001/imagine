# A-09 — remise technique

## Résultat

Outil autonome Python standard, lecture seule : `wp/outils/bascule/tester-redirections`,
module `a09/check.py`, commande de preuve `wp/tests/a09/run.py`, mode d'emploi une page
`tester-redirections.md`, exemple CSV : trois lignes fictives plus l'en-tête.
Aucune redirection réelle proposée ni appliquée. Aucun accès au staging, à la démo,
à une archive, à un compte ou à des données réelles ; aucune opération Git.

## Décisions prises à défaut

- Les deux colonnes d'URI du plan sont relatives à la racine ; l'origine est fournie
  séparément. Les URL absolues de `Location` restent acceptées si l'origine est identique.
- Les mêmes trois prédicats du marqueur vérifié et les mêmes octets de sécurité que
  A04/A05 sont exigés ; `a04/update.py` est importé sans modification. Un petit fichier
  déclaratif supplémentaire lie explicitement l'origine HTTP au répertoire vérifié.
  Le vérificateur n'écrit jamais ces fichiers et n'ouvre pas WordPress ni sa base.
- Conforme signifie strictement : bon premier code, bonne première cible, un saut,
  puis HTTP 200. Les chaînes sont explorées pour le diagnostic, mais jamais conformes.
  Arrêt avant toute autre origine, même au deuxième saut. Maximum neuf GET par ligne.
- L'exemple comporte trois **enregistrements fictifs**, pas trois lignes avec un
  en-tête pris à tort pour une redirection. Aucun plan métier n'a été inventé.

## Preuves et commandes

Depuis `C:/Users/Ced/imagine` :

```text
python -B wp/tests/a09/run.py
python -B production/A-09/verifier.py
python -B production/A-09/verifier.py --replay
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
```

Paquet final : `preuves/6fd5c1c30990/`, **21 tests, 21 réussis**, sorties natives,
13 rapports de scénarios HTTP réels, journaux des GET, piège d'autre origine resté
vide, cinq plans invalides avec zéro requête. Tous les codes 301/302/303/307/308,
chaîne, boucle, auto-boucle, plafond de sauts, cible 404/503, externe immédiat/tardif,
mauvais code/cible, délai, Location absente/double et refus de précontrôles sont couverts.
Les cycles RED puis GREEN sont conservés et référencés dans `manifeste.json`.

Le serveur HTTP jetable est un serveur Python fictif, sur loopback dans un conteneur
`network=none`, sans montage, port publié, privilège, service WordPress ni base.
Les marqueurs de ce banc sont des **entrées synthétiques**, pas une qualification
mensongère d'un staging WordPress. Chaque runner porte `org.imagine.a09-redirections`
et n'est supprimé qu'après contrôle de son nom exact et de son ownership. Les reçus
prouvent aussi son absence après suppression. Aucun balayage d'autres lots.

`preparer-image.ps1` a été réellement relancé après le paquet de tests final : code 0,
image T01 reconstruite/vérifiée (cache Docker accepté), reçu `preparer-image.json` et
sortie native intégrale `preparer-image.log`. Les mentions PowerShell
`RemoteException` autour du progrès Docker sont conservées, pas expurgées ; le
script et sa vérification d'image ont bien terminé à 0. Aucun PHP installé/exécuté
sur Windows, aucune modification du script partagé.

## Limites explicites

Suite dédiée A09, **pas** un rejeu global `wp/tests/rejouer.ps1` ; ce paquet Python
n'ajoute pas de suite PHPUnit à une bibliothèque partagée. Les 80 sources acceptées
suivies dans `baseline.json` sont conservées byte-identiques ; aucun correctif hors
A09 n'a été appliqué. Le manifeste et le vérificateur parent l'exigent à nouveau.
Le délai configurable est un délai d'opération socket, pas une échéance globale
incluant le DNS de l'OS ; les corps ne sont pas téléchargés. HTTPS garde la vérification
TLS standard mais la preuve demandée est HTTP. Aucune analyse de contenu SEO, aucune
acceptation sur un vrai site, aucune autorisation production. Le futur plan et le GO
restent hors de ce lot. Aucune question métier ni visuelle introduite.
