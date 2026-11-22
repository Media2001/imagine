# C-07 — Format d’export configurable, remise du 22 novembre 2026

**Fait :** sélection et ordre des colonnes configurables, neuf colonnes provisoires conservées par défaut.
**Prêt à relire :** bibliothèque PHP et adaptateur Settings API dédié ; `PRET` redéposé après modification.
**À arbitrer :** aucun choix bloquant pour cette consigne ; la réponse du routeur changera le réglage.
**Limite :** adaptateur non branché au bootstrap partagé, aucune recette native/HTTP/visuelle WordPress ni envoi réel.
**Ensuite :** relecture et vérification parent ; lot non clos.

## Constat et interprétation

Les lectures intégrales de la consigne permanente, doctrine, file du 22/11 à 13 h 20, brief C-07, arbitrages du 22/11 et corrections C-07 ont été faites. L’ancien `ExportCsv` imposait `COLONNES` dans l’en-tête et les cellules : la consigne n’était pas déjà satisfaite.

J’ai compris « colonnes et ordre » comme la sélection ordonnée, non vide, des neuf champs déjà disponibles. Pas d’invention de champs, de renommage libre des en-têtes, de séparateur ou de format d’archive. Les valeurs restent des chaînes ; la liste et ses anomalies ne sont pas modifiées. La protection `Imagine\Connecteur\CsvProtection::cellule()` de C-04 est réutilisée à chaque cellule, sans changement de C-04.

## API et administration

- `new FormatExport()` garde les neuf colonnes historiques, dans le même ordre.
- `new FormatExport(['pays', 'code_postal', 'destinataire'])` sélectionne et ordonne ces champs.
- `ExportCsv::liste($liste, anomaliesRevues: false, format: $format)` conserve la barrière des anomalies, même si les colonnes correspondantes sont omises. La signature antérieure reste utilisable.
- `ExportCsv::lignes($lignes, $format)` est toujours le sérialiseur bas niveau, pas un point d’entrée d’expédition.
- Colonnes inconnues, répétées, liste vide, clés associatives/trouées et valeurs non textuelles : refus explicite, pas de correction silencieuse du moteur.

L’adaptateur autonome `AdministrationFormatExport` fournit `brancher()`, `lire()` et `exporter($liste)`. Il utilise la Settings API de WordPress, pas un stockage ou POST maison : option `imagine_envoi_colonnes_export`, page Réglages « Export postal Imagine », `manage_options`, `settings_fields()` et `options.php`. Une colonne par ligne dans l’ordre souhaité ; enregistrer ne nécessite aucun code PHP. Une saisie invalide conserve la dernière valeur et signale une erreur ; l’option absente/corrompue revient aux colonnes provisoires. Le filtre accepte aussi la liste déjà nettoyée pour rester idempotent.

**Limite de périmètre explicite :** conformément au brief pur PHP et à la délégation, le bootstrap partagé n’a pas été modifié. Le futur branchement devra appeler `(new AdministrationFormatExport())->brancher()` et utiliser `exporter($liste)` au point d’entrée sécurisé. L’administration n’est donc pas activée sur un site par cette remise. Les tests d’adaptateur utilisent des doublures nommées et locales dans `tests/Envoi/AdministrationFictive.php` ; ils vérifient appels Settings API, validation, rendu, refus d’affichage sans capacité et lecture du réglage. **Ils ne prouvent ni le nonce natif, ni une sauvegarde HTTP/native en base WordPress, ni une recette visuelle.** La délégation de ces fonctions au standard est livrée, pas une preuve d’exécution de WordPress.

Références officielles effectivement téléchargées dans le paquet final :
- https://developer.wordpress.org/plugins/settings/settings-api/ — soumission à `options.php`, contrôle `manage_options`.
- https://developer.wordpress.org/reference/functions/register_setting/ — `sanitize_callback`, `default`, `show_in_rest`.

Les pages HTML sont conservées avec leurs empreintes dans le scellé de preuve. La récupération via l’extracteur puis le navigateur a échoué (backend extraction indisponible / accès au runtime navigateur refusé) ; récupération publique par curl réussie. Aucun compte utilisé.

