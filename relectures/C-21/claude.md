# Relecture C-21 — Exporter et effacer les données d'un compte (Claude, indépendant)

Date : 26 novembre 2026. Cahier des charges : §4.4 (export et suppression depuis le back-office).
Code relu : `wp/plugins/imagine-site/Confidentialite.php`, `ConfidentialiteRegles.php`, leurs tests, les harnais `wp/tests/demo/c21-*`, `wp/outils/demo/c21*.py`, et les preuves `production/C-21/`.
Je n'ai pas ouvert `relectures/C-21/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée, sans argument)

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

```
REJEU : 1102 tests, 34454 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Conteneur jetable, sans réseau, dépôt monté en lecture seule. Suite entièrement verte.
Écart de comptage avec le sceau (`final.json` : 1097 tests / 34443 assertions, scellé à 06 h 43) : +5 tests / +11 assertions. Il s'explique par des lots postérieurs présents dans l'arbre (C-22 Newsletters / Partenaires, fichiers en cours dans `git status`), pas par C-21 : les fichiers C-21 ne sont pas dans la liste des modifiés et la suite reste à 0 échec.

## 1. Conformité

Le lot fait ce que demande le brief, sans régler de métier à la place de Ced.

- Standard d'abord : `natif.md` tient en **10 lignes** (contrôlé par le vérifieur), chacune citant une page officielle WordPress/WooCommerce/Subscriptions/Memberships. Aucun écran parallèle : uniquement des `add_filter`/`add_action` sur les outils natifs (`Confidentialite.php:15-43`).
- Export et effacement déclarés dans les hooks natifs `wp_privacy_personal_data_exporters` / `_erasers` (`Confidentialite.php:17-33`). Les callbacks natifs Woo/WCS/Memberships sont bien ceux attendus (`conservation-complete.json`).
- Réglages de conservation **inchangés** : `retention_before == retention_after`, valeurs lues et jamais écrites (`http-complet.json`, `conservation-complete.json`). Cité dans `A-VOIR.md` sans y toucher — conforme au brief.
- Abonnement en cours : comportement natif décrit, pas de règle ajoutée. Après effacement, la commande reste `pending` et la souscription `active`, propriétaire inchangé (`http-complet.json` → `commandes_abonnement_actif_comportement_natif_seul`).
- Interdits d'export (mot de passe, jeton, référence de paiement, note interne, adresse technique « sans email ») : filtrés par nom de champ dans `filtrerPage` (`Confidentialite.php:127-131`), neutralisation `.invalid` et email privé dans `texte` (`:99-111`), masquage jusque dans l'archive et son en-tête (`filtrerArchive:142-180`).
- Lignes de journal sans donnée d'abonné (extractions, C-18) : exclues sauf si l'abonné y est opérateur (`audit():235-238`) ; **dit explicitement dans l'inventaire** (ci-dessous et `rapports/…-V2.md` ligne 28). Conforme.
- Parcours sans email de confirmation : la demande native est créée confirmée par la route d'administration en omettant `send_confirmation_email` (`c21-http.py:19-25`) ; envois coupés (`security-final.json` → `mail_coupe`). Conforme au dernier point du brief.

Interprétation signalée par Hermès et que je confirme raisonnable : la **demande native d'effacement terminée est conservée tant que le compte existe**, comme seul support anti-recollecte, sans marqueur ni durée ajoutés (`conserverObservation:46-53`, documenté dans `A-VOIR.md` et le `PRET`).

### Inventaire des données attachées à une personne

| Donnée / stockage | Lot d'origine | Export natif | Effacement natif |
|---|---|---|---|
| Marqueur « sans email » `imagine_sans_email` | C-13/C-16 | groupe `imagine-meta` | méta retirée |
| Confirmation email `imagine_email_confirme` | C-09/C-12 | groupe `imagine-meta` | méta retirée |
| Préférences newsletters `imagine_newsletters_preferences` | C-22 | groupe `imagine-meta` | méta retirée |
| État de l'accès découverte `imagine_decouverte_compte_<id>` | C-12 | groupe `imagine-decouverte` | option retirée |
| Historique postal `imagine_envoi_releve_*` | C-13 | projection de la seule personne (`postal()`) | observation retirée/expurgée, tiers préservés |
| Gel postal `imagine_envoi_gel_*` | C-13 | même projection | CAS relu, numéro/calendrier/clôture conservés |
| Achats de numéros `_imagine_achat_numero_id` | C-14 | ajouté à l'export natif commande (`commerce()`) | objet laissé au standard Woo |
| Début de bloc `_imagine_envoi_bloc_debut` | C-13 | ajouté à l'export natif commande | objet natif |
| Dates de grâce `_imagine_acces_grace_debut/fin` | C-08/C-15 | ajouté à l'export natif souscription | objet natif |
| Justificatif : catégorie/décision/fin + fichier | C-17 | groupe `imagine-justificatif` (octets base64) | option + fichier supprimés, absence relue |
| Brouillon de commande (transient C16) | C-16 | groupe `imagine-brouillon` (sans token/empreinte) | transient supprimé |
| Journal des réglages C10 (opérateur, avant/après) | C-10/C-17 | groupe `imagine-audit` | lien + avant/après retirés, événement daté gardé, opérateur anonymisé |
| Journal d'extraction C18 (opérateur) | C-18 | **aucune donnée d'abonné** ; concerné seulement si l'abonné est opérateur | opérateur anonymisé, sinon intact |
| Coordonnées/commande/souscription | C-16 | exporteurs/effaceurs Woo/WCS natifs | natif |

Inventaire jugé complet : j'ai cherché les écritures `update_user_meta`/`update_option`/`set_transient` du plugin ; tout ce qui attache une donnée à une personne est couvert. Les agrégats C-19, le calendrier, les CSV sur poste et le stockage de lecture B-03 (navigateur) ne sont pas des dossiers personnels serveur — exclusion correcte.

## 2. Exactitude métier (cas déroulés à la main)

- **Observation partagée (un tiers sur le relevé d'un autre)** : `postal()` ne renvoie que ce qui touche l'identifiant demandé ; `destinataire`/adresse du payeur et les autres bénéficiaires ne sortent pas (`testExportPostalNeDivulguePasLesAutresBeneficiaires`, et `autres_personnes_non_divulguees` en HTTP réel sur `C21-PARTAGE`). Vérifié : `C21-AUTRE-PERSONNE`/`C21-AUTRE-BENEFICIAIRE` absents de l'export, préservés après effacement.
- **Cadeau (`origine = offert`)** : l'effacement du bénéficiaire efface aussi son adresse chez l'offrant (`retirerPostal:19-23`, `testCadeauEffaceAussiAdresseDuBeneficiaire`).
- **Gel, retrait d'un seul événement** : une observation étrangère est rendue inchangée, une observation propre devient `null` (donc bloc retiré), les bénéficiaires sont filtrés un à un (`retirerPostal` + `retirer():431-442`). CAS relu sur `option_value` binaire (`replace():377-404`). Après effacement, `imagine_envoi_gel_C21-FICTIF` garde `numero`/`calendrier`/`cloture`, `observations` et `blocs` vides (`gel_vide_conserve_numero_et_cloture`).
- **Journal C18, abonné = opérateur vs non** : l'opérateur abonné est anonymisé (`qui_id=0`, `qui_login='efface'`) en gardant le compteur `lignes` ; la ligne « sans abonné » (admin) reste strictement identique (`journal_C18_operateur_anonymise_compte_conserve`, `journal_C18_sans_abonne_inchange`).
- **Idempotence** : un second passage de l'effaceur ne retire rien (`effacement_idempotent` = `{removed:false, retained:false, done:true}`). L'effaceur relit toujours le début des enregistrements, pas de saut de page après retrait (`effacer():472-478`, comment `:247`).
- **Recollecte après effacement** : `anonymiserObservation` expurge à la source toute nouvelle observation visant un bénéficiaire dont la demande native est terminée (`:70-88`, `beneficiaire_efface_pas_recollecte`).

Résultats conformes au code dans tous ces cas.

## 3. Tests

- Suite complète verte (voir REJEU). PSR-12 : `phpcs-final.log` vide.
- Preuve proportionnée et réelle : HTTP natif **33/33** (POST admin sans email, AJAX paginé, ZIP HTML/JSON relue, octets du document vérifiés par SHA-256, deux pages réelles d'export et d'effacement, refus lecteur et nonce invalide), sécurité **9/9**, pannes/suppression native **8/8**, régressions **C08 30/30, C13 24/24, C09 382/382**.
- Les tests vérifient la règle, pas le code : ils comparent des valeurs attendues (adresses, bénéficiaires, compteurs, statuts d'objets natifs), pas la simple exécution.
- Cas limites couverts : relation inactive, cadeau, observation étrangère, panne disque sur le document, email technique hors `.invalid`. Compte fictif unique créé puis supprimé en `finally` (`compte_fixture_supprime_fin` = vrai), profils C-09 intacts (empreintes natives identiques hors jobs de cache de rapports WCS, exclusion justifiée et étroite).

Réserve de couverture (mineure) : la branche `wp_die(409)` de `supprimerCompte` (blocage de la suppression de compte quand un retrait reste incomplet) n'est pas exercée directement ; seul le retour `items_retained` de l'effaceur l'est (`c21-failures.php`). Le câblage « deletion refusée » n'a pas de test dédié.

## 4. Sécurité et données

- Aucun secret ni donnée réelle : site fictif `imagine-test-demo`, comptes fictifs, adresses `.invalid`/`@example.org`, jetons/notes de fixture volontairement interdits puis vérifiés absents de l'archive (`aucun_secret_note_ou_reference_paiement`).
- Droits/nonces : refus du lecteur et du nonce invalide sur export **et** effacement (`lecteur_*`, `nonce_*`). Les capacités restent celles des écrans natifs.
- Requêtes préparées : `$wpdb->prepare` partout (`demandeTerminee:58-63`, `options():210-225`, `replace():377-404`), `esc_like` sur les préfixes.
- Échappement des sorties : messages d'erreur via `esc_html__` dans `wp_die`. L'exporteur renvoie des paires `name/value`, rendues par le gabarit natif.
- Étanchéité : l'exporteur Imagine ne divulgue jamais un tiers ; après effacement une relecture de l'exporteur rend `{data:[], done:true}` (`relecture_export_Imagine_vide`). Les jetons de paiement sont retirés de l'export Imagine tout en gardant leur effaceur natif enregistré (`:19`).

Point d'attention (mineur) : le filtre de `filtrerPage` retire tout champ dont le nom contient `payment … method` ; il peut donc masquer aussi le **libellé** du mode de paiement dans l'export natif de la commande, au-delà de la seule « référence ». C'est prudent et sans risque de fuite, mais plus large que la lettre du brief — à garder en tête si l'on attend de voir « mode de paiement » dans l'archive.

## 5. Doctrine

- Standard d'abord : respecté, rien n'est reconstruit à côté des outils natifs (§4 doctrine).
- Logique métier hors WordPress : `ConfidentialiteRegles` est du PHP pur testable sans base, la couche WordPress reste fine (§4).
- Conventions §5 : `declare(strict_types=1)`, namespace `Imagine\`, préfixe `imagine_`, textes passés aux fonctions de traduction, README à jour, aucune modification d'extension tierce (seulement des hooks). Conforme.

Nit de code (mineur) : plusieurs `__()` reçoivent une variable (`commerce():204`, `exporter():364` → libellé `__('Imagine — ', …) . $kind`). Les chaînes dynamiques ne sont pas extractibles pour la traduction, et le libellé de groupe affiché au lecteur contient un code interne non traduit (`imagine-gel`, `imagine-brouillon`…). Visible dans l'archive, faible gravité.

## 6. Études

`natif.md` : 10 affirmations, chacune avec adresse de documentation officielle. Cohérentes avec les versions installées (`conservation-complete.json` : WP 7.0.9, Woo 11.2.2, Subscriptions 9.4.1) et avec le comportement observé (durées vides = pas de purge programmée, retrait des souscriptions `no` par défaut effectif). Pas de « doute » non sourcé.

## Décisions techniques, défaut proposé

1. **Clés de méta personnelles dupliquées en dur.** `Confidentialite::META` code en dur `'imagine_sans_email'` et `'imagine_newsletters_preferences'` au lieu de référencer `SansEmail::META` et `Newsletters::META`. Si un de ces lots renomme sa clé, l'exporteur/effaceur cesse **silencieusement** de traiter la donnée — un oubli d'effacement RGPD passerait inaperçu.
   - Catégorie : technique. Défaut proposé (Hermès applique, j'arbitre après) : référencer les constantes de classe (`SansEmail::META`, `Newsletters::META`) plutôt que des littéraux ; ajouter, si possible, un test qui échoue quand une clé personnelle connue n'est pas couverte par l'inventaire.

## Verdict

**Conforme** — ce n'est pas un GO (clôture réservée après fusion et second tour).

Points classés :
- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur** :
  1. Clés de méta personnelles en dur au lieu des constantes de classe (risque d'oubli silencieux si une clé est renommée) — voir « Décisions techniques ».
  2. Branche `wp_die(409)` de `supprimerCompte` non testée directement (blocage de la suppression de compte quand un retrait reste incomplet).
  3. `filtrerPage` peut masquer le libellé du mode de paiement, plus large que la « référence » visée par le brief — prudent, à confirmer comme voulu.
  4. `__()` avec arguments variables et libellé de groupe non traduit, visibles dans l'archive d'export.

`codex.md` existe déjà ; conformément à la consigne, je m'arrête ici et ne rédige pas la fusion.
