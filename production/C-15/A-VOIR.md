# C-15 — À voir

**Prêt à relire, pas une validation visuelle ni un GO sur du réel.** Un seul site entièrement fictif : `imagine-test-demo`.

## Compte et adresse

Se connecter comme **E-ABO** (`e-abo`, Référent abonnements) ou **E-ADMIN** (`e-admin`). Les identifiants privés C09 sont dans `C:\Users\Ced\.imagine-demo\identifiants.json` ; aucun mot de passe dans ce dossier. Les recettes corrigées ne font plus de reset global C09.

Ouvrir **Imagine → Échéances** :

`http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-echeances`

Le menu principal Imagine apparaît une seule fois ; le référent voit Liste d’envoi et Échéances, pas les réglages réservés à l’administrateur.

| Vue (`&vue=…`) | Ce qui doit apparaître |
|---|---|
| `echeances` | A-ECHEANCE, parmi les souscriptions dont la prochaine date ou la fin native tombe dans les 30 jours ; choix 30/90/180 jours, ordre chronologique puis ID |
| `attente` | A-VIR et les autres commandes liées à une souscription, natives `pending/on-hold`, non payées et sans date de paiement ; pas A-CARTE payée |
| `virements` | A-VIR seulement, avec **Paiement reçu** |
| `mandats` | A-PAPIER seulement à l'état restauré actif, montant natif fictif **30,00 EUR** (pas une grille tarifaire Imagine), référence fictive **A-PAPIER**, prochaine échéance native UTC ; bouton d’export CSV |
| `echecs` | Les deux renouvellements natifs échoués A-GRACE et A-SUSP ; pas les commandes déjà payées |

**Paiement reçu** ouvre d’abord une confirmation serveur : commande, abonné, montant, case de confirmation obligatoire, retour sans agir. Après confirmation, Woo enregistre le paiement et sa date ; une note porte le nom/login/ID du référent et l’instant UTC. Pas de paiement bancaire, de remboursement, d’action en masse ni de changement direct du moteur d’accès. Une seconde validation est refusée.

La recette a réellement fait cette action sur A-VIR, puis restauré uniquement son état natif observé et relu A-VIR impayé. Deux confirmations HTTP simultanées donnent **un succès 302, un refus 409 et une seule note C15**. Un retour natif false, même après transition payée, donne 409 sans note C15 de succès. Le verrou par commande est relâché en `finally`, vérifié avant la réponse. Les notes d’audit ne sont pas effacées. Utiliser le runner ci-dessous plutôt qu’un reset global à la main.

L’export est ouvert et parsé par la recette HTTP réelle, pour le référent et l’administrateur : cinq colonnes fixes, une ligne A-PAPIER à l'état restauré, cellules protégées contre les formules, réponse privée/no-store. **Devise** est volontairement ajoutée aux quatre champs du §3.13. Aucun fichier laissé sous la racine publique et aucune donnée bancaire. E-REDAC, A-CARTE et l’anonyme sont refusés ; nonces absent/invalide/tableau, mauvais numéro de commande ou autre période, méthode GET refusés. La colonne État affiche des libellés français distincts pour commandes et souscriptions, pas les identifiants anglais.

## Convention fictive, explicite

Le catalogue C09 nomme A-VIR « virement » et A-PAPIER « mandat papier », mais laisse leurs méthodes de passerelle vides. C15 ne réécrit pas cette fixture : **sur cette seule URL locale**, il reconnaît leurs marqueurs natifs, leurs IDs exacts de manifeste et leurs propriétaires fictifs. L’identifiant natif **A-PAPIER** sert de référence fictive, sans inventer un mandat bancaire. Hors démo, une méthode vide reste inconnue : virement `bacs` requis ; papier `imagine_papier`, référence native `imagine_mandat_reference`. **Une référence absente ne masque plus la ligne : « Référence manquante » dans la liste et le CSV.** Méthode native non vide toujours prioritaire. Ces exceptions locales ne rendent pas un autre profil payable.

Aucun délai « virement en retard » n’est ajouté : attente/échecs sans limite d’ancienneté ; un mandat dont la prochaine date native est déjà due reste à lancer. C06 et C10 restent seuls responsables des droits d’accès. Offerts/groupés absents : aucun lien ni profil fabriqué, aucune attente sur leur question ouverte.

