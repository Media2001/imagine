# Relecture C-18 — Les extractions (Claude, relecteur indépendant)

Date : 2026-11-26. Brief : `briefs/C-18-extractions.md`. CDC : §3.13 (« Extractions », « tout champ présent en base est extractible »). Production relue : `wp/plugins/imagine-site/extractions/*.php`, `ExtractionsRegles.php`, `ExtractionsNatives.php`, `ExtractionsAdmin.php`, `tests/ExtractionsReglesTest.php`, et les preuves de `production/C-18/`.

Je n'ai pas ouvert `codex.md`. Pas de fusion à ce stade.

## 0. Rejeu des tests (commande autorisée, sans argument)

Commande : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
Conteneur jetable : `network=none ; rootfs=ro ; mount=…/wp:/repo/wp:ro ; cap-drop=ALL ; no-new-privileges`.

Dernière ligne :

```
REJEU : 1077 tests, 34327 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

`ExtractionsReglesTest` est bien dans le lot (classe présente dans le JUnit, imagine-site = 13 fichiers de tests). Tout est au vert.

Note de transparence : mon décompte (1077/34327) dépasse celui consigné dans `A-VOIR.md` (1062/34271). L'écart tient à ce que l'arbre de travail porte maintenant aussi des lots postérieurs (C-20 : `wp/tests/demo/c20-native.php`, `wp/outils/demo/c20.py` modifiés dans `git status`) ; `rejouer.ps1` rejoue tous les plugins. Zéro échec malgré tout.

Limite de mon périmètre : je n'ai **pas** accès au site `imagine-test-demo` (droits : lecture du dépôt + tests locaux, aucun accès à un site). Les preuves de niveau site (refus 403 d'un compte sans droit, ouverture réelle du fichier, 9 téléchargements HTTP, contenu du journal in situ) viennent des preuves d'Hermès. Je les ai **déroulées sur la logique pure et par lecture du code et des CSV produits**, pas reproduites sur le site vivant.

## 1. Conformité

Conforme au brief, sans moins ni plus.

- Les quatre extractions de départ sont présentes et `disponible => true` : `localite.php`, `mode.php`, `echeance.php`, `etat.php`. (§3.13 : « abonnés par localité, par mode de paiement, par date d'échéance », états.)
- `age.php` et `etiquette.php` sont `disponible => false` : listées mais non exécutables, titre « — à venir ». Conforme à la consigne « grisées, mention à venir, ne fabrique pas ces données ». `catalogue()` les expose, `definition()` les refuse.
- Nombre de lignes affiché **avant** le bouton CSV : `ExtractionsAdmin::page()` rend `count($rows)` puis le formulaire de téléchargement (brief : « où l'on voit le nombre de lignes avant de télécharger »).
- Une extraction = un seul fichier (`extractions/<id>.php`) décrivant titre, colonnes, filtres, requête, prédicat `selection`. Ajouter une extraction de cette source ne touche pas le noyau (brief : « l'affaire d'un fichier »). Respecté.
- Logique de filtrage en code pur : `ExtractionsRegles` + closures `selection`/`validation`, testables sans WordPress (`ExtractionsReglesTest` tourne hors WP). Conforme à la doctrine §4 « logique métier hors de WordPress ».
- Lecture seule : `ExtractionsNatives::lire` lit l'état natif (comptes, abonnements) sans écrire. Seul effet de bord : une ligne de journal dans `preparer()`.

Interprétations signalées par Hermès (A-VOIR) et que je confirme : une ligne **par abonnement** (pas par abonné dédoublonné) ; correspondance **exacte** sur pays/code postal ; échéance = minimum des dates natives non vides. Voir §2 et les questions en fin de rapport.

## 2. Exactitude métier — cas déroulés à la main

**Cas A — Échéance, bornes inclusives (cas limite « date égale à la clôture »).**
Prédicat (`echeance.php:14-15`) : `echeance_utc !== '' && echeance_utc >= du.' 00:00:00' && echeance_utc <= au.' 23:59:59'`.
Filtre `du=2026-11-26`, `au=2026-12-26`. Les quatre lignes du test :
- `2026-11-26 00:00:00` → `>= '2026-11-26 00:00:00'` vrai → **inclus** (borne basse au grain seconde).
- `2026-12-26 23:59:59` → `<= '2026-12-26 23:59:59'` vrai → **inclus** (borne haute, fin de journée).
- `2026-12-27 00:00:00` → dépasse → **exclu**.
- `''` (pas d'échéance native) → **exclu**.
Résultat = deux premières lignes. Conforme au test `testEcheanceIncludesBothDateBoundariesAndExcludesMissing` et à A-VOIR (A-ECHEANCE inclus, A-EXPIRE exclu). La comparaison est lexicale sur un format `Y-m-d H:i:s` à largeur fixe, donc correcte. Validation `du <= au` : refuse la période inversée (`2026-12-27 > 2026-12-26` → exception), et `createFromFormat('!Y-m-d')` refuse `2026-02-30` (roule en mars → `format` diffère → « Date invalide »).

**Cas B — Localité, correspondance exacte (A-ETRANGER seul hors de Belgique).**
Prédicat (`localite.php:13-14`) : `($pays==='' || row.pays===$pays) && ($code_postal==='' || row.code_postal===$code_postal)`.
Rows du test : `{BE,1000}`, `{FR,1000}`, `{BE,10000}` ; filtre `{BE,1000}` → seule la 1ʳᵉ survit (FR exclu par pays, `10000` exclu par égalité stricte, pas de préfixe). Conforme à `testLocaliteUsesExactCountryAndPostalCode`. Le filtre pays impose l'ISO majuscule 2 lettres (`/^(?:[A-Z]{2})?$/D`) ; `fr` minuscule serait rejeté « Format invalide ». Vide = tous. Cohérent avec l'URL de preuve `…&pays=FR`.

**Cas C — État, libellés existants sans décision d'accès.**
`etat.php` filtre sur `row.etat === filtre.etat`, où `row.etat = MonCompte::etat($sub)` (projection B02 déjà en place, pas une décision de droit). `testEtatUsesExistingLabelsWithoutChangingRights` : `['En délai de grâce','Suspendu','Actif']` filtré sur `'En délai de grâce'` → une ligne. A-VOIR : Grâce sépare A-GRACE de A-SUSP, Suspendu ne rend que A-SUSP. Cohérent.

**Preuve « email vide » (CDC/brief).** `extraction-9_localite.csv` ligne 14 : `A-SANSMAIL` sort avec le champ `email` **vide**, pas une adresse technique. Code (`ExtractionsNatives.php:34`) : `get_user_meta(…SansEmail::META) === '1' ? '' : user_email`. Conforme (« comptes sans email → colonne adresse électronique vide »). Réserve mineure : le blanchiment repose **uniquement** sur le marqueur `SansEmail::META`, pas sur la détection d'une adresse `.invalid`. Un compte technique non marqué laisserait fuiter l'adresse — risque faible, cohérent avec C-13 qui pose le marqueur.

## 3. Tests

- Suite rejouée au vert (voir §0). Les tests C-18 couvrent : réemploi de la primitive CSV C-13 et liste blanche de colonnes (une `note_interne` est bien écartée), filtres invalides (pays non-ISO, saut de ligne, choix hors liste, `../secret`, dates invalides/inversées), rapports indisponibles listés mais non exécutables, et les quatre prédicats métier.
- Les tests vérifient la **règle**, pas le code : bornes d'échéance, égalité stricte localité, choix fermés — chacun avec des contre-exemples qui doivent être exclus.
- Cas limites présents : bornes égales à la clôture (échéance), changement de grain jour/seconde, échéance absente, période inversée, Feb-30.
- Manque assumé : la couverture de `ExtractionsNatives::lire` et de `ExtractionsAdmin` (nonce, capacité, 403, POST-only, journal) n'est **pas** dans le banc pur ; elle est portée par `c18-verifier.py` (HTTP/natif), que je ne rejoue pas (pas d'accès site). Je m'appuie sur les preuves d'Hermès pour ce pan. À signaler, non bloquant.

## 4. Sécurité et données

- **Données** : CSV de preuve 100 % fictifs (`@example.org`, « Personnage Fictif », « pas une offre »). `grep` IBAN/token/password/note sur les CSV : aucun. Colonnes limitées à la liste blanche `COLONNES` ; `csv()` lève `LogicException` si une colonne sort de la liste. Jamais de mot de passe, jeton, référence de paiement, IBAN ni note interne. Conforme au brief.
- **Droit dédié** : `CAP = imagine_extraire_abonnes` (réemploi C-09), `autorise()` exige `manage_options` ou cette capacité. `verifier()` → `wp_die(403)` sinon, appelé sur la page, l'aperçu, `preparer`, `exporter`.
- **Jeton** : `check_admin_referer(jeton($id,$filtres))` ; l'action du nonce intègre `hash(json([id, filtres]))`, donc un nonce valide pour un jeu de filtres n'est pas rejouable sur un autre. Nonce absent/non-chaîne → 403 explicite avant vérification.
- **Fichier à la volée** : `php://output`, aucun fichier serveur public ni privé ; en-têtes `private, no-store`, `Content-Disposition: attachment`, `X-Content-Type-Options: nosniff`. Conforme aux précautions C-13.
- **Protection tableur** : réemploi direct de `Imagine\Connecteur\CsvProtection::cellule` (primitive C-04/C-13, non modifiée) ; préfixe `'` sur `= + @ -` et espaces de tête. Vérifié par test.
- **POST only** : `exporter` refuse GET (405, `Allow: POST`). Hooké aussi en `nopriv` mais `verifier()` y referme (défense en profondeur).
- **Paywall / pas de fuite** : l'écran est back-office, derrière capacité ; pas de voie REST/flux ajoutée. `woocommerce_prevent_admin_access` est rouvert seulement pour cette page et ce compte autorisé.
- **Journal sans donnée d'abonné** : `preparer()` n'enregistre que `qui_id`, `qui_login`, `quand_utc`, `extraction`, `lignes`. Ni filtres, ni identité, ni contenu. Panne du journal → export refusé (fail-closed). Conforme au brief (« qui a extrait quoi, quand, combien ; pas le contenu »).
- **Aucun email, aucun appel sortant** : aucun `wp_mail`/HTTP dans le chemin. Conforme.
- **Requêtes préparées** : `journal()` utilise `$wpdb->prepare` + `esc_like`. Sorties échappées (`esc_html`/`esc_attr`/`esc_url`). RAS.

