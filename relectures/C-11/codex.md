# Relecture indépendante Codex — C-11

Date : 24 novembre 2026. Périmètre : brief C-11, `production/C-11/`, code et tests concernés dans `wp/`, doctrine, décisions et critères R-25 à R-31. Le rapport de l'autre relecteur n'a pas été lu. Aucun accès à un site, une base ou un compte ; aucune modification hors du présent rapport.

## 1. Conformité

Le parcours nominal correspond au brief : endpoint contrôlé par C-06 avec le type `pdf`, réglages C-10 transmis au moteur, retour au numéro en cas de refus, livraison PHP avec en-têtes privés. Le stockage hors racine publique est expliqué en cinq lignes dans `A-VOIR.md`. Les livrables demandés sont présents.

L'achat à l'unité reste fermé et cette limite est explicitement annoncée : c'est l'exception autorisée par le brief, pas une non-conformité à corriger dans ce lot. La vérification des vrais robots et le cache de l'hébergeur ne sont pas revendiqués.

**C11-01 — Bloquant — `wp/outils/demo/b00-seed.php:85` — Le rejeu depuis l'ancien état B00 conserve les PDF publics.**

La branche PDF appelle `protect()` avec la source privée `/var/www/imagine-private-pdf/source/...`, puis retourne sans retirer les anciennes copies dans `uploads/imagine-demo/` et `imagine-demo-build/assets/`. Or `protect()` ne supprime que son argument `$source` lorsque celui-ci est sous la racine publique. Partir d'un B00 antérieur à C11, puis reconstruire avec le constructeur actuel, crée donc les fichiers privés et les références protégées tout en conservant les anciennes adresses statiques connues. Le nettoyage nécessaire existe dans `c11-migrate.php`, mais le constructeur B00 n'appelle pas ce script. Même un éventuel échec ultérieur de comparaison des snapshots ne retire pas ces fichiers.

Cela contredit l'étanchéité des §3.9 et §4.4 et la reconstruction rejouable : le résultat dépend d'une migration C11 préalable réussie, au lieu de converger depuis l'état public initial.

**Correction proposée :** faire converger la branche médias PDF du seed elle-même vers l'état privé, en retirant et vérifiant les deux anciennes copies précisément identifiées avant de considérer le numéro protégé ; mutualiser ce nettoyage avec la migration. Ajouter un test partant de l'ancien état B00, avec les deux copies publiques présentes, puis vérifier leur disparition et rejouer une seconde fois sans changement d'identifiants ni d'octets privés.

## 2. Exactitude métier

Cas déroulés à la main dans `Paywall::decisionPdf()` et le moteur C-06 ; il s'agit de lecture de code, pas de résultats HTTP obtenus par le relecteur :

| Cas | Résultat du code | Référence |
|---|---|---|
| Numéro publié, déjà paru ; abonnement actif commencé avant sa sortie, fin encore future | Décision complète, ouverture du fichier privé, réponse PDF si le fichier est disponible | §3.9, R-25 ; `Paywall.php:95`, `PdfNumero.php:185` |
| Même numéro demandé anonymement | Aucun droit transmis ; décision fermée avec bloc connexion ; redirection vers le numéro sans ouverture du fichier | §3.9, §4.4, R-26 ; `PdfNumero.php:197` |
| PDF paru avant le début d'un abonnement actif | Fermé si C10 vaut `ferme`, ouvert si C10 vaut `ouvert` | Réglage demandé par le brief ; `Moteur.php:122` |
| Instant exactement égal à la fin de l'abonnement | Fermé : la borne de fin est exclue | §3.9 ; `Moteur.php:118` |

La comparaison « PDF antérieur » utilise strictement `<` : une sortie exactement égale au début du droit n'est pas antérieure. Les dates sont des objets temporels, sans calcul particulier fragile au changement d'année. Une date éditoriale absente ou invalide ferme la décision. Les bénéficiaires offert/groupe passent par les mêmes règles de période que l'abonné. Aucun droit d'achat n'est fabriqué par l'adaptateur.

Pas d'écart métier supplémentaire identifié sur ces parcours.

## 3. Tests

**Exécutés localement : 33 tests Python, 33 réussis**, avec la découverte `test_*.py` employée par le runner C11. Les wheels B01 ont été chargées en lecture seule et l'écriture des fichiers bytecode désactivée. Commande rejouable depuis PowerShell :

```powershell
@'
import sys, unittest
from pathlib import Path
sys.dont_write_bytecode = True
sys.path[:0] = [str(p.resolve()) for p in Path('production/B-01/validation').glob('*.whl')]
suite = unittest.defaultTestLoader.discover('wp/tests/demo', pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
'@ | python -B -
```

