# Relecture indépendante Codex — C-17

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine et grille, brief C-17, cahier des charges §3.7, §3.13, §4.4 et question 4 du chapitre 7, `docs/decisions.md`. Lecture des sources, tests et preuves du lot ; aucun accès au site, à une base ou à un compte. La relecture Claude n'a pas été consultée. Seul ce rapport a été écrit.

## 1. Conformité

Le périmètre nominal est couvert : emplacement B-02, quatre états documentaires, dépôt plafonné, consigne de masquage du registre national, file référent sous Imagine, confirmation, date de fin, catégories dans C-10, capacité dédiée et nonces. Le stockage et les en-têtes privés réemploient C-11. Aucun appel modifiant prix, commandes, abonnements ou accès, ni envoi d'email, dans les trois classes C-17 examinées.

Les livrables demandés sont présents : code, tests, `A-VOIR.md`, besoins designer, `PRET` et rapport `files/rapports/2026-11-26-01h26-V2.md`. Les choix de formats, plafond, date non passée et absence d'automatisme à l'échéance sont explicités. La conservation de la décision, de sa date et de l'opérateur suit le brief ; elle dépasse la formulation « catégorie et date de fin » du §4.4. Cet écart entre textes est signalé ici, sans inventer une nouvelle règle de conservation.

La réserve historique C09 annoncée dans `A-VOIR.md` ne doit pas être confondue avec l'état ultérieur : le reçu `verification-successeur-20261126T012239904888-V2.json` annonce `VERIFIED_SUCCESSOR_C09_RESTAURE`, et le rapport parent de 02 h 24 documente C09 382/382. Je ne compte pas l'ancienne réserve comme une anomalie actuelle de C-17.

## 2. Exactitude métier

Déroulés manuels, par lecture du code, sans exécution PHP réussie :

- **Validation (§3.13)** : dépôt « à préciser », état `en_attente` avec référence aléatoire ; décision le 26 novembre 2026, fin au 31 janvier 2027. La règle produit exactement catégorie, décision `valide`, date de décision, fin et opérateur. Le contrôleur supprime le fichier avant l'enregistrement ; le compte affiche la fin. Conforme dans le cas nominal.
- **Refus (§3.13)** : même état initial, décision `refuse`, fin laissée vide. La règle conserve une fin vide, retire la référence du document et le contrôleur supprime le fichier. Un second envoi de l'ancien formulaire échoue sur la version. Conforme dans le cas nominal.
- **Bornes** : une fin égale au jour UTC de décision est acceptée ; le 29 février 2027 et une fin antérieure sont refusés ; le passage décembre–janvier est compatible avec la comparaison ISO après validation de date. Une échéance atteinte ne change aucun droit, conformément au périmètre du brief. Aucun calendrier de parution n'intervient.

**I-1 — Important — `wp/plugins/imagine-site/Justificatifs.php:122` — Un remplacement refusé peut détruire le document en attente et laisser son ancienne version utilisable.**

L'ancien fichier est supprimé avant l'ouverture et l'écriture du nouveau. Si `fopen`, `fwrite` ou la persistance échoue ensuite, la requête est refusée mais l'option reste dans son ancien état `en_attente`, avec son ancien `blob` et la même version. Le compte et la file proposent alors un téléchargement inexistant. Plus grave, un formulaire référent déjà ouvert reste recevable : la décision ne vérifie pas la présence du document et la suppression d'un fichier déjà absent est considérée comme réussie. Une validation peut ainsi être enregistrée après l'échec destructif du remplacement. La limite est annoncée dans la livraison, mais le message générique ne rend pas cet état cohérent.

**Correction proposée :** rendre le remplacement récupérable en cas d'échec, en conservant un état documentaire cohérent et sans seconde pièce durable pour le compte. Si la pièce est perdue, invalider explicitement la révision et empêcher sa validation jusqu'à un nouveau dépôt ; afficher son indisponibilité. Ajouter les scénarios d'échec après suppression, y compris avec un ancien formulaire référent encore ouvert. Le test actuel de suppression impossible s'arrête avant cette situation.

## 3. Tests

**Tentative locale effectuée**, avec le lanceur PHP du dépôt, dépôt monté en lecture seule, réseau coupé et aucun reçu écrit dans `production/` :

```powershell
wsl.exe -d Ubuntu -- docker run --rm --pull never --network none --read-only --user 65534:65534 --cap-drop ALL --security-opt no-new-privileges --tmpfs /tmp:rw,nosuid,nodev,size=256m,mode=1777 --mount type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly --entrypoint php imagine-tests-t01:1 /repo/wp/tests/demo/c16-unit-runtime.php JustificatifReglesTest
```

Résultat : sortie **1**, « Accès refusé », `Wsl/Service/E_ACCESSDENIED`, avant le démarrage des tests. Aucun `php` ni `docker` natif trouvé dans le PATH et aucun `vendor/bin/phpunit` dans le plugin. Je ne revendique donc aucun test PHP passé pendant cette relecture. Les scripts HTTP, réglages, fautes et vérification globale n'ont pas été lancés : ils accèdent au site et réécrivent des preuves, ce qu'interdisent les consignes de ce rôle.

