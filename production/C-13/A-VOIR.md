# C-13 — à voir sur la démonstration

**Soumis à relecture le 25 novembre 2026 : PRET redéposé sur consigne explicite de la file voie 2 et des arbitrages du jour. L’écran et ses contrôles techniques sont consultables ; la recette complète C09 reste non acquise (détails et reçu ci-dessous). PRET signifie ici prêt à relire, pas acceptation complète, validation visuelle ou clôture.**

## Ouvrir l'écran

1. Se connecter en `e-abo` sur `http://192.168.129.32:8085/wp-login.php`. Les identifiants fictifs restent dans `C:\Users\Ced\.imagine-demo\identifiants.json`, hors dépôt.
2. Ouvrir **Imagine → Liste d’envoi**, ou `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-liste-envoi`.
3. Choisir **DEMO-2027-T1**, clôture **5 janvier 2027 à 00:00 Europe/Brussels**. L'écran indique clairement « projection provisoire » : cette clôture est future.
4. L'aperçu réel comporte **2 destinataires : 1 Belgique et 1 étranger**. Ils proviennent exclusivement des deux témoins **C13** natifs supplémentaires (`c13-postal-be`, `c13-postal-fr`), en grâce fictive explicitement bornée. Le témoin BE porte `imagine_sans_email=1` et conserve son adresse technique `@example.org`. Aucun règlement n'a été créé.
5. Les vrais abonnements C09 sont lus aussi : **A-SUSP → Suspendu ; A-VIR → Virement non validé ; A-EXPIRE → Expiré**. Les autres exclusions restent visibles, avec leur motif.
6. Cliquer **Exporter le CSV provisoire**. Le fichier est généré à la demande, jamais déposé dans un répertoire public. Ses colonnes et leur ordre viennent du réglage C10. Les noms commençant par `=` et la ville commençant par `@` des témoins C13 sont neutralisés par C07/C04, avec une apostrophe dans le CSV.
7. Recharger : le journal affiche le compte, la date UTC, le numéro, le nombre de lignes et l'état provisoire/clôturé. Chaque essai réussi crée un événement distinct ; les refus ne sont pas présentés comme des exports.
8. Le compte `e-admin` peut faire le même parcours. `e-redac`, `a-carte` et l'anonyme ne peuvent pas exporter. `e-abo` n'obtient ni réglages C10, ni droits éditoriaux, ni `manage_woocommerce`, ni gestion générale des utilisateurs.

## Blocage attesté — ne pas confondre témoins C13 et profils C09

Le relevé réel donne **12 abonnements C09 et 12 sans date de paiement validé**. En particulier **A-SANSMAIL est exclu pour `paiement_non_valide`, pas parce qu'il n'a pas d'email**. Son inclusion demandée par C13 n'est donc **pas démontrée** sur ce profil. Les états administratifs `active` de C09 ne sont pas silencieusement convertis en règlements ou mandats confirmés.

Les dates natives C09 sont des dates de fixture et aucun historique postal de clôture ni bloc C01 renouvelé n'était raccordé. C13 utilise C01 pour les numéros théoriques, puis C07 pour l'éligibilité ; il n'invente ni paiement, ni activation, ni renouvellement. Pour un abonnement ayant existé avant une clôture mais sans relevé antérieur, l'export ferme. Les changements observés après clôture ne changent pas les lignes antérieures (test au contrat daté du raccord, pas un historique natif antidaté).

Les profils offerts/groupés de C09 n'ont pas de lien natif bénéficiaire/groupe : ils restent hors de la démonstration positive. Le raccord livré couvre les souscriptions individuelles natives ; il ne revendique pas un adaptateur offert/Teams complet.

**Question fermée à arbitrer : autoriser un complément postal C13 explicitement fictif rattaché aux profils C09 (validation administrative et bloc C01 documentés), sans paiement, sans changer leurs états natifs et sans rouvrir C09/C10 : oui ou non ?** À défaut, ces gates restent fermées. Les deux témoins C13 actuels prouvent la chaîne native/CSV, mais ne remplacent pas cette acceptation.

## Rejouer

Depuis `C:/Users/Ced/imagine`, dans bash :

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --require-complete
```

La première commande rejoue **47 assertions PHP/HTTP**, relit les octets installés et vérifie la préservation C09/rôles/options/contenus. Code attendu : **0** pour les gates techniques. Elle journalise ses vrais exports, sans réinstaller ni réinitialiser les profils.

La seconde exécute les mêmes contrôles mais termine volontairement en **code 2** tant que l'acceptation C09 reste incomplète. `production/C-13/resultats.json` conserve explicitement `recette_complete=false` et les constats natifs, sans les présenter comme un succès global.

Installation ciblée déjà exécutée : `PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --deploy`. Elle ne passe pas par le constructeur global, ne réinitialise pas C09/C10/C11/C12 et n'installe rien sur le NUC. Les témoins C13 existants ne sont pas remis à zéro.

Commandes réellement exécutées et contrôle unitaire : `C:/Users/Ced/imagine/production/C-13/COMMANDES.md`. Références officielles et écart de procédure initial : `references.md`. Aucun email, envoi postal, paiement, achat, réseau métier réel, Git ou tâche planifiée n'a été lancé. La garde hors ligne est contrôlée par ses filtres, sans appeler ses transports.
