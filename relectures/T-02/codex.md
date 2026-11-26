# Relecture indépendante Codex — T-02

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief T-02, sources et preuves livrées. Aucune lecture de la relecture Claude. Aucun fichier de production modifié.

## 1. Conformité

Le raccord répond au périmètre principal : découverte des sous-dossiers immédiats contenant `unit.php`, exclusion explicite motivée par `unit.hors-rejeu`, sous-processus dans le conteneur existant, ligne `OUTILS` avant la dernière ligne `REJEU`, propagation des échecs. Les trois lignes de convention sont présentes dans `production/T-01/notes.md`. Les matrices natives classique/HPOS/commerciales restent explicitement hors rejeu.

Le brief ne cite aucun paragraphe métier du cahier des charges ; il s'agit d'outillage. La relocalisation des littéraux de chemin et les deux formats de reçu constituent des interprétations documentées. `FINALISATION.md` remplace explicitement l'état candidat décrit dans `notes.md` ; le PRET est présent. La préparation finale est attestée par les preuves du parent, sans nécessité d'exécuter cette préparation pendant la relecture.

## 2. Exactitude métier

Sans règle métier nouvelle à recalculer, deux cas du contrat technique ont été déroulés à la lecture du code :

- Une banque produit un contrôle `FAIL` avec un processus sortant à zéro : le compteur des outils devient non nul, le résultat PHP est négatif et PowerShell termine par `FAIL`. Le contrat PHP correspondant est présent.
- Une banque contient `unit.hors-rejeu` avec « WordPress et base requis » : elle rejoint la liste des exclusions avant toute copie ou exécution, avec sa raison. Le contrat vérifie également qu'une banque qui lèverait une exception n'est jamais lancée.

**R1 — Important — `wp/tests/t01/tools.php:124` : un reçu ambigu peut masquer un contrôle rouge.** Le lecteur privilégie `tests` et n'examine jamais `checks` lorsque les deux tableaux existent. Ainsi, le reçu `{"tests":{"ancien":true},"checks":[{"check":"nouveau","status":"FAIL"}],"exit_code":0}`, avec processus de code zéro et stderr vide, est compté comme un contrôle vert. Le rejeu peut donc annoncer PASS malgré un échec explicitement présent dans le reçu. Cas établi par déroulement du code, non exécuté dans cette session. **Correction proposée :** imposer exactement un des deux formats et refuser leur coexistence ; ajouter un contrat avec ce reçu mixte et vérifier le FAIL final. Cette ambiguïté n'est pas présente dans les banques actuelles examinées.

## 3. Tests

Exécutions indépendantes :

- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\rejouer.ps1` : code **1**, arrêt sur `Wsl/Service/E_ACCESSDENIED` dès le contrôle Docker. Bilan : `REJEU : 0 tests, 0 assertions, 0 échecs, 1 erreurs, 0 ignorés — FAIL`. Aucun conteneur créé par cette tentative. Ce résultat est une limite de l'environnement de relecture, pas un échec des tests PHP.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\wp\tests\t01\test-tools-summary.ps1` : code **0**, **7/7 PASS**. Ces tests utilisent une frontière Docker simulée ; ils ne prouvent pas l'exécution de PHP.

Preuves fournies contrôlées en lecture : les **46 fichiers** du manifeste correspondent à leurs empreintes, notamment les huit sources T-02. Les sorties finales attestent **1 123 tests PHPUnit, 34 569 assertions**, et **13 outils, 242 contrôles**, sans échec ni exclusion. Banques : a02-audit, a03-non-regression, a10, a11, a12, a14, a15, a16, a17, a18, a19, a20, a21. Le journal avant raccord conserve les mêmes compteurs PHPUnit.

La mutation A-10 fournie produit bien un contrôle rouge et un bilan FAIL, puis la restauration produit PASS ; cette preuve porte sur l'inventaire candidat de 11 outils/204 contrôles. Les journaux montrent la suppression vérifiée des conteneurs. Les 18 contrats PHP couvrent notamment reçu absent, vide, malformé, statut inconnu, avertissement PHP, code de sortie non nul et lien symbolique pendant. Ils ne couvrent pas R1. Je n'ai pas rejoué PHP, la mutation ni le nettoyage réel en raison du refus WSL ; aucune mutation de fichier n'a été faite pour cette relecture.

**R2 — Mineur — `production/T-02/preuves/final/utf8/verification.json:188` : l'empreinte interne du rejeu ne correspond plus au journal livré.** Le champ `commands.rejeu.output_sha256` vaut `d0b5913b627dd1b1a4377236d4ec3ef43a5380ca6d1c8786cbc6de9ed5ab644b`, alors que `utf8/rejeu.log` vaut `441655b5058bf82451149acf93894316db6d41300b2733d02946469f99d93387`. Le manifeste externe est cohérent, mais ce reçu interne ne permet pas de vérifier le journal auquel il se rapporte. **Correction proposée :** conserver distinctement les reçus candidats et finaux, ou régénérer les métadonnées depuis le journal final réellement livré, puis resceller le paquet T-02. Vérifier également le contexte cp1252, où la même discordance est constatée. Ne pas régénérer les preuves des lots clos.

## 4. Sécurité et données

Les options examinées maintiennent le réseau désactivé, le montage `wp/` en lecture seule, la racine du conteneur en lecture seule, les écritures temporaires sous `/tmp`, l'utilisateur non privilégié et les restrictions de capacités. Les alias de bibliothèques pointent vers le montage en lecture seule. Aucun accès au réel ni secret introduit repéré dans le périmètre T-02. Droits WordPress, nonces, SQL et paywall : sans objet pour ce raccord. L'isolation réelle n'a pas pu être vérifiée indépendamment ici.

## 5. Doctrine

Le code réutilise PHPUnit et le dispositif T-01 ; aucune fonctionnalité d'extension WordPress n'est réimplémentée. Les nouveaux fichiers PHP déclarent les types stricts.

**R3 — Mineur — `wp/tests/t01/tools.php:6` : les nouvelles fonctions sont déclarées dans l'espace global.** Cela ne respecte pas l'espace de noms `Imagine\` demandé au §5 de la doctrine. **Correction proposée :** placer les fonctions ajoutées dans un espace de noms dédié sous `Imagine\` et adapter leurs appels ainsi que les contrats, sans réécrire les fonctions historiques de T-01.

## 6. Études (lots sans code)

Sans objet : lot de code et d'outillage, sans étude d'extension à sourcer.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun défaut de cette gravité établi.
- **Important :** R1 — rejet nécessaire des reçus mixtes pouvant masquer un échec.
- **Mineur :** R2 — cohérence des empreintes internes ; R3 — espace de noms des nouvelles fonctions.

Les corrections proposées sont techniques et n'appellent aucun arbitrage de Ced. La validation indépendante des suites PHP reste non acquise dans cette session, pour la raison d'accès WSL indiquée ci-dessus.
