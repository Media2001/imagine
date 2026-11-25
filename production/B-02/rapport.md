# B-02 — Rapport de livraison, 25 novembre 2026

1. **Fait** : cinq rubriques Mon compte, données natives, PDF C11/C14, édition postale Woo/WCS et isolation réelle GET/POST.
2. **Prêt à relire** : squelette technique inspectable, 144/144 contrôles techniques. **Aucun PRET**, conformément à la délégation.
3. **À valider** : visuel par Ced ; manque nominatif C09 et données non raccordées explicités ci-dessous.
4. **Bloqué** : réception complète A-4x-J45 / quatre échéances payées-à-venir et action après rejet non prouvables avec les objets actuellement disponibles sans inventer des états de paiement.
5. **Ensuite** : vérification indépendante du parent, sans réouverture de C13/C14 par ce lot.

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
