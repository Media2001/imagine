# Relecture Codex — C-22

26 novembre 2026. Relecture indépendante du brief, des §3.10 et §4.2 du cahier des charges, des décisions, de la production et du code actuel. Aucun accès au site, à une base ou à un compte ; aucune lecture de la relecture Claude. Seul ce rapport est écrit.

## 1. Conformité

Le périmètre demandé est présent : catalogue administrable dans C-10, choix datés dans le compte, page publique et emplacement Brevo, défaut fermé, exclusion des comptes sans email, inventaire C-21 étendu. Aucun transport ni persona ajouté. Les trois lettres fictives sont des données. Les livrables `A-VOIR.md` et `PRET` sont présents. Réserves ci-dessous sur la stabilité des identifiants et la vérification des fichiers partagés.

### Pour Imagine

**Question métier fermée : souhaitez-vous activer l'inscription à la principale dès la création du compte, sous condition d'un consentement explicite recueilli à cet instant ? Oui / Non.** Défaut prudent : **Non**, `imagine_newsletters_creation=non`. L'origine `defaut_creation` ne constitue pas une preuve de consentement. Le mécanisme de recueil devra être précisé avant une activation destinée aux envois.

## 2. Exactitude métier

Cas déroulés manuellement dans le code, sans exécution WordPress :

- **Choisir puis retirer une newsletter (§3.10)** : un compte admissible sans préférences commence décoché ; l'enregistrement produit un état daté d'origine `lecteur`. Une sauvegarde identique conserve sa date ; décocher produit un état faux avec la nouvelle date. Le rendu relit cette méta. Comportement conforme.
- **Ajouter une quatrième lettre (§3.10)** : un identifiant inédit accepté dans les réglages apparaît dans les deux rendus, sans choix préexistant ; son retrait conserve l'historique pour C-21. Comportement conforme pour un identifiant effectivement inédit.
- **Compte sans email (§4.2)** : le marqueur ferme l'admissibilité, le formulaire et l'inscription à la création ; une phrase remplace la rubrique. Les captures fournies concordent avec ce comportement.

**C22-01 — Important — `wp/plugins/imagine-site/NewslettersReglages.php:70`.** La validation ne contrôle l'unicité que dans le catalogue courant ; elle accepte un identifiant déjà retiré. Scénario : le lecteur choisit `autre`, l'administrateur retire cette lettre puis ajoute une nouvelle lettre avec ce même identifiant. Le rendu reprend alors l'ancien `choix=true`, sa date et son origine pour la nouvelle lettre, sans action du lecteur. L'avertissement « Ne pas réutiliser » n'empêche pas cette réattribution. **Correction proposée :** réserver durablement les identifiants retirés et refuser leur recyclage dans le réglage, tout en conservant les historiques exportables/effaçables. Ajouter un test retrait puis réutilisation avec un ancien choix positif.

**C22-02 — Mineur — `wp/plugins/imagine-site/NewslettersRegles.php:48`.** `strlen` limite les textes en octets, alors que les champs HTML autorisent 150/500 caractères. Un titre de 100 caractères `é` est saisissable mais rejeté comme dépassant 150 ; même divergence pour une présentation accentuée. **Correction proposée :** compter les caractères UTF-8 et tester les bornes avec accents, en accord avec le formulaire.

## 3. Tests

Le lancement local ciblé `NewslettersReglesTest` a été tenté via le lanceur C22, avec son écriture de reçu remplacée en mémoire par une sortie console. Il échoue avant PHPUnit : `wsl.exe -d Ubuntu -- wslpath …` retourne **4294967295**. Aucun PHP/PHPUnit disponible dans le PATH. Les cinq tests PHP du lot ne sont donc **pas rejoués avec succès** par cette relecture.

Les fonctions locales `check_receipts()` et `shared()` du vérificateur ont été exécutées isolément, sans importer ses accès au site et sans écrire de fichier :

- `check_receipts()` : succès. Les reçus déclarent T01 **1 102 tests / 34 454 assertions**, natif **19 contrôles**, HTTP **33 contrôles**. Ce sont les résultats fournis, pas une nouvelle exécution de ces recettes.
- Manifeste : **25 empreintes sur 25 conformes**.
- `shared()` : **échec reproductible ligne 42**.

**C22-03 — Important — `wp/tests/demo/c22-verifier.py:42`.** Le contrat exige la chaîne littérale `'imagine_newsletters_preferences'`, puis une déclaration exacte de `META`. Le code actuel de confidentialité utilise correctement `Newsletters::META` et `SansEmail::META`. Le vérificateur annoncé dans `PRET` échoue donc sur une évolution équivalente du fichier partagé. **Correction proposée :** vérifier les valeurs et le comportement de l'inventaire plutôt que sa syntaxe littérale, puis rejouer le contrat sur les sources actuelles en conservant les reçus historiques.

Les tests purs couvrent les transitions nominales, l'origine, les doublons et les identifiants inconnus ; ils ne couvrent pas C22-01/C22-02. Les recettes distantes ne sont pas lancées : elles nécessitent des accès et des écritures interdits au relecteur.

## 4. Sécurité et données

Contrôles présents : identité issue de la session, comparaison du titulaire, nonce lié au compte, refus des choix inconnus, version du formulaire, verrou utilisateur, requêtes préparées et sorties échappées. Aucun appel Brevo ni email dans le raccord examiné. C-21 inclut bien la méta, y compris les anciennes lettres, dans l'export et l'effacement. Aucun secret ni donnée réelle relevé dans les fichiers examinés. Pas de modification du paywall dans ce lot. C22-01 reste une réserve sur l'attribution des choix.

## 5. Doctrine

Règles pures séparées du raccord WordPress ; Settings API, compte WooCommerce et outils natifs de confidentialité réemployés. Préfixes, espace de noms, typage strict et README présents. Les sources officielles sont référencées dans la production ; leurs reçus contiennent surtout l'en-tête HTML, sans démonstration détaillée. Pas de consultation externe pendant cette relecture. Les captures restent un squelette, sans validation visuelle de ma part.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun identifié.
- **Important :** C22-01, réattribution d'un ancien choix par recyclage d'identifiant ; C22-03, vérificateur incompatible avec le fichier partagé actuel.
- **Mineur :** C22-02, limites de longueur incohérentes pour les textes accentués.

Limite de validation : exécution PHPUnit empêchée par l'environnement WSL ; recettes sur site non rejouées conformément au rôle.
