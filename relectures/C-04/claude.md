# Relecture C-04 — File d'attente du connecteur (Claude, indépendant)

Date : 20/11/2026. Relecteur : Claude Code (NUC). Rôle : relecteur indépendant.
Périmètre lu : `briefs/C-04-file-connecteur.md`, `production/C-04/` (notes, PRET, preuves),
`wp/plugins/imagine-connecteur/` (src, tests, composer, README, examples), doctrine.
**`relectures/C-04/codex.md` n'a pas été ouvert.** Pas de fusion à ce stade.

> Avertissement d'exécution : Docker n'est pas installé sur la machine et l'exécution
> directe de PHP est refusée par le bac à sable. **Je n'ai pas pu relancer la suite
> moi-même.** J'ai donc : (a) vérifié à la main les empreintes SHA-256 des trois fichiers
> les plus lourds en logique (`Worker.php`, `Event.php`, `DailyCsvDestination.php`) —
> elles sont **identiques** à `production/C-04/tests/final.json`, donc les sources livrées
> sont bien celles qui ont été testées par Hermès ; (b) déroulé les cas à la main sur le
> code source. Le verdict s'appuie sur ces deux bases, pas sur une exécution de ma part.

---

## 1. Conformité

- **Le lot fait ce que demande le brief, sans surplus notable.** Les sept points « À
  implémenter » sont couverts : événement immuable + clé d'idempotence (`Event`),
  table des états et transitions fermées (`State`, `Entry`), règles nommées extensibles
  (`Validator`, `NamedRule`, `Rule`), rejeu plafonné à attente croissante (`RetryPolicy`,
  `Worker`), ordre par abonnement (`Worker::blocked`/`ordered`), les quatre interfaces +
  doubles (`QueueStorage`, `Destination`, `Clock`, `Alerts`, `InMemory*`, `FakeDestination`),
  export quotidien CSV dédupliqué (`DailyCsvDestination`).
- **Rattachement au cahier des charges.** Le brief cite §2.2, §2.4, §2.5, §4.5 et R-39/40/41.
  Les règles de `Validator::billing` appliquent §2.2 (identité, adresse, montants, paiement,
  n° entreprise). La file + idempotence applique §2.4/§2.5/§4.5. `notes.md` relie bien le
  tout. Bon point : les règles portent chacune un nom (`identity`, `address`, `amounts`,
  `payment_method`, `enterprise_number`), comme exigé.
- **Interprétations signalées (conforme à la doctrine §1).** Hermès déclare ses choix :
  `sourceId` d'un renouvellement = la commande de renouvellement (pas l'abonnement) ;
  email facultatif ; montants déjà en unité mineure ; n° entreprise bloqué si C-02 absent ;
  quarantaine terminale. Toutes sont écrites dans `notes.md`/`README.md`. Rien d'inventé
  sur les champs Odoo ou le format d'export, laissés à Step. **Conforme.**
- **Point mineur — champs ajoutés hors liste explicite du brief.** `payment_reference` et
  `enterprise_number` figurent dans la liste blanche de contenu et dans le CSV, sans que le
  brief les nomme dans ses règles. Ils sont plausibles (§2.2 « la commande ») et provisoires,
  mais à confirmer par Step pour éviter un schéma qui diverge du besoin réel. Aucun champ de
  personnalisation / préférence / réponse de formulaire n'est présent (§2.2 respecté, testé).
- **Point à signaler — parcours de réception R-39/40/41 non automatisés.** `notes.md` est
  honnête : ces cas restent « proposés, non automatisés comme parcours de réception et non
  déclarés validés ». C'est acceptable pour un **cœur** PHP pur, mais la doctrine §4 impose
  que les parcours de réception du chapitre 5 deviennent des tests de bout en bout. **Ces
  tests restent dus** au lot de branchement, avant tout « connecteur fini ». À tracer.

## 2. Exactitude métier (cas déroulés à la main)

- **Dépôt en double → une entrée.** `InMemoryQueue::add` renvoie `false` si la clé existe ;
  la clé n'inclut ni contenu, ni heure de réception, ni n° d'essai. Le second dépôt est
  ignoré. Correct (et testé, `EventTest::testDeterministic…`).
- **Envoyé puis rejoué → pas de 2ᵉ appel.** `replay()` refuse un état `Sent` (hors
  `[Pending, TemporaryFailure]`). Déroulé à la main : after `Sent`, `replay` retourne `false`
  sans toucher la destination. Correct (confirmé par `demo-result.json` : `replay_sent:false`).
