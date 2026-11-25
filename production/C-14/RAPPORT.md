# Rapport voie 2 — C-14 — 25 novembre 2026

1. **Fait** : produit → numéro, achat natif payé → articles/PDF du seul numéro, révocations et profil de démonstration raccordés.
2. **Prêt à relire** : C-14 livré avec A-VOIR et reçus ; **aucun PRET**, vérification puis dépôt réservés au parent.
3. **À valider ou à arbitrer** : aucun blocage technique ; validation visuelle et toute opération sur le réel restent hors livraison. Achat invité : revendication après création du compte non livrée, accès fermé.
4. **Bloqué** : rien pour le périmètre du brief connecté ; aucune banque, passerelle, adresse réelle ou licence exercée.
5. **Ensuite** : retour au parent pour vérification indépendante ; aucune prise de lot suivant par ce sous-agent.

## Résultat

Démo `imagine-test-demo` uniquement, WP 7.0.9 / Woo 11.2.2 / PHP 8.3.32 / HPOS actif, versions lues sans mise à jour. Dernière installation puis rejeu : **536/536 contrôles chacun**. Non-régression complémentaire : **193/193** (dont PHPUnit C11 36 tests/200 assertions, C12 7/63, C12 natif 32, HTTP 85, unitaires locaux 33). Aucun échec final. Image publique préparée par la commande prescrite, retour 0 ; PSR-12 des deux nouvelles classes, retour 0. Commandes exactes et incidents corrigés : `COMMANDES.md`.

`AchatNumero` est pur ; `AchatsNumeros` lit les commandes/lignes/refunds CRUD et passe le contrat `achat` à C08/C06, moteur inchangé. Processing/completed + date payée + propriétaire natif. Instantané sur ligne et concordance avec le produit ; non payé/remboursé/supprimé, ligne retirée, quantité zéro, mapping retiré/réaffecté ou erreur native : fermé. Les invalidations natives conservent la mémoïsation nécessaire au dernier crédit C12. PDF C11 inchangé, octets et accès directs testés. États partagés/bibliothèques closes conservés ; canaris supprimés et absence relue.

## Décisions prises à défaut

- **Technique** : « V-NUM » n'existe pas dans le catalogue. Conserver compte/login/commande **P-NUMERO** et ajouter l'alias explicite V-NUM ; 30 profils/27 comptes inchangés. T1 ouvert, autres numéros fermés. État/date payés sont des fixtures déclarées à zéro euro, pas un paiement bancaire inventé.
- **Technique** : produits simples seulement ; instantané à la création, aucune migration implicite des anciennes lignes. Réaffecter ne déplace pas un achat. Aucun plan Memberships supplémentaire ni second circuit de téléchargement.
- **Métier** : appliquer littéralement le retrait demandé pour tout remboursement de commande, même partiel/non ventilé ; aucun élargissement de droit. Un autre achat valide demeure indépendant.
- **Invité** : le cahier §3.7 le prévoit pour le papier, avec compte proposé après achat. Sans rattachement natif à un compte : fermé, même si l'email correspond. Le parcours sécurisé de revendication reste hors lot.
- **Référence** : le brief cite §3.11 (événements) ; application des dispositions pertinentes §3.7/§3.9.

## Fichiers livrés

- Plugin : `AchatNumero.php`, `AchatsNumeros.php` (nouveaux) ; `Paywall.php`, `imagine-site.php`, `README.md`, `tests-c12/fixture.php` (raccord/bootstrap du banc).
- `wp/outils/demo/` : nouveaux `c14.py`, `c14-profil.php`, `c14-regressions.py` ; modifications ciblées `c09-seed.php`, `c09-profils.json`, `profils.py`.
- `wp/tests/demo/` : nouveaux `c14-unit.php`, `c14-runtime.php`, `c14-http.py` ; `c09-runtime.php` adapté au profil et aux dates de seed.
- `production/C-14/` : `A-VOIR.md`, `COMMANDES.md`, ce rapport, `resultats.json`, `regressions.json`.

Aucun fichier de voie 1, bibliothèque close, script staging/T01, verrou ou fichier de file n'a été modifié. Aucun Git. Le rapport conventionnel `files/rapports/` reste à intégrer par le parent, hors périmètre d'écriture délégué.