## 5. Doctrine

- **Standard d'abord** : réemploi du menu parent Imagine, de la capacité C-09, des API Woo/WCS en lecture CRUD, de `SansEmail::META`, de l'état B-02, du mode C-15, de la primitive CSV C-04/C-13. Aucune nouvelle base d'abonnés, aucun rôle global. Documentation officielle citée dans A-VOIR (nonces, CRUD Woo). Le sur-mesure se limite au catalogue + filtrage pur + écran, ce que le CDC §3.13 réclame explicitement (« outil d'extraction sur mesure »).
- **Conventions §5** : `declare(strict_types=1)`, espace `Imagine\Site`, préfixe `imagine_` (capacité, page, option de journal), textes via `__(…, 'imagine-site')`, aucune modification d'extension tierce. PSR-12 « zéro erreur » attesté.
- **Une règle ouverte devient un réglage** : la liste définitive des rapports est explicitement différée (« arrêtée avec Imagine »), le lot pose l'outil sans bloquer. Conforme.

## 6. Études

Sans objet (lot avec code).

---

## Verdict : **Conforme** — réserves mineures, aucune bloquante.

Rappel doctrine : ce verdict **n'est pas un GO**. Il ne vaut que pour la clôture technique d'un lot de code, et il reste suspendu à la seconde relecture (Codex), à la fusion, et à la validation visuelle de Ced (écran back-office). Je n'ai pas pu reproduire les preuves de niveau site.