- **Trois pannes puis reprise → part une fois.** Déroulé avec `maxAttempts=5`,
  `down,down,down,ok` : attempts 1→2→3 (échecs temporaires, `retryAt = now + 10/20/40`),
  puis 4ᵉ essai `ok` → `Sent`, `calls = 4`, `accepted = 1`. Cohérent avec le test.
  **Observation :** il faut `maxAttempts ≥ (nb de pannes + 1)` pour que l'événement reparte ;
  la démo règle `RetryPolicy(4,…)`, soit le strict minimum pour 3 pannes. Inhérent à toute
  limite de rejeu, mais à garder en tête au branchement (le paramètre doit couvrir la durée
  d'indisponibilité réelle d'Odoo, sinon exhaustion définitive).
- **Accusé perdu (late_ack).** La file rejoue la même clé ; la déduplication vit dans la
  **destination** (`FakeDestination` mémorise `events[key]`). Correct **à la condition**,
  bien documentée dans `notes.md`, que la destination réelle (Step) garantisse l'unicité
  atomique avec l'effet comptable et un accusé rejouable. Honnête : la file seule ne peut
  pas garantir « exactement une fois » après une réponse perdue.
- **Invalide → quarantaine, les suivants passent.** Déroulé : un événement à `total_minor`
  incohérent est mis en `Quarantine` avec `rule='amounts'` et message FR ; les autres
  abonnements/commandes continuent. Correct (testé).
- **Export relancé → fichier identique.** `exportPreviousDay` recompose le CSV depuis le
  journal durable et, si le fichier du jour existe déjà, **compare les octets** et refuse
  d'écrire ; divergence → `TemporaryFailure`. Déroulé confirmé par `demo` :
  `identical_after_rerun:true`. Correct.
- **Minuit et changement d'heure (Europe/Brussels).** Les calculs temporels passent par
  `DateTimeZone('Europe/Brussels')` et par epoch (`setTimestamp(getTimestamp()+n)`),
  **jamais** par « maintenant − 86 400 s ». La journée civile de la veille est calculée via
  `setTime(0,0)->modify('-1 day')`. Les cas printemps (29/03, jour de 23 h) et automne
  (25/10, 25 h) sont couverts par `ExportTest`. Déroulé du 29/03 : les quatre horodatages
  UTC retombent tous le 29/03 local, export « veille » correct. **Solide.**
- **Cas limite — contenu divergent pour une même clé.** Si l'adaptateur dépose deux fois la
  même `(type, sourceId)` avec un **contenu différent**, le premier gagne et le second est
  **silencieusement** ignoré (`add` → `false`, aucune alerte). C'est correct pour
  l'idempotence, mais une divergence de contenu peut masquer un bug amont sans trace.
  Mineur : envisager une alerte au branchement si un dépôt rejeté porte un contenu différent.

## 3. Tests

- **Non relancés par moi** (ni Docker, ni PHP autorisé). Preuves d'Hermès lues :
  `final.log` = `OK (22 tests, 161 assertions)`, `final.json` `exit_code:0`, lint PSR-12
  code 0, `composer validate --strict` code 0, non-régression C-01 `39 tests` OK.
  **Les empreintes SHA-256 de `Worker.php`, `Event.php`, `DailyCsvDestination.php` que j'ai
  recalculées correspondent à `final.json`** : les sources relues sont celles testées.
- **Couverture des cas limites — bonne.** Les tests vont au-delà du nominal : bail de
  traitement expiré (reprise après crash), événement futur en attente, délai qui démarre
  **après** l'échec (classe anonyme qui avance l'horloge pendant `send`), DST printemps/
  automne, journal corrompu → échec fermé, lien symbolique refusé sans altérer la sentinelle,
  CAS périmé refusé. C'est du test qui vérifie la **règle**, pas qui répète le code.
- **Réserve méthodologique.** La garantie « une seule écriture » du cas `late_ack` est
  vérifiée contre un **double maison** (`FakeDestination`) qui déduplique en mémoire. Le test
  prouve le contrat *attendu* de la destination, pas que la destination réelle le tiendra —
  ce que `notes.md` reconnaît. À transformer en test d'intégration le jour du branchement Step.
- **Manque mineur.** Pas de test direct sur `RetryPolicy::delay` au-delà du plafond
  (`maximumSeconds`) ni sur le refus de paramètres invalides (`factor < 2`, etc.). Le
  comportement est correct à la lecture, mais non couvert isolément.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle.** Jeux fictifs, noms inventés, emails `@example.org`.
  Conforme doctrine §3.
- **Fuite de données dans les erreurs — bien traitée.** `Worker` ne journalise jamais le
  texte brut d'une erreur de transport (`catch (Throwable)` → message générique) ; la liste
  blanche de `Event` refuse les champs hors facturation **sans recopier leur valeur** dans le
  message d'exception (testé : `assertStringNotContainsString('never transmit', …)`). Les
  alertes ne reçoivent que la clé + un code + un message sans charge utile. Bon.
