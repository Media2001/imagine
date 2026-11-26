# B-07 — huit corrections fusion21h41 appliquées

- R1 : le filtre B05 traite les seuls corps d'événements partenaires ; destinations ambiguës commerciales, liens internes et rencontres préservés. Extension minimale de `functions.php`, reste du thème intact.
- R4 : l'export renvoie `WP_Error` sur lecture ratée ; panne SQL transitoire aux pages 1 et 2 puis reprise sans omission, 121 inscriptions paginées 50/50/21 et effacées.
- R2 : projection commune HTML/texte ; la fiche et le JSON-LD réutilisent le même rendu, shortcode exécuté une fois. Égalité exacte du texte vérifiée horslive et en vrai HTTP.
- Partenaire passé : étiquette/lien conservés, ni formulaire ni « inscriptions closes ». i18n : types/champs en littéraux extractibles, domaine thème `imagine`. Saisie invalide signalée en édition ; ternaire d'archive retiré.
- Preuve canonique : **9 tests / 159 assertions Agenda**, 7 tests adaptateur neufs découverts par le runner existant ; **6 mutants de sources jetables exécutés et détectés**, aucune mutation de réponse comptée comme parcours. Image préparée et suite générale **1 135 tests / 35 709 assertions, zéro échec/erreur/ignoré** ; outils : 18 / 417 verts.
- Recettes vraies : HTTP/WP **26 contrôles**, confidentialité native **18**, ancien chemin confidentialité **9**, readback indépendant **6**, tous verts. Zéro transport mail/HTTP, 19 tentatives HTTP d'infrastructure bloquées, zéro appel agenda. État métier initial exact, réglages/événements/métadonnées préservés, fixtures/sessions d'essai et observateur retirés.
- Incident conservé : premier parcours fonctionnel vert mais état rouge à cause du post de styles créé par l'éditeur WordPress ; inverse exact, readback initial vert, harnais corrigé puis recette finale verte. Aucune restauration supplémentaire de cache/session exigée. Historiques et rouges non écrasés.
- Fichiers : `Agenda.php`, `AgendaConfidentialite.php`, `tests/Agenda{AdapterTest,WPStubs}.php`, deux gabarits événement et seul filtre de `functions.php`, nouveaux harnais `wp/{outils,tests}/demo/b07-*`, paquet courant `manifest-correction2141.json`, vérificateur, `A-VOIR.md` et `PRET`.
- Aucun blocage technique restant. Validation visuelle de Ced seule attendue. Ni PSR-12 global, ni anti-spam, ni bibliothèque close/bootstrap, autre voie/site, réel, Git ou rapport parent touchés.

Commandes : `python production/B-07/verifier.py` ; `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1`. Rejeux ciblés et recettes à noms neufs : `A-VOIR.md`.

## Historique initial — chiffres et preuves remplacés par ceux ci-dessus

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
