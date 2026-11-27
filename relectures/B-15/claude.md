# Relecture B-15 — Pied de page identique sur toutes les pages

Relecteur : Claude (indépendant). Date : 2026-11-27.
Brief : `briefs/B-15-pied-de-page.md`. CDC : §3.2 (« Pied de page identique… »).
Code relu : `wp/plugins/imagine-site/PiedPage.php`, `wp/themes/imagine/footer.php`, tests `PiedPageB15Test.php`, `wp/tests/demo/b15-pure.php`, `wp/tests/demo/b15-runtime.php`, README B-15 (l. 654-665), `A-VOIR.md`, `reading.css`.

> `codex.md` existe mais n'a **pas** été ouvert. Pas de fusion à ce stade.

## 1. Conformité

- Les cinq zones sont rendues une fois, dans l'ordre exact du brief : `PiedPage::ZONES = ['abonnement','newsletter','numero','point-vente','mentions']`, bouclé par `rendre()` (`PiedPage.php:11,77`). Conforme §3.2 et au brief.
- **Abonnement** : lien « S'abonner » vers `Navigation::abonnementUrl()`, soit la page `abonnement-en-attente` résolue dynamiquement (`PiedPage.php:81-83` / `Navigation.php:70-74`) — même cible que l'entrée du menu principal. Conforme.
- **Newsletter** : lien « Nos newsletters » vers `/nos-newsletters/`, **aucun champ de saisie** (`PiedPage.php:86-87`). L'absence de formulaire est vérifiée par le test runtime (`pas_saisie_ni_script`). Conforme : l'inscription visiteur attend Brevo.
- **Numéro en cours** : couverture miniature + titre + lien, via `Accueil::numero()` → `imagine_issue_query(1)`, **la même règle que l'accueil** (`PiedPage.php:56-62`, `Accueil.php:15-18`). Conforme (« le même numéro… par la même règle »).
- **Point de vente** : lien « Trouver un point de vente » vers `/points-de-vente/` (page B-10, `b10-seed.php:17`). **Aucune géolocalisation** (navigateur, IP ou tiers) dans le code. Conforme.
- **Mentions** : `wp_nav_menu` sur l'emplacement `imagine-footer` existant, `fallback_cb => false`, sans recréer ni dupliquer le menu (`PiedPage.php:94-104`). Les 5 liens B-09 restent une fois chacun ; le lien « Points de vente » ajouté au menu par B-10 est conservé. Conforme.
- **Identique partout / anonyme = connecté** : le rendu ne dépend d'aucun contexte utilisateur ; les indicateurs de page courante du **seul** menu de pied sont neutralisés au rendu (`classes` retire `current[-_]*`, `page_item`, `page-item-N` ; `attributs` retire `aria-current`) sans toucher au menu stocké (`PiedPage.php:28-48`). Conforme au « même HTML pour un anonyme et pour A-PAPIER ».
- **Mode lecture B-03** : le footer n'est pas masqué par le code B-15 mais par le CSS existant `reading.css:30-35` (`.imagine-reading .imagine-shell > footer { display:none }`). Structure du thème vérifiée : `<div class="imagine-shell">` → `<footer>` est bien enfant direct (`header.php:16`, `footer.php:8`), donc le sélecteur s'applique. Comportement B-03 **inchangé**, comme demandé. Conforme (masquage visuel ; le HTML reste dans le DOM, ce que le brief admet).
- **Standard d'abord** : les trois lignes demandées sont écrites (README l. 656-659) — emplacement de menu natif + `wp_nav_menu`, zone de widgets `register_sidebar` disponible mais **non utilisée** (ordre et contenu imposés), `footer.php` natif + Transients. Conforme.
- Interprétation signalée : les slugs `/nos-newsletters/` et `/points-de-vente/` sont écrits en dur (non résolus par `get_page_by_path`, contrairement à `abonnement`). Choix documenté au README ; voir point mineur 2.

## 2. Exactitude métier — cas déroulés à la main

1. **Page légale vs accueil (anonyme).** Sur `/mentions/` le menu de pied porterait normalement `current-menu-item` / `aria-current` sur l'entrée Mentions. Les filtres les retirent pour `theme_location === 'imagine-footer'` → le `<footer>` est octet pour octet celui de l'accueil. Déroulé cohérent avec le code et confirmé par la preuve HTTP (dix réponses identiques, comparaison brute sans normalisation).
2. **Anonyme vs A-PAPIER, même page.** Aucun branchement sur `current_user` dans `rendre()`/`numero()` ; liens, numéro et menu identiques. Conforme.
3. **Publication d'un numéro plus récent.** `save_post_imagine_numero` → `invalider()` supprime le transient → `numero()` reconstruit le fragment avec le nouveau numéro. **Dépublication** (passage en `draft`) → `save_post` → invalidation → retour **exact** au fragment initial. Déroulé conforme ; couvert par `b15-runtime.php` (`publication_change_numero`, `depublication_retour_exact_numero`).
4. **Numéro absent.** Si `Accueil::numero()` est `null`, la zone rend son titre « Le numéro en cours » et un contenu vide — structure saine, pas de défaut.

