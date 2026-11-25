# Vérification B-04 — 2e tour (après fusion `corrections/B-04.md`)

Rôle : vérificateur, dernier tour. Base de comparaison : état relu `7a75199`
(synchro 22:13, dernière avant les relectures de 23:00–23:07). Diff lu sur
`wp/` et `production/B-04` jusqu'à `HEAD` (`59faebd`). Pas de nouvelle relecture
complète : contrôle des seules corrections demandées, des tests et des régressions.

## 1. Instructions de `corrections/B-04.md`, une par une

**1 — I1 : découverte visible dans les listes sans la consommer. → Appliquée.**
- `Paywall.php:57-64` : nouvelle `decisionListe()` → `evaluer($post, true)`.
- `Paywall.php:84-88` : en mode liste, la branche passe toujours par
  `Decouverte::decider(..., !$liste)`, soit `$consommer = false`.
- `Decouverte.php:196-219` (signature `decider(..., bool $consommer = true)`,
  `Decouverte.php:214-219`) : en non-consommant, état figé (`etat($id)` ou défaut),
  ni `ouvrir()` ni CAS ; `Decouverte.php:250` retourne la décision sans écrire.
- Clé de cache dédoublée `:liste`/`:lecture` (`Paywall.php:73`) : pas de collision
  avec la lecture réelle.
- Le thème consomme la prévision : `catalogue.php:60-61` et
  `single-imagine_numero.php:19-20` appellent `decisionListe()`. Tout le calcul de
  droit reste hors du thème.

**2 — I2 : séparer possession et lecture du PDF. → Appliquée.**
- `Paywall.php:116-157` : `couvreNumero()` → `evaluerNumero($issue, true)`, qui évalue
  le moteur à `max($now, $release)` (`Paywall.php:145`) : un numéro publié à date
  future n'écrase plus la possession déjà acquise.
- `single-imagine_numero.php:26` : le bouton d'achat est piloté par
  `couvreNumero()` (possession), plus par la décision PDF.
- `single-imagine_numero.php:29-30` : la lecture du PDF reste gouvernée par
  `decisionPdf()['complet']` (instant réel) → C-06/C-11 restent seuls juges.
  Vérifié par `CatalogueTest::testOwnershipDoesNotBecomeAnotherPurchaseBeforeRelease`
  (acheteur avant sortie : `possede=true`, `pdf.complet=false`,
  motif `contenu_futur_ferme_par_reglage`).

**3 — Paquet PHPUnit rejouable. → Appliquée.**
- `wp/plugins/imagine-site/phpunit.b04.xml` + `tests/CatalogueStatusTest.php` :
  `imagine_access_status()` seule, les 4 codes/libellés **et les deux motifs
  découverte** (`decouverte_duree`, `decouverte_articles`), en process isolé sans
  WordPress (`tests/b04-status-fixture.php`).
- `tests/CatalogueTest.php` : les deux conditions achat/PDF corrigées
  (`b04-adapter-fixture.php`), I1 et I2 compris.

**4 — Renforcer la recette HTTP. → Appliquée.**
- (a) marqueur privé non vide exigé par article témoin :
  `b04-http.py:46-55` (`require_private_markers`), appelé avant tout
  (`b04-http.py:63`) ; régressions dédiées `test_b04_http_contract.py` (vide,
  blanc, `None`, `0`, catalogue/numéro vide). Corrige M1.
- (b) possession vérifiée indépendamment du PDF : `b04-http.py:40-41` dérive
  `owned` de `AchatsNumeros::droits()`, et l'assertion devient
  `achat_selon_possession` (`b04-http.py:93`), plus `not expected['pdf']`.
- Visiteur « découverte » et acheteur « numéro à date future » : couverts par la
  recette native/HTTP de staging d'Hermès (checks `numero:*:decouverte_visible`,
  `futur:acheteur:*`, `futur:anonyme:*` dans `native-http-corrections-parent.json`)
  **et** par le paquet rejouable `CatalogueTest`. Le script versionné `b04-http.py`
  conserve ses trois profils anonyme/a-carte/p-numero : les deux nouveaux cas sont
  portés par les tests rejouables, ce qui est plus solide que le staging.
  → Appliquée (placement différent de la lettre, intention couverte).

**5 — Sortir l'échafaudage de démo du thème. → Appliquée.**
- `imagine_demo_product_preview` et son `add_filter` retirés de `catalogue.php`
  (ancien `inc/catalogue.php:48-63`).
