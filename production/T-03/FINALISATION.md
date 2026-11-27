# T-03 — finalisation conditionnelle, candidat courant sans PRET

**A-20 est inclus** par consigne du 27 novembre à 7 h 30, postérieure à la fusion. Voir **RECEPTION-CORRECTIONS.md** pour les six instructions et les commandes. L'ancien PRET de 8 h 14 et son paquet sont archivés hors dépôt avant correction ; le seul paquet courant est `preuves/final/`.

Les gates de reprise donnent A-31 `A31_PARTIAL_EVIDENCE` et A-32 `A32_PACKAGE_DRIFT` : **aucun PRET courant**, même avec REJEU PASS. Le manifeste reste donc candidat, `readiness_claimed:false`, `parent_final_gates_pending:true`.

**`verify-corrections.py` ne vaut qu'avant PRET**, pas comme lecteur final. `sceller-candidat.py` régénère le seul sceau candidat par ses contrôles et restaure l'ancien manifeste en cas d'erreur. Après traitement A-32 et gates A-31 par le parent : nouvelle qualification, baseline sans rouge A-20/A-32 compris, preuve réelle nominale/un octet, synchronisation des documents et du manifeste final, PRET seulement justifié puis vérification/rejeu indépendant. Aucun fichier commun gelé ne doit changer. Aucun GO.
