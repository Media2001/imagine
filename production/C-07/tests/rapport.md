# C-07 — Résultats et reprise du 22 novembre 2026

## Preuves actuelles

Paquet : `production/C-07/replays/reveil-22nov-0340/`. Les sources sont comparées à `production/C-07/tests/final.json` de la session interrompue : aucune différence dans la carte des empreintes de la bibliothèque et du connecteur copiés. Les anciens RED/GREEN et le premier final restent historiques.

Commandes exécutées depuis la racine, PHP exclusivement dans le conteneur possédé `imagine-c03-d60863809aab` (label `org.imagine.c07-runner=true`, malgré son préfixe hérité) :

```bash
IMAGINE_C07_PACKET=reveil-22nov-0340 python -B wp/tests/envoi-runner/run.py run --name final
IMAGINE_C07_PACKET=reveil-22nov-0340 python -B wp/tests/envoi-runner/verify.py
```

| Contrôle | Résultat réel |
|---|---|
| `composer test`, XML racine | 270 tests, 29 594 assertions, zéro échec/erreur/ignoré |
| Numeros | 42 tests, 121 assertions |
| Robots | 101 tests, 298 assertions |
| Entreprise | 41 tests, 19 561 assertions |
| Acces | 50 tests, 9 536 assertions |
| Envoi inclus dans la commande standard | 36 tests, 78 assertions |
| Envoi ciblé, fail-on-warning/risky/deprecation | 36 tests, 78 assertions ; code 0 |
| Connecteur C-04, mode strict | 37 tests, 224 assertions ; code 0 |
| PSR-12 `src/Envoi`, `tests/Envoi`, `CsvProtection.php`, `DailyCsvDestination.php` | code 0 |
| Syntaxe de tous les PHP `src/` et `tests/` | code 0 |
| Composer validate strict | code 0 |
| PSR-12 global | code 1 : zéro erreur, six avertissements C-05 préexistants |

**Le lanceur standard retourne 1, pas 0.** Ses tests passent ; son lint global échoue sur `tests/Echeancier/run.php`, lignes 1, 195, 207, 213, 225 et 235. Le lot C-05 est en attente : aucune modification de ces fichiers. Le vérificateur C-07 retourne 0 après tests ciblés et contrôle PSR-12 des PHP modifiés. Ne pas confondre les deux résultats.

## Couverture

- Profils fictifs A-CARTE, A-SEPA4, A-GRACE, A-SUSP, A-VIR, A-PAPIER (validé/non validé), A-EXPIRE, A-NONRENOUV, A-ETRANGER et A-SANSMAIL ; offert, bénéficiaires de groupe et achat unitaire.
- Paiement une seconde avant, exactement à la clôture et une seconde après ; création/réactivation tardives exclues ; fin effective atteinte sans événement d'expiration supplémentaire.
- Historique d'adresse, remplacement de bénéficiaire, place libre ; événement enregistré après clôture même rétrodaté ; rejeu et ordre déterministes ; immutabilité du résultat.
- Filtrage par numéros dus, premiers/derniers numéros et hors-série produits par C-01, sans recalcul de droit dans C-07.
- Anomalies séparées, doublons conservés, blocage de l'export non revu, pays étranger, zéros initiaux, formules, guillemets, retours à la ligne, antislash et CSV vide avec en-tête.

## Exemple réellement généré

`production/C-07/replays/exemples/liste-171.csv` est produit par l'API PHP dans le conteneur, puis relu : un exemplaire offert fictif, aucune anomalie, rejeu octet pour octet identique. SHA-256 : `c4e51ff5aaf1a19b94fb2ba6a957edd90c490bb9e6c10a600b3f44cdd4dfc227`. Le premier exemple sous `production/C-07/exemples/` reste conservé.

## Isolation et remise

Contrôles du runner : aucun montage, volume de données ou port exposé ; privilèges retirés ; réseau Docker détaché ; seul `sleep` avant les commandes. Aucun WordPress, base, compte réel, PHP ou dépendance installé sur Windows. Les dépendances déjà préparées dans le conteneur interrompu ont été réutilisées sans nouvel accès réseau.

La preuve de suppression et la vérification finale des empreintes, des JUnit et du paquet figurent dans `cleanup.json` et `handoff-verification.json` du paquet actuel. La remise `PRET` signifie prêt à relire uniquement ; trois questions du brief restent dans `production/C-07/notes.md`.