- Relogé dans `wp/outils/demo/b04-preview.php` (hors thème).
- Grep sur `wp/themes/imagine/` : **aucune** trace de `192.168.129.32`,
  `imagine_demo_site`, `imagine-test-demo`, `woocommerce_coming_soon_exclude`,
  `_imagine_b04_fixture`. `CatalogueStatusTest` asserte même `hooks === []`.

**6 — Retirer « Dans le numéro : <ce numéro> » sur la page numéro. → Appliquée.**
- `catalogue.php:49` : paramètre `bool $showIssue = true` ; `catalogue.php:81`
  n'interroge le numéro que si `$showIssue`.
- `single-imagine_numero.php:52` passe `false`. Redondance supprimée sur la page
  numéro, conservée ailleurs.

**7 — (Conditionnel) retirer le statut d'accès du kiosque. → Non appliquée, à juste titre.**
- `archive-imagine_numero.php` **inchangé** : l'instruction était conditionnée à
  l'arbitrage de Ced (point 5 de la fusion, visuel). Hermès laisse l'existant en
  attendant la décision. Conforme à la consigne.

## 2. Résultat des tests

Je n'ai **pas pu réexécuter** moi-même la suite complète sur ce poste :
`php` est bloqué par la couche de permissions, et le harnais Python échoue à
l'import (`html5lib` absent — dépendance de conteneur, pas un défaut de code).
J'ai donc contrôlé les preuves committées d'Hermès **et vérifié qu'elles
correspondent trait pour trait au code corrigé committé** (noms de tests, nombres).

- PHPUnit B-04 (`junit-b04-parent.xml`, `phpunit-b04-parent.log`) : **OK, 4 tests,
  91 assertions, 0 échec**. Les 4 cas = exactement `CatalogueTest`
  (`testOwnership…`, `testListingPredictsFirstRead…`,
  `testListingUsesDurationAndCloses…`) + `CatalogueStatusTest`. Concordance confirmée.
- PHPUnit racine (`phpunit-root-parent.log`) : **OK, 70 tests, 467 assertions** →
  pas de régression inter-lots.
- Recette native/HTTP finale (`native-http-corrections-parent.json`) : **32/32
  checks à vrai, 0 échec**, dont I1 (`decouverte_visible`, `sans_ouverture_ni_quota`),
  I2 (`futur:acheteur:achat_independant_du_PDF`, `futur:acheteur:PDF_ferme`),
  étanchéité (`*:sans_corps`, `private_marker_nonempty`), redondance
  (`sommaire_sans_redondance`). `created_order_or_payment: false` (aucun paiement réel).
- Contrôle statique indépendant de ma part : la logique `max($now,$release)` (I2) et
  le chemin non-consommant (I1) tiennent, y compris le principe prudent « dans le
  doute, fermer » (`CatalogueTest::testListingUsesDurationAndCloses…`).

## 3. Régressions / modifications non demandées

- **Aucune régression fonctionnelle** détectée dans le périmètre B-04. Le chemin de
  lecture réelle (`Paywall::decision()` → `$consommer = true`) et `Decouverte::compteur`
  sont inchangés dans leur comportement.
- **Reformatage PSR-12** (passage des conditions `if (` sur plusieurs lignes) dans
  `Paywall.php` et `Decouverte.php` : non strictement demandé par la fusion, mais
  issu de la passe phpcs du lot, **whitespace only** et sans effet fonctionnel.
  Signalé, sans réserve.
- Les autres fichiers du diff (`CommandeAdmin/Native/Regles`, `a10…a13`, `c16`, etc.)
  relèvent d'**autres lots** menés en parallèle, hors B-04 ; non imputables ici. La
  suite racine reste verte.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les instructions techniques 1 à 6 sont appliquées et correctement couvertes par des
tests rejouables (PHPUnit B-04 vert) ; les preuves de staging d'Hermès sont toutes au
vert et cohérentes avec le code committé ; aucune régression ni fuite. Le seul point
en suspens — le statut d'accès sur le kiosque (instruction 7) — n'est pas un problème
de fond restant : c'est l'arbitrage **visuel** explicitement réservé à Ced (fusion §5,
défaut proposé : le retirer). Rien à renvoyer à Hermès.

**Rappel doctrine :** ce verdict n'est pas un GO (§3/§6). La clôture appartient à Ced,
qui doit trancher la question kiosque ; sa réponse « retirer » déclencherait
l'instruction 7 conditionnelle.
