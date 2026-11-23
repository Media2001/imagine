# A-02 — corrections du 23 novembre 2026

**Prêt à relire sur le banc fictif.** Paquet courant : `production/A-02/preuves/5d09a26acfb8/`. Le PRET porte sur l'outil uniquement : aucun audit d'Imagine, import, staging, compte, paiement ou déploiement.

## Résultat réel, sources finales

- `python wp/tests/a02-audit/run.py` : **retour 0**, **144 assertions nommées au vert, 0 échec** (17 unitaires, 120 intégration/qualification, 7 runner). Ce n'est pas un décompte PHPUnit.
- `python wp/tests/a02-audit/verify.py production/A-02/preuves/5d09a26acfb8` : **retour 0, PASS**, inventaire et empreintes des sources courantes identiques au paquet ; JSON/Markdown cohérents ; conteneur exact absent, Docker répondant. Reçu : `verification-corrections.json`. Le parent doit encore exécuter sa vérification indépendante et écrire son propre rapport.
- Les vrais WooCommerce, Subscriptions et Memberships sont actifs dans les fixtures classique et HPOS, hors réseau, sans licence ni compte. Même image compatible déjà disponible ; aucune image T01 préparée.
- **55 tables par base** ; schémas et multiensembles de toutes les lignes inchangés avant/après, y compris les métadonnées volontairement corrompues. Fichiers des sites inchangés et piège de bootstrap non déclenché. Variantes sans cache/journal également inchangées côté base.
- Cinq fichiers PHP réellement lintés dans le conteneur : **5 retours 0**. `test_documentation.py` : **1 méthode unittest, retour 0**, six sources officielles, phrases exactes vérifiées lors de la récupération HTTP 200. Ce test documentaire est séparé des 144 assertions.
- PHPCS PSR-12 : **0 erreur, 98 avertissements, retour 1**, non présenté comme vert. Reçu final : `style/imagine-a02-audit-style-1d583482fa9a/` ; mêmes hashes sources que la fixture et conteneur absent. Les deux erreurs de présentation introduites dans le parseur ont été corrigées. Les avertissements de lignes longues et de point d'entrée monofichier restent déclarés.

SHA-256 final de `wp/outils/bascule/audit` :
`7eb2b4bfa450e37d3f4265e3055cdba61a877b056f4feb0bfce06f681659c6dc`.

Empreintes DB identiques avant/après :

```text
classic c8e99a17c420a4cddfa61049adfe4653aec4677080f2e607f238e41fe810fb4d
hpos    9f09f4177f008a8e03c36270a7cecbfdfb355bd6e85118532b947d567e95e055
```

## Corrections appliquées

1. **C1** : collecte des sources d'une même extension avant résolution, classes tokenisées, héritage inter-fichiers et constantes littérales héritées ; plus de préfiltre excluant la classe concrète. Classe étrangère ignorée. Notices explicites pour ascendance ou ID non résolus, classe concrète sans ID et enfant remplaçant l'ID connu par une expression dynamique. Aucun fichier tiers exécuté.
2. **C2** : sous-requêtes sélectionnant le plus petit identifiant de ligne par abonnement et clé **avant** les jointures, classique et HPOS. Les deux colonnes ne peuvent plus produire de produit cartésien. Comptes séparés des abonnements avec doublons, lignes supplémentaires et contradictions binaires ; aucune valeur ni abonné divulgué. La fixture mêle doublon identique seul, répétition identique puis contradiction de période et contradiction d'intervalle. Total réel maintenu à trois abonnements, chacun dans un seul groupe.
3. **C3** : rôles parent/enfant, priorité par chemin relatif, état `masked_by_child` et `effective=false` conservés pour le parent masqué. Le parent sans équivalent enfant reste effectif. Deux fichiers parent périmés dans l'inventaire mais **un seul risque effectif**, conformément à la priorité n°4.
4. Articles groupés sur `post_date_gmt`, base `UTC_creation`, fixture avec années locale et UTC différentes. `custom_fields_scope` annonce toutes les clés postmeta, internes incluses, noms/fréquences uniquement.
5. Sources officielles renforcées par affirmation, phrase exacte, position dans le texte normalisé, statut et SHA-256. Les anciens reçus documentaires sont conservés dans `sources-officielles-avant-corrections.json`.

