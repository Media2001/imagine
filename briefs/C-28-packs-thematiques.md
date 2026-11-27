# Lot C-28 — Les packs thématiques d'anciens numéros

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : C-14 (achat au numéro), C-06, C-11, B-04, B-02. **Cahier des charges** : §3.3 (« Packs thématiques d'anciens numéros, vendus comme produits groupés »), §3.1 (zone 2 : « numéros achetés à l'unité »). Relis-les.

## Pourquoi

Imagine veut vendre plusieurs anciens numéros d'un coup, autour d'un thème. L'achat d'un numéro existe (C-14) : il ouvre les articles et le PDF de ce numéro, et rien d'autre. Un pack doit ouvrir la même chose, numéro par numéro, sans seconde mécanique de droits.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : ce que le « produit groupé » natif de WooCommerce fait et ne fait pas (un prix pour l'ensemble, ou seulement des produits ajoutés un à un), ce qu'une extension payante ajouterait, et ton choix. Aucune extension commerciale n'est activée.

- Un pack est un produit rattaché à une **liste de numéros** choisie par la rédaction dans l'administration.
- Une page de pack : son titre, les numéros qu'il contient (couverture, titre, date, comme le kiosque de B-04), un bouton d'achat. Prix manifestement fictif.
- L'achat **payé** ouvre, pour chaque numéro du pack, exactement ce que C-14 ouvre pour un numéro acheté seul, **par la même décision d'accès**. Aucune règle d'accès nouvelle.
- Dans « Mon compte », les numéros d'un pack apparaissent avec les numéros achetés.
- Le remboursement suit le réglage de C-14, tel quel.

Règles :

- les droits portent sur **les numéros que le pack contenait au moment du paiement** : si la rédaction retire ou ajoute un numéro ensuite, les acheteurs passés gardent ce qu'ils ont acheté, ni plus ni moins. C'est le défaut prudent ; la question est rangée pour Imagine ;
- un pack dont un numéro est déjà possédé se vend quand même, sans remise calculée : si tu penses qu'il faut autre chose, c'est une question que tu notes, pas une règle que tu inventes ;
- paiement fictif, déclaré comme tel, comme dans C-14 ; les profils de C-09 sont remis dans leur état de départ ;
- aucun style inventé : le squelette de B-01.

## Preuve

Proportionnée. Un pack d'essai de trois numéros : avant paiement, rien n'est ouvert ; après paiement, les articles et le PDF des trois numéros s'ouvrent pour l'acheteur et pour lui seul ; un quatrième numéro ajouté au pack après coup ne s'ouvre pas pour lui ; un numéro retiré reste ouvert ; le remboursement fait ce que le réglage de C-14 dit. Le texte réservé ne sort par aucune voie pour un anonyme sur la page du pack (les témoins de C-26). Données d'essai laissées en place, déclarées fictives dans `A-VOIR.md`.

## Livrables

Le code, ses tests, la section du README de l'extension, `production/C-28/A-VOIR.md`, `PRET`. Rapport court.
