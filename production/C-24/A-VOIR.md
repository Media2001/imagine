# C-24 — À voir, livraison partielle BLOQUÉE (pas de PRET)

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
