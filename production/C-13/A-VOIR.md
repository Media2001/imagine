# C-13 — à voir sur la démonstration

**Complément C09 du 25 novembre 2026 : les paiements fictifs sont présents et A-SANSMAIL est inclus. Recette stricte : 51 PHP + 26 HTTP verts, 10 tests purs / 30 assertions, sortie 2 et `recette_complete=false` seulement pour les liens natifs offert/groupé C09 toujours absents. Ce n’est ni acceptation complète ni validation visuelle. Les marqueurs C13 relèvent du parent.**

## Ouvrir l'écran

1. Se connecter en `e-abo` sur `http://192.168.129.32:8085/wp-login.php`. Les identifiants fictifs restent dans `C:\Users\Ced\.imagine-demo\identifiants.json`, hors dépôt.
2. Ouvrir **Imagine → Liste d’envoi**, ou `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-liste-envoi`.
3. Choisir **DEMO-2027-T1**, clôture **5 janvier 2027 à 00:00 Europe/Brussels**. L'écran indique clairement « projection provisoire » : cette clôture est future.
4. L'aperçu réel comporte **8 destinataires : 6 Belgique et 2 étrangers**. Six sont les profils C09 **A-CARTE, A-SEPA4, A-PAYPAL, A-PAPIER, A-ETRANGER et A-SANSMAIL**, désormais dotés de leur paiement initial fictif. Deux restent les témoins C13 (`c13-postal-be`, `c13-postal-fr`) en grâce fictive, sans paiement. Le témoin BE conserve `imagine_sans_email=1` et son adresse technique. A-SANSMAIL figure bien dans le CSV postal ; cela ne prouve pas son exclusion individuelle des emails, toujours non raccordée.
5. Les vrais abonnements C09 sont lus aussi : **A-SUSP → Suspendu ; A-VIR → Virement non validé ; A-EXPIRE → Expiré**. Les autres exclusions restent visibles, avec leur motif.
6. Cliquer **Exporter le CSV provisoire**. Le fichier est généré à la demande, jamais déposé dans un répertoire public. Ses colonnes et leur ordre viennent du réglage C10. Les noms commençant par `=` et la ville commençant par `@` des témoins C13 sont neutralisés par C07/C04, avec une apostrophe dans le CSV.
7. Recharger : le journal affiche le compte, la date UTC, le numéro, le nombre de lignes et l'état provisoire/clôturé. Chaque essai réussi crée un événement distinct ; les refus ne sont pas présentés comme des exports.
8. Le compte `e-admin` peut faire le même parcours. `e-redac`, `a-carte` et l'anonyme ne peuvent pas exporter. `e-abo` n'obtient ni réglages C10, ni droits éditoriaux, ni `manage_woocommerce`, ni gestion générale des utilisateurs.

## Réserves restantes — paiements fictifs et liens natifs sont distincts

Le relevé réel donne **12 abonnements C09, 4 sans date de paiement sur la souscription, et 6 destinataires C09 inclus**. A-SANSMAIL et A-CARTE ont leur inclusion positive dans l’export réel. Les états payés sont explicitement **fictifs** : métadonnée `imagine_demo_fictif=1`, titre « Paiement fictif de démonstration », identifiant de passerelle vide, aucune transaction, aucun jeton et reconduction manuelle. A-VIR reste non payé ; un actif sans paiement demeure exclu. A-GRACE et A-SUSP ont chacun leur renouvellement failed fictif, sans rejet bancaire réel.

Les observations ne sont jamais antidatées. Un historique antérieur absent ferme l’export. Le gel persiste calendrier, clôture, observations et blocs C01 ; sa relecture ne dépend plus de l’option courante. Réécriture native des clôtures passées refusée, égalité à la clôture exclue. Les vrais renouvellements enregistrés sont désormais transmis à C01 sans déplacer le début initial ; une échéance trimestrielle n’est pas une année.

Les profils offerts/groupés **C09** n’ont toujours pas de lien natif ; ils restent hors de l’acceptation positive. Le **code C13** lit désormais les cadeaux WCS Gifting et les attributions Memberships groupées : identités, adresses, historique. Ces raccords ont été éprouvés avec des objets natifs fictifs jetables et nettoyés : cadeau résolu/non résolu, groupe de trois places dont deux attribuées et une libre, renouvellement natif C01/C07. Une commande neuve à zéro a un statut/date de paiement explicitement fictifs, jamais un règlement bancaire ni la conversion d’un profil C09 actif en paiement.

**Réglage à confirmer par Imagine**, sans attente technique : en `e-admin`, politique des groupes `ferme` (défaut) ou `liens_memberships` (attributions natives et quantité des produits du plan = capacité). Les deux valeurs sont testées ; bénéficiaires requis non résolus = export fermé, jamais remplacement par le payeur. Aucune extension Teams absente n’est simulée. Aucun complément administratif C09 sans preuve native n’est accordé ; le statut actif seul reste insuffisant. Les propositions pour `docs/ecarts.md` sont dans `RAPPORT.md`, sans modification de docs/.

## Rejouer

Depuis `C:/Users/Ced/imagine`, dans bash :

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --require-complete
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13-unit.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

La première commande rejoue **10 tests purs / 30 assertions**, puis **77 contrôles PHP/HTTP**, relit les octets installés et vérifie la préservation C09/rôles/options/contenus et des sources B02/C14/fermées. Code **0** pour les gates techniques ; elle journalise ses vrais exports sans réinitialiser les profils. Seules les attentes des tests de démonstration ont changé : 8 lignes, répartition 6/2, inclusion nominative A-SANSMAIL/A-ETRANGER ; aucune règle C13/C07 n’a changé.

La seconde exécute les mêmes contrôles mais termine volontairement en **code 2** tant que les liens natifs P-OFFERT/P-GEST/P-BENEF manquent. Le complément a réellement rejoué cette recette via `python wp/tests/demo/c09-strict-recipes.py C13` : même fonction stricte sans déploiement, seule destination des reçus redirigée vers `production/C-09/complement-c13-strict.json`. Le résultat C13 antérieur n’a pas été écrasé. Le reçu actuel garde `recette_complete=false` ; aucun succès global n’est fabriqué.

Installation ciblée déjà exécutée : `PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --deploy`. Elle ne passe pas par le constructeur global, ne réinitialise pas C09/C10/C11/C12 et n'installe rien sur le NUC. Les témoins C13 existants ne sont pas remis à zéro.

**Historique de livraison C13, pas un nouveau rejeu global du complément :** le paquet pur est automatiquement découvert par T01 grâce à la configuration racine et aux manifests ajoutés dans `imagine-site`, sans modification du runner fermé. `preparer-image.ps1` a été exécuté, code **0**. Rejeu T01 final : **1010 tests, 33978 assertions, aucun échec/erreur/ignoré**, code **0** ; dont `imagine-site` **46 tests / 230 assertions**, C11 conservé.

Commandes historiques : `COMMANDES.md` ; reçus historiques : `resultats.json`, `resultats-purs.json` ; contrat natif : `references.md`. Reçu du complément effectivement rejoué : `../C-09/complement-c13-strict.json`, sortie stricte dans `../C-09/complement-c13-exit.json`. Les relevés GET avant clôture restent idempotents mais balaient les souscriptions : volume réel non qualifié. Aucun email, envoi postal, paiement réel, achat, réseau métier réel, Git ou tâche planifiée. Contrôle visuel des menus C10/C13 laissé à Ced ; les assertions HTTP ne valent pas validation visuelle.
