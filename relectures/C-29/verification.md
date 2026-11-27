# Vérification — second et dernier tour — Lot C-29 « La fiche du contact pour Brevo, sans Brevo »

Vérificateur : Claude. Date : 2026-11-27.
Base : corrections fusionnées `corrections/C-29.md` (commit `6be70e21`, 17h53), appliquées ensuite par Hermès.
Méthode : `git diff 6be70e21 HEAD` sur `wp/` et `production/C-29/`, lecture du code corrigé, rejeu de la suite PHP autorisée (`wp/tests/rejouer.ps1`, conteneur jetable `network=none`, dépôt monté en lecture seule).
Je ne refais pas une relecture complète : je contrôle uniquement l'application des instructions, les tests et les régressions.

---

## 1. Instructions de `corrections/C-29.md`, une par une

### Instruction 1 — préserver la désinscription explicite hors catalogue (C29-01) — **Appliquée**
`ContactBrevoRegles.php:20-24` : une première boucle parcourt **toutes** les préférences et pose `retrait=true` dès qu'un `origine=lecteur, choix=false` existe, indépendamment du catalogue. La boucle du catalogue (`:25-29`) ne retient plus que les `choix=true` encore présents pour composer `newsletters`. Conséquences vérifiées à la main :
- `catalogue=[]` + préférence `choix=false, origine=lecteur` ⇒ `newsletters=[]`, `retrait=true` ⇒ fiche réduite `{statut:a_retirer}` (`desinscrit_de_tout`). Conforme au défaut arbitré.
- `catalogue=[]` + préférence encore `choix=true, origine=lecteur` (suppression administrative d'une lettre encore choisie) ⇒ `newsletters=[]`, `retrait=false` ⇒ `aucun_choix_lecteur`, **pas** de retrait. Le témoin demandé est respecté.
Les deux cas réclamés sont ajoutés à la fixture : `refus_hors_catalogue` (`tests/fixtures/c29-cases.php:23`) et `suppression_choix_positif_sans_retrait` (`:24`).

### Instruction 2 — identifier le bénéficiaire de groupe indépendamment de l'activité postale (C29-02) — **Appliquée**
`ContactBrevo.php:216-222` : pour l'origine `groupe`, `contexte()` lit désormais `$relation['relation_native']` (les liens natifs `$links` d'`EnvoiRelations`, champ `user_id`) et non le seul `beneficiaires` filtré par `is_active()`. `EnvoiRelations::beneficiaires` (`EnvoiRelations.php:66-89`) construit `$links` **avant** le `continue` sur `!is_active()` : les adhésions suspendues y figurent. Tout bénéficiaire identifié (`user_id>0`, ≠ payeur, compte existant) est marqué ⇒ `statut` et `tarif` passent à `inconnu`, actif ou suspendu.
- **Ne touche pas à C-13** : `EnvoiRelations.php` et `Newsletters.php` sont **inchangés** depuis le commit de corrections (`git diff` vide). L'adaptation est bien côté C-29.
- Test ajouté comme demandé : `wp/tests/demo/c29-runtime.php:141-155` boucle sur `active` puis `paused`, relit l'état natif avant chaque assertion (`groupe_etat_natif_relu_*`, `groupe_lien_natif_relu_*`) et vérifie `beneficiaire_groupe_inconnu_active` et `beneficiaire_groupe_inconnu_paused` (`statut=inconnu`, `tarif=inconnu`) dans les deux cas.

### Instruction 3 — reformater les appels multiligne en PSR-12 (C29-03) — **Appliquée**
`ContactBrevo.php` : `register()`, `reglages()` (`register_setting`), `contexte()` (`wcs_get_subscriptions`) et `fiche()` (`ContactBrevoRegles::fiche`) sont réécrits un argument par ligne, parenthèse ouvrante seule puis fermante sur sa propre ligne. Aucun changement fonctionnel décelé.

### Instruction 4 — i18n extractible (mineur) — **Appliquée**
`ContactBrevo.php:132-143` : les libellés d'en-tête sont déclarés `__('Abonné', 'imagine-site')`, etc., sur **chaîne littérale** dans le tableau `$labels`, puis indexés. Idem pour les raisons `$reasons` (`:144-151`). Les `__($variable, …)` signalés au premier tour ont disparu ; l'extraction `.pot` verra désormais les chaînes.

### Instruction 5 — ne pas clôturer tant que `rejouer.ps1` rend FAIL — **Respectée**
`production/C-29/PRET` dit « C29 **PRET technique** », pas clôture, et `NOTE-corrections-V2.md` applique la règle 19h30 : paquets voisins laissés hors lot, aucune clôture ni validation visuelle revendiquée. Aucune mention de GO réel. Conforme au défaut proposé.

