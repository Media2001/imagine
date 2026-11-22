# C-07 — Remise des corrections, 22 novembre 2026

**Prêt à relire ; pas clos.** Instructions 1–7 et 9 de la fusion, file du 22/11 à 11 h 40. L'instruction 8 appartient à Claude : aucun fichier de `docs/` modifié. Ni Git, compte réel, staging, déploiement, envoi ou PHP sur Windows. Verrou du parent laissé intact.

## Corrections et couverture

| Instruction | Résultat | Vérification |
|---|---|---|
| 1. Grâce | Incluse indépendamment du paiement, réglage unique `inclureGrace` true par défaut ; false exclut toute grâce. `fin <= cloture` demeure exclu : borne C-01 inchangée. | Paiement faux/vrai, réglage actif/inactif, fin atteinte faux/vrai. |
| 2. Sans destinataire | Individuel/offert éligible : `destinataire_manquant` + `abonnement_id`, pas de ligne inventée ; export non revu bloqué. Groupe libre : ni ligne ni anomalie. | Trois origines et non-éligible sans destinataire. |
| 3. Présence Unicode | Contrôle commun nom/rue/code postal/ville/pays. Valeurs originales non réécrites. | 30 cas : cinq champs × trois espaces (ordinaire, U+00A0, U+202F) × vide/vraie valeur entourée. |
| 4. Doublons | ID stable commun + adresse normalisée, sinon nom/adresse avec casse UTF-8 et espaces Unicode. Deux lignes conservées ; une alerte par ligne. | Casse ÉLODIE/élodie, ID commun avec noms différents, personnes distinctes même adresse, ID commun adresses différentes ; doublon ID+nom non signalé deux fois. |
| 5. CSV | Oracle de 16 couples littéraux, sans regex de production. | Chaque valeur exportée dans les neuf colonnes et relue par `fgetcsv` ; contrôles, quatre préfixes, inchangés, zéro initial, guillemets. |
| 6. Profils | Attendus métier littéraux indépendants du prédicat. | Grâce paiement faux ; sans-email null et identité postale distincte ; étranger FR et zéro initial jusqu'au CSV. Aucun adaptateur WooCommerce simulé comme livré. |
| 7. C-01 | Aucun moteur ni borne changé. | 170 absent effectivement, 171–174 + HS-2027, renouvellement octobre 2027 : 175–178 + HS-2028, attendus explicites. |
| 9. Rejeu réel | PHP 8.2.36 dans deux conteneurs jetables successifs, réseau coupé, aucun montage/port/service web/BDD. | JUnit et reçus des suites standard, Envoi et C-04 ; codes stricts ; sources copiées et hachées ; conteneurs supprimés, absence exacte vérifiée. |

**C-05 autorisé :** cinq lignes longues reformatées ; une exception ciblée `PSR1.Files.SideEffects` documente le runner autonome servant aussi de fixture. Aucun autre sniff désactivé, aucune règle modifiée. Résultats complets des **376 cas / 1 473 assertions** identiques avant/après (`c05-style-equivalence.json` dans le paquet TDD). Ce n'est pas une refonte en plusieurs fichiers.

## Résultats réels finaux

Paquet canonique : **`production/C-07/replays/corrections-22nov-final/`**.

| Commande | Tests | Assertions | Échecs / erreurs / ignorés | Code |
|---|---:|---:|---|---:|
| `composer test` standard | 325 | 29 831 | 0 / 0 / 0 | 0 |
| PHPUnit Envoi strict | 91 | 315 | 0 / 0 / 0 | 0 |
| PHPUnit C-04 strict, son propre XML/Composer | 37 | 224 | 0 / 0 / 0 | 0 |
| Lint global pilotage / syntaxe globale / Composer strict | — | — | Aucun diagnostic | 0 / 0 / 0 |
| PSR-12 ciblé / lint complet C-04 | — | — | Aucun diagnostic | 0 / 0 |

