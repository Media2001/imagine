# C-09 — Complément paiements fictifs

- **Fait** : états natifs payés/rejetés autorisés, rejouables sur imagine-test-demo seulement ; A-VIR impayé, souscriptions explicitement manuelles, aucun gateway/token/mandat/transaction/email réel.
- **Prêt à relire** : complément C09, avec les limites permises et les deux recettes strictes toujours partielles ; PRET ne signifie pas acceptation globale.
- **Réserves** : C13 offert/groupé absents ; B02 ne lit pas la seconde échéance payée, marge C05, compteurs/historique et documents non raccordés. Aucun assouplissement de règle ou changement de code C13/B02.
- **Fichiers** : script C09/catalogue/projection de préservation ; recettes C09 et seules attentes de démonstration C13/B02 ; trois A-VOIR et présents rendus sous C09. Aucun thème/B03, bibliothèque close, site voie1, Git, verrou, file ou rapport global modifié.

## Profil par profil — complément

| Profil | État natif relu | Résultat du complément / reste |
|---|---|---|
| A-CARTE | initiale #88 processing, date payée présente | partiel — Aucune carte réelle. Reconduction automatique non posée ; renouvellement manuel maintenu. Compteur 3 numéros et historique C01 non raccordés. |
| A-SEPA4 | initiale #91 processing, date payée présente ; renouvellement #2419 processing, payé, création UTC 2026-10-26T18:01:50+00:00 | partiel — Aucun mandat SEPA ni jeton. WCS planifie seulement la prochaine action, pas une seconde action pour la quatrième échéance. B02 ne lit encore que la commande initiale : sa table ne montre qu’une Payée ; marge C05/dates théoriques non raccordées. |
| A-PAYPAL | initiale #94 processing, date payée présente | partiel — Aucun accord PayPal ni jeton ; renouvellement manuel uniquement. |
| A-PAPIER | initiale #100 processing, date payée présente | partiel — Aucun mandat papier ou IBAN, aucun export bancaire. Quatre fois reste une fixture, pas une règle de domiciliation. |
| A-ETRANGER | initiale #115 processing, date payée présente | partiel — Supplément de port non chiffré : zéro n’est pas un supplément appliqué ni un tarif Imagine. |
| A-SANSMAIL | initiale #118 processing, date payée présente | partiel — Exclusion individuelle des emails non raccordée. Le coupe-circuit global garantit aucun email mais ne prouve pas ce critère individuel. |
| A-ECHEANCE | initiale #121 processing, date payée présente | partiel — Reconduction automatique non posée. Rappel/non-envoi non raccordés ; aucun email envoyé. |
| A-NONRENOUV | initiale #112 processing, date payée présente | partiel — Fin native de renouvellement démontrée ; compteur métier 1 numéro restant et historique non raccordés. |
| A-GRACE | renouvellement #2420 failed, non payé, création UTC 2026-11-24T18:01:50+00:00 | créé — Rejet et fenêtre explicitement fictifs ; aucun rejet bancaire réel. Durée de fixture, pas une règle métier décidée. |
| A-SUSP | renouvellement #2421 failed, non payé, création UTC 2026-11-21T18:01:50+00:00 | créé — Rejet explicitement fictif, jamais un incident bancaire réel ; aucune reconduction automatique. |

A-VIR : on-hold/pending et paiement absent ; P-OFFERT/P-GEST/P-BENEF : liens natifs absents, laissés sans droit inventé. Tableau intégral des 30 profils/décisions : A-VOIR.md. Le complément rend A-GRACE/A-SUSP complets ; V-DEC/V-DEC-FIN/P-NUMERO étaient déjà complétés par C12/C14 mais encore périmés dans l’ancien tableau.

## Exécutions réelles

- C09 : {'local': 7, 'natif': 382, 'paiements': 149, 'securite': 10, 'corrections': 41, 'HTTP': 197, 'C08': 30}, tous verts ; reset **6/6**, altérations réellement détectées puis restaurées. Catégories : {'créé': 9, 'partiel': 20, 'impossible': 1}.
- C13 strict : **51 PHP + 26 HTTP**, pur **10 tests / 30 assertions**, exit **2**. 8 destinataires (6 BE / 2 étranger), dont 6 C09 ; A-SANSMAIL inclus. Seuls liens offert/groupé encore absents ; recette_complete=false.
- B02 strict : **140/140**, HTTP **55/55**, exit **2**. Seconde échéance native payée non consommée par son tableau (une Payée visible), failed A-SUSP attesté HTTP. Snapshot natif/rôles/options et lots clos préservés ; deux observations postales ajoutées, adresse restaurée.
- Trois libellés B02 figés et périmés restent dans le reçu brut : profil a-4x-j45 (corrigé en A-SEPA4 par arbitrage), aucun failed, A-CARTE impayé. Ils ne sont pas repris comme blocages actuels. Aucun code produit ou runner B02 modifié.
- Aucun paquet de dépendances Composer ni manifeste PHP ajouté : preparer-image.ps1 non modifié, rafraîchissement conditionnel non requis pour ces recettes de démonstration. Image existante réellement exercée par les 10 tests purs C13.

## Décisions prises à défaut et incidents

- C09 conserve ses montants de grille fictive existants (ou zéro) et ses ID. Les six profils postaux payés commencent à J-90/J-180 pour garder le prochain numéro dans leur année C01. A-ECHEANCE/A-NONRENOUV conservent J-335/J+30, année native 365 jours testée. Aucun renouvellement annuel ni règle inventé. WCS ne planifie que la prochaine échéance ; la quatrième reste future, sans action supplémentaire fictivement déclarée.
- Le vieux snapshot B00 appelait hash_file sur une pièce jointe retirée par C11 : échec réel avant mutation. Projection C09 adaptée en lecture seule aux fichiers présents et métadonnées ; C08/B00 préservés par comparaison exacte avant/après.
- Au reset, les transitions payées WCS changeaient le rôle customer en subscriber : échec observé sur huit profils, puis restauration explicite du rôle C09 après les transitions ; reset et readback verts. Test RED puis GREEN supplémentaire sur la préservation de l’année native A-ECHEANCE/A-NONRENOUV.
- Un premier vérificateur global a dépassé le watchdog de 420 s pendant B02. Processus terminé, adresses C09 relues intactes ; recette B02 complète rejouée, puis vérificateur relancé comme processus suivi. Aucun résultat inventé ; aucun historique nettoyé.
- Les reçus anciens et incidents antérieurs restent présents. Les seuls nettoyages sont les témoins temporaires créés par les recettes elles-mêmes. Les nouveaux reçus C13/B02 sont redirigés sous C09 ; les fichiers de résultats des autres lots ne sont pas écrasés.

Voir complement-verification.json, complement-final-native.json, complement-c13-strict.json, complement-b02-resultats.json et les trois A-VOIR. Validation visuelle laissée à Ced.
