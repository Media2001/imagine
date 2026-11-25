# C-15 — À voir

**Prêt à relire, pas une validation visuelle ni un GO sur du réel.** Un seul site entièrement fictif : `imagine-test-demo`.

## Compte et adresse

Se connecter comme **E-ABO** (`e-abo`, Référent abonnements) ou **E-ADMIN** (`e-admin`). Les identifiants privés C09 sont dans `C:\Users\Ced\.imagine-demo\identifiants.json` ; aucun mot de passe dans ce dossier. Le reset de recette invalide les sessions C09 : se reconnecter.

Ouvrir **Imagine → Échéances** :

`http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-echeances`

Le menu principal Imagine apparaît une seule fois ; le référent voit Liste d’envoi et Échéances, pas les réglages réservés à l’administrateur.

| Vue (`&vue=…`) | Ce qui doit apparaître |
|---|---|
| `echeances` | A-ECHEANCE, parmi les souscriptions dont la prochaine date ou la fin native tombe dans les 30 jours ; choix 30/90/180 jours, ordre chronologique puis ID |
| `attente` | A-VIR et les autres commandes liées à une souscription, natives `pending/on-hold`, sans statut ni date de paiement ; pas A-CARTE payée |
| `virements` | A-VIR seulement, avec **Paiement reçu** |
| `mandats` | A-PAPIER seulement, montant natif (fixture à zéro, pas un tarif Imagine), référence fictive **A-PAPIER**, prochaine échéance native UTC ; bouton d’export CSV |
| `echecs` | Les deux renouvellements natifs échoués A-GRACE et A-SUSP ; pas les commandes déjà payées |

**Paiement reçu** ouvre d’abord une confirmation serveur : commande, abonné, montant, case de confirmation obligatoire, retour sans agir. Après confirmation, Woo enregistre le paiement et sa date ; une note porte le nom/login/ID du référent et l’instant UTC. Pas de paiement bancaire, de remboursement, d’action en masse ni de changement direct du moteur d’accès. Une seconde validation est refusée.

La recette a réellement fait cette action sur A-VIR, puis exécuté le reset C09 et relu A-VIR impayé. Les notes d’audit ne sont pas effacées. Pour rejouer la démonstration avec restauration automatique, utiliser la commande de recette ci-dessous plutôt qu’un reset global à la main.

L’export est ouvert et parsé par la recette HTTP réelle, pour le référent et l’administrateur : cinq colonnes fixes, une ligne A-PAPIER, cellules protégées contre les formules, réponse privée/no-store. Aucun fichier laissé sous la racine publique et aucune donnée bancaire. E-REDAC, A-CARTE et l’anonyme sont refusés ; nonces absent/invalide/tableau, mauvais numéro de commande ou autre période, méthode GET refusés.

## Convention fictive, explicite

Le catalogue C09 nomme A-VIR « virement » et A-PAPIER « mandat papier », mais laisse leurs méthodes de passerelle vides. C15 ne réécrit pas cette fixture : **sur cette seule URL locale**, il reconnaît leurs marqueurs natifs, leurs IDs exacts de manifeste et leurs propriétaires fictifs. L’identifiant natif **A-PAPIER** sert de référence fictive, sans inventer un mandat bancaire. Hors démo, une méthode vide reste inconnue : virement `bacs` requis ; pour le papier, méthode `imagine_papier` et référence native `imagine_mandat_reference`. Méthode native non vide toujours prioritaire. Ces exceptions locales ne rendent pas un autre profil payable.

Aucun délai « virement en retard » n’est ajouté : attente/échecs sans limite d’ancienneté ; un mandat dont la prochaine date native est déjà due reste à lancer. C06 et C10 restent seuls responsables des droits d’accès. Offerts/groupés absents : aucun lien ni profil fabriqué, aucune attente sur leur question ouverte.

## Rejouer et preuves

Depuis la racine, avec le Python HTTP déjà préparé hors dépôt :

```powershell
& 'C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe' wp/tests/demo/c15-verifier.py --prepare --action
```

Rejeu du 25 novembre 2026 : **257 contrôles/tests comptés sans les relectures répétées, zéro échec** : 18 purs C15, 21 natifs C15, 43 HTTP vues/export, 16 HTTP action/reset, 10 tests purs C13 (30 assertions), 149 contrôles de paiements natifs C09. `preparer-image.ps1` exécuté sans modification, image vérifiée ; C15 autonome n’est pas annoncé dans la découverte T01.

- `verification.json` : synthèse finale et empreintes des sources.
- `pure-final.json`, `runtime-final.json`, `http.json`, `action.json` : détails des assertions.
- `paiement-readback.json`, `restauration.json` : paiement natif constaté, reset C09 et état sémantique initial retrouvé.
- `preparation-image.log` : sortie réelle de préparation.
- `red-*.json`, `action-red.json` : jalons TDD ; `restore-diff.json` conserve le premier écart de recette (date P-NUMERO), corrigé et entièrement restauré ensuite.

Le reset réutilise l’horloge initiale C09 ; le runner restaure aussi les états découverte C12 et la date payée de P-NUMERO, que son initialiseur C14 déplacerait sinon. Aucune restauration de thème ni remplacement de B02/C13/bibliothèque close ; empreintes protégées inchangées. Les IDs de lignes Woo et les notes techniques peuvent évoluer avec le reset canonique : la comparaison porte sur IDs des profils/objets, états, paiements, montants, propriétaires, adresses, dates métier, rôles et états découverte, pas sur des dates de modification.

## Standard consulté

- WooCommerce, référence officielle `WC_Order::payment_complete()` : https://woocommerce.github.io/code-reference/classes/WC-Order.html#method_payment_complete — statut payé et date natifs, pas un registre parallèle.
- WordPress, référence officielle `wp_verify_nonce()` : https://developer.wordpress.org/reference/functions/wp_verify_nonce/ — le nonce ne remplace jamais `current_user_can()`.

Validation visuelle de Ced et deux relectures du code restent à faire. La recette fictive ne prouve aucune transaction réelle ni qualification en grand volume.
