# B-08 — Livraison et rejeu

## Corrections du 27 novembre 2026 — paquet courant

Le paquet initial ci-dessous est **historique**, ses comptes ne qualifient pas les corrections. Le paquet courant est `corrections-final.json`, contrôlé par `python -B production/B-08/verifier.py` (sans argument, Python 3.11). Le PRET initial a été retiré et conservé dans `PRET-avant-corrections-20261127` ; le nouveau PRET n’est posé qu’après ce contrôle et la préparation d’image réelle.

- Bouchon corrigé **avant** le code : `wp_insert_post` déséchappe récursivement les valeurs de `meta_input`, comme `update_metadata`. `corrections-red-slash.log` constate le refus du POST pourtant valide. Le correctif ne touche que la frontière d’écriture (`wp_slash($meta)`), les valeurs propres restent utilisées pour la relecture stricte. Le cas conserve aussi le nom à antislash, l’apostrophe et le saut de ligne.
- Le menu est identifié dès `wp_create_nav_menu`, les items dès `wp_add_nav_menu_item`, avec relecture du témoin et option progressive. Reprise démontrée à la troisième création, après sauvegarde complète **et avant rattachement natif** d’un item. Un menu étranger, un marqueur retiré, un item ajouté sans témoin, une référence détournée ou un item rattaché ailleurs sont refusés. Les tests réels sont dans une transaction InnoDB rollbackée ; utilisateurs, commandes classiques/HPOS, navigation et options métier sont relus après chaque scénario.
- Une URL de parts `http` est refusée aussi en lecture d’une ancienne option invalide. Le seed ne lit de permalink que pour une page publiée existante ; il ne pose un lien d’archive que pour un type enregistré doté d’une archive. Repli explicite pour une cible absente : URL custom **vide**. La page de compte n’utilise plus le repli Woo vers l’accueil.
- README complété pour B-06/B-07/B-08, par sections contrôlées et non par gel de tout le fichier partagé. Colonne de confort admin optionnelle **non ajoutée**, aucune fonction nouvelle.
- La vraie recette HTTP existante est étendue : POST anonyme, sujet et nom à antislash, détail admin exact et callback natif d’export C-21/WordPress exact. Les réglages don/parts reviennent à leur absence/valeur initiale, les deux propositions sont retirées, l’observateur et les scripts temporaires aussi. Aucun appel à CoopHub, aucun don ni paiement.

### Commandes de qualification (depuis la racine)

Toutes les commandes Python utilisent `PYTHONIOENCODING=utf-8` dans le shell Bash, et `-B` (aucun cache dans le dépôt). Sous PowerShell, les deux scripts canoniques sans argument s’exécutent tels quels.

```text
python -B wp/outils/demo/b08-local.py corrections-final-local
python -B wp/outils/demo/b08-mutations.py corrections-final-mutations
python -B wp/outils/demo/b08-corrections.py runtime corrections-final-reprise
python -B wp/outils/demo/b08-corrections.py runtime corrections-final-cibles cibles
python -B wp/outils/demo/b08-corrections.py runtime corrections-final-collisions collisions
python -B wp/outils/demo/b08-corrections.py runtime corrections-final-mutant-item collisions item-etranger
python -B wp/outils/demo/b08-corrections.py runtime corrections-final-mutant-cible cibles cible-absente
python -B wp/outils/demo/b08-corrections.py deploy corrections-final-deploiement
python -B wp/outils/demo/b08.py seed corrections-final-pages-menu
python -B wp/outils/demo/b08-recette.py corrections-final-http
python -B wp/outils/demo/b08-gates.py prepare corrections-final-preparation
python -B wp/outils/demo/b08-gates.py regression corrections-final-canonique
python -B wp/outils/demo/b08-corrections-finaliser.py
python -B production/B-08/verifier.py
```

Les deux commandes `mutant-*` doivent sortir **1**, avec un contrôle métier rouge et une restauration verte ; jamais assimilées à une recette verte. Les wrappers `prepare`/`regression` exécutent et enregistrent respectivement les commandes exactes :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Sources et reçus sont liés aux octets courants par le sceau corrigé ; les rouges et les reçus initiaux restent historiques. Les scripts de qualification ne gèrent ni Git, ni file, ni verrou. Validation visuelle de Ced toujours attendue. C-26 est repris séparément par le parent, aucun de ses critères n’est revendiqué ici.

## Livraison initiale — historique


## Standard d’abord — cinq lignes

1. Les pages et relations parent/enfant WordPress suffisent aux sept pages éditoriales vides ; `wp_insert_post()` crée les seules pages absentes.
2. Le menu natif et `wp_nav_menu()` suffisent à la navigation ; le thème ne reçoit qu’un raccord conditionnel dans son en-tête et conserve son repli B-01.
3. L’API Settings native suffit aux deux réglages, avec capacité administrative et nonce natifs ; défaut don fermé, URL vide.
4. Il manque au standard le sens « proposition de sujet locale » : un type de contenu privé, sans REST, sans recherche publique ni transport, avec boîte de lecture administrative.
5. Les outils de confidentialité natifs reçoivent deux callbacks additifs par adresse ; aucun besoin de toucher C-21, d’ajouter une table, une extension, un paiement ou une intégration CoopHub.

Documentation officielle consultée, quatre réponses HTTP 200 : `standard-officiel.json` (fonctions `wp_insert_post`, `wp_nav_menu`, guides Plugin Handbook des exporteurs et effaceurs de données personnelles).

