# A-19 — Candidat corrigé du 26 novembre 2026

**Fait :** corrections appliquées ; tests dédiés verts. **Candidat seulement**, non clos.
**Gate restante :** préparation commune et suite T01 globale réservées au parent. Ancien `PRET` retiré ; aucun nouveau `PRET`.
**Question Imagine :** garder « référence inconnue » distinct de « absente », ou regrouper ? **Défaut prudent conservé : garder distinct.** Aucune question visuelle ni intervention sur le réel.

## Corrections et décisions prises à défaut

- `confine.py` exige seulement `--wp-path`, `--audit`, `--output`. `--as-of` est facultatif ; le PHP existant fixe l’UTC une seule fois. Aucun changement des règles métier, du collecteur natif ni du runtime commun.
- Tests Python : trois chemins sans date atteignent la validation des chemins, au lieu de `A19_USAGE` ; date répétée avec les trois chemins refusée. Précédents refus conservés.
- Classic **et** HPOS : parcours avec et sans date ; UTC par défaut encadré par les horloges du banc. Un rapport avec cet instant explicite est identique octet par octet au rapport sans date. Date impossible et répétition refusées sans rapport créé.
- Neuf assertions de `unit.php` importées comme neuf cas PHPUnit nommés. En inclusion : aucun fichier produit, aucune sortie, aucun `exit`. L’exécution autonome conserve son reçu. Sonde `php -n` verte avec fonctions d’écriture/processus désactivées, sans extensions, WordPress, base ni réseau.
- La commande sans date déjà livrée dans les deux lignes du mode d’emploi audit reste valide ; ces lignes sont vérifiées, pas réécrites. Le banc natif reste hors T01, comme pour A02/A11/A12.

**Seul ajout hors dossiers A19 :** `wp/plugins/imagine-pilotage/tests/Administration/A19SubscriptionCoherenceTest.php`. Il est déjà découvert par la suite `Administration` du XML existant. Aucun changement du XML, de Composer ni de l’exécuteur partagé. Le runner dédié vérifie découverte/couverture avec les fonctions T01 inchangées, puis exécute réellement PHPUnit filtré A19 : **pas la suite globale**, laissée au parent après sa préparation commune.

## Exécution prouvée

Paquet unique `preuves/final`, cp1252 à la racine et UTF8 dans `utf8/`. Interpréteur découvert : **`C:/Python314/python.exe`, Python 3.14.6 Windows**, pas 3.14.7 ; locale cp1252. stdout/stderr cp1252 avec `PYTHONIOENCODING=cp1252 PYTHONUTF8=0`, puis UTF8 avec `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` mesurés. Chaque contexte : **9 contrôles PHP purs, 108 contrôles natifs classic/HPOS, 7 gardes runner et 5 tests Python**, zéro échec. Enfants des tests de refus explicitement UTF8. PHPUnit T01 filtré A19 : **9 tests, 9 assertions**, aucun échec/erreur/ignoré ; sonde pure PASS. PSR12 strict : zéro erreur/avertissement. **Préparation commune non lancée**, conformément à la délégation. Commandes complètes, environnements et retours réels : `preuves/final/windows-matrix.json`.

```text
C:/Python314/python.exe -B wp/tests/a19/test_launcher.py
C:/Python314/python.exe -B wp/tests/a19/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a19-corrections-20261126/final-proof/utf8
C:/Python314/python.exe -B wp/tests/a19/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a19-corrections-20261126/final-proof/cp1252
C:/Python314/python.exe -B wp/tests/a19/t01.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a19-corrections-20261126/t01-final-2
C:/Python314/python.exe -B wp/tests/a19/style.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a19-corrections-20261126/style-final-3
C:/Python314/python.exe -B wp/tests/a19/verify.py production/A-19/preuves/final
```

Banc réel : WordPress 7.0.9, WooCommerce 11.1.1, Subscriptions 9.4.1, Memberships 1.30.3, les deux stockages faisant autorité. Liens relus par les objets natifs ; parent et renouvellement réellement payés ; échéance passée relue après activation (le standard la recalculait lorsqu’elle était posée avant). Couple cohérent, actif non lié, adhésion autonome, lien vers un abonnement supprimé et doublon hérité explicitement construit. Référence native présente, manquante et adaptateur absent : ce dernier reste inconnu, jamais absent par supposition.

Empreintes logiques de toutes les tables, Action Scheduler et fichiers identiques avant/après ; vraies tentatives SQL/mail/HTTP/cron/fichiers bloquées. Confineur obligatoire, sortie disjointe, six drop-ins fermés, liens symboliques fichier/dossier, configurations arbitraires et date impossible. Canaris absents de stdout/stderr et de tous fichiers produits, aucun ID de compte/abonnement/commande rendu. Les codes d’erreur sont sur **liste littérale fermée** : une exception d’extension au nom ressemblant à un code est ramenée au refus générique ; test natif RED avant correctif puis vert en deux consoles. Runtime commun et A17 non modifiés. Suppression des seuls conteneurs possédés vérifiée.

## Standard et décisions prises à défaut

Dix lignes du mode d’emploi décrivent l’intégration officielle et le code installé ; provenance dans `sources-officielles.json`. `Analysis.php` est pur PHP ; projection native isolée dans `Inventory.php`. Le mode est le drapeau enregistré, pas `is_manual()` qui force le manuel sur staging ou passerelle indisponible. L’historique payé inclut toute commande liée via l’API native, date de paiement conservée ou statut payé. Le lien explicite n’est pas réinterprété selon le titulaire : le standard permet des liens manuels entre titulaires différents. Les comptes « actifs » sont de strict état actif, sans inventer une règle d’accès. Deux lignes propres seulement font contrat sur le README audit partagé, aucune empreinte globale ; manifestes bornés au lot.

## TDD, artefacts et limites

Le test Python sans date a échoué avec `A19_USAGE` avant correctif ; le banc natif a échoué sur ce parcours dans les deux stockages. L’import T01 a échoué sur le chemin réservé au banc autonome, puis les neuf cas ont passé après adaptation de la seule frontière d’inclusion. Reçus RED : `preuves/final/tdd/`. Une première attente de stdout natif vide a été corrigée pour respecter le marqueur nominal existant `A19_OK coherence.json coherence.md`. Permission du premier banc T01 et avertissement PSR12 de sa sonde corrigés dans les seuls fichiers du banc ; essais intermédiaires hors dépôt, non présentés comme verts.

Artefacts : `t01/t01-junit.xml` (neuf cas), `t01/pure.log` (sonde sans extensions/écritures), `style/` (contrôle strict), `sources.json` et `manifest.json` (empreintes finales), à l’intérieur de `preuves/final/`. `verification.json` vérifie le **candidat**, pas la préparation ni T01 global. L’ancien paquet est conservé hors dépôt dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a19-corrections-20261126/historical-delivered-packet`.

Fichiers de travail modifiés/créés : `wp/outils/bascule/a19/{confine.py,README.md}`, `wp/tests/a19/{inside.py,test_launcher.py,unit.php,run.py,style.py,verify.py,t01.py,t01-probe.php}`, le test T01 précis ci-dessus et ce dossier de livraison. Aucun autre lot, A18, verrou ni fichier interdit modifié.

Une référence présente ne prouve ni validité ni débit futur. Aucun droit d’accès décidé. Aucun réel, archive Imagine, compte externe, secret, staging, Git, Novamira ni déploiement ; PHP exclusivement dans les conteneurs jetables. **Le parent doit encore lancer `wp/tests/preparer-image.ps1`, puis `wp/tests/rejouer.ps1` avant tout nouveau `PRET`.** Claude seul clôt.
