# B-09 — à ouvrir et à vérifier après corrections

**Instructions 1–5 appliquées ; prêt technique à relire ; validation visuelle de Ced attendue.** Démonstration entièrement fictive `imagine-test-demo`, aucun réel, email, tiers ou paiement. Ni texte juridique ni design livré.

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

Depuis `C:\Users\Ced\imagine`, avec Python standard :

```powershell
python -B production/B-09/verifier.py
```

Python standard seulement : aucun site, Docker, réseau ou mutation. Il contrôle `corrections-final-V2.json`, les empreintes B-09, les contrats partagés, les ensembles exacts de contrôles, les compteurs, les rouges, la reprise durable et le dernier readback. L'ancien `final-V2.json` reste historique. Ni les files d'orchestration ni les paquets des autres lots ne sont figés.

## Rejouer les vrais tests

Une étiquette neuve à chaque appel, pour conserver les reçus antérieurs :

```powershell
python -B wp/outils/demo/b09-local.py parent-unitaires-NOM-NEUF
python -B wp/outils/demo/b09-mutations.py parent-mutations-NOM-NEUF
python -B wp/outils/demo/b09-local.py parent-meta-NOM-NEUF meta-partielle
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Ces appels utilisent des conteneurs isolés hors réseau, copies temporaires et dépôt en lecture seule. Les sept tests Contact sont découverts par la suite PHPUnit racine existante, sans manifeste Composer ou bibliothèque close modifié. Le mutant `meta-partielle` doit sortir 1 avec un échec PHPUnit, pas une erreur PHP.

Les recettes suivantes utilisent **exclusivement** la démonstration fictive, avec préimages durables privées, nettoyage et readback ; ne pas les confondre avec le vérificateur de paquet :

```powershell
python -B wp/outils/demo/b09.py runtime parent-structure-NOM-NEUF
python -B wp/outils/demo/b09-corrections.py parent-interruption-NOM-NEUF
python -B wp/outils/demo/b09-correction-live.py partial parent-partiel-NOM-NEUF
python -B wp/outils/demo/b09.py reseed parent-seed-stable-NOM-NEUF
python -B wp/outils/demo/b09-recette.py parent-contact-NOM-NEUF
python -B wp/outils/demo/b09-readback.py parent-readback-NOM-NEUF
```

Ne pas rejouer `seed` sur le squelette livré : c'est la recette de première création historique (`pages-reprise-finale.json`). `b09-corrections.py` interrompt réellement un nouvel item après le marqueur et avant l'option, prouve sa reprise puis restitue l'item initial ; `reseed` prouve ensuite l'absence de réécriture sur le squelette complet.

## Preuves retenues

- `corrections-final-unit.log` : **7 tests / 203 assertions**, zéro échec ; doubles d'écriture conformes au déséchappement. Rouge préalable : `corrections-red-partielle.log`, un vrai échec attendu, post disparu/texte survivant.
- **61 contrôles natifs verts** : structure 21, HTTP/contact 31, interruption exacte 4, suppression partielle native 5. Reçus `corrections-structure.json`, `corrections-recette.json`, `corrections-green-seed.json`, `corrections-effacement-natif.json`.
- **14 mutations de sources détectées** : douze rejouées sur le code corrigé (`corrections-final-mutations.json`), relecture des métas retirée (`corrections-final-mutant-meta.log`), scan des marqueurs retiré dans un runner temporaire (`corrections-mutation-scan.json`, cinq contrôles rouges). Les injections natives REST/recherche et suppression partielle sont observées puis inversées.
- `corrections-stable.json` : deux rejeux, mêmes IDs et lignes, état métier conservé. IDs des pages et menus livrés inchangés.
- `corrections-preparation.json/.log` : **vrai `wp/tests/preparer-image.ps1`**, image vérifiée.
- `corrections-final-regression.json/.log` : **1 167 tests / 36 333 assertions**, **22 outils / 584 contrôles**, zéro échec ; **11 paquets vérifiés, zéro échec**, A-32 hors rejeu (journaux absents). Les quatre anciens rouges voie 1 ne sont plus rouges dans ce rejeu ; aucun de leurs fichiers n'a été modifié ici.
- `corrections-final-readback.json` : aucun contact, aucune méta personnelle, aucune option de reprise ; cinq runners/observateurs temporaires absents, sources distantes relues, état initial hors B-09 conservé.
- `corrections-final-V2.json`, `verifier.py` : paquet courant vérifiable ; anciens reçus et `final-V2.json` historiques, sans faux resceau.

Instructions 1–5 et décisions techniques : **`CORRECTIONS.md`**. Duplication Contact/Sujet et chaîne de succès restent en place par défaut technique. Stockage pour l'import, choix natifs et limites : **`NOTE.md`**. Les callbacks sont exécutés par leur registre natif ; ZIP global et email non rejoués. Aucune conformité juridique, validation graphique, rétention ou anti-spam de production revendiqués. Aucun lot clos étendu.
