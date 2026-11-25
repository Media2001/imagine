# Vérification C-09 — complément « paiements fictifs »

Vérificateur : Claude. Date : 25/11/2026.
Base : dernière vérification `relectures/C-09/verification.md` (commit `2229ab7`, 23/11 23 h 33). Diff examiné : `2229ab7..HEAD` sur les fichiers C-09 (`wp/outils/demo/c09-*`, `wp/outils/demo/profils.py`, `wp/tests/demo/c09-*`) et `production/C-09`.
Consigne source du changement : `briefs/C-09-complement-paiements-fictifs.md` et `docs/arbitrages-2026-11-25.md` (§ C-13, reclassement « compléter les profils de C-09 » en **technique** ; § Complément de C-09 du passage de 19 h 30).
Portée : contrôle ciblé du seul complément. Pas de relecture complète refaite. Les suites « site » (démo `imagine-test-demo`) restent hors de mes droits (doctrine §3).

## 1. Consignes et arbitrages — Appliqué / Non / Partiel

| # | Consigne (brief) ou arbitrage | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | Commande initiale **payée** pour A-CARTE, A-PAYPAL, A-ETRANGER, A-SANSMAIL, A-ECHEANCE, A-NONRENOUV | **Appliqué** | Liste `paidInitial` → statut `processing` + `set_date_paid` (`wp/outils/demo/c09-seed.php:232-236`). Contrôle `:initial_paye` (`wp/tests/demo/c09-payments.php:13`). |
| 2 | A-SEPA4 : **deux échéances payées sur quatre**, deux à venir | **Appliqué** (réserve déclarée) | Initiale payée + 1 renouvellement `processing`/payé daté J-30 (`c09-seed.php:298-345`). `:deux_payees_sur_quatre` = `get_payment_count()===2` & prochaine échéance future (`c09-payments.php:40-42`). Réserve : WCS ne planifie que la prochaine action, pas une 2ᵉ action future (déclaré A-VOIR/RAPPORT). |
| 3 | A-PAPIER : actif, échéance à lancer ce mois-ci | **Appliqué** | A-PAPIER dans `paidInitial` (`c09-seed.php:232`) ; échéance « ce mois » via horloge injectable, `:echeance_ce_mois` (`c09-runtime.php:93`). |
| 4 | A-GRACE / A-SUSP : renouvellement **en échec** à la date supposée | **Appliqué** | Boucle renouvellements : statut `failed`, date = `_imagine_acces_grace_debut` (`c09-seed.php:329-336`). `:rejet_date_grace` (`c09-payments.php:44-45`). Reclassés « créé ». |
| 5 | Objets natifs, montant grille fictive/zéro, titre « Paiement fictif de démonstration », aucune passerelle/jeton/mandat/email | **Appliqué** | `set_payment_method('')`, titre posé, `transaction_id=''` (`c09-seed.php:234-235, 310-314`). `:aucune_transaction` + `hors_ligne` (mail/HTTP coupés, `get_available_payment_gateways()===[]`) (`c09-payments.php:16, 25-27`). |
| 6 | Marque `imagine_demo_fictif` sur chaque objet ; refus de tout site non `imagine-test-…` | **Appliqué** | Marque sur comptes/commandes/abonnements/renouvellements/adhésions/produits/lignes (`c09-seed.php:386-399`). Garde cible : `profils.py:validate_target` (inchangée, `imagine-test-demo` seul) + préflight `c09-payments.php:5-8`. |
| 7 | Rejouable : relancé, remet les profils dans cet état | **Appliqué** | `reset` 6/6, `ids_rejoues_identiques=true` (`production/C-09/complement-verification.json:58`). Rôle client restauré après transitions WCS payées (`c09-seed.php:395-399`). |
| 8 | A-VIR reste **non payé** | **Appliqué** | Hors `paidInitial` → `on-hold`/`pending`. `A-VIR:non_paye` (`c09-payments.php:23-24`) ; catalogue `virement_non_valide` (`c09-profils.json`). |
| 9 | P-OFFERT/P-GEST/P-BENEF : complétés **seulement si lien natif existe**, sinon laissés et déclarés | **Appliqué** | Aucun lien inventé : `:aucun_lien_ou_droit_invente` (`c09-payments.php:71-73`) ; déclaré dans A-VOIR et RAPPORT-complement §22. |
| 10 | Renouvellement automatique **non posé** (arbitrage 23/11, maintenu le 25/11) | **Appliqué** | `set_requires_manual_renewal(true)` conservé (`c09-seed.php:256, 353`). `:manuel_sans_jeton` (`c09-payments.php:21`). |
| 11 | Aucune règle ne bouge : actif sans paiement validé reste exclu de la liste | **Appliqué** | Code de la liste inchangé ; les paiements fictifs rendent les profils éligibles sans toucher la règle. `A-SANSMAIL:inclusion_postale` (`c09-payments.php:87-88`). |
| 12 | Ne pas modifier le code de C-13, B-02 ni bibliothèques closes ; adapter l'attente du **test de démonstration** et le signaler | **Appliqué** | Attente de recette adaptée : paiement désormais attendu (`c09-corrections.php:38`). Recettes strictes redirigent seulement leurs reçus, sans toucher les runners (`c09-strict-recipes.py:16-21`). RAPPORT-complement : « Aucun code produit ou runner B02 modifié ». |
| 13 | Mettre à jour les trois `A-VOIR` (C-09, C-13, B-02) et redéposer `production/C-09/PRET` | **Appliqué** | Les trois A-VOIR réécrits + PRET (empreintes dans `complement-livraison.json:16-22`). A-VOIR C-09 : « 9 créés, 20 partiels, 1 impossible ». |
| — | Arbitrage 25/11 § Complément : paiements déclarés fictifs ; rôle rétabli au reset accepté ; liens offert/groupé non fabriqués (C-13/B-02 restent recette partielle) | **Appliqué** | Reset rôle (`c09-seed.php:395`) ; strict C13 exit 2, strict B02 exit 2 (`complement-verification.json:52-53`). |

