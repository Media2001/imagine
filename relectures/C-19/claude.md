# Relecture C-19 — Tableau de bord (Claude, relecteur indépendant)

Brief : `briefs/C-19-tableau-de-bord.md`. Cahier des charges : §3.13 (« Tableau de bord »).
Production relue : `wp/plugins/imagine-site/TableauBordAdmin.php`, `TableauBordNatives.php`, `TableauBordRegles.php`, `indicateurs/*.php` (actifs, echeances, echecs, mouvements), et les dépendances réemployées C15 (`EcheancesRegles.php`, `EcheancesNatives.php`, `EcheancesAdmin.php`) et C18 (`ExtractionsRegles.php`, `ExtractionsNatives.php`, `extractions/etat.php`, `MonCompteRegles.php`).
Je n'ai **pas** ouvert `relectures/C-19/codex.md`. Pas de fusion à ce stade.

## Suite de tests rejouée

Commande autorisée, sans argument : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
Dernière ligne :

```
REJEU : 1077 tests, 34327 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Image T01 : `sha256:88f1103078fc9cb74df3886b46be2f51c52eb3e9f11cac9a97def7afa3f12ca2`. Conteneur jetable, sans réseau, dépôt monté en lecture seule. Les 6 tests purs C19 (`TableauBordReglesTest`, 32 assertions) sont inclus dans ce total.

## 1. Conformité

- **Écran demandé présent.** `TableauBordAdmin::page()` affiche quatre indicateurs en tableaux natifs (`widefat striped`), sans graphique ni script, sous le menu Imagine existant (`add_submenu_page('imagine', …)`, `TableauBordAdmin.php:52-64`). Conforme au brief (« Des nombres dans un tableau simple »).
- **Les quatre indicateurs de départ sont là** : actifs total + par mode (`indicateurs/actifs.php`), échéances 30/90/180 (`echeances.php`), paiements échoués (`echecs.php`), entrées/sorties du mois civil UTC (`mouvements.php`). Correspond aux points 1 à 4 du brief.
- **Grisés « à venir ».** `TableauBordAdmin.php:95-105` liste exactement les six autres indicateurs du §3.13 (par tarif, rétention annuelle, non-renouvellements/motifs, conversion découverte, part solidaire/soutien, personas), chacun avec « ce qui manque » et aucun chiffre. Conforme à « Ne fabrique ni ces données ni leur formule ».
- **Aucune identité.** La sortie de `TableauBordNatives::lire()` ne retient que `etat` + `mode_paiement` (via `array_intersect_key`, `TableauBordNatives.php:18`) et des entiers de dates ; aucun nom, email ni identifiant ne traverse vers l'écran. Conforme à « l'écran ne montre que des nombres ».
- **Réemploi réel des règles C15/C18.** actifs passe par `ExtractionsRegles::selectionner('etat', …)` (la même sélection que C18) ; échéances et échecs passent par `EcheancesRegles::echeances()` / `::paiements()` (les mêmes fonctions que l'écran C15). Aucune règle « actif / échéance / échec » n'est réécrite. Conforme au cœur du brief.
- **Interprétations signalées.** Les phrases d'indicateur et l'`A-VOIR.md` déclarent explicitement : un/trois/six mois = fenêtres **30/90/180 jours** de C15 (pas des mois calendaires) ; actif = **ligne** d'abonnement (pas personne dédupliquée) ; entrées = création native (concept Woo *New Subscription*), pas date de début de calendrier ; sorties = *Ended* natif. Interprétations proches du texte et tracées — bon.

**Point de conformité à arbitrer (cahier vs brief).** Le §3.13 distingue « par **mode** de paiement » et « par **moyen** de paiement » (carte, Bancontact, virement, domiciliation…, cf. §4.2). Le brief a réduit cela à « par mode de paiement », et la répartition codée utilise le champ passerelle de C18 (`mode_paiement` = `EcheancesNatives::methode`, c.-à-d. en pratique le *moyen*). Résultat : un seul axe est fourni, sous le libellé « mode », et « par moyen de paiement » n'apparaît ni actif ni grisé. Ce n'est pas un défaut de code — c'est un écart cahier/brief à tracer (doctrine §7). Voir question « Pour Imagine ».

## 2. Exactitude métier (cas déroulés à la main)

**Cas A — échéances, parité avec C15.** Source : `TableauBordNatives.php:15` lit `EcheancesNatives::lire('echeances', 180)`, qui filtre les statuts `active/pending-cancel/on-hold/pending` puis applique `EcheancesRegles::echeances(rows, time(), 180)`. L'indicateur ré-applique `EcheancesRegles::echeances(…, 30|90|180)` (`echeances.php:12-14`). Le filtre est monotone en jours (un ensemble à 30 ⊆ 90 ⊆ 180), donc ré-filtrer l'ensemble à 180 au seuil 30 redonne l'ensemble à 30 : le nombre du tableau de bord à J jours **égale** celui de la vue C15 au même J. Vérifié de tête sur des bornes 0/30/31/90/91/180/181 : le test `testDueWindowsReuseC15BoundsAndStatuses` donne 2/4/6 et compare directement à `EcheancesRegles::echeances` — cohérent.

**Cas B — échecs, parité avec C15.** `EcheancesNatives::lire('echecs', …)` ignore le paramètre `days` et renvoie `EcheancesRegles::paiements($rows, 'echecs')` = commandes `failed`, non payées, sans date de paiement, liées au même titulaire (parent/renouvellement). L'indicateur compte ces lignes (`echecs.php:10`). Même code que la vue C15 → même nombre. `testFailedPaymentsReuseC15UnpaidSelection` confirme (1 sur 4 lignes, comparé à `EcheancesRegles::paiements`).

**Cas C — entrées/sorties, mois civil UTC.** `mouvements.php` : `start = premier jour du mois UTC à 00:00` via `DateTimeImmutable('@now')->modify('first day of this month')->setTime(0,0)`. `DateTimeImmutable('@…')` est toujours en UTC → correct. entrées = créations natives dans `[start, now]`, tous états ; sorties = `cancelled|expired` dont la fin native est dans la période ; dates absentes (0) et fins futures exclues. Déroulé manuel sur les 6 lignes de `testMonthCountsNativeDatesWithoutInventingTransitions` → `entrees=2, sorties=2`, et l'entrée `data` reste inchangée (lecture seule prouvée par `assertSame($saved, $data)`). Correct.

**Cas limite — création native ≠ début de calendrier.** `testEntryUsesNativeCreationAsStandardNewSubscriptionsNotScheduleStart` : une ligne créée ce mois mais dont le `debut` de calendrier est en 2025 est bien comptée en entrée ; une ligne créée en 2025 mais au début 2026 ne l'est pas. L'indicateur n'utilise que `creation`, pas `debut`. Conforme à l'interprétation déclarée.

**Cas limite — sources vides = vrais zéros.** `testEmptySourcesGiveRealZerosAndUnknownIndicatorIsRefused` : sources vides → tous les chiffres à 0 (pas d'absence masquée), et un id d'indicateur hors catalogue (`../secret`) lève `InvalidArgumentException` (pas de traversée de chemin). Bon. En rendu, une source qui lève (abonnement disparu, `TableauBordNatives.php:21`) est rattrapée par le `try/catch` de `page()` et affiche « Indicateurs indisponibles… Aucun nombre de remplacement » — une source absente ne devient jamais un zéro. Conforme.

**Observation de cohérence (mineure).** actifs filtre sur `MonCompte::etat === 'Actif'` (statut `active`/`pending-cancel` **et** fin > maintenant), tandis que sorties filtre sur le **statut natif brut** `cancelled|expired`. Un abonnement de statut natif `active` mais dont la date de fin est déjà passée est donc **ni** compté en actif (C18 le classe « Expiré ») **ni** compté en sortie. Choix documenté (sorties = *Ended* natif), mais il crée un angle mort : une « sortie par échéance atteinte sans bascule de statut » n'est pas comptée. À garder en tête pour la lecture croisée actifs/sorties.

## 3. Tests

- La suite rejouable passe (ligne REJEU ci-dessus). Les 6 tests purs C19 couvrent les quatre indicateurs, leurs cas limites (bornes de fenêtre, dates absentes, création vs début, états exclus) et l'invariance de l'entrée.
- **Les tests vérifient la règle, pas sa répétition** : échéances et échecs comparent leur résultat à un appel direct de `EcheancesRegles::echeances` / `::paiements` sur les mêmes lignes ; c'est la bonne façon de prouver la parité C15 sans recopier le calcul.
- **Limite de couverture à signaler.** La suite PHP rejouable ne couvre **que** les règles pures (`indicateurs/*`, `TableauBordRegles`). Le comportement d'`TableauBordAdmin` et `TableauBordNatives` — composition `map_meta_cap`, refus 403, POST 405, échappement des sorties, lecture seule de la base (hash avant/après) — n'est vérifié que par les vérificateurs Python de démo (`c19-verifier.py`, contrôles HTTP/Chromium), qui touchent le site vif. **Je ne peux pas les rejouer** (interdit : accès à un site). Ces garanties reposent donc sur les reçus d'Hermès (`final-V2.json`), non reproduits indépendamment par moi. À noter au dossier, sans que cela vaille GO.

## 4. Sécurité et données

- **Échappement.** Toutes les sorties passent par `esc_html` / `esc_attr` ; les nombres sont castés en chaîne puis échappés (`TableauBordAdmin.php:87`). Rien de dynamique non échappé. Bon.
- **Droits.** `autorise()` = `manage_options` OU méta-capacité `imagine_voir_tableau_bord`, résolue par `map_meta_cap` vers les **deux** droits sources C15/C18 (`TableauBordAdmin.php:33-35`). Révoquer une source ferme l'écran, même au référent. Aucun nouveau rôle, `add_cap`, option ni seed. Conforme à « réservé par un droit dédié » sans muter les profils C09.
- **Verbes.** GET/HEAD seulement ; POST d'un lecteur autorisé → 405 avec `Allow` ; non autorisé → 403 (`admin_init`, lignes 37-45, + `verifier()` dans `page()`). Lecture seule respectée.
- **Lecture seule / sortants.** `TableauBordNatives::lire()` n'appelle que des lectures Woo/WCS (`wcs_get_subscriptions`, `wcs_get_subscription`, `wc_get_orders`) et `get_option`. Aucune écriture SQL, aucun email, aucun HTTP, aucune tâche planifiée. En-têtes `nocache` + `Cache-Control: private, no-store`. Conforme.
- **Aucun secret, aucune donnée réelle.** Fichiers entièrement en démo fictive ; la détection `A-VIR`/`A-PAPIER` (`EcheancesNatives::fictif`) est verrouillée à `wp_get_environment_type() === 'local'` + `home_url()` démo + marqueurs natifs. Rien ne fuit hors démo.
- **Paywall.** Sans objet ici (écran d'admin, pas de contenu réservé visiteur) ; mais l'écran lui-même est bien fermé côté serveur avant rendu **et** avant menu.

## 5. Doctrine

- **Logique métier hors WordPress.** `TableauBordRegles` + `indicateurs/*.php` sont du PHP pur, testables sans base ni WP ; `TableauBordNatives` est la couche fine de branchement. Conforme §4 doctrine.
- **Standard d'abord.** Réemploi de C15/C18 au lieu de réécrire ; `map_meta_cap` natif pour composer la capacité ; `A-VOIR.md` cite les docs officielles WP/WCS (map_meta_cap, dates natives, rapports Subscriptions). Bon.
- **Conventions §5.** `declare(strict_types=1)`, namespace `Imagine\Site\`, préfixe `imagine_` pour la capacité et la page, textes français passés par `__()`. `README.md` documente la section C-19 (droit, verbes, découverte des indicateurs, portée lecture seule). Conforme.
- **« Un indicateur = un fichier » — partiel.** Le calcul et la phrase sont bien co-localisés dans `indicateurs/<id>.php`, découverts par `glob`. Mais les **libellés des clés de valeur** (Total, « Virement », « Mandat papier », « À un mois — 30 jours »…) sont codés dans un `match` de `TableauBordAdmin::page()` (lignes 81-86), hors du fichier indicateur. Ajouter un indicateur avec de nouvelles clés rend quand même l'écran (le `default` retombe sur la clé brute), mais un libellé propre oblige à toucher l'admin. La promesse du brief (« en ajouter un soit l'affaire d'un fichier ») est donc tenue pour le calcul/la phrase, pas pour l'étiquetage. Mineur.

## 6. Études

Sans objet : lot avec code.

## Verdict

**Conforme**, sous réserve des points ci-dessous et du fait que je n'ai pas pu rejouer moi-même les contrôles HTTP/droits (site vif interdit). Rappel doctrine : ce verdict **n'est pas un GO**, et la validation visuelle de Ced reste due.

**Bloquant** : aucun.

**Important :**
- *(I-1, écart cahier/brief)* « par moyen de paiement » du §3.13 n'est ni actif ni grisé ; seul un axe est fourni sous le libellé « mode ». À tracer dans `docs/ecarts.md` et à arbitrer (voir « Pour Imagine »).
- *(I-2, couverture)* Le cœur sensible (droits 403/405, `map_meta_cap`, échappement, invariance base) n'est pas dans la suite rejouable ; il dépend de vérificateurs de démo non reproductibles par le relecteur. À conserver au dossier de clôture.

**Mineur :**
- *(M-1)* Phrase placée une fois par indicateur (après le tableau), pas « sous chaque chiffre » : lecture raisonnable mais à confirmer côté atelier (les phrases sont de toute façon à discuter).
- *(M-2)* Cohérence actifs/sorties : une sortie « par date de fin atteinte » sans bascule de statut natif n'est pas comptée (choix *Ended* documenté).
- *(M-3)* Libellés de valeurs hors du fichier indicateur (`match` dans l'admin) — voir §5.
- *(M-4)* Inefficacités en lecture seule, sans impact fonctionnel : `TableauBordRegles::catalogue()` re-`glob`/re-`require` à chaque `calculer()` (≈5× glob, 20× require par rendu, car `require` et non `require_once`) ; `$definition` inutilisé dans `TableauBordNatives::lire()` ; `EcheancesNatives::lire('echecs', 30)` passe un `days` ignoré par la vue échecs.
- *(M-5)* Double application du filtre échéances (source à 180, puis indicateur à 30/90/180) avec deux appels `time()` distincts (t₁ dans `lire`, t₂ dans `maintenant`) : micro-écart possible sur une date à la seconde près, sans effet pratique sur les comptes ni sur la parité C15.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

- **D-1.** Co-localiser les libellés de clés dans chaque `indicateurs/<id>.php` (p. ex. une clé `libelles`) plutôt que dans le `match` de l'admin, pour tenir pleinement « un indicateur = un fichier ». *Défaut prudent :* laisser tel quel pour l'instant (le `default` évite toute régression d'affichage) ; refactor opportuniste au prochain indicateur ajouté.
- **D-2.** Nettoyer les inefficacités M-4 (mémoïser `catalogue()`, retirer `$definition` mort, retirer le `days` factice pour `echecs`). *Défaut prudent :* appliquer, c'est sans risque et purement lecture.

## Pour Imagine (réglage / métier)

- **Q-1 (métier, à tracer en écart).** Le §3.13 veut « abonnés actifs par **mode** de paiement » **et** « par **moyen** de paiement ». Le lot n'expose qu'un axe (la passerelle native, libellée « mode »). Faut-il (a) garder un seul axe et considérer qu'il couvre le besoin de démarrage, ou (b) ajouter « par moyen de paiement » en ligne grisée « à venir » tant que la distinction n'est pas arrêtée ? *Défaut prudent proposé :* (b) — ajouter une ligne grisée « Par moyen de paiement — distinction mode/moyen à arrêter à l'atelier », pour ne rien promettre de faux et refléter fidèlement le §3.13. À confirmer à l'atelier direction.

## Question visuelle / touchant au réel (pour Ced)

- Aucune au sens « réel » (aucun accès, base ou compte). La validation **visuelle** de l'écran (sobriété des tableaux, lisibilité des phrases, grisés) reste à faire par Ced via la capture `tableau-de-bord-referent.png` et le parcours e-abo décrit dans `A-VOIR.md` ; les phrases et libellés sont, de l'aveu même du lot, « à discuter à l'atelier ».

---
`codex.md` existe mais n'a pas été lu. Fusion non effectuée (étape 5 en attente de l'instruction).
