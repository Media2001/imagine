# Relecture A-02 — Audit de l'existant (Claude, indépendant)

Date : 2026-11-23. Relecteur : Claude, rôle indépendant. Je n'ai pas lu `codex.md`.
Objet : script `wp/outils/bascule/audit`, son banc `wp/tests/a02-audit/`, la production `production/A-02/`.
SHA-256 du script relu : `68aadda51ca1ed07310d4852dd8a5a7f1696442e78f883d0a8eecc4fd6798e07` (identique au PRET).

Le script est un collecteur PHP CLI mono-fichier, lecture seule : il tokenise `wp-config.php` sans l'exécuter, ouvre une transaction MySQL `READ ONLY`, n'émet que des `SELECT`, lit en-têtes/sources/journal, et écrit `audit.md` + `audit.json` dans un répertoire neuf hors du site.

---

## 1. Conformité

Le brief demande sept rubriques ; les sept sont produites et nommées (`collect()`, audit:596-598 ; titres Markdown audit:623).

| Rubrique brief | Produit | Référence |
|---|---|---|
| 1. Versions (WP, PHP, base ; par extension/thème : version, actif, dernière connue sans réseau, WP/PHP exigés) | oui | `inventory()` audit:210-274 |
| 2. Commerce (stockage, passerelles, abonnements état×périodicité, adhésions plan×état, commandes/an, produits d'abonnement) | oui | `commerce()` audit:312-376 |
| 3. Memberships (plans, règles, types/taxos, goutte-à-goutte) | oui | `memberships()` audit:378-405 |
| 4. Contenu (types/taxos+comptes, articles/an, champs fréquents, constructeur) | oui | `content()` audit:407-441 |
| 5. Base (tables taille/lignes, candidates au nettoyage, autoload lourds) | oui | `database()` audit:443-490 |
| 6. Planification (Action Scheduler par hook/état, WP-Cron) | oui | `scheduling()` audit:492-523 |
| 7. Risques (écart installé/dernier, >2 ans, gabarits Woo périmés, dépréciations du journal) | oui | `risks()` audit:525-588 |
| Synthèse « cinq points à regarder en premier » | oui | audit:611-617 |

Le cahier des charges ne fixe aucune règle métier propre à cet outil (il n'apparaît que dans l'objectif « disposer d'une référence avant la bascule », CDC l.163-166) : la spécification qui fait foi est le brief. Rien n'est produit au-delà du brief, sauf un champ `requires_woo` par extension (audit:239) non demandé — ajout utile et non sensible, à signaler comme un léger « plus » (mineur).

Les interprétations faites par Hermès sont signalées, conformément à la doctrine §1 : voir `limitations` (audit:604-610) et les étiquettes `*_detection` / `*_policy` / `coverage` dans chaque section. Points où l'interprétation mérite d'être relevée : §5.

## 2. Exactitude métier (déroulé à la main)

J'ai déroulé les cas contre la fixture `seed.php` et la sortie réelle `preuves/211ac0849094/classic/audit.md`.

- **Cas abonnements (brief §2).** `seed.php:36-52` crée 3 abonnements : statuts active / on-hold / pending-cancel, périodes month/month/year, intervalles 1/2/3. Sortie attendue : trois lignes (wc-active, month, 1, 1), (wc-on-hold, month, 2, 1), (wc-pending-cancel, year, 3, 1). Observé identique (audit.md:189-208). ✔
- **Cas goutte-à-goutte (brief §3).** `seed.php:21` pose une règle taxonomie `category` avec `access_schedule = '7 days'`. Attendu : `content_type=taxonomy`, `content_type_name=category`, `access_schedule=after_membership_start`, `drip=true`, `amount=7`, `period=day`. Observé identique (audit.md:276-289). La règle immédiate donne bien `drip=false`, `amount=null` (audit.md:261-274). ✔
- **Cas changement d'année / commandes (brief §2, §4).** Commandes semées en 2023, 2025, 2025 (`seed.php:53`) → `orders_by_year` = 2023:1, 2025:2 (audit.md:226-235). Les abonnements (`shop_subscription`) ne sont **pas** comptés comme commandes : le `WHERE` filtre `shop_order` (audit:321-324). Articles semés 2024/2025/2025 + l'article d'installation 2026 → `posts_by_year` 2024:1, 2025:2, 2026:1 (audit.md:577-590), cohérent avec `post`=4. ✔
- **Cas stockage faisant autorité (HPOS).** Le banc rejoue classique **et** HPOS ; sous HPOS les abonnements sont lus dans `wc_orders type='shop_subscription'` (audit:320) et les agrégats restent justes (assertion `hpos:subscription_aggregates`). ✔

Cas limites couverts par le banc : cache absent (inconnues explicites), journal absent, config dynamique/conditionnelle refusée, sortie existante refusée, symlink parent refusé, table orpheline, table non transactionnelle. Je n'ai pas trouvé de cas limite métier non couvert qui fausserait un chiffre.

## 3. Tests

- **Banc réel, non maquette.** `inside.py` installe un vrai WordPress 7.0.9 + WooCommerce 11.1.1 + Subscriptions 9.4.1 + Memberships 1.30.3 hors réseau, en conteneur isolé (`--network none`, caps retirées, MariaDB par socket). Les sorties `classic/audit.md` et `hpos/audit.md` sont **générées**, pas remplies à la main.
- **Vérificateur indépendant exécuté.** J'ai lancé `python wp/tests/a02-audit/verify.py production/A-02/preuves/211ac0849094` (lecture seule) : **PASS**, 122 assertions (15 unit + 100 intégration + 7 runner), empreintes base classic/hpos identiques, conteneur absent confirmé auprès de Docker, et surtout `current_source_hashes_match: true` — le paquet figé correspond bien au script **actuellement sur disque**. Les assertions testent donc le code livré, pas une version antérieure.
- **Je n'ai pas lancé `run.py`.** Il écrirait un nouveau paquet sous `production/A-02/preuves/`, ce que la doctrine m'interdit (§Droits : écriture limitée à `relectures/` et `corrections/`). Le vérificateur en lecture seule est l'outil adéquat pour mon rôle et recalcule lui-même l'empreinte logique à partir des hachages par table (`verify.py:39-41`), ce qui rend la preuve non circulaire.
- **Les assertions testent la règle, pas le code.** Oracle d'empreinte en PDO séparé sans charger WordPress ni le script (`fingerprint.php`), canaris privés semés puis recherchés dans les sorties (`inside.py:154`), piège d'exécution de `wp-config.php` (`seed.php:96`, assertion `never_bootstrap`), tentative d'écriture refusée même en root dans la transaction (`readonly-probe.php`). C'est de la vérification de propriété, pas une répétition du code.

Réserve : les assertions sont des contrôles nommés maison (pas un décompte PHPUnit), ce que le PRET et les notes assument honnêtement.

## 4. Sécurité et données

Solide, c'est le point fort du lot.

- **Aucune donnée personnelle ni valeur de réglage.** `identifier()` (audit:675-683) masque e-mails, balises, `..`, chemins absolus et motifs de jetons (`sk_`, `pk_`, `whsec_`, hex 40). Les valeurs d'options ne sortent jamais : seuls nom + taille en octets (autoload audit:485 ; `woocommerce_bacs_settings` apparaît par son nom seul, audit.md:988). Titres, utilisateurs, arguments de cron/actions exclus (`arguments_excluded`, audit:522). Le banc le prouve par canaris (`no_private_values`).
- **Config jamais exécutée.** `config()` lit par `token_get_all` et exige des littéraux au niveau supérieur ; dynamique/conditionnel → `A02_CONFIG_NON_LITERAL` (audit:42-86). Désérialisation sans classes ni magie (audit:16-40 ; `__wakeup` non appelé, prouvé).
- **Accès base verrouillé.** Transaction `REPEATABLE READ` + `READ ONLY` (audit:117-119), `MULTI_STATEMENTS` off, garde `SELECT`-seulement (audit:146-148), identifiants de tables validés par liste blanche et regex (audit:154-160), valeurs liées. Multisite refusé (audit:592-593). Écriture de sortie refusée si elle existe, est un lien, ou tombe dans le site (audit:653-654), fichiers en 0600 / dossier 0700.
- **Erreurs fermées.** Codes `A02_*` sur STDERR, jamais le SQL ni de trace (audit:697-701). Toute alerte PHP devient une exception et interrompt avant toute écriture (audit:689-694) : pas de rapport partiel.

Pas de paywall ici (lot en lecture seule) : rubrique §4-paywall de la grille sans objet.

## 5. Doctrine et interprétations à relever

- **Standard d'abord : justifié.** Les notes citent `get_plugins`, `wp_update_plugins`, HPOS, Memberships restrict-content, templates Woo, avec empreintes et HTTP 200 dans `sources-officielles.json`. Le choix de **ne pas** bootstrapper WordPress (qui déclencherait migrations/caches/hooks) est argumenté et cohérent avec « lecture seule ». Conventions §5 respectées (PHP 8.2, `strict_types`, espace de noms `Imagine\`, préfixe `imagine_` pour la sortie `IMAGINE_AUDIT_LIBRARY_ONLY`).
- **Attribution des tables (interprétation, à connaître).** Le registre de propriété est une liste statique WP + Woo + WCS + Action Scheduler (audit:459-477). Toute table d'une **autre** extension active (sécurité, SEO, cache, etc.) sera rangée en `unattributed_candidate`, alors que le brief §5 dit « n'appartenant ni à WordPress ni à une extension active ». Sans bootstrap, l'outil ne peut pas attribuer une table à une extension arbitraire : il sur-signale donc des candidates sur un vrai site riche en extensions. C'est **signalé** (`ownership_policy`, `limitations` : « unknown n'est pas une preuve d'orphelin, ne jamais supprimer »), donc acceptable, mais l'opérateur doit le garder en tête le jour de l'audit réel d'Imagine. (mineur)
- **Base temporelle des articles non déclarée.** `orders_by_year` est en UTC et l'étiquette le dit (`order_year_basis=UTC_creation`, audit:371, via `date_created_gmt`/`post_date_gmt`). `posts_by_year` utilise `post_date` **local** (audit:437) sans étiquette de base. Près d'un 1ᵉʳ janvier, un article peut basculer d'année selon le fuseau. Incohérence mineure et non documentée. (mineur)
- **« Champs personnalisés » = toutes les métadonnées.** `custom_fields` renvoie les 50 clés de postmeta les plus fréquentes (audit:424), dominées par des métas internes Woo/core (`_order_total`, `_billing_email`…) plutôt que des champs éditoriaux. Interprétation littérale défendable (noms seulement, aucune valeur) et disclosed, mais la liste est bruitée pour qui cherche les vrais champs sur-mesure. (mineur)
- **Emplacement `bascule/`.** La doctrine §4 décrit `wp/outils/bascule/` comme les scripts **numérotés qui transforment** l'existant ; l'audit y est posé en lecture seule. Le brief l'exige explicitement à `wp/outils/bascule/audit` et le README précise qu'il reste autonome et hors de `lancer`. Pas de contradiction réelle (le brief fait foi), simple tension à noter. (mineur)
- **PHP observé = CLI.** La version PHP rapportée est celle du runtime qui lance l'audit, pas du pool PHP-FPM du site (audit:268). Bien signalé dans les limites. (pour information)

## 6. Études (lot sans code)

Sans objet : lot avec code. La vérification documentaire (`documentation.py` + `sources-officielles.json`) est un plus honnête, séparée du banc, et chaque affirmation standard renvoie à une URL officielle avec occurrence du terme.

---

## Verdict : **Conforme** (un verdict n'est jamais un GO)

Le script fait ce que le brief demande, ni moins ni — à un champ près — plus. Lecture seule prouvée (empreintes base + fichiers inchangées), sécurité et confidentialité robustes, banc réel rejoué classique/HPOS, vérificateur indépendant relancé au vert et rattaché au script sur disque. Aucun défaut bloquant ni important trouvé.

**Points classés**

- Bloquant : aucun.
- Important : aucun.
- Mineur :
  1. Attribution des tables limitée à un registre statique WP/Woo/WCS/AS ; sur-signalement de candidates pour toute autre extension active (audit:459-477). Disclosed, mais à rappeler pour l'audit réel.
  2. `posts_by_year` en date locale non étiquetée vs `orders_by_year` en UTC (audit:437 vs 371).
  3. `custom_fields` = toutes les métadonnées (métas internes Woo incluses), pas seulement les champs éditoriaux (audit:424).
  4. Champ `requires_woo` produit mais non demandé par le brief (audit:239).
  5. Tension d'emplacement : outil en lecture seule rangé sous `bascule/` (brief l'impose ; sans gravité).
- Pour information : PHP rapporté = runtime CLI (audit:268) ; le gestionnaire d'erreurs strict interrompt tout l'audit sur la moindre alerte PHP (audit:689-694) — risque faible car aucun code tiers n'est chargé.

**À arbitrer par Ced** : aucune question fermée bloquante. Point unique ouvert, non bloquant : souhaites-tu que l'audit réel sur Imagine traite une table d'extension active hors registre comme « à examiner » (comportement actuel) ou qu'on étende le registre aux extensions retenues du §4.1 avant la bascule ? (peut rester tel quel pour clore le lot)

---

`codex.md` non lu. Fusion non effectuée : je m'arrête ici tant que `relectures/A-02/codex.md` n'existe pas ou n'est pas à croiser.
