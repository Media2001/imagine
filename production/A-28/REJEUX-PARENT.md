# Import final A-28 — transmission au parent

L'import est gelé après la correction A-28. Les empreintes exactes et l'heure UTC figurent dans `preuves/final/dependency-invalidations.json` ; les copies antérieures intactes sont hors dépôt sous `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a28-correction-20261127-0258/old-production`.

**Paquets invalidés par les sources d'import : A-21, A-22, A-23, A-24, A-25, A-26, A-27.** Ce constat de dépendance n'est pas un nouveau verdict sur leur code. Aucun vérificateur, matrice, scellement ou PRET de ces lots n'a été lancé/modifié par cette correction. A-29 est réservé au parent et n'est pas touché. A-20 n'est pas requalifié ici.

## Ce qui a changé dans cet import

- `staging-court/inside.py` photographie les identifiants des messages/révisions connus dans son contexte privé avant le premier PHP ; aucune valeur de message n'y est lue ou publiée.
- `staging/engine.php` garde la provenance jusqu'au vérificateur et compte les postmeta survivants. Types inconnus et métadonnées d'origine inconnue restent hors de la purge.
- `staging/lib.php` garde la même interface d'inclusion ; ses quatre déclarations sont séparées dans `engine.php`, `store.php`, `guard.php`, `form-decision-refused.php` pour PSR-12 strict. `staging-court/run.py` transporte réellement ces quatre fichiers. La politique JSON reste inchangée.
- Les décisions sur table connue absente sont aussi refusées ; le constructeur d'exception ne relit plus le JSON. Aucune commande de Ced n'a changé ; les trois lignes README A-28 restent contrôlées par contrat.

Le parent peut maintenant orchestrer la requalification commune demandée par la file de 1 h 30, sur ces empreintes uniquement. **Ne pas resceller une ancienne matrice en remplaçant ses hashes.** T03/A26/A27/A30 et voie 2 sont des propriétaires concurrents : aucun inventaire global de leurs fichiers n'a été épinglé. Les versions communes effectivement observées avant les portes figurent dans `preuves/final/gates/*.common-observed.json`.

Limites : archives entièrement fictives ; la qualification des types hors liste et des stockages inconnus reste ouverte. Deux suffixes Fluent sans citation exacte sont marqués en doute dans `standard.md`. PRET technique n'est jamais un GO réel.
