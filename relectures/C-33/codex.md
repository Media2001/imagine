# Relecture indépendante Codex — C-33

Date : 28 novembre 2026. Références lues : `relecteurs/AGENTS.md`, doctrine, grille, brief C-33, cahier des charges §3.3 et §4.4, décisions, code et preuves du lot. Le rapport de Claude n’a pas été lu. Aucun site, compte ou base n’a été consulté ; aucune correction de production effectuée.

## 1. Conformité

Les livrables demandés sont présents : code, tests, cinq lignes de sources officielles dans le README, trois adresses dans `A-VOIR.md`, preuves et `PRET`. Les fermetures passent par les hooks natifs, sans règle de serveur. La signature réutilise la métadonnée B-16. La limitation des connexions et la double authentification restent hors périmètre.

Le traitement est explicitement limité aux anonymes ; les branches des utilisateurs connectés conservent les résultats natifs. L’activation temporaire du sitemap pour la recette, puis sa restauration, est documentée. Les identifiants numériques présents dans les objets REST `posts` sont explicitement exclus de la promesse du README.

La preuve d’absence dans tous les en-têtes et celle du champ auteur des flux sont toutefois insuffisantes : points I1 et I2 ci-dessous.

## 2. Exactitude métier

Cas déroulés manuellement à partir du code et comparés aux réponses archivées :

| Cas | Résultat attendu | Résultat constaté |
|---|---|---|
| Article avec signature B-16, visiteur anonyme | Signature journalistique dans les flux et l’oEmbed, sans adresse du compte | RSS2 : `dc:creator` signé ; Atom : `author/name` signé, sans URI ; oEmbed : `author_name` signé, sans `author_url`. Conforme sur les réponses fournies. |
| Même article sans signature | Nom du site, aucun repli sur le compte de saisie | La règle pure renvoie le site ; les réponses `rss2-repli` et `oembed-repli` correspondent. Conforme sur ces réponses. |
| Administrateur puis éditeur utilisant REST | Sélecteur d’auteur et lecture d’édition conservés | Le code restitue le résultat natif aux connectés ; les preuves enregistrent les deux parcours réussis. Non rejoués sur site par le relecteur. |

La règle pure couvre les signatures vides, non textuelles et entourées d’espaces. Les preuves natives couvrent `]]>` en RSS2 et l’échappement XML en Atom. Les dates de clôture et changements d’année ne concernent pas ce lot.

## 3. Tests

Exécutions effectuées sans écriture de fichier de test :

- `python -B production/C-33/verifier.py` : **PASS**, code de sortie 0. Ce contrôle vérifie les empreintes et les preuves archivées ; il ne rejoue pas WordPress. Les archives comptent 14 contrôles natifs, 53 contrôles navigateur, 19 réponses et 6 mutations.
- Test PHPUnit ciblé sur `ComptesPublicsC33Test.php`, tenté dans l’image locale `imagine-tests-t01:1`, réseau coupé, dépôt monté en lecture seule et cache PHPUnit désactivé : **non exécuté**, démarrage WSL refusé avec `Wsl/Service/E_ACCESSDENIED`. PHP/PHPUnit ne sont pas disponibles directement dans le PATH.
- Deux contre-épreuves Python en mémoire, utilisant la fonction `control()` extraite du banc et une réponse RSS2 archivée : les faux positifs décrits ci-dessous sont reproduits.

Le total de **1 229 tests / 36 926 assertions**, ainsi que les **23 outils / 852 contrôles**, provient du rejeu fourni par le producteur, pas d’un nouveau rejeu indépendant. Son incident `A-33 VERIFIER_TIMEOUT` est conservé et signalé ; il ne constitue pas un défaut fonctionnel C-33 démontré.

Les recettes natives, navigateur et `--live` n’ont pas été exécutées : `relecteurs/AGENTS.md`, rubrique Droits, interdit « accéder à un site, à une base ou à un compte ». Leur lancement dépasserait également la contrainte d’écriture limitée à ce rapport.

**I1 — important — `wp/outils/demo/c33-browser.py:57` : les en-têtes sont filtrés avant le contrôle d’absence.**

