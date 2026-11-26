# Relecture indépendante Codex — A-26

Date : 27 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief A-26, cahier des charges §4.4 et décisions du dépôt. Examen de `production/A-26`, de l’implémentation, des tests et des dépendances concernées dans `wp/`. La relecture Claude n’a pas été consultée. Aucun accès à un site, une base ou un compte réel.

## 1. Conformité

Les livrables sont présents : inventaire, tests, documentation, paquet unique et marqueur PRET. Le script réemploie le lanceur confiné et le gardien A-22 ; il produit des agrégats sur dix familles et treize services, sans désactivation ni verdict de conformité. La sélection A-16 accepte trois formes de liaison ; sans correspondance, le repli annuel est explicite. Le rattachement au §4.4 est cohérent avec un inventaire préparatoire au registre.

Les restrictions sont annoncées : dix-sept chemins d’extensions, un seul schéma d’identifiant qualifié, intégrations statiques seulement. Elles ne dispensent pas de compter correctement le HTML expressément couvert : voir I1. La disponibilité annoncée par PRET n’est plus étayée pour les dépendances actuelles : voir B1.

- **M1 — mineur — `production/A-26/readme-ajout.txt:1`.** Le renvoi `a26/README.md`, également inséré dans le mode d’emploi commun, ne désigne pas le fichier depuis la racine du dépôt ni depuis le répertoire de ce mode d’emploi. Il rend les prérequis et limites difficiles à retrouver dans le parcours à copier. **Correction proposée :** utiliser le chemin explicite `wp/outils/bascule/a26/README.md` et synchroniser la ligne correspondante du mode d’emploi commun.

## 2. Exactitude métier

Trois cas déroulés à la lecture du code, sans les présenter comme un rejeu PHP :

1. **Copie non neutralisée :** Site Kit actif avec un identifiant non vide, un article comportant deux intégrations YouTube et une ressource d’un domaine inconnu. `families()` rend mesure = 1 et identifiant = oui ; `services()` puis `content()` donnent YouTube = 1 et autre = 1 pour cet article. Ni l’identifiant ni le domaine ne sont projetés. Conforme à la règle « un contenu par service ».
2. **Copie neutralisée :** la marque d’import indique le retrait de Site Kit et du pixel Facebook, et l’import a pu vider un contenu. Les deux familles retirées et leurs identifiants deviennent « inconnu après neutralisation » ; tous les comptes de contenus deviennent inconnus. Une famille encore active conserve son effectif mais son identifiant devient inconnu. Cela évite les faux zéros et correspond aux opérations de neutralisation examinées.
3. **Onze numéros :** le tri décroissant date puis ID retient dix numéros ; l’article lié uniquement au plus ancien et l’orphelin restent dans le total général, hors sélection. Les liens multiples vers des numéros retenus ne multiplient pas le compte d’un article. Le banc fourni exerce les trois formes de liaison ; les dates égales et les références cycliques de blocs ne sont pas couvertes par les cas natifs lus.

- **I1 — important — `wp/outils/bascule/a26/Analysis.php:148`.** L’extraction HTML par expressions régulières confond les délimiteurs de balise avec le contenu des attributs. Avec `<iframe title="a > b" src="https://www.youtube.com/embed/fiction"></iframe>`, `[^>]*` s’arrête dans le titre : l’intégration YouTube réelle est omise. Inversement, `<img title='src="https://vimeo.com/123"' src="/local.png">` fait extraire une prétendue ressource Vimeo depuis le texte du titre, alors que l’image est locale. Ce sont des balises du périmètre annoncé, pas des intégrations dynamiques exclues. Les totaux et leurs répartitions héritent de ces erreurs. **Correction proposée :** lire les véritables balises et attributs avec un parseur HTML sans rendu ni accès réseau, en examinant d’abord l’API HTML native de WordPress ; ajouter ces deux contre-exemples aux tests, puis les vérifier dans les rapports classique et HPOS. Constat établi par analyse du code ; PHP n’a pas pu être rejoué ici.

## 3. Tests

Exécutions locales avec `C:/Python314/python.exe -B` et désactivation des fichiers bytecode :

