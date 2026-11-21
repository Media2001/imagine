# Relecture C-06 — Décision d'accès à un contenu (Claude, relecteur indépendant)

Lot : `wp/plugins/imagine-pilotage/src/Acces/`, `tests/Acces/`.
Brief : `briefs/C-06-decision-acces.md`. Cas de recette R-25 à R-31 (§3.9).
Rapport écrit sans ouvrir `relectures/C-06/codex.md`. Pas de fusion à ce stade.

## Méthode et exécution des tests

- Je n'ai pas pu lancer `docker compose run --rm -w /app/imagine-pilotage php composer test` : dans cette session non interactive, toute commande `docker` est refusée par la couche de permissions (quatre tentatives, toutes bloquées). Aucun PHP n'est lancé sur Windows (interdit par le README et la doctrine).
- À défaut, j'ai vérifié les **preuves scellées** du lot. `production/C-06/tests/final.json` enregistre `composer test -- --configuration tests/Acces/phpunit.xml`, `exit_code 0`, PSR-12 `0`, syntaxe `0`, `composer validate` strict `0`, et `final.log` : **234 tests / 29 516 assertions, OK**. Le rejeu indépendant (`replays/autocontrole-rejeu/final.log`) donne le même résultat.
- J'ai recalculé les empreintes SHA-256 de `src/Acces/Moteur.php`, `src/Acces/Decouverte.php`, `tests/Acces/phpunit.xml`, `tests/Acces/FermetureTest.php` et `composer.json` : **toutes identiques** à `final.json`. La preuve verte correspond donc exactement au code que je relis.
- J'ai déroulé à la main les cas R-25 à R-31 (voir §2).

## 1. Conformité

Le lot fait ce que demande le brief : une fonction de décision pure, entrées passées en arguments, sortie `complet|extrait` + motif nommé + bloc, sans jamais transporter de texte. `Decision` n'expose que `complet`, `motif`, `bloc` (`src/Acces/Decision.php`), vérifié par `DecisionTest.php:103`.

- **Fermé par défaut** : `Moteur::decider` enveloppe tout dans un `try/catch` qui rend `false / entree_invalide / abonnement` (`Moteur.php:18-23`) ; toute l'entrée est validée **avant** le moindre cas favorable, même pour ouvert, équipe ou robot (`Moteur.php:32-60`). Conforme à l'exigence « entrée manquante, incohérente ou inconnue : extrait ».
- **Le plus favorable l'emporte** : départage par `priorite()` (`Moteur.php:166-190`). Tous les motifs d'accès complet (≥ 80) dominent tous les refus (≤ 30) ; un seul droit valide ouvre donc le contenu malgré des droits négatifs. Conforme au brief (« un ancien abonné qui a acheté un numéro »).
- **Découverte** : interface `Decouverte` + deux implémentations réglables (`DureeDecouverte`, `NombreArticlesDecouverte`), aucune variante choisie, aucune valeur commerciale par défaut. Conforme à la décision 5 laissée ouverte (brief §« Ce que tu ne décides pas »).
- **Robots (C-03)** : seuls les positifs d'identité `google`/`bing` sont consommés (`Moteur.php:35,64`). J'ai vérifié que `Robots\Verificateur` pose bien `$robot->identifiant` dans `Decision->robot` (`Verificateur.php:90,112`) et que `config/robots.php:22-23` nomme ces identités `google`/`bing`. Le câblage est cohérent (arbitrage C-03/3). Le booléen d'UA seul ne suffit jamais.
- **Interprétations signalées** : les trois questions hors lot (PDF ancien, grâce au-delà du bandeau, longueur d'extrait) sont nommées et renvoyées à l'arbitrage dans `production/C-06/notes.md`. Bien. Deux interprétations restent à confirmer (voir §5, points mineurs 4 et 5).

**Écart important** : la commande exacte que le brief me demande de lancer — `composer test` — **n'exécute pas** la suite Acces. Le `composer.json` racine appelle `phpunit` avec le `phpunit.xml` racine, qui ne déclare que `Numeros`, `Robots`, `Entreprise` (`wp/plugins/imagine-pilotage/phpunit.xml:3-7`). La suite Acces n'existe que dans `tests/Acces/phpunit.xml`, jouée uniquement par le runner dédié via `--configuration`. Les notes l'assument (« Le simple `composer test` historique n'inclut donc pas encore Acces »). Conséquence : qui lance la commande documentée obtient un vert qui **n'a jamais joué les 50 tests du lot**. Voir §3, point bloquant-fonctionnel.

