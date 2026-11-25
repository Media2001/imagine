# C-15 — rapport court

- **Fait** : cinq vues natives, un seul menu Imagine, contrôle dédié C09 ; action unique Paiement reçu avec confirmation/nonce/capacité et note Woo datée ; export CSV privé sans données bancaires et protégé contre les formules.
- **Prêt à relire** : 257 contrôles/tests verts ; préparation T01 relancée, sans modifier le préparateur. Voir `verification.json` et `A-VOIR.md`.
- **À valider** : visuel par Ced et relectures du code, pas de GO sur le réel.
- **Bloqué** : rien pour la démonstration demandée. Aucun raccord de bénéficiaire offert/groupé ni profil inventé.
- **Périmètre** : trois classes C15 neuves, bootstrap et README imagine-site ; runners/tests C15 ; ce dossier seulement. Pas de Git, de thème téléversé/modifié, d’adaptateur externe ni de bibliothèque close modifiée.

## Décisions prises à défaut

C09 a volontairement des méthodes de passerelle vides : lecture des identifiants natifs existants A-VIR/A-PAPIER, uniquement sur la cible locale fictive, avec contrôle du marqueur, du manifeste et du propriétaire. A-PAPIER lui-même est la référence fictive, aucun mandat bancaire inventé. Hors démo, méthode native explicite requise. Tous les états et montants restent natifs ; pas de registre de paiement parallèle. Aucun délai de retard nouveau : pas de nouveau réglage C10 nécessaire.

## Incident de recette corrigé

Le premier reset C09 a restauré A-VIR mais déplacé la date payée du profil dépendant P-NUMERO (initialiseur C14). La comparaison l’a détecté. Le runner restaure désormais cette date initiale ainsi que les états découverte C12 ; réexécution complète verte et état sémantique initial relu. L’ancien `restore-diff.json` est conservé comme trace de l’écart, pas comme résultat final. Les notes d’audit natives restent conservées.

Tests C15 autonomes : 18 purs, 21 natifs, 43 HTTP écran/export, 16 HTTP action/reset. Régressions : 10 tests purs C13 / 30 assertions et 149 contrôles de paiements natifs C09. Les relectures après reset sont vertes en plus, sans gonfler le total annoncé. Les empreintes B02/C13/bibliothèques protégées n’ont pas changé. Aucun email ni appel sortant de paiement : garde MU et filtres de transition actifs.
