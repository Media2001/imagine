# Vérification C-21 — deuxième et dernier tour (Claude)

Lot : « Exporter et effacer les données d'un compte » (§4.4). Corrections fusionnées : `corrections/C-21.md` (verdict de fusion « À corriger », retenu de Codex). Code relu de nouveau : `wp/plugins/imagine-site/` ; preuves : `production/C-21/`.

Méthode : `git diff` entre le commit de la fusion `a4d0be01` (« synchro 2026-11-26 09:13 », juste après l'écriture de `corrections/C-21.md`) et `HEAD`, sur `wp/` et `production/C-21/`, puis rejeu de la suite PHP. Entre la version relue (`dea00c6d`, 09:03) et la fusion, seul `corrections/C-21.md` a été ajouté : aucune source n'a bougé, le diff capture donc bien les corrections d'Hermès. Pas de relecture complète refaite ; je contrôle l'application des sept instructions + les deux décisions techniques, les tests, et les régressions.

## 1. Instructions de `corrections/C-21.md` (§4)

### Instruction 1 — C21-06 (bloquant) : cloisonner opérateur et client dans le brouillon — **Appliquée**

- Nouveau `clientBrouillon()` (`Confidentialite.php:247-252`) : identifie le **titulaire** par `resultat['client']` puis `client.id`, sinon par e-mail ; il ne reconnaît plus jamais l'opérateur via `qui`. `draft()` (`:254-257`) reste large (`clientBrouillon` **ou** `qui`) mais sert seulement à repérer la ligne.
- Export : si le demandeur n'est pas le titulaire, le brouillon n'expose plus que « A préparé un brouillon » — **aucun** nom, e-mail, adresse du client (`:377-380`). La projection complète (`client`, `commande`) est réservée au titulaire (`:381-396`).
- Effacement symétrique : un opérateur qui exerce ses droits ne supprime plus le brouillon du client ; `qui` est seulement remis à 0 (`:491-497`). La suppression effective du transient reste réservée au titulaire (`:498-504`).
- Preuve rejouée (fixture réelle, deux comptes distincts, `mode=nouveau`) : `operateur_sans_aucune_PII_client`, `operateur_activite_propre_exportee`, `effacement_operateur_preserve_dossier_client_exact` — tous verts (`fusion-native-final.json`). La fuite affirmée par Codex est fermée.

### Instruction 2 — C21-01 (important) : rattacher le brouillon à son titulaire réel — **Appliquée**

- `clientBrouillon()` lit l'id du compte créé dans `resultat['client']` (`:250`), exactement la clé posée par `CommandeNative::creer()`. Plus de rapprochement approximatif par nom.
- Preuves C-16 réelles « nouveau sans email » (`fusion-native-final.json`) : `C16_sans_email_effacement_rattachement_reel`, `C16_sans_email_suppression_rattachement_reel`, et retrait des transients avant expiration (`..._transient`) — verts. Le marqueur `SansEmail::META` est bien vérifié.

### Instruction 3 — C21-02 (mineur) : exporter la clé réellement produite — **Appliquée**

- La projection lit désormais `commande.paiement` sous un libellé français (`match` → « Virement » / « Mandat papier » / « Non renseigné », `:388-392`) ; la clé fantôme `mode_paiement` a disparu.
- La fixture `c21-runtime.php:92-96` est reconstruite à partir du schéma réel `CommandeRegles::commande()` (clé `paiement`), au lieu de la mauvaise clé qui masquait l'écart.
- Preuves : `mode_reglement_reel_exporte` (natif) et `draft['Mode de règlement'] == 'Virement'` (HTTP, `c21-http.py:118`).

### Instruction 4 — C21-03 (important) : ne pas suspendre le groupe pour le retrait d'un membre — **Appliquée**

- `ConfidentialiteRegles.php:57-58` : la ligne inconditionnelle `beneficiaires_resolus = false` est supprimée. Commentaire : un retrait certain ne transforme jamais les attributions restantes en inconnues ; une origine non résolue reste non résolue (aucun droit nouveau).
- Tests PHP purs : `ConfidentialiteReglesTest::testEffacementNeModifiePasUneObservationEtrangereDuGel` asserte maintenant `beneficiaires_resolus === true` après retrait ; `testRetraitNeResoutJamaisUnGroupeInconnu` prouve qu'un groupe initialement `false` le reste (pas de droit créé).
- Preuve bout-en-bout (Memberships natifs, `imagine_envoi_groupes = liens_memberships`) : `gel_reel_retrait_membre_tiers_lignes_exactes`, `CSV_reel_retrait_membre_tiers_servi`, `export_beneficiaire_retrait_autre_sans_perte_exact` — verts. Les autres membres restent servis.

### Instruction 5 — C21-04 (important) : préserver les données postales des tiers à l'effacement du titulaire — **Appliquée**

- `ConfidentialiteRegles::retirerPostal` (`:15-37`) : quand le demandeur est `donnees.user`, on n'annule plus l'observation entière. On anonymise la seule part du payeur (`user = '0'`, adresse d'expédition vidée hors cas `offert`) et on conserve bénéficiaires, liens et adresses. `null` n'est renvoyé que s'il ne reste **aucun** tiers.
- `Confidentialite::anonymiserObservation` (`:76,84-86`) traite aussi le propriétaire une fois son compte supprimé, pour l'anti-recollecte, sans toucher aux tiers. `conserverObservation` (`:49-51`) conserve l'observation tant qu'il reste des bénéficiaires après retrait du seul payeur.
- Tests PHP purs : `testEffacementOffrantPreserveAttributionEtAdresseExactesDuBeneficiaire` (adresse exacte du bénéficiaire conservée, `user=0`). Preuves bout-en-bout : `gel_reel_retrait_payeur_groupe_tiers_exact`, `offrant_efface_cadeau_postal_exact`, `offrant_efface_export_beneficiaire_exact`, `recollecte_payeur_et_membre_effaces_ne_reviennent_pas` — verts.

### Instruction 6 — C21-05 (mineur) : contrat de succession du sceau — **Appliquée**

- Le sceau historique `final.json` et les reçus qu'il nomme sont intacts ; `final-fusion.json` en est le successeur (épingle leurs empreintes + les nouveaux fichiers + les preuves rejouées). `fusion-contrat.md` documente la chaîne et l'évolution autorisée C-22 (`imagine_newsletters_preferences`).
- `c21-verifier.py` délègue désormais à `c21-fusion-verifier.py` quand `final-fusion.json` existe (`c21-verifier.py:133-140`), en lecture seule ; aucun ancien hash n'est remplacé. La commande de validation peut réussir sur l'arbre intégré. `final-fusion.json` : `status = PRET_TECHNIQUE_C21_FUSION`, `failures = []`, `retention_settings_changed = false`, `C09_profiles_preserved = true`, `real_authorization = false`.

### Instruction 7 — Claude-2 (mineur) : test de la branche `wp_die(409)` — **Appliquée**

- `c21-failures.php:44-72` : vrai `wp_delete_user`, panne CAS forcée sur la seule découverte fictive, capture du `wp_die` (code 409, message « nettoyage Imagine incomplet »), puis vérification que le compte **et** la donnée non retirée sont conservés, et que la suppression réussit après levée de la panne. Preuve : `fusion-failures-final.json` (10/10, failures []).

### Décisions techniques (Hermès applique, Claude arbitre après)

- **Claude-1 — clés de méta en dur — Appliquée.** `Confidentialite::META` (`:10`) référence maintenant `SansEmail::META` et `Newsletters::META` au lieu de littéraux. Un test échoue si ces constantes disparaissent de la source (`testTraductionsConfidentialiteOntToutesUnPremierArgumentLitteral`, assertions `SansEmail::META` / `Newsletters::META`). **Arbitrage : OK**, les trois valeurs sémantiques sont conservées à l'identique.
- **Claude-3 — traductions — Appliquée.** Libellés de groupe par `match` littéral (`groupe()`, `:258-271`) ; mode de règlement par `match` littéral ; les `__()` à argument variable (audit `:204-210`, en-tête de groupe `:400`) sont remplacés par des chaînes fixes. Le test ci-dessus vérifie que **tous** les premiers arguments de `__()`/`esc_html__()` de `Confidentialite.php` sont des littéraux. **Arbitrage : OK.**

## 2. Résultat des tests

- Suite PHP rejouée en conteneur jetable (réseau `none`, dépôt monté en lecture seule), commande autorisée sans argument :
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
- Dernière ligne :
  **`REJEU : 1114 tests, 34560 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`**
- `ConfidentialiteReglesTest` passe de 3 à **7 tests / 78 assertions**, tous verts, dont les trois nouveaux qui couvrent précisément C21-03, C21-04 et les littéraux i18n + constantes de méta. Le cœur du lot est désormais couvert par des tests **rejouables par le relecteur**, et non plus seulement par les JSON d'Hermès.
- **Limite (comme en C-21 premier tour et en C-20).** Les chemins couplés à WordPress (export/effacement complets, gels, CSV, parcours C-16, HTTP) ne sont pas dans la suite pure : ils vivent dans les sondes `imagine-test-demo` (`c21-fusion-native.php`, `c21-fusion-http.py`, `c21-fusion-verifier.py`), que je ne peux pas rejouer (pas d'accès staging, hors réseau, dépôt en lecture seule). Conformément au précédent accepté, je m'appuie sur les preuves d'Hermès, liées au code par empreinte. J'ai contrôlé que le code de test est réel et que les reçus sont verts : `fusion-native-final.json` (24/24), `fusion-failures-final.json` (10/10), `fusion-green-draft.json` (13/13), `final-fusion.json` (failures []). Les 24 clés de `fusion-native-final.json` correspondent une à une aux assertions de `c21-fusion-native.php` ; chacune des sept corrections y a au moins une preuve verte explicite.

## 3. Régressions ou modifications non demandées

- **Dans le périmètre C-21 : aucune.** Les seuls fichiers de code C-21 modifiés (`Confidentialite.php`, `ConfidentialiteRegles.php`) le sont uniquement pour les instructions listées ; chaque changement se rattache à une instruction (cloisonnement brouillon, préservation des tiers, i18n, constantes de méta, anti-recollecte). Réglages de conservation toujours lus, jamais écrits (`retention_settings_changed = false`). Profils C-09 et actions planifiées préservés (`profils_C09_et_actions_exacts` vert, `final.json` 8793/pending intact).
- **Hors C-21 (lots parallèles, non bloquant).** Le `git diff a4d0be01→HEAD` montre aussi des changements C-20 / C-22 (`Renouvellement.php` i18n par `match`, `C20PaywallAdapterTest` dont le motif attendu passe de `droits_expires` à `expire`, `c20-fusion*`). Ils ne touchent pas la confidentialité et la suite complète reste verte ; ils relèvent des vérifications de ces lots, pas de C-21.
- **Anomalie de propreté (hors C-21, non bloquant).** Un fichier parasite `prefix}u0024s` traîne à la racine du dépôt (untracked), vraisemblablement un résidu de shell. Sans rapport avec le code C-21 ; à supprimer. Hors de mon périmètre d'écriture, je me contente de le signaler.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les sept instructions et les deux décisions techniques sont **appliquées** ; les trois fuites/destructions de données de tiers qui motivaient le verdict de fusion « À corriger » (C21-06, C21-03, C21-04) sont fermées et prouvées, en tests PHP purs rejoués ici **et** en sondes bout-en-bout vertes. La suite est verte (1114 tests), aucune régression dans le périmètre, aucun problème de fond restant.

Il reste trois questions **métier/visuelle** rangées en défaut prudent dans la fusion (§5), que la validation de Ced doit confirmer — elles ne bloquent pas la clôture (doctrine « une règle ouverte devient un réglage ») :
1. Groupe, retrait d'un membre : les autres membres continuent d'être servis (défaut appliqué : **oui**).
2. Cadeau, effacement de l'offrant : le bénéficiaire conserve adresse et numéro (défaut appliqué : **oui**, part de l'offrant anonymisée).
3. Libellé du mode de paiement natif (Claude-4) : **masquage large conservé** (défaut appliqué).

**Rappel (doctrine §6) : ce verdict n'est pas un GO.** Il ne vaut que pour la clôture d'un lot de code. Les preuves couplées à WordPress sont celles d'Hermès sur `imagine-test-demo` (non rejouables par le relecteur) ; `real_authorization = false` (aucun compte réel, aucun envoi, aucune action Git).