Le total comprend le test C12 désormais présent ; la preuve C11 enregistrée annonce 32 tests. Le seul test Python propre à C11 (`test_c11_seed.py:9`) vérifie des chaînes dans le constructeur, pas la disparition effective de fichiers publics.

Les fichiers livrés annoncent 74/74 contrôles HTTP, 8/8 défauts HTTP, 24/24 contrôles natifs et 10/10 contrôles du seed. **Ces résultats ont été lus, pas reproduits.** Le rejeu `c11.py --check-only` accède au site, téléverse des scripts, modifie des données et réécrit les preuves. Il est incompatible avec les droits du relecteur : `relecteurs/AGENTS.md`, section « Droits », interdit « accéder à un site, à une base ou à un compte » et limite l'écriture au rapport. Une tentative de test PHP local en mémoire n'a pas pu démarrer : la commande `php` n'est pas disponible dans le PATH. Aucun contournement ni installation n'a été effectué.

La recette `c11-seed-runtime.php:23` commence par exiger un PDF déjà protégé ; elle ne couvre donc pas l'état initial à l'origine de C11-01. Les défauts HTTP couvrent fichier absent, préfixe corrompu et traversée de chemin, mais pas les comparaisons de chemins Windows signalées en C11-02. Les sitemaps enregistrés répondent tous 404 : la preuve porte sur leur désactivation, pas sur un sitemap actif. Les politiques robots sont testées avec une décision synthétique, limite correctement documentée.

## 4. Sécurité et données

**C11-02 — Important — `wp/plugins/imagine-site/PdfNumero.php:113` — La détection des chemins publics échoue avec les séparateurs Windows.**

Les chemins issus de `realpath()` ne sont pas normalisés avant comparaison avec `$public . '/'`. Avec `$public = C:\site` et `$realSource = C:\site\uploads\numero.pdf`, le test de préfixe est faux : `protect()` réussit sans retirer le PDF public. Le même défaut à la ligne 40 accepte un répertoire configuré `C:\site\private` comme étant extérieur à `C:\site`. Le stockage annoncé hors racine publique n'est donc pas garanti sur cet environnement ; l'ancienne adresse connue peut continuer à servir le PDF sans contrôle de droit. Ce constat vient de la lecture des comparaisons, sans exécution PHP Windows disponible.

**Correction proposée :** centraliser la comparaison de chemins canoniques, normaliser leurs séparateurs et tenir compte de la casse selon le système, avec une frontière de répertoire explicite. Utiliser cette comparaison tant pour le refus d'un stockage public que pour le retrait de la source. Tester un enfant public, un répertoire frère au préfixe similaire et une source publique, sous Windows et Unix ; à défaut de prise en charge, refuser explicitement cet environnement avant toute protection annoncée réussie.

Sur le parcours Linux nominal examiné, les noms privés sont aléatoires, les traversées de chemin et liens symboliques directs sont refusés, les médias deviennent privés et les URL natives pointent vers le contrôleur. Les droits sont recalculés avant chaque GET/HEAD ; les réponses PDF portent `private, no-store`, sans ETag ni Last-Modified. Les sorties du bloc sont échappées et traduites. Le téléchargement ne réalise pas de mutation nécessitant un nonce. Aucun secret ni donnée réelle identifié dans les fichiers examinés.

Le maintien de copies statiques décrit en C11-01 contourne entièrement ces gardes applicatives.

## 5. Doctrine

La logique métier reste dans C-06 ; l'adaptateur réutilise les droits natifs et l'administration C-10. Les classes principales portent `strict_types` et l'espace de noms `Imagine`, et l'extension possède un README avec les commandes de test.

`A-VOIR.md` cite les références officielles WordPress et WooCommerce justifiant le raccord spécifique. Leur contenu externe n'a pas été consulté pendant cette relecture, conformément à l'interdiction d'accès aux sites. `RAPPORT.md` signale honnêtement leur consultation après le premier prototype : l'écart à la séquence « standard d'abord » est déjà tracé.

La reconstruction depuis un état antérieur et la portabilité restent à corriger conformément aux deux points ci-dessus.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant — C11-01 :** reconstruction depuis l'ancien B00 laissant les copies PDF publiques.
- **Important — C11-02 :** comparaisons de chemins non portables pouvant laisser une source publique et accepter un stockage public sous Windows.
- **Mineur :** aucun point supplémentaire retenu.

Les tests Python exécutés passent. L'étanchéité HTTP n'a pas été vérifiée indépendamment en raison des limites explicites du rôle de relecteur.
