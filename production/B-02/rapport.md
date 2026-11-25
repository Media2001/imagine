# B-02 — Corrections de fusion, 25 novembre 2026, 21 h 58 CET

1. **Fait** : garde Memberships, quatre positions indépendantes du calendrier, deux paiements natifs raccordés, bloc courant renouvelé via Moteur, attente virement réservée à bacs, cœur pur et hook postal redondant retiré.
2. **Prêt à relire** : corrections B02 ; 138/138 contrôles natifs/HTTP/préservation, 9 nouveaux tests PHPUnit (73 assertions), 2 tests du runner. T01 canonique : 1023 tests, 34094 assertions, aucun échec/erreur/ignoré.
3. **À valider** : visuel par Ced ; marge C05, historique d’activation/compteur C01 et documents restent non raccordés ; aucun changement de droits ou de paiement.
4. **Bloqué** : aucune panne technique restante. Acceptation complète toujours partielle, strict **exit 2**, cinq réserves observées ci-dessous.
5. **Ensuite** : relecture de la fusion corrigée ; aucun travail sur C15, les files/verrous, les bibliothèques closes ou les autres lots.

## Preuves actuelles

- `corrections-20261125/resultats.json` : **73 natifs + 8 états + 51 HTTP + 3 readbacks applicatifs + 3 gardes = 138/138**, zéro échec. Rejeu strict sans réinstallation, sortie 2. Trois fichiers seulement déployés et relus : MonCompteRegles.php, MonCompte.php, parts/mon-compte.php. Aucun bootstrap partagé, functions.php ni autre fichier du thème écrasé.
- `corrections-preparer-image.log` : préparation obligatoire réellement exécutée, exit 0 ; image `sha256:8f56b898f0963a86caf5a55cce9ee526e7b6d17c33d3cc8172a1dc7b277a2917`, PHP 8.2.33, quatre paquets. Aucun script T01 modifié.
- `corrections-t01-final.log` : T01 isolé canonique, **1023 tests / 34094 assertions**, zéro échec, erreur ou ignoré. Paquet imagine-site : 59 tests / 346 assertions. Les 9 tests B02, dont les bornes exactes de grâce/fin, passent dans ce paquet. La première exécution T01 a révélé que le thème n’est pas copié parmi les paquets ; test corrigé pour lire le montage source T01, puis rejeu vert ; le reçu FAIL initial reste conservé.
- Les logs `corrections-red-*` et `corrections-red-native.json` conservent les rouges fonctionnels avant les corrections : état pur absent, projection absente, premier bloc figé, deuxième règlement omis, ambiguïtés, fatale Memberships, hook doublonné, gabarit et runner.
- Le premier strict a aussi constaté des mutations **concurrentes d’A-VIR (98)** pendant son snapshot : début/statut/fin puis restauration, quatre observations postales ajoutées entre 20:52:51.19 et 20:52:51.77 UTC. Reçu intégral conservé dans `corrections-first-strict-failure.json` (exit 1, garde non affaiblie). B02 n’a fait aucun save sur ce profil. Rejeu distinct : empreintes natives, rôles, options, lots clos et thème partagé conservés ; **zéro observation postale ajoutée**. Aucune donnée restaurée ou réinitialisée pour faire passer le test.

## Décisions prises à défaut

- `cancelled` ⇒ **Expiré**. `pending` sans bacs ⇒ **Paiement en attente de validation**, et non « virement ». `on-hold` + adhésion pending/delayed ⇒ virement seulement si `get_payment_method() === 'bacs'` ; sinon Suspendu ou grâce dans la fenêtre native `[début, fin[`. Sans API Memberships, on-hold ⇒ Suspendu. Ce sont des libellés, pas des droits.
- Projection pure recevant données et heure. La commande initiale puis les relations de renouvellement natives sont triées chronologiquement, contrôlées par propriétaire et dédupliquées par ID. Dates de confirmation et dates théoriques C05 ne sont jamais confondues. Deux commandes au même instant ou un ID contradictoire : positions concernées signalées ambiguës, détail des commandes connues conservé ; les autres positions fiables restent lisibles.
- Renouvellements d’année : représentation C13 native déjà contrôlée, puis `Moteur::renouveler()`. Cas pur exact **171–174 → 175–178**. Au-delà de l’anniversaire sans renouvellement fiable, « Bloc courant indisponible — renouvellement non raccordé », jamais le premier bloc présenté comme actuel. En 4× sans rang de bloc explicite, on ne transforme pas chaque règlement trimestriel en année.
- Suppression du callback postal de MonCompte : **EnvoiNatif relève déjà toutes les sauvegardes natives**. L’ancienne affirmation « limité au formulaire client » était fausse et est retirée du code actuel ; les anciennes preuves ci-dessous sont historiques.
- HTTP : GET d’isolation, consultation étrangère, POST forgé et nonce invalide conservés et rejoués ; le parcours positif de modification/restauration d’adresse reste dans le test mais **n’est pas exécuté** dans ces corrections, conformément à l’interdiction de modifier les données. Pas de paiement, passerelle, jeton de paiement, droit, rôle, fixture ou queue modifié.