## 2. Exactitude métier — cas déroulés à la main

Contenu de base : réservé, numéro `170`, sortie `2026-10-01`, instant `2026-11-21`.

- **R-25 Abonné connecté** : abonnement actif dans ses dates → `abonnement()` renvoie `abonnement_actif`, `complet`, bloc `aucun` (`Moteur.php:103-105`). Article et PDF ouverts. ✔
- **R-26 Anonyme** : `identifie=false`, droits vides → décision de base `anonyme`, extrait, bloc `connexion` (`Moteur.php:69`). `Decision` ne porte aucun texte. ✔ (L'étanchéité multi-canaux REST/RSS/oEmbed est hors lot : c'est l'adaptateur. Correctement exclu.)
- **R-27 Robot vérifié / faux robot** : `DecisionRobot(VerifieDns,'google')` → `estVerifie()` vrai → `robot_verifie`, complet (`Moteur.php:64-65`). Faux robot (bon UA, mauvaise IP) → C-03 non vérifié, visiteur anonyme → extrait. ✔ (cf. `DecisionTest.php:54-85`, cas `bing` compris.)
- **R-29 Acheteur d'un numéro** : achat `170` acquis le `2026-10-02`, instant postérieur → `numero_achete`, complet pour article **et** PDF de 170 (`achat()`, `Moteur.php:127-135`) ; numéro `169` → `autre_numero`, extrait ; achat avant `acquis_le` → `achat_pas_commence`. Sans limite de durée, pas d'accès aux autres numéros ni au hors-série. ✔
- **R-30 Découverte** : compte vérifié, dans les limites → `decouverte_duree`/`decouverte_articles`, complet ; épuisée → `decouverte_epuisee`, extrait, bloc `decouverte_epuisee` ; non vérifié → `compte_non_verifie`, bloc `connexion` (`PerimetreDecouverte.php:27-42`). L'unicité « une seule fois par personne » est explicitement laissée à l'adaptateur (notes). ✔
- **R-31 Bénéficiaires / coopérateur** : `offert`/`groupe` actifs → `offert_actif`/`groupe_actif`, complet ; coopérateur seul → `cooperateur_sans_abonnement`, extrait, bloc `abonnement` (`Moteur.php:73`). ✔

Cas limites vérifiés dans le code et les tests :
- **Bornes de date** début inclus / fin exclu, à la seconde (`AbonnementTest.php:64-90` : seconde avant/après `debut` et `fin`). ✔
- **Suspension coupée dès la suspension** (arbitrage du 21/11, point 1) : `suspendu` → extrait (`Moteur.php:87-92`). ✔
- **Changements d'heure** : la durée compte des secondes écoulées, pas des heures civiles (`DureeDecouverte.php:23`, `DecouverteTest.php:48-65`). ✔
- **Coexistence** : achat de PDF ancien valable même avec abonnement expiré/suspendu/grâce (`DroitsTest.php:96-112`) ; les droits ne se neutralisent pas. ✔
- **Entrées incohérentes** : anonyme porteur de droits, doublon de droit découverte, clé en trop/en moins, date fractionnaire, robot d'identité inconnue → tous fermés (`FermetureTest.php`). ✔

Je n'ai trouvé **aucun chemin qui renvoie `complet=true` à tort** ni aucune fuite de texte réservé.

## 3. Tests

- **Passent-ils ?** Oui d'après les preuves scellées (234/29 516, exit 0), et la preuve correspond au code (empreintes recalculées identiques). Je n'ai pas pu les relancer moi-même (Docker bloqué en session non interactive) ; je le signale au lieu de l'affirmer.
- **Couverture des cas limites** : forte. Table d'abonnements de 30 lignes (`AbonnementTest::table`), tous les 2^11 sous-ensembles de droits dans les deux ordres (`DroitsTest.php:56-94`), bornes de secondes, DST, quota sans consommation, fermeture défensive par mutation de chaque clé.
- **Les tests vérifient-ils la règle ou répètent-ils le code ?** Ils vérifient la règle : l'oracle attendu est reconstruit indépendamment (ex. `AbonnementTest::table` recompose `complet/motif/bloc` à partir de l'état ; `DroitsTest` ordonne les droits du moins au plus favorable et attend le dernier sélectionné, ce qui épingle réellement le départage et son indépendance à l'ordre). Bon niveau.

**Point important (fonctionnel, pas un échec de test)** : la suite Acces n'est pas raccordée au `composer test` par défaut (voir §1). Le `tests/Acces/phpunit.xml` est un sur-ensemble (il inclut les quatre suites), mais le `phpunit.xml` racine ignore Acces. Il n'y a pas de conflit réel qui l'empêcherait : le lot parallèle Echeancier n'a pas de suite PHPUnit (`tests/Echeancier/run.php` seul). **À corriger** : ajouter `<testsuite name="Acces"><directory>tests/Acces</directory></testsuite>` au `phpunit.xml` racine, pour que les tests du lot tournent sous la commande standard et ne pourrissent pas en silence. Sinon la non-régression documentée du projet ne couvre jamais C-06.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle ; fixtures fictives, numéros opaques, adresses de test uniquement.
- **Paywall / étanchéité** : `Decision` ne transporte que trois valeurs scalaires (bool + deux enums), jamais de texte, HTML, URL de PDF ou extrait. Le moteur ne lit ni base, ni session, ni horloge, ni réseau. Aucune exception n'accorde l'accès (`try/catch` + `FermetureTest::testExceptionDateInjecteeEstFermeeSansEchapper`, `testConfigurationDecouverteInvalide...` avec une politique qui lève sur `estValide`).
- Les canaux serveur (page, REST, flux, oEmbed, recherche, cache, protection physique des PDF) sont explicitement hors lot : c'est le futur adaptateur. Périmètre correct ; pas de revendication d'étanchéité multi-canaux ici.

Aucune faille relevée dans le périmètre du lot.

## 5. Doctrine

- PHP 8.2, `declare(strict_types=1)`, PSR-12 (vert), espace de noms `Imagine\Pilotage\Acces` : conforme (doctrine §5, brief).
- **Standard d'abord** : les trois pages officielles Memberships/Subscriptions sont consignées (`production/C-06/sources-officielles.json`) ; le moteur ne refait ni la persistance ni les écrans natifs, il centralise la seule décision métier. Conforme §4.
- **Logique métier hors WordPress** : respectée intégralement.

**Point mineur (doctrine §5)** : le `README.md` de l'extension (`wp/plugins/imagine-pilotage/README.md`) n'a **pas** de section C-06/Acces — son titre s'arrête à « C-01 à C-04 ». La doctrine §5 impose que chaque module sur mesure documente « ce qu'elle fait, ses réglages, comment lancer ses tests ». Aujourd'hui l'usage, les contrats d'arguments et la commande de test ne vivent que dans `production/C-06/notes.md`, hors du code livré. Ajouter une section C-06 au README.

## 6. Études

Sans objet (lot de code). Les sources documentaires sont néanmoins citées avec adresse et constat dans `sources-officielles.json` ; rien d'affirmé sans source.

## Verdict

**À corriger.**

Points classés :

- **Important**
  1. La suite de tests Acces n'est pas branchée sur le `composer test` par défaut (`phpunit.xml` racine n'a pas la suite `Acces`). La commande même du brief ne joue pas les 50 tests du lot ; risque de fausse confiance et de non-régression aveugle. Ajouter la suite au `phpunit.xml` racine.

