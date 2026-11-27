# Relecture indépendante Codex — A-32

Relecture du 27 novembre 2026. Références : doctrine, grille, brief A-32, cahier des charges §4.3 et §4.4, production et code livrés. Aucun accès au réel. Le rapport de Claude n'a pas été lu. Aucun fichier de production n'a été modifié.

## 1. Conformité

Le périmètre principal est respecté : quinze inventaires, ordre fermé, commandes issues des modes d'emploi, gardien commun réemployé, aucune agrégation métier dans le bilan. A-13/A-14/A-30 sont exclus pour leurs entrées Imagine ; A-29/A-31 restent dehors. `PRET`, `rejeu.json` et vérificateur sans argument sont présents.

L'ajout du contrôle préalable de copie vérifiée n'est **pas** retenu comme un écart : `docs/arbitrages-2026-11-27.md:222` l'autorise explicitement et corrige le brief ; `A-FAIRE.md:34` maintient cette consigne. L'inclusion d'A-26/A-27 est également prescrite. La finalisation conjointe est autorisée par l'arbitrage de 19 h.

- **A32-C01 — mineur — `wp/outils/bascule/README.md:18`.** Le mode d'emploi commun affirme encore qu'A-26/A-27 ne sont pas clos et ne font pas partie de la tournée, alors que la commande située juste au-dessus les lance. Le README local signale cette obsolescence, mais aucun renvoi à cette rectification n'accompagne la liste erronée dans le document commun. **Correction proposée :** corriger cette seule phrase de la section A-32, ou la remplacer par un renvoi explicite à la liste locale courante, sans restructurer le fichier partagé ; contrôler cette information dans le contrat documentaire.

## 2. Exactitude métier

Deux parcours du §4.3 ont été déroulés à la lecture du code et confrontés aux preuves :

1. **Inventaires de migration réussis.** Avec copie vérifiée et prérequis valides, A-10 inventorie les codes, A-11 les adresses, puis les treize suivants sont lancés. Les rapports restent séparés ; le bilan comporte quinze statuts et chemins, aucun compteur recopié. Les bilans classiques et HPOS livrés concordent avec ce parcours.
2. **Refus des codes, échec des adresses.** Le double déclaré d'A-10 retourne `1 / A10_AUDIT_GUARD`, celui d'A-11 retourne `255`. La boucle conserve respectivement « refusé » avec code et « en échec » avec sortie 255, puis poursuit les treize autres outils. Le bilan reste partiel et la sortie globale vaut 1. Les preuves `classic-named-doubles` et `hpos-named-doubles` concordent.

- **A32-C02 — important — `wp/outils/bascule/tournee/tournee.py:64`.** La liste utilisée par `classify()` omet les refus que le gardien construit dynamiquement : notamment `A11_PROCESS_OUTPUT_INVALID`, `A15_PROCESS_TIMEOUT` et `A19_SUCCESS_INCOMPLETE`. `guard.public_error()` les conserve bien, mais A-32 transforme leur réponse exacte `(1, stdout vide, code + LF)` en « en échec », sortie 1, sans code explicatif. Reproduction en mémoire sur les trois suffixes pour A-11/A-12/A-15 à A-19 : **21 codes perdus**. Les bilans natifs des canaux hostiles présentent déjà cette différence entre anciens outils et A-20, dont le code est conservé. Le brief demande précisément de rapporter le code du refus. **Correction proposée :** compléter localement la liste fermée avec les messages effectivement émis par les lanceurs et le gardien des outils inclus, sans modifier le gardien ; tester leur classement et conserver le rejet des messages inconnus ou accompagnés de texte libre.

- **A32-C03 — important — `wp/outils/bascule/tournee/outils.jsonl:8`.** La date illustrative d'A-19, `--as-of=2026-11-26T00:00:00Z`, devient une date permanente de production. `command()` ne substitue que les chemins et la commande de tournée n'offre aucun moyen de changer cette référence. Le rapport livré confirme `as_of_utc` au 26 novembre. Une tournée du 1er décembre examinant un prochain paiement au 28 novembre le traite donc comme futur : le calcul d'A-19 compare strictement l'échéance à la référence reçue. L'égalité au 26 novembre reste également non passée lors de tous les rejeux ultérieurs, y compris au changement d'année. La copie exacte de l'exemple respecte littéralement une phrase du brief, mais fausse le diagnostic attendu lors de la répétition puis de la bascule ; cette conséquence n'est pas signalée. **Correction proposée :** expliciter dans le contrat A-32 le traitement des dates d'exemple et employer une référence actuelle ou choisie explicitement, via les capacités existantes d'A-19, sans modifier son calcul ; couvrir un rejeu ultérieur, l'égalité et le changement d'année.

## 3. Tests

Exécutions indépendantes effectuées avec Python Windows 3.14.6 et `-B` :

