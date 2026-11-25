# Propositions documentaires C-14 — à intégrer par Claude, pas un arbitrage acquis

25 novembre 2026. Références fermées : `corrections/C-14.md` instructions 1–6, doctrine §4, décision du 22 novembre (`docs/decisions.md:29`), cahier §3.7 et §3.9. **Aucun fichier `docs/`, brief ou relecture n’a été modifié.** Ce fichier satisfait l’instruction de proposition, pas l’autorisation d’écrire dans ces dossiers.

## Proposition pour `docs/ecarts.md`

- **C14 — référence du brief.** `briefs/C-14-achat-au-numero.md` cite §3.11, qui traite des événements. Les références applicables à l’achat unitaire sont **§3.7 (achat invité/compte)** et **§3.9 (articles et PDF du numéro acquis sans limite de durée)**. Le raccord corrigé suit ces dispositions ; la maintenance du catalogue ne révoque ni ne déplace un achat historique.
- **C14 — achat invité.** Le §3.7 permet l’achat papier sans compte et propose ensuite la création d’un compte ; le rattachement numérique après achat reste à confirmer au chapitre 7. Dans la démonstration, aucun rapprochement par email ni parcours de revendication n’est livré : sans propriétaire natif connecté, accès fermé. Question fermée pour Imagine : « L’achat invité ouvre-t-il le numérique après création de compte — oui/non ? » Ce n’est pas un silence complet du cahier.

## Proposition pour `docs/decisions.md` — rubrique réglages en attente Imagine

**Ne pas présenter ceci comme une décision métier déjà tranchée par Ced/Imagine.** La décision du 22 novembre impose le mécanisme configurable, pas le choix métier final.

- **C14 — portée d’un remboursement partiel.** Réglage livré dans **Réglages → Achats de numéros**, option `imagine_achat_remboursement=commande|ligne`, capacité `manage_options`, Settings API native.
- **Défaut prudent `commande`** : tout remboursement natif, même partiel et sans ventilation, retire les acquisitions de cette commande. Valeur absente/invalide : même défaut fermé.
- **Alternative `ligne`** : seul un remboursement natif référencé par `_refunded_item_id` retire l’achat de cette ligne produit, même si la quantité remboursée est partielle. Les autres lignes restent acquises ; un partiel non ventilé (ou seulement sur le port) n’identifie aucune ligne produit, donc ne retire aucun de ces achats.
- **Complet** : tous les achats de la commande restent révoqués dans les deux modes (état natif `refunded`, ou remboursement monétaire total pour une commande de montant strictement positif). Une autre commande valide est indépendante.
- **Question fermée pour Imagine** : « On ferme tous les accès d’une commande sur tout remboursement, même partiel/non ventilé — oui/non ? » Oui = défaut `commande`, non = alternative `ligne`, dont le comportement du non ventilé est explicitement décrit ci-dessus. Le lot n’attend pas la réponse.
- Les deux valeurs ont des oracles purs, natifs et HTTP sur une commande à **deux numéros** : partiel ventilé, non ventilé, complet, articles et PDF. Objets synthétiques zéro euro, aucune passerelle ni transfert. Voir `COMMANDES.md` et reçus C14.

## Limites de la livraison

PRET initial existant, non modifié. Corrections à relire, ni clôture ni GO réel. Optimisation N+1 remboursements laissée optionnelle (volume démo). Incident des 12 observations synthétiques C13 antérieures au wrapper transactionnel décrit dans `RAPPORT.md`, pas effacé ni masqué.
