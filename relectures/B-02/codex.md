# Relecture indépendante Codex — B-02

Date : 25 novembre 2026. Périmètre : `briefs/B-02-mon-compte.md`, `production/B-02/`, code et recettes B-02 dans `wp/`, dépendances nécessaires à leur compréhension. Doctrine, grille, décisions et paragraphes du cahier des charges lus. `relectures/B-02/claude.md` n’a pas été consulté.

## 1. Conformité

Les cinq rubriques sont présentes dans le gabarit. La connexion, les routes de gestion et le formulaire d’adresse réutilisent WooCommerce/Subscriptions. Les liens PDF passent par C-11/C-14. Les documents et le compteur non raccordés sont explicitement nommés, ce que permet le brief pour les données indisponibles.

Le renvoi du brief au §3.10 est erroné : ce paragraphe concerne les newsletters. Le compte client relève du §3.7 et les numéros du §3.5. Cette divergence est déjà signalée dans la production ; je retiens les cinq rubriques explicitement demandées, sans ajouter à ce lot un centre Brevo.

`PRET` existe désormais et signifie « prêt à relire avec réserves ». Sa présence n’est pas une affirmation de recette complète. `A-VOIR.md` et `PRET` désignent A-SEPA4 comme remplacement du nom erroné a-4x-j45. L’absence de cet ancien identifiant n’est donc pas un défaut fonctionnel à corriger. Les limites sur les bénéficiaires offerts/groupés restent celles des profils disponibles, conformément à `A-FAIRE-2.md`.

**B02-01 — important — Les quatre emplacements disparaissent si le calendrier est indisponible.**

- Localisation : `wp/plugins/imagine-site/MonCompte.php:126`.
- Problème : la détection du paiement trimestriel et la création des quatre lignes sont à l’intérieur du même `try` que la lecture du calendrier et de la date de début. Si la référence postale n’est pas initialisée, `EnvoiNatif::calendrier()` lève une exception ; `echeances` reste vide. Le gabarit affirme alors « Aucun échéancier en quatre fois natif rattaché à ce compte », même pour une souscription dont la périodicité est connue. Le repli fonctionne pour une marge absente, mais pas pour cette autre dépendance indisponible.
- Correction proposée : établir les quatre positions dès que la formule quatre fois est identifiée, puis enrichir séparément les dates et numéros disponibles. Conserver des emplacements nommés en cas de calendrier absent/invalide ou de début inexploitable. Tester ces trois situations sans faire disparaître l’échéancier.

## 2. Exactitude métier

### Cas déroulés à la main

Ces vérifications sont des parcours du code, pas des exécutions PHP.

1. **§3.5, commande du 8 octobre 2026 après clôture du n°170.** Avec le calendrier de l’exemple, `ouvrir(start)` puis `premier()`/`dernier()` sélectionnent les quatre numéros réguliers encore ouverts : 171 à 174. Le résultat de B-02 est cohérent comme projection initiale. Il ne prouve pas une activation ni un nombre restant, et le gabarit le précise.
2. **§3.5, renouvellement en octobre 2027.** Le résultat attendu est 175 à 178. B-02 relit toujours la date initiale `start`, ouvre une année sans précédente et retrouve 171 à 174. Il ne suit pas le renouvellement : voir B02-03.
3. **A-SEPA4 avec deux paiements natifs.** La commande initiale produit « Payée ». Pour les rangs 2, 3 et 4, `$order` vaut systématiquement `null`, même si une commande de renouvellement payée existe. Résultat : une seule ligne payée et trois états non raccordés. C’est aussi le résultat déclaré par les preuves actualisées : voir B02-02.
4. **Bornes temporelles.** À l’instant exact de clôture, `Numero::estCloture()` exclut le numéro du bloc initial ; le moteur conserve la traversée d’année. À la fin exacte d’une grâce, `now < until` devient faux et B-02 affiche « Suspendu » ; à la fin exacte de la souscription, il affiche « Expiré ». Ces comportements sont lisibles dans le code, mais ne sont pas éprouvés à heure fixe par les recettes B-02 fournies.

**B02-02 — important — Le tableau ignore tous les règlements de renouvellement.**