Les reçus livrés indiquent 5 tests/18 assertions pour les règles, 81/499 pour la suite racine historique, 49 contrôles HTTP, 8 de réglages et 8 de suppression/concurrence, sans échec ; `final.json` annonce T01 1045/34247. Ce sont les résultats du producteur. Les empreintes locales des trois classes C-17 et de leur test correspondent à ce reçu. Parmi les sources qu'il répertorie, le bootstrap partagé et le vérificateur ont évolué ; des reçus de succession existent, donc le reçu historique seul ne certifie pas tout le dépôt actuel.

La couverture comprend droits de lecture, nonces, anciens formulaires, remplacement, suppression physique, décisions concurrentes et refus d'une suppression impossible. Elle ne couvre pas les échecs après suppression relevés en I-1, ni la suppression du titulaire relevée en I-3. Les bornes positives de date, le JPEG valide et la taille exactement au plafond méritent aussi des cas explicites ; le seul test pur nominal PDF utilise un fragment sans document complet.

**I-2 — Important — `wp/tests/demo/b02-runtime.php:43` — Le contrôle de non-régression B-02 attend encore le texte supprimé par C-17.**

Le test exige `Aucune facture ou justificatif disponible`, alors que le template courant affiche `Aucune facture disponible — raccord documentaire Odoo non disponible.` et ajoute le bloc C-17. Ce contrôle devient faux pour les cinq profils parcourus, même lorsque le raccord fonctionne. Il reste exécuté par le vérificateur B-02 ; les résultats verts C-17/T01 ne prouvent donc pas la conservation de ce parcours dépendant.

**Correction proposée :** adapter l'assertion au contrat désormais attendu : liste de factures distincte et vide, présence du bloc documentaire pour la session, absence de mélange entre factures et justificatifs. Rejouer B-02 avec C-17 chargé et joindre le résultat au reçu successeur, sans supprimer la vérification.

## 4. Sécurité et données

Les lectures contrôlent la session et le titulaire ou la capacité dédiée, avant les octets. Les écritures exigent POST et nonce ; les décisions exigent aussi la capacité et la confirmation. Les requêtes variables sont préparées et les sorties de formulaire échappées. Références aléatoires, fichiers hors racine publique, mode 0600, rejet de liens symboliques, téléchargement en pièce jointe, `nosniff`, CSP et `no-store` sont présents. Aucun secret ni document personnel réel repéré dans les fichiers du lot examinés. Aucune nouvelle voie de sortie du texte réservé identifiée dans ce raccord ; l'étanchéité globale n'a pas été rejouée.

Le contrôle PDF reste une reconnaissance MIME assortie de signatures interdites, pas une désinfection générale ; la livraison le dit et n'expose pas de prévisualisation applicative. Je ne transforme pas cette limite déclarée en preuve d'exécution de contenu.

**I-3 — Important — `wp/plugins/imagine-site/Justificatifs.php:333` — Supprimer un titulaire laisse sa pièce personnelle conservée et invisible dans la file.**

Les documents sont rattachés à une option et à un fichier privé, sans nettoyage enregistré lors de la suppression d'un utilisateur. Une fois le compte supprimé, la file saute son entrée ; le verrou refuse également toute opération sur un utilisateur absent. Le fichier et l'option deviennent donc orphelins, sans possibilité de décision par le parcours livré. Cela contredit la prise en charge de la suppression de compte au §4.4 et laisse une pièce personnelle sans issue de traitement.

**Correction proposée :** raccorder le nettoyage documentaire à la suppression du compte, avant de perdre le titulaire, avec gestion explicite d'un échec de suppression physique. Couvrir les états en attente et décidé par un test vérifiant l'absence du fichier et de l'option, ainsi que le comportement lorsque le fichier ne peut pas être retiré. Prévoir le traitement des éventuels orphelins sans supprimer silencieusement leurs seules références.

## 5. Doctrine

La logique de catégories, types et décisions est isolée en PHP pur ; conventions de namespace, typage strict, préfixes et traduction des libellés visibles respectées dans les classes du lot. Le README documente le raccord et ses commandes. Les primitives WordPress et C-11 sont réemployées ; aucune modification d'extension tierce relevée. Les problèmes I-1 et I-3 concernent le cycle de vie des pièces, et I-2 la non-régression exigée par la doctrine.

### Décisions techniques, défaut proposé

Pour I-1 et I-3, défaut prudent : aucune validation d'une révision dont la pièce a disparu ; aucune suppression de compte ne doit abandonner silencieusement sa pièce privée. Hermès peut appliquer ces défauts et fournir les tests sans attendre un arbitrage de Ced.

### Pour Imagine

Les catégories et conséquences du statut ou de l'échéance restent des décisions **métier** déjà ouvertes. Défaut proposé maintenu : catégorie configurable « à préciser », aucun effet automatique sur prix, abonnement ou accès. Aucune nouvelle question bloquante pour ce lot.

## 6. Études (lots sans code)

Sans objet : lot de code. Les liens de documentation officielle sont présents dans `A-VOIR.md` ; ils n'ont pas été ouverts, conformément à l'interdiction d'accès aux sites de ce rôle. Aucune affirmation nouvelle sur une extension n'est fondée ici sur ces liens seuls.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun constat établi de cette gravité.
- **Important :** I-1, remplacement en échec laissant une révision sans pièce encore validable ; I-2, contrôle B-02 devenu incompatible avec le raccord ; I-3, pièce orpheline après suppression du titulaire.
- **Mineur :** aucun point supplémentaire retenu.

Les tests locaux restent à rejouer dans un environnement où WSL est accessible ; les preuves livrées ne remplacent pas cette vérification indépendante.
