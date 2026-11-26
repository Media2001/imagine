# C-24 — À voir : corrections de la fusion du 26 novembre 2026 à 20 h 50

## État courant — paquet neuf `manifest-fusion2050-V2.json`

**Cinq corrections appliquées ; PRET technique après portes vertes, pas de validation visuelle ni GO réel.** Le paquet précédent ci-dessous devient historique ; ses reçus restent intacts et ne sont pas réutilisés comme preuve du produit corrigé.

- Restauration du journal : préimage interne validée, drapeau privé et égalité stricte, puis readback. Tests TDD RED réels (500 et catalogue perdu) avant correction ; GREEN : retrait de question et retrait de choix restaurent exactement l'ancienne option, aussi en lecture SQL. Deux vrais POST `options.php` échouent au journal, retournent une redirection normale sans 500, affichent le refus et conservent la préimage.
- Newsletter : seule `origine=lecteur` compte. La vraie méthode `Newsletters::creation` produit une préférence `defaut_creation` qui reste non transmissible ; origines inconnue/absente également refusées, accord explicite du lecteur admis si consentement et email présents. RED original et mutant d'origine détectés.
- C10 : vraie page rendue par Chromium ; section présente **dans** le formulaire existant, entre son ouverture et sa fermeture, sous le même bouton. Mutation de retrait de l'injection C24 réellement rouge, état métier remis exactement. Aucun déplacement visuel.
- README du plugin complété par sa seule nouvelle section C24 ; autres sections préservées. Rôle des quatre classes, réglage, deux métadonnées, accroches et commandes locales/site distinctes.
- Compteurs frais : **1 128 tests / 35 565 assertions**, zéro échec/erreur/ignoré ; **16 outils / 331 contrôles**, zéro échec. Préparation officielle d'image puis `rejouer.ps1` réellement exécutés, codes 0 (`fusion2050-preparation-V2`, `fusion2050-regression-V2`).

Paquet C24 frais : **148 contrôles nominaux** (29 purs + 35 natifs + 44 HTTP + 8 gardes + 32 corrections), **16 mutations détectées** (7 historiques rejouées + 5 gardes + 3 corrections + 1 C10). Les compteurs sont recalculés depuis les JSON, non repris d'une ancienne annonce. HTTP : **51 requêtes observées, 0 tentative de mail, 69 tentatives HTTP WordPress bloquées sur 69**, aucune issue de Personnalisation. Observateur temporaire retiré, absence relue ; snapshots privés durables avant sessions/mutations et readback final des rôles/profils/commandes/abonnements/adhésions/réglages/actions métier. L'incident historique reste décrit une seule fois dans le relais ancien : aucune restauration des anciennes sessions perdue n'est prétendue.

```bash
PYTHONIOENCODING=utf-8 python -B production/C-24/verifier-fusion2050-V2.py
```

