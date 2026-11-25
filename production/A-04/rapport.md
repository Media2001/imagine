# A-04 — finalisation du sous-agent voie 1 — 25 novembre 2026

**Fait** : outil de mise à jour, garde-fous, reprise réelle, journal durable et réception fictive classique/HPOS.
**Prêt à relire** : A-04, sous contrôle final du manifeste puis dépôt de `PRET` ; état dans `verification-finale.json`.
**À valider par Ced** : rien de technique en attente ; aucune opération réelle demandée ni autorisée par ce rapport.
**Bloqué** : aucun dans le périmètre fictif ; limites de pile et migrations premium historiques conservées.
**Ensuite** : parent voie 1, voir `COORDINATION.md` ; aucune modification partagée par le sous-agent.

## Livré et exécuté

- `wp/outils/bascule/mettre-a-jour`, `a04/{update.py,bootstrap.php,maintenance.php,runtime.php}`, mode d'emploi `mettre-a-jour.md` ; tests et runners dans `wp/tests/a04`. Banc adapté à A-03 : `http-rollback.php` copié, journal configuré depuis `php_error_log`, HTTP avec `log_errors=1`, `date.timezone=UTC`, `error_log` égal aux settings.
- Rejeu final **code 0 observé jusqu'à sortie**, processus suivi : `preuves/9c204eb862d6/runner.json`, `result.json`, `unit.log`, 15 sources et 15 dépendances liées par SHA-256. **32/32 tests Python**, dont **7 vrais tests dans `test_update.py`** (refus d'écriture atomique sans perte ni résidu, checkpoint corrompu, identités de reprise, etc.), **70/70 contrôles fictifs**, **8/8 contrôles du runner**, trois lints PHP réussis. PSR-12 : **0 erreur, 1 avertissement** contre 13 (classe + point d'entrée, conservés sans refonte), contrôle `-n` code 0, rapport intégral code 1 ; `style/imagine-a04-style-4e730d02801c/`.
- A-03 natif classique et HPOS : **code 3**, zéro anomalie, quatre changements attendus (versions WP/Woo, unique hook administratif exact et compteur). Aller-retour production fictif : **code 0**, liste vide. Six nouvelles photos avec bilan `php_log` UTC contrôlé et sans diagnostic ; aucune ancienne photo complétée. Image T01 **préparée de nouveau**, global réellement rejoué : **1 010 tests / 33 978 assertions**, zéro échec/erreur/ignoré ; A-03 **152 / 314**, quatre JUnit et logs dans `global-final/`.
- WP **7.0 → 7.0.9**, Woo **11.0.1 → 11.1.1**, Subscriptions **9.4.1**, Memberships **1.30.3** ; autre extension fictive **1.0.0 → 2.0.0** en dernier. WP **6.9.1** essayé réellement : Woo activable, Subscriptions récent refusé nativement (minimum WP 7.0), sans forçage. La migration historique des premium et la pile complète 6.9.1 ne sont **pas** prouvées.
- Arrêt code 75, SIGKILL au checkpoint, SIGKILL avec enfant WP-CLI actif, contention du même site depuis un autre état, reprise sans refaire le cœur, callback falsifié refusé, maintenance HTTP 503 persistante, absence de nettoyage et de changement du thème. Les quatre callbacks Woo de version sont exécutés une seule fois ; les suites natives tardives sont drainées au bootstrap suivant.
- Branche production répétée uniquement sur ces fixtures isolées, avec GO **synthétique** éphémère ; aucune donnée, archive ou identité réelle. Après restauration du mode staging fictif, A-03 retrouve les mêmes données métier. Réseau Docker `none`, aucun port/montage, MariaDB sur socket, tous les runners supprimés par nom exact et suppression relue.

## Décisions prises à défaut / limites

Sauvegarde ≤ six heures, version exacte sans `latest`, maintenance conservée, aucun rollback destructeur, ancien fichier absent de l'archive conservé, migration inconnue refusée. Décision par défaut : **verdict natif A-03 uniquement**, jamais requalification d'un code 2. Qualification additive A-04 et ses six tests retirés du code actif ; sources et ancienne livraison conservées dans `historique-avant-complements-a03/`, paquets historiques intacts. HTTP fictif avec écritures natives en rollback et séquence d'options restaurée, pas une preuve de HTTP réel sans écriture.

Historique conservé : `preuves/c936dad567c1/recovery.json` ne prétend pas avoir observé la sortie hôte ; `214440542c12` était l'ancienne livraison (A-03 code 2). Le premier rejeu de finalisation `58a4e0927cfd` conserve son échec réel sur l'ancienne interface du banc ; aucun de ces paquets n'est la preuve finale courante.

## Rejeu

```sh
python -B wp/tests/a04/prepare_public.py
python -B wp/tests/a04/run.py --unit-only
python -B wp/tests/a04/run.py
python -B wp/tests/a04/style.py
```

Rejeu complet en processus suivi puis attendu. Trois ZIP publics de cache supprimés individuellement après SHA-256 ; aucun premium, SQL ou GO réel exporté. Runners possédés supprimés par nom exact et absence relue ; aucun orphelin T01 présent au précontrôle, donc aucun supprimé. Dépôt effectif `C:/Users/Ced/imagine`, sans dossier `voie1`. Aucun Git, réel, Novamira ou archive Imagine ; A-03, dépendances utilisées et verrou du parent inchangés. Deux sources hors périmètre et le verrou voie 2 ont évolué pendant l'observation, noms dans la coordination ; ni écrits ni restaurés ici.
