# B-06 — Livraison technique V2

## Résultat

Attribut et fiche utilisateur natifs, ligne du compte Woo, cinq pages vides, journal C10/C17, refus des cinq voies et callbacks privacy réellement exercés. Seul le rôle exact `administrator` pose/retire le statut et lit sans attribut. Un éditeur muni de capacités larges reste fermé. Aucun plan Memberships, droit d’article, consentement ni bibliothèque close modifié.

**165 contrôles verts et 11 mutations négatives détectées** (`livraison-V2.json`). Le parcours HTTP représente 82 contrôles, avec vrais POST natifs de pose, refus de nonce, retrait et repose. Le texte témoin temporaire a été retiré ; P-COOP seul garde son attribut, les autres données et actions métier sont restaurées/reluées. Les journaux des vrais changements B06 restent append-only.

Régression finale : **1 123 tests, 34 569 assertions**, 0 échec/erreur/ignoré ; **16 outils, 306 contrôles**, 0 échec (`regression-final-V2.json`). `image-final-V2.json` prouve la préparation/vérification de l’image après les nouveaux fichiers de test. `quality-V2.json` : PSR12 des deux classes B06, aucune erreur bloquante, avertissements de longueur exclus comme pour les lots précédents.

## Commandes

À la racine du dépôt, sans installation hôte :

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
python -B wp/outils/demo/b06.py deploy NOUVELLE-ETIQUETTE-V2
python -B wp/outils/demo/b06.py seed NOUVELLE-ETIQUETTE-SEED-V2
python -B wp/outils/demo/b06-recette.py NOUVELLE-ETIQUETTE-RECETTE-V2
python -B wp/tests/demo/b06-verifier.py livraison-V2
```

Les commandes d’installation et de recette refusent d’écraser un reçu. Le reçu initial `baseline-V2.json` est conservé. Pour un rejeu indépendant, donner une nouvelle étiquette ; la recette complète prend plusieurs minutes. Le vérificateur courant est en lecture seule et contrôle les sources du reçu de livraison, le bootstrap par contrat, les preuves, les pages encore vides et l’attribut conservé.

Les tests B06 sont tous dans `wp/tests/demo/` et **ne font pas partie des 1 123 tests PHPUnit généraux** ; ils sont exécutés explicitement par la recette B06. Environnement réellement relevé : Python **3.11.15**, sortie UTF-8 ; PHP natif **8.3.32**, WordPress **7.0.9**, WooCommerce **11.2.2** (`environment-V2.json`). L’image de tests est distincte, PHP **8.2.33**.

## Décisions et limites

- Le choix le plus fermé est appliqué : rôle Administrateur seulement, pas la capacité générique `manage_options`. Les deux questions fermées pour Imagine figurent dans `A-VOIR.md`.
- L’espace n’est pas une adhésion Memberships et n’entre dans aucun appel du paywall. Le même article fictif est complet pour l’abonné valide et réduit à l’extrait pour P-COOP.
- Exporteur/effaceur B06 enregistrés séparément dans les outils WordPress ; C21 reste intact. L’attribut et sa source/date sortent à l’export et disparaissent à l’effacement ; la cible des événements est anonymisée sans exporter l’identité de l’opérateur. C21 garde le traitement des données propres à cet opérateur.
- La route HTTP du sitemap est 404 parce que la démo reste noindex. Le **vrai fournisseur WordPress** a aussi été appelé : URL publique positive, pages réservées absentes, puis mutation révélatrice. Aucun réglage d’indexation n’a été ouvert.
- `bootstrap-contract-V2.json` prouve qu’en retirant le seul bloc B06 ajouté, les octets du bootstrap initial sont exactement retrouvés. Les autres sections et bibliothèques ne sont pas réinstallées.
- Aucun écouteur ni appel CoopHub ; le seul hook nommé est un point d’extension. Aucun service réel, paiement ou email sortant. Pas de qualification en charge ni du cache hébergeur.

## Incidents de banc conservés

Le premier HTTP était rouge sur deux attentes du banc : URL de compte supposée `/mon-compte/` au lieu de la vraie `/my-account/`, et redirection native attendue `updated=true` au lieu de `updated=1`. La source WordPress et le permalink Woo ont été lus ; seul le banc a été corrigé et le parcours réel rejoué. Le reçu initial reste présent.

Un premier appel long a dépassé le watchdog de 420 secondes. Les processus et l’absence de fixture native résiduelle ont été contrôlés ; les étapes immuables déjà terminées ont été conservées. Après mise en forme PSR12, **la livraison entière a été rejouée à neuf**, avec une nouvelle série `livraison-*`, dans un processus suivi jusqu’à son vrai code 0. Les rouges TDD et mutations restent des preuves négatives, jamais présentés comme des parcours verts.

**Blocage technique restant : aucun dans le périmètre demandé.** Présentation à valider par Ced, clôture du code par Claude ; aucun GO sur le réel. Liste exacte des fichiers dans `FICHIERS-V2.json`.