- Localisation : `wp/plugins/imagine-site/MonCompte.php:87`.
- Problème : seul le rang 1 charge une commande ; les trois autres ne peuvent jamais afficher « Payée » ni « Échouée ». Le deuxième paiement d’A-SEPA4 est maintenant disponible dans les objets natifs, comme le constatent `A-VOIR.md` et le reçu complémentaire C-09. Ce n’est plus une donnée absente autorisant un emplacement permanent. La même classe sait déjà parcourir les commandes de renouvellement pour son bandeau d’échec.
- Correction proposée : rattacher les commandes initiales et de renouvellement aux positions du bloc concerné, en contrôlant leur propriétaire et sans compter deux fois une tentative rejouée. Afficher leurs états et montants réels ; afficher les positions futures d’après l’échéancier établi. Si un rattachement reste ambigu, le signaler précisément sans ignorer les autres règlements connus. La recette A-SEPA4 doit montrer deux positions payées sur quatre.

**B02-03 — important — Les numéros affichés restent ceux du premier bloc après renouvellement.**

- Localisation : `wp/plugins/imagine-site/MonCompte.php:131`.
- Problème : `ouvrir($start)` reconstruit exclusivement le premier bloc. Ni le bloc renouvelé ni la relation avec le précédent ne sont utilisés. Une souscription renouvelée conserve donc ses anciens premier/dernier numéros ; l’échéancier projeté reste lui aussi attaché au bloc initial. Le mot « projection » ne résout pas cette erreur de période, illustrée par l’exemple 175–178 du §3.5.
- Correction proposée : raccorder la projection au bloc effectivement consulté, en réutilisant la représentation des renouvellements et `Moteur::renouveler()` ; distinguer les blocs si l’historique est présenté. Faute de raccord fiable, nommer le bloc courant indisponible au lieu de présenter le premier comme celui de l’abonnement actuel. Ajouter le cas complet 171–174 puis 175–178.

**B02-04 — important — Une attente de paiement est présentée comme un virement sans preuve du moyen de paiement.**

- Localisation : `wp/plugins/imagine-site/MonCompte.php:54`.
- Problème : toute souscription `pending` devient « Virement en attente de validation », sans lecture de sa méthode de paiement. Une commande carte non finalisée, ou une méthode absente, reçoit donc une qualification bancaire inventée. La branche `on-hold` avec membership `pending`/`delayed` fait la même inférence. Le §3.6 distingue pourtant le circuit virement des autres paiements.
- Correction proposée : réserver ce libellé au circuit virement identifié par la source native ; afficher une attente de paiement non spécifique lorsque la méthode ne permet pas cette qualification. Tester une attente carte, une attente virement et une méthode inconnue. Cette correction d’affichage ne doit pas modifier les droits d’accès.

## 3. Tests

**Exécution indépendante : aucun succès de test revendiqué.** La tentative locale `php -l wp/plugins/imagine-site/MonCompte.php` a échoué avant analyse : la commande `php` n’est pas disponible dans le shell. Il s’agissait d’un contrôle syntaxique, pas d’une recette fonctionnelle.

Les recettes documentées `wp/outils/demo/b02.py --require-complete`, `b02-runtime.php`, `b02-state.php` et `b02-http.py` nécessitent le site WordPress, ses comptes et sa base. Même sans `--deploy`, le runner téléverse les recettes PHP, écrit des preuves hors du rapport et, en mode HTTP, modifie puis restaure une adresse en conservant des observations. Je ne les ai pas exécutées : `relecteurs/AGENTS.md` autorise seulement les tests locaux et interdit « accéder à un site, à une base ou à un compte » ; le présent mandat interdit aussi toute autre écriture. Aucun accès au site, aucune installation et aucun fichier de test ajouté.

**Preuves fournies, lues mais non reproduites :** les anciens reçus B-02 indiquent 144 contrôles techniques et une sortie stricte 2. Le reçu plus récent `production/C-09/complement-b02-resultats.json` indique 140 contrôles, dont 55 HTTP, sans échec technique, avec acceptation partielle. Ces totaux ne constituent pas deux validations indépendantes de cette relecture.

**B02-05 — important — Le test transforme l’omission du deuxième paiement en résultat attendu.**

- Localisation : `wp/tests/demo/b02-runtime.php:53`.
- Problème : l’assertion exige exactement une occurrence de « Payée », puis vérifie à la ligne suivante que WCS compte deux paiements. La recette reste donc verte avec le défaut B02-02 et rejetterait sa correction. Le contrôle HTTP reprend cette attente d’une seule ligne payée.
- Correction proposée : construire l’attendu depuis le scénario métier fixé, avec deux positions payées identifiées, leurs montants et deux positions futures. Mettre à jour l’attendu HTTP. Compléter par un renouvellement échoué, un règlement régularisé et un rejeu sans double comptage ; conserver les tests d’isolation existants.

**B02-06 — mineur — Les réserves du runner sont codées en dur et déjà périmées.**

