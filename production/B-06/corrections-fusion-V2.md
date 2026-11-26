# B-06 — cinq corrections fusionnées, 26 novembre 2026

## Résultat

Cinq instructions de `corrections/B-06.md` appliquées et réellement exercées. Réglages distincts, défaut Administrateur pour chacun ; erreurs de lecture SQL non confondues avec un journal vide ; règle pure découverte par le runner canonique ; source/date cachées après retrait ; collection REST vérifiée avec témoin public présent et mutation réelle de sa protection.

Preuve courante : **`fusion-livraison-V2.json`**, 916 contrôles verts, 13 mutations détectées. Détail : règles complémentaires 16, attribut 19, privacy 29, espace 36, réglages 728, HTTP 88. Les 64 configurations croisées des deux réglages sont exercées sur les vrais adaptateurs ; la décision d’article est comparée avant/après pour chaque rôle, et P-COOP reste à l’extrait. Capacité large seule, valeurs invalides et panne SQL du journal de réglage sont refusées.

Horslive : **1 126 tests / 35 550 assertions**, 0 échec, 0 erreur, 0 ignoré ; 16 outils / 311 contrôles / 0 échec. B06 apparaît dans le JUnit de `rejouer.ps1` : **3 tests / 981 assertions**, sans WordPress ni base. Image préparée/vérifiée après les nouveaux tests ; PHP conteneur 8.2.33. Python réellement exécuté sur ce poste : **3.11.15**, non la version présumée du contexte. PSR12 : 0 erreur, 0 avertissement (longueurs exclues comme dans la livraison antérieure).

## Commandes réellement exécutées

```powershell
python -B wp/outils/demo/b06.py deploy deploy-fusion-final-V2
python -B wp/outils/demo/b06-finaliser.py
# Le finaliseur exécute réellement :
.\wp\tests\preparer-image.ps1
.\wp\tests\rejouer.ps1
python -B wp/outils/demo/b06-recette.py fusion-livraison-V2
python -B wp/tests/demo/b06-verifier.py fusion-livraison-V2
```

Ces commandes ont terminé à code **0**. `fusion-livraison-execution-V2.log` conserve la sortie complète ; chaque mutation a son reçu rouge distinct à code 1, état restauré et assertion attendue effectivement rouge. La vérification finale relit aussi les fichiers installés, les cinq pages vides et l’attribut vrai de P-COOP. Les anciens reçus ne sont ni écrasés ni réinterprétés ; l’ancien `PRET` est conservé sous `PRET-historique-avant-fusion-20261126.txt`.

## TDD, SQL et reprise

- `fusion-red-regles-V2.log` : le runner canonique découvre le nouveau test puis échoue sur la règle de rôle codée en dur ; `fusion-green-regles-V2.log` puis la régression finale passent.
- `fusion-red-reglages-V2.json` : absence des deux réglages détectée avant leur ajout. `fusion-livraison-settings-V2.json` : 728 contrôles verts, dont les 64 configurations, les droits natifs et la panne du journal.
- `fusion-red-affichage-V2.json` : les deux affichages laissaient source/date après retrait ; la vraie recette HTTP finale vérifie leur absence et la repose du statut.
- `fusion-red-sql-V2.json` : faux succès complet export/effacement effectivement reproduits avec un événement présent. Après correction : erreur d’export contrôlée, effacement incomplet avec rétention signalée. Panne de SELECT initial, puis reprise d’export ; panne du SELECT final après 50 événements sur 51, un événement restant relu, puis reprise complète d’effacement.
- `fusion-livraison-mutation-collection-V2.json` : retrait de la vraie protection de requête ; témoin public toujours présent et assertion d’exclusion des pages réservées rouge. Les trois publics non autorisés sont couverts.

## Préservation et limites

Préimages durables privées fsyncées et relues sous le scratch avant mutation des données ; aucune session dans le dépôt. La recette HTTP restaure à partir des octets persistés et compare exactement comptes/métadonnées, puis les invariants d’options et d’actions métier. P-COOP garde son attribut vrai ; les autres états et les cinq pages sont restaurés et relus. Aucun reset de profil, abonnement ou action planifiée. Journaux des vrais changements B06 conservés append-only.

Installation limitée aux deux classes B06 : bootstrap partagé **non réécrit**, blocs C24 préservés. C21/C06 et bibliothèques closes inchangés ; aucun runner T01 modifié. Le test pur est placé dans `imagine-site/tests`, découvert par le mécanisme existant. Aucun fichier de rapport parent, verrou, Git, autre voie ou autre site touché. La matrice C23 est hors de ce périmètre délégué.

Deux attentes du banc ont été corrigées sans changer le produit : la route REST interne terminée par `/` n’est pas enregistrée par WordPress ; et le helper C23 partagé a changé de contrat (redirections désormais non suivies, terme de recherche explicite). La recette B06 utilise son propre suivi borné de redirection, limité à l’origine de démonstration, et passe son terme au filtre de réflexion. Les reçus intermédiaires rouges sont conservés (`fusion-collection-green-V2.json`, `fusion-http-pilote-V2.json`) ; les vrais parcours ont ensuite été rejoués au vert.

**Blocage restant : aucun pour les cinq corrections.** Date UTC brute conservée, choix visuel laissé à Ced ; défauts métier exposés en réglages. Le code reste à clore par Claude, le visuel à valider par Ced. Aucun GO sur le réel. `A-VOIR.md` porte les parcours et les chiffres courants ; `PRET` n’est redéposé qu’après les gates verts.
