# B-07 — rendu

- Agenda livré sur `imagine-test-demo` uniquement : trois types, futur trié, passé séparé, inscription gratuite, partenaire externe commercial sans formulaire, JSON-LD fondé sur l'affichage.
- Standard gratuit étudié sur les readmes officiels de l'éditeur (`STANDARD.md`) : conservation du CPT B-00 et raccord natif, sans installer Event Tickets/Plus ou The Events Calendar.
- Inscriptions privées natives, doublon protégé en base, réponse identique sans révéler compte/inscription, case de recontact facultative et décochée ; callbacks RGPD additifs, aucun changement C-21.
- **Tests :** 14 règles pures ; 15 contrôles adaptateur ; 8 confidentialité ; 83 recette HTTP ; 29 non-régression articles ; 10 readback final. Les reçus donnent séparément leurs mutations témoins, sans les compter comme de nouvelles fonctionnalités.
- **Suite générale : 1 128 tests, 35 565 assertions, zéro échec/erreur/ignoré**, dont les deux nouveaux tests `AgendaReglesTest`. Image préparée après l'ajout des tests. Vérificateur hors réseau : **51 contrôles verts**, en UTF-8 et cp1252.
- **Rien n'est parti :** zéro email, zéro transport HTTP externe ; 17 tentatives d'infrastructure arrêtées par la garde existante, aucun appel de l'agenda. Aucune passerelle, licence, paiement ou export d'inscrits.
- Préimages privées et sessions hors dépôt ; inscriptions d'essai et observateur retirés, état métier relu exact ; seuls les compléments des deux événements B-00 et les deux nouvelles fixtures B-07 persistent.
- Fichiers : `Agenda{,Regles,Confidentialite}.php`, bloc d'amorçage B-07 additif, deux gabarits événement, `tests/AgendaReglesTest.php`, `wp/{outils,tests}/demo/b07*`, paquet `production/B-07/`.
- Incidents corrigés, reçus rouges conservés : permissions de retrait du témoin MU, préférence UI admin native remise à absence, mauvais nom de callback attendu, export natif d'inscrits fermé après rouge/vert, en-têtes Date comparés à tort, nonce REST manquant au harnais abonné. Aucun bloquant restant.
- Décisions à défaut : pas de migration éditoriale/licence, pas de consentement marketing imposé, dates/heures du fuseau WordPress ; validation visuelle de Ced seule restante.

Commandes de contrôle : `python production/B-07/verifier.py` ; parcours rejouables avec nom neuf dans `A-VOIR.md`. Aucun verrou, autre voie/site, bibliothèque close, document d'orchestration, Git ou rapport parent touché.
