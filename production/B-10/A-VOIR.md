# B-10 — à voir sur la démonstration fictive

## Ouvrir

- **Liste et recherche** : http://192.168.129.32:8085/points-de-vente/
- **Même résultat, sans accents/en majuscules** : http://192.168.129.32:8085/points-de-vente/?localite=ETOILE-FICTIVE
- **Code postal exact** : http://192.168.129.32:8085/points-de-vente/?localite=00001
- **Préfixe postal volontairement sans résultat** : http://192.168.129.32:8085/points-de-vente/?localite=000
- **Administration native** (administrateur fictif existant) : http://192.168.129.32:8085/wp-admin/options-general.php?page=imagine-points-vente

Les **30 commerces, toutes les localités et adresses sont entièrement fictifs**. Ils restent en place pour Ced. Page native ID **3410**, lien de pied de page **3411**, menu B09 **38** conservé ; principal et cinq liens B09 inchangés. Aucun nouveau style : squelette B01. Capture mobile : `page-mobile.png`.

Sans recherche : 30 résultats triés par localité puis nom. `Étoile-Fictive`, `etoile-fictive`, `ETOILE-FICTIVE`, la forme accentuée décomposée et `00001` trouvent les mêmes 5 commerces. Ni rayon, ni recherche partielle, ni préfixe postal.

## Essayer l’import et le réglage de carte

1. Lire/copier `mapping-exemple.json` dans la correspondance de l’écran ; séparateur `;` ; enregistrer.
2. Charger `commerces-fictifs.csv` : **30 lignes prises, 1 refusée, ligne 32 : nombre_colonnes**, sans recopier la ligne. Recharger conserve les mêmes IDs et 30 commerces, sans doublon.
3. `personne` et `telephone` ne figurent pas dans le mapping fourni : leurs colonnes témoins ne sont ni rangées ni affichées. Une ligne explicite du mapping est nécessaire pour chacune ; le retrait de cette ligne masque immédiatement son affichage.
4. Un en-tête inconnu est refusé en conservant la liste. Si toutes les lignes sont refusées : 0 prises et numéros/motifs rendus, ancienne liste conservée aussi.
5. **Afficher une carte = Non** à la livraison, et par défaut : aucun emplacement ajouté. **Oui** : simple emplacement « Carte non raccordée », aucune carte ni fournisseur, géocodage, image, iframe ou script tiers. Remettre Non après essai.

## Vérifier (depuis la racine du dépôt)

```text
python -B wp/tests/demo/b10-verifier.py
python -B wp/tests/demo/b10-verifier.py --live
```

La première commande est autonome, hors réseau, Python standard ; elle lie sources, fixtures, note, README B10 et preuves finales. La seconde ajoute uniquement le readback sur imagine-test-demo, les 30 commerces, la carte OFF, l’absence de runners temporaires et les navigations.

Rejouer réellement les tests (étiquettes neuves pour ne pas écraser les preuves) :

```text
python -B wp/outils/demo/b10-local.py parent-unitaires-NOM-NEUF
python -B wp/outils/demo/b10.py runtime parent-natif-NOM-NEUF
python -B wp/outils/demo/b10-recette.py parent-navigateur-NOM-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

`runtime` fait un rollback InnoDB et relit l’état initial ; pas de bouchon WordPress. `recette` emploie de vraies sessions fictives et de vrais formulaires natifs/multipart ; sessions restaurées exactement et observateur temporaire supprimé puis relu. Elle recharge la fixture et laisse la carte OFF. Ne pas relancer un initialiseur historique B09 pour ajouter B10 : le seed additif B10 reprend ses propres objets sans réécrire les objets B09.

## Réception et limites

- **6 tests PHPUnit, 27 assertions ; 12 contrôles natifs ; 26 contrôles navigateur** : tous verts. Rouges conservés (fonction absente, recherche absente, retrait du mapping personnel, toutes lignes refusées), puis verts.
- `recette-reception.json` contient les requêtes réellement observées pour les deux valeurs de carte : **zéro requête tiers sur la page publique** ; détecteurs testés par témoins positifs bloqués avant transport. Aucune tentative email/HTTP issue du code B10.
- Limite séparée : l’administration native tente ses avatars Gravatar ; la recette les détecte et les bloque avant transport. Ce n’est pas une carte ni un appel B10. Les appels HTTP d’ambiance du cœur sont aussi bloqués par B00 et distingués des tentatives B10.
- `preparation-reception.log` : image reconstruite et vérifiée avant PRET. `regression-reception.log` : **1 175 tests, 36 407 assertions, aucun échec/erreur**, 584 contrôles outils verts. Le bilan de paquets relève **A-32 / A32_PARTIAL_EVIDENCE**, hors B10 : signalé, aucun fichier de ce lot touché.
- Décision technique : correspondance/import et carte regroupés sur l’écran natif d’import dédié ; aucun déplacement ni changement de l’écran C10 clos. La règle de placement des sections C10 demeure pour ses sections existantes ; à confirmer en relecture si l’on veut y déplacer ce réglage technique.
- Plafonds techniques : UTF-8, 2 Mio, 2 000 commerces acceptés, champs de 500 caractères ; pas de détection automatique du format. Un arrêt brutal peut laisser un verrou d’import : diagnostic manuel, aucune tâche de reprise inventée.
- Validation visuelle de Ced attendue ; fournisseur et consentement d’une éventuelle carte future non choisis (`NOTE.md`, trois lignes). Aucun raccord C21, paiement, compte réel, email, tiers applicatif, production, B11 ou C28.
