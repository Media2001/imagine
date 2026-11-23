# C-10 — À voir

## Ouvrir l’écran

Sur **imagine-test-demo seulement** :

**http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages**

Se connecter avec le profil fictif **E-ADMIN** (login `e-admin`, rôle administrateur). Les identifiants restent dans `C:/Users/Ced/.imagine-demo/identifiants.json`, hors dépôt. Aucun mot de passe dans ces documents.

Menu natif **Imagine › Réglages**, trois domaines et huit réglages :

- **Accès** : contenus pas encore parus, PDF des robots vérifiés, PDF antérieurs à l’abonnement.
- **Paiement en quatre fois** : marge civile avant clôture, confirmation du premier SEPA, échéances après rejet, changement de tarif.
- **Liste d’envoi** : choix et ordre des colonnes CSV.

Chaque champ indique son effet, son défaut et « À confirmer par Imagine ». La marge est vide par défaut : le moteur refuse de planifier, il ne choisit aucun nombre de jours. Cet écran ne crée ni paiement, ni email, ni envoi postal.

## Effet réel sur un article : changer puis recharger

Ouvrir **http://192.168.129.32:8085/?p=188** dans un deuxième onglet de la même session **E-ADMIN**. C’est « Témoin C10 — lecture de l’équipe avant parution », entièrement fictif, rattaché à un numéro témoin dont la sortie est le **1er janvier 2099**.

1. Dans **Accès › Contenus pas encore parus**, laisser **Fermé pour tous** et enregistrer. Recharger l’article : extrait et bloc d’accès, pas de corps.
2. Choisir **Ouvert à l’équipe uniquement**, enregistrer et recharger le même article. La phrase **« Les lanternes turquoise de C10 éclairent le jardin imaginaire. »** devient visible.
3. Ouvrir ce même lien en navigation privée : le corps reste fermé. Un visiteur ordinaire n’acquiert aucun droit.
4. Revenir à **Fermé pour tous**, enregistrer, puis recharger dans la session E-ADMIN : le corps est de nouveau fermé.
5. Le journal contient les deux changements exacts. Un réenregistrement identique n’ajoute aucun événement.

Cette manipulation a été vérifiée par vrais POST `options.php` et GET de l’article. Les réglages sont restaurés. Le témoin reste disponible : article **188**, numéro brouillon **187**, option `imagine_c10_fixture`. Le numéro brouillon ne remplace pas une carte kiosque ; l’article est daté de 2000 pour ne pas remplacer les nouveautés. Aucun contenu B00/C08/C09 n’est modifié pour ce témoin.

## Effet complémentaire sur l’export CSV

Cette démonstration utilise le **véritable exporteur CSV C07**, pas un rendu imitant un export.

1. Dans **Liste d’envoi**, noter les neuf colonnes affichées.
2. Remplacer leur contenu par ces trois lignes, dans cet ordre :

   ```text
   ville
   destinataire
   pays
   ```

3. Cliquer **Enregistrer les réglages**.
4. Sous le formulaire, **Aperçu CSV fictif — effet du réglage Liste d’envoi** contient désormais :

   ```csv
   ville,destinataire,pays
   "Ville Fictive","Lectrice Fictive C10",BE
   ```

   Il est généré par `ExportCsv::lignes()` avec le format relu en base par l’adaptateur C07. Seules les colonnes changent : aucun destinataire ni droit n’est modifié et rien n’est envoyé.
5. Le **Journal des modifications** contient votre login, votre ID, l’heure UTC, l’ancienne liste et la nouvelle liste. Réenregistrer sans changement n’ajoute aucun événement.
6. Essayer `ville` deux fois : message de refus ; les trois colonnes précédentes sont conservées, sans événement de changement.
7. Restaurer le défaut, une colonne par ligne :

   ```text
   abonnement_id
   destinataire_id
   destinataire
   rue
   complement
   code_postal
   ville
   pays
   origine
   ```

Le runner a déjà effectué cette manipulation par **POST réel vers `options.php`**, vérifié le CSV et restauré les défauts. Le journal des essais est volontairement conservé.

## Vérifications et limites

- **E-REDAC** et **E-ABO** (gestion WooCommerce) : page et enregistrement interdits, même avec leur propre nonce valide. Un abonné est également refusé ; WooCommerce redirige son POST vers « Mon compte » avant le traitement des options.
- Nonces absent, invalide et d’une autre session : HTTP 403 sans écriture.
- Valeur invalide : conservation de l’ancienne configuration du domaine concerné. Les autres domaines valides peuvent être enregistrés : il ne s’agit pas d’une transaction globale des trois domaines.
- Le journal affiche les 50 événements les plus récents ; tous restent conservés, une option non autoloadée par événement. C’est un journal administratif, pas un journal inviolable contre un administrateur de base de données.
- **Les trois réglages Accès sont lus par le paywall C08.** Les deux choix PDF ont été vérifiés aux deux positions via la décision PDF de l’adaptateur et les options natives relues. Aucun téléchargement PDF protégé ni contrôle DNS d’un robot réel n’est livré par ce lot. Le raccord Paiement reste futur : ces valeurs ne modifient pas encore le paiement du site, comme l’indique maintenant l’écran.
- **Journal KO : modification refusée**, ancienne valeur restaurée et message d’erreur. Échec d’insertion réellement injecté dans la recette native. Pas de mécanisme de reprise ; conservation sans purge acceptée par l’arbitrage.
- A-VIR reste fermé avec le motif **`virement_non_valide`**, pas `suspendu`. Le rôle **`imagine_referent_abonnements`** est reconnu pour la lecture équipe ; sa création et son affectation native appartiennent à C09, pas à C10.
- Preuves à jour : `verification-finale.json`, `installation.json`, `http-verification.json`, `correction-final-unit.json`, `correction-final-phpunit.log` et `correction-final-phpunit.xml`. La suite PHPUnit de la façade est découverte par `composer test` ; `composer lint` passe.
- Le navigateur arrive à la connexion, mais le coffre ne propose aucun identifiant enregistré. Aucune saisie de secret ni contournement du coffre : pas de capture d’administration authentifiée. Les preuves HTTP utilisent des sessions WordPress natives éphémères des comptes fictifs, détruites et relues après les essais.

Validation visuelle par Ced toujours à faire ; `PRET` signifie livré et vérifié pour cette relecture, pas validé visuellement.
