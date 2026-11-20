# C-04 — bilan vérifiable des tests

Passage final : **20 novembre 2026**, PHP **8.2.36**, PHPUnit **11.5.58**.
Résultats issus des exécutions réelles, sans WordPress, base, Odoo ou n8n.

| Vérification finale | Résultat | Preuve |
|---|---|---|
| C-04 PHPUnit | **22 tests, 161 assertions, 0 échec, 0 erreur, 0 ignoré** | `final.log`, `final.xml` |
| C-04 PSR-12 | code 0, aucun avertissement | `final-lint.log` |
| Syntaxe PHP src/tests | code 0 | `final.json`, `final-lint.log` |
| Syntaxe de l’exemple réellement exécuté | code 0 | `demo.log` |
| Composer strict | code 0 | `final-composer-validate.log` |
| Non-régression C-01 | **39 tests, 101 assertions, tous réussis**, lint code 0 | `c01-regression.*` |
| Total des deux suites | **61 tests, 262 assertions**, tous réussis | `artifact-verification.json` |
| Sources livrées = sources testées | empreintes identiques | `final.json`, `artifact-verification.json` |
| C-01 intact | inventaire complet et SHA-256 identiques au début | `c01-before.json`, `c01-regression.json` |
| Nettoyage | seul runner possédé supprimé, absence relue | `cleanup.json` |

## Couverture du brief

- Même événement déposé deux fois : une entrée ; envoyé puis rejoué : aucun nouvel appel.
- Trois pannes successives : délais 10/20/40 secondes simulées, puis un seul effet distant.
- Accusé tardif/perdu : deux appels, une seule écriture dans la destination dédupliquante.
- Données invalides : règle nommée et message français, quarantaine, alerte, autres chaînes libres.
- Refus définitif : quarantaine sans nouvel essai ; limite temporaire : alerte unique et conservation.
- Abonnement : tri chronologique même si insertion inversée, blocage de sa seule chaîne.
- Contrôles : identité, adresse, montants entiers/somme/débordement/devise, paiement, entreprise
  injectée ou blocage prudent si indisponible ; extension par une nouvelle règle.
- Transitions : matrice exhaustive ; CAS périmé refusé ; reprise après bail de traitement expiré.
- Vie privée : champs inconnus refusés, y compris dans identité/adresse/lignes.
- CSV : dépôt/rejeu/redémarrage dédupliqués, journée vide, colonnes fixes, minuit local,
  printemps/automne Bruxelles, rattrapage des jours sautés, fichier scellé identique au rejeu,
  arrivée tardive affectée à un prochain lot sans modifier la date de survenue.
- Écritures : lien symbolique refusé sans altérer le fichier extérieur sentinelle ; journal
  corrompu => arrêt au lieu d’un fichier incomplet.

## CSV réellement produit

`demo-2026-11-19.csv` contient une seule ligne fictive. La démonstration a déposé deux fois
le même événement, rejoué l’export et tenté de rejouer l’événement envoyé : une entrée,
état `sent`, aucun second envoi, aucune alerte, empreintes avant/après identiques.
SHA-256 : `b10b8a75af235b4a832f0ad649026da998bc485a63c1f96329fefe2504b28128`.
Le reçu brut est `demo-result.json`, le journal `demo.log`.

## Discipline et incidents résolus

Les reçus `red-*` montrent les absences/échecs avant implémentation de chaque tranche :
événement, contrôles, worker, export, reprise et export scellé. Les passages `green-event`
et `green-export` avaient encore un avertissement de longueur de ligne PSR-12 : ils ne
sont pas présentés comme une validation finale. Tous les codes finaux sont nuls.
La vérification C-01 initiale a révélé l’expansion des variables PHP dans le transport
WSL de `php -r` ; le probe conservé compare l’échec argument et la réussite stdin.
Le lanceur a été corrigé vers stdin, puis C-01 réellement rejoué. Aucun blocage restant.

Image synthétique existante, entrée `sleep`, aucun montage/port/service, réseau détaché
avant suites et exemple. Pas d’installation hôte ni de modification d’un service partagé.
Le cache bytecode de l’import Python C-01 a été désactivé et son seul fichier généré
retiré ; la vérification finale compare aussi l’inventaire complet. Aucun Git utilisé.

## Rejouer / vérifier hors ligne

Les commandes de reconstruction figurent dans `wp/tests/connecteur-runner/README.md`.
Après fermeture du runner, la vérification des sources livrées, JUnit, CSV, C-01 et
nettoyage se rejoue sans Docker ni réseau :

```sh
python wp/tests/connecteur-runner/check_artifacts.py
```

`PRET` = prêt à relire, pas validation de réception, GO, déploiement ou branchement.
Les conditions de Step (clé atomique, champs réels), le rattrapage tardif, la reprise
administrative et le choix intégré/n8n restent explicités dans `../notes.md`.
