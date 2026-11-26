# Relecture indépendante Codex — A-22

Date : 26 novembre 2026. Périmètre : brief A-22, production A-22, gardien commun, intégrations et bancs dans `wp/`. Doctrine, grille et cahier des charges §2.5 et §4.4 lus. La relecture Claude n’a pas été consultée. Aucun code corrigé.

## 1. Conformité

Le tableau de qualification, le gardien commun, les raccordements A03/A11/A12/A14–A21, les tests transversaux, la ligne du mode d’emploi commun et `PRET` sont présents. A02/A10 ne chargent pas WordPress ; A13 reste hors ligne. Les commandes documentées sont contrôlées par un test qui passe lors de cette relecture. Les règles de collecte restent dans les outils ; §2.5 concerne le connecteur Odoo et n’introduit ici aucune nouvelle règle comptable.

**P1 — Important — `wp/outils/bascule/stream_guard.py:138` : le refus historique A12 change.** Pour un nom final contenant un point, par exemple `--output=/rapports/invalid.name`, le gardien produit désormais `A12_OUTPUT_UNSAFE`. La validation PHP conservée dans `a12/Command.php:35` produit `A12_PATH_INVALID` pour ce même nom. Le dictionnaire des compatibilités ne couvre qu’A03 et A11. Cela contredit explicitement « ses codes de refus non plus » dans le brief. **Reproduction locale :** invocation réelle de `a12/confine.py` avec un dossier existant comme chemin de site, un parent temporaire existant et `a22-invalid.name` : sortie 1, stdout vide, stderr `A12_OUTPUT_UNSAFE`, avant tout lancement PHP. **Correction proposée :** préserver `A12_PATH_INVALID` pour cette validation et ajouter ce cas aux tests de compatibilité des refus, sans masquer le nom final par le nom temporaire.

## 2. Exactitude métier

Deux cas du contrat de sécurité, dérivé du §4.4 et précisé par le brief, ont été déroulés dans le code :

- Une extension s’arrête pendant le chargement avec `exit(0)`, sans message final : le gardien attend les deux fins de flux, puis refuse l’absence du message exact de succès. Le dossier temporaire n’est pas publié. Le code zéro seul ne suffit donc pas.
- Une fonction de fin de processus écrit sur stderr après le message de succès : le gardien attend la terminaison et conserve cette écriture ; la condition `stderr` fait refuser la publication. Le test portable avec un véritable processus enfant et une fonction `atexit` passe et confirme que les octets tardifs sont bien capturés.

Ces parcours sont corrects pour les flux. Ils ne prouvent pas l’intégrité des fichiers après les fonctions de fin de processus : voir P3. Dates, clôtures et changements d’année ne sont pas des règles modifiées par A-22.

## 3. Tests

Exécutions réellement effectuées depuis la racine, avec Python 3.14 et écriture des fichiers bytecode désactivée :

| Contrôle | Résultat indépendant |
|---|---|
| `C:/Python314/python.exe -B -m unittest discover -s wp/tests/a22 -p 'test_*.py' -v`, environnement UTF-8 | 17 tests : 11 réussis, 6 erreurs `PermissionError` dans les dossiers temporaires ; code 1 |
| Même suite via `python -B`, résolu vers Python 3.14, avec `PYTHONIOENCODING=cp1252` et `PYTHONUTF8=0` | Même bilan : 11 réussis, 6 erreurs d’accès ; code 1 |
| `C:/Python314/python.exe -B wp/tests/a22/verify.py production/A-22/preuves/final` | Code 1, `A22_PACKET_INVALID`, classe `PermissionError` : paquet final inaccessible |
| Prérequis du banc natif, avec la fonction `call` du runner A02 et son image épinglée | `wsl.exe` retourne 4294967295, `Wsl/Service/E_ACCESSDENIED` ; aucun conteneur lancé |
| Trois sondes complémentaires exécutées en mémoire, sans fichier de test ajouté | Confirment P1, l’omission P2 et l’acceptation par `complete()` décrite en P3 |

Les cinq tests de processus du gardien passent : sortie tardive, dépassement de 64 Kio, délai, descendant conservant les pipes ouverts et transport UTF-8 sur stdin. Les six erreurs des suites complètes concernent l’accès ou le nettoyage des répertoires temporaires ; elles ne sont pas présentées comme six défauts applicatifs. Je n’ai ni changé les permissions ni modifié le harnais pour les contourner.

