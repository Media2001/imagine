# C-13 — à voir sur la démonstration

**État unique : prêt à relire avec réserves C09. Les corrections techniques du 25 novembre 2026 sont appliquées et vérifiées ; `recette_complete=false`. Ce n’est ni acceptation complète, ni validation visuelle, ni clôture. Aucun PRET créé/modifié par ce worker : le marqueur relève du parent, et signifie uniquement prêt à relire.**

## Ouvrir l'écran

1. Se connecter en `e-abo` sur `http://192.168.129.32:8085/wp-login.php`. Les identifiants fictifs restent dans `C:\Users\Ced\.imagine-demo\identifiants.json`, hors dépôt.
2. Ouvrir **Imagine → Liste d’envoi**, ou `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-liste-envoi`.
3. Choisir **DEMO-2027-T1**, clôture **5 janvier 2027 à 00:00 Europe/Brussels**. L'écran indique clairement « projection provisoire » : cette clôture est future.
4. L'aperçu réel comporte **2 destinataires : 1 Belgique et 1 étranger**. Ils proviennent exclusivement des deux témoins **C13** natifs supplémentaires (`c13-postal-be`, `c13-postal-fr`), en grâce fictive explicitement bornée, sans paiement. Le témoin BE porte `imagine_sans_email=1` et conserve son adresse technique `@example.org`.
5. Les vrais abonnements C09 sont lus aussi : **A-SUSP → Suspendu ; A-VIR → Virement non validé ; A-EXPIRE → Expiré**. Les autres exclusions restent visibles, avec leur motif.
6. Cliquer **Exporter le CSV provisoire**. Le fichier est généré à la demande, jamais déposé dans un répertoire public. Ses colonnes et leur ordre viennent du réglage C10. Les noms commençant par `=` et la ville commençant par `@` des témoins C13 sont neutralisés par C07/C04, avec une apostrophe dans le CSV.
7. Recharger : le journal affiche le compte, la date UTC, le numéro, le nombre de lignes et l'état provisoire/clôturé. Chaque essai réussi crée un événement distinct ; les refus ne sont pas présentés comme des exports.
8. Le compte `e-admin` peut faire le même parcours. `e-redac`, `a-carte` et l'anonyme ne peuvent pas exporter. `e-abo` n'obtient ni réglages C10, ni droits éditoriaux, ni `manage_woocommerce`, ni gestion générale des utilisateurs.

## Blocage attesté — ne pas confondre témoins C13 et profils C09

Le relevé réel donne **12 abonnements C09 et 12 sans date de paiement validé**. En particulier **A-SANSMAIL est exclu pour `paiement_non_valide`, pas parce qu'il n'a pas d'email**. Son inclusion demandée par C13 n'est donc **pas démontrée** sur ce profil. Les états administratifs `active` de C09 ne sont pas silencieusement convertis en règlements ou mandats confirmés.

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

La première commande rejoue **10 tests purs / 30 assertions**, puis **75 contrôles PHP/HTTP**, relit les octets installés et vérifie la préservation C09/rôles/options/contenus et des sources B02/C14/fermées. Code **0** pour les gates techniques ; elle journalise ses vrais exports sans réinitialiser les profils.

La seconde exécute les mêmes contrôles mais termine volontairement en **code 2** tant que l'acceptation C09 reste incomplète. `production/C-13/resultats.json` conserve explicitement `recette_complete=false` et les constats natifs, sans les présenter comme un succès global.

Installation ciblée déjà exécutée : `PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --deploy`. Elle ne passe pas par le constructeur global, ne réinitialise pas C09/C10/C11/C12 et n'installe rien sur le NUC. Les témoins C13 existants ne sont pas remis à zéro.

Le paquet pur est automatiquement découvert par T01 grâce à la configuration racine et aux manifests ajoutés dans `imagine-site`, sans modification du runner fermé. `preparer-image.ps1` a été exécuté, code **0**. Rejeu T01 final : **1010 tests, 33978 assertions, aucun échec/erreur/ignoré**, code **0** ; dont `imagine-site` **46 tests / 230 assertions**, C11 conservé.

Commandes : `COMMANDES.md` ; reçus : `resultats.json`, `resultats-purs.json` ; contrats natifs : `references.md`. Les relevés GET avant clôture restent idempotents mais balaient les souscriptions : volume réel non qualifié. Aucun email, envoi postal, paiement réel, achat, réseau métier réel, Git ou tâche planifiée. Contrôle visuel des menus C10/C13 laissé à Ced ; les assertions HTTP ne valent pas validation visuelle.
