# Relecture indépendante Codex — B-12

Date : 27 novembre 2026. Références lues : `relecteurs/AGENTS.md`, doctrine, grille, brief B-12, cahier des charges §3.14 et §4.4, décisions, code et preuves du lot. Aucun accès au site ou à une base. La relecture Claude n'a pas été consultée.

## 1. Conformité

Le dispositif répond aux parcours nominaux du brief : handler avant les caches oEmbed, résolution directe, neutralisation du HTML des blocs `core/embed` et interception du proxy après permissions. Il ne dépend pas du réglage B11, ne crée aucun réglage et ne réécrit pas le corps. Les livrables demandés sont présents ; le standard et la levée future sont expliqués. L'exclusion du HTML arbitraire ajouté à la main est explicitement annoncée.

**B12-01 — bloquant — `wp/plugins/imagine-site/IntegrationsCorps.php:72`.** La sélection du proxy compare strictement le chemin reçu à `/oembed/1.0/proxy`, alors que le routage REST natif accepte une casse différente. Une requête authentifiée et autorisée vers `/oembed/1.0/PROXY`, avec une URL externe non cachée, conserve donc la réponse initiale `null` : le contrôleur natif peut poursuivre vers `get_data()`, que le filtre `pre_oembed_result` n'intercepte pas. Avec un transient préexistant, il peut également restituer l'ancien HTML externe. Cela contredit l'absence inconditionnelle de résolution externe demandée pour l'aperçu. **Correction proposée :** reconnaître la route avec la même insensibilité à la casse que le routeur, ou utiliser la route canonique correspondante fournie au callback ; conserver les permissions natives. Ajouter les variantes de casse au test REST natif, avec cache absent puis cache ancien, et vérifier zéro tentative et seulement un lien. Constat par analyse statique ; cette variante n'a pas été exécutée sur WordPress pendant la relecture.

## 2. Exactitude métier

Déroulement manuel de trois cas issus du brief et des §3.14/§4.4 :

- **Vidéo externe, consentement indisponible, B11 OFF puis ON.** Pour une URL YouTube seule ou `[embed]URL[/embed]`, `lien()` retourne un lien échappé avant le cache et les fournisseurs. Pour le bloc natif externe, `bloc()` retourne ce lien dans un paragraphe. Aucun branchement ne lit l'option B11. Résultat attendu sur ces parcours.
- **Contenu du site lui-même.** Pour une URL de même origine et comprise dans le chemin du site, `externe()` retourne `false` ; le handler délègue et les autres callbacks conservent le résultat reçu. Les reçus comparent aussi le proxy interne avec et sans le verrou. Résultat conforme à l'exception interne sur ces cas.
- **Ancien lecteur externe en cache.** Le handler précède le cache de contenu ; le bloc externe est remplacé avant son HTML enregistré ; le proxy canonique est intercepté avant son transient. Le corps saisi reste inchangé. La variante de route décrite en B12-01 échappe toutefois à cette dernière protection.

Les tests unitaires couvrent notamment les hôtes ressemblants, ports différents, sous-chemins voisins, identifiants dans l'URL et caractères à échapper. Les dates et échéances ne concernent pas ce lot.

## 3. Tests

Commandes effectivement lancées, sans écriture de journaux dans le dépôt :

| Commande | Résultat de cette relecture |
|---|---|
| `python -B wp/tests/demo/b12-proof-tests.py` | **PASS**, 6 tests. |
| `python -B wp/tests/demo/b12-verifier.py` | **FAIL**, code 1, `AssertionError: SOURCES`. |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` | **Non exécuté jusqu'aux suites** : accès WSL refusé, `Wsl/Service/E_ACCESSDENIED` ; 0 test PHP exécuté. |

**B12-02 — important — `production/B-12/reception-V2.json:11`.** La réception certifie le bootstrap `9530b50879a99f44284019ee481a1bd191e1b35a71a61b9a6310da7c1d7a6eb8`, mais celui présent vaut `e27ee706324066048c5610730c7b945b945a7b55e66200325147d0b8dcf00780`. C'est la seule divergence dans les sources déclarées. La suppression **en mémoire seulement** de l'ajout C29 retrouve exactement l'empreinte attendue : aucune modification propre à B12 n'est ainsi établie. Néanmoins, la commande de réception livrée échoue sur l'arbre à relire, et le complément B11/C27/C28 ne couvre pas cet ajout. **Correction proposée :** fournir une réception complémentaire de l'arbre actuel incluant C29, avec vérification explicite de la portion ajoutée et rejeu approprié ; conserver les anciens reçus et leur historique. Ne pas neutraliser l'assertion ni simplement remplacer l'empreinte sans preuve.

Toutes les pièces déclarées dans `evidence` sont présentes et leurs empreintes correspondent. Les reçus fournis annoncent 56 contrôles natifs sans tentative, une mutation de 15 contrôles avec 6 tentatives bloquées avant transport, et PHPUnit B12 à 5 tests / 37 assertions. Ce sont des **résultats archivés**, non un rejeu PHP réussi par ce relecteur. Les six tests locaux éprouvent réellement plusieurs contre-exemples du lecteur de preuves ; ils ne remplacent pas les tests du verrou dans WordPress.

Les commandes `--live`, les sondes natives et la mutation distante n'ont pas été lancées : `relecteurs/AGENTS.md` interdit « accéder à un site, à une base ou à un compte ». Aucune image n'a été reconstruite ou installée. L'impossibilité d'utiliser WSL est une limite de l'environnement de relecture, pas un échec fonctionnel attribué au code.

## 4. Sécurité et données

Le point B12-01 compromet la garantie de non-résolution pour un utilisateur déjà autorisé à utiliser le proxy ; il ne constitue pas un contournement des permissions natives. Les liens sont échappés en attribut et en texte, avec protocoles HTTP/HTTPS. Aucun secret ou donnée personnelle réelle identifié dans les éléments du lot examinés. Les essais sont fictifs et les reçus déclarent leur suppression et la restauration de l'état.

Le code B12 ne modifie ni les champs B11 ni les décisions du paywall. Aucun nouvel accès au texte réservé identifié dans ces callbacks ; l'étanchéité globale du paywall n'a pas été rejouée dans cet environnement.

## 5. Doctrine

Le choix des points d'accroche natifs respecte le principe « standard d'abord ». La classe fonctionnelle utilise le namespace `Imagine\Site`, les types stricts et un identifiant global préfixé. Elle ne modifie pas WordPress ni une extension tierce. Le README explique le fonctionnement et les commandes de test. Les preuves négatives et les limites de réception sont documentées ; B12-02 reste à résoudre avant de présenter la réception actuelle comme verte.

### Décisions techniques, défaut proposé

Les corrections B12-01 et B12-02 sont techniques. Défaut prudent : conserver le verrou inconditionnel, aligner la reconnaissance de route sur WordPress et compléter les preuves sans réécrire les reçus historiques. Aucun arbitrage visuel, métier ou touchant au réel demandé à Ced.

## 6. Études (lots sans code)

Sans objet : lot avec code. Le fichier `sources-officielles-V2.json` contient sept références officielles avec URL et extraits ; elles ont été examinées dans le dépôt, sans consultation externe pendant cette relecture.

## Verdict

**À corriger.**

- **Bloquant : B12-01**, variante de casse du proxy non couverte par le verrou.
- **Important : B12-02**, réception incompatible avec le bootstrap actuel après ajout C29.
- **Mineur :** aucun point retenu.

Ce verdict n'est pas un GO. Les tests PHP restent non rejoués ici pour la raison d'environnement indiquée ci-dessus.
