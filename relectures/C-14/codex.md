# Relecture indépendante Codex — C-14

Date : 25 novembre 2026. Références : consignes du relecteur, doctrine, décisions, brief C-14, cahier des charges §3.7, §3.9 et §3.11. Production C-14, raccords dans `wp/`, tests et profil C09 examinés. Le rapport de Claude n'a pas été consulté. Aucun site, compte ou base n'a été accédé ; seul ce rapport est écrit.

## 1. Conformité

Les livrables sont présents, y compris `PRET`. Le produit simple porte un seul numéro ; les commandes natives alimentent le contrat `achat` du moteur C06 par C08, et le PDF passe par C11. V-NUM est explicitement associé au profil P-NUMERO conservé dans C09.

La référence erronée du brief au §3.11 (événements) est signalée ; le §3.9 porte bien les droits de l'acheteur. Le §3.7 prévoit l'achat papier sans compte puis propose la création du compte pour accéder aux articles, sous réserve de confirmation par Imagine. L'absence de revendication après achat est annoncée, et aucun droit n'est déduit de la seule adresse email : cela répond à la demande de clarification du brief, sans constituer une livraison du parcours invité complet.

**C14-01 — Important — `wp/plugins/imagine-site/AchatsNumeros.php:77`.** Le droit historique dépend du produit courant : la ligne est convertie avec `numero($item->get_product())`, puis comparée à son instantané. Après un achat payé du numéro A, supprimer le produit, vider son champ ou le réaffecter à B ferme donc A, même si la commande et son paiement sont inchangés et A reste publié. Le §3.9 accorde pourtant les articles et le PDF du numéro acheté « sans limite de durée ». Cette révocation liée à la maintenance du catalogue est une restriction métier supplémentaire, présentée comme technique dans la production. **Correction proposée :** utiliser l'instantané validé de la ligne comme référence du numéro acquis, indépendamment du produit courant ; conserver les contrôles de propriétaire, paiement, remboursement et disponibilité du numéro. Une réaffectation doit concerner les achats suivants, sans ouvrir B aux anciens acheteurs ni fermer A. Adapter les tests qui attendent aujourd'hui cette fermeture.

**C14-03 — Mineur — `production/C-14/A-VOIR.md:3`.** L'état indique « vérification indépendante du parent attendue. Aucun PRET créé », alors que `production/C-14/PRET` atteste le rejeu du parent et le dépôt du marqueur. **Correction proposée :** actualiser l'état de livraison pour distinguer les actions terminées des relectures encore attendues, et harmoniser les mentions correspondantes dans les documents de production.

## 2. Exactitude métier

Déroulés manuels à partir du code, distincts d'une exécution WordPress :

| Cas | Résultat du code | Appréciation |
|---|---|---|
| Compte 42, commande processing payée, date passée, ligne du numéro A avec instantané A, aucun remboursement | Contrat `achat(A)` ; articles et PDF A ouverts, numéro B refusé par C06 | Conforme au §3.9 et au brief |
| Même ligne, commande pending, on-hold, failed ou cancelled | Aucun droit d'achat ; articles réservés et PDF refusés en l'absence d'autre droit | Conforme au brief |
| Achat A payé puis remboursement total ; aucun autre achat valide | Aucun droit provenant de cette commande | Conforme au brief |
| Achat A payé, produit supprimé, numéro A toujours publié | Aucun droit malgré l'instantané A conservé | Écart C14-01 |

À l'instant exact d'acquisition, C06 ouvre le droit ; avant cet instant, il le refuse. Le changement d'année ne l'expire pas. Une date éditoriale invalide ferme l'adaptateur. La lecture n'insère aucun droit en double : elle reconstruit les droits depuis les commandes. Un autre achat valide du même numéro subsiste après révocation du premier.

**C14-02 — Important — `wp/plugins/imagine-site/AchatsNumeros.php:71`.** La présence d'un remboursement quelconque est appliquée à toutes les lignes de la commande. Une commande contenant A et B perd ainsi les deux accès même si le remboursement concerne uniquement B, ou seulement les frais de port. Le choix est annoncé, mais le brief ne précise pas ce traitement des remboursements partiels et le §3.9 ne le définit pas. Cette interprétation reste codée en dur, sans le réglage administratif exigé par la doctrine §4 et la décision du 22 novembre pour une règle métier non tranchée. **Correction proposée :** isoler la portée du remboursement derrière un réglage administratif, documenter le défaut prudent et tester une commande à plusieurs numéros, un remboursement ventilé et un remboursement non ventilé. La révocation d'un achat entièrement remboursé doit rester garantie.

### Pour Imagine

