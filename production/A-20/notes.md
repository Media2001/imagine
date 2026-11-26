# A-20 — candidat vérifié, gates parent en attente

1. **Fait** : inventaire natif en lecture seule des récurrences enregistrées, par produit/variation, état, rythme, montant et pays ; seuil de confidentialité de cinq, aucune correspondance ni anomalie proposée.
2. **Prêt à relire** : candidat dans `production/A-20/preuves/final/`, vérificateur à code 0 ; **pas de PRET** déposé par cet enfant.
3. **À valider par Ced** : rien pour ce lot fictif ; grille et correspondance restent les décisions d'Imagine, pas celles de cet outil.
4. **Bloqué** : aucun défaut connu bloquant ; préparation finale d'image et rejeu global T-01 laissés au parent, non exécutés ici.
5. **Ensuite** : parent : gates communes, puis seulement dépôt éventuel de PRET. Aucun accord sur le réel.

## Résultats du dernier paquet vert uniquement

- Windows mesuré : `C:/Python314/python.exe`, **3.14.6**. Matrice complète en UTF-8 (`PYTHONUTF8=1`) et cp1252 (`PYTHONUTF8=0`), stdout/stderr et locale consignés ; chaque sous-processus choisit explicitement son encodage. `windows-matrix.json` : **5 commandes, 0 échec**.
- Dans **chacun** des deux contextes : **8 tests Python**, **23 contrôles PHP purs**, **98 contrôles natifs** (classique puis HPOS) et **9 contrôles du runner**, tous verts. Bibliothèque également rejouée sous `php -n`, écritures/processus interdits à l'inclusion, puis unité déplacée dans une arborescence temporaire sans WordPress : reçu identique. T-02 peut autodécouvrir `wp/tests/a20/unit.php` ; aucun PHPUnit parallèle ajouté.
- PHPCS PSR-12 : **0 erreur, 0 avertissement**, sortie réelle 0. Vérificateur final : **108 contrôles verts**, code 0 sous UTF-8 et cp1252. Il refuse aussi un rapport altéré et un fichier ajouté, essais limités à une copie jetable du paquet en scratch.
- Banc compatible existant : WordPress **7.0.9**, WooCommerce **11.1.1**, Subscriptions **9.4.1**, Memberships **1.30.3**. Deux produits dont une variation ; neuf abonnements natifs dont huit vivants, cinq annuels au même total, un mensuel, frais/port gratuits ou non, total nul, devise étrangère, trois lignes dont répétition, état expiré exclu et noms canaris.
- Empreintes indépendantes des **55 tables** et des fichiers identiques avant/après pour chaque magasin/contexte ; SQL READ ONLY éprouvé aussi avec root, blocages mail/HTTP/cron/fichiers réellement exercés. Commande du mode d'emploi lue et exécutée avec **seulement ses trois arguments**, sans date ni option cachée ; refus fermés (symlink, cache/pare-feu, configuration, audit, exception d'extension), canaris absents des sorties et rapports. Conteneurs exacts détruits et absence relue.

## Décisions prises à défaut et limites

Les montants sont les **totaux récurrents enregistrés** sur l'abonnement (`get_total('edit')`), pas une promesse de prochain débit : la documentation officielle précise que les renouvellements peuvent suivre leur dernière commande et des personnalisations. Aucun renouvellement, paiement ou rapprochement exécuté. Pour plusieurs produits, le total entier est compté dans chacun des groupes, sans allocation inventée ; les groupes ne s'additionnent donc pas. « Annuel » = `1 year` ou `12 month`, sans équivalence jours/semaines ni décision sur l'engagement. Pays de livraison sans repli sur la facturation ; absent/inconnu séparé. Seuil montant par couple produit/variation + devise/montant ; pays global. Tous ces choix sont écrits dans les rapports et le mode d'emploi.

Réemploi d'A-11/A-12 et du banc A-02, **aucune modification** de ces lots ni d'A-18/A-19. Deux lignes ciblées ajoutées au mode d'emploi commun, lignes A-21 conservées ; contrat limité aux lignes A-20, jamais hash du fichier partagé. Standard officiel contrôlé avant l'adaptateur natif (quatre HTTP 200 et empreintes dans `preuves/final/official-sources.json`). Lecture exhaustive en mémoire, gros volumes et Imagine 6.9.1 non qualifiés. Aucun Git, archive, site réel, staging Imagine, Novamira, compte fournisseur, installation hôte ou déploiement ; verrous laissés intacts.

Code : `wp/outils/bascule/a20/` (6 fichiers). Tests : `wp/tests/a20/` (9 fichiers). Sources propres liées aux exécutions et inventaire final scellés dans le paquet ; manifeste ne porte que le lot et ce paquet. Tous les essais RED, débogages et répétitions intermédiaires restent dans `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a20-work/` ; un seul paquet est livré.

Recontrôle : `C:/Python314/python.exe -B wp/tests/a20/verify.py production/A-20/preuves/final`.