## Trace TDD conservée

Les identifiants ci-dessous désignent des répertoires sous `production/A-02/preuves/` ; les vrais retours, erreurs attendues, sources et cleanup y sont conservés.

| Tranche | RED réel | GREEN réel |
|---|---|---|
| C1 unité, héritage/notice | `bfc739683dce` (retour 1, deux assertions en échec) | unité verte dans `3655be4bcee6` |
| C1 collecte inter-fichiers | `3655be4bcee6` (retour 1, `gateway_cross_file` dans les deux stockages) | `4d6759a5c3ee` (retour 0) |
| C2 agrégats avec doublons/conflits | `9a9a2e74312c` (retour 1, `subscription_aggregates` dans les deux stockages) | `e442da4c0f5e` (retour 0) |
| C3 masquage enfant/parent | `12402a6a2898` (retour 1, `child_masks_parent` dans les deux stockages) | `cce400846db4` (retour 0) |
| Articles UTC | `45122674e23f` (retour 1, `posts_utc_year_boundary` dans les deux stockages) | `2161cf7d5d6e` (retour 0) |
| C1 ID concret absent | `6c5996437371` (retour 1) | `df173cd131ba` (retour 0) |
| C1 enfant dynamique masquant ID parent | `552ae6e3ff6f` (retour 1) | `e21442a0f5ab` (retour 0) |
| Étiquette des métas internes | `64b504d8ab53` (retour 1, `custom_fields_internal_scope_explicit` dans les deux stockages) | `4e6588c811e6` (retour 0) |

Le test documentaire a d'abord échoué réellement avec cinq sous-cas `EXACT_PHRASE_MISSING`, puis est devenu vert après régénération par récupération publique. Ce premier stdout n'a pas été archivé dans un paquet de fixture ; il figure dans la trace d'exécution de la session. Tous les paquets fonctionnels historiques sont conservés ; seul le paquet courant correspond aux sources finales.

## Limites et choix propriétaire non tranchés

- Inventaire statique, pas validation d'enregistrement/activation runtime. Namespaces et imports simples reconnus ; imports groupés, traits, fabriques et logique de contrôle dynamique restent à revoir. Les notices ne sont pas une preuve d'exhaustivité des passerelles runtime.
- Le plus petit ID de méta est une convention documentaire déterministe, **pas** une réparation ni un choix de facturation. Les anomalies restent intactes en base et visibles par leurs comptes.
- `requires_woo` est conservé sans ajout de périmètre. **Ced doit encore choisir conserver/retirer** ; aucune réponse n'est inventée. Même réserve sur une éventuelle extension future du registre des tables ; le registre conservateur actuel reste acceptable pour ce lot et ne prouve pas l'orphelinat.
- La première réexécution du runner de style existant a remplacé ses anciens fichiers racine `style/phpcs.json` et `style/receipt.json` (ancien comportement d'écrasement du runner), par le contrôle intermédiaire réel à 2 erreurs / 99 avertissements. Le stdout détaillé antérieur de ce contrôle auxiliaire n'a donc pas été conservé par cette invocation ; le bilan historique 0/99 reste dans les notes initiales. Le runner est désormais à sorties uniques, et les reçus suivants sont conservés. Aucun résultat n'a été reconstitué ou fabriqué pour masquer cet écart d'archivage.
- Les limites générales initiales (cache sans réseau, PHP CLI, droits Memberships sauvegardés et non rejoués par l'audit, etc.) restent celles du README.

## Fichiers concernés

`wp/outils/bascule/audit` ; `wp/tests/a02-audit/{unit.php,inside.py,seed.php,verify.py,documentation.py,style.py,README.md,test_documentation.py}` ; reçus, notes et marqueur dans `production/A-02/`. `run.py` existant réutilisé sans modification. Aucun Git, verrou, rapport parent, dossier de voie 2 ou fichier de pilotage modifié.