Adresses/profils : rubrique « Adresses » plus bas, inchangée. Captures fraîches : `fusion2050-http-V2-compte.png`, `fusion2050-http-V2-sans-email.png`, `fusion2050-http-V2-reglages.png` (données d'essai ensuite restaurées).

Questions non bloquantes : Imagine, localité en choix fermés (défaut) et exclusion de l'inscription newsletter par défaut (défaut prudent) ; Ced, place des rubriques sous « Enregistrer » et ergonomie JSON. Style laissé en l'état selon la fusion ; aucune bibliothèque close, bootstrap partagé, C21/C22/B06/B07 ou autre site modifié. Aucun paiement ni transport extérieur.

---

# Historique de la qualification précédente — remplacé par le paquet fusion2050


## Qualification finale depuis la baseline récupérée

**PRET technique ; validation visuelle de Ced non acquise.** Les adresses et profils ci-dessous restent valables. Captures actuelles : `http-metier-final-V2-compte.png`, `http-metier-final-V2-sans-email.png`, `http-metier-final-V2-reglages.png`. Leurs réponses d'essai ont ensuite été restaurées.

- HTTP réel Chromium + POST : `http-metier-final-V2.json`, **38 contrôles verts**, 45 requêtes observées, 0 tentative de mail, 53 appels HTTP WordPress bloqués sur 53, 0 appel HTTP de Personnalisation. Observateur retiré et absence relue.
- Qualification native : `mutations-qualifiees-V2.json`, **8 contrôles nominaux verts et 5 mutants de vraies sources détectés séparément** : garde de question, garde de choix, consentement, newsletter, admissibilité email. Classes mutées évaluées uniquement en mémoire, jamais installées ; rollback et readback métier pour chaque exécution.
- **29 contrôles purs + 35 natifs et 7 mutations déjà acquis** : reçus historiques réutilisés après vérification des empreintes inchangées des quatre classes produit et des deux tests. Pas de faux rejeu annoncé. Paquet : **110 contrôles nominaux, 12 mutations détectées**, dont 46 contrôles et 5 mutations exécutés pendant cette reprise.
- `preparation-finale-V2.json` : commande officielle `wp/tests/preparer-image.ps1`, code 0, image vérifiée, rien installé sur l'hôte.
- `regression-finale-V2.json` : `wp/tests/rejouer.ps1`, **1 126 tests, 35 550 assertions, 0 échec/erreur/ignoré ; 16 outils, 311 contrôles, 0 échec** ; conteneur hors réseau retiré et absence vérifiée.
- Sources, reçus et readback : `manifest-final-V2.json`. Vérification hors réseau : `PYTHONIOENCODING=utf-8 python -B production/C-24/verifier-V2.py`.

**L'état récupéré est explicitement une nouvelle baseline.** Avant toute session, snapshot privé écrit avec `fsync`, relu et haché dans le scratch privé ; conservé après succès, identifié seulement par nom opaque et empreinte dans le reçu. Restauration depuis les octets relus. Rôles, profils, comptes/métadonnées, commandes, abonnements, adhésions, réglages et actions métier retrouvés ; réserves C22 antérieures conservées exactement. Le snapshot initial historique perdu n'est **jamais** annoncé retrouvé : `recovery-borned-V2.json` reste inchangé et `exact_initial_snapshot_restored: false`.

Le reçu rouge `http-requalification-final-V2.json` est conservé : il confondait le délai d'expiration recréé du cache `_transient_timeout_wcs_woocommerce_active_version` avec l'état métier. Diagnostic : comptes/métadonnées/actions et état natif exacts. Harnais corrigé pour exclure seulement caches transitoires et verrou AS du contrôle métier ; nouveau rejeu vert. Les inverses ne ciblent que les lignes constatées de l'exécution présente, pas les anciennes sessions perdues.

`mutations-finales-id-question-V2.json` conserve un mutant intermédiaire non détecté : l'ancien test sollicitait deux gardes ensemble, celle des choix masquait celle des questions. Le test final les isole ; chacune est réellement détectée. Aucun correctif produit nécessaire.

**Questions non bloquantes conservées :** Imagine, localité libre ou fermée ? Défaut : choix fermés. Ced, place des sections C22/C24 sous « Enregistrer » ? Inchangée. Aucun email, réel, paiement, connecteur, politique de découverte, code C23/B06 ni bibliothèque close modifiés par cette reprise.

---

# Historique de la livraison partielle — conservé, remplacé par la qualification ci-dessus

Les mentions de blocage et d'absence de rejeu ci-dessous décrivent exclusivement la livraison initiale, pas l'état courant.

Site fictif unique : `imagine-test-demo`. Aucune validation visuelle de Ced acquise.

## Adresses

- Mon compte : `http://192.168.129.32:8085/my-account/#ma-personnalisation`, avec **A-PAPIER** : quatre questions explicitement fictives (situation, intérêts, âge, localité), réponses facultatives, datées, modifiables, effaçables. Trois formulaires distincts : réponses, effacement des réponses, consentement aux envois.
- Même adresse avec **A-SANSMAIL** : les questions existent, mais aucune case de consentement aux envois. Ce compte reste exclu des attributs du connecteur.
- Réglages C10 : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages`, avec **E-ADMIN**. Section « Questions de personnalisation » insérée dans le formulaire existant, sous son bouton comme C22 ; emplacement non déplacé. Identifiant, intitulé, choix simple/multiple et liste JSON des choix fermés. La dernière ligne ajoute une question sans changement de code.

Identifiants : fichier privé déjà établi par B00/C09, jamais recopié ici.

Captures du véritable parcours Chromium :

- `http-initial-V2-compte.png` : deux réponses datées, autres questions facultatives, consentement retiré et daté indépendamment.
- `http-initial-V2-sans-email.png` : réponses locales sans consentement aux envois.
- `http-initial-V2-reglages.png` : section C10 et tentative de recyclage refusée.

Ce sont des captures d'essai, **pas un reçu HTTP entièrement vert**.

## Vérifié

`livraison-partielle-V2.json` : **29 contrôles purs + 35 contrôles WordPress natifs, 0 échec nominal ; 7 mutations témoins détectées**. Les cycles RED/GREEN sont conservés. Réponses/consentement entrent dans de vrais callbacks d'export/effacement natifs ajoutés sans modifier C21. Les assertions lisent les résultats et les métadonnées persistées, pas seulement les retours de callbacks.

Le premier parcours Chromium a effectivement traversé les formulaires C10/Mon compte : réponses, modification, consentement donné/retiré, newsletter distincte, cinquième question, retrait et recyclage refusé. L'observateur a compté **45 requêtes, 0 tentative de mail, 53 appels HTTP WordPress tous bloqués, 0 appel HTTP provenant de Personnalisation** (`diagnostic-inverse-refuse-V2.json`). Il a été retiré et son absence relue.

## Pourquoi aucun PRET

Le premier inverse HTTP a refusé deux effets natifs non inventoriés dans son autorisation de restauration : réserves historiques de C22 et option-verrou du lanceur asynchrone Action Scheduler. Le snapshot était seulement en mémoire et a été perdu à la sortie du processus.

Une récupération **bornée**, sans réensemencement global, a retiré les trois métadonnées d'essai, les quatre sessions créées à l'instant exact identifié et les nouvelles options appartenant à cet essai. Le readback confirme que **l'état métier et toutes les empreintes natives de départ C24 sont revenus exactement**, notamment rôles, commandes, adhésions, profils et actions métier. P-COOP conserve son attribut B06 ; la découverte reste fermée, sans numéros.

**On ne peut toutefois plus prouver les octets des anciennes sessions, de l'option-verrou AS et de l'ensemble des caches du premier parcours.** Le reçu `recovery-borned-V2.json` déclare explicitement `exact_initial_snapshot_restored: false`. Aucun état antérieur n'a été inventé pour obtenir du vert.

Le harnais HTTP conserve désormais le snapshot dans le scratch privé **avant** toute session et sépare les échecs de retrait de l'observateur et de restauration. Cette version corrigée n'a pas été rejouée : relais plutôt que multiplier les mutations sur une restauration historique non prouvable. Les mutations spécifiques au contournement des réserves d'identifiants et à la suppression des conditions de consentement restent à qualifier ; les comportements nominaux correspondants sont verts. L'image T01 n'a pas été repréparée et la suite générale n'est pas annoncée verte dans ce lot.
