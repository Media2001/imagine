# B-08 — À voir

Démonstration fictive uniquement : `http://192.168.129.32:8085` (`imagine-test-demo`). Aucun service réel raccordé.

- `/` : menu **WordPress natif**, dans l’ordre §3.1 ; « Notre coopérative » et « Soutenir » ouvrent les bonnes pages. Les sept sous-pages sont sous « Notre coopérative ». « Proposer un sujet » n’y figure pas.
- `/notre-cooperative/` : sept liens aux intitulés du §3.12, lien discret « Proposer un sujet », lien « Espace coopérateurs ». Ce dernier garde les restrictions de B-06 ; aucun droit n’est donné par ce lien.
- Sous-pages vides, sans texte éditorial ajouté : `projet-editorial-et-manifeste/`, `charte-independance/`, `charte-ia/`, `barometre-egalite-diversite/`, `equipe/`, `gouvernance/`, `imagine-coop/`, sous `/notre-cooperative/`. Chaque page permet de revenir à sa racine. Les titres enregistrés sont exactement ceux du CDC ; WordPress applique sa typographie habituelle aux apostrophes à l’affichage.
- `/soutenir/` : **abonnement**, puis **bénévolat** vide, puis **prise de parts** sans lien. L’abonnement pointe sur le « S’abonner » déjà livré, `/#imagine-abonnement` : cet emplacement ne constitue pas un tunnel d’achat nouveau.
- Administration → Réglages → Soutenir : don **OFF**, adresse de parts **vide**. Cocher le don affiche à sa place prévue « don ponctuel ou récurrent » et l’emplacement explicitement « sans paiement ». Aucun don ne peut être fait. Une adresse fictive `https://example.org/parts-fictives` a été utilisée pour vérifier le lien `rel="sponsored"`, puis retirée. **Aucune adresse CoopHub réelle n’est demandée.**
- `/proposer-un-sujet/` : nom, email, sujet et consentement **facultatif, décoché** au recontact. Enregistrer garde la proposition localement ; aucun message ne part et aucune recherche de compte n’est faite.
- Administration → Propositions de sujets : liste native privée, détail réservé à `manage_options`, avec nom, adresse, sujet, consentement et date UTC. La recette a retiré ses propositions : liste vide avant votre propre essai.
- Outils natifs d’export/effacement : « Propositions de sujets », par adresse email ; cela retrouve notamment les propositions de l’adresse d’un compte. Pas de modification de C-21 ni de sa politique de conservation.

## État rendu

Pages et menu conservés, aucun texte inventé, aucun style ajouté. Réglages remis à l’état initial fermé ; propositions et observateur d’essai supprimés. Préimages privées durables avant toute session, restauration exacte métier vérifiée (classique, HPOS, comptes, navigation et options métier). Ces pages sont publiques : matrice C-23 inchangée ; C-26 suit.

Validation visuelle de Ced attendue. Ce lot n’est ni un accord de déploiement, ni un raccordement à CoopHub, ni une activation du don en 2027.
