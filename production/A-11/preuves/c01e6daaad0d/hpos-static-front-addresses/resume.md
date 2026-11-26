# Adresses publiques — lecture seule

24 adresses uniques. Aucun plan de redirections décidé.

## Par nature

- archive d'auteur : 2
- archive de type de contenu : 3
- article : 3
- page : 3
- pièce jointe : 3
- produit : 1
- terme de taxonomie : 11

Une adresse commune (page boutique et archive produit) garde tous ses contextes; les nombres par nature ne sont pas additifs.

## Exclus (comptés, jamais listés) et permaliens

```json
{
    "exclus": {
        "draft": 1,
        "private": 1,
        "password": 1,
        "attachment_parent_not_public": 1,
        "attachment_pages_disabled": 0
    },
    "autres_etats_non_listes": [],
    "permaliens": {
        "structure": "\/%category%\/%postname%\/",
        "base_categories": "rubriques",
        "base_etiquettes": "mots",
        "woocommerce": {
            "product_base": "\/boutique\/%product_cat%",
            "category_base": "familles",
            "tag_base": "etiquettes",
            "attribute_base": "attributs",
            "use_verbose_page_rules": false,
            "product_rewrite_slug": "\/boutique\/%product_cat%",
            "category_rewrite_slug": "familles",
            "tag_rewrite_slug": "etiquettes",
            "attribute_rewrite_slug": "attributs"
        }
    }
}
```

Dates UTC des contenus seulement; les archives et termes n'ont pas de date native de modification : cellule vide. Pièces jointes : pages natives, pas fichiers téléchargeables.
