# C-06 — historique de la livraison et correction du 21 novembre 2026

> **Livraison actuelle : [notes-22nov.md](notes-22nov.md)**, arbitrages du 22/11,
> trois réglages prudents, 247 tests / 30 368 assertions.
> Les comportements, réserves, commandes et comptes rendus ci-dessous sont ceux
> du 21/11 : ils restent historiques, pas des instructions actuelles.
> Les contrats d'entrée inchangés restent utiles ; le sixième argument et
> l'adaptateur d'administration sont décrits dans les notes actuelles.

## Périmètre et sources

PHP 8.2 pur, `Imagine\Pilotage\Acces`, sans WordPress, base, session,
horloge, appel réseau ni restitution de texte. Sources lues : consigne permanente,
doctrine révisée le 21/11/2026, A-FAIRE, brief C-06 entier, cahier des charges
v3.1 entier, décisions et arbitrages du 21/11, briefs et contrats C-01/C-03 utiles.
Les lots C-01/C-03 sont clos dans A-FAIRE. Aucun fichier de `docs/recette/` lu,
modifié ou automatisé. Ces tests sont ceux du moteur demandé, pas la recette R-25–R-31.

Le standard est conservé : Memberships fournit déjà plans, restrictions,
extraits, messages et API de consultation ; Subscriptions porte ses états natifs.
Les trois pages officielles consultées et leur apport sont consignés dans
`sources-officielles.json`. C-06 n'en refait ni la persistance ni les transitions :
il compose les règles Imagine, les motifs et les blocs avec le résultat de C-03.
La documentation ne constitue pas un test de l'étanchéité des extensions.

## API : un seul point de décision

```php
$decision = (new Imagine\Pilotage\Acces\Moteur())->decider(
    $contenu,
    $visiteur,
    $decisionC03,
    $instant,
    $politiqueDecouverte, // null si aucun droit découverte n'est fourni
);
$decision->complet;       // bool : sinon extrait (pour PDF : ne pas servir le fichier)
$decision->motif->value;  // motif stable, enum Motif
$decision->bloc->value;   // aucun, abonnement, connexion, regularisation, decouverte_epuisee
```

`Decision` est readonly et n'a que ces trois propriétés. Ni corps de texte,
ni HTML, URL de PDF, extrait, donnée personnelle ou réponse HTTP ne sont produits.
`decider` accepte volontairement des `mixed` et des arguments omis : erreurs de
forme, clés manquantes/supplémentaires et `Throwable` retournent toujours
`false / entree_invalide / abonnement`. Aucune exception n'accorde l'accès.

### Contrats des arguments (clés exactes)

| Argument | Forme |
|---|---|
| Contenu | `['reserve' => bool, 'numero' => string, 'type' => 'article' ou 'pdf', 'sortie' => DateTimeImmutable, 'decouverte' => bool]` |
| Visiteur | `['identifie' => bool, 'droits' => liste de droits]` |
| Robot | Véritable `Imagine\Pilotage\Robots\Decision`, calculé pour cette requête ; pas un booléen ni un tableau |
| Instant | `DateTimeImmutable`, fourni par l'appelant |
| Politique | `null`, `DureeDecouverte` ou `NombreArticlesDecouverte` |

Identifiants de numéros opaques : chaînes non vides sans espace ASCII ni contrôle ;
pas de trim, conversion numérique, arithmétique de numéro ou rapprochement implicite.
`170`, `0170`, `169`, `171`, `HS-2026` sont distincts. L'existence éditoriale et
l'appartenance à la zone réservée sont préparées par l'adaptateur : ce moteur ne
reconstitue pas un catalogue et ne choisit pas les 5 à 10 derniers numéros.
Un contenu de sortie future est refusé ; aucune fonction de prévisualisation.

Toutes les dates sont immuables, à la seconde entière ; les dates fractionnaires,
chaînes et `DateTime` mutables sont refusées, sans arrondi. Les exemples et tests
utilisent Europe/Brussels conformément à C-01 ; les comparaisons portent sur les
instants réels, même si un appelant transmet un autre fuseau. Pas de date retournée
à sérialiser. Début inclus, fin exclue. La découverte durée compte des secondes
écoulées, pas des heures civiles : changements d'heure testés.

