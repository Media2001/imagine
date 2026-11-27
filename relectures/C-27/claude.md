# Relecture C-27 — « Comment nous avez-vous connus ? » (Claude, relecteur indépendant)

Date : 2026-11-27. Brief : `briefs/C-27-comment-nous-avez-vous-connus.md`. Cahier des charges : §3.7, §4.2, §2.2.
Code lu : `wp/plugins/imagine-site/Acquisition*.php`, `imagine-site.php`, `README.md`, tests PHPUnit.
Ce verdict **n'est pas un GO** (doctrine §6). La fusion avec Codex n'est pas faite ; `codex.md` n'a pas été ouvert.

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus.

- **Après le paiement seulement** (§3.7). `Acquisition::question()` est accroché à `woocommerce_thankyou`, et `eligible()` exige `is_paid()` **et** `date_paid` non nul. Le tunnel n'ajoute aucun hook : rien avant le paiement. Conforme à « Rien de plus que le nécessaire avant le paiement ».
- **Facultative, liste fermée, une seule réponse** : `<select>` avec « Je préfère ne pas répondre » et « Continuer sans répondre ». Réponse vide = aucune écriture. Conforme.
- **Réglage C10 journalisé** (`AcquisitionReglages`) : une ligne `identifiant|libellé`, section additive sous « Enregistrer » comme C22/C24/C25 ; liste vide → aucune question (`question()` sort si `!$choices`). Journal avant/après/auteur/date ; panne du journal → préimage relue et réglage refusé. Conforme.
- **Source d'acquisition du compte (§4.2) seulement si vide** : `Acquisition::repondre()` ligne 123, `if (get_user_meta(...SOURCE) === '')`. Conforme.
- **Nombres sans identité** (`AcquisitionAdmin`) : tableau libellé/nombre, période UTC inclusive, aucun nom/compte/numéro de commande ; mêmes droits que C19. Conforme au « des nombres par réponse… aucune identité ».
- **Déclaré à l'export et à l'effacement C21** (`AcquisitionConfidentialite`). Conforme.
- **Règles** : jamais dans le tunnel ni sur une commande C16 (`via !== 'imagine-c16'`, marqueur réellement posé par `CommandeNative.php:189`) ; **ni Odoo ni newsletter** (aucune métadonnée ajoutée à la commande, meta `imagine_source_acquisition` isolée — vérifié : aucun lecteur externe de ce littéral dans `wp/`) ; **pas de champ libre** ; aucun style, paiement ou email. Conforme.

Interprétations signalées par Hermès (acceptables) : invités refusés sans rapprochement par email (cohérent avec C14 non livré) ; tableau « à côté » de C19 sous forme de sous-menu dédié ; `imagine_source_acquisition` stocké comme enregistrement structuré (voir §Décisions techniques).

## 2. Exactitude métier (déroulé à la main)

