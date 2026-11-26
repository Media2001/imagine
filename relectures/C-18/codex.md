# Relecture indépendante Codex — C-18

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief C-18, cahier des charges §3.13 et décisions du dépôt. Lecture du code, des tests et des preuves locales ; aucun accès au site, à une base ou à un compte. Le rapport de Claude n’a pas été consulté.

## 1. Conformité

Les quatre extractions demandées sont présentes sous Imagine, avec filtres, comptage avant téléchargement et CSV. Âge et étiquette sont désactivés. Le catalogue rassemble colonnes, filtres, requête et prédicat dans un fichier par extraction. Les règles pures sont séparées de WordPress. `A-VOIR.md`, `PRET` et le rapport court `files/rapports/2026-11-26-02h04-V2.md` sont livrés.

Les interprétations sont explicites : une ligne par abonnement, tous états, livraison de la souscription, identité du titulaire, échéance égale au minimum prochain paiement/fin, bornes UTC inclusives. Les limites des modes fictifs et des bénéficiaires non raccordés sont signalées. Le rattachement au §3.13 figure dans la documentation de livraison.

- **C18-01 — mineur — `production/C-18/A-VOIR.md:69`.** « C09 natif reste 381/382 » est présenté comme une limite courante, alors que le reçu successeur `verification-successeur-20261126T012310784456-V2.json` annonce 382/382 et que le rapport du 26 novembre à 02 h 24 documente la restauration ciblée. Le document d’entrée ne distingue donc plus correctement l’état historique de l’état courant. **Correction proposée :** ajouter une mise à jour datée renvoyant au reçu successeur, en conservant explicitement les anciennes preuves et leurs résultats historiques.

## 2. Exactitude métier

Cas déroulés à la main et comparés aux règles et aux CSV enregistrés :

1. **Localité (§3.13).** Avec pays `FR`, le prédicat exclut les lignes `BE`. Le CSV France contient A-ETRANGER et le témoin C13 français ; A-ETRANGER est bien le seul profil C09. Avec `BE` et code postal `1000`, une ligne `FR/1000` ou `BE/10000` est exclue : la comparaison est exacte, sans préfixe implicite.
2. **Échéance (§3.13).** Pour la période du 26 novembre au 26 décembre 2026, A-ECHEANCE au 24 décembre est inclus et A-EXPIRE au 24 novembre est exclu. Le prédicat inclut les instants `00:00:00` du premier jour et `23:59:59` du dernier, exclut le lendemain et une date vide. La comparaison sur le format ISO conserve cet ordre au passage du 31 décembre au 1er janvier. Ce dernier cas est une vérification statique, pas un test PHP exécuté ici.
3. **Compte sans email (§3.13).** La lecture du marqueur supprime l’adresse avant projection CSV ; la ligne A-SANSMAIL du fichier toutes localités a effectivement une colonne email vide.

- **C18-02 — important — `wp/plugins/imagine-site/ExtractionsNatives.php:40`.** L’état utilisé comme donnée de filtrage vient de `MonCompte::etat()`, qui renvoie un libellé passé à `__()`. Or le filtre `extractions/etat.php` compare strictement cette valeur aux chaînes françaises fixes de ses options. Si une traduction ou un filtre gettext transforme `Actif` en `Active`, la sélection « Actif » exclut cet abonnement, alors que son état natif n’a pas changé ; le résultat dépend ainsi de la traduction de l’opérateur. Le test actuel fournit directement les libellés français et ne couvre pas ce raccord. **Correction proposée :** transporter un état stable non traduit pour le filtrage, issu de la projection métier existante, et traduire seulement le libellé de sortie. Ajouter un test de raccord où la traduction change et où les mêmes identifiants restent sélectionnés. Défaut technique proposé : sélection indépendante de la langue, sans modifier les droits ni la règle métier d’état. Défaut établi par lecture du code, non reproduit sur le site.

## 3. Tests

**Tentative de rejeu effectuée**, avec le runtime PHPUnit existant, dépôt monté en lecture seule, image déjà préparée, réseau désactivé et résultats temporaires en mémoire du conteneur :

```powershell
wsl.exe -d Ubuntu -- docker run --rm --pull never --network none --read-only --user 65534:65534 --cap-drop ALL --security-opt no-new-privileges --tmpfs /tmp:rw,nosuid,nodev,size=256m,mode=1777 --mount type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly --entrypoint php imagine-tests-t01:1 /repo/wp/tests/demo/c16-unit-runtime.php ExtractionsReglesTest
```