### Droits (tableaux à clés exactes)

- Abonnement personnel, offert ou groupé :
  `['type' => 'abonnement'|'offert'|'groupe', 'etat' => 'actif'|'grace'|'suspendu'|'expire'|'virement_non_valide', 'debut' => DateTimeImmutable, 'fin' => DateTimeImmutable]`.
  `debut < fin` est obligatoire. `debut` est l'ouverture du droit numérique,
  pas le premier numéro papier ; `fin` est sa borne effective fournie par le
  système de droits, y compris la borne de grâce si l'état est `grace`.
  Aucune année, durée de grâce ni transition de statut n'est recalculée ici.
- Achat : `['type' => 'achat', 'numero' => string, 'acquis_le' => DateTimeImmutable]`.
  Le droit commence à `acquis_le`, sans expiration, seulement pour ce numéro.
- Équipe : `['type' => 'equipe', 'role' => 'redaction'|'administration']`.
- Coopérateur : `['type' => 'cooperateur']`, aucun droit aux articles/PDF à lui seul.
- Découverte : `['type' => 'decouverte', 'debut' => DateTimeImmutable, 'compte_verifie' => bool, 'consommes' => entier >= 0]`.
  Un seul droit découverte dans l'instantané ; doublon = incohérence. Un anonyme
  portant des droits est incohérent. Aucun état natif tel que `on-hold` n'est
  converti implicitement : le futur adaptateur doit traduire les états métier.

## Règles servies, motifs et coexistence

Tout l'instantané est validé **avant** un cas favorable, même pour un contenu
ouvert, une équipe ou un robot. Un droit inconnu/malformé n'est pas ignoré à côté
d'un achat valide. À l'inverse, les droits négatifs **valides** ne sont pas un veto.

| Situation valide | Décision et motif | Bloc |
|---|---|---|
| Ouvert | complet, `contenu_ouvert` | aucun |
| Anonyme réservé | extrait, `anonyme` | connexion |
| Identifié sans droit | extrait, `sans_droit` | abonnement |
| C-03 positif Google/Bing | complet, `robot_verifie` | aucun |
| C-03 négatif, panne, timeout ou faux robot | n'accorde rien ; règles normales du visiteur | selon autre droit |
| Actif personnel/offert/groupé dans ses dates | complet, `abonnement_actif` / `offert_actif` / `groupe_actif` | aucun |
| Grâce dans ses dates | complet, `delai_grace` | régularisation |
| Suspendu / virement non validé | extrait, `suspendu` / `virement_non_valide` | régularisation |
| Expiré, ou fin atteinte | extrait, `expire` | abonnement |
| Avant début abonnement | extrait, `abonnement_pas_commence` | abonnement |
| Achat du numéro, à partir de l'achat | complet article et PDF, `numero_achete` | aucun |
| Autre numéro / achat pas commencé | extrait, `autre_numero` / `achat_pas_commence` | abonnement |
| Coopérateur seul | extrait, `cooperateur_sans_abonnement` | abonnement |
| Équipe | complet, `equipe` | aucun |
| Découverte valable | complet, `decouverte_duree` ou `decouverte_articles` | aucun |
| Découverte épuisée dans son périmètre | extrait, `decouverte_epuisee` | découverte épuisée |
| Découverte non commencée / hors périmètre | extrait, `decouverte_pas_commencee` / `decouverte_hors_perimetre` | abonnement |
| Compte découverte non vérifié | extrait, `compte_non_verifie` | connexion |
| PDF antérieur au début de l'abonnement | extrait sur ce seul droit, `pdf_anterieur_a_arbitrer` | abonnement |

Complet l'emporte toujours sur extrait ; à accès complet égal, l'absence de
bandeau de régularisation est plus favorable. Départage technique stable,
indépendant de l'ordre : équipe > achat > personnel > offert > groupé > découverte
> grâce. Ouvert puis robot sont prioritaires après validation. Un achat de PDF
ancien reste valable même avec un abonnement expiré/suspendu/grâce ; les droits
ne se neutralisent pas. Entre refus, priorité explicative : suspension, virement,
expiration, abonnement non commencé, PDF réservé à arbitrer, achat non commencé,
autre numéro, découverte épuisée/non commencée/hors périmètre/non vérifiée,
coopérateur, sans droit. Ce départage n'élargit aucun accès.

