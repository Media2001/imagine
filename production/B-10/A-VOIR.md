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
2. Charger `commerces-fictifs.csv` : **30 lignes prises, 1 refusée, ligne 32 : Nombre de colonnes incorrect.**, sans recopier la ligne. Recharger conserve les mêmes IDs et 30 commerces, sans doublon (mapping inchangé, ordre des clés compris).
3. `personne` et `telephone` ne figurent pas dans le mapping fourni : leurs colonnes témoins ne sont ni rangées ni affichées. Une ligne explicite du mapping est nécessaire pour chacune ; le retrait de cette ligne masque immédiatement son affichage.
4. Un en-tête inconnu est refusé en conservant la liste. Si toutes les lignes sont refusées : 0 prises et numéros/motifs rendus, ancienne liste conservée aussi.
5. **Afficher une carte = Non** à la livraison, et par défaut : aucun emplacement ajouté. **Oui** : simple emplacement « Carte non raccordée », aucune carte ni fournisseur, géocodage, image, iframe ou script tiers. Remettre Non après essai.

## Vérifier (depuis la racine du dépôt)

```text
python -B wp/tests/demo/b10-verifier.py
python -B wp/tests/demo/b10-verifier.py --live
```

La première commande est autonome, hors réseau, Python standard ; elle lie sources, fixtures, note, seule section README B10 et preuves corrigées de `corrections-reception-V2.json`. La seconde ajoute uniquement le readback sur imagine-test-demo, les 30 commerces, la carte OFF, la reprise vide, l’absence de runners temporaires et les navigations.

Rejouer réellement les tests (étiquettes neuves pour ne pas écraser les preuves) :

```text
python -B wp/outils/demo/b10-local.py parent-unitaires-NOM-NEUF
python -B wp/outils/demo/b10-local.py parent-repli-NOM-NEUF --sans-intl
python -B wp/outils/demo/b10.py runtime parent-natif-NOM-NEUF
python -B wp/outils/demo/b10-recette.py parent-navigateur-NOM-NEUF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

`runtime` fait un rollback InnoDB et relit l’état initial ; pas de bouchon WordPress. `recette` emploie de vraies sessions fictives et de vrais formulaires natifs/multipart ; sessions restaurées exactement et observateur temporaire supprimé puis relu. Elle recharge la fixture et laisse la carte OFF. Ne pas relancer un initialiseur historique B09 pour ajouter B10 : le seed additif B10 reprend ses propres objets sans réécrire les objets B09.

## Réception et limites

- **14 tests PHPUnit, 80 assertions ; 13 contrôles natifs ; 31 contrôles navigateur** : tous verts. Rouges puis verts de chaque correction conservés (`corrections-rouge-*.log`, `corrections-vert-*.log`). Repli latin sans intl testé en PHP isolé ; décomposition intl réellement testée sur WordPress natif. Recherche NFC/NFD hors ancienne table, `œ/oe`, `æ/ae` : mêmes résultats.
- `corrections-recette-finale-V2.json` contient les requêtes réellement observées pour les deux valeurs de carte : **zéro requête tiers sur la page publique** ; détecteurs testés par témoins positifs bloqués avant transport. Aucune tentative email/HTTP issue du code B10.
- Limite séparée : l’administration native tente ses avatars Gravatar ; la recette les détecte et les bloque avant transport. Ce n’est pas une carte ni un appel B10. Les appels HTTP d’ambiance du cœur sont aussi bloqués par B00 et distingués des tentatives B10.
- `corrections-preparation-V2.log` : image reconstruite et vérifiée après ajout des tests, avant PRET. `corrections-regression-V2.log` : **1 187 tests, 36 494 assertions, aucun échec/erreur**, 584 contrôles outils verts. Chiffres frais, B11 stable inchangé ; pas de substitution par les 1 175/1 176 historiques. Le bilan de paquets relève **A-32 / A32_PARTIAL_EVIDENCE**, hors B10 : signalé, aucun fichier de ce lot touché.
- Décision technique : correspondance/import et carte regroupés sur l’écran natif d’import dédié ; aucun déplacement ni changement de l’écran C10 clos. La règle de placement des sections C10 demeure pour ses sections existantes ; à confirmer en relecture si l’on veut y déplacer ce réglage technique.
- Plafonds techniques : UTF-8, 2 Mio, 2 000 commerces acceptés, champs de 500 caractères ; pas de détection automatique du format. Un arrêt brutal peut laisser un verrou d’import : diagnostic manuel, aucune tâche de reprise inventée.
- Suppression ratée réellement injectée par le filtre natif sur un seul commerce fictif : liste remplacée, reprise durable, même fichier/requête suivante sans réinsertion, puis suppression native du post et de sa méta. Message distinct d'un import refusé. Liste illisible réparée par le vrai formulaire multipart. Après recette : 30 fictifs, carte OFF, reprise vide, sessions et observateur restaurés ; tous les objets hors CPT B10 et les navigations restent exacts. Le premier reçu rouge d'oracle historique est conservé et expliqué dans NOTE.md.
- Limite choisie du mapping et dépendance/repli Unicode déclarés dans NOTE.md ; liaison page↔extension à migrer dans un futur script de bascule versionné **hors de ce lot**.
- Validation visuelle de Ced attendue ; fournisseur et consentement d’une éventuelle carte future non choisis (`NOTE.md`, trois lignes). Aucun raccord C21, paiement, compte réel, email, tiers applicatif, production, B11 ou C28.