| Commande / configuration | Résultat observé |
|---|---|
| `C:/Python314/python.exe -B production/A-32/verify.py` | Sortie 0, `A32_PACKAGE_PASS`, confirmé en fin de lecture |
| `C:/Python314/python.exe -B wp/tests/a32/verify.py --evidence=production/A-32/preuves/final` | Sortie 0, `A32_LOCAL_MATRIX` PASS |
| `C:/Python314/python.exe -B -m unittest discover -s wp/tests/a32 -p 'test_*.py' -v`, UTF-8, sans `TMPDIR` | 10 tests : 5 réussis, 5 erreurs d'accès au répertoire temporaire Hermès |
| Même suite, cp1252, `PYTHONUTF8=0`, sans `TMPDIR` | Même résultat : 5 réussis, 5 erreurs d'accès |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1`, sans `TMPDIR` | Sortie 1 avant exécution : `Wsl/Service/E_ACCESSDENIED`, 0 test exécuté |

Les cinq erreurs Python viennent de `TemporaryDirectory(dir=.../hermes/cache/scratch)` imposé par les tests, inaccessible en écriture dans cette session. Ce n'est pas une preuve d'échec fonctionnel du lot. La matrice native complète n'a pas été relancée ici : elle nécessite ce banc WSL. Aucun droit supplémentaire ni modification de harnais n'a été demandé.

Les preuves livrées annoncent 10 tests Python et 54 contrôles natifs/runner par console, classique et HPOS, avec empreintes et canaris. Leur vérificateur passe. J'ai également lu la réception parent après scellement référencée par `PRET`, dans `.../a31-a32-joint-final/post-seal/reception.json`, et contrôlé les empreintes des deux journaux et du manifeste A-32 : concordance. Les deux journaux indiquent `PAQUETS : 12 vérifiés, 0 échecs ; hors rejeu : aucun`, avec A-31/A-32 dans le reçu, 1 204 tests et 36 667 assertions. Il s'agit d'une preuve historique du parent, distincte de mon rejeu empêché par les permissions.

La couverture de poursuite et de confidentialité est utile. Elle ne vérifie toutefois pas tous les codes de refus, ne fait pas avancer l'horloge de la tournée et ne distingue pas une déclaration PHP d'une chaîne qui en contient le texte. Les contre-exemples C02 et C04 ont été exécutés en mémoire, sans fichier supplémentaire ; pour C04, les lectures du site sont des doubles explicitement déclarés.

## 4. Sécurité et données

- **A32-C04 — important — `wp/outils/bascule/tournee/tournee.py:95`.** La recherche de `define()` s'applique aussi à l'intérieur des chaînes PHP conservées par l'étape précédente. Avec un marqueur valide, la configuration `<?php $note = "define('WP_ENVIRONMENT_TYPE', 'staging');";` est acceptée par `verified_site()`, alors qu'elle ne déclare aucune constante d'environnement. Reproduction sur lectures fictives : vraie déclaration staging acceptée, production et absence simple refusées, fausse déclaration dans une chaîne acceptée. Cela contredit le refus des déclarations absentes annoncé au README et permet de franchir la garde sans preuve de la déclaration exigée. **Correction proposée :** reconnaître les jetons d'une véritable instruction dans le code PHP, en excluant commentaires, contenu des chaînes et texte hors PHP, sans exécuter la configuration ; conserver le refus prudent des formes non comprises et ajouter ces contre-exemples à la preuve « zéro outil lancé ». Ne pas modifier les outils clos.

Aucun secret ni donnée personnelle réelle repéré dans le périmètre examiné. Les sorties brutes des enfants ne sont pas recopiées dans le bilan ; les messages publiés sont fermés, les rapports sont hors dépôt/site et les noms proviennent de l'opérateur ou de la liste. Les preuves couvrent les deux flux, les arrêts anticipés, les fins de processus et l'altération des rapports. Aucun nouveau point HTTP, SQL ou paywall n'est créé par A-32 ; droits WordPress, nonces et rendu web ne s'appliquent donc pas directement à cette commande.

## 5. Doctrine

Le choix d'une commande distincte d'A-08 est justifié en trois lignes : aucune étape mutante et poursuite après refus. Le lot réemploie le gardien et les inventaires, sans recompter leurs résultats. Le code neuf est Python ; les conventions PHP ne lui sont pas applicables. La relecture ne propose aucune retouche de l'import, du gardien ou du lanceur gelés.

## 6. Études (lots sans code)

Sans objet : lot de code. La justification du standard repose ici sur le séquenceur A-08 disponible dans le dépôt, sans affirmation nouvelle sur une extension externe.

## Décisions techniques, défaut proposé

**Catégorie technique — C03 : quelle référence temporelle transmettre à A-19 lors d'une nouvelle tournée ?** Défaut proposé : l'instant UTC courant, capacité déjà documentée par A-19 lorsque `--as-of` est omis ; toute date volontairement figée doit être explicite. La correction du contrat de copie des exemples relève d'Hermès et de l'arbitrage technique, sans question pour Ced ni nouveau réglage métier. Les codes inconnus et les configurations non comprises restent refusés par défaut pour C02/C04.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun retenu.
- **Important :** C02 — codes de refus perdus ; C03 — date A-19 figée sur l'exemple ; C04 — fausse déclaration d'environnement acceptée.
- **Mineur :** C01 — liste obsolète dans le mode d'emploi commun.

Les limites de rejeu sont environnementales et déclarées ci-dessus ; elles ne remplacent pas les trois défauts reproduits ou établis par lecture.
