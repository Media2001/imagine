# C-17 — besoins du designer

Écrans natifs fonctionnels, **sans validation visuelle**. Les captures actuelles sont `compte-attente.png`, `compte-valide.png`, `file-referent.png` et `reglage-categories.png` ; elles montrent l'implémentation, pas une proposition graphique.

## Dans Mon compte

- Intégration du bloc solidaire dans la rubrique existante « Mes factures et justificatifs », sans confondre justificatif personnel et facture Odoo.
- Présentation des quatre états : aucun, en attente, validé jusqu'au…, refusé ; état compréhensible sans dépendre de la couleur.
- Hiérarchie de la consigne « Masquez votre numéro de registre national », des formats/taille et de la suppression à la décision.
- Disposition mobile du choix de catégorie, du contrôle de fichier natif et du bouton de dépôt/remplacement ; focus visible, étiquettes et aide conservées. Pas de bibliothèque d'upload ou de prévisualisation exécutante à ajouter.
- Retour visuel après dépôt, refus de dépôt et changement d'état : utiliser les messages serveur existants, sans masquer les refus de sécurité ni promettre un prix ou un accès.

## Côté référent / réglages

- Lisibilité de la file sous Imagine : identité fictive dans la démo, catégorie, téléchargement protégé, date de fin, confirmation de suppression et deux décisions nettement distinguées.
- Prévoir file vide, fichier indisponible, formulaire périmé et suppression impossible ; conserver la confirmation explicite et les champs associés au bon titulaire.
- Maintenir l'insertion du réglage de catégories dans l'écran C10 existant ; pas de nouveau menu principal.

**À ne pas arbitrer visuellement** : catégories d'éligibilité, prix, conséquences sur abonnements/droits, durée et conduite après échéance. Ces questions appartiennent à Imagine. Ce lot n'implémente ni email de relance, ni sanction automatique, ni facture.

Les contrôles de fichier et de date sont ceux du navigateur ; leur apparence et leur langue système peuvent varier. Le rendu doit rester utilisable sans JavaScript. Couleurs, espacements, typographie et composition attendent les maquettes fournies ; aucun design de remplacement n'a été inventé.
