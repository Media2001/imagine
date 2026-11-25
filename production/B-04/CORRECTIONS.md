# B-04 — Corrections techniques prêtes à relire

**Fait** : instructions 1–6 appliquées et vérifiées sur imagine-test-demo uniquement.
**Prêt à relire** : B-04, `A-VOIR.md`, `verification-corrections-finale.json` et commandes de rejeu.
**À arbitrer par Ced** : garder le statut du kiosque, oui/non (fusion point 7) ; rendu conservé à l'identique, sans bloquer les correctifs techniques.
**Bloqué** : rien. Aucun GO réel, paiement ou mise en ligne demandé ou présumé.
**Ensuite** : vérification indépendante par le parent ; C16–18 non traités.

## Corrections et décisions prises à défaut

- **I1** : `Paywall::decisionListe()` et le mode sans consommation du même raccord `Decouverte::decider()` utilisent le moteur et l'état C06/C12, sans écrire ouverture/quota ni activer artificiellement le contexte de lecture. Cache liste/lecture séparé ; erreur = statut réservé. Le thème présente seulement la décision.
- **I2** : `Paywall::couvreNumero()` reconnaît la couverture à la sortie pour le seul CTA ; `decisionPdf()` et C11 restent à l'instant courant. L'acheteur préexistant ne revoit jamais Acheter avant/à la sortie ; PDF fermé avant, ouvert à la sortie selon C06. Le cas a-carte/PDF antérieur fermé conserve son bouton, comme admis par la fusion.
- **Tests** : sous-suite PHPUnit B04 dans le paquet `imagine-site` déjà découvert par T01, sans nouveau manifeste/dépendance ; fonction réelle du thème testée seule, quatre codes/libellés et deux motifs découverte, mode sans écriture, séparation des caches et seconde exacte de sortie.
- **HTTP** : refus de toute fixture/marqueur de corps vide ; présence chez l'ayant droit et absence chez l'anonyme/listes. Nouveau témoin découverte et achat natif préexistant avec date future, attendus indépendants du PDF. Réglages/état/confirmation/thématique/date restaurés et relus exactement.
- **Démo** : exemption Woo déplacée du thème vers `wp/outils/demo/b04-preview.php`, installée comme seul mu-plugin de démo. Aucun réglage Woo/cart/checkout changé. Redondance du numéro retirée du sommaire, conservée sur les thématiques.
- **Défaut technique** : appliquer 1–6 sans attendre Ced, garder 7 inchangé. Les 33 défauts PSR-12 hérités des trois fichiers touchés ont été corrigés uniquement en espaces/retours à la ligne ; preuve d'équivalence et tests finaux rejoués.

## Résultats finaux après dernière écriture de code

- **77 tests PHPUnit uniques, 530 assertions**, zéro erreur/échec/ignoré ; sous-suite B04 rejouée séparément (4 tests, incluse dans les 77). **4 tests Python** verts. JUnit et noms de cas relus ; conteneur hors réseau, dépôt lecture seule, suppression contrôlée.
- **513 contrôles PHP natif/HTTP/SQL/navigateur verts**, dont 32 ciblés découverte/achat futur, 146 sur les trois visiteurs et deux numéros, 201 catalogue et 86 navigateur. **16 captures** actuelles ; mobile anonyme et desktop acheteur inspectés. PDF réellement servi/refusé.
- **PSR-12 `-n` : 0 erreur** sur les cinq fichiers PHP de runtime. Préparateur T01 exécuté sans édition, sortie 0. Les **5 fichiers actifs** sont relus identiques aux sources ; manifeste de **17 fichiers source** et empreintes des reçus/captures. Le runner global n'est pas prétendu rejoué.
- Vingt vrais articles : requêtes **page / gabarit** = anonyme **93/32**, a-carte **246/173**, p-numero **245/176**. Le coût connecté augmente par rapport au premier rendu ; il est mesuré et non optimisé ici. Numéro 2566, ses 20 articles et le contrôleur retirés, absence relue. Candidats de lint propres retirés par empreinte exacte.

Incidents de harnais résolus : tmpfs/chargement des sources pour PHPUnit ; récupération JUnit par stdin plutôt que `docker cp` ; préfixe natif distinct pour éviter une collision de reçus. Échecs historiques conservés, jamais agrégés comme verts. Aucun compte, commande ou paiement créé, aucun mail, aucune autre cible, aucun Git, verrou parent inchangé.

Commandes : `COMMANDES-CORRECTIONS.md` ; scellement : `sceller.py --check`. Le PRET signifie relecture technique, pas validation visuelle ni clôture.