## 3. Tests

- **Suite PHP rejouée** avec la commande autorisée, sans argument :
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
  Conteneur jetable, `network=none`, dépôt monté en lecture seule. Dernière ligne :
  **`REJEU : 1209 tests, 36693 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`**
  (plus `OUTILS : 23 outils, 852 contrôles, 0 échecs` ; `PAQUETS : 13 vérifiés, 0 échecs`).
- Cas limites couverts par `b15-runtime.php` : cache construit/réutilisé/invalidé, anonyme = A-PAPIER (hors IDs natifs dédupliqués en banc), menu B-09 inchangé, publication puis dépublication. Couverture proportionnée et pertinente.
- Réserve (grille §3) : le test **PHPUnit** `PiedPageB15Test` ne vérifie que la constante `ZONES` (assertion tautologique qui recopie le code) et les deux filtres. Tout le comportement de `rendre()`, du cache et de l'échappement n'est éprouvé que par le script de démonstration `b15-runtime.php`, hors PHPUnit. Acceptable (le runtime est réellement exécuté), mais noté. Voir point mineur 3.

## 4. Sécurité et données

- Sorties échappées : `esc_url`, `esc_html`, `esc_attr`, `esc_html__`, `get_the_post_thumbnail` (`PiedPage.php:59-104`). Correct.
- Aucun secret, aucune donnée réelle ; démonstration fictive.
- **Paywall** : le pied ne porte que titre, couverture (miniature publique) et liens — rien de réservé. Aucune voie ne laisse sortir de texte réservé. Conforme §3 doctrine.
- **Étanchéité C-26** : aucun témoin de consentement, script ou cookie émis par le pied pour un anonyme ; vérifié par la preuve navigateur, sans étendre la matrice C-26.
- **Zéro appel sortant** : aucun `<form>`, `<iframe>`, `<script>`, aucune géolocalisation ; `network=none` à l'exécution. Conforme.

## 5. Doctrine

- Standard d'abord respecté et justifié (point 1). Logique du numéro réutilisée (`Accueil::numero()`), pas de duplication de règle.
- Conventions §5 : `declare(strict_types=1)`, namespace `Imagine\Site`, préfixe `imagine_` (`imagine_b15_numero`, action `imagine_pied_page`), i18n française via `__`/`esc_html__`. Aucune modif d'extension tierce. Conforme.

## Points mineurs (défaut proposé — décisions techniques)

Aucun bloquant, aucun important.

1. **Invalidation de cache trop large.** `PiedPage::register()` branche `invalider()` sur `save_post_attachment`, `added_post_meta`, `updated_post_meta`, `deleted_post_meta` **pour tout le site** (`PiedPage.php:16`). Chaque enregistrement de n'importe quel attachement ou métadonnée purge le transient du pied, d'où un renouvellement inutile. Sûr mais coûteux.
   *Défaut proposé* : garder tel quel (correction pure, sans risque) ; arbitrage ultérieur pour cibler le numéro courant si la charge le justifie.

2. **Résolution d'URL hétérogène.** `abonnement` passe par `get_page_by_path` et n'émet rien si la page n'est pas publiée ; `newsletter` et `point-vente` émettent des slugs en dur (`/nos-newsletters/`, `/points-de-vente/`) sans vérifier l'existence de la cible — lien mort possible si un slug change (`PiedPage.php:86-92`). Les slugs correspondent bien aux pages B-08/C-22 et B-10 aujourd'hui, et le brief ne demande qu'« un lien » ; aligné sur `Accueil.php:81` pour la newsletter.
   *Défaut proposé* : conserver (conforme au brief) ; aligner éventuellement sur `get_page_by_path` par cohérence avec `abonnement`.

3. **Test PHPUnit à faible valeur.** `PiedPageB15Test::testOrdreDesCinqZonesEstUtiliseParLeRendu` compare la constante `ZONES` à un littéral identique : il recopie le code sans éprouver `rendre()`. Le vrai comportement n'est couvert que par `b15-runtime.php`.
   *Défaut proposé* : laisser (le runtime couvre la règle) ; porter au besoin un cas de rendu dans la suite PHPUnit.

4. **Écart de comptage dans `A-VOIR.md`.** `A-VOIR.md` annonce « REJEU 1208 tests / 36685 assertions » ; mon rejeu frais donne **1209 / 36693** (PASS, écart expliqué au README l. 652 par un garde-fou B-14 ajouté après). Pas un défaut de code, simple décalage de rédaction.
   *Défaut proposé* : rafraîchir le chiffre dans `A-VOIR.md`.

## Verdict

**Conforme** — mineurs seulement.

- Bloquant : aucun.
- Important : aucun.
- Mineur : 1 (invalidation large), 2 (résolution d'URL hétérogène), 3 (test PHPUnit tautologique), 4 (comptage A-VOIR non rafraîchi).

Ce verdict n'est **pas** un GO. La validation visuelle du pied (habillage) reste du ressort de Ced (doctrine §6) ; aucune question visuelle ou touchant au réel n'est ouverte par cette relecture.
