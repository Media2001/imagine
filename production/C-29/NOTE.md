# C29 — note de livraison V2

## Portée et fichiers partagés

**Le seul changement de bootstrap est le bloc C29 additif.** Le README reçoit une section C29 avant B12, sans retouche des sections antérieures. Réception complémentaire des voisins dans ce lot, jamais dans leurs paquets : C27, B11, C28, B12 ; le complément vivant `production/B-12/reception-complement-voisins-V2.json` est conservé exactement. L’empreinte globale brute du bootstrap de ces paquets est désormais historique, pas leur code.

Cible unique : `imagine-test-demo`, environnement `local`, URL gardée et coupe-circuit B00 email/HTTP/paiements relus. Pas de compte ni clé Brevo, aucun service, paiement, Odoo ou donnée réelle. Aucun fichier de bibliothèque close, de voie 1, du lanceur gelé ou d’import n’est modifié. Aucun Git ni fichier de verrou lu ou modifié.

## Ce qui est livré

- `ContactBrevoRegles::fiche` : calcul PHP pur unique, aucun accès à WordPress, au réseau ou au disque.
- `ContactBrevo` : lecture native WCS paginée, email/choix C22, statut B06, relations de lecture C13 et projection C24 directement consommés ; pas de copie des règles de consentement C24.
- Aperçu **Imagine → Ce qui partirait vers Brevo**, droits C19 inchangés, identifiant de compte par GET, fiche/raison et totaux sur tous les comptes ; privé/no-store et refus des écritures HTTP.
- Réglage distinct **Réglages → Tarifs de la fiche Brevo** : groupe Settings API autonome, administrateur seul. Cette configuration n’est pas le calcul ni l’écran de consultation. Aucun agrandissement du groupe C10 ni réouverture de son écran.
- Tests découverts par le paquet racine existant, recettes pure/native/HTTP et lecteur de preuves hors réseau sans argument. Les scripts de récupération sont historiques, **pas des commandes de rejeu**.

## Standard : cinq lignes

1. L’extension WordPress publiée par Brevo offre formulaires, listes et champs personnalisés, consentement/double opt-in et SMTP après raccord au compte.
2. Brevo for WooCommerce synchronise clients/nouveaux inscrits, historique et nouvelles commandes/données transactionnelles, avec opt-in/opt-out/double opt-in.
3. Ces fonctions ne définissent pas les règles Imagine : coopérateur, bénéficiaire offert/groupé, tarif, et « actif seulement » ne sont pas déduits des achats.
4. Aucune des deux extensions n’est installée ou activée ; aucun compte, clé, traceur, envoi ou synchronisation n’est créé.
5. Notices **publiées par Brevo** consultées dans le répertoire officiel WordPress : provenance et courts extraits dans `sources-officielles-V2.json` ; le centre d’aide derrière Cloudflare n’a pas été utilisé comme preuve.

## Règles et inconnus assumés

| Situation | Résultat |
|---|---|
| Email recevable + ≥1 lettre du catalogue choisie par le lecteur | Fiche calculée |
| Aucun choix, choix automatique à la création seul, choix d’une liste supprimée seul | Absente, raison explicite |
| Sans email recevable, marqueur sans-email ou domaine `.invalid` | Absente ; ne devient pas une demande de retrait |
| Toutes les lettres actuelles explicitement refusées par le lecteur | Fiche réduite à `statut=a_retirer` uniquement |
| Souscription WCS `active` | `abonne`, même sans déduction d’un paiement/droit |
| Grâce, suspension, expiration, pending-cancel ; adhésion manuelle seule, achat de numéro seul | `non_abonne` |
| Bénéficiaire identifié offert/groupé par les relations natives lues | Statut et tarif `inconnu` |
| Tarif non configuré, produit/variation hors liste, ligne absente, contradiction entre tarifs actifs | `inconnu`, sans montant calculé |
| Personnalisation | Valeur exacte de `Personnalisation::attributsConnecteur` ; le refus distinct laisse les réponses locales mais aucune étiquette dans la fiche |

**À définir par Imagine au branchement** : grille réelle et rattachement natif des tarifs, statut d’un bénéficiaire, noms d’attributs Brevo. Pas de prix, de droit d’accès, de double confirmation ou de correspondance externe inventés. La liste fermée peut être modifiée par l’administration sans changer de prix ni donner de droit. Défaut de production : vide. La seule démonstration reçoit les six couples produit/code de C09 existants, sans recopier leurs prix. `demo-tarifs-idempotent-V2.json` prouve le second passage sans changement.

Les profils C09 P-OFFERT/P-BENEF ne possèdent pas de lien cadeau/groupe installé : ils ne sont pas présentés comme bénéficiaires natifs. Le tableau indépendant les compte sans souscription ; deux variantes ajoutent des liens natifs temporaires pour prouver `inconnu`, puis restaurent leur état. Aucune identité n’est déduite d’un login ou d’un email. Le contrat C13 consommé fournit les bénéficiaires identifiés, pas une nouvelle intégration Teams.

## Preuves et limites

