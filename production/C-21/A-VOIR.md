# C-21 — Export et effacement natifs

Site entièrement fictif : **imagine-test-demo**, `http://192.168.129.32:8085`. Compte C09 **E-ADMIN** pour les outils WordPress, droits natifs inchangés ; identifiants privés habituels hors dépôt. Aucun compte réel, email, paiement ni service externe.

## Où ouvrir

- Export : `http://192.168.129.32:8085/wp-admin/export-personal-data.php`.
- Effacement : `http://192.168.129.32:8085/wp-admin/erase-personal-data.php`.
- Suppression du compte, distincte de l’effacement RGPD : `http://192.168.129.32:8085/wp-admin/users.php`.
- Conservation Woo/WCS, **lecture seule** : `http://192.168.129.32:8085/wp-admin/admin.php?page=wc-settings&tab=account`.
- Memberships : `http://192.168.129.32:8085/wp-admin/admin.php?page=wc-settings&tab=memberships`.
- Journal C10 : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages`.

## Ce que montre la preuve

Le compte jetable `imagine-c21-fictif` a porté toutes les familles de l’inventaire : deux marqueurs, découverte, historique postal et gel, commande/numéro acheté, souscription active et dates de grâce, brouillon de commande, justificatif privé et décision historisée C10, opérateur d’extraction C18. Il n’existe plus à la livraison.

L’export réel utilise **le formulaire natif**, confirmation email décochée, puis les AJAX natifs et **Télécharger les données personnelles**, jamais « Envoyer le lien ». L’archive native HTML/JSON est téléchargée et relue : groupes Imagine présents, document en base64 aux octets vérifiés ; ni mot de passe, jeton, référence de paiement, note interne, chemin/blob documentaire, ni adresse technique `.invalid`. Un marqueur sans-email masque aussi une adresse technique hors `.invalid` (témoin A-SANSMAIL, lu sans mutation).

Même création de demande sans email pour l’effacement, puis effaceurs natifs. Deux vraies pages d’export et d’effacement Imagine ; relecture : plus de donnée personnelle dans notre exporteur, plus de document/brouillon, idempotence, tiers préservés. Les coordonnées/adresses du compte restent soumises aux effaceurs natifs Woo. Le compte WordPress n’est **pas** supprimé par cet outil : la suppression native distincte termine le parcours. L’export d’essai, ses demandes, objets commerciaux et compte sont retirés dans `finally`.

## Réglages relus, jamais changés

`conservation-complete.json` en donne valeurs stockées, défauts et valeurs effectives :

| Réglage natif | Valeur effective |
|---|---|
| Retrait des données des commandes sur demande | `no` |
| Retrait des données des souscriptions | `no` (option absente, défaut natif) |
| Retrait des téléchargements | `no` |
| Retrait en masse des données des commandes | `no` |
| Suppression des adhésions Memberships sur demande | `no` |
| Conservation comptes inactifs | nombre vide, unité mois |
| Commandes pending / failed / cancelled | nombre vide, unité jours après parsing natif |
| Commandes refunded / completed | nombre vide, unité mois |
| Abonnements terminés | nombre vide, unité mois (défaut natif) |

Aucune durée de purge n’est activée par ces valeurs vides. **Ce n’est pas une décision de durée légale de conservation.** Avec ces réglages, l’essai garde sa commande en attente et sa souscription **active**, propriétaire inchangé : aucun supplément d’effacement commercial ni règle d’annulation Imagine. Les numéros de ligne et dates ajoutés aux objets commerciaux restent avec ces objets, sous le standard ; ils ne sont pas un fichier personnel parallèle.

## Journal et limites explicites

- C10 garde tous les événements ; pas de purge ni durée inventée. C21 retire seulement le lien au dossier du titulaire et ses catégories/états/fins des avant/après, en gardant l’événement daté et l’opérateur. Si la personne est elle-même opérateur, son ID/login sont anonymisés. Les journaux C13/C18 affichent 50 événements mais n’ont pas de purge : les compteurs ne sont pas des listes d’abonnés. C18 n’est concerné pour un abonné que s’il y apparaît comme opérateur.
- Le gel postal conserve numéro/calendrier/clôture et observations des tiers ; le retrait personnel utilise un compare-and-swap relu, seule exception de confidentialité à l’immutabilité habituelle. Aucun moteur C01/C06/C07 ou règle pure C13 changé.
- **Conserver la demande native d’effacement terminée tant que le compte n’a pas été supprimé.** Elle sert, sans nouveau marqueur ni durée, à ne pas recollecter depuis les objets commerciaux que le standard garde. Supprimer cette demande alors que le compte et ses objets natifs sont conservés peut autoriser une nouvelle observation. Aucun mécanisme de conservation parallèle n’est ajouté ; après suppression du compte, les observations de cet ancien titulaire sont refusées.
- Quotas/catégories/règles globales, contenus éditoriaux, agrégats C19 et marqueurs de fixtures ne sont pas des dossiers de personne. Le stockage de lecture B03 est local au navigateur, hors base WordPress. Les CSV téléchargés sur un poste ne sont pas un stockage serveur à effacer ici.
- Les caches de rapports natifs WCS peuvent créer/annuler des tâches lors de la création/suppression de la fixture. Seul `wcs_report_update_cache` est exclu de la comparaison du planificateur ; toutes les autres actions/logs et l’action **8793, pending, subscription_id=101** sont contrôlés exactement. C09 : 382/382 ; aucun reset.

## Rejouer / vérifier

Depuis la racine du dépôt, commandes sans modification de la file ou d’un autre lot :

```powershell
python -B wp/outils/demo/c21-unit.py unit-relecture
python -B wp/tests/demo/c21-http.py http-relecture
python -B wp/outils/demo/c21.py security security-relecture
python -B wp/outils/demo/c21.py regressions regressions-relecture
python -B wp/tests/demo/c21-verifier.py
```

Les labels des reçus sont uniques : ne pas écraser un reçu existant. Le parcours HTTP crée sa seule fixture et la supprime à la fin. Le dernier contrôle ne modifie ni site ni preuves. Préparation d’image et T01 complet réellement exécutés ; aucun fichier T01, bibliothèque close, C20, B05 ou C22 modifié. Les chemins et captures historiques des autres lots ne sont pas réécrits. Ceci est un prêt technique pour relecture, pas une clôture ni un GO réel.
