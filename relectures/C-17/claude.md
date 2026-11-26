# Relecture C-17 — Justificatifs du tarif solidaire (relecteur Claude indépendant)

Date : 26 novembre 2026. Base : brief `briefs/C-17-justificatifs-tarif-solidaire.md`, CDC §3.13, §3.7, §4.4, doctrine, grille.
Je n'ai **pas** lu `relectures/C-17/codex.md`. Pas de fusion à ce stade.

## Ce que j'ai lu et exécuté

- Code : `wp/plugins/imagine-site/JustificatifRegles.php`, `Justificatifs.php`, `JustificatifsReglages.php`, réemploi de `PdfNumero.php` (C-11), intégration `wp/themes/imagine/parts/mon-compte.php`, enregistrement dans `imagine-site.php`, `README.md`.
- Tests : `tests/JustificatifReglesTest.php` (règles pures) ; démo `tests/demo/c17_http.py`, `c17-faults.py`, `c17-reglages.py`, seed `wp/outils/demo/c17-profils.php`.
- Suite PHP rejouée, conteneur jetable, sans réseau, dépôt en lecture seule, commande autorisée sans argument :

  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

  Dernière ligne :
  `REJEU : 1077 tests, 34327 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

- Les gates HTTP de démo (`http-final.json` 49/49, `reglages-final.json` 8/8, `faults-final.json` 8/8) tournent contre le staging `192.168.129.32:8085`, que je ne touche pas (doctrine §3). Je ne les ai pas rejoués. Mon verdict se fonde sur la lecture du code, la suite PHP conteneurisée (PASS) et le déroulé manuel ci-dessous. Les reçus sont cohérents avec le code lu, mais non revérifiés par moi.

## 1. Conformité

- Côté abonné (`mon-compte.php:66` → `imagine_compte_justificatif` → `Justificatifs::compte`) : statut à quatre états (aucun / en attente / validé jusqu'au… / refusé), dépôt image ou PDF, taille plafonnée (5 Mio), et la phrase qui invite à masquer le numéro de registre national (`Justificatifs.php:298`). Conforme au brief et à §3.7.
- Côté administration (`Justificatifs.php:310` `page()`), sous **Imagine → Justificatifs solidaires**, capacité `imagine_traiter_justificatifs` : file des dépôts en attente, ouverture du fichier protégé, **Valider** (date de fin saisie) ou **Refuser**, confirmation obligatoire. Conforme à §3.13.
- Stockage hors racine publique et service contrôlé à chaque lecture : `chemin()` réutilise `PdfNumero::directory()` et `servir()` réévalue le droit à chaque GET (`Justificatifs.php:54,233`). La mécanique du PDF du numéro (C-11) est réemployée, pas refaite. Conforme à la consigne du brief.
- Suppression à la décision, validation **comme** refus (`decider()` → `supprimerFichier($old)` avant enregistrement, `Justificatifs.php:218`). Le site ne conserve ensuite que l'état documentaire. Jamais deux fichiers : `recevoir()` supprime l'ancien avant d'écrire le nouveau (`Justificatifs.php:122`). Conforme à §4.4 et au brief.
- Type vérifié sur le contenu, pas sur le nom (`JustificatifRegles::mime()` via `finfo`, `Justificatifs.php:65` test `nom-trompeur.php`). Aucun exécutable, livraison en `attachment` + CSP `sandbox` + `nosniff`, pas de prévisualisation exécutante (`Justificatifs.php:266-269`). Conforme.
- Ne touche ni au prix ni à l'accès : aucun appel Woo/abonnement/droit/email dans le flux ; `state()` commercial identique avant/après dans la preuve. Conforme au brief et à la question 4 du chapitre 7 (toujours ouverte dans `docs/decisions.md`).
- Catégories en réglage, écran C-10 par hooks + Settings API + journal, défaut unique **à préciser** (`JustificatifsReglages.php:15,50`). Conforme.
- Droit dédié + nonce + aucun email sortant. Conforme.
- **Point de conformité (voir §Doctrine, point 1)** : après décision l'état conserve `categorie`, `decision`, `date_decision`, `fin`, `operateur` (`JustificatifRegles.php:75-76`). Le brief liste explicitement ces cinq champs, mais le CDC §4.4 dit « ne conserve que la catégorie et la date de fin ». Écart brief↔§4.4 assumé par Hermès dans `A-VOIR.md`, à trancher et à tracer dans `docs/ecarts.md` à la fusion.

## 2. Exactitude métier (déroulé à la main)

- **Cas nominal (scénario du brief)** : P-SOL-ATT dépose → état `en_attente` + blob 32 hex, fichier écrit hors racine. Apparaît dans la file (`page()` requête `LIKE '…decision";s:10:"en_attente";…'`). URL demandée par anonyme / autre abonné / rédaction → `servir()` renvoie 403 avant toute lecture (`Justificatifs.php:243`). Après validation : `supprimerFichier` retire le blob, l'état n'a plus de `blob` → `chemin()` lève, lecture 404, et le compte affiche « Validé jusqu'au … » (`compte()`:290). Fichier absent du disque. **Conforme.**
- **Refus** : `decider('refuse', …)` → `fin=''`, pas de `blob` (`JustificatifReglesTest::testRefusalKeepsNoEndDateOrBlob`), fichier supprimé, compte « Refusé ». **Conforme.**
- **Second dépôt remplace le premier** : `recevoir` sous verrou supprime l'ancien fichier puis écrit un nouveau blob ; un seul fichier subsiste. **Conforme.**
- **Cas limite date = clôture / changement d'année** : `decider` exige `fin` au format `!Y-m-d` strict et `fin >= date UTC du jour` (`JustificatifRegles.php:70-72`). `2027-02-29` (inexistante), `2026-11-25` (passée), `2027-01-01xxx`, `''` rejetées (`testInvalidDateAndReplayAreRejected`). Date = aujourd'hui acceptée (non `<`). Nuance métier mineure (statut expirant le jour même), sans conséquence automatique ici.
- **Événement rejoué / concurrence** : jeton de version = `sha256(serialize(state))` dans le formulaire ; `decider` et `recevoir` revérifient sous `GET_LOCK` par utilisateur. Un formulaire périmé ou une décision déjà prise → 409 (`Justificatifs.php:208,118`). `c17-faults.py` confirme deux référents simultanés : une réussite 200, une 409, une seule suppression. **Conforme, idempotent.**
- **Suppression impossible** : `supprimerFichier` lève si le fichier résiste ; la décision n'est alors pas enregistrée et les octets sont préservés (`c17-faults.py`). **Conforme** : l'opération se ferme sans annoncer de succès.

## 3. Tests

- Suite PHP conteneurisée **au vert** (voir ci-dessus).
- `JustificatifReglesTest` teste la règle, pas la copie du code : détection par octets + plafond, catégories strictes + inconnue rejetée, refus sans date ni blob, dates invalides/rejeu, champs minimaux exacts. Couvre les cas limites.
- Les tests de démo (`c17_http.py`, `c17-faults.py`, `c17-reglages.py`) sont de vrais parcours HTTP de bout en bout (octets/hash sur disque, refus paywall, HEAD, méthode, nonce, remplacement, suppression disque, reset). Bonne couverture. Non rejoués par moi (staging interdit).
- Réserve héritée signalée par Hermès : C-09 **381/382** (`A-PAPIER`, action 8103 annulée le 25/11/2026, antérieure à C-16, inchangée). Non bloquante pour C-17 selon la consigne du parent. Je la relaie sans la rouvrir.

## 4. Sécurité et données

- Aucun secret ni donnée réelle : fixtures PDF synthétiques (`c17-profils.php:document`), identifiants hors dépôt (`~/.imagine-demo/identifiants.json`). Scan des preuves `production/C-17/` : aucun email hors `@example.*`, aucun mot de passe en clair (les clés `*:password` sont des noms d'assertions booléennes, pas des secrets).
- Contrôle des droits à chaque lecture, nonce distinct de l'autorisation, POST obligatoire, méthode restreinte (GET/HEAD pour le service, 405 sinon), échappement systématique des sorties (`esc_html`/`esc_url`/`esc_attr`), requêtes préparées (`$wpdb->prepare`). Vérifié.
- Paywall / étanchéité : le fichier réservé ne sort que pour le titulaire ou le porteur de la capacité, et seulement tant que `decision === 'en_attente'` avec blob exact (`servir()`:253-256). Média non exposé par le chemin standard WordPress (pas de pièce jointe créée). Aucune voie de fuite repérée à la lecture.

## 5. Doctrine

- **Standard d'abord** : formulaire natif, sessions, capacités, nonces, `admin-post.php`, Settings API, journal C-10, stockage privé C-11 réemployé. Sur-mesure limité à ce que le standard ne fait pas (stockage hors public sans média). Conforme, sources citées dans `A-VOIR.md`/`README.md`.
- **Logique métier hors WordPress** : `JustificatifRegles` est du PHP pur testable sans base. Conforme.
- **Conventions §5** : `declare(strict_types=1)`, espace de noms `Imagine\`, préfixe `imagine_`, textes FR traduits, aucune bibliothèque tierce modifiée (extension par hooks), `README` présent. Conforme.
- **Point 1 (conformité ↔ §4.4)** : fait un peu **plus** que §4.4 (métadonnées `decision`/`date_decision`/`operateur` conservées). Défendable comme trace d'audit côté référent (données de personnel, pas du justificatif de l'abonné ; le document est bien détruit). Mais §4.4 fait foi et dit « que la catégorie et la date de fin ». À réconcilier.

## 6. Études

Sans objet (lot de code).

---

## Verdict

**Conforme**, avec points mineurs et une question de conformité à trancher. Rappel doctrine : ce verdict n'est **pas** un GO, et il ne vaut que sous réserve de la relecture croisée et des gates staging que je n'ai pas rejoués.

### Points — classés

**Bloquant** : aucun.

**Important** : aucun.

**Mineurs**

1. *Conformité / §4.4* — `JustificatifRegles.php:75-76`, `Justificatifs.php:218`. L'état après décision conserve `decision`, `date_decision`, `operateur` en plus de `categorie` et `fin`. Le brief l'exige explicitement ; §4.4 dit « que la catégorie et la date de fin ». Écart assumé dans `A-VOIR.md`, à trancher puis tracer dans `docs/ecarts.md` à la fusion. Pas de code à changer tant que la question n'est pas tranchée.
2. *Droit / périmètre réel* — `wp/outils/demo/c09-seed.php:93`. La capacité `imagine_traiter_justificatifs` n'est accordée que par le seed démo C-09 ; le plugin ne la déclare ni ne la mappe aux administrateurs. Hors démo seedée, l'écran serait invisible, même à un admin. Acceptable pour ce lot démo ; à confirmer pour le déploiement réel (futur lot).
3. *Robustesse (déjà assumé)* — `Justificatifs.php:122-123`. Dans `recevoir`, l'ancien fichier est retiré du disque avant l'écriture confirmée du nouveau. Si l'écriture échoue, l'option pointe un blob sans fichier ; auto-rétabli au dépôt suivant. L'invariant « jamais deux fichiers » est préservé (l'erreur va vers zéro fichier). Documenté dans `A-VOIR.md`. Signalé, pas de correction demandée.
4. *Sécurité (déjà assumé)* — `JustificatifRegles.php:48`. Le refus de contenu PDF actif est une regex sur octets bruts, contournable par flux compressés. Ce n'est pas une désinfection universelle ; le brief est satisfait par `attachment` + CSP `sandbox` + `nosniff` (pas d'exécution). Limite explicitée dans `A-VOIR.md`. Acceptable.

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

- *Capacité dédiée hors démo* (point 2). Défaut proposé : **laisser tel quel** (moindre privilège, la capacité reste portée par un rôle et non par tout admin) ; ne rien changer dans ce lot ; ouvrir la déclaration/mappage de la capacité au lot de mise en production réelle. À confirmer par Claude en fusion.

### Pour Imagine (question fermée, devient un réglage/décision)

- *Champs conservés après décision.* Faut-il conserver, côté dossier, en plus de la **catégorie** et de la **date de fin** (§4.4), la **décision**, sa **date** et le **nom de l'opérateur** comme trace d'audit référent ? Défaut prudent proposé : **oui, les conserver** (le justificatif lui-même est détruit, la minimisation côté abonné est maintenue, l'audit est côté personnel). Si non : retirer `date_decision` et `operateur` de l'état et ajuster `JustificatifRegles::decider`. À tracer dans `docs/ecarts.md` à la fusion (contradiction brief ↔ §4.4).

---

`codex.md` existe mais n'a pas été ouvert. Je m'arrête après ce rapport, sans fusion, conformément à `relecteurs/CLAUDE.md`.
