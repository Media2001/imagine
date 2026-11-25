# A-08 — Répétition de la bascule

Ce bloc prépare la copie et les preuves : à la fin, tous les préalables doivent être disponibles sans avoir changé le site.

**Préparer :** copie fraîche vérifiée ; gel externe écritures/queues/déploiements ; plans
A04/A05 relus (ZIP/versions/SHA-256, propriétaires des tables audités) ; sauvegarde base ET
fichiers hors site, intègre, moins de six heures, restauration vérifiée séparément.
Précréer `.imagine-a04-bascule.lock`. Settings A03, journal PHP UTC, compte SQL SELECT seul,
réception HTTP privée. A08 ne modifie aucun de ces préalables. Linux, chemins fictifs :

Ce bloc définit les chemins et lance les deux premières étapes : à la fin, la séquence attend normalement l’opérateur avec le code 75.

```bash
S=/srv/fiction/site; T=/opt/imagine/wp/outils/bascule; E=/srv/fiction/repetition
U=/srv/fiction/plan-maj.json; N=/srv/fiction/plan-nettoyage.json
B=/srv/fiction/sauvegarde.json; C=/srv/fiction/settings-a03.json
sequence=(python3 -B "$T/repeter" --wp-path="$S" --state="$E" --update-plan="$U" --clean-plan="$N" --backup="$B" --config="$C")
"${sequence[@]}"                       # audit puis photo avant ; arrêt NORMAL 75
```

Ce tableau rappelle les six commandes appelées par la séquence : à la fin, chaque étape doit avoir son reçu, sans lancer ces commandes une seconde fois.

| Dans l'ordre | Commande exacte (équivalent natif du premier essai) |
|---|---|
| 1. Audit | `php "$T/audit" --wp-path="$S" --output="$E/audit-1"` |
| 2. Avant | `php "$T/non-regression" --wp-path="$S" --config="$C" --output="$E/avant-1"` |
| 3. Mise à jour | `python3 -B "$T/mettre-a-jour" --wp-path="$S" --plan="$U" --backup="$B" --state="$E/a04"` |
| 4. Nettoyage | `python3 -B "$T/nettoyer" --wp-path="$S" --plan="$N" --backup="$B" --state="$E/a05"` |
| 5. Après | `php "$T/non-regression" --wp-path="$S" --config="$C" --output="$E/apres-1"` |
| 6. Comparaison | `php "$T/comparer" "$E/avant-1/non-regression.json" "$E/apres-1/non-regression.json"` |

**Ne pas exécuter ces équivalents en plus de la séquence** : elle les appelle elle-même.
Leurs arguments exacts et les numéros d'essai effectifs sont dans les reçus JSON.

Ce bloc reprend les transformations puis la réception : à la fin, le code 0 indique une comparaison sans anomalie, après les deux rendez-vous opérateur.

```bash
# Après 1–2 : opérateur, sous gel externe, remet la configuration écriture
# conventionnelle et la maintenance native récente, sans altérer la garde staging.
"${sequence[@]}" --mutations-ready     # étapes 3–4 ; arrêt NORMAL 75 avant réception
# Après 4 : opérateur organise une réception HTTP PRIVÉE, enlève explicitement
# les deux maintenances A04, repasse au compte SELECT ; garde staging conservée.
"${sequence[@]}" --reception-ready     # étapes 5–6 ; 0 seulement sans anomalie
```

Ce bloc précise les changements réservés à l’opérateur : à la fin, la réception reste privée et les gardes sont conservées.

Rendez-vous obligatoires : A03 refuse un compte écriture ; A04/A05 exigent maintenance ;
le MU A04 rend le HTTP indisponible (503). L'opérateur conserve hors web les octets de ce MU
et le rétablit à l'identique avant un second passage. A08 ne retire ni ne réinstalle de garde.
Aucun DNS/exposition publique piloté ; après réception, rétablir la maintenance souhaitée.

Ce bloc explique les arrêts et les reprises : à la fin, le rapport doit correspondre à la tentative et une anomalie reste une anomalie.

**Arrêts/reprise :** `75` = rendez-vous/arrêt natif ; `1` = refus/erreur ; `2` = anomalie,
jamais requalifiée ; `3` natif accepté seulement avec zéro anormal. Lire **`$E/rapport.md`** :
passages séparés, six étapes et comparaison par passage, durées cumulées dans chaque passage
(essais refusés inclus), hors attentes humaines ; aucune valeur de base. En cas de
`A08_REPORT_NOT_UPDATED` sur stderr, le rapport existant ne décrit **pas** cette tentative :
état inaccessible ou verrou non acquis ; ne pas lire un ancien succès comme le résultat du refus.
Même commande et drapeau du rendez-vous ; mêmes outils/plans/settings/sauvegarde.
La clôture scellée couvre les outils appelés, supports A03/A04/A05, comparaison du plugin
hors arbre, sonde runtime et garde staging ; pas les outils A09/A10 non appelés.
Étapes réussies scellées, A04/A05 reprennent leurs checkpoints. Ne supprimer aucun verrou.
**Code 2 :** une reprise ne refait pas la réception ; elle compare les mêmes photos et
conserve l'anomalie. Conserver intégralement l'état et les preuves d'échec, restaurer la
sauvegarde de départ vérifiée (base ET fichiers), puis recommencer les six étapes dans
un **nouvel état**, avec entrées cohérentes et préalables natifs revérifiés. Ne supprimer
ni checkpoints ni verrous pour débloquer. `--new-pass` n'est pas une sortie d'échec.
`A05_UNINSTALL_AMBIGUOUS` impose également restauration vérifiée puis nouvel état ; lecture
coupée : nouvelle sortie. Plan changé, preuve altérée, sauvegarde périmée : aucune réparation
implicite. Les anciens états v1 sont conservés, non migrés vers le scellé v2.

Ce bloc relance les six étapes pour vérifier la répétition : à la fin, les résultats métier sont identiques et les anciennes preuves sont conservées.

**Second passage complet :** préalables de réception, `"${sequence[@]}" --new-pass`, puis
les deux rendez-vous. Six outils relancés, checkpoints A04/A05 conservés, anciennes preuves
conservées, un seul rapport. Sans ce drapeau, l'état terminé ne relance rien.
La maintenance et l'expiration du cache natif WCS peuvent être rafraîchies ;
« sans changement » signifie ici comparaison métier identique, pas octets techniques immobiles.

Ce bloc rappelle la limite d’autorisation : à la fin, aucune opération réelle n’est permise sans les accords écrits distincts de Ced.

**GO ÉCRIT DE CED :** requis séparément pour toute opération réelle/production.
`--go-update=/hors-depot/go-a04.json` et `--go-clean=/hors-depot/go-a05.json` transmettent
les attestations distinctes aux outils, sans les fabriquer ni remplacer leurs contrôles.
A03 exige une copie vérifiée : **chaîne complète qualifiée sur copies fictives seulement**,
pas une qualification de réception production. Ni archive Imagine, ni compte réel ici.

Ce bloc donne le rejeu sur le banc fictif : à la fin, ses tests vérifient la chaîne sans qualifier la durée ni la réception du vrai site.

Rejeu hôte : `python -B wp/tests/a08/run.py` (PHP uniquement dans son Docker A08 jetable).
Les durées fictives du rapport de livraison ne prédisent pas la fenêtre du vrai site.