### Question Ced (C29-01 : un refus explicite survit-il à la suppression de sa lettre ?)
Reste posée à Ced. Le code applique le **défaut prudent « oui »** (on préserve le retrait), comme prévu. Rien à vérifier de plus : c'est un arbitrage réel, pas une instruction de code.

---

## 2. Résultat des tests

Rejeu de la suite PHP autorisée (`powershell.exe -File ./wp/tests/rejouer.ps1`) :

```
PAQUETS : 13 vérifiés, 0 échecs ; hors rejeu : aucun
OUTILS  : 23 outils, 852 contrôles, 0 échecs ; hors rejeu : aucun
REJEU   : 1211 tests, 36697 assertions, 0 échecs, 1 erreurs, 0 ignorés — FAIL
```

Lecture :
- **Lot C-29 vert.** `ContactBrevoC29Test` : 3 tests, **51 assertions** (47 au premier tour ; +4 pour les deux cas ajoutés), 0 erreur, 0 échec.
- **A-31, A-32, A-33 sont désormais VERTS** (outil `a31` : 276 contrôles, 0 échec ; paquets A-31/A-32/A-33 vérifiés, 0 échec). Les rouges voisins vus au premier tour (a31 : 6 échecs ; `A32_PACKAGE_DRIFT`) ont été remis au vert dans leurs lots entre-temps.
- **Le rejeu rend encore FAIL, mais pour une seule erreur, étrangère à C-29** : `PageArticleB16Test::testCorpsEtModeLectureRestentAuxAdaptateursExistants` (`tests/PageArticleB16Test.php:23`), `TypeError: substr_count(): Argument #1 must be of type string, bool given`. C'est le chantier **B-16** en cours (le fichier de test est non suivi dans `git status`), sans aucun lien avec le code ni les tests C-29.
- Les recettes natives/HTTP (`c29-runtime.php`, `c29-http.py`) ne font pas partie de `rejouer.ps1` (elles exigent le site) ; non rejouées de ma main, hors commande autorisée. Leurs preuves sont décrites dans `production/C-29/NOTE-corrections-V2.md`.

## 3. Régressions et modifications non demandées

- **Aucune régression propre à C-29.** Les corrections ne touchent que `ContactBrevoRegles.php`, `ContactBrevo.php`, `tests/fixtures/c29-cases.php`, `wp/tests/demo/c29-runtime.php`, `README.md` (section C-29) et `production/C-29/`. `EnvoiRelations.php` et `Newsletters.php` sont intacts.
- **Modifications voisines dans la même fenêtre de synchro, étrangères à C-29** : `Accueil.php`, `Navigation.php`, `PageArticle.php`, `PiedPage.php`, `imagine-site.php` et leurs tests (B-13/B-14/B-15/B-16) ont été commités dans le même intervalle. Ce sont d'autres lots, non pilotés par `corrections/C-29.md`. C'est l'un d'eux (B-16) qui introduit la seule erreur du rejeu. À traiter dans son lot, pas depuis C-29.
- Conséquence : le rejeu global reste **FAIL**, donc — strictement — C-29 n'est pas *clôturable* tant que la suite autorisée est rouge (défaut « non » des Décisions techniques). Mais le motif du rouge a changé : ce n'est plus A-31/A-32 (verts), c'est B-16, en cours.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions de `corrections/C-29.md` sont **appliquées** et correctement : les deux écarts métier du premier tour (C29-01 refus hors catalogue, C29-02 bénéficiaire de groupe suspendu) sont corrigés et couverts par des tests neufs (pur + natif), le PSR-12 et l'i18n sont réglés, EnvoiRelations/C-13 n'est pas touché, aucune clôture n'est revendiquée. Les tests propres à C-29 sont verts (3 tests, 51 assertions). **Aucun problème de fond ne reste dans C-29.** Il n'y a donc rien à remonter à Ced sur le fond du lot ; son attention porte sur la validation visuelle/métier habituelle.

Réserve de clôture (hors fond C-29, pour mémoire) : `rejouer.ps1` rend encore FAIL à cause d'une erreur **B-16** (lot voisin en cours). La clôture de code de C-29, par la règle « suite verte », reste suspendue à la remise au vert de B-16, à obtenir dans ce lot-là — sans y toucher depuis C-29. Ce verdict de vérification n'est, de toute façon, pas un GO (doctrine §6).
