# B-04 — À voir sur la démonstration fictive

**Corrections techniques 1–6 appliquées, prêtes à relire ; aucune validation graphique ni autorisation de mise en ligne.** La preuve courante est `verification-corrections-finale.json`. Les reçus de première livraison (`verification-finale.json`, ancien PRET conservé) sont historiques.

Le statut ajouté au kiosque est **conservé à l'identique**, en attente du oui/non de Ced (point 7 de la fusion) ; cette décision visuelle ne bloque pas les corrections techniques.

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

Référence courante : `verification-corrections-finale.json` ; commandes dans `COMMANDES-CORRECTIONS.md`, décisions et limites dans `CORRECTIONS.md`. Le designer doit encore fixer les points de `besoins-designer.md`.

## Deux régressions corrigées, preuve ciblée

- **Découverte** : `wp/tests/demo/b04-corrections.py http parent` utilise le profil fictif **V-DEC**, le témoin `/c12-decouverte-un/` et le numéro 39. La recette active temporairement les réglages de test, vérifie deux visites au sommaire et à une thématique : **« Découverte » sans ouvrir ni consommer le quota** ; le clic réel sur l'article consomme ensuite exactement une lecture. État, réglages, confirmation fictive et rattachement thématique sont remis exactement à leur valeur initiale. Le défaut de la démo reste donc fermé après recette : ne pas attendre un badge Découverte permanent sans activer le réglage.
- **Numéro acheté avant sortie** : la même recette réutilise la possession native du 11 par **p-numero**, sans commande neuve ni paiement. Date éditoriale temporairement future : **aucun bouton d'achat, PDF fermé**, y compris sur sa route directe. Une fois sorti : toujours aucun bouton d'achat, PDF réel ouvert. Date originale ensuite restaurée ; la seconde exacte est couverte séparément par PHPUnit.
- **Sommaire** : le lien redondant « Dans le numéro : ce numéro » n'est plus répété sur la page numéro ; il demeure utile sur les pages thématiques. Les extraits et liens d'articles restent les mêmes.
- **Produit public** : même destination native qu'avant ; son exemption de démonstration réside dans le seul mu-plugin local issu de `wp/outils/demo/b04-preview.php`, plus dans le thème livré.

Les captures `anonyme-375-numero11.png` et `p-numero-1280-numero11.png` ont aussi été inspectées : anonyme réservé/achat/sans PDF ; acheteur ouvert/PDF/sans achat ; pas de répétition du numéro ni de débordement visible. Aucune décision d'habillage prise.

