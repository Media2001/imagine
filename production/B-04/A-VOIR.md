# B-04 — À voir sur la démonstration fictive

**Prêt à relire, sans validation graphique ni autorisation de mise en ligne.** L’arrêt précédent est conservé dans `historique-arret/` ; il est remplacé par cette livraison.

Site unique : `http://192.168.129.32:8085` — **imagine-test-demo**. Profils fictifs existants `a-carte` et `p-numero`, identifiants conservés hors dépôt.

## Adresses

- Kiosque : `http://192.168.129.32:8085/numeros/` — cinq numéros, couverture et titre natifs, date éditoriale décroissante, statut issu de C08/C11. Pagination native, taille du site conservée (10). La preuve sur trois pages de taille 2 est dans `catalogue-final.json`, sans changement de réglage.
- Numéro 11 : `http://192.168.129.32:8085/numeros/demo-2026-t1/`.
- Numéro 39 : `http://192.168.129.32:8085/numeros/demo-2026-t4/`.
- Thématique : `http://192.168.129.32:8085/thematiques/demo-thematique-1/` — articles de plusieurs numéros, statut identique à celui de leur destination ; les trois thématiques sont testées.
- Destination publique du bouton C14 : `http://192.168.129.32:8085/product/b04-produit-fictif-numero-11/` — **FICTIF B04**, produit simple natif à zéro euro. Ne pas passer commande. Le produit historique 271 reste privé ; le magasin et le checkout restent en « coming soon ».

## Comparer les trois visiteurs sur les DEUX mêmes numéros

| Visiteur | Numéro 11 | Numéro 39 |
|---|---|---|
| Anonyme | Articles réservés + article libre ; bouton Acheter ; aucun lien/indice PDF | Articles réservés + article libre ; aucun PDF ; aucun produit public C14 associé, donc aucun achat inventé |
| a-carte | Articles ouverts selon C08 ; PDF antérieur fermé par le réglage existant ; bouton d’achat disponible | Articles ouverts et PDF ; pas de bouton d’achat |
| p-numero | Numéro acheté : articles ouverts et PDF ; pas de bouton d’achat | Autre numéro : articles réservés sauf libre ; aucun PDF ni achat inventé |

Chaque page numéro comporte une présentation publique, un article libre mis en avant, un sommaire détaillé avec libellés textuels et liens réels, et l’emplacement nommé « Sommaire audio », **sans lecteur ni fichier**. Les liens du sommaire ont aussi été suivis pour vérifier le texte réellement servi. Le PDF reste servi par C11, jamais par une adresse physique.

Captures finales : `captures/` (16 images, 1280 et 375 px). Géométrie, focus et navigation au clavier : `browser.json`. Mesure sur vingt vrais articles : `queries-20.json` ; le numéro, ses vingt articles et le contrôleur HTTP temporaire ont été retirés exactement après mesure.

Référence de livraison : `verification-finale.json` ; détails et décisions dans `RAPPORT.md`. Le designer doit encore fixer les points de `besoins-designer.md`.
