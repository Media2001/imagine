# Relecture C-12 — L'accès découverte, branché (Claude, relecteur indépendant)

Date : 2026-11-24. Relecteur : Claude, indépendant. Codex non lu, fusion non faite (consigne).

Rejeu de la suite PHP autorisée, commande sans argument :
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne rapportée :

> REJEU : 812 tests, 33434 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS

Portée réelle de ce rejeu : conteneur jetable, réseau coupé, dépôt en lecture seule. Il exécute les suites PHPUnit des **bibliothèques closes** `imagine-pilotage` (dont `Acces\DecouverteTest` 3/3 et `Acces\QuotaTest` 3/3, le moteur C06) et `imagine-connecteur`. Il **avertit** (sortie lignes 4-5) que `plugins/imagine-site` (le raccord C-12) et `themes/imagine` n'ont **aucun test PHPUnit** ; ils ne sont donc pas couverts par cette commande (voir §3).

---

## 1. Conformité

- **Ouverture** (brief « Ouverture » ; §3.9 « un compte vérifié ... ouvre un accès de découverte »). `Decouverte::ouvrir()` crée un état une seule fois, si `ouverture = premiere_lecture`, périmètre non vide et compte vérifié (`verifie()` : prénom, nom, email valide, drapeau `imagine_email_confirme = '1'`). Conforme. Le déclencheur exact reste un réglage par défaut fermé — conforme à la doctrine « règle ouverte = réglage ».
- **Décompte côté serveur attaché au compte** (brief). État en `wp_options` clé `imagine_decouverte_compte_<id>`, `autoload=off` (`Decouverte.php:90-96,131-156`). `INSERT IGNORE` à l'ouverture + compare-and-swap binaire au décompte (`:217-220`) : jamais d'UPSERT ni de recrédit concurrent. Conforme.
- **Droits prioritaires ne consomment jamais** (brief). `decider()` renvoie `$base` sans toucher au compteur dès que l'abonné/acheteur/équipe/robot vérifié a déjà le texte complet, ou si visiteur anonyme, contenu non-article, non réservé, ou à paraître (`Decouverte.php:181-190`). Vérifié : la découverte est un dernier recours. Conforme.
- **Pas de décompte pour robot / aperçu / REST / flux** (brief, §3.9 étanchéité). `preparer()` ne pose `self::$article` que pour une vraie lecture GET d'article singulier publié, hors admin/ajax/cron/CLI/REST/feed/preview/embed/trackback/404, hors UA de robot ou vide, hors prefetch/prerender (`Decouverte.php:31-61`). Sans `self::$article`, `concerne()` est faux et le moteur est appelé sans découverte. Conforme.
- **Épuisement** (brief). Moteur C06 renvoie `Motif::DecouverteEpuisee` + `Bloc::DecouverteEpuisee` ; le thème rend l'extrait puis `parts/paywall-decouverte_epuisee.php` (« Votre accès découverte est épuisé »). Conforme.
- **Réglages dans l'écran C-10 avec mention** (brief). `DecouverteReglages::champs()` ajoute 5 champs (ouverture, forme, jours, nombre, périmètre) dans la section **Accès**, chacun marqué **« À confirmer par Imagine »** (`DecouverteReglages.php:80-111`). Enveloppe le rendu C-10 par hooks, sans modifier la bibliothèque close. Conforme.
- **Pas de contournement simple** (brief). État attaché au compte : vider les cookies rend anonyme sans rendre de crédit ; une autre session lit le même état ; rappeler l'adresse en boucle sur le même article ne réappend pas (`seen`). Les tests HTTP `sessions_cookies_boucle_sans_recredit`, `cookies_vides_restent_anonymes`, `epuise_nouvelle_session_et_boucle` couvrent ces cas. Multi-adresses / unicité par personne : signalé hors périmètre dans A-VOIR. Conforme.
- **Vérification email** (brief). Drapeau fictif `imagine_email_confirme`, posé par le script des profils ; aucun email ni parcours réel revendiqué. Dit explicitement dans A-VOIR et le RAPPORT. Conforme.
- **Mise à jour des profils V-DEC / V-DEC-FIN dans le script C-09** (brief). `c09-seed.php:176-178` appelle `c12-profils.php` quand la ligne porte `decouverte: 'C12'` ; les deux profils sont décrits dans `c09-profils.json:5-6`. Conforme.

**Interprétation non signalée comme question (voir §2, point important).** Le choix « relecture fermée après quota épuisé » engage un droit d'accès ; il est appliqué et documenté, mais n'est pas posé en question fermée à Ced/Imagine.

## 2. Exactitude métier (cas déroulés à la main)

Réglage : `premiere_lecture`, forme `articles`, `nombre = 2`, périmètre = numéro N. Compte vérifié V-DEC.

