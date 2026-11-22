# C-06 — reprise du 22 novembre 2026

## Livraison actuelle

Trois politiques réglables, avec défauts prudents et deux positions testées.
Le moteur reste en PHP pur ; un adaptateur WordPress optionnel expose les trois
réglages. Aucun bootstrap partagé modifié : raccordement au parent/futur branchement.

Relus entièrement : consigne permanente, doctrine du 22/11, A-FAIRE du 22/11
13 h 20, brief C-06, corrections/C-06 et notes précédentes, arbitrages du 22/11,
décisions, cahier des charges v3.1 et exigences C-01. C-01/C-02/C-03 clos ;
C-05/C-07 exclus des dépendances. Aucun fichier de recette ouvert ou automatisé.

## Réglages et motifs

`Acces\Reglages` est final readonly ; ses trois booléens sont `false` par défaut.
`depuisOptions` normalise le stockage externe, `options()` fournit la forme canonique.
Option WordPress unique : **`imagine_acces_reglages`**.

| Clé | Défaut | Autre valeur | Propriété |
|---|---|---|---|
| `contenu_futur` | `ferme_tous` | `equipe` | `contenuFuturEquipe` |
| `pdf_robot` | `extrait` | `complet` | `pdfRobotComplet` |
| `pdf_anterieur_abonnement` | `ferme` | `ouvert` | `pdfAnterieurAbonnement` |

Option absente/malformée : défauts prudents. Position inconnue/mal typée : défaut
pour ce champ ; clés inconnues supprimées. Comparaisons strictes, pas de coercition
de vérité. Huit combinaisons testées en aller-retour, normalisation idempotente.

L'ensemble des entrées/droits reste validé **avant** tout accès favorable.
Un sixième argument autre que `null` ou `Reglages` ferme l'entrée.

- Sortie strictement future : fermé pour tous, même contenu marqué ouvert,
  équipe et robots. Position `equipe` : seuls les identifiés rédaction/administration
  ouvrent. Aucun autre droit ne traverse ce verrou. Prévisualisation WordPress
  hors moteur. À la seconde de sortie, règles normales.
- Robot C-03 vérifié : article complet ; PDF réservé en extrait par défaut,
  complet sur l'autre position. Faux robot : aucun droit acquis.
- PDF paru avant début d'abonnement : fermé sur ce seul droit par défaut, ouvert
  sur l'autre position. Personnel/offert/groupé, actif/grâce dans les dates ;
  la grâce garde le bloc régularisation. Aucun état négatif/hors dates réactivé.
- Le plus favorable reste applicable : achat perpétuel du numéro, équipe et autre
  droit valide indépendants. Un contenu ouvert déjà paru reste complet pour tous.

J'ai compris les réglages PDF comme les limites du droit robot/abonnement,
**pas comme un veto** retirant un autre droit favorable du tableau du brief.

Motifs définitifs : `contenu_futur_ferme_par_reglage`,
`contenu_futur_equipe_par_reglage`, `pdf_robot_extrait_par_reglage`,
**`pdf_anterieur_ferme_par_reglage`** (`Motif::PdfAnterieurFermeParReglage`).
Le motif provisoire n'existe plus dans le code métier. En position ouverte,
les motifs favorables existants restent stables.

## API et seam administration à raccorder

```php
$decision = (new Imagine\Pilotage\Acces\Moteur())->decider(
    $contenu, $visiteur, $decisionRobotC03, $instant,
    $politiqueDecouverte, // null si aucun droit découverte
    $reglages,            // sixième argument ; null/omis = trois défauts prudents
);
```

Les cinq premiers arguments, les droits et les contrats exacts restent ceux
expliqués dans `notes.md` (historique). Dates immuables à la seconde entière,
début inclus/fin exclue. Aucune lecture d'horloge/base/session/réseau dans le
moteur et les objets métier. Toute entrée incohérente ferme ; aucune exception
n'ouvre. `Decision` porte seulement bool + motif + bloc, aucun texte/HTML/URL PDF.
Découverte durée/quota inchangée, paramètres obligatoires sans offre choisie.

Seule couche WordPress ajoutée : **`src/Acces/AdministrationReglages.php`**.
Le futur bootstrap devra appeler une fois, après autoload :

```php
$administrationAcces = new Imagine\Pilotage\Acces\AdministrationReglages();
$administrationAcces->brancher();
// À chaque requête : lire l'instantané courant et le passer au moteur.
$reglages = $administrationAcces->lire();
```

Hooks admin_menu/admin_init ; sans effet au chargement/constructeur. Page
**Réglages → Accès Imagine**, slug `imagine-acces`, capacité `manage_options`.
Trois listes de deux choix ; sélection relue, français traduit (`imagine-pilotage`)
et échappé. register_setting : type array, défauts, normaliseur, show_in_rest=false.
Formulaire vers options.php ; settings_fields délègue nonce et groupe au cœur.
Aucun POST/stockage maison. Sans capacité : aucun rendu. Panne de lecture : défauts.

