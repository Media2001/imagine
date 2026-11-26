# A-14 — Livraison après fusion du 26 novembre

A-14 : quatre instructions de fusion appliquées : résumé français traduit et convention par ligne ; API native examinée et SQL conservé avec justification/référence Automattic ; pending-cancel non actif, domaine réservé sans marqueur et deux abonnements actifs pour un seul compte explicitement prouvés sur classic/HPOS. Accounts.php et Matcher.php sont byte-identiques au rendu antérieur, resume.json et ses clés ne changent pas. duplicate_contact_lines compte des lignes, pas une mesure des personnes distinctes.

**Vert : 8 assertions PHP, 63 natives, 8 gardes runner**, 3 tests Python de lecture/transport, zéro échec. Deux rejeux complets classic/HPOS sous **Python natif Windows 3.14.7**, UTF-8 puis **cp1252/PYTHONUTF8=0**, locale cp1252 mesurée. PHPCS strict 0 erreur/0 avertissement ; preparer-image.ps1 relancé code 0 après les nouveaux tests. Version, commandes et encodages : preuves/final/windows-matrix.json et *-environment.json.

Un seul paquet final ; anciens paquets et essais RED/GREEN hors dépôt. Empreintes de toutes tables/options/Action Scheduler et des fichiers identiques avant/après, gardes réellement tentées. Contrôle : `python wp/tests/a14/verify.py production/A-14/preuves/final`, 15 PASS dans les deux contextes. Manifestes bornés au lot, pas à la documentation partagée entière.

Décisions prises à défaut : statut strict active conservé (pending-cancel non actif), comptes par ligne ; aucun droit ou tarif déduit. La question métier reste à Imagine, sans bloquer ce diagnostic.

Limites de méthode des relectures : les relecteurs ne disposaient pas de Docker pour un rejeu natif indépendant. Les preuves présentes sont nos exécutions réelles, pas les leurs. T01 global est un autre périmètre : son échec historique TableauBordReglesTest était voie2, pas corrigé ni requalifié ici. Aucun GO réel, aucun contact/email/site/compte réel.
