# Relecture indépendante Codex — C-10

Date : 23 novembre 2026. Périmètre : brief C-10, production C-10, façade administrative, adaptateurs réutilisés, raccord existant et tests correspondants dans `wp/`. Références : doctrine, décisions et arbitrages du 22 novembre, cahier des charges §§3.4, 3.5, 3.9 et 3.13. Le brief ne cite pas directement de paragraphe du cahier des charges ; ces sections correspondent aux domaines examinés.

Le rapport de l’autre relecteur n’a pas été lu. Aucun accès à un site, une base ou un compte ; aucune installation. Seul ce rapport est écrit.

## 1. Conformité

Les éléments attendus sont présents : menu Imagine, page Réglages, trois domaines, huit champs, explications françaises, défauts et mentions de confirmation, groupe Settings API commun, aperçu CSV, journal, `A-VOIR.md` et `PRET`. Le formulaire réutilise les trois adaptateurs sans recopier leurs moteurs. L’enregistrement indépendant des domaines est une interprétation explicitement documentée ; le brief n’impose pas de transaction globale.

**C10-01 — Important — L’écran présente comme effectifs des réglages d’accès qui ne sont pas raccordés.**

- **Fichier et ligne :** `wp/plugins/imagine-pilotage/src/Administration/Reglages.php:150`.
- **Problème :** l’explication « L’autre choix autorise seulement l’équipe » accompagne un choix enregistrable, sans préciser que ce choix reste sans effet sur le paywall actuel. La livraison reconnaît cette limite dans ses notes, et la lecture du raccord confirme que l’option enregistrée n’est pas transmise au moteur. Un administrateur peut donc enregistrer « Ouvert à l’équipe uniquement », constater un succès et croire ce comportement actif. La mention « À confirmer par Imagine » décrit une décision métier provisoire, pas une absence de raccordement.
- **Correction proposée :** indiquer directement dans la section Accès que les valeurs sont conservées pour le branchement futur et ne modifient pas encore les accès du site de démonstration ; distinguer clairement l’effet métier prévu de l’effet actuellement disponible. Ajouter une assertion sur ce texte. Cela reste une correction de l’écran, sans imposer ici une nouvelle livraison du paywall ou des PDF.

L’effet choisi pour la réception est bien le format C07 : le brief autorise un exemple autre que l’accès à un article. L’aperçu appelle réellement l’exporteur, mais ne constitue pas une preuve d’expédition postale. L’absence de capture authentifiée et l’attente de validation visuelle sont déclarées.

## 2. Exactitude métier

Cas déroulés manuellement par lecture des appels et des branches, sans prétendre à une exécution PHP :

1. **Paiement en quatre fois, §§3.4–3.5 et arbitrage du 22 novembre.** Avec les défauts, la marge vide devient `null` et le planificateur refuse de planifier : aucune durée n’est inventée. Avec une marge de trois jours, une commande le 30 décembre 2026 à 10 h et une confirmation SEPA le 31 décembre à 10 h donnent, en mode `avec_marge`, une disponibilité le 2 janvier 2027 à 10 h, heure de Bruxelles. Le mode `sans_marge` retient le 31 décembre ; une confirmation absente reste absente. L’explication de l’écran correspond au calcul de la bibliothèque, y compris au changement d’année.
2. **Droits PDF, §3.9 précisé par l’arbitrage C-06.** Pour un abonnement actif commencé le 8 octobre 2026 et un PDF paru le 5 octobre, le moteur refuse au titre de l’abonnement avec `pdf_anterieur_abonnement=ferme`, et autorise avec `ouvert`. Si la sortie coïncide exactement avec le début, le test strict « sortie antérieure au début » ne s’applique pas. La façade accepte les deux valeurs et rejette une valeur inconnue. Cela vérifie la cohérence de la configuration avec le moteur, pas son raccordement au téléchargement sur le site.
3. **Liste d’envoi, §3.13 et arbitrage C-07.** La sélection `ville`, `destinataire`, `pays` conserve cet ordre et produit l’en-tête `ville,destinataire,pays`, sans recalculer les destinataires. Une liste contenant deux fois `ville` est refusée ; l’adaptateur restitue le format antérieur. L’aperçu est une ligne explicitement fictive. Les règles de clôture et de sélection des abonnés restent dans les bibliothèques existantes.

Pas de nouvelle interprétation métier non déclarée repérée dans les valeurs proposées. Les limites de raccordement doivent toutefois être visibles dans le produit lui-même : C10-01.

## 3. Tests

**Exécuté localement :**

```text
python -B -m unittest discover -s wp/tests/demo -p test_c10_scope.py -v
4 tests exécutés — OK — aucun échec ni saut.
```

Ces quatre tests vérifient les gardes du déploiement avec transports simulés, pas les droits WordPress, le nonce ou la persistance. Le mode `-B` évite de créer des fichiers de cache Python.

Un contrôle local en mémoire compare aussi les six empreintes SHA-256 de `verification-finale.json` aux cinq fichiers PHP applicatifs et à `c10-runtime.php` : **six correspondances, aucun écart**. Cela rattache les preuves fournies aux sources présentes ; ce n’est pas une nouvelle vérification du site.

Une tentative de cas PHP local a échoué avant exécution : **commande `php` introuvable**. Aucun résultat PHP indépendant, PHPUnit ou PHP_CodeSniffer n’est donc revendiqué.

**Preuves livrées, lues mais non rejouées :** 13 contrôles WordPress, 79 contrôles HTTP dont 23 soumissions invalides, et 30 contrôles C08 déclarés réussis. Les scénarios vérifient notamment les rôles, les nonces, les valeurs alternatives, la conservation de valeurs non standard, les événements avant/après et les réenregistrements identiques. Ces assertions portent sur des résultats utiles et ne se limitent pas à répéter les constantes du code.

