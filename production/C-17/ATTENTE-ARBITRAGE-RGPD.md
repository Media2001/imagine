# C-17 — question 5 en attente de Ced

26 novembre 2026. **ATTENTE : donnée personnelle / conservation RGPD. Aucun arbitrage appliqué.** Cette attente reste limitée à C-17 ; les quatre corrections techniques sont prêtes à relire. Elle ne vaut pas autorisation de toucher à une donnée réelle.

Deux prescriptions sont contradictoires :
- CDC §4.4 : ne conserver que **catégorie et date de fin** après décision.
- Brief C-17, règle ligne 20 : conserver **catégorie, décision, date de décision, date de fin et opérateur**.

**Question fermée : Ced confirme-t-il les deux champs du CDC ou les cinq champs du brief ?**

Le modèle existant à cinq champs reste inchangé tant qu'aucun arbitrage écrit ne l'autorise. La recommandation de la fusion n'est pas une décision de Ced. Aucun transfert de ces champs vers le journal C-10, aucune trace d'audit nouvelle, aucun réglage de conservation et aucun hook privacy C-21 ne sont ajoutés. Le marqueur technique temporaire d'indisponibilité ne subsiste pas après une décision réussie.

Décisions et arbitrages du 26 novembre relus : aucun arbitrage de cette question n'y figure à ce rendu. **À Claude : reporter la contradiction brief / CDC dans `docs/ecarts.md` ; Hermès n'a pas écrit dans ce dossier.**

Preuve que le modèle n'a pas été réduit : `corrections-20261126/boundaries-final.json`, contrôle `cinq_champs_conserves_sans_arbitrage_RGPD`, et test pur `testDecisionRemovesAllDocumentReferences`. Le fichier privé disparaît à la décision et à la suppression native de compte ; cela ne tranche pas les champs à conserver après décision.

Aucune conformité RGPD globale, validation visuelle, clôture C-17 ou mise en ligne n'est revendiquée.
