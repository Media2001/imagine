# B-05 — sept corrections, preuve V2

## Résultat technique

Sept instructions appliquées, aucune mutation du bootstrap partagé, de bibliothèque close, de T01, de C22 ou des fichiers d’orchestration. Site seul : `imagine-test-demo`, identité relue par la garde existante avant intervention. Trois fichiers de production transférés et relus octet pour octet : `wp/plugins/imagine-site/Partenaires.php`, `wp/themes/imagine/functions.php`, `wp/themes/imagine/archive-imagine_partenaire.php`. Aucun reset de site/profil, email, paiement ni appel commercial. Validation visuelle toujours à Ced ; distinction graphique toujours au designer.

| Instruction | Application et preuve |
|---|---|
| 1 — R2 | Vraie section `section[aria-labelledby="imagine-latest-posts"] .imagine-list a`, présence > 0, aucune relation sponsored et aucun permalien partenaire. Mutations DOM réelles : sponsored, partenaire et liste vide sont détectés, puis DOM restauré. 50 contrôles HTTP ; 9 hors réseau Chromium. Le premier test du nouveau contrôle partenaire a effectivement échoué (`browser-offline-V2.json`) : il avait oublié le slash avant `?p=` ; corrigé puis vert. L’ancien sélecteur passe à tort sur le même article sponsorisé, le nouveau le refuse. |
| 2 — R1 | Espaces/contrôles ASCII du navigateur retirés, antislashes HTTP et autorités à slashes surnuméraires normalisés ; destinations ambiguës commerciales dans le seul contenu partenaire ; relations préservées et dédoublonnées. RED réel `red-links-4-V2.json` : cinq cas attendus faux avant correction. GREEN : cas malformés, interne, ancre, protocole relatif et article intact. Les deux formes de la fusion sont aussi dans le canari HTTP live. |
| 3 — hors live | `b05-offline.php` : 64 contrôles ; stockage et requête limités à des doubles de frontière, moteur HTML et `wp_parse_url` du vrai cœur WordPress de l’image publique déjà présente. Réseau none, racine et dépôt en lecture seule, aucun site/base ; conteneur propre supprimé et absence relue. `selection/nettoyer` couvre valide, zéro, dépublié, non-partenaire, invalide et null conservant l’ancien choix. |
| 4 — injection C10 | RED `red-injection-V2.json` : deux ancres manquantes sans signalement. Ajout d’un avertissement admin français visible dans la sortie du formulaire. GREEN pour formulaire normal, fin absente et groupe absent ; formulaire préservé. Recette admin réelle confirme champ unique et avertissement absent dans le cas normal. |
| 5 — archive | RED `red-copy-V2.json`, puis texte explicite : les fiches de liste sont internes ; leurs destinations sortantes sont commerciales. |
| 6 — reçus | RED de l’ancien vérificateur conservé (`red-verifier-V2.json`). Le reçu **courant** est `final-V2.json`. L’ancien `final.json` reste intact, historique, pour ne pas réécrire une certification passée. A-VOIR et PRET désignent V2, pas l’ancien total. Le résultat réel courant est 1123 tests / 34569 assertions (non 1097/34443, ni le total intermédiaire 1114/34560 cité dans la fusion), plus 14 outils / 279 contrôles purs. Le bootstrap partagé est contrôlé par contrat B05, jamais épinglé globalement ni transféré. Hash observé et hash historique figurent dans le reçu pour expliquer leur divergence entre lots. README partagé contrôlé par sa section B05, pas par l’empreinte d’un prédécesseur. |
| 7 — imagine_list | RED `red-list-V2.json`, retrait de la branche commerciale morte ; tous ces permaliens sont de navigation interne. Suite finale exerce aussi le vrai rendu de liste avec une requête fictive non vide, article et partenaire : liens présents et ordinaires. |

## Exécution réelle

Windows, Python **3.11.15**, `PYTHONIOENCODING=utf-8`, PHP du banc WordPress 8.3 ; PHPUnit T01 PHP 8.2.33. Nouveaux paquets uniquement sous `wp/tests/demo/` et `wp/outils/demo/`, pas dans les bibliothèques ni la suite close.

Commandes lancées depuis `C:/Users/Ced/imagine` (chaque reçu est immuable ; pour rejouer un producteur, utiliser un **nouveau** nom finissant par `-V2`) :

```bash
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py red-links-4-V2 links
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py green-links-V2 links
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py baseline-selection-V2 selection
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py red-injection-V2 injection
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py green-injection-V2 injection
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py red-copy-V2 copy
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py red-list-V2 list
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py green-all-V2
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/b05-browser-unit.py browser-offline-green-V2
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05.py baseline corrections-baseline-V2
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05.py deploy installation-corrections-V2
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05.py runtime final-runtime-V2
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/b05-http.py final-http-V2
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/b05-admin.py final-admin-V2 --read-only --capture
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-quality.py quality-green-V2
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/b05-unit.py offline-final-V2
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Les deux commandes PowerShell sont capturées par `b05.command` dans `preparer-image-V2.log` et `rejouer-final-V2.log`, code 0. Syntaxe des six PHP vérifiée ; PSR12 ciblé sans erreur, comme le gate antérieur, avec `--warning-severity=0`. L’essai sans cette option a zéro erreur et des avertissements de longueur de ligne/bootstrap WordPress : `quality-final-V2.log`, conservé comme diagnostic et non annoncé vert.

Bilan : PHP hors live **64/64** ; Chromium hors réseau **9/9** ; natif B05 **15/15** ; pages HTTP **50/50** ; admin lecture/refus/captures **12/12** ; qualité **8/8** ; C09 **382/382** ; T01 **1123/34569**, 0 échec/erreur/ignoré ; outils **14/279**, 0 échec. État métier, corps témoins, option B05 et action 8793 relus après restauration. Le formulaire partagé C10 n’est pas sauvegardé : aucun réglage C22 n’est touché.

Relecture finale :

```bash
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/b05-verifier.py
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/b05-verifier.py --live
```

Le premier contrôle est hors réseau ; le second lit seulement la démo autorisée. Pour rejouer les **comportements** hors live, utiliser `b05-unit.py` avec un nouveau reçu. Le code source du bootstrap partagé peut évoluer pour un autre lot sans invalider les contrats B05.

## Incidents et décisions à défaut

- Trois premiers amorçages du banc WordPress ont révélé des dépendances natives manquantes (utf8/compat/kses), pas des RED métier ; ils sont conservés mais seul `red-links-4-V2.json` démontre R1.
- La première mutation témoin a révélé un défaut de qualification du permalien dans le test lui-même ; réparation prouvée avant installation.
- Extraction web générique indisponible dans cet environnement ; récupération directe des trois pages officielles WordPress réussie (HTTP 200 et empreintes dans `standard-sources-V2.json`). Aucune installation sur l’hôte, aucun contenu de résultat inventé.
- Conservation des reçus historiques prioritaire : `final.json` reste daté et périmé ; **`final-V2.json` seul fait foi pour les corrections**. Aucune attribution de la divergence du fichier partagé à B05.
- Aucun blocage restant. Aucun arbitrage métier nouveau ; aucun GO réel.