## Réserves réelles (strict exit 2)

1. Marge C05 non renseignée : aucune date théorique fabriquée.
2. Historique activation/réactivation C01 non raccordé : compteur restant indisponible.
3. Factures/justificatifs : raccord documentaire non disponible.
4. A-VIR : méthode native vide, donc aucun virement identifié sur ce profil ; libellé générique correct. Les branches bacs/carte/inconnu sont couvertes en pur, pas par une fausse passerelle installée.
5. Édition positive d’adresse non rejouée dans ce périmètre sans mutation ; preuves historiques séparées.

**Ne sont plus des réserves** : A-SEPA4 existe et affiche **2 Payée / 2 À venir** ; A-SUSP a sa commande native failed et son bandeau HTTP ; A-CARTE possède un paiement natif validé. `acceptance_blockers` est calculé depuis les contrôles réels et testé sur jeux complets/incomplets, sans alias a-4x-j45.

## Écarts à reporter par Claude dans docs/ecarts.md

**25 novembre 2026** : le brief renvoie par erreur au §3.10 (Newsletters), le contenu compte relève des §3.7/3.8/3.9 ; `a-4x-j45` est une erreur de brief, profil applicable **A-SEPA4**. Le dossier docs/ est interdit au worker : écarts consignés ici, sans écriture hors périmètre.

## Fichiers de cette correction

`wp/plugins/imagine-site/{MonCompte.php,MonCompteRegles.php,tests/MonCompteReglesTest.php,tests/MonCompteAdapterTest.php,tests/b02-adapter-fixture.php}` ; `wp/themes/imagine/parts/mon-compte.php` seulement ; `wp/outils/demo/b02.py` ; `wp/tests/demo/{b02-runtime.php,b02-state.php,b02-http.py,test_b02_runner.py}` ; preuves et documentation sous `production/B-02/`. Bootstrap/README partagés inchangés.

---

# Historique antérieur à la fusion B02 — reçu de livraison du 25 novembre 2026

**Tout ce qui suit est historique, non un constat actuel. Les reçus JSON et logs anciens n’ont pas été réécrits. Le hook limité au formulaire et les anciens manques de paiement ci-dessous sont périmés ; voir le rapport de correction en tête.**

1. **Fait** : cinq rubriques Mon compte, données natives, PDF C11/C14, édition postale Woo/WCS et isolation réelle GET/POST.
2. **Prêt à relire** : squelette technique inspectable, 144/144 contrôles techniques. **Aucun PRET**, conformément à la délégation.
3. **À valider** : visuel par Ced ; manque nominatif C09 et données non raccordées explicités ci-dessous.
4. **Bloqué** : réception complète A-4x-J45 / quatre échéances payées-à-venir et action après rejet non prouvables avec les objets actuellement disponibles sans inventer des états de paiement.
5. **Ensuite** : vérification indépendante du parent effectuée : 144 contrôles techniques verts, code strict 2 maintenu. Corrections C13/C14 traitées séparément ; réception B02 nominative toujours partielle.

## Résultat réel

Dernière commande : `PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/b02.py --deploy --require-complete`, **exit 2**. Technique : 75 assertions PHP native + 8 états/gardes + 54 HTTP + 4 readbacks/syntaxes + 3 gardes = **144/144**. Recettes avec vrais cookies WordPress et vrais objets HPOS, pas un rendu local simulé. Runtime relevé : PHP 8.3.32, WordPress 7.0.9, Woo 11.2.2, Subscriptions 9.4.1, HPOS actif. Image de tests préparée et vérifiée séparément, PHP 8.2.33.

## Ce qui est branché

