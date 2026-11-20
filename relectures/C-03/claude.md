# Relecture C-03 — Vérification des robots d'indexation (Claude, indépendant)

Lot : C · code sur mesure, PHP pur sans WordPress.
Brief : `briefs/C-03-verification-robots.md`. Cahier des charges : §3.9, §4.4 ; cas R-27 (R-26/R-28 en partie).
Sources relues : `wp/plugins/imagine-pilotage/src/Robots/`, `tests/Robots/`, `config/robots.php`, `production/C-03/` (notes, sources, PRET, preuves de `tests/`).
Je n'ai pas ouvert `relectures/C-03/codex.md`. Pas de fusion à ce stade.

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus.

- **Fonction de décision** (UA + IP → robot vérifié / motif de refus) : `Verificateur::verifier()` renvoie une `Decision` (`estVerifie()`, `robot`, `motif`). Conforme au point 1 du brief et au §4.4 (« agent utilisateur et résolution inverse… ou plages d'adresses publiées. Un agent utilisateur seul ne suffit pas »).
- **Deux méthodes par robot, configurables** : `Methode::Dns` (inverse + domaine autorisé + directe concordante) et `Methode::Plages` (CIDR). Conforme point 2 et §4.4.
- **Liste de robots hors du code de décision** : le moteur lit `Configuration->robots` ; aucune liste figée dans `Verificateur`. `config/robots.php` fournit Google/Bing en DNS, en citant les pages officielles. Conforme point 3.
- **DNS derrière interface injectée** : interface `Dns`, aucun appel réseau dans le moteur. Conforme point 4.
- **Cache derrière interface, deux durées** : interface `Cache`, `ttlPositif`/`ttlNegatif`. Conforme point 5.
- **Fermeture par défaut** : exception, délai dépassé, cache indisponible → jamais de positif. Conforme point 6 et §3.9/§4.4.

Interprétations faites — **toutes signalées** dans `notes.md`, donc recevables :
- Le brief dit « cache des décisions **par adresse IP** ». L'implémentation clé en fait sur **IP canonique + identité candidate + empreinte de la configuration + version de politique** (`Verificateur.php:45`). C'est plus strict que le texte et correctement justifié (`notes.md`, section « Cache ») : une clé sur l'IP seule transférerait une vérification Google à Bing ou à un navigateur. Interprétation plus sûre, à confirmer comme intentionnelle.
- Le domaine **nu** (`googlebot.com`) est refusé ; seuls les sous-domaines sont admis (`domaineAdmis`, suffixe `.googlebot.com`). Choix aligné sur la documentation Google, signalé.

Périmètre : R-27 est servi **au niveau bibliothèque** (décision d'identité). La recette HTTP R-27 (V-ROBOT reçoit le texte complet, V-FAUX l'extrait — `docs/recette/cas.md:157`) et R-26/R-28 (étanchéité page/REST/flux/oEmbed/recherche, cache) restent explicitement hors lot. Correctement borné et dit dans `notes.md`.

## 2. Exactitude métier

Deux cas du cahier des charges déroulés **à la main** sur le code (R-27, profils `docs/recette/profils.md`), config `google = DNS / googlebot.com`.

- **V-ROBOT — robot vérifié.** UA `Googlebot/2.1`, IP `192.0.2.1`, PTR `crawl-fictif.googlebot.com`, A `192.0.2.1`.
  Jeton `Googlebot` reconnu (1 candidat) → IP valide → canonique `192.0.2.1` → cache vide → `verifierDns` : inverse rend le PTR, nom valide se terminant par `.googlebot.com` → admis → directe rend `192.0.2.1`, `inet_pton` identique → `VerifieDns`.
  **Résultat : vérifié, robot `google`, motif `verifie_dns`.** Conforme (texte complet au robot).
- **V-FAUX — bon agent, mauvaise adresse.** Même UA/IP/PTR mais A `192.0.2.2`.
  Même chemin jusqu'à la directe ; `inet_pton(192.0.2.2) !== inet_pton(192.0.2.1)` → aucune correspondance, domaine admis mais adresse différente → `AdresseDifferente`.
  **Résultat : non vérifié, robot `null`.** Conforme (extrait au faux robot). Le PTR seul n'ouvre rien.

Cas limites déroulés à la main et vérifiés corrects :
- Nom qui *contient* le domaine sans s'y terminer : `googlebot.com.exemple.net` se termine par `.exemple.net` → `domaineAdmis` faux → pas de résolution directe → `DomaineRefuse`. Le point initial du suffixe (`'.' . domaine`) bloque aussi `evilgooglebot.com`. Correct, c'est le point sensible du §4.4.
- Bon UA, adresse quelconque sans PTR du bon domaine → `DomaineRefuse`, non vérifié (une seule résolution). Correct.
- Agent d'un robot absent → `AgentInconnu` **sans aucune résolution DNS** (`candidats === []` avant tout appel). Correct.
- Délai total dépassé : budget unique PTR + A/AAAA (`reste()` sur `delaiDnsMs`, non renouvelé entre inverse et directe) → `DelaiDepasse`, et la décision négative est mise en cache plus court (`ttlNegatif`). Correct, conforme au point de vigilance « doute profite au paywall ».
- IPv6 et formes équivalentes ramenées à la même clé par `inet_ntop(inet_pton())` ; IPv6 IPv4-mappée non transformée en IPv4 (comparaison binaire par famille dans `Plage`). Correct.

Je n'ai trouvé **aucune voie de faux positif** : un positif exige soit une FCrDNS complète (inverse sous domaine autorisé **puis** directe redonnant l'IP exacte — l'attaquant ne contrôle pas la zone directe de Google/Bing), soit une appartenance CIDR sur un instantané non expiré. La propriété de sécurité centrale du §3.9/§4.4 tient.

## 3. Tests

- **Je n'ai pas pu lancer la suite moi-même** dans cette session : l'exécution d'un binaire (docker/php/composer) exige une approbation interactive indisponible ici. Je m'appuie donc sur les preuves livrées et je le signale, comme l'exige la grille.
- Preuves relues : `production/C-03/tests/final.log` → `OK (128 tests, 300 assertions)` pour `composer test` (suites Numeros = C-01 et Robots = C-03) ; `artifact-verification.json` → PASS, C-01 39/101, **C-03 89/199**, C-04 22/161, total 150/461, « injected fake DNS only » ; `rapport.md` cohérent (PHP 8.2.36, PHPUnit 11.5.58, réseau détaché). Les décomptes concordent entre `rapport.md`, `final.log` et `artifact-verification.json`.
- Couverture des cas limites : forte, pas seulement le nominal. Agents trompeurs (`NotGooglebot`, `GooglebotFake`, `Googlebot-Image`) et agent ambigu, inverse falsifié, faux suffixes/URL/espaces/labels invalides, IPv6 et point DNS terminal, CIDR /0 /32 /127 /128 et IPv4-mappée, pannes inverse/directe, timeout explicite et tardif, budget non renouvelé, caches positif/négatif avec échéance exacte et absence de prolongation, recul d'horloge, panne lecture/écriture, séparation IP/robot/config, en-têtes serveur contradictoires ignorés.
- Les tests vérifient la **règle**, pas le code : ils assertent les motifs, le nombre d'appels DNS (preuve qu'aucune résolution superflue n'a lieu) et le nombre de lectures de cache. Démarche TDD avec reçus RED→GREEN conservés. Qualité élevée.
- Réserve mineure : les tests reposant sur l'`HorlogeFictive` partagée simulent le temps ; aucune latence d'un résolveur réel n'est mesurée — limite assumée (voir §5 ci-dessous).

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Plages de test en documentation (RFC 5737 `192.0.2.0/24`, `198.51.100.0/24`, `2001:db8::/32`), domaines `example.*`, emails absents. `config/robots.php` ne contient **aucun préfixe réel**. Conforme doctrine §3.
- Le moteur ne lit **jamais** `X-Forwarded-For`, `Forwarded` ni `REMOTE_ADDR` : l'IP est un argument. Un test fournit des en-têtes `$_SERVER` contradictoires et prouve qu'ils sont ignorés. `notes.md` explique pourquoi `X-Forwarded-For` ne vaut que derrière un répartiteur connu et liste le travail hébergeur (inventaire des proxies, verrouillage de l'origine, `set_real_ip_from`/`real_ip_recursive`, une seule IP normalisée). Conforme au point de vigilance du brief.
- Étanchéité paywall : hors lot ici (aucun contenu servi), mais la seule faille possible — un faux positif ouvrant le texte payant — est fermée (cf. §2). Le refus par défaut sur exception/délai/cache indisponible va dans le bon sens (le doute ferme).
- La bibliothèque n'écrit aucune IP en journal ; le hash de clé n'est pas présenté comme une anonymisation (dit dans `notes.md`). Correct.

## 5. Doctrine

- **Standard d'abord** : l'étude A-00 / la page Memberships (`W1`) est citée pour montrer que WooCommerce ne fournit pas de contrat de vérification FCrDNS/CIDR Google/Bing ; le sur-mesure se borne à cette lacune. Conforme doctrine §4.
- **Conventions §5** : PHP 8.2, `declare(strict_types=1)`, PSR-12 (lint vert dans les preuves), espace de noms `Imagine\Pilotage\Robots`, objets immuables, interfaces injectées. README mis à jour (appendice C-03). Conforme. *Réserve cosmétique : l'en-tête du README dit encore « lot C-01 » alors qu'il couvre désormais C-01→C-04.*
- **Logique métier hors WordPress** : respecté (aucune fonction WP, horloge et DNS injectés). Conforme.

## 6. Études

Non applicable : lot avec code. Volet documentaire limité aux sources citées, qui respectent la grille (chaque affirmation — domaines, méthodes, sources de plages — cite une page officielle avec URL et citation courte dans `sources-officielles.json` : Google `G1/G2`, Bing `B1`, nginx `N1`, PHP `P1/P2`, plus Applebot/DuckDuckBot/Yandex non activés). Daté du 20/11/2026. Les fichiers de plages réels ne sont pas téléchargés : dit et borné.

## Verdict

**Conforme** (rappel : un verdict n'est jamais un GO). Lot solide, sûr sur le point critique (pas de faux positif), honnête sur ses limites.

Points classés :

**Bloquant**
- Aucun.

**Important**
1. *(Vérification)* La suite n'a **pas été rejouée par le relecteur** dans cette session (exécution de binaire non approuvée). Le « passent » repose sur les preuves livrées (`final.log`, `artifact-verification.json`, `rapport.md`), cohérentes entre elles. À rejouer dans le conteneur autorisé avant toute conclusion ferme.
2. *(Garantie de délai, connue)* Le moteur transmet le temps restant au résolveur mais **ne peut pas interrompre** un adaptateur DNS qui ne rend pas la main (`notes.md`, « Délai » ; `P1/P2`). La promesse « résolution trop lente → non vérifié » ne vaut que si le futur adaptateur impose un délai dur. C'est explicitement hors lot, mais c'est le maillon à garantir à l'intégration, pas un acquis.

**Mineur**
1. Jeton d'agent : l'anticipation `[/\s;)]` (`Verificateur.php:26`) n'inclut ni `,` ni `(`. Sans effet sur les UA réels de Google/Bing (toujours `jeton/version`), mais un UA inhabituel `Jeton(...)` ou `Jeton,...` ne serait pas reconnu. À garder en tête si la liste s'élargit.
2. `serialize($this->configuration)` est recalculé à chaque appel pour la clé de cache (`Verificateur.php:45`). L'empreinte de configuration pourrait être pré-calculée une fois. Micro-optimisation, pas un défaut.
3. En-tête du `README.md` encore « (lot C-01) » alors que le fichier documente C-01→C-04. Cosmétique.

## À arbitrer par Ced (questions fermées)
1. Confirmez-vous les durées proposées **3 600 s / 60 s / 200 ms** (`config/robots.php`) ? Risque SEO à peser : un budget DNS total de **200 ms** pour PTR + directe, combiné au **cache négatif de 60 s** sur timeout, peut refuser un vrai Googlebot en cas de lenteur DNS passagère et lui servir l'extrait — perte d'indexation. Faut-il des valeurs plus tolérantes côté délai ?
2. Validez-vous que la clé de cache intègre l'identité du robot et l'empreinte de configuration (plus strict que « par IP » du brief), comme proposé ?
3. Le référenceur confirme-t-il **Googlebot et Bingbot seulement** à ce stade, sans agents Google spécialisés (Image/Video/Other) ni autres robots ?
4. Faut-il faire confirmer par l'hébergeur les répartiteurs de confiance et la restitution d'une IP unique normalisée **avant** tout branchement (prérequis de R-27/R-28 en recette) ?
