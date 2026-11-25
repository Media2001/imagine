# A-04 — corrections vérifiées — 25 novembre 2026, 17h31

**Fait** : les six instructions de `corrections/A-04.md` sont traitées.
**Prêt à relire** : A-04 ; `PRET` est produit uniquement par le contrôleur final après tous les contrôles.
**À valider ou arbitrer par Ced** : aucun choix technique en attente ; aucun GO réel.
**Bloqué** : rien sur fixtures ; pile commerciale complète WP 6.9.1 et migrations premium historiques non prouvées.
**Ensuite** : retour au parent voie 1, qui gère A-05 ; aucun enchaînement ici.

## Livraison courante

- **I3** : comparaison des sauvegardes après résolution canonique avec le site ; liens du fichier et de tous ses parents refusés. Régressions `..`, parent lié vers le site et parent lié vers une sauvegarde extérieure réellement exécutées sous Linux.
- **I1** : `main_file` obligatoire, chemin relatif PHP validé, `null` pour le cœur ; identité commune pour métadonnées du ZIP et versions installées avant/après/reprise. Fixture `a04-rest/fiction-entry.php`, dossier et fichier distincts, mise à jour en dernier sur les deux stockages.
- **I2** : sous les deux verrous, sauvegarde/staging/checkpoint liés contrôlés puis octets stricts du MU avant rafraîchissement natif et tout bootstrap. Essai avec timestamp vieilli de **1 200 s** et sauvegarde encore valide. MU absent/modifié, checkpoint invalide et contention : refus sans rafraîchissement ; sentinelle de bootstrap vérifiée négativement puis positivement. SIGKILL avec enfant WP-CLI héritant du verrou reste couvert.
- **Audit** : chaque `bootstrap-only` exige une trace nommant le composant, un fichier absolu non vide, son SHA-256 et la conclusion explicite d'absence de migration différée. Le fichier est relu avant bootstrap ; faux hash, fichier manquant et parent symbolique refusés. Le runtime PHP et son balayage `(?!)` sont inchangés ; l'audit reste une responsabilité humaine.
- **Adaptateurs / journal** : documentation et risques alignés : aucun adaptateur additionnel après les quatre premiers n'est accepté, même qualifié ; une extension à migration spécifique reste exclue jusqu'à un lot de support dédié. Statu quo autorisé pour `journal.txt` (lignes JSON), `journal.json` restant la source.

## Preuves et commandes courantes

`preuves/eb2aea037769/` : **48 tests Python / 86 contrôles d'intégration / 8 contrôles de runner**, trois lints PHP, tous verts ; **16 sources et 15 dépendances** liées par SHA-256 et relues conformes. Vrai code hôte **0 observé jusqu'à sortie**, conservé avec commande/stdout/stderr dans `corrections-20261125/final-run.{json,log}`. A-03 natif classique et HPOS : **code 3**, zéro anomalie, quatre changements attendus ; aller-retour production fictif : **code 0**, aucun changement. Six photos régénérées avec logs PHP contrôlés et propres ; plans et audits réels exportés, hash du plan égal à celui du checkpoint.

Image T01 **préparée de nouveau après les derniers ajouts** : `corrections-20261125/image-final/`, code 0, image `sha256:8b9ad379a68eea59c4cdd633655cc3d09b018437c377b58cbf18c626367b35c9`. Rejeu sur cette image dans `corrections-20261125/global-final/` : **1 012 tests / 34 006 assertions**, zéro échec/erreur/ignoré, quatre JUnit, inventaire des bibliothèques stable. T01 ne prétend pas découvrir Python A-04. PSR-12 `style/imagine-a04-style-cc43212267af/` : **0 erreur / 1 avertissement préexistant**, contrôle des erreurs code 0, rapport intégral code 1 ; aucun PHP modifié.

```sh
python -B wp/tests/a04/prepare_public.py
python -B wp/tests/a04/run.py --unit-only
python -B wp/tests/a04/run.py
python -B wp/tests/a04/style.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
python -B production/A-04/corrections-20261125/verifier.py --style production/A-04/style/imagine-a04-style-cc43212267af --report files/rapports/2026-11-25-17h31.md --seal
```

Toutes ces commandes sont lancées depuis `C:/Users/Ced/imagine` ; les longues exécutions sont enveloppées pour conserver leur vrai code et leurs sorties, jamais reconstruites. Précontrôle T01 vide : aucun orphelin partagé supprimé. Les runners créés sont supprimés par nom/label exacts puis relus absents. PHP uniquement dans les conteneurs jetables ; A-04 sans montage/port et `network none`, T01 avec le dépôt en lecture seule. Les trois ZIP publics créés ici sont retirés individuellement après hash et absence relue : `corrections-20261125/public-cache-cleanup.json`.

## Décisions, fichiers, historique et limites