Seuls les positifs `google`/`bing` de C-03 sont consommés, conformément à
l'arbitrage C-03/3 ; identité positive inconnue = refus global. Le booléen d'UA
ne suffit jamais. La liste `['google', 'bing']` reste synchronisée manuellement
avec `config/robots.php` : ajout approuvé à reporter aux deux endroits, sinon
le nouveau robot est fermé en extrait (correction C-06/3, documentée au code et
au README). Pas de nouveau DNS ni cache en C-06 ; C-03 doit être calculé
avec la vraie IP normalisée et pour la même requête par le futur adaptateur.

## Découverte : deux variantes disponibles, aucune choisie

Interface `Decouverte`, deux implémentations finales readonly :

```php
new DureeDecouverte($secondesPositives, $listeExacteNumeros, $pdfAutorise);
new NombreArticlesDecouverte($quotaPositif, $listeExacteNumeros, $pdfAutorise);
```

Tous les réglages sont obligatoires, sans valeur commerciale par défaut.
Une liste vide est valide et n'ouvre rien. Chaque variante exige également le
marqueur éditorial `decouverte=true`. Le booléen PDF est explicite dans les deux
variantes ; il ne choisit pas la recommandation du chapitre 7. Une politique
absente avec un droit découverte, malformée ou d'une troisième implémentation
non prise en charge ferme tout l'instantané, même en présence d'un autre droit.

Durée : `debut <= instant` et secondes écoulées strictement inférieures au réglage.
Quota : `consommes < maximum` ; pas d'expiration temporelle inventée. Les valeurs
10/3600 secondes et 1/3 articles ne sont que des fixtures fictives, pas une offre.
Les méthodes des politiques sont des détails internes appelés après validation
par `Moteur::decider`, seul point d'entrée défensif supporté.

Ce moteur ne consomme rien, ne réinitialise rien et n'enregistre aucune identité.
L'unicité par personne, le compte vérifié et l'état non renouvelable doivent être
établis et conservés par l'adaptateur de confiance. Le futur branchement du quota
devra réserver/compter atomiquement l'article réellement servi après sélection
du motif ; une lecture HTTP concurrente ne doit pas réutiliser le même crédit.
Il faudra arrêter avec Imagine ce qui compte comme article consommé et la
relecture après épuisement : aucun droit permanent de relecture n'est inventé.

## À arbitrer par Ced / Imagine — réserves explicitement hors lot C-06

Ces questions du brief ne sont ni tranchées, ni des raisons de confondre PRET
avec une validation métier. Leur mise en application appartient au lot suivant :

1. **PDF ancien** : ouvrir au seul titre d'un abonnement actif le PDF d'un numéro
   paru avant son début numérique : **oui/non** ? En attendant, ce seul droit ne
   l'ouvre pas ; article oui selon le brief, achat indépendant oui. Méthode isolée
   `Moteur::abonnement`, motif `pdf_anterieur_a_arbitrer`.
2. **Grâce au-delà du bandeau** : confirmer strictement les mêmes articles et PDF
   qu'à l'état actif jusqu'à la borne de grâce fournie, seul le bandeau change :
   **oui/non** ? Implémentation minimale prescrite par le brief : texte complet
   et bloc régularisation, sans effet financier ni autre avantage/refus inventé,
   avec la même réserve PDF ancien. Durée et déclenchement au premier rejet non
   décidés ; aucune valeur de quatorze jours n'est appliquée.
3. **Extrait (décision 20)** : retenir les deux premiers paragraphes, réglables
   par article : **oui/non** ? Aucune longueur, découpe ou génération d'extrait
   dans C-06, seulement le booléen `complet=false`.
4. **Découverte (décision 5)** : choisir la variante durée plutôt que quota :
   **oui/non** ? Puis confirmer l'étendue aux seuls numéros explicitement retenus
   et l'absence de PDF : **oui/non** ? Les deux variantes sont livrées réglables,
   sans activation ni recommandation codée. Convention de décompte/relecture à
   réserver au futur branchement, pas une décision prise par le moteur.
5. **Sortie future (fusion C-06)** : doit-elle rester fermée pour tout le monde,
   équipe et robots compris, sans prévisualisation via cette décision : **oui/non** ?
   Comportement existant conservé, sans nouvel arbitrage sur les droits.