- **Cas A — première lecture admissible.** Lecture de l'article 1 (réservé, numéro N, sorti). `preparer()` pose `$article`, `decider()` : `base` fermé, `ouvrir()` crée l'état (`articles=[]`), `seen=false`, règle `consommes 0 < 2` → complet, append → `articles=[A1]`. Compteur « 1/2 ». **Conforme.**
- **Cas B — relecture du même article sous quota.** Recharge de l'article 1 : `seen=true`, `consommes 1 < 2` → complet, pas d'append. Reste « 1/2 ». **Conforme** (le code `template_redirect` reconsomme-t-il ? non : `seen` empêche l'append, et le compare-and-swap relit l'état frais).
- **Cas C — épuisement sur article neuf.** Après `articles=[A1,A2]`, lecture de l'article 3 : `consommes 2 < 2` faux → `DecouverteEpuisee`, bloc épuisé, pas d'append. **Conforme.**
- **Cas limite D — forme « durée », fin UTC exclue.** `DureeDecouverte` : `instant − début < secondes`. À `+86399 s` complet, à `+86400 s` épuisé (test `duree_fin_exclue_moteur`). **Conforme** à « fin UTC exclue ».
- **Cas limite E — robot vérifié.** `base` complet via `RobotVerifie` avant toute découverte → aucun état écrit (`robot_verifie_contrat_sans_compteur`). **Conforme.**
- **Cas limite F — périmètre courant.** La porte `decider()` lit le périmètre **courant** (`Decouverte.php:188`) tandis que la règle utilise le périmètre **figé** à l'ouverture (`:206-207`). Un numéro retiré du courant ferme l'accès ; un numéro ajouté au courant mais absent du figé reste `HorsPerimetre`. **Conforme** à « le courant peut retirer, pas élargir ».

**Point important — relecture d'un article déjà ouvert après épuisement du quota (forme « nombre »).**
`decider()` passe `consommes = count($state['articles'])` au moteur (`Decouverte.php:202-203`), et la règle C06 décide `consommes < maximum` (`NombreArticlesDecouverte.php:23`). Pour un article **déjà ouvert** (`seen=true`), son identifiant est déjà dans `articles`, donc `consommes` l'inclut. Conséquence : une fois le quota atteint (`articles=[A1,A2]`, `nombre=2`), **recharger A1 ou A2 renvoie « découverte épuisée »**, pas le texte déjà débloqué. C'est assumé : test `relecture_apres_quota_fermee_sans_credit` (`c12-runtime.php:53`), profil V-DEC-FIN (`c09-profils.json:6`), et A-VOIR.md:10 (« Une relecture après épuisement est également fermée, conformément au moteur C06 »).

Observations :
1. Le brief dit « un article déjà ouvert en découverte **ne recompte pas** ». La lettre (ne pas reconsommer de crédit) est respectée : aucun ré-append. Mais l'**accès** à un article déjà ouvert n'est plus rendu une fois le quota atteint, ce qui se lit mal au regard de la promesse « déjà ouvert ».
2. L'attribution « conformément au moteur C06 » (A-VOIR.md:10) est imprécise : le moteur applique `consommes < maximum` ; c'est le **raccord** qui fixe `consommes = count(articles)` plutôt que, pour un article déjà vu, le rang de cet article. Fermer ou non la relecture après quota est donc un choix du raccord, pas une contrainte de C06.
3. Pour la forme **« durée »**, fermer après expiration est juste par nature — la remarque ne vise que la forme **« nombre »**.
4. Ce choix engage un **droit d'accès** : la doctrine §1 impose alors de ne pas trancher seul mais de poser la question (« À arbitrer par Ced »). Le défaut retenu (fermé) est cohérent avec « dans le doute, fermé » ; il manque seulement la question explicite. → §Verdict + À arbitrer.

## 3. Tests