Les commandes `c10.py`, `c10-verifier.py` et `c10-final.py` accèdent au site et/ou écrivent d’autres fichiers. Elles n’ont pas été exécutées : `relecteurs/AGENTS.md` interdit « accéder à un site, à une base ou à un compte », et la demande limite l’écriture au présent rapport. La recette PHP exige elle-même un environnement WordPress de démonstration.

**C10-02 — Mineur — Les tests de forme ne distinguent pas une clé supplémentaire d’un tableau incomplet.**

- **Fichier et ligne :** `wp/tests/demo/c10-verifier.py:163`.
- **Problème :** les trois formes testées sont une chaîne, un tableau vide et un tableau contenant uniquement `extra`. Ce dernier manque aussi de toutes les clés attendues : il ne prouve pas le refus d’une clé supplémentaire lorsque toutes les clés obligatoires sont présentes. La livraison annonce pourtant une couverture des clés surnuméraires. Une validation relâchée sur les seules clés supplémentaires pourrait passer cette suite.
- **Correction proposée :** partir d’un domaine valide, lui ajouter une seule clé inconnue, puis vérifier le refus, la conservation exacte de la valeur et l’absence d’événement. Tester séparément le retrait d’une seule clé obligatoire.

Autres limites de couverture observées : aucune injection d’échec d’écriture du journal ; pas de scénario associant un domaine invalide à un autre domaine réellement modifié dans la même soumission. Les refus actuels laissent les autres domaines inchangés et ne prouvent donc pas ce dernier comportement annoncé.

## 4. Sécurité et données

À la lecture : capacité `manage_options` sur le menu et la page, capacité explicite du groupe Settings API, formulaire vers `options.php` avec `settings_fields`, validation stricte des choix et des clés Accès/Paiement, validation du format C07, options non exposées en REST. Les sorties HTML, attributs et cellules du journal sont échappés ; la recherche du journal utilise `esc_like` et une requête préparée. Aucun secret ni donnée d’abonné réel repéré dans les fichiers du lot examinés. Les fichiers d’identifiants hors dépôt n’ont pas été ouverts.

**C10-03 — Important — Un échec d’écriture du journal est ignoré après la modification du réglage.**

- **Fichier et ligne :** `wp/plugins/imagine-pilotage/src/Administration/Reglages.php:121`.
- **Problème :** le retour de `add_option()` n’est jamais contrôlé. Si l’option métier est enregistrée mais que l’insertion de l’événement échoue, le traitement termine normalement : la modification persiste sans trace et sans avertissement. Un nouvel enregistrement de la même valeur ne répare rien, puisqu’il ne déclenche plus de changement. L’exigence « chaque modification est journalisée » n’est donc pas assurée dans ce cas d’échec. Constat statique ; panne non injectée ici.
- **Correction proposée :** contrôler la persistance de l’événement et définir un traitement explicite de l’échec, avec signalement à l’administrateur et mécanisme permettant de conserver ou reprendre l’événement manquant. Ne pas présenter l’opération comme entièrement réussie quand la trace obligatoire manque. Ajouter un test où l’écriture métier réussit et celle du journal échoue.

Le choix d’un événement distinct non autoloadé évite de réécrire tout l’historique à chaque changement. La limite d’affichage à 50 ne supprime pas les anciennes entrées. Le lot n’ajoute pas de restitution publique de contenu réservé ; la non-régression HTTP du paywall reste une preuve fournie, non rejouée par cette relecture.

## 5. Doctrine

Le choix du standard WordPress est adapté : Settings API, menu natif, nonce natif, aucun traitement bancaire ou moteur métier supplémentaire. Les références officielles figurent dans la livraison ; elles n’ont pas été consultées en ligne pendant cette relecture. Le décalage entre leur consultation réseau et le premier squelette est reconnu dans les notes. Les sources PHP examinées déclarent les types stricts et emploient le namespace Imagine.

**C10-04 — Mineur — La nouvelle façade ne respecte pas PSR-12.**

- **Fichier et ligne :** `wp/plugins/imagine-pilotage/src/Administration/Reglages.php:45`.
- **Problème :** cet appel répartit ses arguments sur plusieurs lignes tout en conservant plusieurs arguments sur la première ligne et la parenthèse fermante après le dernier argument. Ce format contrevient à la règle PSR-12 des listes d’arguments multilignes. Le même style revient dans la façade. Le script `composer lint` couvre `src`, mais les preuves C10 ne comportent pas ce contrôle ; le parsing PHP ne le remplace pas.
- **Correction proposée :** reformater la façade selon PSR-12, puis exécuter le lint prévu par le projet dans son environnement autorisé et conserver son résultat. Aucun changement des moteurs n’est nécessaire.

Les bibliothèques restent séparées de WordPress. Sans historique Git exécuté ni comparaison indépendante avec un état antérieur des lots clos, je ne certifie pas leur immutabilité historique ; la liste de déploiement C10 et les empreintes livrées sont cohérentes avec le périmètre annoncé.

## 6. Études (lots sans code)

Sans objet : lot de code et d’interface administrative. La liste de sources est un appui au choix technique, pas une étude autonome d’extensions.

## Verdict

**À corriger.**

- **Bloquant :** aucun point classé bloquant identifié dans le périmètre examiné.
- **Important :** C10-01, signaler dans l’écran les réglages d’accès encore sans effet ; C10-03, traiter l’échec de persistance du journal.
- **Mineur :** C10-02, isoler le test des clés surnuméraires ; C10-04, respecter PSR-12 et produire le lint correspondant.

Ce verdict n’est pas un GO. Il ne vaut ni validation visuelle ni confirmation indépendante des tests exécutés sur le site.