- **Achat payé, titulaire connecté, liste non vide** → `eligible()` vrai, clé de commande vérifiée, `VUE` posée une fois → formulaire affiché. Rechargement → `VUE` déjà posée (ou `REPONSE` présente) → rien. « Ne revient pas en boucle » : correct.
- **Double envoi** → la 2e écriture voit `REPONSE` non nulle (verrou `GET_LOCK` + unicité de l'option) → `WP_Error` → 403. Une seule réponse : correct.
- **Envoi par un autre compte / invité** → `actor !== owner` ou `actor = 0` → `eligible()` faux → 403. Correct.
- **Impayé / commande C16** → `eligible()` faux → ni formulaire ni écriture. Correct (témoin natif de mutation prévu).
- **Bornes de période** (`AcquisitionRegles::compter`) : `>= from.'T00:00:00Z'` et `<= until.'T23:59:59Z'`, inclusives. `2026-11-30T23:59:59Z` compte pour `au=2026-11-30` ; `2026-12-01T00:00:00Z` exclu. `from > until` → `null` ; date inexistante (`2026-11-31`) → `null`. Changement d'année (`2026-12-31`→`2027-01-01`) : comparaison ISO correcte. Correct.
- **Immutabilité et effacement** : réponse datée figée ; l'effacement (C21) est la **seule** exception, laisse `commande`/`etat=effacee` (sans date, source ni compte) pour interdire un redépôt, exclut la déclaration des nombres, et **préserve les tiers** (filtre par `owner`). Correct.

## 3. Tests

Suite PHP rejouée, commande autorisée sans argument, conteneur jetable hors réseau, dépôt en lecture seule. Dernière ligne :

```
REJEU : 1169 tests, 36380 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

- Les 7 tests C27 (`AcquisitionReglesTest`, `AcquisitionAdapterTest`) sont découverts par le paquet racine ; ils vérifient la **règle** (validation de liste, bornes, éligibilité paiement/propriétaire/C16), pas seulement le code.
- Point à signaler, **hors C-27** : la ligne `PAQUETS : 12 vérifiés, 1 échecs ; hors rejeu : aucun ; A-32 A32_PARTIAL_EVIDENCE` → un paquet scellé du **chantier A (A-32)** est en « preuve partielle ». Il est indépendant de C-27 (voie 2, chantier C) et le rejeu lui-même n'a aucun échec. À suivre côté chantier A ; sans incidence sur ce lot.
- Non rejoués par moi (hors commande autorisée) : le vérificateur parent `production/C-27/verifier.py`, les recettes mutantes Python (`c27-native.py`, `c27-recette.py`) et leurs contre-exemples. Les preuves correspondantes (mutants de source, témoins natifs, HTTP) sont reportées dans `NOTE.md`/`A-VOIR.md` mais non re-vérifiées ici.

## 4. Sécurité et données

- Nonces (`wp_nonce_field` / `wp_verify_nonce`), contrôle de méthode POST, `wp_die(403)` sur refus. Lecture seule GET/HEAD côté tableau (`405` sinon).
- Échappement systématique (`esc_html`/`esc_attr`/`esc_url`/`esc_textarea`) ; `$id` typé `int` avant écho. Requêtes préparées, `esc_like` sur le `LIKE`.
- Droits : tableau réservé via `TableauBordAdmin::autorise()` (mêmes droits que C19) ; réglage C10 via `register_setting`/`manage_options`.
- Aucun secret, aucune donnée réelle : libellés fictifs. Pas de contenu éditorial → paywall sans objet.
- **Étanchéité confirmée** : la réponse n'entre ni dans les métadonnées de commande Woo ni dans un événement de synchro ; la meta `imagine_source_acquisition` n'est lue par aucun autre lot (ni `Newsletters`, ni `ExtractionsNatives`, ni connecteur). Rien ne part vers Odoo ni Brevo.

## 5. Doctrine

- **Standard d'abord** : README, 5 lignes sourcées (attribution d'origine WooCommerce, CRUD/HPOS, exporter/eraser WordPress), références consultées listées dans `sources-officielles.json`. Conforme.
- **Logique métier hors WordPress** : `AcquisitionRegles` est pur, testable sans base ni WP. Conforme.
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\Site`, préfixe `imagine_`, textes en français traduits, README de l'extension mis à jour, aucun code d'extension tierce modifié (hooks seulement). Conforme (NOTE : 32 avertissements PSR-12 de longueur de ligne, 0 erreur).
- **Idempotence / rejouable** : unicité SQL de l'option + verrou utilisateur ferment doubles envois et course à la première source.

## 6. Études

Les cinq affirmations « standard d'abord » citent chacune une page officielle (WooCommerce order attribution, CRUD objects, exporter/eraser WordPress). Sourçage conforme à la grille §6 ; je n'ai pas ouvert les URL (hors réseau).

## Verdict : **Conforme**

Aucun point bloquant ni important relevé. Le lot est cohérent, testé, étanche sur le périmètre prouvé.

Rappels (ne lèvent pas le verdict, mais ne valent pas GO) :
- Validation **visuelle** de Ced attendue (squelette sans CSS) et emplacement de la section C10 « sous Enregistrer » — question visuelle déjà en attente.
- `verifier.py` et les recettes mutantes Python non re-rejoués ici (seule `rejouer.ps1` était autorisée).

### Points mineurs

1. `AcquisitionConfidentialite::effacer()` sur le hook `delete_user` fait `wp_die` si le nettoyage échoue : une erreur de lecture transitoire bloque la suppression du compte. Prudent pour la donnée personnelle, mais peut surprendre en suppression groupée. `AcquisitionConfidentialite.php:29-33`.
2. `lignes()` renvoie `WP_Error` au moindre enregistrement malformé : une option corrompue bloque export/compte/effacement entiers (jamais de faux zéro). Choix prudent assumé, à connaître. `AcquisitionConfidentialite.php:45-67`.
3. Écriture en base sur requête GET (`add_option(VUE…)` dans `question()` sur `woocommerce_thankyou`) : effet de bord sur GET, nécessaire pour « une seule proposition » ; `nocache_headers()` posé. Acceptable ; à garder à l'esprit si un cache de page très agressif est ajouté. `Acquisition.php:52-55`.

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

1. **Forme de `imagine_source_acquisition`.** Le champ « source d'acquisition » du compte (§4.2) reçoit l'**enregistrement structuré** complet (`commande`, `compte`, `date`, `choix`, `libelle`) et non le seul libellé. Question fermée : garder le tableau structuré, ou n'écrire que le libellé ? *Défaut proposé* : garder le tableau (daté, traçable), **et** documenter ce contrat dans le README pour un futur lecteur (tableau de bord C19, migration) qui pourrait attendre un scalaire. Aucun lecteur externe n'existe aujourd'hui, donc sans risque immédiat.

### Pour Ced (visuel / touchant au réel)

1. Emplacement de la section « Comment nous avez-vous connus ? » dans l'écran de réglages C10 (sous « Enregistrer », comme C22/C24/C25). *Défaut proposé* : conserver cet emplacement jusqu'à arbitrage visuel.

— Fin de la relecture indépendante. Fusion non effectuée (consigne).
