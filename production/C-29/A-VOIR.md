# C29 — à voir et commandes du parent

## Pour Ced — uniquement la démo fictive existante

1. Dans `imagine-test-demo`, ouvrir une session **Référent abonnements** (E-ABO) ou Administrateur avec le mécanisme privé habituel ; aucun identifiant n’est dans ce paquet.
2. **Imagine → Ce qui partirait vers Brevo**. Saisir l’identifiant **9** (A-CARTE fictif) puis **19** (A-SANSMAIL fictif), ou un compte sans choix. Vérifier fiche/raison, totaux et les mentions d’inconnu. Le formulaire est GET, il ne sauvegarde rien. Ne pas confondre « actif pour Brevo » et accès numérique jusqu’au terme.
3. À part, pour l’administrateur : **Réglages → Tarifs de la fiche Brevo**. Liste fermée produit/variation → clé interne ; vide signifie inconnu. Six correspondances fictives C09 sont livrées, aucun prix. Ce formulaire de configuration distinct écrit seulement lors de sa soumission native ; la consultation n’enregistre jamais de fiche ni d’option.

Adresse de la consultation : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-contact-brevo&compte=9`.
Adresse de la configuration séparée : `http://192.168.129.32:8085/wp-admin/options-general.php?page=imagine-brevo-tarifs`.

Capture : `http-reception-V2.png`, prise pendant la recette à données fictives contrôlées ; **profils et réglages de cette recette restaurés ensuite**, pas une invitation à laisser les préférences de test en place. Validation visuelle de Ced non acquise. Les commentaires techniques et les valeurs fictives ne remplacent pas la future grille Imagine ni les noms d’attributs Brevo.

## Vérifier le paquet — aucune mutation ni accès au site par défaut

Depuis `C:\Users\Ced\imagine` :

```powershell
python -B production/C-29/verifier.py
python -B wp/tests/demo/c29-proof-tests.py
```

Le premier lit les octets et les preuves liés par `reception-V2.json` ; le second montre que des preuves incomplètes, des tentatives cachées ou un observateur jamais entré sont refusés. Bibliothèque standard Python uniquement pour ces commandes. Aucun compte Brevo ni réseau requis.

Lecture **du seul site fictif gardé**, sans réinstaller ni changer ses données :

```powershell
python -B production/C-29/verifier.py --live
```

## Rejouer les preuves — certaines recettes mutent temporairement la seule démo

Chaque étiquette doit être neuve. Aucun argument n’autorise un autre site.

```powershell
# PHP pur dans l’image locale, réseau none, dépôt en lecture seule
python -B wp/outils/demo/c29.py pure parent-pur-NOM-NEUF
# Objets et préférences fictifs dans une transaction, rollback et empreintes exactes
python -B wp/outils/demo/c29.py native parent-natif-NOM-NEUF
# Vrai HTTP + navigateur, compteurs/choix/consentement contrôlés, inverse et relecture
python -B wp/outils/demo/c29-http.py parent-http-NOM-NEUF
# Lecteurs indépendants des voisins sur l’arbre courant, pas de resceau historique
python -B wp/outils/demo/c29-neighbors.py parent-voisins-NOM-NEUF
# Préparation et rejeu canoniques autorisés, scripts gelés non modifiés
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Si le code devait seulement être recopié sur la démo déjà gardée : `python -B wp/outils/demo/c29.py deploy parent-code-NOM-NEUF`. Le bootstrap distant est refusé s’il diffère du courant ou du courant privé du seul bloc C29. Pas de constructeur global ni de reset C09. La configuration fictive ne s’initialise séparément que si absente/identique : `python -B wp/outils/demo/c29.py seed parent-tarifs-NOM-NEUF` ; un autre réglage existant est refusé, jamais remplacé silencieusement.

**Ne pas relancer les scripts `c29-recover*`** : ce sont des inverses d’incidents datés, conditionnées aux checksums de leur état, pas des recettes ni des outils d’administration. Le lecteur de réception n’en a pas besoin pour fonctionner.

## À ne pas confondre avec PRET

- Les trois tests C29 sont dans le JUnit canonique ; les recettes natives/HTTP sont séparées et ne gonflent pas ce nombre.
- La remise en état des profils/options/actions est prouvée. La limite historique des sessions d’un essai interrompu et leur récupération est détaillée en NOTE ; le rejeu HTTP final prouve les sessions exactes à **son** départ.
- Les expirations de caches du cœur ne sont pas présentées comme zéro écriture de WordPress ; le vrai rendu C29 a son interception SQL/HTTP/mail et ses témoins positifs.
- B11 conserve `UI_save_verified=false`, conformément à sa réception parent de 13h30. C29 ne certifie pas ses éditeurs par sa propre capture.
- A31/A32 rouges connus restent hors lot. Aucun paquet, bibliothèque close ou droit/prix n’a été corrigé pour rendre ce lot vert.
- Aucun branchement Brevo/Odoo, aucune activation, clé, export de contacts, transmission, tâche planifiée ou écouteur de synchronisation.

`PRET` = technique, prêt aux relectures ; ni clôture, ni validation visuelle, ni GO sur le réel.
