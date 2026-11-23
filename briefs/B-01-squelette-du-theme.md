# Lot B-01 — Le squelette du thème

**Voie** : 2. **Chantier** : B. **Nature** : thème WordPress, structure sans habillage. **Délai** : une demi-journée.
**Dépend de** : B-00 (tu construis dessus dès qu'il est `PRET`, sans attendre sa clôture).

## Pourquoi

Les maquettes arrivent plus tard, et elles apporteront un système de design (couleurs, typographies, espacements) et une page par gabarit. Tout ce qui ne dépend pas d'elles peut exister maintenant : la liste des gabarits, ce que chacun affiche, d'où viennent les données. Le jour où les maquettes arrivent, il ne restera qu'à habiller.

## Ce qu'on veut

Dans `wp/themes/imagine/`, un thème qui s'active sur le site de démonstration et sert, **sans aucun parti pris graphique** :

| Gabarit | Affiche |
|---|---|
| Accueil | Dernier numéro, derniers articles, entrées vers kiosque, thématiques, agenda |
| Kiosque | Tous les numéros, du plus récent au plus ancien, hors-séries compris |
| Numéro | Couverture, sommaire (articles du numéro), lien vers le PDF |
| Article | Titre, chapô, auteur, numéro d'appartenance, thématiques, corps |
| Thématique | Articles de la thématique |
| Agenda et événement | Liste et fiche |
| Partenaire | Liste et fiche |
| Page simple, recherche, 404 | Le minimum |
| En-tête et pied | Navigation, accès au compte, lien d'abonnement |

- **Apparence volontairement neutre** : une feuille de style minimale, noir sur blanc, une seule colonne lisible, aucune couleur de marque, aucune police chargée. Tu ne devances pas le designer. Chaque page porte une mention discrète « squelette, sans habillage ».
- **Prêt pour le système de design** : toutes les valeurs visuelles passent par des variables (un seul fichier, `theme.json` ou variables CSS, à ton choix, dis lequel et pourquoi en deux lignes). Rien en dur dans les gabarits.
- **Sémantique et accessibilité de base** : un seul `h1`, titres hiérarchisés, repères `header` / `nav` / `main` / `footer`, liens d'évitement, textes alternatifs. C'est de la structure, pas du design.
- **Le corps de l'article** passe par **un seul point de sortie** (une fonction du thème), que C-08 branchera sur la décision d'accès. Dans ce lot, il affiche le texte complet.
- Pas de constructeur de pages, pas de dépendance à une extension tierce, pas de JavaScript sauf nécessité.

## Hors périmètre

Le mode lecture, le tunnel d'abonnement, l'espace « mon compte », la performance fine : plus tard, avec les maquettes.

## Livrables

- Le thème, activé par le script de B-00 (tu peux modifier ce script).
- `production/B-01/A-VOIR.md` : une adresse par gabarit, et ce que Ced doit y voir.
- `production/B-01/notes.md` : la liste des gabarits, et **ce dont tu auras besoin du designer** pour chacun (une liste courte, que Claude transmettra telle quelle ou non).
- Preuve : réponse HTTP de chaque adresse, validation HTML sans erreur de structure.
- `production/B-01/PRET`.