- Tableau attendu indépendant des **27 comptes C09** : `wp/tests/demo/c29-attendus.php`, avec comparaison des champs complets, et par HTTP aussi. Les trois visiteurs sans compte du catalogue C09 ne sont pas inventés comme contacts ; compte inexistant éprouvé séparément.
- Calcul pur : **21 contrôles**, dont toutes les classes d’état, retrait, choix automatique, coopérateur, liste fermée, valeurs inconnues/contradictoires et absence de mutation des entrées.
- Réception native : **51 contrôles**, dont les 27 profils. Positif consentement + attribut fictif, retrait du seul consentement distinct, puis mutant du vrai adaptateur lisant les réponses brutes : le contrôle d’absence le détecte.
- SQL non-SELECT, HTTP et mail interceptés pendant calcul/rendu, puis témoins positifs effectivement détectés et bloqués avant transport. Pas un simple compteur à zéro sans témoin.
- Réception HTTP : **73 contrôles**, 27 vrais aperçus du référent et leurs observations de rendu, totaux exacts tous comptes, administrateur, refus 403/405, HEAD vide, identifiant absent/invalide, vrai menu et formulaire GET, vraie configuration native distincte sauvegardée/relue puis restaurée.
- Les ressources Gravatar de l’administration native sont séparément détectées et bloquées par Chromium avant transport. Le contenu C29 n’ajoute ni ressource tierce ni script. Le zéro tentative concerne le calcul/rendu C29, **pas l’amorçage entier de WordPress**.
- Les trois volatilités C19 sont conservées : `_transient_timeout_wcs_woocommerce_active_version`, `_transient_timeout_novamira-pro_update_checker`, `action_scheduler_lock_async-request-runner`. Trois autres **seules expirations de cache d’amorçage réellement observées** dans `http-first-V2.json` : `_transient_timeout_novamira_update_info`, `_transient_timeout_as_is_ensure_recurring_actions_scheduled`, `_transient_timeout_woocommerce_admin_settings_payments_has_providers_with_incentive`. Aucune option métier ou ligne d’action/log n’est exclue pour verdir la réception.
- L’empreinte native réutilisée de C18 exclut ses quatre clés de métadonnées volatiles (sessions, panier persistant, `_last_update`, `wc_last_active`). Les sessions du rejeu HTTP final sont en plus comparées/restaurées explicitement, sans secret dans les preuves. Les états, rôles, profils et tables de planification restent contrôlés.
- Une exception remontée de source WCS affiche « indisponible » sans faux zéro, avec point de panne natif réellement atteint. Comme C19, ce n’est pas une garantie sur une erreur SQL absorbée en liste vide par Woo.
- Lecture linéaire sur tous les comptes et relations, sans cache persistant : proportionnée à la démo ; pas de qualification de volume réel.

## Incidents de banc, corrigés et tracés

1. Une première mise en place de lien cadeau via sauvegarde WCS a programmé son rafraîchissement de rapport au shutdown, **après** le rollback. Détecté par les empreintes brutes d’actions/logs, non masqué. Deux essais ont été réparés par inverse strictement bornée et contrôlée au checksum original **avant commit** (`recovery-setup-shutdown*-V2.json`). Le banc final prépare les seuls liens natifs dans une transaction sans hooks de sauvegarde WCS ; production inchangée. Ses empreintes de planification sont réellement identiques avant/après.
2. Le premier parcours HTTP était fonctionnellement vert mais son nettoyage initial omettait réserves/journaux de catalogue C22/C24 et transients du formulaire de configuration ; retrait ciblé prouvé. Un deuxième nettoyage a refusé, à raison, une famille de journal non listée par erreur (`imagine_newsletters_catalogue`), interrompant son `finally`. Récupération limitée aux champs touchés, depuis le snapshot privé **préexistant** de C27, avec égalité des empreintes C29 originales des profils/options métier et tables natives exigée avant commit (`recovery-HTTP-finally-interrupted-V2.json`). Aucun paquet C27 n’a été changé.
3. **Limite historique précise** : aucune empreinte des sessions du départ de ce deuxième essai interrompu n’avait été conservée ; leur égalité octet pour octet à ce départ n’est donc pas revendiquée. Elles ont été remises depuis le snapshot privé. Les profils et actions originaux sont, eux, prouvés identiques. Le rejeu HTTP de réception, postérieur, conserve sa préimage métier hors sessions et l’empreinte des sessions avant toute mutation, et prouve leur restauration exacte à son propre départ. Cookies et jetons ne sont jamais écrits dans le dépôt.
4. Un diagnostic additionnel de changement d’état Memberships dans le même processus rencontrait son cache d’objet natif, pas une règle C29. Il n’est pas compté comme preuve d’un bénéficiaire expiré ; retiré du scénario final, données rollbackées. Le lot consomme le contrat de lecture existant, sans rouvrir cette bibliothèque.

## Réception

Image canonique reconstruite avant PRET. Rejeu standard réellement exécuté : **1 203 tests / 36 657 assertions**, aucun échec/erreur/ignoré ; **22 outils / 720 contrôles**, aucun échec. Les trois tests C29 représentent **47 assertions** dans le JUnit réel. Les paquets **A31/A32 restent rouges hors lot**, aux codes connus, sans modification.

Le complément courant vérifie **C27 628 ; B11 32/35 ; C28 31/37 ; B12 hors réseau et lecture native** sur le bootstrap courant, en ne retirant que les ajouts exacts C29 puis B12 pour leurs contrats respectifs. Un octet étranger au bloc C29 est refusé. Les recettes mutantes historiques des voisins ne sont pas rejouées ; leurs lecteurs indépendants et le rejeu unitaire courant le sont. `UI_save_verified=false` de B11 reste inchangé.

`PRET` signifie **prêt technique pour les relectures**, pas clôture, validation visuelle de Ced, conformité juridique ou autorisation sur le réel. Lecteur hors réseau sans argument et lecture du seul site fictif : `verifier.py`, `verifier.py --live`.