**Métier — C14-02 :** un remboursement partiel retire-t-il tous les accès de la commande ou seulement ceux des numéros concernés ? **Défaut prudent proposé :** conserver provisoirement la fermeture de toute la commande, mais comme réglage explicite et modifiable ; prévoir une politique par ligne pour les remboursements attribuables. Une réponse d'Imagine n'est pas nécessaire pour réaliser le réglage et ses tests.

## 3. Tests

**Exécuté pendant cette relecture : 33 tests Python locaux réussis, code retour 0**, en 0,418 seconde. Sélection identique à la partie locale de `c14-regressions.py` : découverte de `wp/tests/demo/test_*.py`, dépendances chargées depuis les wheels B01 existantes, sans installation. Lancement par `python -B -` pour éviter les fichiers de bytecode. Les transports des scénarios concernés sont simulés. Ces tests vérifient surtout les scripts, profils et contrats de non-régression ; ils ne prouvent pas l'accès Woo/PDF C14.

Tentatives du test PHP pur `wp/tests/demo/c14-unit.php` :

- `php -n wp/tests/demo/c14-unit.php` : impossible de démarrer, `php` absent du chemin Windows.
- Commande Docker locale reprise de `c14.py::pure()`, via WSL, image existante, réseau désactivé et dépôt monté en lecture seule : refus `Wsl/Service/E_ACCESSDENIED`, avant exécution PHP.

Les tests PHP C14 et PHPUnit C11/C12 ne sont donc **pas confirmés par cette relecture**. Aucun contournement ni installation effectué. Les recettes natives et HTTP n'ont pas été lancées : `relecteurs/AGENTS.md` interdit l'accès à un site ou une base ; les runners complets téléversent également des fichiers et réécrivent des reçus hors du seul rapport autorisé.

Les reçus fournis annoncent 536 contrôles réussis et 193 tests/contrôles complémentaires. Leur lecture confirme les catégories annoncées, sans valoir rejeu indépendant. La couverture inclut paiements, refus, remboursements, autre numéro, PDF, pagination à 51 commandes, suppressions et erreurs de lecture.

Limite des oracles : `wp/tests/demo/c14-runtime.php:120` exige précisément la révocation contestée en C14-01 ; un résultat vert valide ici l'implémentation plutôt que le droit durable du §3.9. Les corrections C14-01 et C14-02 doivent apporter les cas métier correspondants, avec conservation de l'accès historique et commandes à plusieurs lignes selon le réglage retenu.

## 4. Sécurité et données

Aucune fuite nouvelle démontrée par l'examen statique. Le client provient de l'identité native ; les commandes sont filtrées et leur propriétaire revérifié. Les invités restent fermés sans rapprochement par email. Les identifiants de numéro sont strictement contrôlés. Le champ produit utilise le composant Woo et son circuit administratif natif, avec contrôle supplémentaire de capacité. Le raccord utilise le CRUD Woo, sans SQL construit à partir d'une entrée utilisateur.

Le PDF demeure derrière la décision C08/C11 ; aucun téléchargement public supplémentaire n'est créé. Les invalidations étendent la mémoire limitée à la requête aux mutations Woo. Les tests HTTP fournis contrôlent les octets PDF, le REST authentifié, les refus anonymes et les anciennes routes média ; leur réussite n'a pas été reproduite ici.

Les fixtures examinées sont déclarées fictives, avec adresses en `@example.org`. Les chemins de fichiers privés sont documentés ; ces fichiers n'ont pas été ouverts. Aucun secret ni donnée personnelle réelle identifié dans les fichiers examinés.

## 5. Doctrine

Séparation satisfaisante entre conversion PHP pure et adaptation Woo ; moteur C06 réutilisé, pas de table miroir de droits ni de second circuit PDF. Les nouvelles classes déclarent le typage strict, utilisent l'espace de noms `Imagine\Site` et traduisent les textes d'interface. Le README décrit le fonctionnement et les commandes de test.

Le choix du CRUD natif et du contrôleur existant est expliqué, avec des références officielles dans A-VOIR. Leur contenu distant n'a pas été vérifié, conformément à l'interdiction d'accéder à un site. Aucun contrôle PSR-12 indépendant n'a pu être exécuté via WSL.

L'écart doctrinal sur la règle de remboursement non réglable est C14-02. C14-01 ne doit pas être traité comme un simple choix technique : il modifie les droits acquis définis par le cahier des charges.

## 6. Études (lots sans code)

Sans objet : lot de code.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant :** aucun défaut classé à ce niveau démontré ; validation PHP/native limitée par l'environnement et les droits du relecteur.
- **Important : C14-01** — préserver le numéro acquis malgré les changements du catalogue.
- **Important : C14-02** — rendre réglable la portée des remboursements partiels et couvrir les commandes à plusieurs numéros.
- **Mineur : C14-03** — aligner l'état documentaire sur le marqueur PRET effectivement présent.
