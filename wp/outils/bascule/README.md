# Bascule

Ces scripts transforment l’existant sur la copie vérifiée, puis sur une copie fraîche lors de la mise en ligne décidée par Ced. Ne jamais remonter une base de staging. Ne placer ici ni neutralisation, ni anonymisation, ni installation de Novamira.

Exécuter `bash lancer` dans le contexte isolé choisi par l’opérateur ; le lanceur ne cherche pas de site et n’ouvre aucune connexion. Il valide les noms et permissions avant de commencer, puis exécute les fichiers exécutables `010-nom`, `020-nom`, etc. dans l’ordre numérique. Chaque numéro est unique. Chaque script futur doit être idempotent et testé séparément. À la première erreur, le lanceur s’arrête et renvoie le code du script. Aucun saut automatique au redémarrage : on reprend depuis le début. Le journal de progression (nom, résultat, code ; aucune sortie métier) va sur stderr, à conserver par l’appelant hors racine web. Aucun script numéroté à ce stade.

## A-32 — Tournée des inventaires

A-08 enchaîne audit, photos, mise à jour et nettoyage avec arrêt au premier refus ; la tournée ne lance aucune de ces étapes et ne modifie rien. Préparer séparément l'audit A-02 d'une copie vérifiée et la correspondance A-16. Dans le contexte Linux déconnecté déjà requis par les outils, le parent de sortie existe hors dépôt/site et reste frère de l'audit ; sortie et sorties d'outils neuves.

```text
python3 wp/outils/bascule/tournee/tournee.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --correspondance=/hors-web/correspondance.json --output=/hors-web/tournee-date
```

A32-CONTRAT : outils clos et ordre fermés dans tournee/outils.jsonl ; chaque commande documentée garde ses seuls arguments, seuls les chemins opérateur changent ; gardien commun inchangé.
A32-BILAN : bilan.json et bilan.md hors dépôt, statuts et codes fermés, sorties entières et chemins opérateur seuls ; tous les outils continuent, sortie 1 au moindre refus/échec, bilan partiel jamais complet.

La liste courante des quinze outils et leur ordre sont définis dans `tournee/outils.jsonl` (A-26/A-27 inclus) ; A-13/A-14/A-30 demandent des fichiers Imagine, A-29/A-31 restent hors tournée. A-22 est le gardien, A-28 l'import ; aucun n'est un inventaire autonome. Les exclusions et leur raison fermée sont dans tournee/exclusions.json. Lire production/A-32/RAPPORT.md pour les preuves et wp/tests/a32 pour le rejeu synthétique ; aucune autorisation sur un site réel.

## A-33 — Le poids des archives

A33-PORTEE : lecture seule sur copie vérifiée ; correspondance et refus A-16 inchangés, dix numéros ; publications hors dix par rôle/type fermé et année UTC ; originaux mesurés par stat sans ouverture, absents séparés, totaux incomplets inconnus et dossiers exclus inconnus après import. Aucun nom, titre ni chemin du site en sortie. Détails et limites : a33/README.md.

```sh
python3 wp/outils/bascule/a33/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --correspondance=/hors-web/correspondance.json --output=/hors-web/archives-date
```


