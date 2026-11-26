# A-16 — Rapport candidat, retouche du 26/11/2026 (file 10 h 30)

- **Fait** : `A16_MAPPING_KEY_ABSENT` nomme seulement `numero_type`, `thematique`, `pdf_cle`, `liaison.cle`, jamais la valeur. Runtime commun et autres outils inchangés.
- **Prêt à relire** : candidat vérifié, aucun `PRET` avant préparation commune du parent.
- **À arbitrer par Ced** : rien.
- **Bloqué** : pas de blocage technique ; préparation d'image réservée au parent.
- **Ensuite** : parent rattache son reçu de préparation, rescelle, vérifie sans `--candidate`, puis décide de `PRET`.

## Résultats réels

Paquet unique : `production/A-16/preuves/final/`. Dernier run cp1252 à sa racine, UTF-8 dans `utf8/`. Commandes intégrales et environnements dans `windows-matrix.json`. Python Windows natif **C:/Python314/python.exe, 3.14.6**, locale cp1252. Deux contextes : `PYTHONIOENCODING=utf-8/PYTHONUTF8=1` et `PYTHONIOENCODING=cp1252/PYTHONUTF8=0`. Décodage explicite des sous-processus Windows ; tests Python fixant l'encodage des enfants.

Par contexte : **23 assertions PHP, 78 contrôles natifs classic/HPOS, 7 gardes runner, 3 tests Python**, zéro échec. PSR-12 strict : **0 erreur, 0 avertissement**. PHP seulement en conteneurs jetables sans réseau/montage/port, suppression vérifiée par nom exact.

Un test par champ et magasin : refus exact `A16_MAPPING_KEY_ABSENT {"field":"..."}`, stdout vide, valeur canari absente et aucun fichier produit. Lien symbolique au nom canari : refus muet dans les deux magasins. Commande du README extraite, chemins fictifs substitués, **aucun argument ajouté**, exécution native verte classic et HPOS. Empreintes base entière et fichiers inchangées, cas PDF privés, dates égales et orphelins hors N toujours verts.

## TDD et commandes

RED probant : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a16-retouche-red-exact-20261126/result.json` : **78 contrôles, 8 échecs attendus**, un par champ/magasin, tous sur l'ancien refus sans champ. GREEN : **78/78** dans les deux contextes. Un premier essai avait un point dans le nom du dossier de sortie `liaison.cle` : nom de banc corrigé avant le RED probant, garde de l'outil inchangée.

Depuis `C:/Users/Ced/imagine` :
- RED, UTF-8 : `C:/Python314/python.exe -B wp/tests/a16/run.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a16-retouche-red-exact-20261126` (code 1 attendu).
- Matrice GREEN : `C:/Python314/python.exe -B C:/Users/Ced/AppData/Local/hermes/cache/scratch/a16-retouche-matrix.py` (code 0 ; commandes individuelles dans le paquet).
- Candidat : `C:/Python314/python.exe -B wp/tests/a16/verify.py production/A-16/preuves/final --candidate`.

## Décisions prises à défaut / limites

Filtrage fermé au point de sortie A-16 ; aucun changement Runtime. `article_type` et `date_cle`, hors liste arbitrée, restent par code seul. `--candidate` contrôle explicitement l'attente du parent et l'absence de `PRET`, sans fabriquer de préparation ; sans ce drapeau, le reçu de préparation réel reste obligatoire. Anciennes preuves et RED hors dépôt. Aucun `preparer-image.ps1`, T01 global, verrou, Git, donnée réelle, archive, compte, staging ou déploiement touché.
