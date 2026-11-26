# A-14 — livraison

Un seul paquet : `preuves/final/` (dernier rejeu vert). Commande de contrôle depuis la racine : `python wp/tests/a14/verify.py production/A-14/preuves/final`.

8 assertions PHP, 2 méthodes unittest de lecture CSV (plus sous-cas), 55 assertions natives classic/HPOS, 8 gardes du runner : verts. Les personnes, emails, abonnements et le CSV de 30 lignes sont entièrement fictifs. Comparaison des tables complètes et fichiers avant/après, garde mail/HTTP/cron/écritures effectivement exercée. Exclusion sans-email, doublons, anomalies par ligne physique et ambiguïté entre comptes prouvés ; aucun rapprochement fournisseur. Préparation T01 réellement relancée (`preparation.json`, code 0).

Décisions prises à défaut : plusieurs comptes au même email normalisé = ambiguïté bloquant uniquement cette ligne, jamais premier compte choisi ; aucun statut d'abonnement attribué. Statut newsletter non configuré = inconnu, pas inscrit. `active` signifie strictement l'état natif, les champs coopérateur et tarif restent vides. Réemploi A11/A12/A13 sans modification ; manifeste du lot seul, dépendances seulement observées pour la stabilité pendant le run. Aucun bootstrap supplémentaire.

Limites : pas de fichier tableur binaire (exporter CSV), pas de test réel, pas de GO sur sauvegarde/site/contact réel. Mise en lecture autorisée à part par Ced sur copie vérifiée. Les drop-ins et symlinks sont refusés avec nom, sans les désactiver : mode d'emploi `wp/outils/bascule/a14/README.md`.