6. **Robot et PDF (fusion C-06)** : un robot vérifié reçoit-il `complet` sur un PDF
   déjà paru comme sur un article : **oui/non** ? Comportement du tableau du brief
   conservé ; le contrôle par téléchargement appartiendra à l'adaptateur.

## Tests, preuves et reproduction

Les tranches TDD sont conservées dans `tests/red-*` puis `tests/green-*` : base,
robots/blocs, abonnements, achats/coexistence, durée, quota, fermeture défensive.
Le premier RED base échoue par absence de classe ; le premier RED robot par
absence de constantes, puis `red-robot-assertions` contient les vrais écarts de
résultat. Les autres RED constatent les règles manquantes, pas un succès simulé.
`red-fermeture-contract` montre les exceptions injectées et les défauts de
validation avant correction. Les journaux rouges restent rouges et immuables.

| Règle / source | Tests |
|---|---|
| C-06 tableau, §3.9, ouverts/anonymes/robots | DecisionTest |
| Personnel/offert/groupé, §3.5/3.8/3.9, suspension décidée le 21/11 | AbonnementTest, table de 30 lignes |
| Achats perpétuels, coopérateur, équipe, §3.9 et C-06 | DroitsTest |
| Coexistence favorable | DroitsTest : tous les sous-ensembles de 11 droits, dans les deux ordres ; QuotaTest |
| Dates seconde avant/à/après début et fin, grâce incluse | AbonnementTest, DroitsTest, DecouverteTest, QuotaTest |
| Découverte réglable, décision 5 non choisie | DecouverteTest, QuotaTest ; transitions heure été/hiver |
| Inconnu/incohérent/manquant/exceptions, C-06 fermé par défaut | FermetureTest, mutation de chaque clé, mêmes refus avec ouvert/équipe/robot |
| PDF ancien réservé à arbitrage | AbonnementTest, DroitsTest |

Lanceur propre : `wp/tests/acces-runner/run.py`. Il importe les patterns C-03/C-01
sans les modifier ni générer de bytecode dans leurs dossiers. Label d'appartenance
`org.imagine.c06-runner`, aucun montage, volume, port, privilège ou service web/DB.
L'image synthétique existante a son entrypoint remplacé par `sleep`. Composer et
les dépendances publiques sont installés seulement dans le conteneur jetable,
puis le réseau est déconnecté avant PHPUnit, PHPCS et syntaxe. Aucun PHP Windows.

La configuration PHPUnit racine inclut désormais Acces aux côtés des trois
suites closes. Correction C-06/1 : `composer test` standard exécute les quatre
suites ; le lanceur n'injecte plus `tests/Acces/phpunit.xml`. La configuration
locale reste disponible à titre historique/ciblé, mais n'est pas nécessaire.
Le XML racine et le README ont été modifiés sur instruction de la fusion ;
Composer, lock et sources des lots clos restent inchangés. Le lanceur exécute
`composer test -- --log-junit /tmp/result.xml`, dans le conteneur uniquement.
Le contrôle `check-standard-suite.py` vérifie commande, configuration racine,
présence des quatre suites et absence d'échec/erreur/ignoré.

Depuis Git Bash, dans `C:/Users/Ced/imagine`, nouveau paquet de preuves sans
écraser l'original (prendre un nom neuf pour chaque rejeu) :

```bash
export IMAGINE_C06_PACKET=relecture-1
python wp/tests/acces-runner/run.py prepare
python wp/tests/acces-runner/run.py run --name final
python wp/tests/acces-runner/run.py close
python wp/tests/acces-runner/verify.py seal
python wp/tests/acces-runner/verify.py check
unset IMAGINE_C06_PACKET
```

Facultatif avant la commande finale, pour PHPCBF limité aux deux dossiers Acces :
`python wp/tests/acces-runner/format.py`. Tout changement PHP exige de refaire
`run --name <nom-neuf>` ; ne pas réutiliser un ancien JUnit. Le lanceur supprime
le JUnit précédent du conteneur avant chaque exécution.