Standard officiel consulté avant l'adaptateur : Settings API, register_setting,
settings_fields (voir `sources-officielles-22nov.json`). Memberships/Subscriptions :
constats précédents dans `sources-officielles.json`, pas de persistance refaite.

**Limite explicite :** tests PHP réels du contrat d'administration avec doubles
`WordPressFictif`, rendu HTML/DOM et normalisation → relecture → décision.
Ce ne sont pas des tests du cœur WordPress, HTTP/CSRF ou de sa persistance.
Aucun site démarré. Bootstrap partagé, cache, canaux paywall, protection physique
PDF et décompte atomique découverte restent au futur branchement.

## Preuves exécutées et TDD

Paquet actuel : **`production/C-06/replays/reglages-22nov/`**.

- baseline : **234 tests / 29 516 assertions**, avant changement métier.
- red-robot-default : vraie assertion, PDF robot complet avant correction.
- red-robot-setting : classe absente ; red-robot-value : vraie assertion,
  position complète ignorée. red-future : ancien motif entrée invalide ;
  red-old-pdf : ancien motif provisoire ; red-coexistence : achat masqué.
- red-options / red-admin : API/adaptateur encore absents.
- green-* : passages après chaque tranche verticale. Les premiers écarts PSR-12
  sont conservés ; PHPCBF ciblé ensuite exécuté dans le conteneur.
- **final : 247 tests / 30 368 assertions**, zéro échec/erreur/ignoré ;
  PSR-12, syntaxe PHP et Composer validate strict : **codes 0**.

| Suite jouée | Tests | Assertions |
|---|---:|---:|
| Acces | 63 | 10 388 |
| Numeros (clos) | 42 | 121 |
| Robots (clos) | 101 | 298 |
| Entreprise (clos) | 41 | 19 561 |

Couverture : deux positions de chaque réglage, huit combinaisons, rôles équipe,
vrais/faux robots, PDF/article, ouvert/réservé, trois familles d'abonnements et
cinq états, bornes à la seconde, droits indépendants, stockage invalide/panne,
et contrat administration. Toutes les suites closes historiques restent jouées.

PHP **8.2.36**, PHPUnit **11.5.58**, uniquement conteneur jetable WSL. Aucun
montage/volume/port/privilège/service web ou DB ; entrypoint sleep. Dépendances
installées uniquement dedans, réseau déconnecté avant tests/lint. SHA-256 des
copies vérifiés. Conteneur principal supprimé, absence vérifiée par nom exact.

Preuve complémentaire : `replays/cleanup-bridge-22nov/failure-cleanup-proof.json`.
Le nettoyage réussit avant déconnexion réseau et avec une dérive **synthétique
du manifeste de test**, sans modification de source protégée. Le reçu indique
honnêtement shared_sources_unchanged=false pour ce cas volontaire. Runner supprimé.

## Commande parent bornée

Depuis `C:/Users/Ced/imagine` :

```bash
python -B wp/tests/acces-runner/replay.py
```

Paquet parent-<identifiant> neuf ; préparation, tests/lint/syntaxe/Composer,
contrôle de couverture, nettoyage en finally, scellement et contrôle. Bornes
par sous-processus : 420 s / 180 s / 30 s / 60 s / 60 s / 60 s. Refuse tout
paquet existant. Échec non nul : pas de sceau de succès.

Contrôle sans rejouer ni installer de dépendances :

```bash
IMAGINE_C06_PACKET=reglages-22nov python -B wp/tests/acces-runner/verify.py check
```

**Composition bornée volontaire :** XML racine partagé incluant désormais Envoi,
non clos, donc exclu comme Echeancier. Commande réelle :
`composer test -- --configuration tests/Acces/phpunit.xml --log-junit /tmp/result.xml`.
C-06 et trois suites closes seulement ; ce n'est pas le rejeu de la composition
racine entière. La présence d'Acces dans le XML racine (correction du 21/11)
est conservée, sans écriture partagée. Garde de couverture et nouvelles classes vérifiés.

## Fichiers et relais parent

Modifiés : Moteur, Motif, AbonnementTest, FermetureTest ; run.py, verify.py,
check-standard-suite.py ; notes/PRET. Ajoutés : Reglages, AdministrationReglages ;
ReglagesTest, OptionsReglagesTest, AdministrationReglagesTest, WordPressFictif ;
replay.py, ces notes, sources officielles et reçus de reprise.

Composer/lock, XML racine, README plugin et sources closes non écrits.
C-05/C-07 et leurs preuves ni importés ni modifiés. **README partagé à actualiser
par le parent** : il décrit encore le PDF robot complet du 21/11 ; interdit au worker.
**Branchement du bootstrap partagé à coordonner par le parent** comme indiqué ci-dessus.

Aucune règle ouverte ne bloque plus C-06 : trois réglages conformément à doctrine §4.
Longueur d'extrait, offre découverte et branchement grâce hors de cette décision.
PRET = prêt à relire, pas clôture ni GO ; deux relectures/second tour au parent/Claude.
Ni Git, verrou, rapport global, archive/donnée/compte réel, staging ou déploiement.
Les preuves historiques et `notes.md` restent identifiées comme historique du 21/11.