Seuls `location`, `content-type` et `link` arrivent au contrôleur et dans les preuves. Une identité présente dans un autre en-tête échappe donc à la vérification demandée par le brief. Contre-épreuve : ajout de l’identifiant fictif dans `X-Account` ; après la sélection exacte du banc, `control()` renvoie encore `ok=true`, tandis qu’il refuse les en-têtes complets. Le contrôle d’absence de `set-cookie` dans `production/C-33/verifier.py:24` porte aussi sur une donnée déjà exclue en amont.

Correction proposée : contrôler l’intégralité des noms et valeurs d’en-têtes reçus avant toute sélection ou occultation pour archivage ; conserver les résultats de ces contrôles sans enregistrer de jeton sensible. Ajouter une mutation d’en-tête hors des trois noms actuels et exiger son rejet. Aucune fuite réelle dans un en-tête omis n’est affirmée ici : c’est la preuve qui est incomplète.

**I2 — important — `wp/outils/demo/c33-browser.py:34` : la présence de la signature est recherchée dans tout le document, pas dans son auteur.**

Le nom du site figure déjà ailleurs dans un flux, notamment dans ses adresses et métadonnées. Sur la réponse réelle `browser-final-V2-rss2-repli.txt`, supprimer en mémoire l’élément `dc:creator` entier laisse le contrôleur au vert (`ok=true`, `present=true`, `leak=false`). Le banc ne prouve donc pas le repli demandé dans le champ auteur. La mutation existante, qui réintroduit le nom du compte, ne détecte pas ce défaut distinct.

Correction proposée : repérer l’élément correspondant à l’article témoin et comparer exactement son `dc:creator` RSS2 ou son `author/name` Atom à la signature attendue, après décodage XML. Vérifier séparément l’absence d’adresse de compte. Ajouter une mutation supprimant le champ auteur et couvrir le repli Atom également.

## 4. Sécurité et données

Aucun secret ni donnée personnelle réelle identifié dans les fichiers C-33 examinés. Les témoins sont explicitement fictifs, avec adresses `@example.org`. Les preuves finales déclarent le compte et l’article supprimés, la sonde retirée et l’état restauré ; leur intégrité locale est vérifiée.

Les hooks livrés n’ajoutent ni écriture en base ni formulaire et n’étendent pas les droits REST. Les réponses de flux et d’oEmbed examinées conservent le bloc d’abonnement, sans texte réservé. La limite de contrôle des en-têtes est décrite en I1.

Le sitemap archivé contient `post`, `page`, `product`, `imagine_numero`, `imagine_evenement`, `imagine_partenaire`, ainsi que les taxonomies `category`, `product_cat` et `imagine_thematique`. Aucun type de message de visiteur, de contact ou de pièce privée n’apparaît dans cet index. Aucun autre sitemap n’a été corrigé.

## 5. Doctrine

Les classes livrées utilisent `declare(strict_types=1)`, l’espace de noms `Imagine\Site`, des hooks WordPress et une règle pure distincte de l’adaptateur. Le message REST est traduisible. La métadonnée existante B-16 est réutilisée ; aucune modification de code tiers n’est introduite. Le README expose le périmètre et les limites des preuves.

Les corrections I1 et I2 sont techniques et peuvent être appliquées sans arbitrage métier ni intervention sur le réel.

## 6. Études (lots sans code)

Sans objet : lot avec code. Les cinq liens officiels sont présents dans le README et leurs empreintes figurent dans `standard-V2.json`. Leur consultation distante n’a pas été renouvelée, conformément aux droits du relecteur.

## Verdict

**À corriger.** Les réponses nominales fournies sont cohérentes avec le brief, mais deux contre-épreuves démontrent des lacunes dans la preuve automatisée exigée.

- **Bloquant :** aucun défaut de ce niveau établi.
- **Important : I1**, contrôler tous les en-têtes avant leur éventuelle occultation.
- **Important : I2**, contrôler la valeur du champ auteur de chaque flux témoin et détecter sa suppression.
- **Mineur :** aucun point supplémentaire retenu.

Ce verdict n’est pas un GO.
