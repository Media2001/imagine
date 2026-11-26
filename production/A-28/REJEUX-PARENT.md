# Dépendances invalidées — à traiter par le parent, sans faux rescellement

Les anciens paquets restent **historiques, octets non réécrits**. A-28 modifie l'import expressément autorisé, pas le gardien. `wp/outils/bascule/stream_guard.py` est resté identique au départ. Les observations ci-dessous sont de vrais lancements en lecture seule, conservés dans `preuves/final/dependency-invalidations.json` et `additional-dependency-observations.json`, avec leurs flux et empreintes.

| Vérificateur actuel | Sortie réelle | Motif constaté |
|---|---:|---|
| A-20 | 0 | Aucun contrôle rouge. |
| A-21 | 1 | `exact_current_dependencies`, `cp1252:executed_dependency_snapshot`, `utf8:executed_dependency_snapshot`. |
| A-22 | 1 | `exact_current_executed_sources`. Ce n'est pas un changement de son gardien ; sa source de rejeu inclut l'import. Son ancienne réserve de revalidation indépendante n'est pas levée par A-28. |
| A-23 | 1 | `utf8:current_dependencies`, `cp1252:current_dependencies`. |
| A-24 | 1 | `dependencies_exact`. |
| A-25 | 1 | `utf8:dependencies_equal`, `cp1252:dependencies_equal`. |
| A-26 / A-27 | 1 / 1 | `SEALED_VERIFICATION_FAILED` : leur gel de 23 h 42 contient les anciennes empreintes de `staging/lib.php` et `staging/command.php`, changées par A-28. |

Les deux fichiers PHP de l'import changent et `staging/form-policy.json` est ajouté ; les inventaires complets de cette dépendance diffèrent donc également par ce nouveau fichier. Les bancs A-23 à A-27 copient déjà le dossier `staging` entier : **pas de correctif de transport JSON supposé nécessaire**, à vérifier par leur rejeu. Ne pas remplacer les anciennes empreintes par les nouvelles sans exécution.

## Rejeux précis, sous l'unique propriétaire Docker du parent

Après son propre gel des sources, un dossier **neuf hors dépôt** par commande ; toutes ces commandes lancent de vrais conteneurs et ne doivent pas tourner en parallèle avec un autre propriétaire Docker. Les `$S/...` ci-dessous sont des dossiers nouveaux sous le scratch Hermes, choisis par le parent, pas des sites.

```powershell
C:/Python314/python.exe -B wp/tests/a21/matrix.py --output "$S/a21"
C:/Python314/python.exe -B wp/tests/a22/matrix.py --output "$S/a22"
C:/Python314/python.exe -B wp/tests/a23/matrix.py --output "$S/a23"
C:/Python314/python.exe -B wp/tests/a24/matrix.py --output "$S/a24"
C:/Python314/python.exe -B wp/tests/a25/matrix.py --output "$S/a25"
C:/Python314/python.exe -B wp/tests/a26/matrix.py --output "$S/a26"
C:/Python314/python.exe -B wp/tests/a27/matrix.py --include-native --parent-serialized --output "$S/a27"
```

**Avant A-25 seulement :** `wp/tests/a25/neutralise.php:13` demande encore `garder` pour `wp_fluentform_submissions`, et `inside.py`/`verify.py` exigent encore `actual_import_comments_changed_forms_clear`. Le nouveau refus est voulu. Son propriétaire doit remplacer cette ancienne attente par la purge obligatoire et qualifier les messages inconnus séparément ; **ne pas desserrer A-28 ni changer son gardien** pour rendre l'ancien test vert. Ces fichiers ne sont pas modifiés ici. Les autres lots sont à rejouer à source métier inchangée, sous réserve d'un vrai échec observé.

Puis préparation de l'image, rejeu global dans les deux environnements et relecture des nouveaux paquets par leurs vérificateurs respectifs ; le parent décide de leurs nouveaux gels/PRET. A-28 a sa propre matrice et ses propres portes, indépendantes de ces paquets historiques. Aucun rescellement d'un autre lot n'a été effectué ici.
