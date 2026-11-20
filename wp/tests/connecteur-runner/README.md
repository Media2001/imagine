# Banc C-04, réutilisation de C-01

Depuis la racine du checkout autorisé :

```sh
python wp/tests/connecteur-runner/run.py prepare
python wp/tests/connecteur-runner/run.py run --name final
python wp/tests/connecteur-runner/verify.py
python wp/tests/connecteur-runner/run.py close
```

L’import utilise le banc existant `wp/tests/numeros-runner/run.py` inchangé. Seuls
`PLUGIN`, `OUT`, `STATE`, `LABEL` sont spécialisés. Le nom de conteneur garde le préfixe
`imagine-c01-` mais l’étiquette de propriété est `org.imagine.c04-runner=true` ; le
lanceur C-01 ne peut donc pas le gérer par erreur. Le cache bytecode Python est désactivé
avant import pour préserver l’autre lot. `--filter` et `--name` fonctionnent comme C-01.

Isolation héritée : image publique synthétique existante, entrée `sleep`, aucun montage,
volume, port, privilège ni base/WordPress. Préparation Composer uniquement en réseau,
réseau détaché avant tous les tests. Aucun accès au staging Imagine ou à un service réel.
En cas d’échec : appeler `close` et signaler le blocage, ne rien installer sur l’hôte.

`verify.py` exige un runner C-04 déjà préparé et un passage `run` avec les dernières
sources. Il compare C-01 aux empreintes `production/C-04/tests/c01-before.json`, le
copie dans `/baseline`, réutilise les seules dépendances de test et régénère l’autoload
**dans le conteneur**. Il lance ses tests/lint sans toucher à ses sources/preuves.
Il exécute aussi le vrai exemple CSV C-04 et récupère le résultat/CSV dans les preuves.
Il passe le PHP contenant `$` via stdin : des arguments `php -r` traversant WSL peuvent
subir une expansion shell, défaut reproduit dans `wsl-php-transport-probe.json`.

Journaux, XML JUnit, reçus d’exécution/isolation, manifeste et CSV :
`production/C-04/tests/`. Les noms de preuve ne sont pas des garanties de réussite :
les premiers passages `green-event`/`green-export` avaient seulement un avertissement
PSR-12, corrigé ensuite ; seuls les codes réels des reçus font foi.
