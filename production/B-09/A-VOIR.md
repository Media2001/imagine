# B-09 — à ouvrir et à vérifier

**Squelette complet du brief, prêt technique à relire ; validation visuelle de Ced attendue.** Démonstration entièrement fictive `imagine-test-demo`, aucun réel, email, tiers ou paiement. Ni texte juridique ni design livré.

## Adresses

| Ouvrir | Attendu |
|---|---|
| <http://192.168.129.32:8085/> | Pied de page : cinq liens natifs ci-dessous ; menu principal inchangé |
| <http://192.168.129.32:8085/faq-service-client/> | Quatre rubriques : Accès numérique, Abonnement, Facturation, Livraison ; aucune question/réponse |
| <http://192.168.129.32:8085/conditions-generales-de-vente/> | Intitulé et contenu vide |
| <http://192.168.129.32:8085/politique-de-confidentialite/> | Intitulé et contenu vide ; vraie page native déclarée |
| <http://192.168.129.32:8085/gestion-des-cookies/> | Intitulé et contenu vide ; aucun bandeau ajouté |
| <http://192.168.129.32:8085/contact/> | Nom, adresse électronique, message, consentement au recontact non coché ; aucun envoi |
| <http://192.168.129.32:8085/wp-admin/edit.php?post_type=page> | Éditer la FAQ sans code : sous un Titre, ajouter Détails, question dans son résumé et réponse dans son paragraphe intérieur |
| <http://192.168.129.32:8085/wp-admin/options-privacy.php> | Politique sélectionnée : page B-09 `Politique de confidentialité` (ID 3316) |
| <http://192.168.129.32:8085/wp-admin/nav-menus.php> | Menu `imagine-b09-footer` (ID 38), emplacement `imagine-footer`, cinq éléments ; principal ID 22 conservé |
| <http://192.168.129.32:8085/wp-admin/edit.php?post_type=imagine_contact> | Administration seule ; liste vide après nettoyage des essais |
| <http://192.168.129.32:8085/wp-admin/export-personal-data.php> et <http://192.168.129.32:8085/wp-admin/erase-personal-data.php> | Outils natifs existants, callbacks additionnels `imagine-contacts` |

Comptes fictifs et connexion : mécanisme existant B-00/C-09, aucun identifiant dans le dépôt. Les pages finales ont les IDs 3314–3318 ; les premiers IDs de développement 3296–3305 ont été retirés puis leur absence relue, afin de refaire l’interruption avec le seed final.

## Commande de vérification parent — sans argument au script

Depuis `C:\Users\Ced\imagine`, avec le Python 3.11.15 effectivement utilisé :

```powershell
python -B production/B-09/verifier.py
```

Python standard seulement : aucun site, Docker, réseau ou mutation. Il contrôle les empreintes B-09, les contrats des fichiers partagés, les ensembles exacts de contrôles, les compteurs recalculés, les vrais logs rouges de mutations, les inverses et le dernier readback. Le manifeste ne fige ni les files d’orchestration ni les paquets des autres lots.

## Rejouer les vrais tests

Une étiquette neuve à chaque appel, pour conserver les reçus antérieurs :

```powershell
python -B wp/outils/demo/b09-local.py parent-unitaires-NOM-NEUF
python -B wp/outils/demo/b09-mutations.py parent-mutations-NOM-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Ces deux premiers appels utilisent des conteneurs isolés hors réseau, copies temporaires et dépôt en lecture seule. Les six tests Contact sont également découverts par la suite PHPUnit racine existante, sans manifeste Composer ou bibliothèque close modifié.

Les recettes suivantes utilisent **exclusivement** la démonstration fictive, avec préimages durables privées, nettoyage et readback ; ne pas les confondre avec le vérificateur de paquet :

```powershell
python -B wp/outils/demo/b09.py runtime parent-structure-NOM-NEUF
python -B wp/outils/demo/b09.py reseed parent-seed-stable-NOM-NEUF
python -B wp/outils/demo/b09-recette.py parent-contact-NOM-NEUF
python -B wp/outils/demo/b09-readback.py parent-readback-NOM-NEUF
```

Ne pas rejouer `seed` sur le squelette livré : c’est la recette de **première création** déjà interrompue puis reprise réellement sous trois processus. La preuve finale est `pages-reprise-finale.json` ; `reseed` démontre ensuite l’absence de réécriture sur le squelette complet.

## Preuves retenues

- `tests-finaux.log` : **6 tests, 188 assertions**, sans échec ; doubles d’écriture conformes au déséchappement WordPress.
- `structure-finale-verifiee.json`, `pages-reprise-finale.json`, `recette-finale.json` : ensembles exacts de **16 + 6 + 31 = 53 contrôles natifs**, sans échec. Readback final séparé dans `readback-final.json`.
- `mutations-finales.json` et ses douze logs : **12 mutations de sources détectées** ; mutation réelle REST/recherche supplémentaire dans `recette-finale.json`, suivie du retour au vert.
- `reprise-stable-finale.json` : deux rejeux, mêmes IDs et mêmes lignes existantes, état métier conservé ; la première mesure avait révélé une actualisation des dates natives des cinq items. Corrigée, prouvée rouge/verte (`red-seed-stable.json`, `green-seed-stable.json`), puis rejouée sur la fixture finale.
- `preparation-finale.json/.log` : reconstruction et vérification hors ligne de l’image par **le vrai `wp/tests/preparer-image.ps1`**.
- `regression-finale.json/.log` : dernier rejeu général, nombres exacts dans `final-V2.json`. Le premier `regression.json/.log` est un **échec historique** (conteneur disparu avant inspection), jamais un succès ; le rejeu a été refait après cinq minutes, sans modifier le lanceur.
- `final-V2.json`, `verifier.py` : paquet vérifiable, contrats B-09 du bootstrap/footer/README ; aucun ancien paquet rescellé.

Stockage pour l’import de la voie 1, dix sources officielles consultées, choix prudents et limites : **`NOTE.md`**. Les callbacks de confidentialité sont réellement exécutés par leur registre natif, pas un nouvel export maison ; le ZIP global WordPress et son email ne sont pas rejoués ici. Pas de prétention de conformité juridique, de validation graphique, d’anti-spam ou de rétention automatique de production. La réception de ce squelette est complète pour B-09, pas une mise en ligne.