- Dashboard et navigation Woo existants, cinq sections HTML sans nouvelle CSS. Formule, état en clair, premier/dernier C01 théoriques, prochaine date/montant récurrent natifs, moyen de paiement absent nommé comme tel.
- Quatre positions visibles en A-SEPA4 ; aucune date C05 sans marge obligatoire, aucun état payé inventé. Bandeau suspendu/grâce avec lien natif ; branche failed peut pointer sur le paiement natif d'une commande propre lorsque présent.
- Numéros/PDF recalculés par C11/C14 ; A-SUSP n'a aucun lien, P-NUMERO un seul.
- Adresse native de la souscription, même source que C13. Vrai POST avec nonces, modification relue en souscription/client/relevé/HTTP, puis restauration. Les deux observations nouvelles sont conservées append-only ; aucun ancien relevé réécrit. Les notes natives d'édition restent présentes.
- Isolation : dashboard aux IDs changés, détail de souscription étrangère, commande étrangère, formulaire d'adresse étranger, POST forgé et nonce invalide, session anonyme. Titulaire recontrôlé, aucun ID HTTP utilisé pour choisir l'identité du modèle.
- Liste de factures/justificatifs explicitement vide ; commandes non rebaptisées factures.

## Limites de réception, sans maquillage

1. **`a-4x-j45` n'existe ni dans C09 ni sur le site.** Aucun alias ni nouveau profil fabriqué. A-SEPA4 sert seulement à inspecter quatre lignes, pas à attester deux règlements sur quatre.
2. Marge C05 actuellement `null`, conformément au réglage clos : aucun défaut de jours décidé par B02. Quatre dates métier ne peuvent donc pas être publiées.
3. Historique activation/réactivation C01 non raccordé : nombre restant nommé indisponible, pas le « 3 » attendu en C09 inventé. Factures/justificatifs sans connecteur : liste vide nommée.
4. Aucun ordre failed natif sur les profils demandés. Bandeau suspendu et son action de gestion réellement testés, mais pas de preuve HTTP positive d'une échéance rejetée ; aucun rejet/paiement fabriqué pour la produire.
5. A-CARTE est administrativement actif sans paiement validé. Identité adresse/source postale prouvée, **inclusion positive dans un export C07 non attestée**. La réserve C13/C09 n'est pas rouverte ou effacée.

## Décisions prises à défaut

Standard d'abord : réutilisation My Account, formulaire/adresses, nonces et actions Woo/WCS, documentation officielle et classe native lues. Adaptateur local limité à la projection/structure absente du standard. Le vrai test a trouvé que C13 écoute `woocommerce_after_order_object_save` alors que WCS 9.4.1 sauvegarde sous `woocommerce_after_subscription_object_save` : B02 ajoute ce raccord vers `EnvoiNatif::relever` existant et dédupliqué, **sans modifier le code C13 ni les bibliothèques closes**. Les options métier, rôles, contrats et droits sont préservés ; seules les observations/notes légitimes de l'aller-retour d'adresse s'ajoutent.

Le §3.10 est « Newsletters et segmentation », pas Mon compte : application du minimum explicite du brief, aucune fonction Brevo ajoutée. Les éléments visuels attendent Ced ; pas de règle métier nouvelle ni de valeur financière décidée ici.

**Signal prioritaire au parent au contrôle final : `corrections/C-13.md` et `corrections/C-14.md` sont maintenant présents et arbitrés « À corriger ».** C13 : bénéficiaires/groupés, renouvellements, gel du calendrier persistant et tests autonomes ; C14 : droit acquis indépendant du catalogue mutable, remboursement partiel réglable et état documentaire. Ils n'ont pas été traités dans cette délégation B02, dont les dossiers de restitution excluent C13/C14. Le texte B02 ne prétend plus attester le gel C13 : une assertion rouge puis verte garde cette limite. Le raccord de sauvegarde postale est limité au formulaire client (`did_action('woocommerce_customer_save_address')` + titulaire), pas aux saves génériques des autres lots ; canari natif non persisté rouge puis vert, sans aucun faux paiement.

## Fichiers

Applicatif : `wp/plugins/imagine-site/{MonCompte.php,imagine-site.php,README.md}`, `wp/themes/imagine/{functions.php,parts/mon-compte.php}`. Tests/transport : `wp/tests/demo/{b02-runtime.php,b02-state.php,b02-http.py}`, `wp/outils/demo/b02.py`. Dossier de restitution : `production/B-02/` (`A-VOIR.md`, besoins designer, sources, commandes, rapports et JSON sans secrets).

Aucun Git, verrou ou file modifié ; aucune écriture hors cible imagine-test-demo, aucun reset C09, compte réel, email, mandat, paiement, licence ou connecteur. Les preuves ne contiennent ni cookie/nonce ni HTML authentifié. Déploiement ciblé avec relecture exacte, syntaxes PHP parsées. Les bibliothèques et C13/C14 restent conservés, le parent garde sa vérification indépendante.