- **Écriture de fichiers confinée.** `DailyCsvDestination` : `realpath` + `is_dir` +
  `is_writable` au départ ; `path()` refuse séparateurs, `..`, `\`, liens symboliques et
  cibles non régulières ; écriture atomique (fichier temporaire + `fsync` + `rename`) et
  verrou `flock` — tout reste dans le dossier passé en argument (exigence du brief respectée).
- **À signaler (important, format provisoire) — injection de formule CSV.** `csv()` écrit les
  champs texte (`name`, `street`, `city`, `payment_method`, …) sans neutraliser un préfixe
  `=`, `+`, `-`, `@`. En données réelles, un nom/adresse contrôlé par l'abonné du type
  `=HYPERLINK(...)` devient une **formule** à l'ouverture dans un tableur par un administrateur.
  Le code s'en remet à la consigne « importer comme texte » (README/notes), pas à une
  neutralisation. Le fichier vit dans un dossier privé et le format est provisoire (Step
  tranchera), donc ce n'est pas bloquant, mais **à corriger avant tout usage où un humain
  ouvre le CSV** : préfixer d'une apostrophe les cellules commençant par un méta-caractère,
  ou documenter l'import strict en texte comme une obligation, pas une recommandation.
- **Paywall / sortie de texte réservé :** sans objet pour ce lot (pas de contenu éditorial).

## 5. Doctrine

- **Conventions §5 :** PHP 8.2, `declare(strict_types=1)` partout, PSR-12 (lint vert),
  namespace `Imagine\Connecteur`, classes `readonly`/immuables, enums. Conforme.
- **Logique métier hors de WordPress (§4) :** respecté — cœur PHP pur, testable sans base ni
  WP, interfaces pour le branchement. C'est l'esprit même du brief. Bon.
- **Standard d'abord (§4) :** le cœur file/idempotence/quarantaine est du sur-mesure
  légitime (aucune extension retenue ne fait la file vers Odoo). `notes.md` rappelle que la
  couverture native des extensions (A-00) et le branchement WooCommerce/Odoo restent séparés.
  Pas de réinvention d'un standard existant visible. OK.
- **Point mineur — textes d'interface et traduction.** Doctrine §5 : « Textes de l'interface
  en français, passés par les fonctions de traduction. » Les messages de règles et d'alerte
  sont en français mais **codés en dur**, sans `__()`/i18n — justifié par Hermès (cœur sans
  WordPress). Interprétation raisonnable, mais la traçabilité i18n doit être réglée à la
  couche de branchement WP (ré-emballage par gettext), sinon ces messages admin ne seront
  pas traduisibles. À arbitrer : où et comment ces chaînes sont rendues traduisibles.

## 6. Études

Sans objet : lot avec code.

---

## Verdict : **Conforme** (à corriger sur un point de sécurité avant branchement)

Le cœur est sobre, immuable, bien testé et honnête sur ses limites. Aucun défaut de
correction bloquant trouvé à la lecture et au déroulé manuel. Les réserves portent sur la
sécurité du format provisoire et sur des manques de couverture, pas sur la logique métier.

**Points classés :**

- **Bloquant :** aucun.
- **Important :**
  1. *Injection de formule CSV* (`DailyCsvDestination::csv`, `src/DailyCsvDestination.php:139`)
     — neutraliser les cellules texte débutant par `= + - @`, ou traiter « import en texte »
     comme une obligation vérifiée, avant tout usage où un humain ouvre le fichier.
  2. *Parcours de réception R-39/40/41 non automatisés* — dus au lot de branchement avant de
     déclarer le connecteur « fini » (doctrine §4) ; à tracer dans `docs/ecarts.md`.
- **Mineur :**
  1. Dépôt d'une même clé avec contenu divergent : ignoré **sans alerte** (`InMemoryQueue::add`,
     `src/InMemoryQueue.php:12`) — envisager un signalement au branchement.
  2. `RetryPolicy::delay` et le refus des paramètres invalides ne sont pas couverts par un
     test isolé (`tests/WorkerTest.php`).
  3. Messages FR codés en dur sans i18n (cohérent avec un cœur hors WP, mais à ré-emballer au
     branchement) — doctrine §5.
  4. Champs `payment_reference` / `enterprise_number` présents sans être nommés par le brief :
     à confirmer par Step avec le schéma réel.

**À arbitrer par Ced (questions fermées, reprises/complétées depuis `notes.md`) :**

- Neutraliser l'injection de formule dans le CSV dès ce lot (préfixe apostrophe), oui/non ?
- Maintenir le blocage des événements suivants **du même abonnement** quand un antérieur est
  en quarantaine, jusqu'à reprise administrative auditée, oui/non ?
- Signaler (alerte) un dépôt rejeté pour clé déjà connue mais **contenu différent**, oui/non ?

> Rappel de rôle : ce verdict **n'est pas un GO**. `codex.md` existe ; la fusion dans
> `corrections/C-04.md` reste à faire dans une étape ultérieure, après croisement explicite.
