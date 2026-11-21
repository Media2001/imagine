A-01 — BLOQUÉ PARTIELLEMENT, 21 novembre 2026

Sous-lot d'import/vérification hors ligne et fidélité synthétique : PASS.
Staging complet publiable : NON PRÊT ; aucun PRET ni GO déposé.

Preuve : tests-21nov/120fc4c09863/result.json.
Suite native fraîche : wp/tests/staging-e2e/evidence/9ff611303d90/.
Rapport : files/rapports/2026-11-21-A-01-chemin-court.md.
Guide : wp/outils/staging-court/README.md.

PUBLICATION_AND_UPDATE_EGRESS_NOT_IMPLEMENTED : pas de port ni sortie réseau général ouverts pour masquer le manque. Le vrai entrypoint testé retourne 78, imported, DATA_VERIFIED_PUBLICATION_BLOCKED. Le prototype partagé présent dans le checkout élimine les fichiers ; toute nouvelle orchestration réseau/frontend demanderait de dépasser le chemin court. Aucune source hors checkout ni service partagé recherché/modifié. Formats SQL/archives/versions hors sous-ensemble non qualifiés.

Seul Ced pourra importer. Ne pas utiliser cette branche contre une archive réelle avant qualification/adoption explicite. Aucun accès à l'ancienne copie, au site ou à Novamira n'a eu lieu.
