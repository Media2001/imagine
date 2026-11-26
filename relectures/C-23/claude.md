# Relecture C-23 — Test d'étanchéité de livraison (Claude, indépendant)

Date : 26 novembre 2026. Relecteur : Claude. Codex non lu (consigne). Fusion non faite.

Brief : `briefs/C-23-test-d-etancheite-de-livraison.md`. Cahier des charges : §3.9 (l. 799+), §4.4 (l. 1128-1130 : « Un test automatisé vérifie, à chaque livraison, qu'un visiteur anonyme ne peut obtenir le texte réservé par aucune de ces voies »).

## En tête : fuite paywall ?

**Aucune fuite constatée** sur le corpus livré (matrice verte, 0 fuite). Rien à escalader vers un lot propriétaire d'une sortie. Je signale en revanche un **angle mort du détecteur** (§4 ci-dessous) : une fuite confinée à un attribut de balise de partage ne serait **pas** vue par la commande actuelle.

## Rejeu de la suite autorisée

Commande lancée, sans argument, depuis la racine :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, réseau `none`, dépôt monté en lecture seule, nettoyé. Dernière ligne :

```
REJEU : 1123 tests, 34569 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

**Mais** la ligne `OUTILS : 14 outils, 279 contrôles, 0 échecs ; hors rejeu : aucun` et le marqueur `T01_RESULT` montrent une suite **100 % PHP**. **Aucun test C-23 n'est dans ce rejeu** : le lot est un outillage Python (`c23.py`, `c23-tests.py`, `c23-verifier.py`, `c23-preparer.py`, `c23-inventaire.php`) qui interroge le site de démonstration en HTTP. Le rejeu conteneur n'exerce donc pas C-23.

Ce que j'ai pu rejouer moi-même, hors ligne, sans site : la suite unitaire du lot, `python -B wp/tests/demo/c23-tests.py` → **12 tests, OK**. Côté effet de bord : cette suite n'importe que `c23.py` et teste des fonctions pures (pas de réseau, pas d'écriture).

## 1. Conformité

- **Voies minimales du brief** : toutes présentes dans `build_routes` (`wp/outils/demo/c23.py:81-163`). Article, accueil, numéro, kiosque, thématique, archives ; REST contenu/recherche/révisions ; flux (rss2, rss, atom, rdf, flux-article) ; oEmbed + vue intégrée (`embed`) ; recherche interne ; `partage` + `extrait-automatique` ; `sitemap` ; PDF par téléchargement, par adresse directe médias, par pièce jointe. Conforme.
- **Publics imposés** : les 5 du brief sont la base de `PUBLICS` (`c23.py:17`). S'ajoutent **9 publics sans droit** issus du catalogue C-09 (`c23-inventaire.php:62-73`, `audience_order` `c23.py:19-23`). Plus strict que demandé, et assumé dans `INVENTAIRE.md`. Interprétation signalée, défendable.
- **Contrôle inverse** présent : `inverse-article`, `inverse-pdf` (phrase témoin **et** SHA-256 exact + `content-type` PDF), `inverse-C08` (`c23.py:264-266`). Sans lui, le vert ne prouverait rien.
- **Mutation témoin** présente et séparée de la commande GET : ouverture provisoire du seul article 42 (`c23-preparer.py:113-124`), rouge attendu puis restauration.
- **Sortie** conforme : matrice voies × publics + ligne `ETANCHEITE : <n> contrôles, <n> fuites — PASS|FAIL` + code 0/1 (`c23.py:288-300`).
- **« En lecture seule »** : la **commande** `c23.py` est GET pur (vérifié : `methods==['GET']`, aucun import `subprocess`, `c23-tests.py:63-67`). La **préparation/restauration** écrit en base (sessions, réglage découverte, méta `imagine_reserve` en mutation) **hors** commande — `c23-preparer.py:66-124`. C'est l'interprétation retenue du brief (qui autorise la mutation « par un réglage remis ensuite ») et elle est signalée (A-VOIR, INCIDENTS). Conforme à la lettre ; à connaître.
- **§4.4 « à chaque livraison »** : livré comme **commande rejouable**, pas comme déclencheur automatique de livraison ; limite assumée (hébergement). La « commande unique » du brief est en pratique une exploitation en 3 étapes (`c23-preparer.py` → `c23-tests.py` → `c23-verifier.py`) autour d'un unique GET. Mineur, disclosed.
- **Plan de site** : la voie prouve seulement la **fermeture 404** actuelle (sitemaps désactivés nativement, `c23.py:120-127`), pas l'étanchéité d'un sitemap **activé**. Chemin « activé » présent dans le code mais non exercé. Limite assumée.

## 2. Exactitude métier (déroulé à la main)

- **Anonyme × article réservé T4** : session `{}`, `present=titre`, témoins = marqueurs dont `CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1`. Attendu : titre visible, témoin absent. `assess` (`c23.py:37-43`) : statut 200 ∈ attendus, surface présente, aucun témoin → `ok=True`. Matrice : OK. Conforme.
- **Abonné actif (contrôle inverse) × article + PDF** : `positive=True`. Attendu : témoin **présent**, et pour le PDF SHA-256 exact + `content-type` PDF (`c23.py:246,265`). Si le paywall était trop fermé → `ok=False` → FAIL. Reçu : `inverse_article_pdf=true`, `witnesses_found>0`. Prouve la non-trivialité du vert.
- **Acheteur d'un autre numéro** : T1 possédé lisible (C08 appartient au T1), T4 refusé. Les marqueurs de l'émission possédée sont retirés des témoins interdits pour ce public (`c23.py:268`), contrôle positif `pdf-inventorie-11-endpoint` OK et `pdf-telechargement` (T4) sans témoin. Vérifié : `C14_owned_allowed_other_denied=true`. Conforme.
- **Découverte épuisée** : `V-DEC-FIN` réellement épuisé ; bloc `decouverte_epuisee` exigé (`c23.py:243-244`). Le `V-DEC` encore ouvrable n'est **pas** consommé (lecture seule). Bon choix.
- **Mutation** : article 42 ouvert → **177 fuites**, `article × anonyme` fuit, code **1** (`mutation-publics-complets.json`/`-restauration.json`), puis `native_before_sha256 == native_after_sha256` (`4d81b43e…`) et `metadata_restored_exactly=true`. Restauration exacte prouvée. Conforme.

## 3. Tests

- Rejeu PHP autorisé : **PASS** (ligne reportée ci-dessus), mais **n'exerce pas C-23**.
- Suite unitaire du lot rejouée par moi hors ligne : **12/12 OK**. Vrais tests comportementaux : fuite détectée (`test_fuite_texte_reel_refusee`), garde réseau (`validate_path`), CDATA non masquant, recherche réfléchie non assimilée à une fuite, inverse nécessaire, GET seul. Qualité correcte — ils vérifient la règle, pas seulement le code.
- **Limite de ma vérification indépendante** : je **ne peux pas** reproduire la matrice live. `c23.py` exige le site `http://192.168.129.32:8085` + réseau ; le conteneur est read-only/no-network ; mes droits interdisent l'accès au site/à la base et l'écriture dans `production/`. Donc **« 1432 contrôles, 0 fuite, PASS » repose sur les reçus d'Hermès**, que j'ai lus (totaux cohérents : `livraison.json` total 1432, leaks 0, failures 0) mais **non reproduits**. `c23-verifier.py` recoupe la cohérence interne (25 contrôles, 0 échec) mais (a) **écrit dans `production/`** `verification.json` (`c23-verifier.py:63`) — non lancé par moi, interdit à un relecteur ; (b) réutilise `c23.py` → preuve non indépendante.
- Lacune de couverture : **aucun test ne couvre la fuite par attribut de partage** (§4). C'est précisément le cas non détecté.

## 4. Sécurité et données

- **[Important] Angle mort du détecteur — fuite par attribut HTML.** `canonical` retire tout attribut : `re.sub(r'<[^>]*>', ' ', text)` (`c23.py:34`). Une fuite de texte réservé confinée à un attribut (`og:description`, `twitter:description`, `meta name=description`, `data-*`) est donc **invisible**. Vérifié hors ligne avec le détecteur réel :
  - corps visible → `leak=True` ✔
  - `og:description content="…témoin…"` → **`leak=False`** ✗ (`canonical` ne garde que « extrait public »)
  - JSON-LD entre balises `<script>` → `leak=True` ✔

  La voie « balises de partage » / « extrait automatique » est nommée au brief ; sa **détection de fuite est partielle** (la structure est vérifiée présente, `c23.py:171-172`, mais pas le contenu des attributs). Pas de fuite live aujourd'hui, mais le test pourrait rester **vert** après une régression qui enverrait du texte réservé dans `og:description`. Correction proposée : scanner aussi les valeurs d'attributs des balises meta/partage connues (brut), et ajouter une régression « témoin dans `og:description` → rouge ».
- **Secrets** : aucun dans les reçus (grep `wordpress_logged_in_|X-WP-Nonce|Set-Cookie|session_tokens` → vide ; `no_session_dump=true`). Cookies/nonces en mémoire/stdin, jamais écrits (`c23-preparer.py:85-87`). Bon.
- **[Mineur] Restauration non transactionnelle** : `finally` + instantané de métadonnées (`c23-preparer.py:125-136`). INCIDENTS documente un cas réel où une chaîne tuée a laissé un résidu récupéré **à la main** via `c23-recovery.py`. Pour un usage « à chaque livraison », c'est un risque opérationnel. Assumé, état final prouvé propre.
- **[Mineur] SHA natif figé en dur** : `business_original_exact … == '4d81b43e…'` (`c23-verifier.py:43`). Toute évolution légitime de la démo fera un faux rouge. Robustesse.

## 5. Doctrine

- **Standard d'abord** (§4) : le détecteur consomme les sorties natives WP/Woo ; **aucun code de paywall, thème ou extension n'est modifié**. Conforme.
- **Langage Python** : cohérent avec l'outillage de démo existant (`b05`, `profils`, `b00_fixtures`). Ce n'est pas une dérive introduite par C-23 ; §5 (PHP 8.2/PSR-12/namespace `Imagine`) vise le code produit WordPress, pas ce harnais HTTP de test.
- **Ce lot ne modifie pas le paywall** : respecté.

## 6. Études

Sans objet (lot avec code).

---

## Verdict : À corriger

Un verdict de relecture n'est jamais un GO.

- **Bloquant** : aucun. Pas de fuite paywall constatée.
- **Important**
  1. Angle mort « attribut de partage » (§4) : une fuite dans `og:description`/`twitter:description`/`data-*` n'est pas détectée (confirmé hors ligne). Ajouter le scan des attributs + une régression. Tant que ce n'est pas corrigé, la voie « balises de partage » n'est pas pleinement prouvée.
  2. Vérification indépendante limitée (§3) : la matrice live n'est pas reproductible par le relecteur ; le rejeu conteneur PHP n'exerce pas C-23 ; la preuve « 1432, 0 fuite » repose sur les reçus d'Hermès, lus et cohérents mais non reproduits.
- **Mineur** : restauration non transactionnelle (risque pour l'automatisation, assumé) ; SHA natif figé en dur dans le vérificateur ; « commande unique » = 3 étapes d'exploitation ; sitemap prouve seulement la fermeture 404.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre)

1. **Attributs HTML dans la détection de fuite.** Défaut proposé : étendre la recherche de témoins aux valeurs d'attributs des balises meta/partage connues, plus un test de régression `og:description`. Catégorie : technique.
2. **Le vérificateur de paquet écrit dans `production/`.** Défaut proposé : écrire la sortie de `c23-verifier.py` sur stdout (ou hors `production/`), pour qu'un relecteur puisse la rejouer sans violer ses droits et sans toucher aux livrables. Catégorie : technique.
3. **Périmètre des publics.** Défaut proposé : conserver les 14 publics (plus strict que les 5 nommés). Catégorie : technique.

## Pour Imagine (métier)

Aucune règle métier à trancher dans ce lot.

## Pour Ced (visuel / réel)

Aucune question visuelle ni touchant au réel : la démonstration est fictive et neutralisée, aucune donnée réelle, aucun compte, aucun appel extérieur.

---

**Étape suivante** : `relectures/C-23/codex.md` existe mais n'a pas été ouvert. Je m'arrête après la relecture. La fusion (`corrections/C-23.md`) reste à faire, sur demande.