Les banques natives, leurs quatre canaris obligatoires, les mutations et les suites des lots clos n’ont donc pas pu être rejoués ici. La production annonce 42 commandes vertes et 159 contrôles par console ; ces nombres sont des résultats déclarés dans les documents livrés, pas une validation indépendante du paquet inaccessible. Une première tentative d’affichage du diagnostic WSL a aussi rencontré une erreur d’encodage dans ma sonde ; le nouvel affichage échappé a confirmé le refus WSL ci-dessus.

**P2 — Important — `wp/tests/a22/matrix.py:26` : les sources métier A03 sont absentes des empreintes.** La construction `'a'+str(3)` désigne `a3`, alors que le dossier est `a03`. L’énumération silencieuse d’un dossier inexistant omet `Policy.php`, `Report.php` et `Site.php`. L’appel réel à `sources()` confirme l’absence des trois chemins. Le contrôle `exact_current_executed_sources` du vérificateur compare donc deux inventaires qui peuvent tous deux ignorer une modification de ces fichiers ; l’empreinte du runner ne remplace pas celle du code exécuté. **Correction proposée :** utiliser le chemin `a03`, refuser les racines attendues inexistantes, tester explicitement la couverture de ces trois fichiers et régénérer les preuves concernées après correction. Ajouter une mutation qui altère une de ces sources sur une copie jetable et exige le refus du vérificateur.

## 4. Sécurité et données

Les flux bruts restent en mémoire bornée ; les refus sont reconstruits depuis une liste fermée, sans recopier un préfixe arbitraire. Le délai et l’attente des deux fins de flux sont testés. Les canaris du banc sont fictifs. Aucun accès au réel, à un compte ou à une API n’a été effectué. Nonces, interfaces publiques et droits du paywall ne sont pas modifiés par ce lot.

**P3 — Important — `wp/outils/bascule/stream_guard.py:118` : la validation des rapports laisse passer une modification silencieuse en fin de processus.** `complete()` vérifie les noms, types et tailles des fichiers, puis seulement la syntaxe JSON. Aucun contenu Markdown ou CSV n’est contrôlé. Une extension peut enregistrer une fonction de fin de processus qui ajoute un chemin ou un nom confidentiel à `contenus.md` après la production normale du rapport, sans écrire sur stdout/stderr. Le sous-processus conserve le droit d’écrire dans son dossier temporaire ; les flux et le code de sortie restent ceux du succès, puis le parent publie le fichier altéré. La protection de la publication ne couvre donc pas cette autre sortie tardive.

**Niveau de preuve :** une sonde en mémoire de la vraie fonction `complete()` lui présente les deux fichiers attendus, un JSON `{}` et un Markdown contenant uniquement `A22_PRIVATE_FLOW_CANARY` ; elle retourne `True`. L’exploitation complète par une extension PHP n’a pas été exécutée, puisque le banc natif est inaccessible. Le chemin de publication est établi par lecture du code. Les validations propres A20/A21 sont plus strictes et ne présentent pas cette même simple acceptation du Markdown arbitraire.

**Correction proposée :** contrôler les rapports des anciens outils après la terminaison, avec des contrats propres qui conservent leurs formats et comptes autorisés, avant publication. Ajouter au banc une fonction de fin de processus qui contamine silencieusement un rapport, et vérifier le refus ainsi que l’absence du canari dans tous les fichiers publiés. Ne pas considérer le seul succès des canaris stdout/stderr comme une preuve de cette propriété.

## 5. Doctrine

La supervision d’un processus est correctement placée hors de WordPress ; elle ne réimplémente pas une règle de commerce. Le mécanisme commun évite les copies du lecteur de flux, notamment pour A20/A21. Les fichiers PHP communs examinés déclarent les types stricts. Je n’ai pas rejoué le contrôle de style natif, soumis au même accès WSL indisponible.

Les corrections proposées sont techniques ; aucune question métier, visuelle ou touchant au réel n’est adressée à Ced. Le défaut prudent est de refuser une publication dont le contenu final n’a pas été validé, tout en conservant les contrats des outils clos.

## 6. Études (lots sans code)

Sans objet : lot de code. Aucune documentation externe ni aucun site n’a été consulté.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun point classé à ce niveau.
- **Important :** P1 — refus A12 modifié ; P2 — empreintes A03 incomplètes ; P3 — contenu des rapports modifiable silencieusement avant publication.
- **Mineur :** aucun point supplémentaire.

La validation indépendante des preuves natives reste à effectuer dans un environnement autorisant leur lecture et le banc local. Les restrictions d’accès de cette session ne constituent pas, à elles seules, un défaut de la production.
