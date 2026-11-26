# A-29 — Rapport court du 27 novembre 2026

**Fait :** inventaire lecture seule des tâches WP-Cron/Action Scheduler, schéma fermé K5, horloge de l'audit UTC, retards, huit fenêtres de renouvellement et échecs AS ; banques PHP pur/classique/HPOS et réception parent préparées.
**Prêt à relire :** aucun `PRET` ; paquet local **Python seulement**, explicitement partiel.
**À valider/arbitrer par Ced :** aucune question technique bloquante ; aucun accès au réel demandé ou autorisé.
**Bloqué :** qualification PHP installé, PSR-12, natif, immutabilité DB/fichiers et portes Docker/WSL réservées au parent ; non exécutées ici.
**Ensuite :** fin d'A-28, gel des sources, puis commandes exactes de `RECEPTION-PARENT.md` : style, matrice native, vérificateur, portes communes, paquet unique et sceau.

## Résultats réellement mesurés

- Windows, `C:/Python314/python.exe` **3.14.6** : **42 tests verts par contexte**, UTF-8/mode 1 puis cp1252/mode 0. Encodages stdout/stderr et locale mesurés dans le paquet.
- RED/GREEN Python réels dans les deux encodages : baseline verte, mutation du seuil K5 rouge (code 1), octets restaurés puis vert. Copies jetables seulement. Les échecs de construction initiaux restent en scratch, pas un deuxième paquet livré.
- Vrais enfants Python, deux flux et descendant conservant les pipes ; parcours Python de publication, cinq canaux et altération silencieuse JSON/Markdown cohérente. Les frontières PHP et noyau y sont explicitement doublées, **pas validées nativement**.
- `preuves/partiel-python/`, `verification-python-partielle.json`, `manifest-python-partiel.json` : preuve source/dépendances/journaux liée aux octets exécutés. Le contrôleur complet ne peut pas confondre ce paquet avec une matrice native. Les commandes du README et l'import réel sur clone sont préparés, non déclarés exécutés.

## Décisions prises à défaut et limites

- Huit semaines glissantes UTC `[audit+7j×(n−1), audit+7j×n)`, pas d'extrapolation des occurrences futures ; égalité à l'audit non en retard, borne audit+56 jours exclue.
- Historique `failed` **AS uniquement** ; WordPress n'a pas de journal d'échec équivalent. Une file connue à zéro ne prouve pas l'absence d'échecs WP-Cron.
- Aucune attribution inventée d'une tâche inconnue à une extension active : **attribution indéterminée** ; nom, groupe et callback ne prouvent pas l'auteur de planification. Cette limite du nombre demandé est écrite au mode d'emploi.
- L'import existant efface/annule/supprime les tâches pertinentes. Tous les six comptes deviennent **inconnu après neutralisation**, jamais zéro. Aucune modification de l'import, aucune lecture de la source réelle ; oracle par moteur commun inchangé sur clone fictif réservé au rejeu parent.
- Documentation officielle consultée et provenance conservée ; confrontation au code installé réservée au parent. A-28 peut encore changer `staging/lib.php` : une nouvelle empreinte ne rend pas un ancien rejeu valide ; le vérificateur refuse ce décalage.
- Seuls `wp/outils/bascule/a29/`, `wp/tests/a29/`, `production/A-29/` et scratch écrits. Gardien A-22, infrastructure commune, lots A-26/A-27, README partagé et verrous non modifiés. Les deux lignes LF de `readme-ajout.txt` restent à intégrer par le parent. Aucun Docker/WSL/PHP Windows, Git, archive, compte, site ou Novamira utilisé.