Résultat : code de sortie 1, `Wsl/Service/E_ACCESSDENIED`, avant exécution de PHPUnit. Aucun PHP directement disponible dans le PATH. **Les tests PHP ne sont donc pas confirmés par un rejeu indépendant.** Le lanceur global `c18-verifier.py` n’a pas été exécuté : il accède au site et réécrit des preuves, contrairement aux droits du relecteur.

Contrôles locaux exécutés avec Python, sans écriture : les neuf CSV se relisent, ont les quinze colonnes attendues, des lignes complètes, les nombres et les empreintes annoncés ; A-SANSMAIL n’expose pas d’email. Les neuf fichiers PHP propres à C18 correspondent aux empreintes du reçu historique. Une première comparaison incluant le bootstrap partagé a signalé son changement ; l’ajout C19 est visible dans ce bootstrap et documenté dans le README. Ce changement partagé n’est pas assimilé à une régression C18.

Les preuves du producteur annoncent 17 tests/24 assertions ciblés, 98/523 pour le paquet, 14 contrôles natifs, 95 contrôles HTTP et 1 062/34 271 pour T01. Ces nombres sont des résultats enregistrés, distincts de mes contrôles locaux. La réserve C09 historique est levée dans le reçu successeur, également seulement consulté.

Les tests couvrent les filtres mal formés, dates impossibles ou inversées, bornes inclusives, extractions indisponibles, projection des colonnes et neutralisation des formules. Les contrôles HTTP vérifient notamment droits, nonce, méthode, journal et conservation des données.

- **C18-03 — mineur — `wp/tests/demo/c18-runtime.php:26`.** Le contrôle du lecteur natif repose sur les seize abonnements de la démo ; aucun test C18 consulté ne franchit la page de cent abonnements. Une omission de la deuxième page ou un arrêt incorrect resterait invisible dans les preuves. **Correction proposée :** ajouter un test local du lecteur avec 100 puis 101 abonnements, dont le seul résultat correspondant au filtre est en deuxième page ; vérifier aussi l’absence de doublon et l’arrêt après une page vide. Le test doit exercer `ExtractionsNatives::lire()`, pas seulement filtrer un tableau déjà constitué.

## 4. Sécurité et données

Pas de défaut supplémentaire identifié dans le périmètre examiné. Capacité dédiée ou administrateur, vérification avant lecture, POST imposé, nonce lié à l’extraction et aux filtres, sorties HTML échappées et requête du journal préparée. Le CSV utilise la protection C13/C04 et une liste fermée de colonnes. Production via `php://output`, en-têtes privés/no-store, pièce jointe et `nosniff` ; aucun fichier serveur créé par le contrôleur.

Le journal contient opérateur, date, type et nombre, sans filtres ni contenu d’abonné ; une panne de persistance refuse l’export. Les données de preuve examinées sont fictives. Aucun appel réseau ou envoi d’email explicite dans les classes C18. Le lot ne modifie pas une voie de diffusion du texte réservé. Ces constats de code ne remplacent pas une observation dynamique de WordPress, interdite dans cette relecture.

## 5. Doctrine

Réemploi des API natives Woo/WCS, du menu et du droit existants, de SansEmail et de la protection CSV. Pas de modification d’extension tierce identifiée. Espace de noms Imagine, typage strict et README présents ; filtrage testable sans WordPress. Les textes d’interface passent par la traduction, avec le défaut de séparation entre traduction et donnée métier décrit en C18-02.

La capture locale montre le menu, les filtres, le nombre et le journal sans chevauchement évident à cette résolution. Elle ne vaut pas validation visuelle de Ced. Aucune question nouvelle à lui soumettre dans ce rapport.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références officielles déclarées par le producteur figurent dans `A-VOIR.md` ; elles n’ont pas été consultées en ligne, conformément à l’interdiction d’accès aux sites du rôle de relecteur.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut classé bloquant identifié.
- **Important :** C18-02, filtrage d’état dépendant d’un libellé traduit.
- **Mineurs :** C18-01, document d’entrée non actualisé ; C18-03, pagination non éprouvée.

Le rejeu PHPUnit reste non réalisé à cause du refus WSL ; les contrôles locaux des CSV et des sources propres au lot ont réussi. Ce verdict n’est pas un GO.