Défauts prudents appliqués : identité déclarée, reprise MU stricte sous verrou, audit obligatoire sans élargir le balayage, journal inchangé. Les anciens plans sans `main_file` sont refusés ; ne jamais réécrire un plan lié à un checkpoint actif. Code modifié : `wp/outils/bascule/a04/update.py`. Tests modifiés : `wp/tests/a04/{inside.py,test_packages.py,test_safety.py}` ; nouveau `test_corrections.py`. Documentation : `mettre-a-jour.md`, risques, coordination et présents rapports/reçus sous A-04. Aucun runner commun modifié.

RED réels conservés : I3 `8bc96f19d4df`, I1 `d981f3f542c0`, I2 `b865ec3b1c1e` puis `e810b2e9995c`, audit `fb95fa211760`. GREEN intermédiaires également conservés. Originaux, ancien `PRET`, rapports et manifestes dans `corrections-20261125/avant/` avant modification ; **436 fichiers historiques relus conformes** au précédent manifeste. Aucun paquet historique réécrit.

Pile complète prouvée : WP **7.0 → 7.0.9**, Woo **11.0.1 → 11.1.1**, Subscriptions **9.4.1** et Memberships **1.30.3** à version constante. WP 6.9.1 essayé mais Subscriptions récent refusé nativement : ni pile commerciale complète 6.9.1, ni migrations historiques premium, ni moyens de paiement réels, ni restaurabilité des sauvegardes revendiqués. Répétition sur staging Imagine vérifié uniquement après GO écrit nominatif de Ced ; le présent verdict n'en est pas un. Aucun Git, compte, site réel, archive Imagine, Novamira, verrou parent, thème, lot voisin ni voie 2 touché. A-05 laissé au parent.

---

## Rapport antérieur conservé comme historique — ne décrit pas le paquet courant

**Fait** : outil de mise à jour, garde-fous, reprise réelle, journal durable et réception fictive classique/HPOS.
**Prêt à relire** : A-04 ; état de `PRET` et contrôle final du manifeste dans `verification-finale.json`.
**À valider par Ced** : rien de technique en attente ; aucune opération réelle demandée ni autorisée par ce rapport.
**Bloqué** : aucun dans le périmètre fictif ; limites de pile et migrations premium historiques conservées.
**Ensuite** : parent voie 1, voir `COORDINATION.md` ; aucune modification partagée par le sous-agent.

## Livré et exécuté

- `wp/outils/bascule/mettre-a-jour`, `a04/{update.py,bootstrap.php,maintenance.php,runtime.php}`, mode d'emploi `mettre-a-jour.md` ; tests et runners dans `wp/tests/a04`. Banc adapté à A-03 : `http-rollback.php` copié, journal configuré depuis `php_error_log`, HTTP avec `log_errors=1`, `date.timezone=UTC`, `error_log` égal aux settings.
- Rejeu final **code 0 observé jusqu'à sortie**, processus suivi : `preuves/9c204eb862d6/runner.json`, `result.json`, `unit.log`, 15 sources et 15 dépendances liées par SHA-256. **32/32 tests Python**, dont **7 vrais tests dans `test_update.py`** (refus d'écriture atomique sans perte ni résidu, checkpoint corrompu, identités de reprise, etc.), **70/70 contrôles fictifs**, **8/8 contrôles du runner**, trois lints PHP réussis. PSR-12 : **0 erreur, 1 avertissement** contre 13 (classe + point d'entrée, conservés sans refonte), contrôle `-n` code 0, rapport intégral code 1 ; `style/imagine-a04-style-4e730d02801c/`.
- A-03 natif classique et HPOS : **code 3**, zéro anomalie, quatre changements attendus (versions WP/Woo, unique hook administratif exact et compteur). Aller-retour production fictif : **code 0**, liste vide. Six nouvelles photos avec bilan `php_log` UTC contrôlé et sans diagnostic ; aucune ancienne photo complétée. Image T01 **préparée de nouveau** (`global-final/preparation.log`), global réellement rejoué puis actualisé après les changements parallèles hors A-04 : **1 012 tests / 34 006 assertions**, zéro échec/erreur/ignoré ; A-03 **152 / 314**, quatre JUnit et log dans `global-actualisation/`, sources stables pendant ce rejeu. Premier global **1 010 / 33 978** conservé dans `global-final/`.
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

Rejeu complet en processus suivi puis attendu. Trois ZIP publics de cache supprimés individuellement après SHA-256 ; aucun premium, SQL ou GO réel exporté. Runners possédés supprimés par nom exact et absence relue ; aucun orphelin T01 présent au précontrôle, donc aucun supprimé. Dépôt effectif `C:/Users/Ced/imagine`, sans dossier `voie1`. Aucun Git, réel, Novamira ou archive Imagine ; A-03, dépendances utilisées et verrou du parent inchangés. Des sources hors périmètre et le verrou voie 2 évoluent en parallèle ; observation nominative dans la vérification finale, aucun écrit ni restauration ici. Le reçu global est daté et ne fige pas les travaux ultérieurs des autres lots.