## Tests réellement exécutés

Paquet final neuf : `production/C-07/replays/format-export-22nov-final/`.

| Vérification | Tests | Assertions | Résultat |
|---|---:|---:|---|
| `composer test` standard | 362 | 30 770 | 0 erreur, échec ou ignoré |
| Envoi strict | 115 | 402 | 0 erreur, échec ou ignoré |
| C-04 strict, copie indépendante | 37 | 224 | 0 erreur, échec ou ignoré |

Les suites utilisent `--fail-on-warning --fail-on-risky --fail-on-deprecation`. Lint PSR-12 global et ciblé, syntaxe PHP globale, validation Composer stricte et lint C-04 : codes 0. Les totaux proviennent des JUnit, relus par `format.py check`. Aucun lot C-05/C-06 n’est supposé clos : aucune classe de ces lots n’est appelée par le code C-07. La suite agrégée les exerce seulement comme non-régression.

TDD réel conservé dans `replays/format-export-22nov/` : six RED→GREEN (format absent, validation absente, API liste sans argument format, réglage absent, gestion invalide absente, branchement adaptateur absent). Le premier passage nommé `green-02` échouait parce que le test ciblé ne chargeait pas CsvProtection ; correction du bootstrap de test puis `green-02-fixed` vert. Le premier `final` avait les tests verts mais lint non vert : reçu conservé, style corrigé exclusivement dans Envoi. Le paquet final a été préparé dans un nouveau conteneur après correction.

`sample.csv` vérifie le défaut. `format-sample.csv` est un vrai CSV généré et rejoué : en-tête `pays,code_postal,destinataire`, zéro initial `00100` conservé et `=Camille Fictive` protégé par apostrophe. La tentative initiale de l’exemple chargeait deux copies du même autoloader Composer, causant une collision de classe d’initialisation ; `autoload_collision.json/.log` conservent l’échec réel. Le banc charge maintenant directement l’utilitaire C-04 vérifié pour cet exemple. Aucune modification de C-04 ou de Composer partagé.

## Isolation, fichiers et remise

PHP/Composer uniquement dans deux conteneurs jetables possédés : `imagine-c03-47ba19d2b32b` et `imagine-c03-9b50cf42a289`, label C-07, entrée `sleep`, sans montage/port/privilèges, réseau coupé avant tests, sans base ni WordPress démarré. Les deux ont été supprimés ; `cleanup.json` de chaque paquet conserve `docker inspect` et le diagnostic exact `no such object`. Le check parent réinspecte les deux noms.

C-04 : inventaire complet de 34 fichiers et SHA-256 identiques sur hôte avant/après et dans sa copie testée. Aucun Git, archive réelle, compte, installation hôte, staging, envoi ou déploiement. Verrou parent non touché. Aucun fichier C-05/C-06, README partagé, rapport global ou documentation partagée modifié.

Fichiers de code créés : `src/Envoi/FormatExport.php`, `src/Envoi/AdministrationFormatExport.php`, `tests/Envoi/FormatExportTest.php`, `tests/Envoi/AdministrationFormatExportTest.php`, `tests/Envoi/AdministrationFictive.php`. Modifié : `src/Envoi/ExportCsv.php`. Runner créé : `wp/tests/envoi-runner/format.py`. Notes et PRET C-07 actualisés ; preuves propres au lot.

### Vérification parent, sans lancer PHP sur l’hôte

Depuis `C:/Users/Ced/imagine` :

```bash
IMAGINE_C07_PACKET=format-export-22nov-final python wp/tests/envoi-runner/format.py check
```

Cette commande relit JUnit/codes retour, compare les empreintes finales, l’inventaire C-04, et vérifie l’absence exacte des deux conteneurs. Pour un rejeu PHP indépendant, choisir un **nouveau** nom de paquet (les reçus sont immuables), puis `format.py prepare`, `run.py run --name final`, `format.py strict`, `format.py example`, `format.py close`. PHP reste dans le conteneur ; `close` ne supprime que le conteneur possédé par ce paquet.

**PRET signifie prêt à relire dans ce périmètre, pas clos, ni validation métier/visuelle, ni GO réel.**