- **Suite autorisée rejouée** : voir ligne REJEU ci-dessus — 812/0/0, vert. Elle valide le **moteur C06** (règles découverte nombre/durée, périmètre, début, non-régression des droits indépendants) de façon indépendante et rejouable.
- **Limite de couverture (important).** Le raccord C-12 (`imagine-site` : `Decouverte.php`, `DecouverteReglages.php`, `Paywall.php`) n'a **aucun test PHPUnit** (avertissement du rejeu). Ses tests — `wp/tests/demo/c12-runtime.php`, `c12-http.py`, `test_c12_profiles.py` — s'exécutent **uniquement contre la démo en ligne** `http://192.168.129.32:8085` via WP-CLI/HTTP. Dépôt en lecture seule et réseau coupé : **je n'ai pas pu les rejouer**. Les chiffres « 25 PHP / 75 HTTP / 28 C11 / 33 unitaires » du RAPPORT ne sont donc pas vérifiés par moi ; je n'atteste que les 812 tests des bibliothèques closes et le déroulé manuel du §2.
- **Contenu des tests du raccord (relu, non exécuté)** : les cas du brief sont présents — ouverture, décompte, relecture idempotente, épuisement, contournement (sessions/cookies/boucle), durée, changement de réglage sans recrédit, hors-périmètre, état corrompu jamais réinitialisé, persistance refusée. Bonne couverture des cas limites ; les assertions vérifient l'état persistant, pas seulement la sortie. Réserve : le test `relecture_apres_quota_fermee_sans_credit` **fige** l'interprétation discutée au §2 ; il valide le code mais pas la règle métier tant qu'elle n'est pas arbitrée.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. État anonyme (identifiants numériques), noms fictifs, emails `@example.org`, cible démo uniquement. Les scripts refusent toute cible autre que `imagine-test-demo` / `192.168.129.32:8085`.
- Paywall : la découverte ne grante que via une décision `complet` légitime ; le compteur n'ajoute qu'un `<p>` de texte neutre, jamais de corps réservé. Les sorties réservées (REST, flux, oEmbed, recherche, aperçus de partage, en-têtes de cache) restent gérées par `Paywall` sans régression introduite par C-12. Le corps complet n'est reservé qu'après `decision()['complet']` dans `imagine_article_body()`.
- Capacité/nonce de l'écran C-10 réutilisés tels quels (enveloppe du rendu, pas de nouveau formulaire). Le journal d'audit est écrit **avant** de confirmer la modification ; si l'audit échoue, le réglage est annulé (`DecouverteReglages.php:114-137`, tests `audit_panne_annule_*`). Échappement systématique (`esc_attr`/`esc_html`/`selected`). Conforme.
- Validation stricte des réglages et de l'état : `valide()` / `etatValide()` refusent tout format inattendu ; un état corrompu n'est jamais réinitialisé (prudent). Conforme.

## 5. Doctrine

- **Standard d'abord.** Réutilise le moteur C06, les adhésions/restrictions Memberships, la Settings API native (`options.php`), `template_redirect`. Le stockage sur mesure se limite à l'ouverture et au compteur, que rien de natif ne couvre. Sources officielles citées dans A-VOIR. Conforme.
- **Bibliothèques closes inchangées.** C-12 n'ajoute que des hooks et l'enveloppe de rendu C-10 ; aucun fichier `imagine-pilotage` modifié. Conforme.
- **Conventions §5.** PHP 8.2, `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_`, textes traduits. Conforme.
- **Règle ouverte = réglage, défaut prudent fermé.** Respecté pour le déclencheur/forme/durée/nombre/périmètre.
- **Rejouable / non-régression.** Satisfait pour le **moteur** (rejeu autorisé vert). **Partiellement** pour le **raccord** : sa seule voie de test est la démo en ligne, non rejouable dans le conteneur isolé — cf. §3.
- **Tracer les écarts.** L'interprétation « relecture fermée après quota » touche une règle métier non tranchée ; à reporter dans `docs/ecarts.md` lors de la clôture (hors de mon périmètre d'écriture ici).

## 6. Études

Sans objet (lot avec code).

---

## Verdict : À corriger

Le code est solide, prudent et bien testé là où il peut l'être ; le moteur C06 est vérifié et rejouable. Rien de bloquant. Deux points justifient « à corriger » avant clôture.

**Bloquant**
- Aucun.

**Important**
1. **Relecture d'un article déjà ouvert fermée après épuisement du quota (forme « nombre »).** Le raccord fixe `consommes = count(articles)` (`Decouverte.php:202-203`), si bien que recharger A1/A2 après quota renvoie « épuisée » (`c12-runtime.php:53`, A-VOIR.md:10). Ce choix engage un droit d'accès : la doctrine §1 impose de le poser en question fermée, pas seulement de le documenter. Soit on confirme la règle (et on le dit comme arbitrage, pas comme contrainte C06), soit on garde l'accès aux articles déjà ouverts (passer au moteur le rang de l'article vu plutôt que le total). → question à Ced ci-dessous.
2. **Tests du raccord C-12 non rejouables par la commande autorisée.** `rejouer.ps1` ne couvre que les bibliothèques closes ; `imagine-site` n'a aucun test PHPUnit (avertissement du rejeu). Les 161 contrôles annoncés dépendent de la démo en ligne et n'ont pas pu être vérifiés indépendamment. Ajouter une couche de tests PHPUnit (ou harnais rejouable hors réseau) sur la logique du raccord renforcerait le « rejouable » de la doctrine.

**Mineur**
3. **A-VOIR.md:10 — attribution imprécise.** « conformément au moteur C06 » : la fermeture de la relecture après quota est un choix du raccord, pas une contrainte du moteur. Reformuler pour ne pas masquer l'arbitrage.
4. **A-VOIR / démo — parcours soigneusement non-collisionnant.** La démonstration ne recharge jamais un article après le quota (seule la forme nominale est montrée) ; un lecteur pressé n'y verra pas le point 1. Mentionner ce cas dans A-VOIR éviterait une surprise.

## À arbitrer par Ced

1. **Après épuisement du quota « nombre d'articles », un article déjà ouvert en découverte doit-il rester lisible (texte complet) ou se refermer sur le bloc « épuisée » ?** Le lot a retenu « se refermer » (défaut prudent, fermé). Confirmez-vous ce choix, à faire remonter à Imagine ?