**Choix prudents explicites** : attente/virements uniquement pour commandes liées à une souscription du même propriétaire ; commandes à l'unité exclues jusqu'à réponse Imagine (Q1). La vue échéances inclut `pending` et `on-hold` avec prochaine date/fin native, en plus de `active`/`pending-cancel` ; ce n'est pas une décision de droit d'accès. Les mandats `on-hold` ne sont retenus que s'il existe une commande de renouvellement native exigible impayée (Q2), jamais pour une suspension quelconque. Le montant et la création UTC de cette commande priment sur la prochaine échéance projetée ; aucun doublon futur.

### Témoins d'état du catalogue C09 — A-PAPIER existant

La recette C15 a exercé **renouvellement exigible non payé**, puis **renouvellement payé**, sous le même A-PAPIER : création native WCS d'une commande de renouvellement, transition native d'impayé (`on-hold`, dette visible/exportable), puis statut natif payé fictif (dette retirée). Aucun nouveau profil, passerelle ou transaction. Les deux états sont attestés dans `corrections-paper-final-unpaid-native.json` et `corrections-paper-final-paid-native.json`, puis nettoyés : ils ne restent pas affichés comme dettes après le rejeu. Aucun état manquant ; catalogue/source C09 inchangé. Restauration des dates métier, statut, rôle et adhésion observés ; commandes témoins supprimées et absence relue.

## Rejouer et preuves

Depuis la racine, avec le Python HTTP déjà préparé hors dépôt :

```powershell
& 'C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe' wp/tests/demo/c15-corrections.py
```

Rejeu corrigé terminé le **25 novembre 2026 à 22 h 07 CET** : préparation T01 réelle sans modification, puis commande standard `wp/tests/rejouer.ps1` **PASS : 1 030 tests / 34 124 assertions**, dont **9 tests purs C15 / 45 assertions**, nommés dans le JUnit. Banque autonome renforcée : 28 contrôles ; natifs 21 ; HTTP vues/export 43 ; action/restauration 16 ; états papier 6 ; concurrence 7 ; refus natif 7 ; français 4 ; paiements C09 149. Catégories distinctes, pas de somme gonflée par les reprises.

- `corrections-final.json` : synthèse corrigée et empreintes scellées des sources.
- `corrections-preparation-image.log`, `corrections-t01.log` : commandes réelles ; découverte et JUnit C15.
- `corrections-pure-final.json`, `corrections-phpunit-final.json`, `corrections-runtime-final.json`, `corrections-http-final.json`, `corrections-action-final.json` : assertions finales.
- `corrections-paper-final*`, `corrections-concurrent-final*`, `corrections-native_false-final*`, `corrections-french-final.json` : parcours corrigés.
- `corrections-renewals-deleted-readback.json`, `restauration.json` : nettoyage possédé et restauration sémantique exacte.
- `corrections-red-*.json` : RED réels avant correction. L'ancien total 257, `verification.json` et `restore-diff.json` sont historiques, pas le verdict corrigé.

Le runner restaure uniquement A-PAPIER ou A-VIR concerné, sans relancer les initialiseurs globaux C09/C12/C14. États découverte C12 et date payée P-NUMERO restent inchangés. Aucun téléversement de thème ni remplacement de B02, bootstrap, README partagé ou bibliothèque close ; empreintes distantes protégées inchangées pendant le rejeu. Comparaison des profils/objets, états, paiements, montants, propriétaires, adresses, dates métier observées, rôles et découverte ; les notes natives d'audit et dates techniques de modification peuvent évoluer. Le MU de rendez-vous de concurrence est retiré et son absence relue. Aucun email ni appel sortant de paiement.

## Standard consulté

- WooCommerce, référence officielle `WC_Order::payment_complete()` : https://woocommerce.github.io/code-reference/classes/WC-Order.html#method_payment_complete — statut payé et date natifs, pas un registre parallèle.
- WordPress, référence officielle `wp_verify_nonce()` : https://developer.wordpress.org/reference/functions/wp_verify_nonce/ — le nonce ne remplace jamais `current_user_can()`.
- MySQL, fonctions natives `GET_LOCK` / `RELEASE_LOCK` : https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html — exclusion mutuelle consultative de connexion, pas de registre de paiements.

Validation visuelle de Ced et deux relectures du code restent à faire. La recette fictive ne prouve aucune transaction réelle ni qualification en grand volume.