- Localisation : `wp/outils/demo/b02.py:83`.
- Problème : `acceptance_blockers` affirme systématiquement l’absence du profil requis, de toute commande échouée et d’un paiement validé A-CARTE. Les documents actualisés et les assertions du complément C-09 constatent l’inverse pour ces trois sujets. Le code strict 2 est déterminé par une liste toujours non vide, non par les capacités effectivement constatées ; le rapport de diagnostic ne permet donc pas de distinguer les anciennes réserves des manques actuels.
- Correction proposée : calculer les réserves depuis les contrôles de réception, employer le profil A-SEPA4 retenu et ne conserver que les manques observés. Dater les anciens reçus comme historiques, sans les réécrire. Une réserve réelle peut continuer à produire une sortie 2.

La couverture existante est utile pour le titulaire, l’anonyme, les identifiants forgés, les nonces et l’aller-retour postal. Elle ne couvre pas la sélection du deuxième bloc, le calendrier indisponible, les méthodes de paiement en attente ni les instants exacts de changement d’état. `b02-state.php` calcule la grâce avec l’heure courante et une condition proche de celle du produit ; cela ne remplace pas des cas temporels fixés.

## 4. Sécurité et données

Aucune fuite intercompte établie par la lecture du raccord B-02 : l’identité provient de la session, les souscriptions et commandes sont recontrôlées, le gabarit vérifie le titulaire. Les sorties variables sont échappées et le compte reçoit des en-têtes privés sans stockage. Le formulaire et ses nonces restent natifs. Les tests fournis incluent des GET/POST avec identifiants étrangers et un nonce invalide ; leur exécution n’a pas été reproduite ici.

Les PDF exposent une route contrôlée, pas le chemin du fichier physique, et leur sélection délègue à C-11/C-14. Aucun nouveau chemin de sortie du texte réservé n’est introduit dans les fichiers B-02 examinés. Cela ne constitue pas une nouvelle validation exhaustive de l’étanchéité des dépendances.

Aucun secret ni donnée d’abonné réel repéré dans les fichiers examinés. Les fichiers d’identifiants mentionnés dans la documentation n’ont pas été ouverts.

## 5. Doctrine

Le choix du standard est respecté pour le compte, les adresses et les commandes. C-01/C-05 sont appelés pour les projections ; les droits PDF restent délégués. Les emplacements sans documents ni historique d’activation sont honnêtement signalés et ne justifient pas de fabriquer ces données.

Les fichiers applicatifs portent `strict_types`, un espace de noms et des appels de traduction. Pour corriger les règles d’état et de sélection des blocs, conserver une projection pure recevant les données et l’heure, avec un adaptateur WordPress mince : cela permettra les tests locaux et les bornes temporelles demandés par la doctrine. La méthode actuelle `etat()` dépend directement de WordPress et de l’heure réelle.

### Décisions techniques, défaut proposé

Aucune question nécessitant l’attente de Ced. Défauts techniques proposés pour les corrections : garder les quatre emplacements en cas de dépendance indisponible ; ne qualifier ni une méthode de paiement ni un bloc courant sans source ; ne jamais changer un paiement ou un droit pour obtenir un affichage attendu. Hermès peut appliquer ces défauts, avec arbitrage technique ultérieur par Claude.

### Pour Imagine

Aucune nouvelle question métier soulevée par cette relecture. La marge C-05 reste un réglage à renseigner selon son contrat ; B-02 ne doit pas lui attribuer une valeur arbitraire. Les documents restent conditionnés au raccord de Step. La validation visuelle demeure à faire sur les maquettes, sans être remplacée par ce rapport.

## 6. Études (lots sans code)

Sans objet : B-02 contient du code. `production/B-02/sources.md` donne deux adresses officielles et décrit la classe native consultée. Ces pages et cette installation n’ont pas été ouvertes par le relecteur ; leurs affirmations restent des sources déclarées par la production, non une vérification externe indépendante.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun défaut de sécurité bloquant démontré dans le périmètre examiné.
- **Important :** B02-01, conservation des quatre lignes quand une dépendance manque ; B02-02, paiements de renouvellement ignorés ; B02-03, premier bloc conservé après renouvellement ; B02-04, virement inféré sans méthode ; B02-05, test qui valide l’omission du deuxième paiement.
- **Mineur :** B02-06, réserves du runner codées en dur et périmées.

Les preuves techniques fournies ne suffisent pas à accepter le tableau quatre fois. Les corrections doivent être accompagnées de recettes dont les attentes expriment le résultat métier, puis d’un rejeu par un exécutant autorisé à accéder à la démonstration.
