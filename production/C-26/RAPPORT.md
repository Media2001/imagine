# C-26 — Rapport de livraison

- **Fait** : extension de la matrice aux sorties B07/C24/C25/B08, données des autres comptes incluses ; inventaire de chaque sortie ; couverture B06 explicitement remise en relecture ; correctif TMPDIR.
- **Prêt à relire** : C-26, sur les sources et reçus nommés dans `A-VOIR.md` et `manifest.json` ; les deux relectures restent au circuit parent.
- **À arbitrer par Ced** : rien de nouveau ; aucune règle métier ni aucun droit choisi pour les besoins du test.
- **Bloqué** : aucun gate restant. Aucun autre lot/site, plugin, paywall, thème, bibliothèque close, verrou, file ou rapport parent modifié.
- **Ensuite** : retour au parent, sans prendre un autre lot.

## Preuves

- Livraison normale fraîche **après restauration des mutations** : **3 951 contrôles**, tous verts, zéro fuite : C23 1 922 + sorties C26 1 965 + callbacks privacy 64. Pas de double comptage des 35 voies B06 déjà incluses dans C23.
- Six familles de mutations positives détectées : quatre mauvais titulaires au raccord vers les vrais callbacks natifs (15 tiers rouges par famille), B06 par statut persisté puis vrai GET, Soutenir par témoin réservé persisté puis vrai GET. Aucun corps/résultat applicatif fabriqué en mémoire.
- **42 tests Python 3.11.15**, en UTF-8 et cp1252, sans TMPDIR et avec socket réseau bloquée ; image préparée après ajout des tests, code 0.
- Vérificateur offline **46/46** ; **9/9 falsifications** de paquet refusées, huit rescellées pour éprouver les contrôles sémantiques ; production inchangée pendant le vérificateur.
- État métier, profils et actions planifiées identiques avant/après ; quatorze collections métier comparées exactement et relues ; préimages durables privées avant toute session/fixture ; sources live et bootstrap courant inchangés.

## Décisions prudentes et écarts

- Réemploi de C23 sans changer sa commande GET ni réécrire ses preuves scellées. La seule source C23 modifiée est le test TMPDIR autorisé ; sa nouvelle preuve est dans C26, pas un rescellement historique de C23.
- Découverte livrée fermée conservée : V-DEC-FIN est sans droit ; aucun cas ouvert/épuisé prétendu rejoué. V-DEC sert seulement de propriétaire fictif des nouvelles données temporaires, sans lecture consommant sa découverte.
- Les appels de flux sur types privés sont des sorties HTTP réellement inspectées mais, sur cette version native, replient sur les articles publics : pas de fausse preuve d'un flux privé non vide. Inverses privacy réels pour l'existence des données.
- Les diagnostics rouges conservés provenaient du nouveau test : mauvais chemin de compte supposé, apostrophe transformée, droit C14 légitime sur un repli de flux, terme date réfléchi dans un lien RSS encodé. Corrigés par régressions, pas par changement du site.
- Les 35 anciennes injections B06 en mémoire restent des tests de détecteur, non crédités comme 35 mutations applicatives. Fichiers et fonctions B06 à relire nommés précisément dans `A-VOIR.md`.

## Fichiers

Nouveaux : `wp/outils/demo/c26.py`, `c26-preparer.py`, `wp/tests/demo/c26-fixture.php`, `c26-tests.py`, `c26-verifier.py`, `c26-paquet-tests.py` et `production/C-26/` (inventaire, matrices, reçus, qualification, sceau et présentes notes). Modifié : `wp/tests/demo/c23-tests.py` uniquement, helper scratch et deux appels.
