# Relecture indépendante — C-19 — Codex

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille de relecture, brief C-19, cahier des charges §3.13 et décisions du dépôt. Lecture du code C19, de ses dépendances C15/C18, des tests, des preuves livrées et de la capture. Aucun accès au site, à une base ou à un compte ; aucun fichier autre que ce rapport modifié. La relecture Claude n’a pas été consultée.

## 1. Conformité

Les quatre familles d’indicateurs, les explications de comptage, les six emplacements « à venir », le menu Imagine et les livrables demandés sont présents. L’écran utilise des tableaux sans script propre. Les interprétations sont signalées : abonnements plutôt que personnes distinctes, fenêtres C15 de 30/90/180 jours, créations et fins natives, mois UTC. Les différences avec C18 sont expliquées. Les indicateurs différés ne reçoivent aucune formule inventée.

**R1 — Important — Le droit annoncé comme dédié ne peut pas être administré indépendamment.** Fichier : `wp/plugins/imagine-site/TableauBordAdmin.php:34`. Le filtre remplace systématiquement `imagine_voir_tableau_bord` par les deux droits C15/C18. Un utilisateur non administrateur possédant ces deux droits reste autorisé même si sa capacité `imagine_voir_tableau_bord` est explicitement fausse ; inversement, lui donner seulement cette capacité ne lui ouvre pas le tableau. Pour donner accès aux seuls nombres, il faut donc aussi attribuer le droit d’extraction et celui de gestion des échéances. Le brief demande un droit dédié, et pas seulement un nom dédié pour la combinaison des droits existants. **Correction proposée :** rendre l’autorisation C19 attribuable et révocable séparément, avec attribution rejouable à e-abo hors du chemin d’affichage. Tester le lecteur du seul tableau et le refus explicite C19 d’un détenteur des droits sources. L’affichage doit rester sans mutation des rôles.

**R3 — Mineur — Les libellés des mesures restent définis hors du fichier de l’indicateur.** Fichier : `wp/plugins/imagine-site/TableauBordAdmin.php:81`. Le `match` central connaît les fenêtres, les mouvements et les moyens de paiement. Un nouvel indicateur peut calculer ses valeurs dans un fichier, mais doit modifier ce rendu pour afficher des libellés métier autres que ses clés techniques. Cela limite la promesse du brief : « pour qu’en ajouter un soit l’affaire d’un fichier ». **Correction proposée :** inclure les libellés des mesures dans chaque définition d’indicateur et rendre l’administration générique ; conserver calcul et phrase dans cette même définition.

## 2. Exactitude métier

Cas déroulés manuellement à partir du §3.13 et des règles réemployées ; il s’agit d’une vérification du code, pas d’une exécution PHP réussie :

- **Actifs par moyen de paiement :** deux lignes Actif, l’une par virement et l’autre sans méthode, plus une ligne Suspendu et une ligne En délai de grâce sur mandat papier. Résultat attendu et obtenu par lecture : total 2, virement 1, inconnu 1. La grâce n’est pas réinterprétée en actif. Cas présent dans `TableauBordReglesTest.php:89`.
- **Paiements échoués :** quatre commandes, respectivement failed impayée sans date payée, failed déjà payée, failed avec date payée, pending impayée. Attendu et obtenu par lecture : 1. La sélection est effectivement celle de C15, sans nouvelle règle de retard.
- **Mois civil et changement d’année :** au 1er janvier 2027 à 00:00 UTC, une création au 31 décembre à 23:59:59 est exclue ; une création exactement à minuit est incluse. Une fin expired à minuit est incluse, une fin pending-cancel à minuit ne l’est pas, une fin future non plus. Le calcul de `mouvements.php:10` donne ces résultats. Le test livré couvre les bornes d’un mois de novembre, mais pas explicitement le passage d’année.

**R2 — Important — La double sélection temporelle peut perdre une échéance valide à 180 jours.** Fichier : `wp/plugins/imagine-site/TableauBordNatives.php:15`. L’adaptateur récupère une liste déjà filtrée à 180 jours par C15 à son propre `time()`, puis attend la lecture des échecs et des mouvements avant de fixer `maintenant` ligne 26. Le calcul pur filtre de nouveau cette liste avec ce second instant. Contre-exemple sans changement des données : à l’instant T, un abonnement actif dont le prochain paiement vaut T + 180 jours + 1 seconde, sans date de fin, est éliminé par la première sélection. Si le calcul intervient à T + 2 secondes, cet abonnement appartient désormais à la fenêtre C15 de 180 jours, mais C19 ne peut plus le retrouver : 0 au lieu de 1. Les lectures natives intermédiaires rendent ce décalage possible. **Correction proposée :** partager un instant de référence unique entre la sélection native et les trois calculs, ou transmettre les lignes non filtrées temporellement au moteur commun. Ajouter un test d’adaptateur avec horloge contrôlée et borne supérieure franchie pendant la lecture ; ne pas dupliquer la règle C15.

## 3. Tests