## 2. Résultat des tests

- **Suite PHP rejouée par moi** : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1` (conteneur jetable WSL, réseau coupé, montage `wp/` en lecture seule). Dernière ligne :
  `REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`.
  Refus du tool PowerShell natif (processus imbriqué non validable) ; rejouée via le tool Bash, sans modification de la commande.
- **Limite de portée.** Cette suite couvre `imagine-connecteur` (37), `imagine-non-regression`, `imagine-pilotage`, `imagine-site`. Elle **n'inclut pas** les recettes de démonstration du complément (`c09-payments.php`, `c09-complement.py`, `c09-delivery.py`, `c09-strict-recipes.py`, `c09-runtime.php`) : elles s'exécutent contre le site `imagine-test-demo`, auquel je n'ai pas accès.
- **Reçus de livraison d'Hermès** (non reproduits ici) : local 7/7, natif 382/382, **paiements 149/149**, sécurité 10/10, corrections 41/41, HTTP 197/197, régression C08 30/30, **reset 6/6** ; strict C13 exit 2, strict B02 exit 2 (`complement-verification.json`). Aucun secret (61 fichiers scannés, 0 correspondance). **Le rejeu réel des suites site sur le NUC par Ced reste dû**, comme à chaque tour.

## 3. Régressions / modifications non demandées

- **Non bloquant — le seed C-09 câble désormais C-12 et C-14.** Pour rendre le tableau cohérent, le seed appelle `c12-profils.php` (profils `decouverte: C12` → V-DEC/V-DEC-FIN) et `c14-profil.php` (P-NUMERO) (`c09-seed.php:176-179, 238-241`), fichiers poussés par `profils.py:65-67`. Au-delà de la liste explicite du brief, mais **sans modifier** le code clos de C-12/C-14 (il n'est qu'appelé). Déclaré dans RAPPORT-complement §22. À connaître : le seed C-09 dépend maintenant de C-12/C-14.
- **Adaptation de banc déclarée.** `profils.py:preserve()` remplace le `require b00-snapshot.php` par une projection en lecture seule (l'ancien snapshot appelait `hash_file` sur une pièce jointe retirée par C-11 → échec réel avant mutation). Conforme à l'arbitrage (« Projection C09 adaptée en lecture seule »). RAS.
- **Cosmétique.** `c09-profils.json` est passé du format compact au format indenté : gros diff visuel, aucun changement fonctionnel.
- **Défaut hors C-09.** B-02 ne lit encore qu'**une** échéance A-SEPA4 payée (sa table n'affiche qu'une « Payée »). C'est un défaut de B-02, à traiter dans sa relecture, confirmé par l'arbitrage 25/11 ; pas un défaut du complément.
- **Diff large hors périmètre.** Depuis `2229ab7`, le diff `wp/` touche aussi B-03, C-11, C-12, C-14 et le thème : ce sont d'autres lots livrés dans la même fenêtre, **non examinés ici**. Aucun fichier `docs/` modifié (conforme). Aucune bibliothèque close ni runner C-13/B-02 modifié par le complément.

## 4. Verdict

**Prêt pour la clôture.**

Le complément applique les treize points du brief et les arbitrages du 25/11 concernés, prouvés au code : commandes initiales payées fictives pour les profils décrits, A-SEPA4 à 2/4, A-GRACE/A-SUSP en renouvellement échoué, marque `imagine_demo_fictif` partout, A-VIR laissé impayé, reconduction automatique non posée, règle d'exclusion inchangée, aucun secret ni donnée réelle, aucune passerelle/jeton/mandat/email. La suite PHP globale est au vert (1 012). Aucun problème de fond résiduel sur C-09.

Réserves portées à la clôture, sans effet sur elle :
1. Les recettes de démonstration du complément s'exécutent sur `imagine-test-demo` : leurs décomptes (paiements 149/149, etc.) sont une **livraison d'Hermès**, non reproduite par le relecteur ; le rejeu réel sur le NUC reste à la main de Ced.
2. Le seed C-09 câble maintenant C-12 et C-14 (au-delà du brief, sans modifier leur code clos) — à connaître pour la maintenance.
3. Limites hors ligne inhérentes et assumées (mandats/jetons réels absents, moyens de paiement indistincts, échéancier métier et compteurs C01 non raccordés), déclarées profil par profil ; le défaut B-02 (seconde échéance payée non lue) relève de la relecture de B-02.

> Ce verdict n'est pas un GO au sens de la doctrine §3/§6.
