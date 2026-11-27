1. Réveil de diagnostic autorisé consommé le 27/11/2026 : aucun nouvel essai A-29 sans consigne ; pas de PRET.
2. Commande réelle : C:/Python314/python.exe -B wp/tests/a29/run.py --parent-serialized --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-reveil-20261127-serial/a29-diagnostic ; sortie 1.
3. PHP pur : 42 contrôles verts ; banc natif classique/HPOS : 168 contrôles dont 164 PASS et 4 FAIL (deux neutral_success et leurs exceptions).
4. Lecture nominale, canaux, empreintes DB/fichiers, canaris et confinement sont verts jusqu'au clone neutralisé ; le moteur d'import réel a été exercé sans modification.
5. Sur chacun des deux magasins neutralisés, le gardien refuse correctement par A29_PROCESS_OUTPUT_INVALID ; sortie publique vide, aucun faux succès.
6. Le diagnostic PHP conserve le même confinement noyau/SQL : sortie réelle 255 après protocole de succès et liaison finale, stderr vide ; ce résultat n'est pas une acceptance.
7. Les onze indicateurs fermés d'erreur native restent faux : la cause du 255 n'est pas établie et l'immutabilité de cette lecture neutralisée n'est pas certifiée.
8. Hypothèse 1 non prouvée : un callback de fin de requête WordPress/Action Scheduler échoue après la neutralisation sous les interdictions d'écriture ; il faut identifier le callback exact.
9. Hypothèse 2 non prouvée : un destructeur ou une écriture de journal Woo/WCS échoue au démontage du processus après la liaison finale ; il faut une trace de fin de processus bornée sur fixture.
10. Aucun compteur/canari retiré, aucun import/gardien/lanceur changé ; runner possédé nettoyé (contrôle cleanup vert), aucune nouvelle réparation tentée, décision à Claude/Ced.