**Rejoué ici :** `python -B wp/tests/demo/test_c19_contract.py` : **2 tests réussis**, sans génération de bytecode ni reçu.

**Tenté ici, non exécuté :** les tests `TableauBordReglesTest` via l’image existante `imagine-tests-t01:1`, montage de `wp/` en lecture seule, réseau désactivé et PHPUnit sans cache de résultat. La commande WSL échoue avant le démarrage de PHPUnit : **`Wsl/Service/E_ACCESSDENIED`**, code de sortie 1. Aucun PHP ni Docker natif n’a été trouvé dans le PATH. Ce blocage d’environnement n’est pas un échec des assertions du lot.

Le lanceur `c19-verifier.py` n’a pas été exécuté : il accède au site, réécrit des reçus et téléverse la sonde runtime, ce qui dépasse les droits de cette relecture. Aucun test HTTP, navigateur ou natif WordPress n’a donc été rejoué ici.

**Preuves livrées, examinées mais non rejouées :** PHP C19 6 tests/32 assertions ; paquet site 104/555 ; canonique 1 068/34 303 ; 18 contrôles natifs et 28 HTTP/navigateur, tous déclarés réussis. Les tests purs ont des attentes chiffrées indépendantes en plus des comparaisons au moteur partagé. Ils couvrent vide, méthode inconnue, grâce exclue, bornes inclusives, fin future, création distincte du début contractuel et paiements déjà réglés. Ils ne couvrent pas la double horloge R2. La révocation testée retire un droit source, et ne démontre pas une révocation indépendante du droit C19 (R1).

**R4 — Mineur — Une empreinte du reçu final ne correspond plus au fichier livré.** Fichier : `production/C-19/final-V2.json`, entrée exacte `source_sha256["wp/plugins/imagine-site/README.md"]`. Parmi les 17 empreintes recalculées, les 16 autres concordent ; celle du README diffère, même après normalisation CRLF vers LF. Le reçu annonce `2bdc71aeb9427bb5263d3ba23d109d7446cd8f0eecf6fa51723d01bd0005f6e9`, contre `638da75e9e5e36372ab40d07c66b708ff27a5698165171e4c788af8d2bf40150` après normalisation du fichier actuel. **Correction proposée :** documenter la modification du README dans un reçu successeur, ou rétablir les octets attendus si la modification est involontaire. Préserver les preuves historiques ; ne pas simplement remplacer leur empreinte. Cet écart documentaire ne démontre pas une dérive du PHP testé, dont les empreintes concordent.

## 4. Sécurité et données

Contrôles d’autorisation avant rendu et lors de l’accès administratif, refus des méthodes autres que GET/HEAD, échappement des titres, phrases, clés et nombres : présents. Aucun formulaire ni action d’écriture C19 nécessitant un nonce. Aucune requête SQL libre ajoutée par C19 ; lecture par les adaptateurs natifs existants. Aucun secret ni identité réelle relevé dans les fichiers examinés. La sortie métier contient des nombres ; l’identité fictive de l’opérateur demeure dans la barre native WordPress. Le lot ne crée pas de voie d’accès au texte réservé.

Réserve d’autorisation : R1. Aucune fuite vers un visiteur anonyme n’est établie par cette revue.

La preuve de lecture seule est limitée explicitement dans `production/C-19/A-VOIR.md:51` : trois options volatiles et les sessions sont exclues des comparaisons HTTP. Les reçus prouvent donc l’invariance des données protégées et l’absence d’écriture propre au calcul/rendu C19, pas l’identité intégrale de la base après une requête WordPress complète. Cet écart à la formulation littérale du brief est déclaré ; je ne certifie pas ici une base intégralement inchangée.

## 5. Doctrine

Logique pure séparée des raccords WordPress, types stricts, espace de noms des classes, préfixes de capacités, README et textes français : présents. Les textes du rendu passent par les fonctions de traduction. La production cite les documentations officielles WordPress/WooCommerce pour justifier le raccord sur mesure et les notions de création/fin ; aucune consultation externe n’a été effectuée, conformément au rôle de relecteur.

Les corrections R1/R2/R3 sont techniques. Défaut proposé : permission C19 indépendante, instant unique transmis au moteur partagé, métadonnées de présentation portées par l’indicateur. Elles ne nécessitent pas de question à Ced. La capture a été examinée pour sa conformité au brief ; la validation visuelle reste à Ced et n’est pas accordée par ce rapport.

## 6. Études (lots sans code)

Sans objet : lot avec code. Les références documentaires livrées ne sont pas présentées comme des sources vérifiées en ligne pendant cette relecture.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun établi.
- **Important :** R1, permission C19 non indépendante ; R2, sous-comptage possible à la borne de 180 jours.
- **Mineur :** R3, libellés des mesures centralisés hors des indicateurs ; R4, empreinte documentaire finale divergente.

Limite de validation : les deux tests Python passent ; le rejeu PHP indépendant est empêché par le refus WSL. Les résultats PHP et d’intégration cités restent ceux de la livraison.
