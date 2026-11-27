# C29 — consultation et réception courante au contrat

Parcours Ced inchangé : `A-VOIR.md` conserve les adresses de la démo, les 27 comptes fictifs attendus et la distinction consultation GET / configuration native séparée. Ouvrir **Imagine → Ce qui partirait vers Brevo** pour les comptes 9 puis 19 ; aucune fiche n’est transmise ou enregistrée. Les données de recette ont été restaurées, la capture reste historique.

Depuis `C:\Users\Ced\imagine` :
```text
python -B production/C-29/verifier.py
python -B production/C-29/verifier.py --live
python -B wp/tests/demo/b11-c29-contract-tests.py C29
python -B wp/tests/demo/c29-proof-tests.py
```
Lecteurs : PASS/code 0, preuves intactes **21 purs / 51 natifs / 73 HTTP / 27 profils**. Qualification courte : 12 tests ; tests des lecteurs de preuves : 9. La première commande n’accède à aucun site ; `--live` ne fait que lire `imagine-test-demo` sous sa garde existante. Les fichiers propres, le bloc propre exact unique et la section README bornée sont contrôlés ; ajout étranger accepté, changement propre refusé. Aucun PRET voisin ni sceau global du bootstrap.

Réception neuve `reception-contrat-V2.json`, note actuelle `NOTE-contrat-V2.md`. Les reçus et compléments antérieurs restent historiques exacts ; le lecteur précédent est archivé dans `verifier-avant-contrat-V2.py`. Ne pas relancer les anciens finaliseurs, recettes voisins ou scripts de récupération pour ce changement de contrat. Le finaliseur borné commun `wp/outils/demo/b11-c29-contract.py` est à usage unique et refuse d’écraser la réception. Pas de nouveau PHP/rejeu général, aucune modification fonctionnelle ou écriture métier. Ni clôture, validation visuelle, compte Brevo/Odoo ou GO réel.