Les deux suites ciblées ont `--fail-on-warning --fail-on-risky --fail-on-deprecation` dans leurs commandes enregistrées. Les tests Envoi font partie des 325, ils ne s'y ajoutent pas. Les cas autonomes C-05 sont comptés séparément.

Preuves principales : `final.json`, `final.xml`, `final.log`, `final-lint.log`, `final-composer-validate.log`, `envoi-strict.{json,xml,log}`, `c04-strict.{json,xml,log}`, `c04-integrity.json`, `c04-after-tests.json`, `container-inspection.json`, `sample.{csv,json}`, `cleanup.json`, `source-seal.json`, `evidence-seal.json`, `handoff-verification.json`.

C-04 : inventaire complet **34 fichiers**, mêmes octets avant/après sur l'hôte, dans la copie conteneur avant et après tests. Composer C-04 déclare le chemin frère C-02 ; le banc recrée ce chemin par lien interne au conteneur vers la vraie bibliothèque copiée, sans monter l'hôte ni modifier C-04. `CsvProtection.php` est intact.

Le CSV fictif est réellement produit depuis l'API et rejoué à l'identique : une copie offerte pour une destinataire sans email en grâce, paiement faux, pays FR, zéro postal initial. Pas de transmission au routeur.

## TDD et incident de banc conservés

Paquet **`production/C-07/replays/corrections-22nov-1155/`** : cinq paires de reçus RED→GREEN (`grace`, `destinataire`, `postal-unicode`, `doublon-unicode`, `doublon-identite`). Les RED échouent sur les assertions visées avant modification de production. Les GREEN précoces conservent le code global non nul dû au lint C-05 encore présent ; aucun faux vert global.

Premier essai C-04 séparé : **37 / 222, un échec**, chemin frère C-02 manquant. Échec et XML conservés sous `c04-strict.*`. Après correction du seul banc, `c04-strict-c02.*` : **37 / 224, zéro échec**. Le paquet canonique rejoue ensuite tous les tests depuis un conteneur neuf et passe sans cette réserve. Les deux `cleanup.json` contiennent le diagnostic Docker d'absence du conteneur exact.

## Fichiers et limites

Sources modifiées :

- `wp/plugins/imagine-pilotage/src/Envoi/ListeEnvoi.php` ;
- `wp/plugins/imagine-pilotage/tests/Envoi/ListeEnvoiTest.php` ;
- `wp/plugins/imagine-pilotage/tests/Envoi/ExportCsvTest.php` ;
- section C-07 seulement de `wp/plugins/imagine-pilotage/README.md` ;
- `wp/plugins/imagine-pilotage/tests/Echeancier/run.php` (style autorisé).

Ajout du vérificateur `wp/tests/envoi-runner/corrections.py`, réutilisant le banc existant sans modifier les runners C-01/C-03. Notes, `PRET`, ce compte rendu, rapport horodaté et deux paquets de preuve mis à jour/créés. Aucune dépendance installée sur l'hôte ; pas de `vendor/` exporté. Les empreintes finales sont calculées après les écritures des livrables.

Limites conservées : mbstring nécessaire ; pas de rapprochement flou/NFC ; entrées UTF-8 de confiance ; archivage historique persistant à fournir par le futur adaptateur. Maintien/durée de grâce et contrat du routeur restent chez Imagine avant branchement. La précision de Claude sur l'email et les doublons est appliquée ; aucun nouvel arbitrage financier/d'accès/comptable. Lots en attente non repris.

## Contrôle de remise (depuis la racine)

```bash
IMAGINE_C07_PACKET=corrections-22nov-final python -B wp/tests/envoi-runner/corrections.py check
```

Cette commande relit les sources et inventaires exacts, leurs empreintes, les reçus/JUnit et l'absence effective du runner. Elle n'exécute pas PHP sur Windows. Pour un nouveau rejeu réel, suivre les commandes de la section C-07 du README de la bibliothèque avec un **nouveau** nom de paquet ; ne pas écraser les preuves.