## Code et stockage

`wp/plugins/imagine-site/{CooperativeRegles,Cooperative,Soutenir,SujetRegles,Sujet,SujetConfidentialite}.php`, tests correspondants dans `tests/`. Bootstrap additif B08 ; blocs B05/B06/C24/B07/C25 préservés. Seule modification du thème : `wp/themes/imagine/header.php`, sélection du menu natif sans nouveau style.

Les propositions sont des lignes `wp_posts`, type `imagine_sujet`, statut `private`, titre neutre et corps vide ; nom/email/texte/consentement/date sont dans `wp_postmeta`, clés `imagine_sujet_*`. Pas de compte créé, de newsletter ni de copie dans un journal. Les deux outils natifs fonctionnent aussi par adresse sans compte ; le dépôt ne conserve aucune proposition d’essai. Les préimages privées (base incluant HPOS et navigation, sessions avant création) vivent dans le scratch privé, seul identifiant opaque et SHA-256 publiés.

`imagine_soutenir` porte don et URL ; option absente à la livraison = défauts fermés. `imagine_b08_pages` et `imagine_b08_menu` identifient les seuls contenus/menu de ce lot. La création est rejouée deux fois et relue ; aucune page d’un lot antérieur n’est réécrite. Les huit entrées principales respectent §3.1 ; les sept sous-pages éditoriales sont des enfants natifs du menu. « Proposer un sujet » reste hors menu.

## Commandes réellement exécutées

Depuis `C:\Users\Ced\imagine`, Python 3.11.15 (interpréteur réellement exécuté), sorties UTF-8 ; PHP de tests 8.2.33, PHPUnit 11.5.58 :

```text
python wp/outils/demo/b08-local.py horslive-final
python wp/outils/demo/b08-mutations.py
python wp/outils/demo/b08-gates.py prepare preparation-image
python wp/outils/demo/b08-gates.py regression canonique
python wp/outils/demo/b08-recette.py recette-livraison
python wp/outils/demo/b08-finaliser.py
python production/B-08/verifier.py
```

Les noms de reçus sont immuables : utiliser un nom neuf pour un nouveau rejeu. Les recettes live refusent tout site autre que `imagine-test-demo` et contrôlent préalablement le coupe-circuit mail/HTTP/paiements B00. Les mutations ne tournent que sur des copies en conteneur sans réseau : jamais sur le site.

- TDD : reçus rouges `red-structure`, `red-soutenir`, `red-sujet`, `red-abonnement`, puis verts. L’URL de l’abonnement a été corrigée sur la découverte réelle de l’emplacement B-01, et non par création d’une page imaginaire.
- Hors live : **6 tests, 181 assertions**, pagination d’export 101 propositions, trois tranches d’effacement, tiers préservé, échecs de lecture/écriture/suppression, nonce et capacités, consentement décoché, transports nuls.
- **12 mutations sources détectées** : don fermé, lien commercial, case cochée, mail, HTTP, statut privé, exposition REST/public, export vide, effacement absent, lecture masquée et nonce supprimé. Le premier mutant nonce survivait parce que le cas invalide omettait les autres champs ; reçu conservé, cas complété, les 12 rejoués rouges sans erreur PHP. Rien n’a été renommé vert.
- Préparation d’image canonique refaite ; suite globale **1 149 tests, 36 036 assertions, 0 échec/erreur/ignoré**, **18 outils, 417 contrôles**, code 0. Soit les 1 143 tests C25 de départ plus les six tests B08.
- HTTP réel : pages publiques, menu, OFF/ON, lien parts, deux POST anonymes (adresse d’un compte/adresse sans compte), message uniforme, nonce refusé, lecture admin, export et effacement ciblés, témoins publics avant les absences. Aucun appel de B08 aux transports ; les éventuelles tentatives d’ambiance WordPress sont distinguées et bloquées par B00.
- La première recette HTTP rouge portait sur l’apostrophe typographiée native et un sélecteur de recherche inexistant ; état métier restauré malgré l’échec, reçu gardé. Le contrôleur corrigé vérifie la vraie liste de résultats et l’affichage typographié, pas une réponse fabriquée.

Les reçus finaux, leur empreinte, le lien aux sources exécutées, la restauration et les portes de `PRET` sont contrôlés par `verifier.py`. Les fichiers d’orchestration et les bibliothèques closes ne sont pas épinglés ni modifiés. Les comparaisons de bootstrap sont par bloc B08, non par empreinte globale d’un fichier partagé.

## Limites et décisions à défaut

Aucun framework ajouté ; pas de conception graphique, de texte éditorial, de paiement, de don même d’essai, d’installation sur l’hôte ni d’écriture Git dans la livraison. Le don activé n’est qu’un emplacement de démonstration sans action. L’URL de parts est volontairement vide : aucun accès CoopHub n’a été tenté. Consentement de recontact facultatif, conforme à la seule case demandée ; aucune réutilisation commerciale.

Le « S’abonner » existant est un emplacement B-01, pas un tunnel livré par B08. Les titres enregistrés sont exactement ceux du §3.12 ; les apostrophes d’affichage suivent WordPress. La protection B06 reste indépendante. Ces pages publiques ne sont pas ajoutées à C23 ; l’extension transversale C26 demeure le lot suivant. Validation visuelle à Ced ; aucun blocage métier retenu.
