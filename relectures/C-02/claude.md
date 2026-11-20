# Relecture indépendante — Lot C-02 (numéro d'entreprise)

Relecteur : Claude, indépendant. Date : 20/11/2026.
Brief : `briefs/C-02-numero-entreprise.md`. Cas : R-06 (`docs/recette/cas.md`).
Périmètre lu : `wp/plugins/imagine-pilotage/src/Entreprise/`, `tests/Entreprise/`,
`production/C-02/`. `codex.md` non ouvert. Fusion non faite (consigne).

## 0. Méthode et limite d'exécution

- Je n'ai **pas** pu lancer les tests dans cette session : `php`, `docker` et
  `composer` sont refusés par les droits d'exécution ici. Je le signale (grille §3).
- J'ai donc : (a) dérouré la logique à la main, (b) recalculé la clé de contrôle
  sur des bases fictives, (c) relu les preuves fournies par Hermès
  (`production/C-02/tests/final.log`, `rapport.md`), (d) vérifié leur cohérence
  interne (comptes de tests et d'assertions).

## 1. Conformité

Le lot fait ce que demande le brief, sans recherche réseau. Points relevés :

- **Normalisation (brief §À implémenter 1)** : conforme.
  `NumeroEntreprise::depuisSaisie()` tolère `BE`/`be` en préfixe contigu, points,
  tirets, espaces Unicode (`\p{Zs}`), mélange de séparateurs, et complète un ancien
  format à neuf chiffres par un seul zéro initial. Sortie : dix chiffres (`normalise`)
  et affichage `0123.456.749` (`affichage()`). `src/Entreprise/NumeroEntreprise.php:14-57`.
- **Contrôle de cohérence (brief 2 ; §3.4)** : conforme.
  Dix chiffres, premier chiffre 0 ou 1, clé = `97 - (8 premiers mod 97)`.
  `NumeroEntreprise.php:35-41`.
- **Résultat explicite (brief 3)** : conforme sur le fond, avec un écart signalé.
  Le brief énumère les motifs « vide, mauvaise longueur, caractères interdits, clé
  de contrôle fausse ». Le code ajoute un cinquième motif `PremierChiffre`
  (`Motif.php:13`, `NumeroEntreprise.php:35`). Cet ajout est **nécessaire** : sans
  lui, un numéro comme `2234567825` (premier chiffre 2, clé juste) passerait le
  contrôle de clé et serait accepté, en violation de la règle 2. L'ajout est
  justifié et documenté (`notes.md`, §Interprétations, point 4). → point mineur de
  conformité : confirmer que ce motif granulaire supplémentaire convient (voir §À arbitrer).
- **Recherche de dénomination (brief 4 ; §3.4 « affiche la dénomination trouvée »)** :
  conforme à la consigne. Seule une interface `RechercheDenomination` et une
  implémentation vide `RechercheDenominationIndisponible` qui répond « non
  disponible » (jamais « inexistante »). Aucun appel réseau. Décision 8 laissée
  ouverte et renvoyée à Ced. `src/Entreprise/RechercheDenomination*.php`.
- **Interprétation signalée** : Hermès documente clairement ses choix dans
  `notes.md` (jeu de caractères admis, préfixe contigu, priorité des motifs,
  numéros étrangers hors lot, sources BCE/VIES non consultées). Conforme à la
  doctrine §1 (« j'ai compris X »).

## 2. Exactitude métier

Dérouulé à la main, deux cas + cas limites :

- **Cas valide (base fictive `01234567`)** : `(int)01234567 = 1234567`,
  `1234567 mod 97 = 48`, clé `= 97 − 48 = 49` → `0123456749`.
  `depuisSaisie('BE 0123.456.749')` → valide, `normalise = '0123456749'`,
  `affichage() = '0123.456.749'`. **Concorde** avec le code.
- **Clé fausse (R-06 « numéro mal formé refusé »)** : `depuisSaisie('0123456700')`
  → `CleIncorrecte`, message FR clair, `normalise` et `affichage()` à null. Correct.
- **Ancien format à neuf chiffres** : prépendre un `0` préserve la clé, car les huit
  premiers chiffres deviennent `0` + sept premiers, de même reste mod 97. Un numéro
  à neuf chiffres valide reste valide à dix. Mathématiquement correct ; bien couvert.
- **Premier chiffre 2 avec clé juste** : refusé par `PremierChiffre` (et non accepté).
  Correct, et c'est l'intérêt du contrôle de premier chiffre.
- **Cas limites de clé** : reste 0 → clé 97 (valide) ; les clés 00, 98, 99 ne sont
  jamais valides. Cohérent avec l'algorithme belge officiel.
- **Priorité des motifs** : caractères interdits (avant tout nettoyage) → vide →
  longueur → premier chiffre → clé. Vérifiée sur `0123A56749` (interdits, pas
  longueur), `BE` seul (vide), `B E…` (interdits). Cohérente.

Aucune divergence métier trouvée.

## 3. Tests

- **Exécution** : non relancée par moi (droits refusés, cf. §0). Preuves d'Hermès :
  `final.log` = 169 tests / 19 860 assertions, code 0 ; suite Entreprise 41 tests.
  **Cohérence vérifiée** : `formes` (10) + `invalides` (21) + 4 méthodes
  `NumeroEntrepriseTest` = 35 ; `RechercheDenominationTest` 2 + `denominationsInvalides`
  (4) = 6 ; total 41, conforme au rapport. Les 19 400 assertions de
  `testCouvreTousLesRestesEtToutesLesCles` (2 × 97 × 100) concordent.
- **Couverture du brief** : tous les cas exigés sont présents — valide dans chaque
  forme de saisie, clé fausse, neuf chiffres, onze chiffres, lettres, chaîne vide,
  premier chiffre 2. ✔
- **Qualité (grille §3)** : `testCouvreTousLesRestesEtToutesLesCles` utilise un
  **oracle indépendant** (divisions/soustractions successives), distinct du modulo
  de production → vérifie vraiment la règle, ne la répète pas. Bon.
- **Cas limites solides** : espaces insécables/fines, tabulation, saut de ligne,
  octet nul, chiffres Unicode pleine largeur, UTF-8 mal formé, préfixe coupé/répété/
  étranger, signe `+`, barre oblique. Large et pertinent.
- **Réserve mineure** : le format d'affichage `4.3.3` n'est épinglé par **aucune
  assertion littérale** ; le test (`NumeroEntrepriseTest.php:30,130`) reconstruit
  l'attendu avec la même formule `substr()` que la production. Un changement
  concordant du regroupement dans les deux endroits passerait inaperçu. Mineur.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Numéros de test **calculés** à partir de
  bases fictives ; `notes.md` précise qu'aucun registre n'est consulté et qu'une
  éventuelle coïncidence avec un numéro réel n'est pas affirmée. Conforme doctrine §3.
- Aucun appel réseau ; implémentation de recherche strictement vide. Conforme au brief.
- `normalise` et `affichage()` sont null après refus : pas de saisie partiellement
  nettoyée transmissible en comptabilité (`notes.md`). Bonne précaution côté Odoo.
- La saisie d'origine n'est ni conservée ni journalisée. Bon.
- Pas de sortie HTML ici (lib pure) ; l'échappement est renvoyé au futur adaptateur,
  explicitement (`notes.md`). Les motifs sont des identifiants stables, pas des
  messages techniques à exposer. Correct.

## 5. Doctrine

- Conventions §5 respectées : PHP 8.2, `declare(strict_types=1)`, espace de noms
  `Imagine\Pilotage\Entreprise`, messages en français, traduction **injectable**
  (`message(?callable $traduire)`) plutôt qu'un `__()` codé en dur — approprié pour
  une bibliothèque sans WordPress ; le futur adaptateur injectera
  `fn ($t) => __($t, 'imagine-pilotage')`. Conforme.
- Logique métier hors de WordPress (doctrine §4) : respectée.
- « Standard d'abord » (§4) : Hermès indique honnêtement n'avoir pas revérifié
  qu'une extension retenue couvre déjà cette normalisation, et renvoie à A-00 avant
  intégration. Le brief impose le sur-mesure en PHP pur, donc l'écrire est justifié ;
  la vérification du standard reste à faire avant branchement. Signalé, acceptable.
- Immutabilité : `readonly`, constructeur privé pour `NumeroEntreprise`,
  `ResultatRecherche` readonly. Vérifié par réflexion dans les tests. Bon.

## 6. Études (sources officielles du brief)

Le brief demande, dans `notes.md`, les sources officielles possibles avec adresses,
conditions et limites. Fourni : tableau BCE (SPF Économie, Public Search) et VIES,
avec adresses de documentation, et insistance explicite que ce sont des **pistes
non consultées, non vérifiées dans ce lot**. Aucune affirmation de coût/quota/SLA
n'est présentée comme établie. Conforme à la grille §6 (pas de source → « doute »
assumé). Numéros étrangers : traités comme hors lot, avec la liste de ce qu'il
faudrait pour les accepter. Conforme au brief.

## Verdict

**Conforme** (ce n'est pas un GO). Aucun point bloquant ni important. Points mineurs :

- **Mineur — tests non relancés par le relecteur** : droits `php`/`docker`/`composer`
  refusés dans cette session. Verdict de test fondé sur les preuves d'Hermès
  (cohérentes) et le déroulé manuel. À rejouer dans le runner jetable avant
  toute étape ultérieure.
- **Mineur — motif `PremierChiffre` hors liste du brief (item 3)** : ajout justifié
  et documenté, nécessaire à la règle 2. À confirmer par Ced (question fermée ci-dessous).
- **Mineur — format d'affichage non épinglé par une assertion littérale** : le test
  reconstruit l'attendu avec la formule de production. Suggestion (à Hermès) :
  ajouter une assertion sur la chaîne littérale `0123.456.749` pour une base donnée.
- **Mineur — validation de `ResultatRecherche`** : le rejet d'une dénomination vide
  **ou** mal encodée repose sur le même `preg_match` (retour `false` pour l'UTF-8
  invalide, `1` pour le vide). Ça fonctionne, mais conflue deux causes sous un seul
  message. `src/Entreprise/ResultatRecherche.php:14`. Cosmétique.

### À arbitrer par Ced (questions fermées)

1. **Décision 8** : conserve-t-on le seul contrôle de format local (état actuel),
   ou autorise-t-on un lot d'étude pour une recherche de dénomination en ligne
   (BCE/VIES) ? (Aucun service n'est activé tant que non tranché.)
2. Le motif distinct `PremierChiffre` (en plus des quatre motifs listés au brief)
   est-il accepté tel quel, ou faut-il le fondre dans « clé de contrôle fausse » ?

### Portée R-06

Couvert **au niveau bibliothèque** uniquement : numéro mal formé refusé avec
message clair, numéro valide accepté et normalisé, prêt à transmettre. Le parcours
complet (champ de commande WooCommerce, affichage, confirmation client,
transmission → Odoo) reste pour un lot ultérieur. Le catalogue de recette n'est ni
modifié ni automatisé. Conforme à ce qui était attendu de C-02.
