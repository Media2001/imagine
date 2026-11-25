# B-04 — Arrêt sur prérequis manquants

**Fait** : lecture de la file de 19h30, consigne, doctrine, §3.3, décisions et interfaces C08/C11/C14 ; premier tracer-bullet TDD exécuté.
**Prêt à relire** : aucun PRET déposé en fin de passage. B03 fonctionnellement vert, mais son PRET a été retiré après détection de quatre empreintes de tables changées pendant le travail C15 parallèle (voir le rapport B03). **B04 n’est pas PRET.**
**À décider par le parent** : autoriser un complément ciblé des données fictives, hors du périmètre d’écriture confié à ce worker.
**Bloqué** : aucun produit WooCommerce publié ; aucun numéro de vingt articles disponible.
**Ensuite** : lot arrêté conformément à la demande, sans fabriquer d’objet, de droit ou de parcours d’achat.

## Constat vérifié sur imagine-test-demo

`blocage-catalogue.json`, inventaire natif en lecture seule : **8 produits, tous privés**. Le seul produit simple est **271**, lié au **numéro 11**, avec prix enregistré, mais `post_status=private`. Un visiteur anonyme ne peut donc pas suivre un vrai parcours public C14. Publier ce produit ou en créer un dépasserait les chemins autorisés ; aucun produit n’a été modifié. L’absence de bouton ne peut pas être présentée comme conforme à l’exigence « il apparaît à l’anonyme ».

Les **5 numéros** contiennent **26 articles** au total, **6 au maximum par numéro**. La mesure demandée sur un véritable sommaire de vingt articles n’a pas été exécutée ; vingt lectures répétées ou des objets réaffectés auraient été une autre mesure, pas la preuve demandée. Pas de seed ni d’injection d’objet ou de métadonnée.

Les droits existants diffèrent réellement : `p-numero` reçoit le PDF du numéro 11 ; `a-carte` reçoit celui du numéro 39, mais pas celui du numéro 11 (`pdf_anterieur_ferme_par_reglage`). Aucun droit n’a été changé pour aligner la démonstration.

## Travail conservé et état final

- Fonction de présentation pure `imagine_access_status`, sans recalcul de droits : **rouge natif**, puis **11 contrôles PHP verts**. Le candidat exact est conservé dans `catalogue-candidat.php`, lié par SHA-256 dans l’inventaire ; ce n’est pas un thème B04 livré.
- Test HTTP des deux mêmes numéros sous anonyme / A-CARTE / P-NUMERO : **102 contrôles, 68 échecs attendus au stade rouge**, avant gabarits B04. Ce reçu n’est pas une recette réussie. Les marqueurs de corps réservés sont uniquement en mémoire ; aucun cookie, mot de passe ou corps connecté enregistré.
- Le tracer-bullet avait été déployé pour exercer le vrai runtime. À l’arrêt, **restauration exacte des préimages du thème**, localement et à distance : `arret-verifie.json`. Le helper n’est plus inclus ni installé. Les trois gabarits restent ceux d’avant B04. Aucun snapshot de plugin utilisé.
- Suppression du seul nouveau helper refusée par les permissions de WP-CLI ; retrait ciblé effectué depuis le même volume hôte que le transport d’upload, avec contrôle préalable du SHA-256, puis relecture exacte. Aucun droit de fichier ni outil partagé modifié.
- `wp/tests/preparer-image.ps1` relancé sans modification, succès vérifié dans `preparer-image.txt` ; aucun paquet Composer ajouté.

## Déblocage minimal proposé

1. Le parent élargit explicitement le périmètre aux données fictives nécessaires, et publie le produit C14 existant 271 après vérification de son parcours public, ou fournit une autre destination réellement publique. Ne pas créer un simple lien vers le produit privé.
2. Pour la mesure vingt articles : fournir/autoriser un jeu fictif dédié de vingt vrais articles sous un numéro, ou accepter explicitement une mesure distincte sur vingt articles existants, tous numéros confondus.
3. Reprendre le helper depuis son candidat exact, rejouer la tranche TDD, puis les trois gabarits, contrôles HTTP, clavier/mobile et mesure réelle. Aucun PRET avant ces vérifications.

Aucun Git, verrou, file, rapport global, autre site ou plugin modifié par ce worker. Les changements C15 parallèles sont laissés au parent.
