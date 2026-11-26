# A-20 — gardien commun intégré, nouveau paquet vérifié sans PRET

## Résultat courant — remplace les preuves antérieures

`production/A-20/preuves/final` provient intégralement de la nouvelle matrice `a20-shared-final-04`, exécutée après les dernières sources communes et la restauration des refus d’arguments avant staging. Code réel de la matrice : **0**, cinq commandes vertes. Windows `C:/Python314/python.exe`, **3.14.6**, consoles UTF-8 puis cp1252 mesurées ; encodage enfant explicite et scratch Hermes explicite.

Par console : **34 tests Python, 23 assertions PHP pures, 158 contrôles natifs classique+HPOS, 9 contrôles runner**, plus **21 contrôles additionnels du gardien commun**. Tous PASS. Deux mutations réelles (une par magasin) retirent uniquement le gardien dans les copies jetables : le canari fuit alors effectivement ; aucune sortie brute du témoin n’est conservée. Les gardiens et fixtures sont restaurés octet pour octet. Syntaxe/PSR-12 : zéro erreur, zéro avertissement. Le vérificateur livré a réellement exécuté **111 contrôles PASS**, code **0**, dans chacune des deux consoles. Six sondes de miroir jetable passent également, dont PRET futur accepté, corruption et omission rescellée refusées, dérive du gardien refusée, restauration verte ; reçus racine `candidate-verification.json` et `verification-probes.json`.

Une seule implémentation des pipes : `wp/outils/bascule/stream_guard.py`, partagée avec A21 et les outils clos. A20 garde son contrôle strict `report.py` / `report-contract.json`, sa publication privée différée et ses refus fermés. Comptage `without_product_line` et annuel `1 year` / `12 month` inchangés. Toutes les dépendances exécutées, gardien commun inclus, sont maintenant comparées aux sources courantes ; README partagé contrôlé uniquement par ses deux lignes exactes.

Les paquets précédents et leurs reçus racine sont conservés hors dépôt dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a22-superseded-a20` et `a22-superseded-candidate02-a20`. Aucun PRET créé. Préparation globale, T01 global et décision de PRET restent au parent ; aucune des anciennes gates n’est revendiquée pour les nouvelles sources. Le vérificateur n’exige plus l’absence perpétuelle de PRET et accepte une preuve parent optionnelle `--parent-proof` (sources exactes, chemins vers vrais reçus préparation/T01 à code zéro). Aucun réel, archive Imagine, compte, Novamira, déploiement, Git, verrou ou README partagé touché.

Commandes effectivement exécutées, indépendantes du dossier courant :

```text
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a20/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a20-shared-final-04
C:/Python314/python.exe -B C:/Users/Ced/imagine/wp/tests/a20/verify.py C:/Users/Ced/imagine/production/A-20/preuves/final
```

Pour rejouer, choisir un nom de sortie **neuf**. Les cinq commandes enfants, environnements, noms exacts des conteneurs et suppressions relues sont dans le paquet. Aucun paquet d’un lot clos n’a été réécrit : leurs rejeux appartiennent à A22.

## Historique avant gardien commun — non probant pour les sources actuelles

1. **Fait** : inventaire natif en lecture seule des récurrences enregistrées, par produit/variation, état, rythme, montant et pays ; seuil de confidentialité de cinq, aucune correspondance ni anomalie proposée.
2. **Prêt à relire** : candidat dans `production/A-20/preuves/final/`, vérificateur à code 0 ; **pas de PRET** déposé par cet enfant.
3. **À valider par Ced** : rien pour ce lot fictif ; grille et correspondance restent les décisions d'Imagine, pas celles de cet outil.
4. **Bloqué** : aucun défaut connu bloquant ; préparation finale d'image et rejeu global T-01 laissés au parent, non exécutés ici.
5. **Ensuite** : parent : gates communes, puis seulement dépôt éventuel de PRET. Aucun accord sur le réel.

### Résultats du paquet antérieur — historique

- Windows mesuré : `C:/Python314/python.exe`, **3.14.6**. Matrice complète en UTF-8 (`PYTHONUTF8=1`) et cp1252 (`PYTHONUTF8=0`), stdout/stderr et locale consignés ; chaque sous-processus choisit explicitement son encodage. `windows-matrix.json` : **5 commandes, 0 échec**.
- Dans **chacun** des deux contextes : **34 tests Python**, **23 contrôles PHP purs**, **158 contrôles natifs** (classique puis HPOS) et **9 contrôles du runner**, tous verts. Bibliothèque également rejouée sous `php -n`, écritures/processus interdits à l'inclusion, puis unité déplacée dans une arborescence temporaire sans WordPress : reçu identique. T-02 peut autodécouvrir `wp/tests/a20/unit.php` ; aucun PHPUnit parallèle ajouté.
- PHPCS PSR-12 : **0 erreur, 0 avertissement**, sortie réelle 0. Vérificateur final : **110 contrôles verts**, code 0 sous UTF-8 et cp1252. Il refuse aussi un rapport altéré et un fichier ajouté, essais limités à une copie jetable du paquet en scratch.
- Banc compatible existant : WordPress **7.0.9**, WooCommerce **11.1.1**, Subscriptions **9.4.1**, Memberships **1.30.3**. Deux produits dont une variation ; neuf abonnements natifs dont huit vivants, cinq annuels au même total, un mensuel, frais/port gratuits ou non, total nul, devise étrangère, trois lignes dont répétition, état expiré exclu et noms canaris.
- Empreintes indépendantes des **55 tables** et des fichiers identiques avant/après pour chaque magasin/contexte ; SQL READ ONLY éprouvé aussi avec root, blocages mail/HTTP/cron/fichiers réellement exercés. Commande du mode d'emploi lue et exécutée avec **seulement ses trois arguments**, sans date ni option cachée ; refus fermés (symlink, cache/pare-feu, configuration, audit, exception d'extension), canaris absents des sorties et rapports. Conteneurs exacts détruits et absence relue.

### Décisions prises à défaut et limites

Les montants sont les **totaux récurrents enregistrés** sur l'abonnement (`get_total('edit')`), pas une promesse de prochain débit : la documentation officielle précise que les renouvellements peuvent suivre leur dernière commande et des personnalisations. Aucun renouvellement, paiement ou rapprochement exécuté. Pour plusieurs produits, le total entier est compté dans chacun des groupes, sans allocation inventée ; les groupes ne s'additionnent donc pas. « Annuel » = `1 year` ou `12 month`, sans équivalence jours/semaines ni décision sur l'engagement. Pays de livraison sans repli sur la facturation ; absent/inconnu séparé. Seuil montant par couple produit/variation + devise/montant ; pays global. Tous ces choix sont écrits dans les rapports et le mode d'emploi.

Réemploi d'A-11/A-12 et du banc A-02, **aucune modification** de ces lots ni d'A-18/A-19. Deux lignes communes existantes contrôlées par contrat sur les lignes A-20, jamais par empreinte du fichier partagé ; aucun delta de README commun nécessaire. Recherche officielle antérieure conservée comme fondation inchangée dans `preuves/final/official-sources.json`, pas comme nouvelle collecte. Lecture exhaustive en mémoire, gros volumes et Imagine 6.9.1 non qualifiés. Aucun Git, archive d'Imagine, site réel ou existant, staging Imagine, Novamira, compte fournisseur, installation hôte ou déploiement ; verrous laissés intacts.

Code : `wp/outils/bascule/a20/` (8 fichiers). Tests : `wp/tests/a20/` (10 fichiers). Sources propres liées aux exécutions et inventaire final scellés dans le paquet ; manifeste ne porte que le lot et ce paquet. Tous les essais RED, débogages et répétitions intermédiaires de cette correction restent dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a20-b1-work/` ; un seul paquet est livré. L'ancien PRET et l'ancien paquet ont été retirés vers ce scratch.