| Contrôle | Résultat observé |
|---|---|
| `-m unittest discover -s wp/tests/a26 -p 'test_*.py' -v`, UTF-8 | 24 tests : 14 réussis, 10 erreurs d’environnement, aucun échec d’assertion |
| Même découverte, cp1252 et `PYTHONUTF8=0`, résultats capturés en mémoire | 24 tests : 14 réussis, 10 erreurs d’environnement, aucun échec d’assertion |
| `wp/tests/a26/verify.py` | Code 1 : `A26_SOURCE_DRIFT` |
| `production/A-26/verify.py` | Code 1 : `SEALED_VERIFICATION_FAILED` ; cause précisée par appel en mémoire : `FROZEN_SOURCE_DRIFT` |
| Précondition native, inspection de l’image par la fonction du banc | WSL refuse l’accès : `Wsl/Service/E_ACCESSDENIED` |

Les dix erreurs Python portent sur l’accès aux répertoires temporaires et leur nettoyage (`PermissionError` / WinError 5). Elles ne démontrent pas un défaut fonctionnel du lot. Je n’ai pas déplacé les écritures de test dans le dépôt ni modifié les tests pour contourner ces restrictions. Les suites PHP, classique/HPOS et style n’ont donc pas été rejouées ; la commande opérateur n’a pas été exécutée sur une copie.

Les reçus fournis annoncent, par console, 24 tests Python, 33 assertions PHP pur, 188 assertions natives et 20 contrôles du lanceur. La couverture des sorties est substantielle : flux directs, arrêt anticipé, shutdown, fichiers de rapport et altération cohérente JSON/Markdown. Des témoins de mutation vérifient effectivement le rôle des gardiens. En revanche, les cas HTML I1 ne figurent pas dans cette couverture.

- **B1 — bloquant pour la validation — `production/A-26/PRET:1`.** Le marqueur annonce des matrices, gates et sceau verts, mais les deux vérificateurs fournis refusent actuellement la livraison. Comparaison des empreintes : `wp/outils/staging/command.php` et `wp/outils/staging/lib.php` ont changé ; `wp/outils/staging/form-policy.json` est une dépendance supplémentaire absente du gel. Les fichiers A-26 recensés par son manifeste n’ont pas changé : la dérive concerne ses dépendances. L’import réel étant expressément utilisé dans la preuve de neutralisation, les anciens résultats ne qualifient pas l’ensemble actuellement livré. **Correction proposée :** rejouer le paquet unique et les contrôles requis avec les dépendances actuelles figées, puis renouveler les empreintes, le sceau et PRET après réussite effective. Ne pas simplement remplacer les empreintes ni désactiver les contrôles. Ce refus est distinct des restrictions d’exécution de cette session.

## 4. Sécurité et données

Aucune fuite directe identifiée à la lecture des chemins examinés. Les requêtes de collecte sont des SELECT avec paramètres préparés ; les identifiants de table proviennent de WordPress. La désérialisation interdit l’instanciation de classes. Le schéma public impose des clés fermées, des nombres et des états prédéfinis ; les domaines inconnus deviennent « autre ».

Le gardien attend la fin du processus, contrôle les flux, les empreintes finales et les deux fichiers canoniques avant publication. Les titres et contenus lus ne sont pas repris dans les rapports ; aucune nouvelle voie de rendu du paywall n’est ajoutée. Les canaris du banc sont fictifs. La preuve native d’absence d’écriture et de fuite reste celle du paquet fourni, avec la réserve B1 et sans confirmation native indépendante dans cette session.

## 5. Doctrine

Réemploi des parseurs de blocs et de codes courts WordPress, de la validation A-16 et des protections A-11/A-12/A-22. La logique d’agrégation est séparée de l’accès WordPress. Les classes PHP examinées déclarent les types stricts et utilisent l’espace de noms `Imagine`. Aucun changement de l’import n’est proposé dans cette relecture.

I1 appelle aussi l’application du « standard d’abord » à l’analyse HTML. Les corrections proposées sont techniques ; aucune question métier, visuelle ou touchant au réel n’est adressée à Ced. Défaut prudent : conserver les refus fermés et les états inconnus, sans assouplir les contrôles pour obtenir un résultat vert.

## 6. Études (lots sans code)

Lot avec code ; rubrique non applicable comme étude autonome. Les sources officielles sont néanmoins archivées avec URL et empreintes dans `production/A-26/standard/sources.json`. Les extraits consultés étayent le schéma Site Kit et la distinction entre WP Consent API et un gestionnaire de consentement. Aucune consultation réseau effectuée ; aucune conclusion de conformité juridique formulée.

## Verdict

**À corriger.**

- **Bloquant : B1**, qualification périmée des dépendances actuelles.
- **Important : I1**, comptes HTML inexacts sur des attributs valides.
- **Mineur : M1**, renvoi documentaire incomplet.

Ce verdict n’est pas un GO.
