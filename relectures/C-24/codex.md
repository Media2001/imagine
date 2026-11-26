# Relecture indépendante — C-24

Relecture du 26 novembre 2026 : brief C-24, doctrine, décisions, cahier des charges §3.7, §3.10, §4.2 et §4.4, sources dans `wp/` et dossier `production/C-24`. Le rapport Claude n'a pas été consulté. Aucun accès au site, à une base ou à un compte.

## 1. Conformité

Le périmètre demandé est présent : catalogue administrable dans C10, réponses facultatives, consentement séparé, compte sans email, réserves d'identifiants, export/effacement natifs, accroches nommées sans connecteur. Les reports du tunnel et du rappel email sont explicites. Aucun transport sortant trouvé dans les quatre classes produit. La validation visuelle reste à Ced.

### Pour Imagine

Question déjà documentée dans `production/C-24/TRANSMISSION.md`, citation exacte : « si la future localité doit être du texte libre, le confirmer explicitement ». **Catégorie : métier. Défaut prudent : liste fermée**, réglable avec les questions et leurs choix ; conserver ce défaut tant qu'Imagine n'a pas tranché.

## 2. Exactitude métier

Cas déroulés à la lecture du code, sans les présenter comme des exécutions :

- **Réponse puis consentement puis retrait** (§3.7, §3.10) : répondre écrit les choix et leur date sans créer le consentement ; donner l'accord sans newsletter laisse la projection vide ; retirer l'accord conserve les réponses. Conforme sur ce parcours.
- **Question retirée et compte sans email** (§3.7, §4.2) : la question retirée disparaît du formulaire, sa réponse historique reste stockée, son identifiant est refusé à la réintroduction ; l'effacement global retire aussi cet historique. Le compte sans email peut répondre mais ne voit pas la case d'accord et n'obtient aucun attribut transmissible. Conforme sur ces parcours.

**R1 — Important — `wp/plugins/imagine-site/PersonnalisationReglages.php:144` : la restauration réutilise le validateur qui interdit précisément de réintroduire les identifiants retirés.** Dans une sauvegarde C10, retirer une question puis faire échouer l'ajout du journal conduit à `update_option($key, $old, false)`. Cette écriture repasse par `nettoyer()` : le catalogue courant ne contient plus la question, mais sa réserve existe ; la restauration est donc refusée aux lignes 80–81. Le drapeau `$restoring` ne court-circuite que `journal()`. Résultat déduit : réponse 500 et nouveau catalogue conservé sans journal, au lieu de l'ancien état. Même problème au retrait d'un choix. **Correction proposée :** prévoir une restauration interne limitée à la préimage vérifiée, distincte de la validation d'une nouvelle saisie, puis relire l'état restauré. Ajouter un test injectant l'échec du journal après chacun de ces deux retraits.

## 3. Tests

- **Exécuté localement :** `python -B production/C-24/verifier-V2.py`, avec sortie UTF-8 : code **0**, **185 contrôles PASS**. Ce vérificateur contrôle les empreintes et la cohérence des reçus ; il ne réexécute pas les parcours métier.
- **Rejeu tenté :** `wp/tests/demo/c24-rules.php` dans l'image locale `imagine-tests-t01:1`, dépôt en lecture seule, réseau désactivé, sans téléchargement. Échec avant lancement de PHP : **`Wsl/Service/E_ACCESSDENIED`**, code 1. Aucun PHP disponible dans le PATH comme solution locale de remplacement.
- Les tests natifs et HTTP nécessitent le site et sa base : non relancés, conformément à `relecteurs/AGENTS.md`. La régression générale n'est pas annoncée rejouée par cette relecture.
- Les reçus vérifiés attestent historiquement **110 contrôles nominaux et 12 mutations**, ainsi que **1 126 tests / 35 550 assertions** pour la régression. La distinction entre preuves réutilisées et nouveaux essais est explicite. La perte du snapshot initial reste déclarée ; la baseline récupérée n'est pas présentée comme sa restauration exacte.

Les tests couvrent les refus de tiers/nonces, l'indépendance du consentement, les identifiants réservés et les résultats d'export/effacement. Ils ne couvrent ni l'échec de restauration R1 ni la préférence newsletter d'origine `defaut_creation` décrite en R2. Ajouter ces deux scénarios avec vérification de l'état final, pas seulement du code de retour.

## 4. Sécurité et données

**R2 — Important — `wp/plugins/imagine-site/Personnalisation.php:52` : une préférence newsletter créée par défaut est assimilée à un accord aux envois.** La projection ne vérifie que `choix === true`. Or C22 peut produire cette valeur avec `origine = defaut_creation` ; `Newsletters.php:95` précise : « Ne signifie jamais consentement explicite ou double confirmation Brevo. » Un compte avec email, réponses et consentement de personnalisation devient donc admissible sans avoir lui-même accepté une newsletter. Cela confond les deux consentements distincts exigés par §3.10 et §4.4. Aucun envoi effectif n'existe aujourd'hui, mais le contrat livré au futur connecteur est trop permissif. **Correction proposée :** ne compter qu'une préférence portant un accord explicite reconnu ; exclure `defaut_creation` et les origines inconnues. Tester que cette origine ferme la projection et que l'accord newsletter explicite l'ouvre, toutes les autres conditions étant réunies.

Les contrôles du compte courant, de POST et du nonce sont présents ; les sorties du formulaire sont échappées et les paramètres SQL préparés. Les callbacks de confidentialité ciblent le compte demandé et relisent l'absence des métadonnées après effacement. Aucun secret ou abonné réel identifié dans les fichiers examinés. Aucune nouvelle voie de diffusion du texte réservé relevée.

## 5. Doctrine

Les API natives de réglages, métadonnées et confidentialité sont réutilisées ; les transitions sont isolées en PHP pur. Les espaces de noms, `strict_types` et préfixes Imagine sont présents. Les références officielles sont consignées dans la transmission, sans vérification en ligne durant cette relecture.

**R3 — Mineur — `wp/plugins/imagine-site/PersonnalisationReglages.php:25` : plusieurs instructions et structures sont comprimées sur une ligne, contrairement à PSR-12 imposé par la doctrine §5.** **Correction proposée :** mettre les quatre nouvelles classes au format PSR-12, notamment les blocs conditionnels, boucles et méthodes, sans changement fonctionnel.

**R4 — Mineur — `wp/plugins/imagine-site/README.md:1` : le README de l'extension ne documente pas C-24.** Les réglages et commandes existent seulement dans la transmission de production. **Correction proposée :** ajouter au README une entrée C-24 avec les options, les deux métadonnées, les accroches et les commandes de tests, en distinguant le contrôle local des parcours nécessitant le site de démonstration.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.**

- **Bloquant :** aucun relevé.
- **Important :** R1, restauration impossible après retrait en cas d'échec du journal ; R2, admissibilité des attributs fondée sur une inscription par défaut sans accord newsletter explicite.
- **Mineur :** R3, format PSR-12 ; R4, documentation du README.

Ce verdict n'est pas un GO. Le rejeu PHP indépendant reste non obtenu à cause du refus d'accès à WSL.