### Correction B1 et TDD réel

Le superviseur externe Python capture stdout et stderr PHP en octets, sans jamais les recopier ni les conserver, jusqu'à la terminaison et aux deux EOF (shutdown compris). Un arrêt 0 sans rapports complets ne suffit jamais. Seuls le jeton exact de succès, stderr vide et deux rapports validés permettent la publication ; les refus sont des messages exacts de listes fermées. Le tampon PHP reste une défense secondaire.

Rapports dans un répertoire privé jetable, puis contrôle par `report.py` et `report-contract.json` : noms exacts, fichiers ordinaires sans liens, JSON UTF-8 sans doublons, clefs/types/textes fermés, définitions fixes, comptes/seuils cohérents, magasin et empreinte d'audit, Markdown identique à sa projection JSON. En échec, pas de rapport final et suppression du répertoire jetable. Q1 `without_product_line` et Q2 annuel `1 year`/`12 month` conservés ; logique métier PHP inchangée.

Quinze injections par magasin et contexte, chacune avec refus exact et absence de résidu : stdout/stderr directs, echo+exit 0, exit 0 muet, die, faux succès sans rapports, octet non UTF-8, trois canaux de shutdown, rapports partiels/altérés et fichier supplémentaire. Aucune sortie brute capturée dans les reçus, même lors d'un échec du test.

Dans le scratch ci-dessus : `red-stdout/result.json` montre l'échec attendu `direct_stdout_closed` classique+HPOS contre le lanceur initial, puis `green-stdout/result.json` est vert. `red-reports/result.json` montre l'échec attendu `closed_process:report_extra_field` sur les deux magasins contre le superviseur sans contrat complet, puis `green-reports/result.json` est vert après validation stricte. La matrice complète `final-matrix/` a été exécutée après la dernière écriture des sources ; elle seule est livrée. `candidate-verification.json` consigne les deux vérifications finales et les mutations refusées sur copie jetable.

### Reprise indépendante du répertoire courant — PowerShell Windows

Chemins de sortie neufs obligatoires ; aucun PHP hôte :

```powershell
& 'C:/Python314/python.exe' -B 'C:/Users/Ced/imagine/wp/tests/a20/matrix.py' --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a20-b1-reprise-matrice
& 'C:/Python314/python.exe' -B 'C:/Users/Ced/imagine/wp/tests/a20/run.py' --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a20-b1-reprise-native
& 'C:/Python314/python.exe' -B 'C:/Users/Ced/imagine/wp/tests/a20/verify.py' 'C:/Users/Ced/imagine/production/A-20/preuves/final'
```

La matrice fixe elle-même les deux contextes de console, lance les suites Python, classique+HPOS deux fois et PHPCS. Runner limité à son conteneur exact `imagine-a20-prices-<identifiant>`, style sous son propre nom : aucune suppression globale.

Capture des flux en mémoire : sorties illimitées et disponibilité face à une extension bloquée non qualifiées. Le contrat ferme les textes imprévus ; il ne certifie pas l'honnêteté de chiffres fabriqués par une extension hostile. **Aucun PRET déposé ; ancien PRET retiré.** Image commune, rejeu global et contrôle indépendant restent au parent. `FINALISATION.md` remplace les anciennes gates, périmées pour ce code. Ni `preparer-image.ps1`, ni T-02, ni surface commune, ni verrou modifiés. Aucun rapport `files/rapports` : le parent s'en charge.
