# A-04 — rapport du sous-agent voie 1 — 25 novembre 2026

**Fait** : outil de mise à jour, garde-fous, reprise réelle, journal durable et réception fictive classique/HPOS.
**Prêt à relire** : code A-04 et preuves ci-dessous ; **pas de fichier PRET**.
**À valider par Ced** : rien de technique en attente ; aucune opération réelle demandée ni autorisée par ce rapport.
**Bloqué pour la clôture** : politique canonique A-03 du seul hook administratif Woo et rattachement image/suite globale, réservés au parent.
**Ensuite** : parent voie 1, voir `COORDINATION.md` ; aucune modification partagée par le sous-agent.

## Livré et exécuté

- `wp/outils/bascule/mettre-a-jour`, `a04/{update.py,qualification.py,bootstrap.php,maintenance.php,runtime.php}`, mode d'emploi `mettre-a-jour.md` ; tests et runners dans `wp/tests/a04` ; risques et références dans ce dossier.
- Rejeu final **code 0 observé jusqu'à sortie**, lancé comme processus suivi : `preuves/214440542c12/runner.json`, `result.json`, `unit.log`, sources et dépendances liées par SHA-256. **32/32 tests unitaires**, **62/62 contrôles fictifs**, **8/8 contrôles du runner**, lint PHP des trois fichiers réussi. PSR-12 : **0 erreur, 13 avertissements** conservés (12 lignes longues, 1 classe + point d'entrée), contrôle `-n` code 0, rapport intégral code 1.
- WP **7.0 → 7.0.9**, Woo **11.0.1 → 11.1.1**, Subscriptions **9.4.1**, Memberships **1.30.3** ; autre extension fictive **1.0.0 → 2.0.0** en dernier. WP **6.9.1** essayé réellement : Woo activable, Subscriptions récent refusé nativement (minimum WP 7.0), sans forçage. La migration historique des premium et la pile complète 6.9.1 ne sont **pas** prouvées.
- Arrêt code 75, SIGKILL au checkpoint, SIGKILL avec enfant WP-CLI actif, contention du même site depuis un autre état, reprise sans refaire le cœur, callback falsifié refusé, maintenance HTTP 503 persistante, absence de nettoyage et de changement du thème. Les quatre callbacks Woo de version sont exécutés une seule fois ; les suites natives tardives sont drainées au bootstrap suivant.
- Branche production répétée uniquement sur ces fixtures isolées, avec GO **synthétique** éphémère ; aucune donnée, archive ou identité réelle. Après restauration du mode staging fictif, A-03 retrouve les mêmes données métier. Réseau Docker `none`, aucun port/montage, MariaDB sur socket, tous les runners supprimés par nom exact et suppression relue.

## Décisions prises à défaut / limites

Sauvegarde ≤ six heures, version exacte sans `latest`, maintenance conservée, aucun rollback destructeur, ancien fichier absent de l'archive conservé, migration inconnue refusée. Défaut technique A-03 appliqué sans attendre : qualification **additive exacte** du seul hook `woocommerce_run_on_woocommerce_admin_updated` et de son compteur, aucun autre écart toléré. Les deux rapports **bruts A-03 restent au code 2**, deux anomalies ; ils ne sont ni masqués ni réécrits. Le parent doit intégrer/qualifier cette liste canonique et rattacher le rejeu global/image avant `PRET`.

Un passage a dépassé le watchdog hôte : `preuves/c936dad567c1/recovery.json` conserve le vrai résultat interne mais ne prétend pas avoir observé la sortie hôte. Son runner exact a été récupéré et supprimé, puis la même version a été rejouée normalement dans `214440542c12`.

## Rejeu

```sh
python -B wp/tests/a04/prepare_public.py
python -B wp/tests/a04/run.py --unit-only
python -B wp/tests/a04/run.py
python -B wp/tests/a04/style.py
```

Le rejeu complet doit être lancé en processus suivi puis attendu, car il peut dépasser le watchdog d'un appel terminal au premier plan. Les ZIP publics sont un cache reproductible nettoyé après qualification ; aucun premium, dump SQL ou GO réel n'est exporté. Aucune opération Git, aucun accès réel. Aucun verrou Hermès, A-FAIRE, source A-03 ni banc partagé modifié. Aucun accès au site `imagine-test-demo` ni à Novamira.
