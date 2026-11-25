# Répéter la bascule — A-08 (une page)

**Avant :** copie fraîche **vérifiée**, gel externe des écritures/queues/déploiements,
plans A-04/A-05 relus (versions/ZIP/SHA-256 explicites, propriétaires des tables audités),
sauvegarde base **et** fichiers hors du site, empreintes exactes, moins de six heures,
restauration vérifiée séparément. Précréer le verrou natif `.imagine-a04-bascule.lock`.
Préparer les settings A-03, leur journal PHP UTC lisible et le compte SQL **SELECT seul**.
Le contrôle HTTP doit rester inaccessible au public pendant les deux réceptions.
A08 ne crée aucune sauvegarde et ne modifie jamais maintenance, compte ou garde de sûreté.

## Commande commune (Linux, outils hors racine web ; chemins fictifs à remplacer)

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

Ces rendez-vous sont nécessaires : A03 refuse un compte écriture, A04/A05 exigent
maintenance ; sous le MU de maintenance A04 le HTTP répond 503. **Jamais de levée
automatique ni de garde contournée.** L'opérateur rétablit l'état de maintenance voulu
après réception ; aucun DNS ni exposition publique n'est piloté ici.

**Arrêts :** `75` = rendez-vous ou arrêt natif demandé ; `1` = refus/erreur ; `2` =
anomalie native de comparaison, jamais requalifiée ; `3` natif = changements attendus,
accepté comme succès de la séquence seulement avec zéro anormal. Lire **`$E/rapport.md`**
(six étapes, durées cumulées de tous les essais, résultat, reçus ; aucune valeur de base).
Les attentes humaines sont exclues. Les sorties détaillées restent dans les preuves.

**Reprise :** même commande et mêmes plans/settings/sauvegarde/outils, avec le drapeau
du rendez-vous concerné. Les étapes réussies et leurs preuves sont scellées, jamais rejouées.
A04/A05 reprennent leurs propres checkpoints ; `A05_UNINSTALL_AMBIGUOUS` impose une
restauration vérifiée puis un nouvel état, pas une reprise forcée. Une sauvegarde périmée,
un plan modifié ou une preuve altérée n'est jamais réparé implicitement. Ne supprimer aucun
verrou/checkpoint. Un arrêt brutal pendant une lecture laisse un essai incomplet conservé ;
la lecture seule recommence dans une autre sortie. Les enfants héritent des verrous A08.

**Second passage complet :** remettre les préalables de réception, lancer
`"${sequence[@]}" --new-pass`, puis les deux commandes de rendez-vous ci-dessus.
Les six outils sont réellement relancés, A04/A05 gardent leurs checkpoints ; le rapport
reste unique et les anciennes photos/reçus sont conservés. Sans `--new-pass`, une
séquence terminée n'effectue aucune opération native.

**GO ÉCRIT DE CED :** requis séparément pour toute opération réelle/production.
`--go-update=/hors-depot/go-a04.json` et `--go-clean=/hors-depot/go-a05.json` transmettent
les attestations distinctes aux outils, sans les fabriquer ni remplacer leurs contrôles.
A03 exige une copie vérifiée : **chaîne complète qualifiée sur copies fictives seulement**,
pas une qualification de réception production. Ni archive Imagine, ni compte réel ici.

Rejeu hôte : `python -B wp/tests/a08/run.py` (PHP uniquement dans son Docker A08 jetable).
Les durées fictives du rapport de livraison ne prédisent pas la fenêtre du vrai site.
