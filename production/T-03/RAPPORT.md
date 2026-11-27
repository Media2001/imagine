# T-03 — rapport court

1. **Fait :** chaine de rejeu de paquets ajoutee, declaration fermee, journaux absents hors rejeu, ligne PAQUETS independante ; trois lignes exactes dans le mode d'emploi T-01.
2. **Pret a relire :** candidat de code seulement ; aucun `PRET`.
3. **A integrer par le parent :** wrappers/declarations des lots 20–29 avant leurs gels, preparation de l'image Python puis preuve reelle A-22/A-28 ; commandes exactes dans `RECEPTION-PARENT.md`.
4. **Bloque :** reception native volontairement non executee (Docker/WSL reserve a A-28, PHP Windows interdit) ; aucune preuve native ni nombre de tests PHP invente.
5. **Ensuite :** parent execute `test-paquets-native.ps1` : copie scratch, un seul octet de recu modifie, A-28 PACKAGE_DRIFT seul, meme REJEU PASS et memes tests, deux absences de conteneurs relues, copie supprimee.

Contrats finaux locaux : **15 tests du collecteur + 8 tests d'integration**, verts en Python **3.14.6 Windows**, stdout/stderr UTF-8 puis cp1252/PYTHONUTF8=0 mesures. Frontieres historiques simulees : **18/18 T-01**, **7/7 T-02** dans chaque contexte. Ces doubles ne lancent pas le vrai transport WSL/Docker et ne sont pas des recus PHP. RED dans le scratch seulement ; preuves finales locales : `preuves/local/result.json` et sorties `.txt`.

Ni Git ni `scripts/relire.ps1`, autre lot/verificateur, gardien ou import touches par T-03. Surveillance : une modification concurrente de `wp/outils/staging/lib.php` a ete observee et signalee au parent ; les empreintes du gardien commun sont inchangees. Le preparateur d'image est inchange ; seul son Dockerfile installe Python. Aucun conteneur cree par ce worker, donc aucun conteneur a nettoyer ici. Les nombres natifs verifies/hors rejeu restent a mesurer par le parent, pas a deduire des contrats.