### Points classés

**Bloquant** — aucun.

**Important**
- (I-1) Vérification site non reproduite de mon côté : les refus 403, l'ouverture du fichier et le contenu du journal in situ reposent sur `c18-verifier.py` / les preuves d'Hermès, hors de mon périmètre de droits. Ce n'est pas un défaut du code, mais la clôture ne doit pas traiter ces preuves comme doublement relues. À confirmer en fusion avec Codex.

**Mineur**
- (M-1) `ExtractionsAdmin.php:201` — le journal (`imagine_extraction_journal_<uuid>`, une option `wp_options` par extraction, autoload off, « sans purge ») croît sans borne ; `journal()` fait un `LIKE` à chaque affichage. Acceptable en démo ; prévoir une rotation/purge avant volume réel. *Défaut proposé : garder tel quel pour la démo.*
- (M-2) `etat.php:10-12` — les valeurs du filtre « État » sont les libellés français bruts, comparés à `MonCompte::etat()` qui passe par `__()`. Si une traduction `imagine-site` était un jour chargée, la clé posée (FR) ne correspondrait plus au libellé traduit et le filtre rendrait zéro ligne. Couplage libellé-comme-clé fragile. *Défaut proposé : garder (admin FR, aucune traduction chargée) ; à surveiller si i18n.*
- (M-3) `ExtractionsNatives.php:34` — email vide tributaire du seul marqueur `SansEmail::META` (cf. §2). *Défaut proposé : garder ; cohérent avec C-13.*

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)
- Pagination native de 100 et constitution en mémoire, sans qualification volumétrique. *Défaut : conserver pour la démo ; réévaluer avant un vrai volume (export en flux par lots).* 
- M-1 (purge du journal) et M-2 (clé d'état) relèvent de cette catégorie : défauts ci-dessus.

### Pour Imagine (réglages / métier)
- (Q-1) **Granularité des lignes.** L'extraction rend **une ligne par abonnement** : un compte à deux abonnements apparaît deux fois. Est-ce « abonnés » (uniques, dédoublonnés) ou « abonnements » qui est attendu dans ces listes ? *Défaut proposé : une ligne par abonnement (plus riche, déjà documenté), dédoublonnage ajouté plus tard si demandé.*
- (Q-2) **Filtre localité.** Correspondance **exacte** pays (ISO majuscule) + code postal. Imagine voudra-t-il filtrer par préfixe de code postal, plage, ou liste de pays ? *Défaut proposé : égalité exacte ; affiner à la demande.*

Ces deux questions ne touchent ni au réel ni au visuel : elles pourront devenir des réglages sans bloquer le lot.