Les fichiers partagés sont comparés à `tests/shared-before.json` ; un ajout du
lot parallèle Echeancier a d'abord déclenché la garde, sans test ni écriture
partagée. Le lanceur exclut désormais explicitement Echeancier de ses copies et
de son inventaire. Les anciens fichiers partagés restent vérifiés octet à octet.

Aucun Git, secret, compte réel, donnée réelle, staging ou production accessible.
Aucun rapport global ni fichier partagé écrit. Le verrou détenu par le parent
n'a pas été manipulé. Les deux relectures indépendantes et la clôture appartiennent
au parent/Claude ; PRET signifie uniquement prêt à relire, pas GO.

Le résultat final, les empreintes et le nettoyage sont dans `tests/final.*`,
`tests/cleanup.json` et `tests/artifact-verification.json`. Les limites restantes
sont l'adaptateur WordPress, les canaux serveur, le cache de pages et la protection
physique des PDF, qui ne sont pas livrés ni revendiqués testés par ce moteur.

### Résultats réellement exécutés

PHP **8.2.36**, PHPUnit **11.5.58**. Passage final et préparation/rejeu dans un
second conteneur neuf : **234 tests / 29 516 assertions**, zéro erreur, échec ou
ignoré ; PHPCS PSR-12, syntaxe PHP et Composer validate strict : codes **0**.
Détail issu de JUnit : Acces **50 / 9 536**, Numeros **42 / 121**, Robots
**101 / 298**, Entreprise **41 / 19 561** (tests / assertions).

Rejeu indépendant de préparation, sans changer le code ni écraser l'historique :
`replays/autocontrole-rejeu/final.*`, `preparation.json` et `cleanup.json` dans
ce même dossier. Deux runners C-06 supprimés ; absence vérifiée par leur nom
exact et le diagnostic Docker de disparition, pas seulement un code d'erreur.
Les inventaires finaux et les vérifications de sources sont ceux du paquet
original et du rejeu, chacun dans son `artifact-verification.json`.

## Remise corrective du 21 novembre 2026

Les trois instructions techniques de `corrections/C-06.md` sont appliquées :

1. Acces ajouté au XML racine, sans configuration injectée par le lanceur.
   Reproduction avant correction : commande standard verte avec seulement
   **184 tests / 19 980 assertions** ; le nouveau garde de couverture échoue
   bien sur l'absence d'Acces. Paquet historique conservé :
   `replays/corrections-21nov-1505-red/standard-before.*`.
2. README de l'extension complété : entrées exactes, droits, sortie, découverte,
   réserves et commandes de test isolées.
3. Couplage de la liste blanche documenté dans le code et le README, sans
   ouvrir de nouvelle identité ni changer la décision d'accès.

Rejeu après dernières modifications PHP/XML/README et lanceurs :
`replays/corrections-21nov-1505/final.*`. Commande standard, XML racine :
**234 tests / 29 516 assertions**, dont **50 / 9 536** Acces, zéro erreur,
échec ou ignoré ; PSR-12, syntaxe et Composer strict : codes 0. Le garde de
couverture passe. Les deux conteneurs de ce réveil sont supprimés, leur absence
vérifiée. Les anciens paquets et sceaux sont historiques et restent inchangés ;
ils ne certifient pas les sources de cette remise. Le nouveau sceau est produit
après la mise à jour des notes et de PRET, puis contrôlé.

Les questions métier de la fusion restent ouvertes, sans modification du
comportement : sortie future, robots/PDF et PDF ancien, ainsi que les réserves
du brief. La doctrine §6 prime sur la formulation « le GO appartient à Ced »
en fin de fusion : la clôture technique appartient à Claude après second tour ;
Ced arbitre les droits et les opérations réelles. Aucune clôture, autorisation
de branchement ou publication revendiquée.

Les mentions « fichiers partagés inchangés » des paquets initiaux se rapportent
à la livraison initiale. Cette correction autorise explicitement XML racine et
README ; les bibliothèques des lots clos, Composer et lock restent protégés
par le nouvel inventaire. Les sources non métier de C-06 changent seulement
pour le branchement de la suite et sa preuve ; le seul changement du moteur
est un commentaire documentaire.

Aucun échec technique restant dans ce périmètre. Les réserves métier ci-dessus
restent à arbitrer ; le code n'est ni une intégration du paywall, ni une clôture
indépendante du lot.
