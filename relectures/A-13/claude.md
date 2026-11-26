# Relecture A-13 — Contrôle d'un export d'abonnés hors ligne (Claude)

Lot : A-13. Brief : `briefs/A-13-controle-export-hors-ligne.md`.
Production : `wp/outils/bascule/controler-export`, `wp/outils/bascule/a13/`,
`wp/tests/a13/`, `wp/tests/fixtures/a13-export-*-fictif.csv`, `production/A-13/`.
Cahier des charges : §4.3 (« Abonnés hors ligne », « Abonnés sans email »), §2.3, §3.13.

Relecture indépendante. Je n'ai pas ouvert `relectures/A-13/codex.md`. Pas de fusion.

## 1. Conformité

Le périmètre du brief est couvert, sans débordement.

- Outil autonome, Python pur, sans WordPress, sans import, sans réseau : `controler-export:1-13`.
  Il lit un fichier et dit ce qui ne va pas ; il ne crée ni compte ni abonnement. Conforme §4.3.
- Entrées : un CSV + un fichier de correspondance (`--correspondance`), `controler-export:280-282`.
  La correspondance est une configuration, pas du code ; exemple livré
  `wp/outils/bascule/a13/correspondance.exemple.json` sur les champs nommés par le CDC
  (contact, type d'abonnement, numéros dus, échéance, coopérateur, mode de paiement, mandat).
- Aucun IBAN : préflight `preflight_iban` (`controler-export:23-31`) par nom de colonne et par
  contenu, exécuté **avant** toute analyse et toute écriture ; il nomme la colonne et ne recopie
  aucune valeur. Couvre aussi le CSV cassé (`preflight_format_invalide:136-139`). Conforme.
- Contrôles par ligne (`analyser:200-241`) : obligatoires absents, date illisible/passée, numéros
  illisibles/négatifs, adresse postale incomplète, email mal formé, mode de paiement hors liste,
  mandat papier sans référence. Tous présents.
- Contrôles d'ensemble (`analyser:242-252`) : doublon email, doublon nom+adresse postale normalisés,
  référence de mandat en double ; **tous** les membres d'un doublon sont signalés.
- Lignes sans email : comptées à part, jamais rejetées pour ce motif (`analyser:224-225`) ;
  aucune adresse inventée. Conforme §4.3/§3.13.
- Encodage et séparateur détectés ou déclarés, jamais devinés en silence : `decoder:105-118`
  (refus d'un repli silencieux sur un encodage ancien), `lire_csv:142-176` (auto exige un seul
  candidat cohérent, sinon refus). Conforme.
- Sorties écrites à côté du fichier et **jamais dans le dépôt** : `ecrire:34-39` (refus si le
  chemin résolu tombe dans le dépôt, y compris par lien symbolique ; refus d'écraser une sortie).
- Fichier des rejets : `ligne;motif` en français, **sans aucune donnée de la ligne**
  (`controler:270-274`). Les motifs ne portent que des libellés fixes ou un nom de champ *logique*
  (`'Champ obligatoire absent : ' + field`), jamais une valeur de cellule ni un en-tête du CSV.
- Code de retour non nul s'il y a des rejets (`controler:275` → 1) ; refus → 2 (`main:286-291`).
- Aucune règle métier nouvelle : le filtre `types_abonnement_autorises` est désactivé par défaut
  (`[]`) et signalé (`controler-export.md:59-61`). L'échéance passée est signalée, pas une décision
  d'import. Conforme à « l'outil ne décide pas ».

Interprétations signalées (doctrine §1) : « adresse complète = rue + code postal + ville + pays »,
« date passée = avant la date locale » et « email = syntaxe ASCII, pas de délivrabilité » sont
écrites dans `controler-export.md`. Une seule mérite un arbitrage métier (voir § Pour Imagine).

## 2. Exactitude métier — deux cas déroulés à la main

**Cas 1 — §4.3, doublons et échéances (fixture `a13-export-defauts-fictif.csv`, `--au 2026-11-25`).**
J'ai déroulé les 30 lignes à la main :

- L2 nom vide → *Champ obligatoire absent : nom*. L3 échéance `illisible-fictif` → *illisible*.
  L4 `2000-01-01` < référence → *passée*. L5 `texte-fictif` / L26 `1.5` → *numéros illisibles*.
  L6 `-1` → *négatif*. L7/L21/L22/L23 un champ postal vide → *adresse incomplète* (×4).
  L8 `pas-un-email` → *mal formée*. L9 `inconnu-fictif` → *mode non déclaré*.
  L10 mandat papier sans référence → *mandat sans référence*.
- L12/L13 : `doublon-fictif@…` vs ` DOUBLON-FICTIF@… ` → doublon email après normalisation.
- L14/L15 : `Fictif Éléphant / Flocon / 12 allée Fictive` vs la même en casse/espaces/accents
  variés → doublon nom + adresse postale (emails différents, donc pas un doublon email).
- L16/L17 : `MANDAT-FICTIF-DOUBLE` → référence de mandat en double.
- L18-20, L24-25 : obligatoires absents (type, échéance, numéros, coopérateur, mode).
- L27 `2027-02-29` (2027 non bissextile) → *illisible*. L11 email vide → **sans email, non rejetée**.

Total dérivé : **25 lignes rejetées**, **5 sans défaut** (L11 + L28-31), **6 lignes en doublon**,
**1 sans email**. Identique au résumé produit (`production/A-13/verification.json`, bloc `defauts`)
et au test `test_dirty_fixture…:187-215`. Chaque défaut tombe sur sa ligne physique exacte.

**Cas 2 — §4.3 « Aucun IBAN n'est importé » (fixture `a13-export-iban-fictif.csv`).**
En-tête colonne 14 = « IBAN fictif » → `normaliser` donne `ibanfictif` qui contient `iban` →
refus. Le contenu `ZZ00 0000 0000 0000 0000` déclenche aussi la regex (`controler-export:15`).
Résultat attendu : code **2**, « IBAN suspect : colonne 14 », **aucune sortie**, **aucune valeur
recopiée**. Conforme au bloc `iban` de `verification.json` et aux tests `test_iban_*`.

**Cas limites vérifiés.** Échéance = date du jour → acceptée (`<` strict, `analyser:212` ;
test `:237-241`). `0` numéro → accepté. Changement d'année / année bissextile → `2027-02-29`
illisible. Cellule multiligne entre guillemets → le numéro de ligne reste physique
(`test_source_line_number…:264-269`). Encodages cp1252 (refusé sans déclaration), BOM UTF-8/UTF-16,
séparateur ambigu (refusé) : tous déroulés dans la suite et cohérents.

Le découpage « signaler sans décider » est respecté : l'échéance passée est un motif, pas une
décision de migration (§2.3 : ces abonnés ne partent à Odoo qu'au renouvellement).

## 3. Tests

### Suite PHP autorisée (non-régression globale)

Commande exécutée, sans argument, conteneur jetable sans réseau, dépôt monté en lecture seule :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Dernière ligne :

```text
REJEU : 1062 tests, 34271 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Réserve : cette suite est **en PHP** et ne couvre pas A-13, qui est en Python. Elle prouve la
non-régression du reste du dépôt, pas le comportement de l'outil A-13. Ce dernier se valide par sa
propre suite Python, le déroulé manuel ci-dessus et les trois appels CLI du vérificateur.

### Suite Python du lot (ses tests)

```text
python -m unittest discover -s wp/tests/a13 -v   →  35 tests, 34 ok, 1 ERREUR
python wp/outils/bascule/a13/… (vérificateur)    →  échec (même cause)
```

Sur ce poste (Python 3.14.6, Windows, locale cp1252), **la suite et le vérificateur officiel
échouent**. Un seul test est en cause : `test_repository_output_refused_without_touching_fixture`.
La livraison (`LIVRAISON.md`) annonce « 35 tests, 0 échec » sur Python 3.11.15 ; ce résultat n'est
donc **pas reproductible** selon la locale. Détail et correction au § Verdict (point bloquant).

Qualité des tests : ils vérifient la règle, pas le code. Les diagnostics sont contrôlés sur la
ligne physique exacte, les fuites de données sont testées négativement
(`test_dirty_fixture…:213-215`, vérificateur `:63-64`), et le préflight est couvert avant écriture.
Couverture des cas limites réelle, pas seulement nominale.

## 4. Sécurité et données

- Aucune donnée réelle : fixtures fictives, noms inventés, adresses `@example.org`. Conforme §3.
- Aucune recopie de cellule dans les sorties ; IBAN jamais ré-émis (tests négatifs explicites).
- Écriture dans le dépôt refusée, lien symbolique résolu compris (`ecrire:34-39`).
- Pas de secret, pas de réseau, pas d'appel à un site/compte/API. Lecture seule du CSV.
- Les refus publics passent par `Refus` (`controler-export:52-53`), sans trace ni donnée de
  cellule ; le `main` rattrape aussi `OSError/ValueError/csv.Error` en message générique
  (`:289-291`). Pas de « paywall » ici : hors périmètre.

Rien à signaler sur ce chapitre.

## 5. Doctrine

- Standard d'abord : rien à réutiliser côté WordPress, le besoin est précisément un contrôle
  préalable autonome, hors site. Choix de Python pur justifié et documenté.
- Conventions : outil hors WordPress, donc PSR-12/`Imagine\` sans objet ; le code est clair,
  typé par usage, messages d'interface en français.
- Rejouable / preuves hors dépôt : le vérificateur copie en scratch, exécute la vraie CLI, vérifie
  codes/quantités/intégrité puis nettoie. Bon. **Mais** la reproductibilité de la suite est prise
  en défaut par la locale (voir Verdict) : la doctrine §4 (« donne le même résultat ») n'est pas
  tenue tant que ce test n'est pas durci.

## 6. Études

Sans objet : lot de code.

## Verdict : **À corriger**

Le code de l'outil est conforme et correct ; le blocage porte sur le harnais de test.

### Bloquant

1. **La suite A-13 et le vérificateur officiel échouent selon la locale** —
   `wp/tests/a13/test_controler_export.py:89-90`. C'est le seul appel `subprocess.run` de la suite
   qui **n'ajoute pas** `env={**os.environ, 'PYTHONIOENCODING': 'utf-8', …}` (présent partout
   ailleurs, `:34-37`), alors que `assert_refused` lit `stderr` en UTF-8 (`:47-52`). Le message
   `REFUS : … dépôt …` est accentué ; l'enfant l'émet dans l'encodage local (cp1252 ici), le thread
   lecteur du parent plante (`UnicodeDecodeError`), `stderr` devient `None`, puis
   `assert_refused` lève `TypeError: can only concatenate str (not "NoneType")`.
   J'ai confirmé la cause : avec `PYTHONIOENCODING=utf-8` passé à l'enfant, la CLI retourne bien le
   code **2** et un `stderr` exploitable, sans crash — l'outil lui-même est correct.
   **Conséquence** : « tests au vert » n'est pas reproductible (doctrine §4, §6) ; la clôture ne
   peut pas s'appuyer sur ces preuves tant que ce test tombe sur un poste à locale cp1252.
   **Correction proposée** (une ligne) : ajouter le même dict `env=…` à l'appel `:89-90`, comme
   `run_cli`. Aucune modification de l'outil n'est nécessaire.

### Mineur

2. **Double libellé possible** — `analyser:200-221`. Si un champ postal (`rue`, `code_postal`,
   `ville`, `pays`) est placé dans `obligatoires`, une ligne vide porte à la fois
   « Champ obligatoire absent : … » et « Adresse postale incomplète ». La correspondance d'exemple
   ne le fait pas, donc pas visible aujourd'hui. À documenter dans `controler-export.md`, ou à
   dédoublonner. Non bloquant.

## Décisions techniques, défaut proposé

- **Détection IBAN volontairement large** (`controler-export:15`). La regex peut bloquer un faux
  positif (le brief l'accepte explicitement, `controler-export.md:30-32`). Défaut proposé :
  **conserver** le biais prudent (bloquer en cas de doute). J'arbitre : rien à changer.
- **Portée de la preuve PHP vs Python** : l'unique commande de rejeu autorisée exécute la suite
  PHP, qui ne touche pas A-13. Défaut proposé : **conserver** la validation A-13 par sa suite
  Python une fois le point bloquant corrigé ; mentionner cette séparation dans `LIVRAISON.md`.

## Pour Imagine (question métier)

- **Clé du doublon « nom + adresse postale »** — `controler-export:231`. Le code inclut le
  **prénom** dans la clé, alors que le brief dit « même nom et même adresse postale ». Choix
  signalé (`controler-export.md:65-66`). Question fermée : le doublon « nom + adresse » doit-il
  **ignorer le prénom** (deux personnes de même nom à la même adresse = un seul doublon) ou le
  **garder** (conjoints/colocataires au même nom de famille non confondus) ?
  Défaut prudent proposé : **garder le prénom** (comportement actuel, moins de faux positifs).
  Aujourd'hui ce n'est pas un réglage ; si Imagine veut le nom seul, en faire une option de la
  correspondance, désactivée par défaut.

---

*Rappel doctrine §6 : ce verdict n'est pas un GO. Le marqueur `production/A-13/PRET` et le
déploiement relèvent de Ced. La fusion avec `codex.md` n'est pas faite (non demandée).*