- **Mineur**
  2. `README.md` de l'extension non mis à jour pour C-06 (doctrine §5). L'usage et le mode de test ne sont documentés qu'en `production/`.
  3. La liste blanche `['google','bing']` est codée en dur dans `Moteur.php:35,64` et duplique les identités de `config/robots.php`. Un robot futur approuvé par le référenceur serait fermé en extrait (régression d'indexation) tant qu'Acces n'est pas mis à jour. Sans fuite ni blocage d'un humain, mais couplage à documenter ou à partager via une constante.
  4. Interprétation à confirmer : un contenu à sortie future (`sortie > instant`) est traité comme `entree_invalide` et fermé, y compris pour l'équipe ou un robot (`Moteur.php:44`). Non demandé par le brief, signalé dans les notes ; confirmer qu'aucun besoin de prévisualisation avant parution ne passe par cette décision.
  5. Interprétation à confirmer : un robot vérifié reçoit `complet` pour un contenu `type=pdf` exactement comme pour un article (`Moteur.php:64`). Le tableau du brief dit « Complet » sans distinction (donc conforme), mais §3.9 formule l'exception robot autour du *texte de l'article* et impose un contrôle du droit « à chaque téléchargement » du PDF. À confirmer avec Imagine.

Aucun point **bloquant** : pas de fuite de texte réservé, pas d'octroi d'accès erroné.

Rappel : ce verdict n'est pas un GO. `codex.md` existe ; la fusion (`corrections/C-06.md`) reste à faire dans un second temps, non réalisée ici conformément à la consigne.
