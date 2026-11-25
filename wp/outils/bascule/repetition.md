# A-08 — Répétition de la bascule

**Préparer :** copie fraîche vérifiée ; gel externe écritures/queues/déploiements ; plans
A04/A05 relus (ZIP/versions/SHA-256, propriétaires des tables audités) ; sauvegarde base ET
fichiers hors site, intègre, moins de six heures, restauration vérifiée séparément.
Précréer `.imagine-a04-bascule.lock`. Settings A03, journal PHP UTC, compte SQL SELECT seul,
réception HTTP privée. A08 ne modifie aucun de ces préalables. Linux, chemins fictifs :

```bash
S=/srv/fiction/site; T=/opt/imagine/wp/outils/bascule; E=/srv/fiction/repetition
U=/srv/fiction/plan-maj.json; N=/srv/fiction/plan-nettoyage.json
B=/srv/fiction/sauvegarde.json; C=/srv/fiction/settings-a03.json
sequence=(python3 -B "$T/repeter" --wp-path="$S" --state="$E" --update-plan="$U" --clean-plan="$N" --backup="$B" --config="$C")
"${sequence[@]}"                       # audit puis photo avant ; arrêt NORMAL 75
```

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

```bash
# Après 1–2 : opérateur, sous gel externe, remet la configuration écriture
# conventionnelle et la maintenance native récente, sans altérer la garde staging.
"${sequence[@]}" --mutations-ready     # étapes 3–4 ; arrêt NORMAL 75 avant réception
# Après 4 : opérateur organise une réception HTTP PRIVÉE, enlève explicitement
# les deux maintenances A04, repasse au compte SELECT ; garde staging conservée.
"${sequence[@]}" --reception-ready     # étapes 5–6 ; 0 seulement sans anomalie
```

Rendez-vous obligatoires : A03 refuse un compte écriture ; A04/A05 exigent maintenance ;
le MU A04 rend le HTTP indisponible (503). L'opérateur conserve hors web les octets de ce MU
et le rétablit à l'identique avant un second passage. A08 ne retire ni ne réinstalle de garde.
Aucun DNS/exposition publique piloté ; après réception, rétablir la maintenance souhaitée.

**Arrêts/reprise :** `75` = rendez-vous/arrêt natif ; `1` = refus/erreur ; `2` = anomalie,
jamais requalifiée ; `3` natif accepté seulement avec zéro anormal. Lire **`$E/rapport.md`** :
six étapes, durées cumulées hors attentes humaines, résultats, preuves ; aucune valeur de base.
Même commande et drapeau du rendez-vous ; mêmes outils/plans/settings/sauvegarde.
Étapes réussies scellées, A04/A05 reprennent leurs checkpoints. Ne supprimer aucun verrou.
`A05_UNINSTALL_AMBIGUOUS` impose restauration vérifiée puis nouvel état ; lecture coupée :
nouvelle sortie. Plan changé, preuve altérée, sauvegarde périmée : aucune réparation implicite.

**Second passage complet :** préalables de réception, `"${sequence[@]}" --new-pass`, puis
les deux rendez-vous. Six outils relancés, checkpoints A04/A05 conservés, anciennes preuves
conservées, un seul rapport. Sans ce drapeau, l'état terminé ne relance rien.
La maintenance et l'expiration du cache natif WCS peuvent être rafraîchies ;
« sans changement » signifie ici comparaison métier identique, pas octets techniques immobiles.

**GO ÉCRIT DE CED :** requis séparément pour toute opération réelle/production.
`--go-update=/hors-depot/go-a04.json` et `--go-clean=/hors-depot/go-a05.json` transmettent
les attestations distinctes aux outils, sans les fabriquer ni remplacer leurs contrôles.
A03 exige une copie vérifiée : **chaîne complète qualifiée sur copies fictives seulement**,
pas une qualification de réception production. Ni archive Imagine, ni compte réel ici.

Rejeu hôte : `python -B wp/tests/a08/run.py` (PHP uniquement dans son Docker A08 jetable).
Les durées fictives du rapport de livraison ne prédisent pas la fenêtre du vrai site.
